"""Prospective v3.3 development-only score capture, fitting, and replay.

Calibration artifacts are deliberately outside the bounded observation schema.
They retain threshold-independent component scores so every frozen candidate can
be replayed without another neural-model invocation.  Only the selected replay
is compiled into the ordinary development result tree.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping

from prototype.semantic_secrets.v3 import SemanticCompilerV3, load_active_contract

from .dataset import (
    GROUND_TRUTH_VERSION, OPPORTUNITY_FIELDS, audit_ground_truth_freeze,
    audit_manifest, audit_scenario_specification, deterministic_opportunity_id,
)
from .evaluation import Counts, _reference_mapping, _scope_prediction
from .execution import AdapterSession, cache_key
from .guard import git_commit
from .io import atomic_write, canonical_bytes, read_json, sha256_file, sha256_tree
from .schemas import validate
from .thresholds import (
    CALIBRATION_VERSION, CANDIDATE_GRID, SCORE_CONTRACT, grid_values,
    ranking_key, select_candidate, validate_settings,
)


ARTIFACT_SCHEMA = "development-score-artifact-v3.3.0"
STRATA = ("A_controlled_geometric", "B_naturalistic_t2i")


def assert_validation_isolation(results: Path, artifacts: Iterable[Mapping[str, Any]] = ()) -> None:
    for name in ("validation", "validation-repeat"):
        directory = results / name
        if directory.exists() and any(directory.rglob("*.json")):
            raise ValueError("calibration refuses any existing validation or validation-repeat output")
    for artifact in artifacts:
        if artifact.get("split") != "development":
            raise ValueError("calibration artifact is not development-only")


def validate_score_payload(value: Mapping[str, Any]) -> None:
    """Fail closed on incomplete artifacts that cannot replay the frozen grid."""

    pipeline, kind, payload = value["pipeline_id"], value["artifact_kind"], value["payload"]
    if payload.get("score_capture_version") != "development-score-capture-v3.3.0":
        raise ValueError("score artifact capture version mismatch")
    if not isinstance(payload.get("component_provenance"), Mapping):
        raise ValueError("score artifact lacks component provenance")
    if kind == "entity":
        candidates = payload.get("entity_candidates")
        if not isinstance(candidates, Mapping) or set(candidates) != {_grid_key(value) for value in CANDIDATE_GRID}:
            raise ValueError("entity artifact does not contain the complete frozen grid")
        for rows in candidates.values():
            if not isinstance(rows, list):
                raise ValueError("entity candidate rows are malformed")
            for row in rows:
                score = row.get("score")
                box = row.get("bbox")
                if (
                    isinstance(score, bool) or not isinstance(score, (int, float))
                    or not math.isfinite(float(score)) or not 0 <= float(score) <= 1
                    or not isinstance(box, list) or len(box) != 4
                ):
                    raise ValueError("entity candidate score/box is malformed")
        if pipeline == "v3.1-gdino-siglip2" and not {
            "logits", "pred_boxes", "input_ids"
        } <= set(payload.get("raw_postprocess_inputs", {})):
            raise ValueError("Grounding DINO artifact lacks raw postprocessor inputs")
        if pipeline == "v3.1-egtr-siglip2" and not all(
            isinstance(payload.get(name), list) for name in ("threshold_independent_objects", "relations")
        ):
            raise ValueError("EGTR artifact lacks threshold-independent object/relation scores")
    elif kind == "downstream":
        tasks = payload.get("siglip_tasks")
        if not isinstance(tasks, Mapping) or set(tasks) != set(_siglip_tasks(pipeline)):
            raise ValueError("downstream artifact task set mismatch")
        contract = load_active_contract()
        expected_labels = {
            **{task: list(labels) for task, labels in contract.base_observation["attributes"].items()},
            "unary_action": list(contract.base_observation["unary_actions"]),
            "binary_interaction": list(contract.base_observation["binary_interactions"]),
            "scene": list(contract.base_observation["scenes"]),
        }
        for task, rows in tasks.items():
            if not isinstance(rows, list):
                raise ValueError("SigLIP task vectors are malformed")
            for row in rows:
                labels, prompts, scores = row.get("labels"), row.get("prompts"), row.get("scores")
                if (
                    not isinstance(labels, list) or not labels
                    or labels != expected_labels[task]
                    or not isinstance(prompts, list) or not isinstance(scores, list)
                    or len(labels) != len(prompts) or len(labels) != len(scores)
                    or not isinstance(row.get("scope"), Mapping)
                    or not isinstance(row.get("crop_provenance"), Mapping)
                    or row.get("score_name") != "siglip2_sigmoid_logit"
                    or row.get("score_range") != [0.0, 1.0]
                    or any(isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(float(score)) or not 0 <= float(score) <= 1 for score in scores)
                ):
                    raise ValueError("incomplete SigLIP closed-label score vector")


def _grid_key(value: Fraction | float) -> str:
    return f"{float(value):.2f}"


def _setting(pipeline: str, task: str, threshold: float, margin: float | None = None) -> dict[str, Any]:
    score_name, needs_margin = SCORE_CONTRACT[pipeline][task]
    value: dict[str, Any] = {
        "score_name": score_name,
        "score_range": [0.0, 1.0],
        "threshold": threshold,
        "threshold_source": "development",
    }
    if needs_margin:
        if margin is None:
            raise ValueError(f"{pipeline}/{task} requires a top-two margin")
        value["minimum_top_two_margin"] = margin
    return value


def _component_events(pipeline: str, *artifacts: Mapping[str, Any]) -> list[dict[str, Any]]:
    contract = load_active_contract()
    found: dict[str, dict[str, Any]] = {}
    for artifact in artifacts:
        for row in artifact.get("payload", {}).get("component_events", []):
            found[row["component_id"]] = dict(row)
    rows = []
    for component_id, component in sorted(contract.component_map(pipeline).items()):
        rows.append(found.get(component_id, {
            "component_id": component_id,
            "component_revision": component["revision"],
            "status": "abstain",
            "failure_code": None,
            "elapsed_seconds": 0.0,
            "peak_rss_bytes": 0,
            "peak_gpu_bytes": 0,
        }))
    return rows


def _confidence(score: float, setting: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "value": round(float(score), 6),
        "score_name": setting["score_name"],
        "score_range": setting["score_range"],
        "threshold": setting["threshold"],
        "threshold_source": "development",
    }


def _base_observation(pipeline: str, artifact: Mapping[str, Any], *others: Mapping[str, Any]) -> dict[str, Any]:
    contract = load_active_contract()
    return {
        "observation_version": contract.observation_version,
        "pipeline_id": pipeline,
        "pipeline_revision": contract.expected_pipeline_revision(pipeline),
        "image_id": artifact["image_id"],
        "image_sha256": artifact["image_sha256"],
        "detections": [],
        "attributes": [],
        "unary_actions": [],
        "binary_interactions": [],
        "scenes": [],
        "component_events": _component_events(pipeline, artifact, *others),
        "execution_telemetry": [
            row for item in (artifact, *others)
            for row in item.get("payload", {}).get("execution_telemetry", [])
        ],
    }


def _entity_rows(artifact: Mapping[str, Any], threshold: float) -> list[dict[str, Any]]:
    rows = artifact["payload"].get("entity_candidates", {}).get(_grid_key(threshold))
    if not isinstance(rows, list):
        raise ValueError(f"missing entity candidate {_grid_key(threshold)} in {artifact['image_id']}")
    return rows


def _add_entities(observation: dict[str, Any], pipeline: str, artifact: Mapping[str, Any], threshold: float) -> None:
    setting = _setting(pipeline, "entity", threshold)
    component_id = "grounding-dino-tiny" if pipeline == "v3.1-gdino-siglip2" else "egtr-vg"
    revision = load_active_contract().component_map(pipeline)[component_id]["revision"]
    for row in _entity_rows(artifact, threshold):
        observation["detections"].append({
            "local_id": row["local_id"], "category": row["category"], "bbox": row["bbox"],
            "confidence": _confidence(row["score"], setting),
            "component_id": component_id, "component_revision": revision,
        })


def _winner(row: Mapping[str, Any], threshold: float, margin: float) -> tuple[str, float] | None:
    labels, scores = row.get("labels"), row.get("scores")
    if not isinstance(labels, list) or not isinstance(scores, list) or len(labels) != len(scores) or not labels:
        raise ValueError("malformed complete SigLIP score vector")
    order = sorted(range(len(scores)), key=lambda index: (-float(scores[index]), str(labels[index])))
    best = order[0]
    second = order[1] if len(order) > 1 else best
    delta = float(scores[best]) - float(scores[second]) if len(order) > 1 else float(scores[best])
    if float(scores[best]) < threshold or delta < margin:
        return None
    return str(labels[best]), float(scores[best])


def _add_siglip_task(
    observation: dict[str, Any], pipeline: str, artifact: Mapping[str, Any],
    task: str, threshold: float, margin: float,
) -> None:
    setting = _setting(pipeline, task, threshold, margin)
    revision = load_active_contract().component_map(pipeline)["siglip2-base-384"]["revision"]
    for row in artifact["payload"].get("siglip_tasks", {}).get(task, []):
        selected = _winner(row, threshold, margin)
        if selected is None:
            continue
        value, score = selected
        common = {
            "confidence": _confidence(score, setting),
            "component_id": "siglip2-base-384", "component_revision": revision,
        }
        scope = row["scope"]
        if task in {"colour", "size", "material", "pattern"}:
            observation["attributes"].append({
                "detection_id": scope["detection_id"], "attribute_type": task,
                "value": value, **common,
            })
        elif task == "unary_action":
            observation["unary_actions"].append({
                "detection_id": scope["detection_id"], "action": value, **common,
            })
        elif task == "binary_interaction":
            observation["binary_interactions"].append({
                "source_detection_id": scope["source_detection_id"],
                "target_detection_id": scope["target_detection_id"],
                "interaction": value, **common,
            })
        elif task == "scene":
            observation["scenes"].append({"value": value, **common})
        else:  # pragma: no cover - guarded by SCORE_CONTRACT
            raise ValueError(f"unsupported SigLIP task {task}")


def _add_egtr_relations(
    observation: dict[str, Any], artifact: Mapping[str, Any], predicate: float,
    connectivity: float,
) -> None:
    retained = {row["local_id"] for row in observation["detections"]}
    predicate_setting = _setting("v3.1-egtr-siglip2", "predicate", predicate)
    connectivity_setting = _setting("v3.1-egtr-siglip2", "connectivity", connectivity)
    revision = load_active_contract().component_map("v3.1-egtr-siglip2")["egtr-vg"]["revision"]
    for row in artifact["payload"].get("relations", []):
        if row["source_detection_id"] not in retained or row["target_detection_id"] not in retained:
            continue
        if float(row["predicate_score"]) < predicate or float(row["connectivity_score"]) < connectivity:
            continue
        observation["binary_interactions"].append({
            "source_detection_id": row["source_detection_id"],
            "target_detection_id": row["target_detection_id"],
            "interaction": row["interaction"],
            "confidence": _confidence(row["predicate_score"], predicate_setting),
            "connectivity_confidence": _confidence(row["connectivity_score"], connectivity_setting),
            "component_id": "egtr-vg", "component_revision": revision,
        })


def _compile(observation: Mapping[str, Any]) -> dict[str, Any]:
    return SemanticCompilerV3().compile_object(observation)


def _read_development_opportunities(
    path: Path, development: Mapping[str, Mapping[str, Any]],
    scenarios: Mapping[str, Mapping[str, Any]],
) -> dict[str, list[dict[str, str]]]:
    rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    counts: Counter[tuple[str, str, str]] = Counter()
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != OPPORTUNITY_FIELDS:
            raise ValueError("support-opportunity header does not match v3.2 exactly")
        for row in reader:
            if row["split"] != "development":
                continue
            image = development.get(row["image_id"])
            if image is None:
                raise ValueError("development opportunity references a non-development image")
            if row["opportunity_id"] != deterministic_opportunity_id(row):
                raise ValueError("development opportunity identifier is not deterministic")
            if row["ground_truth_version"] != GROUND_TRUTH_VERSION:
                raise ValueError("development opportunity ground-truth version mismatch")
            if any(row[name] != str(image[name]) for name in ("family_id", "stratum", "split", "scenario_specification_id")):
                raise ValueError("development opportunity scope disagrees with manifest")
            scenario = scenarios[row["image_id"]]
            atoms = scenario["reference_atoms"]
            exact = any(
                atom["atom_type"] == row["atom_type"]
                and str(atom["value"]) == row["reference_value"]
                and (atom["source_reference_id"] or "") == row["source_reference_id"]
                and (atom["target_reference_id"] or "") == row["target_reference_id"]
                and (atom.get("scope_category") or "") == row["scope_category"]
                for atom in atoms
            )
            if exact != (row["polarity"] == "positive"):
                raise ValueError("development opportunity polarity contradicts scenario")
            counts[(row["stratum"], row["atom_type"], row["polarity"])] += 1
            rows[row["image_id"]].append(row)
    plan = load_active_contract().amend_prereg["dataset_support"]["validation_plan_each_stratum"]
    for stratum in STRATA:
        for atom_type, rule in plan.items():
            for polarity in ("positive", "negative"):
                if counts[(stratum, atom_type, polarity)] != int(rule[polarity]):
                    raise ValueError(f"development support mismatch for {stratum}/{atom_type}/{polarity}")
    return rows


def _context(manifest_path: Path, opportunities_path: Path, data_root: Path) -> tuple[dict[str, Any], dict[str, list[dict[str, str]]], dict[str, dict[str, Any]]]:
    manifest = read_json(manifest_path)
    audit_manifest(manifest)
    development = {row["image_id"]: row for row in manifest["images"] if row["split"] == "development"}
    scenarios = {
        image_id: read_json(data_root / row["scenario_specification_path"])
        for image_id, row in development.items()
    }
    for image_id, scenario in scenarios.items():
        audit_scenario_specification(scenario, development[image_id])
    return manifest, _read_development_opportunities(opportunities_path, development, scenarios), scenarios


def _metrics(
    results: Mapping[str, Mapping[str, Any]], atom_type: str,
    manifest: Mapping[str, Any], opportunities: Mapping[str, list[dict[str, str]]],
    scenarios: Mapping[str, Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    image_rows = {row["image_id"]: row for row in manifest["images"]}
    totals = {stratum: Counts() for stratum in STRATA}
    for image_id in sorted(results):
        result = results[image_id]
        stratum = image_rows[image_id]["stratum"]
        selected = [row for row in opportunities[image_id] if row["atom_type"] == atom_type]
        if result.get("status") == "graph":
            mapping = _reference_mapping(scenarios[image_id], result)
            for opportunity in selected:
                exact, covered = _scope_prediction(opportunity, result, scenarios[image_id], mapping)
                totals[stratum].add(opportunity["polarity"], exact, covered)
        else:
            for opportunity in selected:
                totals[stratum].add(opportunity["polarity"], False, False)
    report: dict[str, dict[str, Any]] = {}
    for stratum, counts in totals.items():
        precision = Fraction(counts.tp, counts.tp + counts.fp) if counts.tp + counts.fp else Fraction()
        recall = Fraction(counts.tp, counts.tp + counts.fn) if counts.tp + counts.fn else Fraction()
        f1 = Fraction(2 * counts.tp, 2 * counts.tp + counts.fp + counts.fn) if 2 * counts.tp + counts.fp + counts.fn else Fraction()
        coverage = Fraction(counts.covered, counts.opportunities) if counts.opportunities else Fraction()
        report[stratum] = {
            "counts": {"tp": counts.tp, "fp": counts.fp, "fn": counts.fn, "covered": counts.covered, "opportunities": counts.opportunities},
            "precision": float(precision), "recall": float(recall),
            "f1": float(f1), "coverage": float(coverage),
            "precision_exact": str(precision), "recall_exact": str(recall),
            "f1_exact": str(f1), "coverage_exact": str(coverage),
        }
    return report


def _candidate_record(threshold: float, secondary: float, metrics: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    value = {
        "threshold": threshold,
        "secondary_threshold_or_margin": secondary,
        "metrics_by_stratum": metrics,
    }
    key = ranking_key(metrics, threshold, secondary)
    value["preferred_development_criterion_met"] = bool(key[0])
    value["ranking_key"] = [str(item) for item in key]
    return value


def _write_candidate_table(path: Path, rows: list[dict[str, Any]]) -> None:
    payload = b"".join(canonical_bytes(row) for row in rows)
    atomic_write(path, payload)


def _load_artifacts(score_root: Path, score_manifest: Path) -> dict[tuple[str, str, str], dict[str, Any]]:
    manifest = read_json(score_manifest)
    validate("development_score_manifest_v3_3.schema.json", manifest)
    artifacts: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in manifest["artifacts"]:
        path = score_root / row["relative_path"]
        if not path.is_file() or path.stat().st_size != row["bytes"] or sha256_file(path) != row["sha256"]:
            raise ValueError(f"score artifact provenance mismatch: {path}")
        value = read_json(path)
        validate("development_score_artifact_v3_3.schema.json", value)
        validate_score_payload(value)
        expected_provenance = {
            "config_hashes": manifest["config_hashes"],
            "manifest_sha256": manifest["manifest_sha256"],
            "opportunities_sha256": manifest["opportunities_sha256"],
            "ground_truth_freeze_sha256": manifest["ground_truth_freeze_sha256"],
        }
        if any(value["provenance"].get(name) != expected for name, expected in expected_provenance.items()):
            raise ValueError(f"score artifact has inconsistent provenance: {path}")
        key = (value["artifact_kind"], value["pipeline_id"], value["image_id"])
        if key in artifacts:
            raise ValueError(f"duplicate score artifact {key}")
        artifacts[key] = value
    assert_validation_isolation(Path("."), artifacts.values())
    return artifacts


def build_score_manifest(
    score_root: Path, output: Path, inventory: Path, manifest_path: Path,
    opportunities_path: Path, ground_truth_path: Path,
) -> dict[str, Any]:
    contract = load_active_contract()
    rows = []
    for path in sorted((score_root / "artifacts").rglob("*.json")):
        value = read_json(path)
        validate("development_score_artifact_v3_3.schema.json", value)
        validate_score_payload(value)
        rows.append({
            "artifact_kind": value["artifact_kind"], "pipeline_id": value["pipeline_id"],
            "image_id": value["image_id"], "relative_path": path.relative_to(score_root).as_posix(),
            "bytes": path.stat().st_size, "sha256": sha256_file(path),
        })
    value = {
        "schema_version": "development-score-manifest-v3.3.0",
        "status": "development_only_threshold_independent_scores",
        "config_hashes": dict(contract.config_hashes),
        "manifest_sha256": sha256_file(manifest_path),
        "opportunities_sha256": sha256_file(opportunities_path),
        "ground_truth_freeze_sha256": sha256_file(ground_truth_path),
        "artifacts": rows,
    }
    validate("development_score_manifest_v3_3.schema.json", value)
    atomic_write(output, canonical_bytes(value))
    inventory_rows = [
        {"relative_path": row["relative_path"], "bytes": row["bytes"], "sha256": row["sha256"]}
        for row in rows
    ] + [{"relative_path": output.name, "bytes": output.stat().st_size, "sha256": sha256_file(output)}]
    atomic_write(inventory, canonical_bytes({"schema_version": "sha256-inventory-v1", "files": sorted(inventory_rows, key=lambda row: row["relative_path"])}))
    return value


def _write_score_artifact(score_root: Path, value: dict[str, Any]) -> Path:
    validate("development_score_artifact_v3_3.schema.json", value)
    validate_score_payload(value)
    payload = canonical_bytes(value)
    import hashlib
    digest = hashlib.sha256(payload).hexdigest()
    directory = score_root / "artifacts" / value["artifact_kind"] / value["pipeline_id"]
    path = directory / f"{value['image_id']}.{digest}.json"
    existing = list(directory.glob(f"{value['image_id']}.*.json")) if directory.exists() else []
    if existing:
        if len(existing) == 1 and sha256_file(existing[0]) == digest:
            return existing[0]
        raise ValueError(f"score artifact already exists with different content for {value['image_id']}")
    atomic_write(path, payload)
    return path


def capture(args: argparse.Namespace) -> dict[str, Any]:
    assert_validation_isolation(args.results)
    contract = load_active_contract()
    manifest = read_json(args.manifest)
    audit_ground_truth_freeze(read_json(args.ground_truth), args.manifest, args.opportunities, args.data)
    development = [row for row in manifest["images"] if row["split"] == "development"]
    scope_rows: dict[tuple[str, str], Any] = {}
    if args.stage == "downstream":
        scopes = read_json(args.entity_scopes)
        validate("development_entity_scopes_v3_3.schema.json", scopes)
        scope_rows = {(row["pipeline_id"], row["image_id"]): row["detections"] for row in scopes["scopes"]}
    provenance = {
        "git_commit": git_commit(), "config_hashes": dict(contract.config_hashes),
        "ground_truth_freeze_sha256": sha256_file(args.ground_truth),
        "manifest_sha256": sha256_file(args.manifest),
        "opportunities_sha256": sha256_file(args.opportunities),
        "model_manifest_sha256": sha256_file(args.model_manifest),
        "adapter_source_sha256": sha256_tree(args.adapter_source),
    }
    produced = 0
    for pipeline in contract.pipeline_ids:
        with AdapterSession(args.adapter_command[pipeline]) as session:
            for image in development:
                image_path = args.data / image["relative_path"]
                if not image_path.is_file() or sha256_file(image_path) != image["image_sha256"]:
                    raise ValueError(f"missing or hash-mismatched development image {image['image_id']}")
                request = {
                    "adapter_protocol": "bounded-observation-adapter-v3.1.0",
                    "operation": f"calibration_capture_{args.stage}",
                    "mode": "calibration", "pipeline_id": pipeline,
                    "pipeline_revision": contract.expected_pipeline_revision(pipeline),
                    "image_id": image["image_id"], "image_path": str(image_path.resolve()),
                    "image_sha256": image["image_sha256"], "timeout_seconds": args.timeout_seconds,
                }
                if args.stage == "downstream":
                    request["entity_scope"] = scope_rows[(pipeline, image["image_id"])]
                payload = session.request(request)
                value = {
                    "schema_version": ARTIFACT_SCHEMA, "artifact_kind": args.stage,
                    "split": "development", "pipeline_id": pipeline,
                    "image_id": image["image_id"], "image_sha256": image["image_sha256"],
                    "provenance": provenance, "payload": payload,
                }
                _write_score_artifact(args.score_root, value)
                produced += 1
    build_score_manifest(args.score_root, args.score_manifest, args.inventory, args.manifest, args.opportunities, args.ground_truth)
    return {"stage": args.stage, "artifacts": produced, "score_manifest_sha256": sha256_file(args.score_manifest)}


def fit_entities(args: argparse.Namespace) -> dict[str, Any]:
    assert_validation_isolation(args.results)
    if args.output.exists():
        raise ValueError("entity-scope freeze already exists")
    manifest, opportunities, scenarios = _context(args.manifest, args.opportunities, args.data)
    artifacts = _load_artifacts(args.score_root, args.score_manifest)
    score_record = read_json(args.score_manifest)
    if score_record["manifest_sha256"] != sha256_file(args.manifest) or score_record["opportunities_sha256"] != sha256_file(args.opportunities):
        raise ValueError("score manifest does not bind the requested development dataset")
    expected_images = sorted(row["image_id"] for row in manifest["images"] if row["split"] == "development")
    selected_thresholds: dict[str, float] = {}
    entity_selection: dict[str, Any] = {}
    scopes: list[dict[str, Any]] = []
    args.candidate_metrics.mkdir(parents=True, exist_ok=True)
    for pipeline in load_active_contract().pipeline_ids:
        entity_artifacts = {image_id: artifacts[("entity", pipeline, image_id)] for image_id in expected_images}
        candidates = []
        for threshold_fraction in CANDIDATE_GRID:
            threshold = float(threshold_fraction)
            results = {}
            for image_id, artifact in entity_artifacts.items():
                observation = _base_observation(pipeline, artifact)
                _add_entities(observation, pipeline, artifact, threshold)
                results[image_id] = _compile(observation)
            metrics = _metrics(results, "entity", manifest, opportunities, scenarios)
            candidates.append(_candidate_record(threshold, 0.0, metrics))
        _write_candidate_table(args.candidate_metrics / f"{pipeline}.entity.jsonl", candidates)
        selected = select_candidate(candidates)
        entity_selection[pipeline] = selected
        threshold = float(selected["threshold"])
        selected_thresholds[pipeline] = threshold
        for image_id, artifact in entity_artifacts.items():
            scopes.append({"pipeline_id": pipeline, "image_id": image_id, "detections": _entity_rows(artifact, threshold)})
    value = {
        "schema_version": "development-entity-scopes-v3.3.0",
        "score_manifest_sha256": sha256_file(args.score_manifest),
        "selected_entity_thresholds": selected_thresholds,
        "entity_selection": entity_selection,
        "scopes": sorted(scopes, key=lambda row: (row["pipeline_id"], row["image_id"])),
    }
    validate("development_entity_scopes_v3_3.schema.json", value)
    atomic_write(args.output, canonical_bytes(value))
    return {"output": str(args.output), "sha256": sha256_file(args.output), "thresholds": selected_thresholds}


def _siglip_tasks(pipeline: str) -> tuple[str, ...]:
    excluded = {"entity", "predicate", "connectivity"}
    return tuple(task for task in SCORE_CONTRACT[pipeline] if task not in excluded)


def fit_all(args: argparse.Namespace) -> dict[str, Any]:
    assert_validation_isolation(args.results)
    for path in (args.settings, args.report, args.inventory):
        if path.exists():
            raise ValueError(f"calibration output already exists: {path}")
    development = args.results / "development"
    if development.exists() and any(development.iterdir()):
        raise ValueError("integrated development result directory is not empty")
    manifest, opportunities, scenarios = _context(args.manifest, args.opportunities, args.data)
    artifacts = _load_artifacts(args.score_root, args.score_manifest)
    score_record = read_json(args.score_manifest)
    if any((
        score_record["manifest_sha256"] != sha256_file(args.manifest),
        score_record["opportunities_sha256"] != sha256_file(args.opportunities),
        score_record["ground_truth_freeze_sha256"] != sha256_file(args.ground_truth),
    )):
        raise ValueError("score manifest does not bind the requested development dataset/ground truth")
    scopes_value = read_json(args.entity_scopes)
    validate("development_entity_scopes_v3_3.schema.json", scopes_value)
    scope_map = {(row["pipeline_id"], row["image_id"]): row for row in scopes_value["scopes"]}
    expected_images = sorted(row["image_id"] for row in manifest["images"] if row["split"] == "development")
    args.candidate_metrics.mkdir(parents=True, exist_ok=True)
    settings: dict[str, dict[str, Any]] = {}
    preferred: dict[str, bool] = {}
    selections: dict[str, Any] = {}
    for pipeline in load_active_contract().pipeline_ids:
        entity_threshold = float(scopes_value["selected_entity_thresholds"][pipeline])
        settings[pipeline] = {"entity": _setting(pipeline, "entity", entity_threshold)}
        selections[f"{pipeline}/entity"] = scopes_value["entity_selection"][pipeline]
        preferred[f"{pipeline}/entity"] = bool(scopes_value["entity_selection"][pipeline]["preferred_development_criterion_met"])
        entity_artifacts = {image_id: artifacts[("entity", pipeline, image_id)] for image_id in expected_images}
        downstream = {image_id: artifacts[("downstream", pipeline, image_id)] for image_id in expected_images}
        if pipeline == "v3.1-egtr-siglip2":
            candidates = []
            for predicate_fraction in CANDIDATE_GRID:
                predicate = float(predicate_fraction)
                for connectivity_fraction in CANDIDATE_GRID:
                    connectivity = float(connectivity_fraction)
                    results = {}
                    for image_id, artifact in entity_artifacts.items():
                        observation = _base_observation(pipeline, artifact, downstream[image_id])
                        _add_entities(observation, pipeline, artifact, entity_threshold)
                        _add_egtr_relations(observation, artifact, predicate, connectivity)
                        results[image_id] = _compile(observation)
                    metrics = _metrics(results, "binary_interaction", manifest, opportunities, scenarios)
                    candidates.append(_candidate_record(predicate, connectivity, metrics))
            _write_candidate_table(args.candidate_metrics / f"{pipeline}.predicate-connectivity.jsonl", candidates)
            selected = select_candidate(candidates)
            predicate, connectivity = float(selected["threshold"]), float(selected["secondary_threshold_or_margin"])
            settings[pipeline]["predicate"] = _setting(pipeline, "predicate", predicate)
            settings[pipeline]["connectivity"] = _setting(pipeline, "connectivity", connectivity)
            key = f"{pipeline}/predicate_connectivity"
            preferred[key] = bool(selected["preferred_development_criterion_met"])
            selections[key] = selected
        for task in _siglip_tasks(pipeline):
            candidates = []
            for threshold_fraction in CANDIDATE_GRID:
                threshold = float(threshold_fraction)
                for margin_fraction in CANDIDATE_GRID:
                    margin = float(margin_fraction)
                    results = {}
                    for image_id, artifact in entity_artifacts.items():
                        observation = _base_observation(pipeline, artifact, downstream[image_id])
                        _add_entities(observation, pipeline, artifact, entity_threshold)
                        _add_siglip_task(observation, pipeline, downstream[image_id], task, threshold, margin)
                        results[image_id] = _compile(observation)
                    metrics = _metrics(results, task, manifest, opportunities, scenarios)
                    candidates.append(_candidate_record(threshold, margin, metrics))
            _write_candidate_table(args.candidate_metrics / f"{pipeline}.{task}.jsonl", candidates)
            selected = select_candidate(candidates)
            threshold, margin = float(selected["threshold"]), float(selected["secondary_threshold_or_margin"])
            settings[pipeline][task] = _setting(pipeline, task, threshold, margin)
            key = f"{pipeline}/{task}"
            preferred[key] = bool(selected["preferred_development_criterion_met"])
            selections[key] = selected
        validate_settings(pipeline, settings[pipeline], exact_tasks=True)
    settings_value = {
        "schema_version": "development-threshold-settings-v3.3.0",
        "calibration_version": CALIBRATION_VERSION,
        "preferred_development_criterion_met": preferred,
        "pipelines": settings,
    }
    validate("development_threshold_settings_v3_3.schema.json", settings_value)
    atomic_write(args.settings, canonical_bytes(settings_value))

    for pipeline in load_active_contract().pipeline_ids:
        entity_threshold = float(settings[pipeline]["entity"]["threshold"])
        for image_id in expected_images:
            entity_artifact = artifacts[("entity", pipeline, image_id)]
            downstream_artifact = artifacts[("downstream", pipeline, image_id)]
            observation = _base_observation(pipeline, entity_artifact, downstream_artifact)
            _add_entities(observation, pipeline, entity_artifact, entity_threshold)
            if pipeline == "v3.1-egtr-siglip2":
                _add_egtr_relations(
                    observation, entity_artifact,
                    float(settings[pipeline]["predicate"]["threshold"]),
                    float(settings[pipeline]["connectivity"]["threshold"]),
                )
            for task in _siglip_tasks(pipeline):
                task_setting = settings[pipeline][task]
                _add_siglip_task(
                    observation, pipeline, downstream_artifact, task,
                    float(task_setting["threshold"]),
                    float(task_setting["minimum_top_two_margin"]),
                )
            compiled = _compile(observation)
            request = {
                "mode": "development", "pipeline_id": pipeline, "image_id": image_id,
                "image_sha256": entity_artifact["image_sha256"],
                "pipeline_revision": load_active_contract().expected_pipeline_revision(pipeline),
                "thresholds": settings[pipeline], "calibration_version": CALIBRATION_VERSION,
                "development_score_manifest_sha256": sha256_file(args.score_manifest),
                "ground_truth_freeze_sha256": sha256_file(args.ground_truth),
                "opportunities_sha256": sha256_file(args.opportunities),
                "model_manifest_sha256": entity_artifact["provenance"]["model_manifest_sha256"],
                "adapter_source_sha256": entity_artifact["provenance"]["adapter_source_sha256"],
            }
            record = {
                "cache_key": cache_key(request),
                "request": request, "observation": observation, "compiler_result": compiled,
                "pipeline_failure": None,
                "complete_pipeline_elapsed_seconds": sum(float(row.get("elapsed_seconds", 0)) for row in observation["execution_telemetry"]),
                "controller_telemetry": None,
            }
            atomic_write(development / pipeline / f"{image_id}.json", canonical_bytes(record))
    atomic_write(development / ".complete", canonical_bytes({
        "schema_version": "development-replay-complete-v3.3.0",
        "records": len(expected_images) * len(load_active_contract().pipeline_ids),
        "settings_sha256": sha256_file(args.settings),
        "score_manifest_sha256": sha256_file(args.score_manifest),
    }))

    candidate_hash = sha256_tree(args.candidate_metrics)
    report = {
        "schema_version": "threshold-fit-report-v3.3.0",
        "calibration_version": CALIBRATION_VERSION,
        "candidate_grid": grid_values(),
        "score_manifest_sha256": sha256_file(args.score_manifest),
        "entity_scopes_sha256": sha256_file(args.entity_scopes),
        "candidate_metrics_sha256": candidate_hash,
        "selected": selections,
        "validation_isolation_confirmed": True,
    }
    validate("threshold_fit_report_v3_3.schema.json", report)
    atomic_write(args.report, canonical_bytes(report))
    named_files = [
        ("development_score_manifest_v3_3.json", args.score_manifest),
        ("development_entity_scopes_v3_3.json", args.entity_scopes),
        ("development_threshold_settings_v3_3.json", args.settings),
        ("threshold_fit_report_v3_3.json", args.report),
    ]
    named_files.extend(
        (f"candidate_metrics/{path.relative_to(args.candidate_metrics).as_posix()}", path)
        for path in sorted(args.candidate_metrics.rglob("*.jsonl"))
    )
    named_files.extend(
        (f"development/{path.relative_to(development).as_posix()}", path)
        for path in sorted(development.rglob("*")) if path.is_file()
    )
    inventory_rows = [
        {"path": name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for name, path in named_files
    ]
    atomic_write(args.inventory, canonical_bytes({"schema_version": "sha256-inventory-v1", "files": inventory_rows}))
    return {"settings": str(args.settings), "report": str(args.report), "development_records": 240}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="P9-v3B prospective v3.3 development calibration")
    sub = result.add_subparsers(dest="command", required=True)
    capture_parser = sub.add_parser("capture")
    capture_parser.add_argument("--stage", choices=["entity", "downstream"], required=True)
    capture_parser.add_argument("--adapter-command", action="append", required=True)
    for name in ("manifest", "opportunities", "ground-truth", "model-manifest", "adapter-source", "data", "results", "score-root", "score-manifest", "inventory"):
        capture_parser.add_argument(f"--{name}", type=Path, required=True)
    capture_parser.add_argument("--entity-scopes", type=Path)
    capture_parser.add_argument("--timeout-seconds", type=int, default=180)

    entity_parser = sub.add_parser("fit-entities")
    for name in ("manifest", "opportunities", "data", "results", "score-root", "score-manifest", "candidate-metrics", "output"):
        entity_parser.add_argument(f"--{name}", type=Path, required=True)

    fit_parser = sub.add_parser("fit")
    for name in ("manifest", "opportunities", "ground-truth", "data", "results", "score-root", "score-manifest", "entity-scopes", "candidate-metrics", "settings", "report", "inventory"):
        fit_parser.add_argument(f"--{name}", type=Path, required=True)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if hasattr(args, "adapter_command"):
        parsed = {}
        for value in args.adapter_command:
            pipeline, command = value.split("=", 1)
            parsed[pipeline] = command
        args.adapter_command = parsed
        if args.stage == "downstream" and args.entity_scopes is None:
            raise SystemExit("downstream capture requires --entity-scopes")
    if args.command == "capture":
        value = capture(args)
    elif args.command == "fit-entities":
        value = fit_entities(args)
    else:
        value = fit_all(args)
    print(json.dumps(value, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
