"""Formal P9-v3B preflight guard.

Formal authorization is deliberately an external record under persistent
storage. It binds an already-created Git commit without creating a
self-referential tracked commit hash.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from prototype.semantic_secrets.v3 import load_active_contract

from .dataset import audit_ground_truth_freeze
from .io import canonical_bytes, read_json, sha256_file, sha256_tree
from .schemas import validate
from .thresholds import validate_settings


ROOT = Path(__file__).resolve().parents[3]


class GuardFailure(RuntimeError):
    pass


@dataclass(frozen=True)
class FormalPaths:
    authorization: Path
    ground_truth: Path
    manifest: Path
    opportunities: Path
    thresholds: Path
    score_manifest: Path
    calibration_inventory: Path
    entity_scopes: Path
    fit_report: Path
    threshold_settings: Path
    model_manifest: Path
    gpu_environment: Path
    models: Path
    results: Path


def git_commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def _equal(label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        raise GuardFailure(f"{label} mismatch: expected {expected!r}, found {actual!r}")


def _utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def verify_formal(paths: FormalPaths, *, pipeline_ids: tuple[str, ...], mode: str | None = None, resume: bool = False) -> dict[str, Any]:
    contract = load_active_contract()
    authorization = read_json(paths.authorization)
    ground_truth = read_json(paths.ground_truth)
    manifest = read_json(paths.manifest)
    thresholds = read_json(paths.thresholds)
    score_manifest = read_json(paths.score_manifest)
    calibration_inventory = read_json(paths.calibration_inventory)
    entity_scopes = read_json(paths.entity_scopes)
    fit_report = read_json(paths.fit_report)
    threshold_settings = read_json(paths.threshold_settings)
    model_manifest = read_json(paths.model_manifest)
    gpu_environment = read_json(paths.gpu_environment)

    validate("formal_authorization_v3_2.schema.json", authorization)
    validate("ground_truth_freeze_v3_2.schema.json", ground_truth)
    validate("capability_manifest_v3_2.schema.json", manifest)
    validate("threshold_freeze_v3_3.schema.json", thresholds)
    validate("development_score_manifest_v3_3.schema.json", score_manifest)
    validate("development_entity_scopes_v3_3.schema.json", entity_scopes)
    validate("threshold_fit_report_v3_3.schema.json", fit_report)
    validate("development_threshold_settings_v3_3.schema.json", threshold_settings)
    validate("model_acquisition_v3_1.schema.json", model_manifest)
    validate("gpu_environment_v3_1.schema.json", gpu_environment)
    audit_ground_truth_freeze(ground_truth, paths.manifest, paths.opportunities, paths.manifest.parent)

    _equal("Git commit", git_commit(), authorization["expected_git_commit"])
    _equal("configuration hashes", dict(contract.config_hashes), authorization["expected_config_hashes"])
    _equal("manifest SHA-256", sha256_file(paths.manifest), authorization["expected_manifest_sha256"])
    _equal("opportunities SHA-256", sha256_file(paths.opportunities), authorization["expected_opportunities_sha256"])
    _equal("ground-truth freeze SHA-256", sha256_file(paths.ground_truth), authorization["expected_ground_truth_freeze_sha256"])
    _equal("threshold freeze SHA-256", sha256_file(paths.thresholds), authorization["expected_threshold_freeze_sha256"])
    _equal("development score manifest SHA-256", sha256_file(paths.score_manifest), thresholds["development_score_manifest_sha256"])
    _equal("calibration inventory SHA-256", sha256_file(paths.calibration_inventory), thresholds["calibration_inventory_sha256"])
    _equal("entity scopes SHA-256", sha256_file(paths.entity_scopes), thresholds["entity_scopes_sha256"])
    _equal("threshold fit report SHA-256", sha256_file(paths.fit_report), thresholds["threshold_fit_report_sha256"])
    _equal("threshold settings SHA-256", sha256_file(paths.threshold_settings), thresholds["settings_sha256"])
    _equal("threshold settings", threshold_settings["pipelines"], thresholds["pipelines"])
    _equal("score-manifest configurations", score_manifest["config_hashes"], dict(contract.config_hashes))
    _equal("fit-report score manifest", fit_report["score_manifest_sha256"], thresholds["development_score_manifest_sha256"])
    _equal("fit-report entity scopes", fit_report["entity_scopes_sha256"], thresholds["entity_scopes_sha256"])
    for row in score_manifest["artifacts"]:
        candidate = paths.score_manifest.parent / "scores" / row["relative_path"]
        if not candidate.is_file() or candidate.stat().st_size != row["bytes"] or sha256_file(candidate) != row["sha256"]:
            raise GuardFailure(f"development score artifact mismatch: {row['relative_path']}")
    if calibration_inventory.get("schema_version") != "sha256-inventory-v1" or not isinstance(calibration_inventory.get("files"), list):
        raise GuardFailure("calibration inventory is malformed")
    named_calibration = {
        "development_score_manifest_v3_3.json": paths.score_manifest,
        "development_entity_scopes_v3_3.json": paths.entity_scopes,
        "development_threshold_settings_v3_3.json": paths.threshold_settings,
        "threshold_fit_report_v3_3.json": paths.fit_report,
    }
    for row in calibration_inventory["files"]:
        logical = row.get("path")
        if logical in named_calibration:
            candidate = named_calibration[logical]
        elif isinstance(logical, str) and logical.startswith("candidate_metrics/"):
            candidate = paths.calibration_inventory.parent / logical
        elif isinstance(logical, str) and logical.startswith("development/"):
            candidate = paths.results / logical
        else:
            raise GuardFailure(f"unknown calibration inventory path: {logical!r}")
        if not candidate.is_file() or candidate.stat().st_size != row.get("bytes") or sha256_file(candidate) != row.get("sha256"):
            raise GuardFailure(f"calibration inventory mismatch: {logical}")
    candidate_rows = sorted((
        {"relative_path": row["path"].removeprefix("candidate_metrics/"), "bytes": row["bytes"], "sha256": row["sha256"]}
        for row in calibration_inventory["files"]
        if isinstance(row.get("path"), str) and row["path"].startswith("candidate_metrics/")
    ), key=lambda row: row["relative_path"])
    _equal(
        "candidate-metrics aggregate SHA-256",
        hashlib.sha256(canonical_bytes(candidate_rows)).hexdigest(),
        fit_report["candidate_metrics_sha256"],
    )
    _equal("model manifest SHA-256", sha256_file(paths.model_manifest), authorization["expected_model_manifest_sha256"])
    _equal("pipeline shortlist", list(contract.pipeline_ids), authorization["pipeline_ids"])
    _equal("requested pipelines", tuple(contract.pipeline_ids), pipeline_ids)
    if not (
        _utc(manifest["created_at_utc"])
        <= _utc(ground_truth["frozen_at_utc"])
        <= _utc(thresholds["frozen_at_utc"])
        <= _utc(authorization["authorized_at_utc"])
    ):
        raise GuardFailure("manifest/ground-truth/threshold/authorization chronology is invalid")

    for pipeline_id in contract.pipeline_ids:
        try:
            validate_settings(pipeline_id, thresholds["pipelines"][pipeline_id], exact_tasks=True)
        except ValueError as exc:
            raise GuardFailure(str(exc)) from exc
    development_dir = paths.results / "development"
    if not (development_dir / ".complete").is_file() or len(list(development_dir.rglob("*.json"))) != 240:
        raise GuardFailure("formal validation requires the complete 240-record development run")
    _equal("development result SHA-256", sha256_tree(development_dir), thresholds["development_results_sha256"])

    if not gpu_environment.get("cuda_available") or not gpu_environment.get("nvidia_smi_sha256"):
        raise GuardFailure("recorded GPU environment is missing CUDA or nvidia-smi provenance")
    _equal("container image digest", gpu_environment.get("container_image_digest"), authorization["expected_container_image_digest"])
    _equal("GPU-record config hashes", gpu_environment.get("verified_environment", {}).get("config_hashes"), dict(contract.config_hashes))
    acquired = model_manifest.get("components")
    if not isinstance(acquired, list):
        raise GuardFailure("model acquisition manifest lacks components")
    for pipeline_id in contract.pipeline_ids:
        expected = contract.component_map(pipeline_id)
        for component_id, component in expected.items():
            matches = [row for row in acquired if row.get("component_id") == component_id]
            if not matches:
                raise GuardFailure(f"model manifest lacks {component_id}")
            if not any(
                row.get("revision") == component["revision"]
                and row.get("verified") is True
                and all(row.get(key) == component[key] for key in ("model_id", "repository", "checkpoint_identity") if key in component)
                for row in matches
            ):
                raise GuardFailure(f"model revision/provenance is not verified for {component_id}")
    for row in acquired:
        files = row.get("files")
        if not isinstance(files, list) or not files:
            raise GuardFailure(f"model manifest has no file inventory for {row.get('component_id')}")
        component_root = (paths.models / row["component_id"]).resolve()
        for item in files:
            candidate = (component_root / item["relative_path"]).resolve()
            if component_root not in candidate.parents or not candidate.is_file():
                raise GuardFailure(f"model inventory path is missing or escapes its component root: {candidate}")
            if candidate.stat().st_size != item.get("bytes") or sha256_file(candidate) != item.get("sha256"):
                raise GuardFailure(f"model file provenance mismatch: {candidate}")

    for prior_dir in (paths.results / "development", paths.results / "smoke" / "development"):
        if not prior_dir.exists():
            continue
        for path in prior_dir.rglob("*.json"):
            request = read_json(path).get("request")
            if not isinstance(request, dict):
                raise GuardFailure(f"prior development/smoke record lacks request provenance: {path}")
            if (
                request.get("ground_truth_freeze_sha256") != authorization["expected_ground_truth_freeze_sha256"]
                or request.get("opportunities_sha256") != authorization["expected_opportunities_sha256"]
            ):
                raise GuardFailure(f"prior development/smoke output predates or mismatches ground truth: {path}")

    validation_dir = paths.results / "validation"
    validation_records = list(validation_dir.rglob("*.json")) if validation_dir.exists() else []
    if mode != "validation-repeat" and validation_records and not resume:
        raise GuardFailure("validation output directory is not empty; refuse overwrite or accidental second run")
    if mode == "validation-repeat" and len(validation_records) != 240:
        raise GuardFailure("validation repeat requires exactly 240 completed first-pass records")
    repeat_dir = paths.results / "validation-repeat"
    repeat_records = list(repeat_dir.rglob("*.json")) if repeat_dir.exists() else []
    if repeat_records and not resume:
        raise GuardFailure("validation-repeat output directory is not empty")
    if resume:
        expected_images = {row["image_id"]: row["image_sha256"] for row in manifest["images"] if row["split"] == "validation"}
        adapter_sha = sha256_tree(ROOT / "experiments" / "v3" / "runtime" / "adapters")
        for expected_mode, records in (("validation", validation_records), ("validation-repeat", repeat_records)):
            if len(records) > 240:
                raise GuardFailure(f"too many cached records for {expected_mode}")
            seen: set[tuple[str, str]] = set()
            for path in records:
                record = read_json(path)
                request = record.get("request")
                if not isinstance(request, dict):
                    raise GuardFailure(f"resume record lacks request: {path}")
                key = (request.get("pipeline_id"), request.get("image_id"))
                if key in seen or key[0] not in pipeline_ids or key[1] not in expected_images:
                    raise GuardFailure(f"unexpected or duplicate resume record: {path}")
                seen.add(key)
                projection = {name: value for name, value in request.items() if name not in {"image_path", "timeout_seconds"}}
                import hashlib
                actual_key = hashlib.sha256(canonical_bytes(projection)).hexdigest()
                if record.get("cache_key") != actual_key:
                    raise GuardFailure(f"resume cache-key mismatch: {path}")
                if request.get("mode") != expected_mode or request.get("image_sha256") != expected_images[key[1]]:
                    raise GuardFailure(f"resume mode/image mismatch: {path}")
                if (
                    request.get("model_manifest_sha256") != authorization["expected_model_manifest_sha256"]
                    or request.get("threshold_freeze_sha256") != authorization["expected_threshold_freeze_sha256"]
                    or request.get("ground_truth_freeze_sha256") != authorization["expected_ground_truth_freeze_sha256"]
                    or request.get("opportunities_sha256") != authorization["expected_opportunities_sha256"]
                    or request.get("adapter_source_sha256") != adapter_sha
                ):
                    raise GuardFailure(f"resume provenance mismatch: {path}")
                if request.get("pipeline_revision") != contract.expected_pipeline_revision(key[0]):
                    raise GuardFailure(f"resume pipeline revision mismatch: {path}")

    return {
        "ground_truth_status": ground_truth["status"],
        "ground_truth_freeze_sha256": authorization["expected_ground_truth_freeze_sha256"],
        "config_hashes": dict(contract.config_hashes),
        "git_commit": authorization["expected_git_commit"],
        "manifest_sha256": authorization["expected_manifest_sha256"],
        "opportunities_sha256": authorization["expected_opportunities_sha256"],
        "model_manifest_sha256": authorization["expected_model_manifest_sha256"],
        "pipeline_ids": list(pipeline_ids),
        "threshold_freeze_sha256": authorization["expected_threshold_freeze_sha256"],
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Fail-closed formal P9-v3B guard")
    result.add_argument("--formal", action="store_true", help="required acknowledgement; no default formal mode")
    result.add_argument("--resume", action="store_true", help="allow only hash-verified partial caches")
    result.add_argument("--authorization", type=Path, required=True)
    result.add_argument("--ground-truth", type=Path, required=True)
    result.add_argument("--manifest", type=Path, required=True)
    result.add_argument("--opportunities", type=Path, required=True)
    result.add_argument("--thresholds", type=Path, required=True)
    result.add_argument("--score-manifest", type=Path, required=True)
    result.add_argument("--calibration-inventory", type=Path, required=True)
    result.add_argument("--entity-scopes", type=Path, required=True)
    result.add_argument("--fit-report", type=Path, required=True)
    result.add_argument("--threshold-settings", type=Path, required=True)
    result.add_argument("--model-manifest", type=Path, required=True)
    result.add_argument("--gpu-environment", type=Path, required=True)
    result.add_argument("--models", type=Path, required=True)
    result.add_argument("--results", type=Path, required=True)
    result.add_argument("--pipeline", action="append", required=True)
    return result


def main(argv: list[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    if "--formal" not in raw:
        raise SystemExit("REFUSED: --formal is required")
    args = parser().parse_args(raw)
    try:
        record = verify_formal(
            FormalPaths(
                args.authorization, args.ground_truth, args.manifest, args.opportunities,
                args.thresholds, args.score_manifest, args.calibration_inventory,
                args.entity_scopes, args.fit_report, args.threshold_settings,
                args.model_manifest, args.gpu_environment, args.models, args.results,
            ),
            pipeline_ids=tuple(args.pipeline), mode=None, resume=args.resume,
        )
    except (GuardFailure, FileNotFoundError, ValueError) as exc:
        raise SystemExit(f"REFUSED: {exc}") from exc
    print(json.dumps(record, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
