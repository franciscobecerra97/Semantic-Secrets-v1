"""CPU-only checks for P9-v3B manifests, guards, schemas, and caches."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import jsonschema
import pytest

from experiments.v3.runtime.acquire import plan
from experiments.v3.runtime.dataset import audit_manifest, audit_opportunities, expected_image_ids, randomized_assignment
from experiments.v3.runtime.execution import cache_key
from experiments.v3.runtime.guard import main as guard_main
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
            "prompt_hash_if_applicable": None, "seed_if_applicable": None,
            "relative_path": f"images/{image_id}.png", "image_sha256": "0" * 64,
            "annotation_version": "rubric-v3.1",
        })
    return {"schema_version": "capability-manifest-v3.1.0", "dataset_version": "p9-v3-capability-data-v3.0.0", "created_at_utc": "2026-08-26T00:00:00Z", "images": rows}


def test_manifest_schema_and_frozen_split_counts() -> None:
    result = audit_manifest(manifest())
    assert result["images"] == 240
    assert set(result["split_counts"].values()) == {60}


def test_manifest_identifier_change_fails_closed() -> None:
    value = manifest()
    value["images"][0]["image_id"] = "cap-v3-A-F01-99"
    with pytest.raises(ValueError, match="deterministic"):
        audit_manifest(value)


def test_annotation_example_is_deliberately_unconfirmed() -> None:
    example = json.loads((Path(__file__).parent / "templates" / "annotation_resource_v3_1.example.json").read_text(encoding="utf-8"))
    with pytest.raises(jsonschema.ValidationError):
        validate("annotation_resource_v3_1.schema.json", example)


def test_confirmed_annotation_record_schema() -> None:
    value = {
        "schema_version": "annotation-resource-v3.1.0", "status": "confirmed",
        "annotator_roles": ["project_researcher", "qualified_independent_external_human"],
        "availability_confirmation": "Both named resources confirmed the scheduled independent sessions.",
        "rubric_version": "visibility-rubric-v3.1", "independence_statement": "Both annotators work independently and remain model-output blind.",
        "randomized_image_id_procedure": "Use the committed blind identifier map derived with split seed 925031.",
        "conflict_provenance_statement": "Retain both raw records and link every conflict to its source rows.",
        "adjudication_procedure": "Resolve conflicts by documented consensus against the frozen visibility rubric.",
        "confirmed_by": "project-owner", "confirmed_at_utc": "2026-08-26T00:00:00Z",
    }
    validate("annotation_resource_v3_1.schema.json", value)


def test_randomization_is_seeded_and_complete() -> None:
    first = randomized_assignment(manifest(), 925031)
    second = randomized_assignment(manifest(), 925031)
    assert first == second
    assert len(first) == 240
    assert len({row["blind_id"] for row in first}) == 240


def test_opportunity_counts_match_frozen_plan(tmp_path: Path) -> None:
    path = tmp_path / "opportunities.csv"
    fields = ["opportunity_id", "image_id", "family_id", "stratum", "split", "atom_type", "polarity", "reference_value", "source_detection_id", "target_detection_id", "rubric_version"]
    config = load_active_contract().amend_prereg["dataset_support"]["validation_plan_each_stratum"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        index = 0
        for stratum in ("A_controlled_geometric", "B_naturalistic_t2i"):
            for atom_type, rule in config.items():
                for polarity in ("positive", "negative"):
                    for _ in range(rule[polarity]):
                        index += 1
                        writer.writerow({"opportunity_id": f"opp-{index:05d}", "image_id": "fixture", "family_id": "F13", "stratum": stratum, "split": "validation", "atom_type": atom_type, "polarity": polarity, "reference_value": "x", "source_detection_id": "", "target_detection_id": "", "rubric_version": "v3.1"})
    assert audit_opportunities(path)["opportunities"] == index


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
