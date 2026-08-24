"""Run the cheap P4 model/backend screening checks.

Outputs are engineering observations, not publication results. Large D1 generator
weights and the P3 image corpus are deliberately not acquired here.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import math
import os
import platform
import re
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable, Iterable


ROOT = Path(__file__).resolve().parents[2]
SCREEN_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = SCREEN_ROOT / "config" / "screen_v1.json"
DEFAULT_OUTPUT = ROOT / "results" / "p4" / "screen_v1.json"
sys.path.insert(0, str(ROOT / "prototype"))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        result = json.load(handle)
    if not isinstance(result, dict):
        raise TypeError(f"Expected JSON object: {path}")
    return result


def resolve_config_path(value: str) -> Path:
    return (CONFIG_PATH.parent / value).resolve()


class PeakRSS:
    """Best-effort process RSS sampler for cross-platform smoke metadata."""

    def __init__(self) -> None:
        import psutil

        self._process = psutil.Process()
        self._peak = self._process.memory_info().rss
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._sample, daemon=True)

    def _sample(self) -> None:
        while not self._stop.wait(0.01):
            with contextlib.suppress(Exception):
                self._peak = max(self._peak, self._process.memory_info().rss)

    def __enter__(self) -> "PeakRSS":
        self._thread.start()
        return self

    def __exit__(self, *_: object) -> None:
        self._stop.set()
        self._thread.join(timeout=1)
        with contextlib.suppress(Exception):
            self._peak = max(self._peak, self._process.memory_info().rss)

    @property
    def peak_mib(self) -> float:
        return round(self._peak / (1024 * 1024), 2)


def timed(call: Callable[[], Any]) -> tuple[Any, float, float]:
    start = time.perf_counter()
    with PeakRSS() as memory:
        result = call()
    return result, round(time.perf_counter() - start, 6), memory.peak_mib


def make_fixture(name: str):
    from PIL import Image, ImageDraw

    image = Image.new("RGB", (256, 256), "white")
    draw = ImageDraw.Draw(image)
    if name == "left_right":
        draw.rectangle((25, 80, 105, 160), fill=(220, 30, 30), outline="black", width=3)
        draw.ellipse((155, 80, 235, 160), fill=(30, 80, 220), outline="black", width=3)
        expected = ["square", "red", "circle", "blue", "left"]
    elif name == "count_above":
        draw.ellipse((45, 35, 105, 95), fill=(25, 170, 70), outline="black", width=3)
        draw.ellipse((150, 35, 210, 95), fill=(25, 170, 70), outline="black", width=3)
        draw.rectangle((60, 160, 200, 220), fill=(30, 30, 30), outline="black", width=3)
        expected = ["circle", "green", "2", "rectangle", "above"]
    elif name == "inside":
        draw.rectangle((35, 35, 220, 220), fill=(130, 60, 170), outline="black", width=4)
        draw.polygon(((128, 70), (75, 175), (181, 175)), fill=(245, 205, 30), outline="black")
        expected = ["triangle", "yellow", "square", "purple", "inside"]
    else:
        raise ValueError(f"Unknown fixture: {name}")
    return image, expected


def schema_prompt() -> str:
    return (
        "Return JSON only, with no markdown or explanation. Describe visible semantics using exactly this root shape: "
        '{"schema_version":"structured-extraction-v1","objects":[{"id":"object_1","label":"...","confidence":null}],'
        '"attributes":[{"subject":"object_1","name":"colour","value":"...","confidence":null}],'
        '"counts":[{"object_id":"object_1","value":1,"confidence":null}],'
        '"actions":[],"relations":[{"subject":"object_1","predicate":"left_of","object":"object_2","confidence":null}],'
        '"scenes":[],"warnings":[]}. '
        "Use lowercase snake_case IDs and labels. Include only visible facts. Use confidence null."
    )


def extract_json_object(text: str) -> dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("No JSON object in model output")
    value = json.loads(text[start : end + 1])
    if not isinstance(value, dict):
        raise TypeError("Structured output is not an object")
    return value


def validate_structure(value: dict[str, Any], schema_path: Path) -> None:
    import jsonschema

    jsonschema.Draft202012Validator(read_json(schema_path)).validate(value)


def snapshot_hashes(model_id: str, revision: str) -> dict[str, Any]:
    from huggingface_hub import snapshot_download

    snapshot = Path(snapshot_download(model_id, revision=revision, local_files_only=True))
    allowed = {".safetensors", ".bin", ".json", ".model", ".txt", ".py", ".md"}
    files = []
    tree = hashlib.sha256()
    for path in sorted(p for p in snapshot.rglob("*") if p.is_file() and p.suffix.lower() in allowed):
        relative = path.relative_to(snapshot).as_posix()
        digest = hashlib.sha256()
        size = 0
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                size += len(chunk)
                digest.update(chunk)
        file_hash = digest.hexdigest()
        tree.update(relative.encode("utf-8") + b"\0" + file_hash.encode("ascii") + b"\0")
        files.append({"path": relative, "bytes": size, "sha256": file_hash})
    return {
        "model_id": model_id,
        "revision": revision,
        "artifact_tree_sha256": tree.hexdigest(),
        "hashed_file_count": len(files),
        "hashed_bytes": sum(item["bytes"] for item in files),
        "files": files,
    }


def screen_tiny_generator(config: dict[str, Any]) -> dict[str, Any]:
    import torch
    from diffusers import DiffusionPipeline

    model_id = config["model_id"]
    revision = config["revision"]

    def load():
        pipeline = DiffusionPipeline.from_pretrained(
            model_id,
            revision=revision,
            torch_dtype=torch.float32,
            safety_checker=None,
        )
        pipeline.set_progress_bar_config(disable=True)
        return pipeline.to("cpu")

    pipeline, load_seconds, load_peak = timed(load)

    def generate(seed: int) -> tuple[str, tuple[int, int]]:
        generator = torch.Generator(device="cpu").manual_seed(seed)
        image = pipeline(
            config["prompt"],
            generator=generator,
            width=config["width"],
            height=config["height"],
            num_inference_steps=config["inference_steps"],
            guidance_scale=config["guidance_scale"],
            output_type="pil",
        ).images[0].convert("RGB")
        return sha256_bytes(image.tobytes()), image.size

    repeated = []
    for _ in range(2):
        value, seconds, peak = timed(lambda: generate(config["seed"]))
        repeated.append({"rgb_sha256": value[0], "size": list(value[1]), "latency_seconds": seconds, "peak_process_rss_mib": peak})
    different, seconds, peak = timed(lambda: generate(config["different_seed"]))
    artifact = snapshot_hashes(model_id, revision)
    return {
        "backend_id": "fixture_tiny_sd",
        "status": "completed-interface-fixture",
        "interpretation": config["interpretation"],
        "load_seconds": load_seconds,
        "load_peak_process_rss_mib": load_peak,
        "fixed_seed_runs": repeated,
        "fixed_seed_repeat_equal": repeated[0]["rgb_sha256"] == repeated[1]["rgb_sha256"],
        "different_seed_run": {"rgb_sha256": different[0], "size": list(different[1]), "latency_seconds": seconds, "peak_process_rss_mib": peak},
        "different_seed_differs": repeated[0]["rgb_sha256"] != different[0],
        "artifact": artifact,
        "semantic_coverage": None,
        "publication_result": False,
    }


def screen_smolvlm(config: dict[str, Any], schema_path: Path) -> dict[str, Any]:
    import torch
    from transformers import AutoModelForVision2Seq, AutoProcessor

    model_id = config["model_id"]
    revision = config["revision"]

    def load():
        processor = AutoProcessor.from_pretrained(model_id, revision=revision)
        model = AutoModelForVision2Seq.from_pretrained(
            model_id,
            revision=revision,
            torch_dtype=torch.float32,
            _attn_implementation="eager",
            low_cpu_mem_usage=True,
        ).to("cpu")
        model.eval()
        return processor, model

    (processor, model), load_seconds, load_peak = timed(load)

    def infer(image) -> str:
        messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": schema_prompt()}]}]
        prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
        inputs = processor(text=prompt, images=[image], return_tensors="pt").to("cpu")
        with torch.inference_mode():
            generated = model.generate(
                **inputs,
                max_new_tokens=config["max_new_tokens"],
                do_sample=config["do_sample"],
            )
        new_tokens = generated[:, inputs["input_ids"].shape[1] :]
        return processor.batch_decode(new_tokens, skip_special_tokens=True)[0].strip()

    fixtures = []
    total_expected = 0
    total_found = 0
    schema_failures = 0
    deterministic = True
    for fixture_name in config["fixtures"]:
        image, expected = make_fixture(fixture_name)
        runs = []
        for _ in range(2):
            raw, seconds, peak = timed(lambda image=image: infer(image))
            parsed = None
            error = None
            try:
                parsed = extract_json_object(raw)
                validate_structure(parsed, schema_path)
            except Exception as exc:  # screening records schema failures verbatim
                error = f"{type(exc).__name__}: {exc}"
            runs.append(
                {
                    "raw_output": raw,
                    "output_sha256": sha256_bytes(raw.encode("utf-8")),
                    "latency_seconds": seconds,
                    "peak_process_rss_mib": peak,
                    "schema_valid": error is None,
                    "schema_error": error,
                    "parsed": parsed,
                }
            )
        deterministic &= runs[0]["output_sha256"] == runs[1]["output_sha256"]
        schema_failures += sum(not run["schema_valid"] for run in runs)
        coverage_text = json.dumps(runs[0]["parsed"], sort_keys=True).casefold() if runs[0]["parsed"] else runs[0]["raw_output"].casefold()
        found = [term for term in expected if term.casefold() in coverage_text]
        total_expected += len(expected)
        total_found += len(found)
        fixtures.append(
            {
                "fixture_id": fixture_name,
                "fixture_rgb_sha256": sha256_bytes(image.tobytes()),
                "expected_probe_terms": expected,
                "found_probe_terms": found,
                "probe_coverage": round(len(found) / len(expected), 4),
                "runs": runs,
            }
        )
    artifact = snapshot_hashes(model_id, revision)
    return {
        "backend_id": "e_smolvlm_256m",
        "status": "completed-lightweight-structured-screen",
        "load_seconds": load_seconds,
        "load_peak_process_rss_mib": load_peak,
        "fixed_input_repeat_equal": deterministic,
        "schema_failures": schema_failures,
        "schema_attempts": len(config["fixtures"]) * 2,
        "probe_semantic_coverage": round(total_found / total_expected, 4),
        "coverage_interpretation": "lexical probe on procedural fixtures; candidate-elimination evidence only",
        "fixtures": fixtures,
        "artifact": artifact,
        "publication_result": False,
    }


def screen_siglip(config: dict[str, Any]) -> dict[str, Any]:
    import torch
    import torch.nn.functional as functional
    from transformers import AutoModel, AutoProcessor

    model_id = config["model_id"]
    revision = config["revision"]

    def load():
        processor = AutoProcessor.from_pretrained(model_id, revision=revision)
        model = AutoModel.from_pretrained(model_id, revision=revision, torch_dtype=torch.float32).to("cpu")
        model.eval()
        return processor, model

    (processor, model), load_seconds, load_peak = timed(load)
    images = [make_fixture(name)[0] for name in config["fixtures"]]
    labels = [
        "a red square to the left of a blue circle",
        "two green circles above a black rectangle",
        "a yellow triangle inside a purple square",
    ]

    def infer() -> dict[str, Any]:
        inputs = processor(text=labels, images=images, padding="max_length", return_tensors="pt")
        with torch.inference_mode():
            outputs = model(**inputs)
        image_embeddings = functional.normalize(outputs.image_embeds.float(), p=2, dim=-1)
        text_embeddings = functional.normalize(outputs.text_embeds.float(), p=2, dim=-1)
        similarity = image_embeddings @ text_embeddings.T
        payload = image_embeddings.numpy().tobytes() + text_embeddings.numpy().tobytes()
        return {
            "embedding_sha256": sha256_bytes(payload),
            "image_shape": list(image_embeddings.shape),
            "text_shape": list(text_embeddings.shape),
            "similarity": [[round(float(value), 6) for value in row] for row in similarity],
            "top_label_indices": similarity.argmax(dim=1).tolist(),
        }

    runs = []
    for _ in range(2):
        value, seconds, peak = timed(infer)
        runs.append({**value, "latency_seconds": seconds, "peak_process_rss_mib": peak})
    artifact = snapshot_hashes(model_id, revision)
    return {
        "backend_id": "b_siglip_base_224",
        "status": "completed-dense-image-screen",
        "load_seconds": load_seconds,
        "load_peak_process_rss_mib": load_peak,
        "fixed_input_repeat_equal": runs[0]["embedding_sha256"] == runs[1]["embedding_sha256"],
        "fixture_top_label_matches": sum(index == expected for expected, index in enumerate(runs[0]["top_label_indices"])),
        "fixture_count": len(images),
        "runs": runs,
        "artifact": artifact,
        "publication_result": False,
    }


def screen_minilm(config: dict[str, Any]) -> dict[str, Any]:
    import torch
    import torch.nn.functional as functional
    from transformers import AutoModel, AutoTokenizer

    model_id = config["model_id"]
    revision = config["revision"]
    manifest_path = resolve_config_path(config["manifest"])
    texts = [json.loads(line)["core_prompt"] for line in manifest_path.read_text(encoding="utf-8").splitlines()]

    def load():
        tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)
        model = AutoModel.from_pretrained(model_id, revision=revision, torch_dtype=torch.float32).to("cpu")
        model.eval()
        return tokenizer, model

    (tokenizer, model), load_seconds, load_peak = timed(load)

    def infer() -> dict[str, Any]:
        encoded = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
        with torch.inference_mode():
            output = model(**encoded)[0]
        mask = encoded["attention_mask"].unsqueeze(-1).expand(output.size()).float()
        pooled = torch.sum(output * mask, dim=1) / torch.clamp(mask.sum(dim=1), min=1e-9)
        embeddings = functional.normalize(pooled, p=2, dim=1)
        return {
            "embedding_sha256": sha256_bytes(embeddings.numpy().tobytes()),
            "shape": list(embeddings.shape),
            "finite": bool(torch.isfinite(embeddings).all()),
        }

    runs = []
    for _ in range(2):
        value, seconds, peak = timed(infer)
        runs.append({**value, "latency_seconds": seconds, "peak_process_rss_mib": peak})
    artifact = snapshot_hashes(model_id, revision)
    return {
        "backend_id": "b_minilm_text",
        "status": "completed-dense-text-screen",
        "input_count": len(texts),
        "load_seconds": load_seconds,
        "load_peak_process_rss_mib": load_peak,
        "fixed_input_repeat_equal": runs[0]["embedding_sha256"] == runs[1]["embedding_sha256"],
        "runs": runs,
        "artifact": artifact,
        "publication_result": False,
    }


def controlled_text_extract(text: str) -> dict[str, Any]:
    """Transparent P4 lower-bound parser for the controlled English fixture grammar."""
    normal = re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()
    object_terms = [
        "axolotl", "bicycle", "book", "boulder", "box", "cat", "chef", "clock", "cup",
        "dog", "fox", "frisbee", "motorcycle", "orange", "owl", "robot", "sailboat",
        "scarf", "teapot", "tree",
    ]
    objects = []
    for term in object_terms:
        plural = term + "s"
        if re.search(rf"\b(?:{re.escape(term)}|{re.escape(plural)})\b", normal):
            objects.append({"id": term, "label": term, "confidence": None})
    attributes = []
    for value in ("blue", "bright", "ceramic", "glass", "green", "red", "white", "yellow"):
        if re.search(rf"\b{value}\b", normal) and objects:
            subject = "scarf" if "scarf" in normal else "teapot" if "teapot" in normal else "owl" if "owl" in normal else "orange" if "orange" in normal else objects[0]["id"]
            name = "material" if value in {"ceramic", "glass"} else "colour"
            attributes.append({"subject": subject, "name": name, "value": value, "confidence": None})
    count_map = {"one": 1, "single": 1, "pair": 2, "two": 2, "three": 3}
    counts = []
    for word, number in count_map.items():
        if re.search(rf"\b{word}\b", normal) and objects:
            counts.append({"object_id": objects[0]["id"], "value": number, "confidence": None})
            break
    actions = []
    for surface, canonical in (("catch", "catch"), ("carry", "carry"), ("carries", "carry"), ("carrying", "carry"), ("juggle", "juggle"), ("juggles", "juggle"), ("holding", "hold"), ("holds", "hold"), ("watch", "watch"), ("watches", "watch")):
        if re.search(rf"\b{surface}\w*\b", normal) and objects:
            actions.append({"subject": objects[0]["id"], "verb": canonical, "object": objects[1]["id"] if len(objects) > 1 else None, "confidence": None})
            break
    relations = []
    relation_map = (("left of", "left_of"), ("right of", "right_of"), ("between", "between"), ("beside", "beside"), ("next to", "beside"), ("above", "above"), ("below", "below"), ("under", "below"))
    for surface, canonical in relation_map:
        if surface in normal and len(objects) > 1:
            relations.append({"subject": objects[0]["id"], "predicate": canonical, "object": objects[1]["id"], "confidence": None})
            break
    scenes = []
    for surface, canonical in (("aquarium", "aquarium"), ("sunrise", "coastal_sunrise"), ("coast at night", "coastal_night"), ("forest", "forest"), ("kitchen", "kitchen"), ("library", "library"), ("lunar", "lunar"), ("warehouse", "warehouse")):
        if surface in normal:
            scenes.append({"label": canonical, "confidence": None})
            break
    return {
        "schema_version": "structured-extraction-v1",
        "objects": objects,
        "attributes": attributes,
        "counts": counts,
        "actions": actions,
        "relations": relations,
        "scenes": scenes,
        "warnings": ["controlled_grammar_lower_bound"],
    }


def screen_controlled_text(config: dict[str, Any], schema_path: Path) -> dict[str, Any]:
    manifest_path = resolve_config_path(config["manifest"])
    texts = [json.loads(line)["core_prompt"] for line in manifest_path.read_text(encoding="utf-8").splitlines()]

    def infer() -> list[dict[str, Any]]:
        outputs = [controlled_text_extract(text) for text in texts]
        for output in outputs:
            validate_structure(output, schema_path)
        return outputs

    runs = []
    for _ in range(2):
        outputs, seconds, peak = timed(infer)
        runs.append(
            {
                "output_sha256": sha256_bytes(canonical_bytes(outputs)),
                "latency_seconds": seconds,
                "peak_process_rss_mib": peak,
                "schema_valid_count": len(outputs),
            }
        )
    return {
        "backend_id": "b_controlled_text_parser",
        "status": "completed-structured-text-lower-bound",
        "interpretation": config["interpretation"],
        "input_count": len(texts),
        "fixed_input_repeat_equal": runs[0]["output_sha256"] == runs[1]["output_sha256"],
        "schema_failures": 0,
        "runs": runs,
        "publication_result": False,
    }


def environment_metadata() -> dict[str, Any]:
    import accelerate
    import diffusers
    import jsonschema
    import torch
    import transformers

    nvidia = None
    try:
        command = ["nvidia-smi", "--query-gpu=name,memory.total,driver_version,compute_cap", "--format=csv,noheader"]
        nvidia = subprocess.run(command, check=True, capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        pass
    return {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "torch": torch.__version__,
        "torch_cuda_build": torch.version.cuda,
        "torch_cuda_available": torch.cuda.is_available(),
        "transformers": transformers.__version__,
        "diffusers": diffusers.__version__,
        "accelerate": accelerate.__version__,
        "jsonschema": getattr(jsonschema, "__version__", "unknown"),
        "nvidia_smi": nvidia,
        "cpu_threads": os.cpu_count(),
    }


def validate_report(report: dict[str, Any]) -> None:
    required = {"generator_fixture", "structured_vlm", "dense_image", "dense_text", "structured_text"}
    missing = required - set(report["screens"])
    if missing:
        raise ValueError(f"Missing mandatory screens: {sorted(missing)}")
    generator = report["screens"]["generator_fixture"]
    if not generator["fixed_seed_repeat_equal"] or not generator["different_seed_differs"]:
        raise ValueError("Generator fixture determinism check failed")
    for key in ("structured_vlm", "dense_image", "dense_text", "structured_text"):
        if not report["screens"][key]["fixed_input_repeat_equal"]:
            raise ValueError(f"Repeatability failed: {key}")


def run(config: dict[str, Any]) -> dict[str, Any]:
    schema_path = resolve_config_path(config["structured_schema"])
    screens: dict[str, Any] = {}
    screens["generator_fixture"] = screen_tiny_generator(config["generator_fixture"])
    screens["structured_vlm"] = screen_smolvlm(config["structured_vlm"], schema_path)
    screens["dense_image"] = screen_siglip(config["dense_image"])
    screens["dense_text"] = screen_minilm(config["dense_text"])
    screens["structured_text"] = screen_controlled_text(config["structured_text"], schema_path)
    report = {
        "$schema_version": "semantic-secrets-p4-screen-result-v1",
        "screen_id": config["screen_id"],
        "run_kind": "engineering-screen-not-publication-result",
        "config_sha256": sha256_bytes(canonical_bytes(config)),
        "environment": environment_metadata(),
        "screens": screens,
        "boundaries": {
            "p3_manifest_rows_consumed": 36,
            "p3_images_generated": 0,
            "d1_production_generator_weights_acquired": False,
            "security_or_usability_claim": False,
        },
    }
    validate_report(report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if args.validate_only:
        report = read_json(args.output)
        validate_report(report)
    else:
        config = read_json(args.config)
        report = run(config)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    summary = {
        "output": str(args.output),
        "screens": {key: value["status"] for key, value in report["screens"].items()},
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
