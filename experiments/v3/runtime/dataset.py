"""Deterministic capability-manifest and project-authored ground-truth checks."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from prototype.semantic_secrets.v3 import load_active_contract

from .io import atomic_write, canonical_bytes, read_json, sha256_file
from .schemas import validate


GROUND_TRUTH_VERSION = "project-authored-ground-truth-v3.2.0"
OPPORTUNITY_FIELDS = (
    "opportunity_id", "image_id", "family_id", "stratum", "split",
    "scenario_specification_id", "atom_type", "polarity", "reference_value",
    "source_reference_id", "source_reference_bbox_xyxy", "target_reference_id",
    "target_reference_bbox_xyxy", "scope_category", "ground_truth_version",
)
SINGLE_ENTITY_TYPES = {"entity", "colour", "size", "material", "pattern", "unary_action"}
PAIR_TYPES = {"binary_interaction", "geometry_relation"}
GLOBAL_TYPES = {"count", "scene"}


def _closed_labels() -> dict[str, set[str]]:
    contract = load_active_contract()
    return {
        "entity": set(contract.amend_observation["shared_gate_entity_label_intersection"]),
        **{key: set(values) for key, values in contract.base_observation["attributes"].items()},
        "count": set(contract.base_observation["count_buckets"]),
        "unary_action": set(contract.base_observation["unary_actions"]),
        "binary_interaction": set(contract.base_observation["binary_interactions"]),
        "geometry_relation": set(contract.base_observation["derived_spatial_relations"]),
        "scene": set(contract.base_observation["scenes"]),
    }


def expected_image_ids() -> list[str]:
    return [
        f"cap-v3-{stratum}-F{family:02d}-{image:02d}"
        for stratum in ("A", "B")
        for family in range(1, 25)
        for image in range(1, 6)
    ]


def deterministic_opportunity_id(row: Mapping[str, str]) -> str:
    projection = {field: row.get(field, "") for field in OPPORTUNITY_FIELDS if field != "opportunity_id"}
    return f"opp-v3-{hashlib.sha256(canonical_bytes(projection)).hexdigest()[:20]}"


def _resolved_child(root: Path, relative: str, label: str) -> Path:
    candidate = (root / relative).resolve()
    resolved_root = root.resolve()
    if resolved_root != candidate and resolved_root not in candidate.parents:
        raise ValueError(f"{label} path escapes data root: {relative}")
    return candidate


def _validate_box(value: Any, label: str) -> tuple[float, float, float, float]:
    if not isinstance(value, list) or len(value) != 4 or any(isinstance(item, bool) or not isinstance(item, (int, float)) for item in value):
        raise ValueError(f"{label} is not a four-number normalized box")
    box = tuple(float(item) for item in value)
    if any(item < 0 or item > 1 for item in box) or box[0] >= box[2] or box[1] >= box[3]:
        raise ValueError(f"{label} is not a valid normalized xyxy box")
    return box


def audit_scenario_specification(value: dict[str, Any], manifest_row: Mapping[str, Any] | None = None) -> dict[str, Any]:
    validate("scenario_specification_v3_2.schema.json", value)
    labels = _closed_labels()
    expected_method = (
        "controlled_scene_specification"
        if value["stratum"] == "A_controlled_geometric"
        else "project_authored_naturalistic_reference"
    )
    if value["authoring_method"] != expected_method:
        raise ValueError(f"scenario authoring method does not match {value['stratum']}")
    if manifest_row is not None:
        for key in ("scenario_specification_id", "image_id", "family_id", "stratum", "split"):
            expected = manifest_row["scenario_specification_id"] if key == "scenario_specification_id" else manifest_row[key]
            if value[key] != expected:
                raise ValueError(f"scenario/manifest {key} mismatch for {manifest_row['image_id']}")
    entities: dict[str, tuple[str, tuple[float, float, float, float]]] = {}
    for entity in value["reference_entities"]:
        reference_id = entity["reference_id"]
        if reference_id in entities:
            raise ValueError(f"duplicate reference entity {reference_id} in {value['image_id']}")
        if entity["category"] not in labels["entity"]:
            raise ValueError(f"reference entity {reference_id} is outside the frozen closed labels")
        entities[reference_id] = (entity["category"], _validate_box(entity["bbox_xyxy"], reference_id))
    atom_ids: set[str] = set()
    for atom in value["reference_atoms"]:
        atom_id = atom["reference_atom_id"]
        if atom_id in atom_ids:
            raise ValueError(f"duplicate reference atom {atom_id} in {value['image_id']}")
        atom_ids.add(atom_id)
        if atom["value"] not in labels[atom["atom_type"]]:
            raise ValueError(f"reference atom {atom_id} is outside the frozen closed labels")
        source, target = atom["source_reference_id"], atom["target_reference_id"]
        if source is not None and source not in entities:
            raise ValueError(f"unknown source reference {source} in {atom_id}")
        if target is not None and target not in entities:
            raise ValueError(f"unknown target reference {target} in {atom_id}")
        if atom["atom_type"] in SINGLE_ENTITY_TYPES and (source is None or target is not None):
            raise ValueError(f"{atom_id} has invalid single-entity scope")
        if atom["atom_type"] in PAIR_TYPES and (source is None or target is None or source == target):
            raise ValueError(f"{atom_id} has invalid ordered-pair scope")
        if atom["atom_type"] in GLOBAL_TYPES and (source is not None or target is not None):
            raise ValueError(f"{atom_id} has invalid global scope")
        if atom["atom_type"] == "count":
            if atom.get("scope_category") not in labels["entity"]:
                raise ValueError(f"{atom_id} count lacks a frozen closed-label scope_category")
        elif atom.get("scope_category") is not None:
            raise ValueError(f"{atom_id} has an unexpected scope_category")
        if atom["atom_type"] == "entity" and entities[source][0] != atom["value"]:
            raise ValueError(f"entity atom {atom_id} contradicts its reference category")
    return {"entities": entities, "atoms": value["reference_atoms"]}


def audit_manifest(manifest: dict[str, Any], data_root: Path | None = None) -> dict[str, Any]:
    validate("capability_manifest_v3_2.schema.json", manifest)
    rows = manifest["images"]
    ids = [row["image_id"] for row in rows]
    if len(ids) != len(set(ids)) or sorted(ids) != sorted(expected_image_ids()):
        raise ValueError("manifest IDs do not equal the deterministic 240-image identifier set")
    family_split: dict[tuple[str, str], set[str]] = defaultdict(set)
    counts = Counter((row["stratum"], row["split"]) for row in rows)
    scenarios: dict[str, dict[str, Any]] = {}
    for row in rows:
        family_split[(row["stratum"], row["family_id"])].add(row["split"])
        expected_stratum = "A_controlled_geometric" if "-A-" in row["image_id"] else "B_naturalistic_t2i"
        if row["stratum"] != expected_stratum or row["scenario_specification_id"] != f"scenario-{row['image_id']}":
            raise ValueError(f"stratum/scenario identifier mismatch for {row['image_id']}")
        if row["stratum"] == "B_naturalistic_t2i" and (row["prompt_hash_if_applicable"] is None or row["seed_if_applicable"] is None):
            raise ValueError(f"naturalistic provenance is incomplete for {row['image_id']}")
        if data_root is not None:
            image = _resolved_child(data_root, row["relative_path"], "image")
            scenario_path = _resolved_child(data_root, row["scenario_specification_path"], "scenario")
            if not image.is_file() or sha256_file(image) != row["image_sha256"]:
                raise ValueError(f"missing or hash-mismatched image {row['image_id']}")
            if not scenario_path.is_file() or sha256_file(scenario_path) != row["scenario_specification_sha256"]:
                raise ValueError(f"missing or hash-mismatched scenario {row['image_id']}")
            scenario = read_json(scenario_path)
            audit_scenario_specification(scenario, row)
            scenarios[row["image_id"]] = scenario
    if any(len(splits) != 1 for splits in family_split.values()):
        raise ValueError("semantic scenario family crosses development/validation")
    expected_counts = Counter({
        ("A_controlled_geometric", "development"): 60,
        ("A_controlled_geometric", "validation"): 60,
        ("B_naturalistic_t2i", "development"): 60,
        ("B_naturalistic_t2i", "validation"): 60,
    })
    if counts != expected_counts:
        raise ValueError(f"split counts mismatch: {dict(counts)}")
    scenario_digest = hashlib.sha256(canonical_bytes([
        {"image_id": row["image_id"], "sha256": row["scenario_specification_sha256"]}
        for row in sorted(rows, key=lambda item: item["image_id"])
    ])).hexdigest()
    return {
        "images": len(rows),
        "sha256": hashlib.sha256(canonical_bytes(manifest)).hexdigest(),
        "scenario_specifications_sha256": scenario_digest,
        "split_counts": {"|".join(key): value for key, value in sorted(counts.items())},
        "scenarios": scenarios,
    }


def _csv_box(raw: str, label: str) -> tuple[float, float, float, float] | None:
    if not raw:
        return None
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} is not canonical JSON") from exc
    if json.dumps(value, separators=(",", ":"), allow_nan=False) != raw:
        raise ValueError(f"{label} is not canonical JSON")
    return _validate_box(value, label)


def audit_opportunities(path: Path, manifest: dict[str, Any] | None = None, data_root: Path | None = None) -> dict[str, Any]:
    contract = load_active_contract()
    config = contract.amend_prereg["dataset_support"]["validation_plan_each_stratum"]
    labels = _closed_labels()
    manifest_rows = {row["image_id"]: row for row in manifest["images"]} if manifest is not None else {}
    scenario_values: dict[str, dict[str, Any]] = {}
    if manifest is not None and data_root is not None:
        scenario_values = audit_manifest(manifest, data_root)["scenarios"]
    counts: Counter[tuple[str, str, str, str]] = Counter()
    per_image: Counter[tuple[str, str, str]] = Counter()
    seen: set[str] = set()
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != OPPORTUNITY_FIELDS:
            raise ValueError("support-opportunity header does not match v3.2 exactly")
        for row in reader:
            opportunity_id = row["opportunity_id"]
            if opportunity_id in seen or opportunity_id != deterministic_opportunity_id(row):
                raise ValueError(f"duplicate or non-deterministic opportunity_id {opportunity_id}")
            seen.add(opportunity_id)
            if row["polarity"] not in {"positive", "negative"} or row["atom_type"] not in config:
                raise ValueError(f"invalid opportunity type/polarity in {opportunity_id}")
            if row["split"] not in {"development", "validation"} or row["ground_truth_version"] != GROUND_TRUTH_VERSION:
                raise ValueError(f"invalid split/ground-truth version in {opportunity_id}")
            if row["reference_value"] not in labels[row["atom_type"]]:
                raise ValueError(f"reference value is outside the frozen closed labels in {opportunity_id}")
            source_box = _csv_box(row["source_reference_bbox_xyxy"], f"{opportunity_id} source box")
            target_box = _csv_box(row["target_reference_bbox_xyxy"], f"{opportunity_id} target box")
            source, target = row["source_reference_id"], row["target_reference_id"]
            if row["atom_type"] in SINGLE_ENTITY_TYPES and (not source or source_box is None or target or target_box is not None):
                raise ValueError(f"invalid single-entity opportunity scope in {opportunity_id}")
            if row["atom_type"] in PAIR_TYPES and (not source or source_box is None or not target or target_box is None or source == target):
                raise ValueError(f"invalid pair opportunity scope in {opportunity_id}")
            if row["atom_type"] in GLOBAL_TYPES and (source or target or source_box is not None or target_box is not None):
                raise ValueError(f"invalid global opportunity scope in {opportunity_id}")
            if row["atom_type"] == "count":
                if row["scope_category"] not in labels["entity"]:
                    raise ValueError(f"count opportunity lacks a closed-label scope_category in {opportunity_id}")
            elif row["scope_category"]:
                raise ValueError(f"unexpected scope_category in {opportunity_id}")
            counts[(row["split"], row["stratum"], row["atom_type"], row["polarity"])] += 1
            per_image[(row["image_id"], row["atom_type"], row["polarity"])] += 1
            if manifest is not None:
                manifest_row = manifest_rows.get(row["image_id"])
                if manifest_row is None:
                    raise ValueError(f"unknown image in {opportunity_id}")
                for key in ("family_id", "stratum", "split", "scenario_specification_id"):
                    expected = manifest_row["scenario_specification_id"] if key == "scenario_specification_id" else manifest_row[key]
                    if row[key] != expected:
                        raise ValueError(f"manifest {key} mismatch in {opportunity_id}")
            if scenario_values:
                audited = audit_scenario_specification(scenario_values[row["image_id"]])
                entities = audited["entities"]
                if source and (source not in entities or source_box != entities[source][1]):
                    raise ValueError(f"source reference mismatch in {opportunity_id}")
                if target and (target not in entities or target_box != entities[target][1]):
                    raise ValueError(f"target reference mismatch in {opportunity_id}")
                matching = any(
                    atom["atom_type"] == row["atom_type"]
                    and str(atom["value"]) == row["reference_value"]
                    and (atom["source_reference_id"] or "") == source
                    and (atom["target_reference_id"] or "") == target
                    and (atom.get("scope_category") or "") == row["scope_category"]
                    for atom in audited["atoms"]
                )
                if matching != (row["polarity"] == "positive"):
                    raise ValueError(f"opportunity polarity contradicts scenario in {opportunity_id}")
    for split in ("development", "validation"):
        for stratum in ("A_controlled_geometric", "B_naturalistic_t2i"):
            for atom_type, rule in config.items():
                for polarity in ("positive", "negative"):
                    expected = int(rule[polarity])
                    actual = counts[(split, stratum, atom_type, polarity)]
                    if actual != expected:
                        raise ValueError(f"{split}/{stratum}/{atom_type}/{polarity}: expected {expected}, found {actual}")
                if manifest is not None:
                    start_text, end_text = rule["families"].split("-")
                    local_start, local_end = int(start_text[1:]), int(end_text[1:])
                    for image in manifest_rows.values():
                        if image["split"] != split or image["stratum"] != stratum:
                            continue
                        family_number = int(image["family_id"][1:]) - (12 if split == "validation" else 0)
                        contributes = local_start <= family_number <= local_end
                        for polarity in ("positive", "negative"):
                            expected_per_image = int(rule["per_contributing_image"][polarity]) if contributes else 0
                            actual_per_image = per_image[(image["image_id"], atom_type, polarity)]
                            if actual_per_image != expected_per_image:
                                raise ValueError(
                                    f"{image['image_id']}/{atom_type}/{polarity}: expected "
                                    f"{expected_per_image}, found {actual_per_image}"
                                )
    return {"opportunities": len(seen), "sha256": sha256_file(path)}


def audit_ground_truth_freeze(
    record: dict[str, Any],
    manifest_path: Path,
    opportunities_path: Path,
    data_root: Path,
    results_root: Path | None = None,
) -> dict[str, Any]:
    validate("ground_truth_freeze_v3_2.schema.json", record)
    contract = load_active_contract()
    manifest = read_json(manifest_path)
    manifest_audit = audit_manifest(manifest, data_root)
    opportunity_audit = audit_opportunities(opportunities_path, manifest, data_root)
    expected = {
        "config_hashes": dict(contract.config_hashes),
        "manifest_sha256": sha256_file(manifest_path),
        "opportunities_sha256": opportunity_audit["sha256"],
        "scenario_specifications_sha256": manifest_audit["scenario_specifications_sha256"],
    }
    for key, value in expected.items():
        if record[key] != value:
            raise ValueError(f"ground-truth freeze {key} mismatch")
    if results_root is not None and results_root.exists() and any(results_root.rglob("*.json")):
        raise ValueError("ground truth must be frozen before any model-output JSON exists")
    return {"status": record["status"], **expected, "images": manifest_audit["images"], "opportunities": opportunity_audit["opportunities"]}


def build_opportunities(path: Path, manifest_path: Path, data_root: Path) -> dict[str, Any]:
    """Materialize the frozen opportunity layout from final scenario records."""

    if path.exists():
        raise ValueError("support-opportunity output already exists")
    manifest = read_json(manifest_path)
    audit = audit_manifest(manifest, data_root)
    labels = {key: sorted(value) for key, value in _closed_labels().items()}
    plan = load_active_contract().amend_prereg["dataset_support"]["validation_plan_each_stratum"]
    rows: list[dict[str, str]] = []
    for image in sorted(manifest["images"], key=lambda item: item["image_id"]):
        local_family = int(image["family_id"][1:]) - (12 if image["split"] == "validation" else 0)
        scenario = audit["scenarios"][image["image_id"]]
        entities = {row["reference_id"]: row for row in scenario["reference_entities"]}
        atoms = scenario["reference_atoms"]
        for atom_type, rule in plan.items():
            start_text, end_text = rule["families"].split("-")
            if not int(start_text[1:]) <= local_family <= int(end_text[1:]):
                continue
            positives = sorted(
                (row for row in atoms if row["atom_type"] == atom_type),
                key=lambda row: (row["reference_atom_id"], row["value"]),
            )
            required = int(rule["per_contributing_image"]["positive"])
            if len(positives) < required:
                raise ValueError(f"{image['image_id']}/{atom_type}: scenario has {len(positives)} positives, needs {required}")
            for positive in positives[:required]:
                source = positive["source_reference_id"] or ""
                target = positive["target_reference_id"] or ""
                scope_category = positive.get("scope_category") or ""
                common = {
                    "opportunity_id": "", "image_id": image["image_id"], "family_id": image["family_id"],
                    "stratum": image["stratum"], "split": image["split"],
                    "scenario_specification_id": image["scenario_specification_id"], "atom_type": atom_type,
                    "source_reference_id": source,
                    "source_reference_bbox_xyxy": json.dumps(entities[source]["bbox_xyxy"], separators=(",", ":")) if source else "",
                    "target_reference_id": target,
                    "target_reference_bbox_xyxy": json.dumps(entities[target]["bbox_xyxy"], separators=(",", ":")) if target else "",
                    "scope_category": scope_category,
                    "ground_truth_version": GROUND_TRUTH_VERSION,
                }
                positive_row = {**common, "polarity": "positive", "reference_value": str(positive["value"])}
                positive_row["opportunity_id"] = deterministic_opportunity_id(positive_row)
                rows.append(positive_row)
                same_scope = {
                    str(row["value"]) for row in atoms
                    if row["atom_type"] == atom_type
                    and (row["source_reference_id"] or "") == source
                    and (row["target_reference_id"] or "") == target
                    and (row.get("scope_category") or "") == scope_category
                }
                negative_value = next((value for value in labels[atom_type] if value not in same_scope), None)
                if negative_value is None:
                    raise ValueError(f"{image['image_id']}/{atom_type}: no applicable negative label remains")
                negative_row = {**common, "polarity": "negative", "reference_value": negative_value}
                negative_row["opportunity_id"] = deterministic_opportunity_id(negative_row)
                rows.append(negative_row)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OPPORTUNITY_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return audit_opportunities(path, manifest, data_root)


def create_ground_truth_freeze(
    path: Path, manifest_path: Path, opportunities_path: Path, data_root: Path,
    results_root: Path, frozen_by: str,
) -> dict[str, Any]:
    if path.exists():
        raise ValueError("ground-truth freeze output already exists")
    contract = load_active_contract()
    manifest = read_json(manifest_path)
    manifest_audit = audit_manifest(manifest, data_root)
    opportunity_audit = audit_opportunities(opportunities_path, manifest, data_root)
    if results_root.exists() and any(results_root.rglob("*.json")):
        raise ValueError("ground truth cannot be frozen after model-output JSON exists")
    record = {
        "schema_version": "ground-truth-freeze-v3.2.0",
        "status": "frozen_before_model_inference",
        "methodology": "project-authored-scenario-specifications-and-support-opportunities",
        "dataset_version": "p9-v3-capability-data-v3.0.0",
        "ground_truth_version": GROUND_TRUTH_VERSION,
        "config_hashes": dict(contract.config_hashes),
        "manifest_sha256": sha256_file(manifest_path),
        "opportunities_sha256": opportunity_audit["sha256"],
        "scenario_specifications_sha256": manifest_audit["scenario_specifications_sha256"],
        "project_authored": True, "human_participants": False, "human_annotators": False,
        "derived_from_model_predictions": False, "model_outputs_accessed_before_freeze": False,
        "frozen_before_model_inference": True, "frozen_by": frozen_by,
        "frozen_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    atomic_write(path, canonical_bytes(record))
    audit_ground_truth_freeze(record, manifest_path, opportunities_path, data_root, results_root)
    return {"path": str(path), "sha256": sha256_file(path)}


def build_manifest(path: Path, data_root: Path, prompt_plan_path: Path, generation_receipt_path: Path) -> dict[str, Any]:
    if path.exists():
        raise ValueError("capability manifest output already exists")
    prompt_plan = read_json(prompt_plan_path)
    prompt_rows = {row["image_id"]: row for row in prompt_plan.get("images", [])}
    expected_b = {image_id for image_id in expected_image_ids() if "-B-" in image_id}
    if set(prompt_rows) != expected_b:
        raise ValueError("prompt plan must contain every B-stratum image exactly once")
    generator = load_active_contract().base_prereg["dataset"]["strata"]["B_naturalistic_t2i"]["generator"]
    if prompt_plan.get("model_id") != generator["model_id"] or prompt_plan.get("revision") != generator["revision"] or prompt_plan.get("seed_rule") != generator["seed_rule"]:
        raise ValueError("prompt plan does not match the frozen generator/revision/seed rule")
    receipt = read_json(generation_receipt_path)
    receipt_hashes = {row["image_id"]: row["sha256"] for row in receipt.get("image_files", [])}
    if any((
        receipt.get("schema_version") != "sd-turbo-generation-receipt-v3.0.0",
        receipt.get("status") != "complete", receipt.get("images") != 120,
        receipt.get("model_id") != generator["model_id"], receipt.get("revision") != generator["revision"],
        receipt.get("generation_config") != {key: generator[key] for key in ("width", "height", "steps", "guidance_scale")},
        receipt.get("prompt_plan_sha256") != sha256_file(prompt_plan_path), set(receipt_hashes) != expected_b,
    )):
        raise ValueError("naturalistic generation receipt does not match the frozen prompt/model plan")
    rows = []
    for image_id in expected_image_ids():
        family = image_id.split("-")[-2]
        naturalistic = "-B-" in image_id
        image_relative = f"images/{image_id}.png"
        scenario_relative = f"scenarios/{image_id}.json"
        image_path = _resolved_child(data_root, image_relative, "image")
        scenario_path = _resolved_child(data_root, scenario_relative, "scenario")
        if not image_path.is_file() or not scenario_path.is_file():
            raise ValueError(f"missing final image or scenario for {image_id}")
        if naturalistic and receipt_hashes[image_id] != sha256_file(image_path):
            raise ValueError(f"naturalistic generation receipt hash mismatch for {image_id}")
        scenario = read_json(scenario_path)
        audit_scenario_specification(scenario)
        prompt = prompt_rows.get(image_id)
        if naturalistic and (not isinstance(prompt.get("prompt"), str) or not isinstance(prompt.get("seed"), int)):
            raise ValueError(f"invalid prompt provenance for {image_id}")
        rows.append({
            "image_id": image_id, "family_id": family,
            "stratum": "B_naturalistic_t2i" if naturalistic else "A_controlled_geometric",
            "split": "development" if int(family[1:]) <= 12 else "validation",
            "source_type": "frozen_sd_turbo" if naturalistic else "deterministic_controlled_renderer",
            "licence": generator["license"] if naturalistic else "project-authored",
            "generator_or_asset_revision": generator["revision"] if naturalistic else "controlled-renderer-v3.2.0",
            "prompt_hash_if_applicable": hashlib.sha256(prompt["prompt"].encode("utf-8")).hexdigest() if naturalistic else None,
            "seed_if_applicable": prompt["seed"] if naturalistic else None,
            "relative_path": image_relative, "image_sha256": sha256_file(image_path),
            "scenario_specification_id": f"scenario-{image_id}",
            "scenario_specification_path": scenario_relative,
            "scenario_specification_sha256": sha256_file(scenario_path),
        })
    value = {
        "schema_version": "capability-manifest-v3.2.0", "dataset_version": "p9-v3-capability-data-v3.0.0",
        "ground_truth_version": GROUND_TRUTH_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "images": rows,
    }
    atomic_write(path, canonical_bytes(value))
    return audit_manifest(value, data_root)


def materialize_scenarios(plan_path: Path, data_root: Path, stratum_code: str) -> dict[str, Any]:
    """Write one stratum's 120 canonical files from a reviewed authoring plan."""

    plan = read_json(plan_path)
    scenarios = plan.get("scenarios")
    if not isinstance(scenarios, list):
        raise ValueError("scenario authoring plan lacks a scenarios array")
    ids = [row.get("image_id") for row in scenarios if isinstance(row, dict)]
    expected = [image_id for image_id in expected_image_ids() if f"-{stratum_code}-" in image_id]
    if len(scenarios) != 120 or sorted(ids) != sorted(expected):
        raise ValueError(f"scenario authoring plan must contain all 120 {stratum_code}-stratum image IDs exactly once")
    output = data_root / "scenarios"
    output.mkdir(parents=True, exist_ok=True)
    for scenario in sorted(scenarios, key=lambda row: row["image_id"]):
        audit_scenario_specification(scenario)
        if stratum_code == "B" and not (data_root / "images" / f"{scenario['image_id']}.png").is_file():
            raise ValueError(f"naturalistic final reference precedes its generated image: {scenario['image_id']}")
        destination = output / f"{scenario['image_id']}.json"
        if destination.exists():
            raise ValueError(f"scenario output already exists: {destination}")
        atomic_write(destination, canonical_bytes(scenario))
    return {"scenarios": len(scenarios), "plan_sha256": sha256_file(plan_path), "output": str(output)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="P9-v3B project-authored ground-truth preparation")
    sub = parser.add_subparsers(dest="command", required=True)
    manifest_parser = sub.add_parser("audit-manifest")
    manifest_parser.add_argument("path", type=Path)
    manifest_parser.add_argument("--data-root", type=Path)
    opportunity_parser = sub.add_parser("audit-opportunities")
    opportunity_parser.add_argument("path", type=Path)
    opportunity_parser.add_argument("--manifest", type=Path)
    opportunity_parser.add_argument("--data-root", type=Path)
    freeze_parser = sub.add_parser("audit-ground-truth")
    freeze_parser.add_argument("record", type=Path)
    freeze_parser.add_argument("--manifest", type=Path, required=True)
    freeze_parser.add_argument("--opportunities", type=Path, required=True)
    freeze_parser.add_argument("--data-root", type=Path, required=True)
    freeze_parser.add_argument("--results", type=Path, required=True)
    build_parser = sub.add_parser("build-opportunities")
    build_parser.add_argument("path", type=Path)
    build_parser.add_argument("--manifest", type=Path, required=True)
    build_parser.add_argument("--data-root", type=Path, required=True)
    create_parser = sub.add_parser("create-ground-truth-freeze")
    create_parser.add_argument("path", type=Path)
    create_parser.add_argument("--manifest", type=Path, required=True)
    create_parser.add_argument("--opportunities", type=Path, required=True)
    create_parser.add_argument("--data-root", type=Path, required=True)
    create_parser.add_argument("--results", type=Path, required=True)
    create_parser.add_argument("--frozen-by", required=True)
    manifest_build_parser = sub.add_parser("build-manifest")
    manifest_build_parser.add_argument("path", type=Path)
    manifest_build_parser.add_argument("--data-root", type=Path, required=True)
    manifest_build_parser.add_argument("--prompt-plan", type=Path, required=True)
    manifest_build_parser.add_argument("--generation-receipt", type=Path, required=True)
    scenarios_parser = sub.add_parser("materialize-scenarios")
    scenarios_parser.add_argument("--plan", type=Path, required=True)
    scenarios_parser.add_argument("--data-root", type=Path, required=True)
    scenarios_parser.add_argument("--stratum", choices=["A", "B"], required=True)
    args = parser.parse_args(argv)
    if args.command == "audit-manifest":
        result = audit_manifest(read_json(args.path), args.data_root)
    elif args.command == "audit-opportunities":
        manifest_value = read_json(args.manifest) if args.manifest else None
        if (args.manifest is None) != (args.data_root is None):
            raise SystemExit("audit-opportunities requires --manifest and --data-root together")
        result = audit_opportunities(args.path, manifest_value, args.data_root)
    elif args.command == "audit-ground-truth":
        result = audit_ground_truth_freeze(
            read_json(args.record), args.manifest, args.opportunities, args.data_root, args.results
        )
    elif args.command == "build-opportunities":
        result = build_opportunities(args.path, args.manifest, args.data_root)
    elif args.command == "create-ground-truth-freeze":
        result = create_ground_truth_freeze(
            args.path, args.manifest, args.opportunities, args.data_root, args.results, args.frozen_by
        )
    elif args.command == "build-manifest":
        result = build_manifest(args.path, args.data_root, args.prompt_plan, args.generation_receipt)
    else:
        result = materialize_scenarios(args.plan, args.data_root, args.stratum)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
