"""Shared closed-label scoring and observation helpers."""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from pathlib import Path
from typing import Any, Sequence

from PIL import Image, ImageDraw

from prototype.semantic_secrets.v3 import load_active_contract

from ..telemetry import Telemetry
from ..thresholds import validate_settings


MODELS = Path(os.environ.get("SEMANTIC_SECRETS_MODELS", "/workspace/models"))


def read_request() -> dict[str, Any]:
    value = json.load(sys.stdin)
    if not isinstance(value, dict) or value.get("adapter_protocol") != "bounded-observation-adapter-v3.1.0":
        raise ValueError("unsupported adapter request")
    path = Path(value["image_path"])
    if hashlib.sha256(path.read_bytes()).hexdigest() != value["image_sha256"]:
        raise ValueError("adapter image SHA-256 mismatch")
    return value


def confidence(score: float, setting: dict[str, Any]) -> dict[str, Any]:
    return {
        "value": round(float(score), 6),
        "score_name": setting["score_name"],
        "score_range": setting["score_range"],
        "threshold": setting["threshold"],
        "threshold_source": "development",
    }


def setting(request: dict[str, Any], name: str) -> dict[str, Any]:
    validate_settings(request["pipeline_id"], request["thresholds"], exact_tasks=False)
    value = request["thresholds"].get(name)
    if not isinstance(value, dict):
        raise ValueError(f"missing threshold setting {name}")
    required = {"score_name", "score_range", "threshold", "threshold_source"}
    if not required <= value.keys() or value["threshold_source"] != "development":
        raise ValueError(f"invalid threshold setting {name}")
    return value


def component_event(component_id: str, revision: str, status: str, telemetry: dict[str, Any], failure_code: str | None = None) -> dict[str, Any]:
    return {
        "component_id": component_id,
        "component_revision": revision,
        "status": status,
        "failure_code": failure_code,
        "elapsed_seconds": telemetry["elapsed_seconds"],
        "peak_rss_bytes": telemetry["peak_process_rss_bytes"],
        "peak_gpu_bytes": telemetry["framework_peak_gpu_allocated_bytes"],
    }


def base_observation(request: dict[str, Any]) -> dict[str, Any]:
    contract = load_active_contract()
    return {
        "observation_version": contract.observation_version,
        "pipeline_id": request["pipeline_id"],
        "pipeline_revision": request["pipeline_revision"],
        "image_id": request["image_id"],
        "image_sha256": request["image_sha256"],
        "detections": [], "attributes": [], "unary_actions": [],
        "binary_interactions": [], "scenes": [], "component_events": [],
        "execution_telemetry": [],
    }


def padded_crop(image: Image.Image, bbox: Sequence[float]) -> Image.Image:
    width, height = image.size
    x1, y1, x2, y2 = bbox
    pad_x, pad_y = (x2 - x1) * 0.10, (y2 - y1) * 0.10
    pixels = (max(0, math.floor((x1 - pad_x) * width)), max(0, math.floor((y1 - pad_y) * height)), min(width, math.ceil((x2 + pad_x) * width)), min(height, math.ceil((y2 + pad_y) * height)))
    return image.crop(pixels)


def pair_crop(image: Image.Image, source: Sequence[float], target: Sequence[float]) -> Image.Image:
    width, height = image.size
    x1, y1 = min(source[0], target[0]), min(source[1], target[1])
    x2, y2 = max(source[2], target[2]), max(source[3], target[3])
    pad_x, pad_y = (x2 - x1) * 0.10, (y2 - y1) * 0.10
    left, top, right, bottom = max(0, math.floor((x1 - pad_x) * width)), max(0, math.floor((y1 - pad_y) * height)), min(width, math.ceil((x2 + pad_x) * width)), min(height, math.ceil((y2 + pad_y) * height))
    result = image.crop((left, top, right, bottom)).copy()
    draw = ImageDraw.Draw(result)
    for bbox, colour in ((source, "red"), (target, "blue")):
        rectangle = ((int(bbox[0] * width) - left, int(bbox[1] * height) - top), (int(bbox[2] * width) - left, int(bbox[3] * height) - top))
        draw.rectangle(rectangle, outline=colour, width=2)
    return result


class SiglipScorer:
    def __init__(self) -> None:
        import torch
        from transformers import AutoModel, AutoProcessor

        path = MODELS / "siglip2-base-384"
        self.torch = torch
        self.processor = AutoProcessor.from_pretrained(path, local_files_only=True)
        self.model = AutoModel.from_pretrained(path, local_files_only=True).eval().cuda()

    def scores(self, image: Image.Image, prompts: list[str]) -> list[float]:
        inputs = self.processor(text=prompts, images=image, padding="max_length", return_tensors="pt").to("cuda")
        with self.torch.inference_mode():
            logits = self.model(**inputs).logits_per_image[0]
        return logits.sigmoid().float().cpu().tolist()

    def winner(self, image: Image.Image, prompts: list[str], labels: list[str], threshold: dict[str, Any]) -> tuple[str, float] | None:
        scores = self.scores(image, prompts)
        order = sorted(range(len(scores)), key=lambda index: (-scores[index], labels[index]))
        best, second = order[0], order[1] if len(order) > 1 else order[0]
        margin = scores[best] - scores[second] if len(order) > 1 else scores[best]
        if scores[best] < threshold["threshold"] or margin < threshold.get("minimum_top_two_margin", 0.0):
            return None
        return labels[best], scores[best]


def emit(value: dict[str, Any]) -> None:
    if sum(len(value[key]) for key in ("detections", "attributes", "unary_actions", "binary_interactions", "scenes")) > 64:
        raise RuntimeError("bounded observation exceeds the frozen 64-record limit")
    print(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
