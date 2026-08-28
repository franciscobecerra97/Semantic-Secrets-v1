"""CPU-only checks for P9-v3B manifests, guards, schemas, and caches."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import jsonschema
import pytest

from experiments.v3.runtime.acquire import plan
from experiments.v3.runtime.dataset import (
    GROUND_TRUTH_VERSION,
    OPPORTUNITY_FIELDS,
    audit_manifest,
    audit_opportunities,
    audit_scenario_specification,
    deterministic_opportunity_id,
    expected_image_ids,
)
from experiments.v3.runtime.execution import cache_key
from experiments.v3.runtime.guard import FormalPaths, main as guard_main, parser as guard_parser
from experiments.v3.runtime.io import canonical_bytes, sha256_tree
from experiments.v3.runtime.results import observation_projection
from experiments.v3.runtime.schemas import SCHEMA_DIR, validate
from experiments.v3.runtime.telemetry import environment_record
from experiments.v3.runtime.thresholds import SCORE_CONTRACT, validate_settings
from prototype.semantic_secrets.v3 import load_active_contract


def manifest() -> dict:
    rows = []
    for image_id in expected_image_ids():
        stratum = "A_controlled_geometric" if "-A-" in image_id else "B_naturalistic_t2i"
        family = image_id.split("-")[-2]
        split = "development" if int(family[1:]) <= 12 else "validation"
        rows.append({
            "image_id": image_id, "family_id": family, "stratum": stratum, "split": split,
            "source_type": "deterministic_fixture" if stratum.startswith("A_") else "frozen_t2i",
            "licence": "project-authored", "generator_or_asset_revision": "fixture-v3",
            "prompt_hash_if_applicable": "1" * 64 if stratum.startswith("B_") else None,
            "seed_if_applicable": 1 if stratum.startswith("B_") else None,
            "relative_path": f"images/{image_id}.png", "image_sha256": "0" * 64,
            "scenario_specification_id": f"scenario-{image_id}",
            "scenario_specification_path": f"scenarios/{image_id}.json",
            "scenario_specification_sha256": "2" * 64,
        })
    return {
        "schema_version": "capability-manifest-v3.2.0",
        "dataset_version": "p9-v3-capability-data-v3.0.0",
        "ground_truth_version": GROUND_TRUTH_VERSION,
        "created_at_utc": "2026-08-28T00:00:00Z",
        "images": rows,
    }


def test_manifest_schema_and_frozen_split_counts() -> None:
    result = audit_manifest(manifest())
    assert result["images"] == 240
    assert set(result["split_counts"].values()) == {60}


def test_manifest_identifier_change_fails_closed() -> None:
    value = manifest()
    value["images"][0]["image_id"] = "cap-v3-A-F01-02"
    with pytest.raises(ValueError, match="deterministic"):
        audit_manifest(value)


def test_manifest_scenario_provenance_fails_closed(tmp_path: Path) -> None:
    value = manifest()
    first = value["images"][0]
    image_path = tmp_path / first["relative_path"]
    image_path.parent.mkdir(parents=True)
    image_path.write_bytes(b"fixture-image")
    first["image_sha256"] = hashlib.sha256(b"fixture-image").hexdigest()
    scenario_path = tmp_path / first["scenario_specification_path"]
    scenario_path.parent.mkdir(parents=True)
    scenario_path.write_text("{}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="scenario"):
        audit_manifest(value, tmp_path)


def test_ground_truth_example_is_deliberately_incomplete() -> None:
    example = json.loads((Path(__file__).parent / "templates" / "ground_truth_freeze_v3_2.example.json").read_text(encoding="utf-8"))
    with pytest.raises(jsonschema.ValidationError):
        validate("ground_truth_freeze_v3_2.schema.json", example)


def test_frozen_ground_truth_record_schema_forbids_humans_and_model_outputs() -> None:
    value = {
        "schema_version": "ground-truth-freeze-v3.2.0",
        "status": "frozen_before_model_inference",
        "methodology": "project-authored-scenario-specifications-and-support-opportunities",
        "dataset_version": "p9-v3-capability-data-v3.0.0",
        "ground_truth_version": GROUND_TRUTH_VERSION,
        "config_hashes": {f"c{index}": "0" * 64 for index in range(5)},
        "manifest_sha256": "1" * 64,
        "opportunities_sha256": "2" * 64,
        "scenario_specifications_sha256": "3" * 64,
        "project_authored": True,
        "human_participants": False,
        "human_annotators": False,
        "derived_from_model_predictions": False,
        "model_outputs_accessed_before_freeze": False,
        "frozen_before_model_inference": True,
        "frozen_by": "project-owner",
        "frozen_at_utc": "2026-08-28T00:00:00Z",
    }
    validate("ground_truth_freeze_v3_2.schema.json", value)
    value["human_annotators"] = True
    with pytest.raises(jsonschema.ValidationError):
        validate("ground_truth_freeze_v3_2.schema.json", value)


def test_scenario_schema_checks_reference_scope_and_boxes() -> None:
    value = {
        "schema_version": "capability-scenario-specification-v3.2.0",
        "scenario_specification_id": "scenario-cap-v3-A-F01-01",
        "image_id": "cap-v3-A-F01-01", "family_id": "F01",
        "stratum": "A_controlled_geometric", "split": "development",
        "authoring_method": "controlled_scene_specification", "model_output_blind": True,
        "reference_entities": [{"reference_id": "r1", "category": "person", "bbox_xyxy": [0.1, 0.1, 0.4, 0.8]}],
        "reference_atoms": [{"reference_atom_id": "a1", "atom_type": "entity", "value": "person", "source_reference_id": "r1", "target_reference_id": None}],
    }
    audit_scenario_specification(value)
    value["reference_entities"][0]["bbox_xyxy"] = [0.4, 0.1, 0.1, 0.8]
    with pytest.raises(ValueError, match="normalized"):
        audit_scenario_specification(value)


def test_opportunity_counts_match_frozen_plan(tmp_path: Path) -> None:
    path = tmp_path / "opportunities.csv"
    fields = list(OPPORTUNITY_FIELDS)
    config = load_active_contract().amend_prereg["dataset_support"]["validation_plan_each_stratum"]
    manifest_value = manifest()
    labels = {
        "entity": ["person", "cat"], "colour": ["red", "blue"],
        "size": ["small", "large"], "material": ["wood", "metal"],
        "pattern": ["solid", "striped"], "count": ["1", "2"],
        "unary_action": ["standing", "sitting"],
        "binary_interaction": ["holding", "riding"],
        "geometry_relation": ["left_of", "above"], "scene": ["indoor", "outdoor"],
    }
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        index = 0
        for split in ("development", "validation"):
            for stratum in ("A_controlled_geometric", "B_naturalistic_t2i"):
                images = [row for row in manifest_value["images"] if row["stratum"] == stratum and row["split"] == split]
                for atom_type, rule in config.items():
                    start_text, end_text = rule["families"].split("-")
                    start, end = int(start_text[1:]), int(end_text[1:])
                    eligible_images = [
                        image for image in images
                        if start <= int(image["family_id"][1:]) - (12 if split == "validation" else 0) <= end
                    ]
                    for polarity in ("positive", "negative"):
                        for item_index in range(rule[polarity]):
                            index += 1
                            image = eligible_images[item_index % len(eligible_images)]
                            source = "r1" if atom_type not in {"count", "scene"} else ""
                            target = "r2" if atom_type in {"binary_interaction", "geometry_relation"} else ""
                            row = {
                                "opportunity_id": "", "image_id": image["image_id"], "family_id": image["family_id"],
                                "stratum": stratum, "split": split,
                                "scenario_specification_id": image["scenario_specification_id"],
                                "atom_type": atom_type, "polarity": polarity,
                                "reference_value": labels[atom_type][(item_index // len(images)) % len(labels[atom_type])],
                                "source_reference_id": source,
                                "source_reference_bbox_xyxy": "[0.1,0.1,0.4,0.8]" if source else "",
                                "target_reference_id": target,
                                "target_reference_bbox_xyxy": "[0.5,0.1,0.8,0.8]" if target else "",
                                "ground_truth_version": GROUND_TRUTH_VERSION,
                            }
                            row["opportunity_id"] = deterministic_opportunity_id(row)
                            writer.writerow(row)
    assert audit_opportunities(path, manifest_value)["opportunities"] == index


def test_pipeline_plan_is_exact_and_deduplicates_siglip() -> None:
    rows = plan()
    assert {row["component_id"] for row in rows} == {"grounding-dino-tiny", "siglip2-base-384", "egtr-vg"}
    assert [row["component_id"] for row in rows].count("siglip2-base-384") == 1


def test_cache_key_is_canonical_and_mode_sensitive() -> None:
    first = {"mode": "validation", "pipeline": "v3.1-gdino-siglip2", "image": "0" * 64}
    assert cache_key(first) == cache_key(dict(reversed(list(first.items()))))
    assert cache_key(first) != cache_key({**first, "mode": "validation-repeat"})
    assert cache_key({**first, "image_path": "/host/a", "timeout_seconds": 10}) == cache_key({**first, "image_path": "/host/b", "timeout_seconds": 999})


def test_adapter_bundle_hash_is_repeatable() -> None:
    path = Path(__file__).parent / "runtime" / "adapters"
    assert len(sha256_tree(path)) == 64
    assert sha256_tree(path) == sha256_tree(path)


def test_environment_record_reports_python_runtime() -> None:
    record = environment_record()
    assert record["python"] == sys.version
    assert isinstance(record["platform"], str)
    assert "cuda_available" in record


def test_formal_guard_requires_explicit_flag() -> None:
    with pytest.raises(SystemExit, match="--formal"):
        guard_main([])


def test_formal_guard_exposes_only_ground_truth_freeze_dependency() -> None:
    assert "ground_truth" in FormalPaths.__dataclass_fields__
    assert "annotation" not in FormalPaths.__dataclass_fields__
    help_text = guard_parser().format_help()
    assert "--ground-truth" in help_text
    assert "--annotation" not in help_text
    schema = json.loads((SCHEMA_DIR / "formal_authorization_v3_2.schema.json").read_text(encoding="utf-8"))
    assert "expected_ground_truth_freeze_sha256" in schema["required"]
    assert "expected_annotation_record_sha256" not in schema["required"]


def test_threshold_freeze_requires_both_pipelines() -> None:
    value = {"schema_version": "threshold-freeze-v3.1.0", "status": "frozen_before_validation", "development_manifest_sha256": "0" * 64, "frozen_at_utc": "2026-08-26T00:00:00Z", "pipelines": {}}
    with pytest.raises(jsonschema.ValidationError):
        validate("threshold_freeze_v3_1.schema.json", value)


def test_all_preparation_schemas_are_valid_json() -> None:
    for path in SCHEMA_DIR.glob("*.schema.json"):
        jsonschema.Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))


def test_canonical_records_are_newline_terminated() -> None:
    assert canonical_bytes({"b": 2, "a": 1}) == b'{"a":1,"b":2}\n'


def test_repeat_projection_excludes_volatile_telemetry() -> None:
    base = {key: [] for key in ("detections", "attributes", "unary_actions", "binary_interactions", "scenes")}
    base.update(observation_version="visual-observation-v3.1.0", pipeline_id="v3.1-gdino-siglip2", pipeline_revision="r", image_id="i", image_sha256="0" * 64)
    first = {**base, "component_events": [{"component_id": "c", "component_revision": "r", "status": "ok", "failure_code": None, "elapsed_seconds": 1, "peak_rss_bytes": 2, "peak_gpu_bytes": 3}], "execution_telemetry": [{"framework_peak_gpu_reserved_bytes": 4}]}
    second = json.loads(json.dumps(first))
    second["component_events"][0]["elapsed_seconds"] = 999
    second["execution_telemetry"][0]["framework_peak_gpu_reserved_bytes"] = 999
    assert observation_projection(first) == observation_projection(second)


@pytest.mark.parametrize("pipeline_id", sorted(SCORE_CONTRACT))
def test_component_score_domains_are_exact(pipeline_id: str) -> None:
    values = {}
    for task, (score_name, margin_required) in SCORE_CONTRACT[pipeline_id].items():
        values[task] = {"score_name": score_name, "score_range": [0.0, 1.0], "threshold": 0.5, "threshold_source": "development"}
        if margin_required:
            values[task]["minimum_top_two_margin"] = 0.1
    validate_settings(pipeline_id, values, exact_tasks=True)
    values[next(iter(values))]["score_name"] = "changed-domain"
    with pytest.raises(ValueError, match="score-domain"):
        validate_settings(pipeline_id, values, exact_tasks=True)
