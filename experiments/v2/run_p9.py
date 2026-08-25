from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import re
import statistics
import threading
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

import numpy as np
import psutil
import torch
from PIL import Image
from scipy.optimize import linear_sum_assignment


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "experiments" / "v2" / "config" / "preregistration_v2.json"
GRAPH_PATH = ROOT / "experiments" / "v2" / "config" / "semantic_graph_v2.json"
CAPABILITY_PATH = ROOT / "experiments" / "v2" / "manifests" / "capability_v2.jsonl"
ACQUISITION_PATH = ROOT / "experiments" / "v2" / "manifests" / "model_acquisition_v2.json"
RESULT_ROOT = ROOT / "results" / "p9-v2"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def model_entry(backend: str) -> dict[str, Any]:
    manifest = read_json(ACQUISITION_PATH)
    for entry in manifest["models"]:
        if entry["backend"] == backend:
            return entry
    raise RuntimeError(f"{backend} has not been acquired and reviewed")


def extraction_prompt(graph: dict[str, Any]) -> str:
    categories = ",".join(graph["entity_categories"])
    colours = ",".join(graph["attributes"]["colour"])
    sizes = ",".join(graph["attributes"]["size"])
    unary = ",".join(graph["unary_actions"])
    binary = ",".join(graph["binary_actions"] + graph["spatial_relations"])
    scenes = ",".join(graph["scenes"])
    return (
        "Inspect the image itself. Return ONLY one minified JSON object, without markdown or explanation, using exactly this shape: "
        '{"nodes":[{"id":"n1","category":"cat","bbox":[0.1,0.1,0.4,0.5],"attributes":{"colour":"red","size":"small"}}],'
        '"unary":[{"node":"n1","action":"sleeping"}],"binary":[{"source":"n1","type":"left_of","target":"n2"}],'
        '"counts":[{"category":"cat","bucket":"1"}],"scene":"indoor"}. '
        "Boxes are normalized x_min,y_min,x_max,y_max. Include every visible credential entity and one count for every included category. "
        "Use empty arrays when no fact applies. Do not infer hidden entities. Use only these exact tokens. "
        f"categories={categories}; colours={colours}; sizes={sizes}; unary={unary}; binary={binary}; "
        f"count buckets=1,2,3,4,5_plus; scenes={scenes}."
    )


class PeakRSS:
    def __enter__(self) -> "PeakRSS":
        self.process = psutil.Process(os.getpid())
        self.peak = self.process.memory_info().rss
        self.stop = threading.Event()

        def sample() -> None:
            while not self.stop.wait(0.02):
                try:
                    self.peak = max(self.peak, self.process.memory_info().rss)
                except psutil.Error:
                    return

        self.thread = threading.Thread(target=sample, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *_: Any) -> None:
        self.stop.set()
        self.thread.join(timeout=1)
        try:
            self.peak = max(self.peak, self.process.memory_info().rss)
        except psutil.Error:
            pass


def parse_json_answer(answer: str) -> dict[str, Any]:
    value = answer.strip()
    if value.startswith("```"):
        value = re.sub(r"^```(?:json)?\s*", "", value)
        value = re.sub(r"\s*```$", "", value)
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        start, end = value.find("{"), value.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("no JSON object in answer")
        parsed = json.loads(value[start:end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("answer is not a JSON object")
    return parsed


def normalise_graph(raw: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    if set(raw) != {"nodes", "unary", "binary", "counts", "scene"}:
        raise ValueError("top-level keys do not exactly match schema")
    if not all(isinstance(raw[key], list) for key in ("nodes", "unary", "binary", "counts")):
        raise ValueError("graph collection fields must be arrays")
    if not isinstance(raw["scene"], str) or raw["scene"] not in config["scenes"]:
        raise ValueError("invalid scene")
    if not 0 < len(raw["nodes"]) <= config["maximum_nodes"]:
        raise ValueError("invalid node count")

    nodes = []
    ids: set[str] = set()
    for value in raw["nodes"]:
        if not isinstance(value, dict) or set(value) != {"id", "category", "bbox", "attributes"}:
            raise ValueError("invalid node keys")
        node_id, category = value["id"], value["category"]
        if not isinstance(node_id, str) or not node_id or node_id in ids:
            raise ValueError("invalid or duplicate node id")
        if category not in config["entity_categories"]:
            raise ValueError("unknown entity category")
        box = value["bbox"]
        if not isinstance(box, list) or len(box) != 4 or not all(isinstance(x, (int, float)) and math.isfinite(x) for x in box):
            raise ValueError("invalid bounding box")
        box = [float(x) for x in box]
        if not (0 <= box[0] < box[2] <= 1 and 0 <= box[1] < box[3] <= 1):
            raise ValueError("bounding box outside normalized range")
        attrs = value["attributes"]
        if not isinstance(attrs, dict) or any(key not in config["attributes"] for key in attrs):
            raise ValueError("invalid attributes")
        clean_attrs = {}
        for key, attr_value in attrs.items():
            if attr_value not in config["attributes"][key]:
                raise ValueError("unknown attribute value")
            clean_attrs[key] = attr_value
        ids.add(node_id)
        nodes.append({"id": node_id, "category": category, "bbox": box, "attributes": clean_attrs})

    unary = []
    for value in raw["unary"]:
        if not isinstance(value, dict) or set(value) != {"node", "action"} or value["node"] not in ids or value["action"] not in config["unary_actions"]:
            raise ValueError("invalid unary action")
        unary.append({"node": value["node"], "action": value["action"]})

    inverse = config["inverse_normalisation"]
    allowed_binary = set(config["binary_actions"] + config["spatial_relations"])
    binary = []
    for value in raw["binary"]:
        if not isinstance(value, dict) or set(value) != {"source", "type", "target"}:
            raise ValueError("invalid binary keys")
        source, edge_type, target = value["source"], value["type"], value["target"]
        if source not in ids or target not in ids or source == target or edge_type not in allowed_binary:
            raise ValueError("invalid binary edge")
        if edge_type in inverse:
            source, target = target, source
            edge_type = inverse[edge_type]["canonical"]
        binary.append({"source": source, "type": edge_type, "target": target})

    category_counts = defaultdict(int)
    for value in nodes:
        category_counts[value["category"]] += 1
    counts = []
    seen_count_categories: set[str] = set()
    for value in raw["counts"]:
        if not isinstance(value, dict) or set(value) != {"category", "bucket"}:
            raise ValueError("invalid count keys")
        category, bucket = value["category"], str(value["bucket"])
        if category not in config["entity_categories"] or bucket not in config["count_buckets"] or category in seen_count_categories:
            raise ValueError("invalid count")
        observed = category_counts.get(category, 0)
        expected = "5_plus" if observed >= 5 else str(observed)
        if observed == 0 or bucket != expected:
            raise ValueError("count/entity contradiction")
        seen_count_categories.add(category)
        counts.append({"category": category, "bucket": bucket})

    return {"nodes": nodes, "unary": unary, "binary": binary, "counts": counts, "scene": raw["scene"]}


def canonical_graph(graph: dict[str, Any]) -> str:
    groups: dict[str, list[str]] = defaultdict(list)
    for node in graph["nodes"]:
        groups[node["category"]].append(node["id"])
    categories = sorted(groups)
    permutations = [list(itertools.permutations(groups[category])) for category in categories]
    serialisations = []
    for choice in itertools.product(*permutations):
        mapping: dict[str, str] = {}
        for category, ordered in zip(categories, choice):
            for index, old_id in enumerate(ordered):
                mapping[old_id] = f"{category}:{index}"
        value = {
            "nodes": sorted((mapping[node["id"]], node["category"], tuple(sorted(node["attributes"].items()))) for node in graph["nodes"]),
            "unary": sorted((mapping[item["node"]], item["action"]) for item in graph["unary"]),
            "binary": sorted((mapping[item["source"]], item["type"], mapping[item["target"]]) for item in graph["binary"]),
            "counts": sorted((item["category"], item["bucket"]) for item in graph["counts"]),
            "scene": graph["scene"],
        }
        serialisations.append(json.dumps(value, sort_keys=True, separators=(",", ":")))
    return min(serialisations)


class MoondreamExtractor:
    def __init__(self, snapshot: str, prompt: str) -> None:
        import os
        import shutil
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        os.environ["HF_MODULES_CACHE"] = str(ROOT / "artifacts" / "downloads" / "p9_v2" / "modules_cache")
        from tokenizers import Tokenizer
        from transformers import AutoModelForCausalLM
        from transformers.dynamic_module_utils import _sanitize_module_name

        self.prompt = prompt
        # Transformers 4.57 only stages direct relative imports for a local
        # trust_remote_code model, but Moondream has transitive local imports.
        # Stage the exact already-reviewed root Python files into its isolated
        # dynamic-module cache before class discovery recursively inspects them.
        snapshot_path = Path(snapshot)
        module_path = Path(os.environ["HF_MODULES_CACHE"]) / "transformers_modules" / _sanitize_module_name(snapshot_path.name)
        module_path.mkdir(parents=True, exist_ok=True)
        (module_path / "__init__.py").touch()
        for source in snapshot_path.glob("*.py"):
            shutil.copy2(source, module_path / source.name)
        local_tokenizer = str(Path(snapshot) / "tokenizer.json")
        original_from_pretrained = Tokenizer.from_pretrained
        Tokenizer.from_pretrained = staticmethod(lambda *_args, **_kwargs: Tokenizer.from_file(local_tokenizer))
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                snapshot, revision=None, trust_remote_code=True, local_files_only=True,
                dtype=torch.float32, device_map={"": "cpu"}, low_cpu_mem_usage=True,
            )
        finally:
            Tokenizer.from_pretrained = original_from_pretrained
        self.model.eval()

    def __call__(self, image: Image.Image) -> str:
        with torch.inference_mode():
            result = self.model.query(
                image,
                self.prompt,
                settings={"temperature": 0.0, "max_tokens": 384, "variant": None},
            )
        if isinstance(result, dict):
            return str(result.get("answer", result))
        return str(result)


class SmolVLM2Extractor:
    def __init__(self, snapshot: str, prompt: str) -> None:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        from transformers import AutoModelForImageTextToText, AutoProcessor
        self.prompt = prompt
        self.processor = AutoProcessor.from_pretrained(snapshot, local_files_only=True)
        self.model = AutoModelForImageTextToText.from_pretrained(
            snapshot, local_files_only=True, dtype=torch.bfloat16,
            device_map={"": "cpu"}, low_cpu_mem_usage=True,
        )
        self.model.eval()

    def __call__(self, image: Image.Image) -> str:
        messages = [{"role": "user", "content": [{"type": "image", "image": image}, {"type": "text", "text": self.prompt}]}]
        inputs = self.processor.apply_chat_template(messages, add_generation_prompt=True, tokenize=True, return_dict=True, return_tensors="pt")
        with torch.inference_mode():
            output = self.model.generate(**inputs, do_sample=False, max_new_tokens=384)
        trimmed = output[:, inputs["input_ids"].shape[1]:]
        return self.processor.batch_decode(trimmed, skip_special_tokens=True)[0]


def load_extractor(backend: str, prompt: str) -> Callable[[Image.Image], str]:
    entry = model_entry(backend)
    snapshot = str(ROOT / entry["snapshot_relpath"])
    if backend == "moondream":
        if not entry.get("remote_code_review", {}).get("approved"):
            raise RuntimeError("Moondream remote code was not approved before execution")
        return MoondreamExtractor(snapshot, prompt)
    if backend == "smolvlm2":
        return SmolVLM2Extractor(snapshot, prompt)
    raise ValueError(backend)


def run_key(record: dict[str, Any], backend: str, revision: str, prompt: str, pass_name: str) -> str:
    value = {"fixture_id": record["fixture_id"], "image_sha256": record["image_sha256"], "backend": backend,
             "revision": revision, "prompt_sha256": sha256_text(prompt), "pass": pass_name,
             "config_sha256": sha256(CONFIG_PATH), "graph_sha256": sha256(GRAPH_PATH)}
    return sha256_text(json.dumps(value, sort_keys=True, separators=(",", ":")))


def infer(backend: str, run_id: str, limit: int | None, repeat_validation: bool, split: str | None = None) -> Path:
    prereg, graph_config = read_json(CONFIG_PATH), read_json(GRAPH_PATH)
    manifest = load_jsonl(CAPABILITY_PATH)
    if split is not None:
        manifest = [record for record in manifest if record["split"] == split]
    candidate = next(item for item in prereg["extractor_screen"]["candidates"] if
                     (backend == "moondream" and item["model_id"] == "vikhyatk/moondream2") or
                     (backend == "smolvlm2" and item["model_id"] == "HuggingFaceTB/SmolVLM2-2.2B-Instruct"))
    prompt = extraction_prompt(graph_config)
    tasks = [(record, "primary") for record in manifest]
    if repeat_validation:
        tasks.extend((record, "repeat") for record in manifest if record["split"] == "validation")
    if limit is not None:
        tasks = tasks[:limit]

    raw_dir = RESULT_ROOT / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    output_path = raw_dir / f"{backend}_{run_id}.jsonl"
    existing = load_jsonl(output_path) if output_path.exists() else []
    by_key = {item["run_key"]: item for item in existing}
    pending = [(record, pass_name, run_key(record, backend, candidate["revision"], prompt, pass_name))
               for record, pass_name in tasks]
    pending = [item for item in pending if item[2] not in by_key]
    print(f"backend={backend} run_id={run_id} cached={len(tasks)-len(pending)} pending={len(pending)}", flush=True)
    if not pending:
        return output_path

    extractor = load_extractor(backend, prompt)
    for number, (record, pass_name, key) in enumerate(pending, 1):
        image_path = ROOT / record["image_relpath"]
        started = time.perf_counter()
        gpu_peak = 0
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
        answer, parsed, error = "", None, None
        with PeakRSS() as memory:
            try:
                with Image.open(image_path) as source:
                    answer = extractor(source.convert("RGB"))
                parsed = normalise_graph(parse_json_answer(answer), graph_config)
            except Exception as exc:  # evidence records every model/schema failure
                error = f"{type(exc).__name__}: {exc}"
        if torch.cuda.is_available():
            gpu_peak = int(torch.cuda.max_memory_allocated())
        observation = {
            "run_key": key, "fixture_id": record["fixture_id"], "split": record["split"], "fixture_style": record["fixture_style"],
            "pass": pass_name, "backend": backend, "model_id": candidate["model_id"], "revision": candidate["revision"],
            "image_sha256": record["image_sha256"], "prompt_sha256": sha256_text(prompt), "answer": answer,
            "parsed_graph": parsed, "schema_valid": parsed is not None, "error": error,
            "elapsed_seconds": time.perf_counter() - started, "peak_rss_bytes": memory.peak, "peak_gpu_allocated_bytes": gpu_peak,
        }
        with output_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(observation, sort_keys=True, separators=(",", ":")) + "\n")
        print(f"{number}/{len(pending)} {record['fixture_id']} {pass_name} valid={parsed is not None} seconds={observation['elapsed_seconds']:.2f} error={error}", flush=True)
    return output_path


def analyze_futility(backend: str, run_id: str) -> dict[str, Any]:
    prereg = read_json(CONFIG_PATH)
    manifest = load_jsonl(CAPABILITY_PATH)
    validation_total = sum(item["split"] == "validation" for item in manifest)
    observations = [
        item for item in load_jsonl(RESULT_ROOT / "raw" / f"{backend}_{run_id}.jsonl")
        if item["pass"] == "primary" and item["split"] == "validation"
    ]
    if not observations:
        raise RuntimeError("futility analysis requires at least one validation observation")
    invalid = sum(not item["schema_valid"] for item in observations)
    best_case_valid = validation_total - invalid
    best_case_valid_rate = best_case_valid / validation_total
    minimum_failure_rate = invalid / validation_total
    advance = prereg["extractor_screen"]["advance"]
    limits = prereg["extractor_screen"]["hard_limits"]
    validity_impossible = best_case_valid_rate < advance["schema_valid_rate_min"]
    failure_impossible = minimum_failure_rate > limits["maximum_failure_rate"]
    if not (validity_impossible or failure_impossible):
        raise RuntimeError("observations do not yet make a preregistered gate check impossible")
    elapsed = [item["elapsed_seconds"] for item in observations]
    impossible_checks = []
    if validity_impossible:
        impossible_checks.append("schema-valid rate")
    if failure_impossible:
        impossible_checks.append("failure rate")
    result = {
        "schema_version": "p9a-capability-futility-result-v2",
        "backend": backend,
        "run_id": run_id,
        "manifest_sha256": sha256(CAPABILITY_PATH),
        "config_sha256": sha256(CONFIG_PATH),
        "graph_sha256": sha256(GRAPH_PATH),
        "validation_images_planned": validation_total,
        "validation_images_observed": len(observations),
        "schema_invalid_observed": invalid,
        "best_case_if_every_unobserved_image_passed": {
            "schema_valid": best_case_valid,
            "schema_valid_rate": best_case_valid_rate,
            "failure_rate": minimum_failure_rate,
        },
        "fatal_checks": {
            "schema_valid_rate": {
                "best_case_value": best_case_valid_rate,
                "threshold": advance["schema_valid_rate_min"],
                "pass_possible": not validity_impossible,
            },
            "failure_rate": {
                "best_case_value": minimum_failure_rate,
                "threshold": limits["maximum_failure_rate"],
                "pass_possible": not failure_impossible,
            },
        },
        "observed_resource_descriptive": {
            "median_seconds": statistics.median(elapsed),
            "peak_rss_bytes": max(item["peak_rss_bytes"] for item in observations),
            "peak_gpu_allocated_bytes": max(item["peak_gpu_allocated_bytes"] for item in observations),
        },
        "metrics_not_estimated": [
            "atom precision/recall/F1 and bootstrap intervals",
            "full-set latency median",
            "determinism",
            "structured error strata",
        ],
        "advance": False,
        "early_stop_reason": (
            "Logical futility: all P9A checks must pass, but the observed validation schema failures make "
            + " and ".join(impossible_checks)
            + " impossible even if every unobserved image passed."
        ),
        "selection_rule": "No candidate replacement, prompt change, output repair, or authentication outcome was used.",
    }
    aggregate_dir = RESULT_ROOT / "aggregate"
    aggregate_dir.mkdir(parents=True, exist_ok=True)
    output = aggregate_dir / f"{backend}_capability_v2.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def iou(a: list[float], b: list[float]) -> float:
    left, top = max(a[0], b[0]), max(a[1], b[1])
    right, bottom = min(a[2], b[2]), min(a[3], b[3])
    intersection = max(0.0, right-left) * max(0.0, bottom-top)
    union = (a[2]-a[0])*(a[3]-a[1]) + (b[2]-b[0])*(b[3]-b[1]) - intersection
    return intersection / union if union else 0.0


def object_matches(gt: dict[str, Any], pred: dict[str, Any]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    categories = sorted(set(node["category"] for node in gt["nodes"]) | set(node["category"] for node in pred["nodes"]))
    for category in categories:
        gt_nodes = [node for node in gt["nodes"] if node["category"] == category]
        pred_nodes = [node for node in pred["nodes"] if node["category"] == category]
        if not gt_nodes or not pred_nodes:
            continue
        matrix = np.array([[-iou(g["bbox"], p["bbox"]) for p in pred_nodes] for g in gt_nodes])
        rows, columns = linear_sum_assignment(matrix)
        for row, column in zip(rows, columns):
            if -matrix[row, column] >= 0.5:
                mapping[pred_nodes[column]["id"]] = gt_nodes[row]["id"]
    return mapping


def triplet(tp: int, fp: int, fn: int) -> dict[str, int]:
    return {"tp": int(tp), "fp": int(fp), "fn": int(fn)}


def score_image(gt: dict[str, Any], pred: dict[str, Any] | None, graph_config: dict[str, Any]) -> dict[str, dict[str, int]]:
    if pred is None:
        action_gt = len(gt["unary"]) + sum(edge["type"] in graph_config["binary_actions"] for edge in gt["binary"])
        relation_gt = sum(edge["type"] in graph_config["spatial_relations"] for edge in gt["binary"])
        return {
            "object": triplet(0, 0, len(gt["nodes"])),
            "attribute": triplet(0, 0, sum(len(node["attributes"]) for node in gt["nodes"])),
            "count": triplet(0, 0, len(gt["counts"])),
            "action": triplet(0, 0, action_gt),
            "relation": triplet(0, 0, relation_gt),
            "scene": triplet(0, 0, 1),
        }
    mapping = object_matches(gt, pred)
    object_score = triplet(len(mapping), len(pred["nodes"])-len(mapping), len(gt["nodes"])-len(mapping))

    gt_attrs = {(node["id"], key, value) for node in gt["nodes"] for key, value in node["attributes"].items()}
    pred_attrs = {(mapping.get(node["id"], f"unmatched:{node['id']}"), key, value) for node in pred["nodes"] for key, value in node["attributes"].items()}
    gt_counts = {(item["category"], item["bucket"]) for item in gt["counts"]}
    pred_counts = {(item["category"], item["bucket"]) for item in pred["counts"]}

    gt_actions = {(item["node"], "unary", item["action"], "") for item in gt["unary"]}
    gt_actions |= {(item["source"], "binary", item["type"], item["target"]) for item in gt["binary"] if item["type"] in graph_config["binary_actions"]}
    pred_actions = {(mapping.get(item["node"], f"unmatched:{item['node']}"), "unary", item["action"], "") for item in pred["unary"]}
    pred_actions |= {(mapping.get(item["source"], f"unmatched:{item['source']}"), "binary", item["type"], mapping.get(item["target"], f"unmatched:{item['target']}")) for item in pred["binary"] if item["type"] in graph_config["binary_actions"]}
    gt_relations = {(item["source"], item["type"], item["target"]) for item in gt["binary"] if item["type"] in graph_config["spatial_relations"]}
    pred_relations = {(mapping.get(item["source"], f"unmatched:{item['source']}"), item["type"], mapping.get(item["target"], f"unmatched:{item['target']}")) for item in pred["binary"] if item["type"] in graph_config["spatial_relations"]}

    def set_score(expected: set[Any], observed: set[Any]) -> dict[str, int]:
        return triplet(len(expected & observed), len(observed - expected), len(expected - observed))

    return {
        "object": object_score, "attribute": set_score(gt_attrs, pred_attrs), "count": set_score(gt_counts, pred_counts),
        "action": set_score(gt_actions, pred_actions), "relation": set_score(gt_relations, pred_relations),
        "scene": set_score({gt["scene"]}, {pred["scene"]}),
    }


def f1(counts: dict[str, int]) -> dict[str, float]:
    tp, fp, fn = counts["tp"], counts["fp"], counts["fn"]
    precision = tp / (tp + fp) if tp + fp else (1.0 if fn == 0 else 0.0)
    recall = tp / (tp + fn) if tp + fn else 1.0
    value = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": value}


def aggregate(scores: list[dict[str, dict[str, int]]]) -> dict[str, dict[str, float | int]]:
    result: dict[str, dict[str, float | int]] = {}
    for task in ("object", "attribute", "count", "action", "relation", "scene"):
        counts = {key: sum(score[task][key] for score in scores) for key in ("tp", "fp", "fn")}
        result[task] = counts | f1(counts)
    result["macro"] = {"f1": statistics.mean(float(result[task]["f1"]) for task in ("object", "attribute", "count", "action", "relation", "scene"))}
    return result


def bootstrap(scores: list[dict[str, dict[str, int]]], repetitions: int, seed: int) -> dict[str, dict[str, float]]:
    rng = np.random.default_rng(seed)
    values: dict[str, list[float]] = defaultdict(list)
    for _ in range(repetitions):
        sampled = [scores[index] for index in rng.integers(0, len(scores), size=len(scores))]
        metrics = aggregate(sampled)
        values["macro"].append(float(metrics["macro"]["f1"]))
        for task in ("object", "attribute", "count", "action", "relation", "scene"):
            values[task].append(float(metrics[task]["f1"]))
    return {task: {"lower": float(np.quantile(series, 0.025)), "upper": float(np.quantile(series, 0.975))} for task, series in values.items()}


def analyze(backend: str, run_id: str = "primary") -> dict[str, Any]:
    prereg, graph_config = read_json(CONFIG_PATH), read_json(GRAPH_PATH)
    manifest = {item["fixture_id"]: item for item in load_jsonl(CAPABILITY_PATH)}
    observations = load_jsonl(RESULT_ROOT / "raw" / f"{backend}_{run_id}.jsonl")
    primary = {item["fixture_id"]: item for item in observations if item["pass"] == "primary"}
    repeats = {item["fixture_id"]: item for item in observations if item["pass"] == "repeat"}
    if len(primary) != len(manifest) or len(repeats) != sum(item["split"] == "validation" for item in manifest.values()):
        raise RuntimeError(f"incomplete primary run: primary={len(primary)} repeat={len(repeats)}")
    validation_ids = sorted(key for key, item in manifest.items() if item["split"] == "validation")
    scores = [score_image(normalise_graph(manifest[key]["graph"], graph_config), primary[key]["parsed_graph"], graph_config) for key in validation_ids]
    metrics = aggregate(scores)
    intervals = bootstrap(scores, prereg["uncertainty"]["bootstrap_repetitions"], prereg["uncertainty"]["bootstrap_seed"])
    valid = sum(primary[key]["schema_valid"] for key in validation_ids)
    deterministic = 0
    for key in validation_ids:
        first, second = primary[key]["parsed_graph"], repeats[key]["parsed_graph"]
        if first is not None and second is not None and canonical_graph(first) == canonical_graph(second):
            deterministic += 1
    elapsed = [item["elapsed_seconds"] for item in primary.values()]
    peak_rss = max(item["peak_rss_bytes"] for item in primary.values())
    peak_gpu = max(item["peak_gpu_allocated_bytes"] for item in primary.values())
    advance = prereg["extractor_screen"]["advance"]
    limits = prereg["extractor_screen"]["hard_limits"]
    checks = {
        "schema_valid_rate": {"value": valid/len(validation_ids), "threshold": advance["schema_valid_rate_min"], "pass": valid/len(validation_ids) >= advance["schema_valid_rate_min"]},
        "failure_rate": {"value": 1-valid/len(validation_ids), "threshold": limits["maximum_failure_rate"], "pass": 1-valid/len(validation_ids) <= limits["maximum_failure_rate"]},
        "macro_f1": {"value": metrics["macro"]["f1"], "threshold": advance["macro_atom_f1_min"], "pass": metrics["macro"]["f1"] >= advance["macro_atom_f1_min"]},
        "macro_f1_lower": {"value": intervals["macro"]["lower"], "threshold": advance["macro_atom_f1_bootstrap_lower_min"], "pass": intervals["macro"]["lower"] >= advance["macro_atom_f1_bootstrap_lower_min"]},
        "determinism": {"value": deterministic/len(validation_ids), "threshold": advance["deterministic_canonical_equality_min"], "pass": deterministic/len(validation_ids) >= advance["deterministic_canonical_equality_min"]},
        "median_seconds": {"value": statistics.median(elapsed), "threshold": limits["maximum_median_seconds_per_image"], "pass": statistics.median(elapsed) <= limits["maximum_median_seconds_per_image"]},
        "peak_rss_gib": {"value": peak_rss/(1024**3), "threshold": limits["maximum_system_ram_gib"], "pass": peak_rss/(1024**3) <= limits["maximum_system_ram_gib"]},
    }
    for task in ("object", "count", "action", "relation"):
        checks[f"{task}_f1"] = {"value": metrics[task]["f1"], "threshold": advance["critical_type_f1_min"], "pass": metrics[task]["f1"] >= advance["critical_type_f1_min"]}
        checks[f"{task}_f1_lower"] = {"value": intervals[task]["lower"], "threshold": advance["critical_type_f1_bootstrap_lower_min"], "pass": intervals[task]["lower"] >= advance["critical_type_f1_bootstrap_lower_min"]}
    result = {
        "schema_version": "p9a-capability-result-v2", "backend": backend, "run_id": run_id,
        "manifest_sha256": sha256(CAPABILITY_PATH), "config_sha256": sha256(CONFIG_PATH), "graph_sha256": sha256(GRAPH_PATH),
        "validation_images": len(validation_ids), "metrics": metrics, "bootstrap_95": intervals,
        "schema_valid_validation": valid, "deterministic_equal_validation": deterministic,
        "resource": {"median_seconds": statistics.median(elapsed), "peak_rss_bytes": peak_rss, "peak_gpu_allocated_bytes": peak_gpu,
                     "confidence_or_calibration": "unavailable from constrained generative output; recorded as a limitation"},
        "checks": checks, "advance": all(item["pass"] for item in checks.values()),
        "selection_rule": "all preregistered capability and resource checks must pass; no authentication outcome used",
    }
    aggregate_dir = RESULT_ROOT / "aggregate"
    aggregate_dir.mkdir(parents=True, exist_ok=True)
    output = aggregate_dir / f"{backend}_capability_v2.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    infer_parser = sub.add_parser("infer")
    infer_parser.add_argument("backend", choices=["moondream", "smolvlm2"])
    infer_parser.add_argument("--run-id", default="primary")
    infer_parser.add_argument("--limit", type=int)
    infer_parser.add_argument("--repeat-validation", action="store_true")
    infer_parser.add_argument("--split", choices=["development", "validation"])
    analyze_parser = sub.add_parser("analyze")
    analyze_parser.add_argument("backend", choices=["moondream", "smolvlm2"])
    analyze_parser.add_argument("--run-id", default="primary")
    futility_parser = sub.add_parser("analyze-futility")
    futility_parser.add_argument("backend", choices=["moondream", "smolvlm2"])
    futility_parser.add_argument("--run-id", default="futility")
    args = parser.parse_args()
    if args.command == "infer":
        print(infer(args.backend, args.run_id, args.limit, args.repeat_validation, args.split))
    elif args.command == "analyze":
        print(json.dumps(analyze(args.backend, args.run_id), indent=2, sort_keys=True))
    else:
        print(json.dumps(analyze_futility(args.backend, args.run_id), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
