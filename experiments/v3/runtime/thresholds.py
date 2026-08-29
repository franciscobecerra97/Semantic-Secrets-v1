"""Prospective v3.3 development-threshold contract and freeze helpers."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from fractions import Fraction
from typing import Any, Mapping, Sequence

from .io import atomic_write, canonical_bytes, read_json, sha256_file, sha256_tree
from .schemas import validate
from prototype.semantic_secrets.v3 import load_active_contract


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

CALIBRATION_VERSION = "development-threshold-calibration-v3.3.0"
CANDIDATE_GRID = tuple(Fraction(index, 100) for index in range(101))
PREFERRED = {
    "precision": Fraction(90, 100),
    "recall": Fraction(70, 100),
    "f1": Fraction(80, 100),
    "coverage": Fraction(75, 100),
}


def grid_values() -> list[float]:
    return [float(value) for value in CANDIDATE_GRID]


def _fraction(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError("metric is not numeric")
    return Fraction(str(value))


def ranking_key(
    metrics: Mapping[str, Mapping[str, Any]], threshold: Any,
    secondary: Any = 0,
) -> tuple[Fraction, ...]:
    """Exact descending v3.3 ranking key for the two development strata."""

    strata = ("A_controlled_geometric", "B_naturalistic_t2i")
    if set(metrics) != set(strata):
        raise ValueError("candidate metrics must contain exactly both development strata")
    values = {
        name: [
            _fraction(metrics[stratum].get(f"{name}_exact", metrics[stratum][name]))
            for stratum in strata
        ]
        for name in PREFERRED
    }
    preferred = all(all(value >= PREFERRED[name] for value in values[name]) for name in PREFERRED)
    key: list[Fraction] = [Fraction(int(preferred), 1)]
    for name in ("f1", "coverage", "precision", "recall"):
        key.extend((min(values[name]), sum(values[name], Fraction()) / len(strata)))
    key.extend((_fraction(threshold), _fraction(secondary)))
    return tuple(key)


def select_candidate(candidates: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Select one candidate deterministically; input ordering cannot affect it."""

    if not candidates:
        raise ValueError("no calibration candidates")
    ranked: list[tuple[tuple[Fraction, ...], str, Mapping[str, Any]]] = []
    for candidate in candidates:
        key = ranking_key(
            candidate["metrics_by_stratum"], candidate["threshold"],
            candidate.get("secondary_threshold_or_margin", 0),
        )
        canonical = canonical_bytes(candidate).decode("utf-8")
        ranked.append((key, canonical, candidate))
    key, _, selected = max(ranked, key=lambda item: (item[0], item[1]))
    result = dict(selected)
    result["preferred_development_criterion_met"] = bool(key[0])
    result["ranking_key"] = [str(value) for value in key]
    return result


def validate_settings(
    pipeline_id: str, values: Mapping[str, Any], *, exact_tasks: bool,
    threshold_source: str = "development",
) -> None:
    expected = SCORE_CONTRACT[pipeline_id]
    if exact_tasks and set(values) != set(expected):
        raise ValueError(f"threshold task set mismatch for {pipeline_id}")
    for task, setting in values.items():
        if task not in expected or not isinstance(setting, Mapping):
            raise ValueError(f"unknown threshold setting {pipeline_id}/{task}")
        score_name, needs_margin = expected[task]
        if setting.get("score_name") != score_name or setting.get("score_range") != [0.0, 1.0] or setting.get("threshold_source") != threshold_source:
            raise ValueError(f"score-domain mismatch for {pipeline_id}/{task}")
        threshold = setting.get("threshold")
        if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not 0 <= threshold <= 1:
            raise ValueError(f"invalid threshold for {pipeline_id}/{task}")
        if needs_margin:
            margin = setting.get("minimum_top_two_margin")
            if isinstance(margin, bool) or not isinstance(margin, (int, float)) or not 0 <= margin <= 1:
                raise ValueError(f"missing/invalid top-two margin for {pipeline_id}/{task}")


def freeze_settings(
    settings_path: Path, manifest_path: Path, results: Path, output: Path, *,
    score_manifest: Path, inventory: Path, entity_scopes: Path, fit_report: Path,
) -> dict[str, Any]:
    """Freeze v3.3-fitted settings and every independently replayable input."""

    if output.exists():
        raise ValueError("threshold freeze output already exists")
    for name in ("validation", "validation-repeat"):
        if (results / name).exists() and any((results / name).rglob("*.json")):
            raise ValueError("thresholds cannot be frozen after validation output")
    development = results / "development"
    if not (development / ".complete").is_file() or len(list(development.rglob("*.json"))) != 240:
        raise ValueError("threshold freeze requires the complete 240-record development run")
    settings = read_json(settings_path)
    validate("development_threshold_settings_v3_3.schema.json", settings)
    score_record = read_json(score_manifest)
    scopes_record = read_json(entity_scopes)
    report_record = read_json(fit_report)
    inventory_record = read_json(inventory)
    validate("development_score_manifest_v3_3.schema.json", score_record)
    validate("development_entity_scopes_v3_3.schema.json", scopes_record)
    validate("threshold_fit_report_v3_3.schema.json", report_record)
    if inventory_record.get("schema_version") != "sha256-inventory-v1" or not isinstance(inventory_record.get("files"), list):
        raise ValueError("invalid calibration SHA-256 inventory")
    contract = load_active_contract()
    if score_record["config_hashes"] != dict(contract.config_hashes):
        raise ValueError("score manifest configuration hashes are not active v3.3")
    if score_record["manifest_sha256"] != sha256_file(manifest_path):
        raise ValueError("score manifest dataset hash mismatch")
    if scopes_record["score_manifest_sha256"] != sha256_file(score_manifest):
        raise ValueError("entity scopes do not bind the score manifest")
    if (
        report_record["score_manifest_sha256"] != sha256_file(score_manifest)
        or report_record["entity_scopes_sha256"] != sha256_file(entity_scopes)
    ):
        raise ValueError("threshold report provenance mismatch")
    if set(settings.get("pipelines", {})) != set(SCORE_CONTRACT):
        raise ValueError("development settings must contain both frozen pipelines")
    for pipeline, values in settings["pipelines"].items():
        validate_settings(pipeline, values, exact_tasks=True)
        for task, setting in values.items():
            selection_name = "predicate_connectivity" if task in {"predicate", "connectivity"} else task
            selected = report_record["selected"].get(f"{pipeline}/{selection_name}")
            if not isinstance(selected, Mapping):
                raise ValueError(f"fit report lacks selected setting for {pipeline}/{task}")
            expected = selected.get(
                "secondary_threshold_or_margin" if task == "connectivity" else "threshold"
            )
            if setting["threshold"] != expected:
                raise ValueError(f"settings/report threshold mismatch for {pipeline}/{task}")
            if "minimum_top_two_margin" in setting and setting["minimum_top_two_margin"] != selected.get("secondary_threshold_or_margin"):
                raise ValueError(f"settings/report margin mismatch for {pipeline}/{task}")
    value = {
        "schema_version": "threshold-freeze-v3.3.0",
        "status": "frozen_before_validation",
        "calibration_version": CALIBRATION_VERSION,
        "development_manifest_sha256": sha256_file(manifest_path),
        "development_results_sha256": sha256_tree(development),
        "development_score_manifest_sha256": sha256_file(score_manifest),
        "calibration_inventory_sha256": sha256_file(inventory),
        "entity_scopes_sha256": sha256_file(entity_scopes),
        "threshold_fit_report_sha256": sha256_file(fit_report),
        "settings_sha256": sha256_file(settings_path),
        "frozen_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "pipelines": settings["pipelines"],
    }
    validate("threshold_freeze_v3_3.schema.json", value)
    atomic_write(output, canonical_bytes(value))
    return {"output": str(output), "sha256": sha256_file(output)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and freeze development-fitted P9-v3B thresholds")
    parser.add_argument("--settings", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--score-manifest", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--entity-scopes", type=Path, required=True)
    parser.add_argument("--fit-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    print(json.dumps(freeze_settings(
        args.settings, args.manifest, args.results, args.output,
        score_manifest=args.score_manifest, inventory=args.inventory,
        entity_scopes=args.entity_scopes, fit_report=args.fit_report,
    ), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
