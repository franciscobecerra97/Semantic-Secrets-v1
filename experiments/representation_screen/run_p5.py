"""Run the bounded P5 smoke representation comparison.

This runner checkpoints model outputs so long local inference can resume. Generated
images live under an ignored cache; compact hashes, raw Florence text, canonical
atoms, embeddings, and engineering metrics are versioned results.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
SCREEN_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = SCREEN_ROOT / "config" / "p5_smoke_v1.json"
INPUTS_PATH = ROOT / "experiments" / "datasets" / "manifests" / "smoke_v1.inputs.jsonl"
LABELS_PATH = ROOT / "experiments" / "datasets" / "manifests" / "smoke_v1.labels.jsonl"
RESULT_ROOT = ROOT / "results" / "p5"
CACHE_ROOT = RESULT_ROOT / "cache"
IMAGE_ROOT = CACHE_ROOT / "images"
FLORENCE_CACHE = CACHE_ROOT / "florence"
GENERATION_MANIFEST = RESULT_ROOT / "generation_manifest_smoke_v1.json"
FLORENCE_RAW = RESULT_ROOT / "florence_raw_v1.jsonl"
STRUCTURED_RESULT = RESULT_ROOT / "structured_v1.jsonl"
SIGLIP_ARRAY = RESULT_ROOT / "siglip_image_v1.npy"
MINILM_ARRAY = RESULT_ROOT / "minilm_text_v1.npy"
EMBEDDING_METADATA = RESULT_ROOT / "embedding_metadata_v1.json"
FINAL_RESULT = RESULT_ROOT / "smoke_v1.json"
FINAL_PLOT = RESULT_ROOT / "separation_smoke_v1.svg"
sys.path.insert(0, str(ROOT / "prototype"))

from semantic_secrets.semantics import (  # noqa: E402
    CANONICAL_SCHEME_VERSION,
    StructuredSet,
    WeightedStructuredSet,
    canonicalize_extraction,
    canonicalize_label_atoms,
    extract_controlled_text,
    fit_idf_weights,
)
from semantic_secrets.semantics.canonicalize import normalise_token  # noqa: E402


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(canonical_bytes(row).decode("utf-8") + "\n")


def load_config() -> dict[str, Any]:
    return read_json(CONFIG_PATH)


def selected_rows(config: Mapping[str, Any]) -> list[dict[str, Any]]:
    inputs = {row["row_id"]: row for row in read_jsonl(INPUTS_PATH)}
    labels = read_jsonl(LABELS_PATH)
    splits = set(config["selection"]["splits"])
    roles = set(config["selection"]["roles"])
    order = {role: index for index, role in enumerate(config["selection"]["roles"])}
    selected: list[dict[str, Any]] = []
    for label in labels:
        if label["split"] not in splits or label["trial_role"] not in roles:
            continue
        input_row = inputs[label["row_id"]]
        selected.append({"input": input_row, "label": label})
    selected.sort(key=lambda row: (row["label"]["family_id"], order[row["label"]["trial_role"]]))
    families = {row["label"]["family_id"] for row in selected}
    if len(selected) != 27 or len(families) != 9:
        raise ValueError(f"P5 selection drifted: {len(selected)} rows, {len(families)} families")
    if any(row["label"]["split"] == "test" for row in selected):
        raise ValueError("test split must remain sealed")
    counts = Counter((row["label"]["family_id"], row["label"]["trial_role"]) for row in selected)
    if any(value != 1 for value in counts.values()) or len(counts) != 27:
        raise ValueError("each evaluated family must have exactly one row per selected role")
    return selected


def snapshot_hashes(model_id: str, revision: str) -> dict[str, Any]:
    from huggingface_hub import snapshot_download

    snapshot = Path(snapshot_download(model_id, revision=revision, local_files_only=True))
    files: list[dict[str, Any]] = []
    for path in sorted(item for item in snapshot.rglob("*") if item.is_file()):
        relative = path.relative_to(snapshot).as_posix()
        if relative.startswith(".cache/"):
            continue
        files.append({"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return {
        "model_id": model_id,
        "revision": revision,
        "artifact_tree_sha256": sha256_bytes(canonical_bytes(files)),
        "hashed_file_count": len(files),
        "hashed_bytes": sum(item["bytes"] for item in files),
        "files": files,
    }


def image_path(row_id: str) -> Path:
    return IMAGE_ROOT / f"{row_id}.png"


def run_generation(config: Mapping[str, Any]) -> None:
    import numpy as np
    import torch
    from diffusers import AutoPipelineForText2Image

    rows = selected_rows(config)
    cfg = config["generator"]
    IMAGE_ROOT.mkdir(parents=True, exist_ok=True)
    started = time.time()
    load_start = time.perf_counter()
    pipeline = AutoPipelineForText2Image.from_pretrained(
        cfg["model_id"],
        revision=cfg["revision"],
        variant=cfg["variant"],
        use_safetensors=True,
    ).to(cfg["device"])
    load_seconds = time.perf_counter() - load_start
    if next(pipeline.unet.parameters()).dtype != torch.float32:
        raise RuntimeError("P5 generator must use float32; fp16 produced all-NaN latents on the target GPU")

    observations: list[dict[str, Any]] = []

    def generate(row: Mapping[str, Any]) -> tuple[Any, dict[str, Any]]:
        input_row = row["input"]
        torch.cuda.reset_peak_memory_stats()
        before = time.perf_counter()
        image = pipeline(
            input_row["render_prompt"],
            num_inference_steps=cfg["inference_steps"],
            guidance_scale=cfg["guidance_scale"],
            generator=torch.Generator(device=cfg["device"]).manual_seed(input_row["generator_seed"]),
            width=cfg["width"],
            height=cfg["height"],
        ).images[0].convert("RGB")
        torch.cuda.synchronize()
        pixels = np.asarray(image)
        observation = {
            "latency_seconds": round(time.perf_counter() - before, 6),
            "peak_cuda_allocated_mib": round(torch.cuda.max_memory_allocated() / 1048576, 2),
            "peak_cuda_reserved_mib": round(torch.cuda.max_memory_reserved() / 1048576, 2),
            "pixel_min": int(pixels.min()),
            "pixel_max": int(pixels.max()),
            "pixel_mean": round(float(pixels.mean()), 6),
            "rgb_sha256": sha256_bytes(image.tobytes()),
        }
        if observation["pixel_min"] == observation["pixel_max"]:
            raise RuntimeError(f"degenerate generated image for {input_row['row_id']}")
        return image, observation

    for index, row in enumerate(rows, start=1):
        row_id = row["input"]["row_id"]
        path = image_path(row_id)
        if path.exists():
            from PIL import Image

            image = Image.open(path).convert("RGB")
            pixels = np.asarray(image)
            observation = {
                "latency_seconds": None,
                "peak_cuda_allocated_mib": None,
                "peak_cuda_reserved_mib": None,
                "pixel_min": int(pixels.min()),
                "pixel_max": int(pixels.max()),
                "pixel_mean": round(float(pixels.mean()), 6),
                "rgb_sha256": sha256_bytes(image.tobytes()),
                "resumed_from_cache": True,
            }
        else:
            image, observation = generate(row)
            image.save(path, format="PNG", optimize=False, compress_level=6)
            observation["resumed_from_cache"] = False
        observation.update(
            {
                "row_id": row_id,
                "family_id": row["label"]["family_id"],
                "split": row["label"]["split"],
                "trial_role": row["label"]["trial_role"],
                "seed": row["input"]["generator_seed"],
                "prompt_sha256": sha256_bytes(row["input"]["render_prompt"].encode("utf-8")),
                "png_sha256": sha256_file(path),
                "png_bytes": path.stat().st_size,
            }
        )
        observations.append(observation)
        print(json.dumps({"stage": "generate", "row": index, "total": len(rows), "row_id": row_id, "seconds": observation["latency_seconds"]}), flush=True)

    repeat_row = next(row for row in rows if row["label"]["trial_role"] == "enrolment")
    repeat_image, repeat_observation = generate(repeat_row)
    original = next(item for item in observations if item["row_id"] == repeat_row["input"]["row_id"])
    fixed_repeat_equal = repeat_observation["rgb_sha256"] == original["rgb_sha256"]
    if not fixed_repeat_equal:
        raise RuntimeError("SD-Turbo fixed-seed repeat failed")
    manifest = {
        "$schema_version": "semantic-secrets-p5-generation-manifest-v1",
        "screen_id": config["screen_id"],
        "config_sha256": sha256_bytes(canonical_bytes(config)),
        "started_unix": started,
        "completed_unix": time.time(),
        "backend": cfg,
        "environment": {
            "torch": torch.__version__,
            "torch_cuda": torch.version.cuda,
            "gpu": torch.cuda.get_device_name(0),
        },
        "load_seconds": round(load_seconds, 6),
        "fixed_seed_repeat_equal": fixed_repeat_equal,
        "repeat_observation": repeat_observation,
        "artifact": snapshot_hashes(cfg["model_id"], cfg["revision"]),
        "rows": observations,
        "publication_result": False,
    }
    write_json(GENERATION_MANIFEST, manifest)


def run_florence(config: Mapping[str, Any]) -> None:
    import torch
    from PIL import Image
    from transformers import AutoModelForCausalLM, AutoProcessor

    rows = selected_rows(config)
    if not all(image_path(row["input"]["row_id"]).exists() for row in rows):
        raise FileNotFoundError("run --stage generate before Florence extraction")
    cfg = config["florence"]
    FLORENCE_CACHE.mkdir(parents=True, exist_ok=True)
    load_start = time.perf_counter()
    model = AutoModelForCausalLM.from_pretrained(
        cfg["model_id"],
        revision=cfg["revision"],
        trust_remote_code=True,
        torch_dtype=torch.float32,
        attn_implementation=cfg["attention"],
        local_files_only=True,
    ).eval().to(cfg["device"])
    processor = AutoProcessor.from_pretrained(
        cfg["model_id"], revision=cfg["revision"], trust_remote_code=True, local_files_only=True
    )
    load_seconds = time.perf_counter() - load_start

    def invoke(image: Any, task: str, max_new_tokens: int) -> dict[str, Any]:
        inputs = processor(text=task, images=image, return_tensors="pt")
        inputs = {key: value.to(cfg["device"]) for key, value in inputs.items()}
        torch.cuda.reset_peak_memory_stats()
        before = time.perf_counter()
        with torch.inference_mode():
            ids = model.generate(
                input_ids=inputs["input_ids"],
                pixel_values=inputs["pixel_values"],
                max_new_tokens=max_new_tokens,
                num_beams=cfg["num_beams"],
                do_sample=cfg["do_sample"],
                use_cache=cfg["use_cache"],
            )
        torch.cuda.synchronize()
        raw = processor.batch_decode(ids, skip_special_tokens=False)[0]
        parsed = processor.post_process_generation(raw, task=task, image_size=image.size)
        return {
            "raw": raw,
            "parsed": parsed,
            "latency_seconds": round(time.perf_counter() - before, 6),
            "peak_cuda_allocated_mib": round(torch.cuda.max_memory_allocated() / 1048576, 2),
            "peak_cuda_reserved_mib": round(torch.cuda.max_memory_reserved() / 1048576, 2),
        }

    outputs: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        row_id = row["input"]["row_id"]
        cache_path = FLORENCE_CACHE / f"{row_id}.json"
        if cache_path.exists():
            output = read_json(cache_path)
            output["resumed_from_cache"] = True
        else:
            image = Image.open(image_path(row_id)).convert("RGB")
            tasks = {task: invoke(image, task, int(tokens)) for task, tokens in cfg["tasks"].items()}
            output = {
                "row_id": row_id,
                "family_id": row["label"]["family_id"],
                "split": row["label"]["split"],
                "trial_role": row["label"]["trial_role"],
                "image_png_sha256": sha256_file(image_path(row_id)),
                "tasks": tasks,
                "resumed_from_cache": False,
            }
            write_json(cache_path, output)
        outputs.append(output)
        seconds = sum(item["latency_seconds"] for item in output["tasks"].values())
        print(json.dumps({"stage": "florence", "row": index, "total": len(rows), "row_id": row_id, "seconds": round(seconds, 3)}), flush=True)

    repeat_rows = []
    for split in config["selection"]["splits"]:
        repeat_rows.append(next(row for row in rows if row["label"]["split"] == split and row["label"]["trial_role"] == "enrolment"))
    repeats: list[dict[str, Any]] = []
    for row in repeat_rows:
        row_id = row["input"]["row_id"]
        image = Image.open(image_path(row_id)).convert("RGB")
        tasks = {task: invoke(image, task, int(tokens)) for task, tokens in cfg["tasks"].items()}
        original = next(item for item in outputs if item["row_id"] == row_id)
        equal = all(tasks[task]["raw"] == original["tasks"][task]["raw"] for task in tasks)
        repeats.append({"row_id": row_id, "fixed_input_equal": equal, "tasks": tasks})
        if not equal:
            raise RuntimeError(f"Florence fixed-input repeat failed: {row_id}")

    artifact = snapshot_hashes(cfg["model_id"], cfg["revision"])
    rows_for_result = sorted(outputs, key=lambda item: item["row_id"])
    write_jsonl(
        FLORENCE_RAW,
        [
            {
                key: value
                for key, value in row.items()
                if key != "resumed_from_cache"
            }
            for row in rows_for_result
        ],
    )
    metadata = {
        "$schema_version": "semantic-secrets-p5-florence-metadata-v1",
        "screen_id": config["screen_id"],
        "backend": cfg,
        "load_seconds": round(load_seconds, 6),
        "repeat_samples": repeats,
        "artifact": artifact,
        "raw_output_sha256": sha256_file(FLORENCE_RAW),
        "publication_result": False,
    }
    write_json(RESULT_ROOT / "florence_metadata_v1.json", metadata)


def _normalise_embeddings(value: Any) -> Any:
    import torch

    return torch.nn.functional.normalize(value.float(), p=2, dim=-1)


def run_embeddings(config: Mapping[str, Any]) -> None:
    import numpy as np
    import torch
    from PIL import Image
    from transformers import AutoModel, AutoProcessor, AutoTokenizer

    rows = selected_rows(config)
    row_ids = [row["input"]["row_id"] for row in rows]
    images = [Image.open(image_path(row_id)).convert("RGB") for row_id in row_ids]
    texts = [row["input"]["core_prompt"] for row in rows]
    metadata: dict[str, Any] = {
        "$schema_version": "semantic-secrets-p5-embedding-metadata-v1",
        "screen_id": config["screen_id"],
        "row_ids": row_ids,
        "publication_result": False,
    }

    siglip_cfg = config["siglip"]
    start = time.perf_counter()
    siglip_processor = AutoProcessor.from_pretrained(
        siglip_cfg["model_id"], revision=siglip_cfg["revision"]
    )
    siglip_model = AutoModel.from_pretrained(
        siglip_cfg["model_id"], revision=siglip_cfg["revision"], torch_dtype=torch.float32
    ).eval().to(siglip_cfg["device"])
    siglip_load = time.perf_counter() - start

    def embed_images() -> tuple[Any, float, float]:
        batches = []
        torch.cuda.reset_peak_memory_stats()
        before = time.perf_counter()
        with torch.inference_mode():
            for offset in range(0, len(images), siglip_cfg["batch_size"]):
                inputs = siglip_processor(images=images[offset : offset + siglip_cfg["batch_size"]], return_tensors="pt")
                inputs = {key: value.to(siglip_cfg["device"]) for key, value in inputs.items()}
                batches.append(_normalise_embeddings(siglip_model.get_image_features(**inputs)).cpu())
        torch.cuda.synchronize()
        return torch.cat(batches), time.perf_counter() - before, torch.cuda.max_memory_allocated() / 1048576

    siglip_first, siglip_time_1, siglip_peak_1 = embed_images()
    siglip_second, siglip_time_2, siglip_peak_2 = embed_images()
    siglip_hashes = [sha256_bytes(value.numpy().astype("<f4", copy=False).tobytes()) for value in (siglip_first, siglip_second)]
    if siglip_hashes[0] != siglip_hashes[1]:
        raise RuntimeError("SigLIP fixed-input embeddings did not repeat exactly")
    np.save(SIGLIP_ARRAY, siglip_first.numpy().astype("<f4", copy=False), allow_pickle=False)
    metadata["siglip"] = {
        "backend": siglip_cfg,
        "load_seconds": round(siglip_load, 6),
        "run_seconds": [round(siglip_time_1, 6), round(siglip_time_2, 6)],
        "peak_cuda_allocated_mib": [round(siglip_peak_1, 2), round(siglip_peak_2, 2)],
        "fixed_input_equal": True,
        "embedding_sha256": siglip_hashes[0],
        "array_file_sha256": sha256_file(SIGLIP_ARRAY),
        "shape": list(siglip_first.shape),
        "artifact": snapshot_hashes(siglip_cfg["model_id"], siglip_cfg["revision"]),
    }
    del siglip_model, siglip_processor, siglip_first, siglip_second
    torch.cuda.empty_cache()

    minilm_cfg = config["minilm"]
    start = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(minilm_cfg["model_id"], revision=minilm_cfg["revision"])
    text_model = AutoModel.from_pretrained(
        minilm_cfg["model_id"], revision=minilm_cfg["revision"], torch_dtype=torch.float32
    ).eval().to(minilm_cfg["device"])
    minilm_load = time.perf_counter() - start

    def embed_texts() -> tuple[Any, float, float]:
        batches = []
        torch.cuda.reset_peak_memory_stats()
        before = time.perf_counter()
        with torch.inference_mode():
            for offset in range(0, len(texts), minilm_cfg["batch_size"]):
                encoded = tokenizer(
                    texts[offset : offset + minilm_cfg["batch_size"]],
                    padding=True,
                    truncation=True,
                    return_tensors="pt",
                )
                encoded = {key: value.to(minilm_cfg["device"]) for key, value in encoded.items()}
                output = text_model(**encoded)[0]
                mask = encoded["attention_mask"].unsqueeze(-1).expand(output.size()).float()
                pooled = torch.sum(output * mask, dim=1) / torch.clamp(mask.sum(dim=1), min=1e-9)
                batches.append(_normalise_embeddings(pooled).cpu())
        torch.cuda.synchronize()
        return torch.cat(batches), time.perf_counter() - before, torch.cuda.max_memory_allocated() / 1048576

    minilm_first, minilm_time_1, minilm_peak_1 = embed_texts()
    minilm_second, minilm_time_2, minilm_peak_2 = embed_texts()
    minilm_hashes = [sha256_bytes(value.numpy().astype("<f4", copy=False).tobytes()) for value in (minilm_first, minilm_second)]
    if minilm_hashes[0] != minilm_hashes[1]:
        raise RuntimeError("MiniLM fixed-input embeddings did not repeat exactly")
    np.save(MINILM_ARRAY, minilm_first.numpy().astype("<f4", copy=False), allow_pickle=False)
    metadata["minilm"] = {
        "backend": minilm_cfg,
        "load_seconds": round(minilm_load, 6),
        "run_seconds": [round(minilm_time_1, 6), round(minilm_time_2, 6)],
        "peak_cuda_allocated_mib": [round(minilm_peak_1, 2), round(minilm_peak_2, 2)],
        "fixed_input_equal": True,
        "embedding_sha256": minilm_hashes[0],
        "array_file_sha256": sha256_file(MINILM_ARRAY),
        "shape": list(minilm_first.shape),
        "artifact": snapshot_hashes(minilm_cfg["model_id"], minilm_cfg["revision"]),
    }
    write_json(EMBEDDING_METADATA, metadata)
    print(json.dumps({"stage": "embeddings", "siglip_shape": metadata["siglip"]["shape"], "minilm_shape": metadata["minilm"]["shape"]}), flush=True)


def florence_to_extraction(raw_row: Mapping[str, Any], object_lexicon: Sequence[str]) -> dict[str, Any]:
    caption_task = raw_row["tasks"]["<MORE_DETAILED_CAPTION>"]["parsed"]
    caption = str(caption_task.get("<MORE_DETAILED_CAPTION>", ""))
    od_task = raw_row["tasks"]["<OD>"]["parsed"].get("<OD>", {})
    labels = [normalise_token(value, singular=True) for value in od_task.get("labels", [])]
    boxes = od_task.get("bboxes", [])
    lexicon = sorted(set(object_lexicon) | set(labels))
    extraction = extract_controlled_text(caption, object_lexicon=lexicon)
    existing = {item["label"] for item in extraction["objects"]}
    for label in labels:
        if label and label not in existing:
            extraction["objects"].append(
                {"id": f"od_{len(extraction['objects']) + 1}", "label": label, "confidence": None}
            )
            existing.add(label)
    for label, count in Counter(labels).items():
        if label and count > 1:
            extraction["counts"].append({"object_id": label, "value": count, "confidence": None})

    for left_index in range(len(boxes)):
        for right_index in range(left_index + 1, len(boxes)):
            if left_index >= len(labels) or right_index >= len(labels):
                continue
            a, b = boxes[left_index], boxes[right_index]
            a_center = ((a[0] + a[2]) / 2, (a[1] + a[3]) / 2)
            b_center = ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
            a_width, b_width = a[2] - a[0], b[2] - b[0]
            vertical_overlap = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
            min_height = max(1.0, min(a[3] - a[1], b[3] - b[1]))
            if vertical_overlap / min_height >= 0.25 and abs(a_center[0] - b_center[0]) > 0.5 * max(a_width, b_width):
                subject, target = (labels[left_index], labels[right_index]) if a_center[0] < b_center[0] else (labels[right_index], labels[left_index])
                extraction["relations"].append(
                    {"subject": subject, "predicate": "left_of", "object": target, "confidence": None}
                )
    return extraction


def build_pairs(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by_family: dict[str, dict[str, Mapping[str, Any]]] = defaultdict(dict)
    family_split: dict[str, str] = {}
    for row in rows:
        label = row["label"]
        by_family[label["family_id"]][label["trial_role"]] = row
        family_split[label["family_id"]] = label["split"]
    pairs: list[dict[str, Any]] = []
    for family, roles in sorted(by_family.items()):
        anchor = roles["enrolment"]["input"]["row_id"]
        for relation, role in (("same", "paraphrase"), ("near_negative", "near_negative")):
            pairs.append(
                {
                    "family_id": family,
                    "split": family_split[family],
                    "relationship": relation,
                    "changed_atom_type": roles[role]["label"].get("changed_atom_type"),
                    "anchor_row_id": anchor,
                    "candidate_row_id": roles[role]["input"]["row_id"],
                }
            )
    for split in sorted(set(family_split.values())):
        families = sorted(family for family, value in family_split.items() if value == split)
        for index, family in enumerate(families):
            candidate_family = families[(index + 1) % len(families)]
            pairs.append(
                {
                    "family_id": family,
                    "split": split,
                    "relationship": "unrelated",
                    "changed_atom_type": None,
                    "anchor_row_id": by_family[family]["enrolment"]["input"]["row_id"],
                    "candidate_row_id": by_family[candidate_family]["enrolment"]["input"]["row_id"],
                }
            )
    return sorted(pairs, key=lambda item: (item["family_id"], item["relationship"]))


def _summary(values: Sequence[float]) -> dict[str, float]:
    return {
        "count": len(values),
        "mean": round(statistics.fmean(values), 6),
        "median": round(statistics.median(values), 6),
        "minimum": round(min(values), 6),
        "maximum": round(max(values), 6),
    }


def _bootstrap_gap(
    pairs: Sequence[Mapping[str, Any]],
    scores: Sequence[float],
    negative_type: str,
    *,
    seed: int,
    repetitions: int,
) -> dict[str, Any]:
    per_family: dict[str, dict[str, float]] = defaultdict(dict)
    for pair, score in zip(pairs, scores, strict=True):
        per_family[pair["family_id"]][pair["relationship"]] = score
    differences = [values["same"] - values[negative_type] for values in per_family.values()]
    rng = random.Random(seed + sum(map(ord, negative_type)))
    samples = []
    for _ in range(repetitions):
        draw = [differences[rng.randrange(len(differences))] for _ in differences]
        samples.append(statistics.fmean(draw))
    samples.sort()
    low = samples[int(0.025 * (len(samples) - 1))]
    high = samples[int(0.975 * (len(samples) - 1))]
    return {
        "family_count": len(differences),
        "mean_paired_gap": round(statistics.fmean(differences), 6),
        "bootstrap_95pct": [round(low, 6), round(high, 6)],
        "bootstrap_repetitions": repetitions,
    }


def _atom_metrics(expected: Mapping[str, set[str]], observed: Mapping[str, set[str]]) -> dict[str, Any]:
    rows = []
    per_type: dict[str, dict[str, int]] = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    for row_id in sorted(expected):
        truth, prediction = expected[row_id], observed[row_id]
        tp, fp, fn = len(truth & prediction), len(prediction - truth), len(truth - prediction)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        rows.append((precision, recall, 2 * precision * recall / (precision + recall) if precision + recall else 0.0))
        for atom in truth | prediction:
            atom_type = atom.split(":", 1)[0]
            if atom in truth and atom in prediction:
                per_type[atom_type]["tp"] += 1
            elif atom in prediction:
                per_type[atom_type]["fp"] += 1
            else:
                per_type[atom_type]["fn"] += 1
    by_type = {}
    for atom_type, counts in sorted(per_type.items()):
        denominator = counts["tp"] + counts["fn"]
        by_type[atom_type] = {**counts, "recall": round(counts["tp"] / denominator if denominator else 0.0, 6)}
    return {
        "row_count": len(rows),
        "macro_precision": round(statistics.fmean(row[0] for row in rows), 6),
        "macro_recall": round(statistics.fmean(row[1] for row in rows), 6),
        "macro_f1": round(statistics.fmean(row[2] for row in rows), 6),
        "empty_rows": sum(not observed[row_id] for row_id in expected),
        "by_atom_type": by_type,
    }


def _dense_retrieval(matrix: Any, rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    import numpy as np

    similarities = matrix @ matrix.T
    exact_top1 = int(np.sum(np.argmax(similarities, axis=1) == np.arange(len(matrix))))
    enrolments = [index for index, row in enumerate(rows) if row["label"]["trial_role"] == "enrolment"]
    paraphrases = [index for index, row in enumerate(rows) if row["label"]["trial_role"] == "paraphrase"]
    family_hits = 0
    for anchor in enrolments:
        candidate = paraphrases[int(np.argmax(similarities[anchor, paraphrases]))]
        family_hits += rows[anchor]["label"]["family_id"] == rows[candidate]["label"]["family_id"]
    return {
        "dictionary_self_retrieval_top1": exact_top1,
        "dictionary_size": len(matrix),
        "enrolment_to_paraphrase_family_link_top1": family_hits,
        "enrolment_count": len(enrolments),
        "interpretation": "cheap known-candidate/linkability probe; not a general inversion attack",
    }


def render_svg(score_summaries: Mapping[str, Mapping[str, Mapping[str, float]]]) -> None:
    names = list(score_summaries)
    relationships = ("same", "near_negative", "unrelated")
    colors = {"same": "#2f855a", "near_negative": "#dd6b20", "unrelated": "#4a5568"}
    width = 980
    row_height = 42
    height = 80 + row_height * len(names)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="20" y="28" font-family="sans-serif" font-size="18">P5 smoke diagnostic medians (not publication results)</text>',
    ]
    for index, name in enumerate(names):
        y = 55 + index * row_height
        lines.append(f'<text x="20" y="{y + 14}" font-family="sans-serif" font-size="12">{name}</text>')
        for rel_index, relationship in enumerate(relationships):
            value = score_summaries[name][relationship]["median"]
            x = 285 + rel_index * 220
            bar_width = max(0, min(190, 190 * value))
            lines.append(f'<rect x="{x}" y="{y}" width="{bar_width:.2f}" height="16" fill="{colors[relationship]}"/>')
            lines.append(f'<text x="{x + 194}" y="{y + 13}" font-family="sans-serif" font-size="11">{value:.3f}</text>')
    for rel_index, relationship in enumerate(relationships):
        x = 285 + rel_index * 220
        lines.append(f'<text x="{x}" y="48" font-family="sans-serif" font-size="12" fill="{colors[relationship]}">{relationship}</text>')
    lines.append("</svg>")
    FINAL_PLOT.parent.mkdir(parents=True, exist_ok=True)
    FINAL_PLOT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_analysis(config: Mapping[str, Any]) -> None:
    import numpy as np

    rows = selected_rows(config)
    required = [GENERATION_MANIFEST, FLORENCE_RAW, SIGLIP_ARRAY, MINILM_ARRAY, EMBEDDING_METADATA]
    if missing := [str(path) for path in required if not path.exists()]:
        raise FileNotFoundError(f"missing P5 stage outputs: {missing}")
    row_ids = [row["input"]["row_id"] for row in rows]
    expected = {
        row["input"]["row_id"]: set(canonicalize_label_atoms(row["label"]["expected_atoms"]).atoms)
        for row in rows
    }
    training_object_lexicon = sorted(
        {
            normalise_token(atom["value"], singular=True)
            for row in rows
            if row["label"]["split"] == config["weighting"]["fit_split"]
            for atom in row["label"]["expected_atoms"]
            if atom["type"] == "object"
        }
    )
    text_atoms = {}
    text_warnings = {}
    for row in rows:
        row_id = row["input"]["row_id"]
        result = canonicalize_extraction(
            extract_controlled_text(row["input"]["core_prompt"], object_lexicon=training_object_lexicon),
            minimum_confidence=config["canonicalisation"]["minimum_confidence"],
        )
        text_atoms[row_id] = set(result.atoms)
        text_warnings[row_id] = list(result.warnings)

    florence_rows = {row["row_id"]: row for row in read_jsonl(FLORENCE_RAW)}
    florence_atoms = {}
    florence_warnings = {}
    for row_id in row_ids:
        result = canonicalize_extraction(
            florence_to_extraction(florence_rows[row_id], training_object_lexicon),
            minimum_confidence=config["canonicalisation"]["minimum_confidence"],
        )
        florence_atoms[row_id] = set(result.atoms)
        florence_warnings[row_id] = list(result.warnings)

    training_documents = [
        expected[row["input"]["row_id"]]
        for row in rows
        if row["label"]["split"] == config["weighting"]["fit_split"]
        and row["label"]["trial_role"] == "enrolment"
    ]
    weights = fit_idf_weights(training_documents, weights_version=config["weighting"]["weights_version"])
    pairs = build_pairs(rows)
    siglip = np.load(SIGLIP_ARRAY, allow_pickle=False)
    minilm = np.load(MINILM_ARRAY, allow_pickle=False)
    if list(siglip.shape) != [27, 768] or list(minilm.shape) != [27, 384]:
        raise ValueError("embedding shape mismatch")
    indexes = {row_id: index for index, row_id in enumerate(row_ids)}

    atom_sources = {
        "oracle_structured": expected,
        "controlled_text_structured": text_atoms,
        "florence_structured": florence_atoms,
    }
    scores: dict[str, list[float]] = {}
    for name, source in atom_sources.items():
        values = []
        for pair in pairs:
            left = StructuredSet(CANONICAL_SCHEME_VERSION, frozenset(source[pair["anchor_row_id"]]))
            right = StructuredSet(CANONICAL_SCHEME_VERSION, frozenset(source[pair["candidate_row_id"]]))
            values.append(left.jaccard(right))
        scores[name] = values
        weighted_values = []
        for pair in pairs:
            left = WeightedStructuredSet(
                CANONICAL_SCHEME_VERSION,
                frozenset(source[pair["anchor_row_id"]]),
                weights,
                config["weighting"]["weights_version"],
            )
            right = WeightedStructuredSet(
                CANONICAL_SCHEME_VERSION,
                frozenset(source[pair["candidate_row_id"]]),
                weights,
                config["weighting"]["weights_version"],
            )
            weighted_values.append(left.overlap(right))
        scores[name.replace("structured", "weighted")] = weighted_values

    for name, matrix in (("siglip_image", siglip), ("minilm_text", minilm)):
        scores[name] = [
            float(matrix[indexes[pair["anchor_row_id"]]] @ matrix[indexes[pair["candidate_row_id"]]])
            for pair in pairs
        ]

    summaries: dict[str, Any] = {}
    pair_relationships = config["analysis"]["pair_types"]
    for name, values in scores.items():
        by_relationship = {
            relationship: _summary(
                [score for pair, score in zip(pairs, values, strict=True) if pair["relationship"] == relationship]
            )
            for relationship in pair_relationships
        }
        advance = (
            by_relationship["same"]["median"] > by_relationship["near_negative"]["median"]
            and by_relationship["same"]["median"] > by_relationship["unrelated"]["median"]
        )
        summaries[name] = {
            "by_relationship": by_relationship,
            "paired_gap_same_minus_near": _bootstrap_gap(
                pairs,
                values,
                "near_negative",
                seed=config["analysis"]["bootstrap_seed"],
                repetitions=config["analysis"]["bootstrap_repetitions"],
            ),
            "paired_gap_same_minus_unrelated": _bootstrap_gap(
                pairs,
                values,
                "unrelated",
                seed=config["analysis"]["bootstrap_seed"],
                repetitions=config["analysis"]["bootstrap_repetitions"],
            ),
            "advance_to_p6_by_smoke_rule": advance,
        }
        near_gap = summaries[name]["paired_gap_same_minus_near"]
        unrelated_gap = summaries[name]["paired_gap_same_minus_unrelated"]
        summaries[name]["uncertainty_supports_positive_separation"] = (
            near_gap["bootstrap_95pct"][0] > 0 and unrelated_gap["bootstrap_95pct"][0] > 0
        )
        summaries[name]["by_split"] = {
            split: {
                relationship: _summary(
                    [
                        score
                        for pair, score in zip(pairs, values, strict=True)
                        if pair["split"] == split and pair["relationship"] == relationship
                    ]
                )
                for relationship in pair_relationships
            }
            for split in config["selection"]["splits"]
        }
        near_types = sorted(
            {
                pair["changed_atom_type"]
                for pair in pairs
                if pair["relationship"] == "near_negative" and pair["changed_atom_type"]
            }
        )
        summaries[name]["near_sensitivity_by_changed_atom_type"] = {
            atom_type: _summary(
                [
                    score
                    for pair, score in zip(pairs, values, strict=True)
                    if pair["relationship"] == "near_negative" and pair["changed_atom_type"] == atom_type
                ]
            )
            for atom_type in near_types
        }

    structured_rows = []
    for row in rows:
        row_id = row["input"]["row_id"]
        structured_rows.append(
            {
                "row_id": row_id,
                "family_id": row["label"]["family_id"],
                "split": row["label"]["split"],
                "trial_role": row["label"]["trial_role"],
                "scheme_version": CANONICAL_SCHEME_VERSION,
                "oracle_atoms": sorted(expected[row_id]),
                "controlled_text_atoms": sorted(text_atoms[row_id]),
                "controlled_text_warnings": text_warnings[row_id],
                "florence_atoms": sorted(florence_atoms[row_id]),
                "florence_warnings": florence_warnings[row_id],
            }
        )
    write_jsonl(STRUCTURED_RESULT, structured_rows)

    generation = read_json(GENERATION_MANIFEST)
    florence_metadata = read_json(RESULT_ROOT / "florence_metadata_v1.json")
    embedding_metadata = read_json(EMBEDDING_METADATA)
    atom_metrics = {
        "controlled_text": _atom_metrics(expected, text_atoms),
        "florence": _atom_metrics(expected, florence_atoms),
    }
    atom_metrics_by_split = {}
    row_split = {row["input"]["row_id"]: row["label"]["split"] for row in rows}
    for split in config["selection"]["splits"]:
        split_expected = {row_id: value for row_id, value in expected.items() if row_split[row_id] == split}
        atom_metrics_by_split[split] = {
            "controlled_text": _atom_metrics(split_expected, {row_id: text_atoms[row_id] for row_id in split_expected}),
            "florence": _atom_metrics(split_expected, {row_id: florence_atoms[row_id] for row_id in split_expected}),
        }
    report = {
        "$schema_version": "semantic-secrets-p5-result-v1",
        "screen_id": config["screen_id"],
        "run_kind": "bounded engineering smoke; not pilot or publication result",
        "publication_result": False,
        "config_sha256": sha256_bytes(canonical_bytes(config)),
        "boundaries": {
            "selected_rows": len(rows),
            "selected_families": len({row["label"]["family_id"] for row in rows}),
            "splits": config["selection"]["splits"],
            "roles": config["selection"]["roles"],
            "test_rows_evaluated": 0,
            "pilot_catalog_status": "not authored; P3 planned 60 families",
            "model_drift": config["analysis"]["model_drift"],
        },
        "versions": {
            "canonical_scheme": CANONICAL_SCHEME_VERSION,
            "structured_schema": "structured-extraction-v1",
            "weights_version": config["weighting"]["weights_version"],
            "weights_fit_split": config["weighting"]["fit_split"],
            "weights_training_documents": len(training_documents),
            "weights_sha256": sha256_bytes(canonical_bytes(weights)),
        },
        "pair_count": len(pairs),
        "pairs": pairs,
        "representations": summaries,
        "atom_metrics": atom_metrics,
        "atom_metrics_by_split": atom_metrics_by_split,
        "qualitative_failures": {
            "generator": ["QF-NUMERIC-FP16", "QF-HARDWARE-OVERSUBSCRIPTION"],
            "florence_structured": ["QF-COVERAGE", "QF-MISSING-ATOM", "QF-HALLUCINATION"],
            "controlled_text_structured": ["QF-COVERAGE", "QF-TRAIN-LEXICON-OOV"],
            "all_real_representations": ["QF-NEAR-UNCERTAINTY"],
        },
        "determinism": {
            "generator_fixed_seed_equal": generation["fixed_seed_repeat_equal"],
            "florence_repeat_samples": [
                {"row_id": row["row_id"], "fixed_input_equal": row["fixed_input_equal"]}
                for row in florence_metadata["repeat_samples"]
            ],
            "siglip_fixed_input_equal": embedding_metadata["siglip"]["fixed_input_equal"],
            "minilm_fixed_input_equal": embedding_metadata["minilm"]["fixed_input_equal"],
            "controlled_text_equal": all(
                extract_controlled_text(row["input"]["core_prompt"], object_lexicon=training_object_lexicon)
                == extract_controlled_text(row["input"]["core_prompt"], object_lexicon=reversed(training_object_lexicon))
                for row in rows
            ),
        },
        "resources": {
            "generator": {
                "measured_rows": len(generation["rows"]),
                "latency_seconds": [row["latency_seconds"] for row in generation["rows"]],
                "peak_cuda_allocated_mib": [row["peak_cuda_allocated_mib"] for row in generation["rows"]],
                "png_bytes": sum(row["png_bytes"] for row in generation["rows"]),
            },
            "florence": {
                "task_latency_seconds": {
                    task: [row["tasks"][task]["latency_seconds"] for row in florence_rows.values()]
                    for task in config["florence"]["tasks"]
                },
                "peak_cuda_allocated_mib": max(
                    row["tasks"][task]["peak_cuda_allocated_mib"]
                    for row in florence_rows.values()
                    for task in config["florence"]["tasks"]
                ),
            },
            "siglip": {key: embedding_metadata["siglip"][key] for key in ("run_seconds", "peak_cuda_allocated_mib", "shape")},
            "minilm": {key: embedding_metadata["minilm"][key] for key in ("run_seconds", "peak_cuda_allocated_mib", "shape")},
            "structured_result_bytes": STRUCTURED_RESULT.stat().st_size,
            "siglip_array_bytes": SIGLIP_ARRAY.stat().st_size,
            "minilm_array_bytes": MINILM_ARRAY.stat().st_size,
        },
        "leakage_probes": {
            "structured": {
                "direct_atom_disclosure": True,
                "raw_set_cross_service_linkable_without_domain_protection": True,
                "interpretation": "structured atoms are readable and exact sets are stable identifiers unless protected",
            },
            "siglip": _dense_retrieval(siglip, rows),
            "minilm": _dense_retrieval(minilm, rows),
            "warning": "raw embeddings are not private; these cheap probes do not establish resistance to general inversion",
        },
        "private_matching_compatibility": {
            "structured_set": "plausible PSI/PSI-cardinality/private threshold path; exact protocol and leakage wait for D6/P9",
            "weighted_structured_set": "requires private weighted intersection/threshold and public or protected frozen weights; greater complexity",
            "dense_embedding": "requires approximate dot-product comparison with MPC/HE or related machinery; raw cosine is only a baseline",
            "plaintext_storage": "rejected as privacy-preserving for all representation families",
        },
        "artifacts": {
            "generation_manifest_sha256": sha256_file(GENERATION_MANIFEST),
            "florence_raw_sha256": sha256_file(FLORENCE_RAW),
            "structured_sha256": sha256_file(STRUCTURED_RESULT),
            "embedding_metadata_sha256": sha256_file(EMBEDDING_METADATA),
            "siglip_array_sha256": sha256_file(SIGLIP_ARRAY),
            "minilm_array_sha256": sha256_file(MINILM_ARRAY),
        },
    }
    write_json(FINAL_RESULT, report)
    render_svg({name: value["by_relationship"] for name, value in summaries.items()})
    validate_result(report)
    print(json.dumps({"stage": "analyze", "result": str(FINAL_RESULT), "advanced": [name for name, value in summaries.items() if value["advance_to_p6_by_smoke_rule"]]}), flush=True)


def validate_result(report: Mapping[str, Any]) -> None:
    if report.get("publication_result") is not False:
        raise ValueError("P5 smoke result must be marked non-publication")
    if report["boundaries"]["test_rows_evaluated"] != 0:
        raise ValueError("test labels must remain sealed")
    if report["boundaries"]["selected_rows"] != 27 or report["pair_count"] != 27:
        raise ValueError("P5 row/pair count drift")
    if report["versions"]["weights_fit_split"] != "train" or report["versions"]["weights_training_documents"] != 6:
        raise ValueError("weights must use six training-family enrolments only")
    if not all(
        value is True
        for key, value in report["determinism"].items()
        if key != "florence_repeat_samples"
    ):
        raise ValueError("mandatory deterministic repeat failed")
    if not all(row["fixed_input_equal"] for row in report["determinism"]["florence_repeat_samples"]):
        raise ValueError("Florence repeat sample failed")
    if not any(value["advance_to_p6_by_smoke_rule"] for value in report["representations"].values()):
        raise ValueError("no representation reached the P6 smoke handoff rule")


def validate_saved() -> None:
    report = read_json(FINAL_RESULT)
    validate_result(report)
    for name, expected in report["artifacts"].items():
        path = {
            "generation_manifest_sha256": GENERATION_MANIFEST,
            "florence_raw_sha256": FLORENCE_RAW,
            "structured_sha256": STRUCTURED_RESULT,
            "embedding_metadata_sha256": EMBEDDING_METADATA,
            "siglip_array_sha256": SIGLIP_ARRAY,
            "minilm_array_sha256": MINILM_ARRAY,
        }[name]
        if sha256_file(path) != expected:
            raise ValueError(f"artifact hash mismatch: {path}")
    print(json.dumps({"validated": str(FINAL_RESULT), "screen_id": report["screen_id"]}, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("generate", "florence", "embeddings", "analyze", "all"), default="all")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if args.validate_only:
        validate_saved()
        return 0
    config = load_config()
    if args.stage in ("generate", "all"):
        run_generation(config)
    if args.stage in ("florence", "all"):
        run_florence(config)
    if args.stage in ("embeddings", "all"):
        run_embeddings(config)
    if args.stage in ("analyze", "all"):
        run_analysis(config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
