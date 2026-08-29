"""Outcome-independent component-local score-domain contract."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .io import atomic_write, canonical_bytes, read_json, sha256_file, sha256_tree
from .schemas import validate


SCORE_CONTRACT: dict[str, dict[str, tuple[str, bool]]] = {
    "v3.1-gdino-siglip2": {
        "entity": ("grounding_dino_postprocessed_score", False),
        "colour": ("siglip2_sigmoid_logit", True),
        "size": ("siglip2_sigmoid_logit", True),
        "material": ("siglip2_sigmoid_logit", True),
        "pattern": ("siglip2_sigmoid_logit", True),
        "unary_action": ("siglip2_sigmoid_logit", True),
        "binary_interaction": ("siglip2_sigmoid_logit", True),
        "scene": ("siglip2_sigmoid_logit", True),
    },
    "v3.1-egtr-siglip2": {
        "entity": ("egtr_object_softmax", False),
        "predicate": ("egtr_relation_sigmoid", False),
        "connectivity": ("egtr_connectivity_sigmoid", False),
        "colour": ("siglip2_sigmoid_logit", True),
        "size": ("siglip2_sigmoid_logit", True),
        "material": ("siglip2_sigmoid_logit", True),
        "pattern": ("siglip2_sigmoid_logit", True),
        "scene": ("siglip2_sigmoid_logit", True),
    },
}


def validate_settings(pipeline_id: str, values: Mapping[str, Any], *, exact_tasks: bool) -> None:
    expected = SCORE_CONTRACT[pipeline_id]
    if exact_tasks and set(values) != set(expected):
        raise ValueError(f"threshold task set mismatch for {pipeline_id}")
    for task, setting in values.items():
        if task not in expected or not isinstance(setting, Mapping):
            raise ValueError(f"unknown threshold setting {pipeline_id}/{task}")
        score_name, needs_margin = expected[task]
        if setting.get("score_name") != score_name or setting.get("score_range") != [0.0, 1.0] or setting.get("threshold_source") != "development":
            raise ValueError(f"score-domain mismatch for {pipeline_id}/{task}")
        threshold = setting.get("threshold")
        if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not 0 <= threshold <= 1:
            raise ValueError(f"invalid threshold for {pipeline_id}/{task}")
        if needs_margin:
            margin = setting.get("minimum_top_two_margin")
            if isinstance(margin, bool) or not isinstance(margin, (int, float)) or not 0 <= margin <= 1:
                raise ValueError(f"missing/invalid top-two margin for {pipeline_id}/{task}")


def freeze_settings(settings_path: Path, manifest_path: Path, results: Path, output: Path) -> dict[str, Any]:
    """Freeze already development-fitted settings without inventing a fit rule."""

    if output.exists():
        raise ValueError("threshold freeze output already exists")
    if (results / "validation").exists() and any((results / "validation").rglob("*.json")):
        raise ValueError("thresholds cannot be frozen after validation output")
    development = results / "development"
    if not (development / ".complete").is_file() or len(list(development.rglob("*.json"))) != 240:
        raise ValueError("threshold freeze requires the complete 240-record development run")
    settings = read_json(settings_path)
    if settings.get("schema_version") != "development-threshold-settings-v3.1.0":
        raise ValueError("settings are not an explicit v3.1 development-threshold record")
    if set(settings.get("pipelines", {})) != set(SCORE_CONTRACT):
        raise ValueError("development settings must contain both frozen pipelines")
    for pipeline, values in settings["pipelines"].items():
        validate_settings(pipeline, values, exact_tasks=True)
    value = {
        "schema_version": "threshold-freeze-v3.1.0",
        "status": "frozen_before_validation",
        "development_manifest_sha256": sha256_file(manifest_path),
        "development_results_sha256": sha256_tree(development),
        "frozen_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "pipelines": settings["pipelines"],
    }
    validate("threshold_freeze_v3_1.schema.json", value)
    atomic_write(output, canonical_bytes(value))
    return {"output": str(output), "sha256": sha256_file(output)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and freeze development-fitted P9-v3B thresholds")
    parser.add_argument("--settings", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    print(json.dumps(freeze_settings(args.settings, args.manifest, args.results, args.output), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
