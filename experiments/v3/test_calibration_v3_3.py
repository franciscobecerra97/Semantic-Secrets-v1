"""CPU-only deterministic tests for prospective P9-v3B calibration."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from experiments.v3.runtime.calibration import (
    _add_egtr_relations, _add_entities, _add_siglip_task, _base_observation,
    _compile, _winner, assert_validation_isolation, validate_score_payload,
)
from experiments.v3.runtime.schemas import validate
from experiments.v3.runtime.thresholds import (
    CALIBRATION_VERSION, CANDIDATE_GRID, grid_values, ranking_key,
    select_candidate, validate_settings,
)
from prototype.semantic_secrets.v3 import load_active_contract


def metrics(*, precision: float, recall: float, f1: float, coverage: float) -> dict:
    row = {"precision": precision, "recall": recall, "f1": f1, "coverage": coverage}
    return {"A_controlled_geometric": dict(row), "B_naturalistic_t2i": dict(row)}


def candidate(threshold: float, secondary: float, values: dict) -> dict:
    return {
        "threshold": threshold,
        "secondary_threshold_or_margin": secondary,
        "metrics_by_stratum": values,
    }


def test_v33_grid_is_exact_and_closed() -> None:
    assert len(CANDIDATE_GRID) == 101
    assert grid_values()[0] == 0.0
    assert grid_values()[-1] == 1.0
    assert grid_values()[37] == 0.37
    assert all(CANDIDATE_GRID[index + 1] - CANDIDATE_GRID[index] == CANDIDATE_GRID[1] for index in range(100))


def test_candidate_selection_is_order_independent_and_uses_conservative_tie() -> None:
    equal = metrics(precision=0.95, recall=0.8, f1=0.86, coverage=0.9)
    rows = [candidate(0.4, 0.1, equal), candidate(0.5, 0.0, equal), candidate(0.5, 0.2, equal)]
    first = select_candidate(rows)
    second = select_candidate(list(reversed(rows)))
    assert first == second
    assert first["threshold"] == 0.5
    assert first["secondary_threshold_or_margin"] == 0.2
    assert first["preferred_development_criterion_met"] is True


def test_fallback_is_deterministic_when_preferred_criterion_is_unmet() -> None:
    weak = metrics(precision=0.7, recall=0.8, f1=0.74, coverage=0.9)
    better = metrics(precision=0.8, recall=0.8, f1=0.8, coverage=0.9)
    selected = select_candidate([candidate(0.9, 0.0, weak), candidate(0.3, 0.0, better)])
    assert selected["threshold"] == 0.3
    assert selected["preferred_development_criterion_met"] is False


def test_worst_stratum_precedes_mean_and_pooling_cannot_rescue_candidate() -> None:
    unbalanced = {
        "A_controlled_geometric": {"precision": 1.0, "recall": 1.0, "f1": 1.0, "coverage": 1.0},
        "B_naturalistic_t2i": {"precision": 0.8, "recall": 0.5, "f1": 0.6, "coverage": 0.7},
    }
    balanced = metrics(precision=0.88, recall=0.75, f1=0.78, coverage=0.8)
    selected = select_candidate([candidate(0.9, 0.0, unbalanced), candidate(0.2, 0.0, balanced)])
    assert selected["threshold"] == 0.2


def test_siglip_complete_vector_tie_and_margin_replay() -> None:
    row = {"labels": ["red", "blue"], "scores": [0.8, 0.8]}
    assert _winner(row, 0.8, 0.0) == ("blue", 0.8)
    assert _winner(row, 0.8, 0.01) is None


def test_validation_outputs_and_nondevelopment_artifacts_fail_closed(tmp_path: Path) -> None:
    validation = tmp_path / "validation"
    validation.mkdir()
    (validation / "record.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="validation"):
        assert_validation_isolation(tmp_path)
    with pytest.raises(ValueError, match="development-only"):
        assert_validation_isolation(tmp_path / "empty", [{"split": "validation"}])


def test_smoke_settings_are_fixed_and_cannot_validate_as_development() -> None:
    root = Path(__file__).parent
    value = json.loads((root / "config" / "engineering_smoke_settings_v3_3.json").read_text(encoding="utf-8"))
    validate("engineering_smoke_settings_v3_3.schema.json", value)
    for pipeline, settings in value["pipelines"].items():
        validate_settings(pipeline, settings, exact_tasks=True, threshold_source="engineering_smoke")
        assert all(row["threshold"] == 0.5 for row in settings.values())
        assert all(row.get("minimum_top_two_margin", 0.0) == 0.0 for row in settings.values())
        with pytest.raises(ValueError, match="score-domain"):
            validate_settings(pipeline, settings, exact_tasks=True)


def test_v33_amendment_is_active_and_preserves_frozen_gate() -> None:
    contract = load_active_contract()
    amendment = contract.calibration_prereg
    assert amendment["versions"]["calibration"] == CALIBRATION_VERSION
    assert amendment["staging"]["count_and_geometry"].startswith("compiler-derived")
    assert amendment["inherited_unchanged"].count("Gate V3-A1 metrics, criteria, uncertainty, and resource limits") == 1
    assert "preregistration_v3_3.json" in contract.config_hashes
    assert "engineering_smoke_settings_v3_3.json" in contract.config_hashes


def test_development_score_schema_rejects_validation_split() -> None:
    value = {
        "schema_version": "development-score-artifact-v3.3.0",
        "artifact_kind": "entity", "split": "validation",
        "pipeline_id": "v3.1-gdino-siglip2", "image_id": "i", "image_sha256": "0" * 64,
        "provenance": {
            "git_commit": "0" * 40,
            "config_hashes": {f"c{i}": "0" * 64 for i in range(7)},
            "ground_truth_freeze_sha256": "0" * 64, "manifest_sha256": "0" * 64,
            "opportunities_sha256": "0" * 64, "model_manifest_sha256": "0" * 64,
            "adapter_source_sha256": "0" * 64,
        },
        "payload": {},
    }
    with pytest.raises(jsonschema.ValidationError):
        validate("development_score_artifact_v3_3.schema.json", value)


def test_incomplete_entity_grid_fails_closed_before_fitting() -> None:
    value = {
        "artifact_kind": "entity", "pipeline_id": "v3.1-gdino-siglip2",
        "payload": {
            "score_capture_version": "development-score-capture-v3.3.0",
            "component_provenance": {}, "entity_candidates": {"0.50": []},
            "raw_postprocess_inputs": {"logits": [], "pred_boxes": [], "input_ids": []},
        },
    }
    with pytest.raises(ValueError, match="complete frozen grid"):
        validate_score_payload(value)


def test_ranking_key_requires_exactly_both_strata() -> None:
    with pytest.raises(ValueError, match="both"):
        ranking_key({"A_controlled_geometric": metrics(precision=1, recall=1, f1=1, coverage=1)["A_controlled_geometric"]}, 0.5)


def component_event(pipeline: str, component_id: str) -> dict:
    revision = load_active_contract().component_map(pipeline)[component_id]["revision"]
    return {
        "component_id": component_id, "component_revision": revision, "status": "ok",
        "failure_code": None, "elapsed_seconds": 0.1, "peak_rss_bytes": 1,
        "peak_gpu_bytes": 1,
    }


def test_offline_siglip_replay_compiles_without_model_access() -> None:
    pipeline = "v3.1-gdino-siglip2"
    labels = list(load_active_contract().base_observation["attributes"]["colour"])
    scores = [0.1] * len(labels)
    scores[labels.index("red")] = 0.9
    entity = {
        "image_id": "development-image", "image_sha256": "0" * 64,
        "payload": {
            "entity_candidates": {"0.50": [{"local_id": "d1", "category": "person", "bbox": [0.1, 0.1, 0.4, 0.8], "score": 0.9}]},
            "component_events": [component_event(pipeline, "grounding-dino-tiny")],
            "execution_telemetry": [],
        },
    }
    downstream = {
        "payload": {
            "siglip_tasks": {"colour": [{"labels": labels, "scores": scores, "scope": {"detection_id": "d1"}}]},
            "component_events": [component_event(pipeline, "siglip2-base-384")],
            "execution_telemetry": [],
        }
    }
    observation = _base_observation(pipeline, entity, downstream)
    _add_entities(observation, pipeline, entity, 0.5)
    _add_siglip_task(observation, pipeline, downstream, "colour", 0.5, 0.1)
    result = _compile(observation)
    assert result["status"] == "graph"
    assert result["graph"]["attributes"] == [{"node": "n001", "type": "colour", "value": "red"}]


def test_offline_egtr_joint_relation_replay_requires_both_scores() -> None:
    pipeline = "v3.1-egtr-siglip2"
    rows = [
        {"local_id": "egtr-q001", "category": "person", "bbox": [0.1, 0.1, 0.4, 0.8], "score": 0.9},
        {"local_id": "egtr-q002", "category": "horse", "bbox": [0.5, 0.1, 0.9, 0.8], "score": 0.9},
    ]
    artifact = {
        "image_id": "development-image", "image_sha256": "0" * 64,
        "payload": {
            "entity_candidates": {"0.50": rows},
            "relations": [{
                "source_detection_id": "egtr-q001", "target_detection_id": "egtr-q002",
                "interaction": "riding", "predicate_score": 0.8, "connectivity_score": 0.4,
            }],
            "component_events": [component_event(pipeline, "egtr-vg")], "execution_telemetry": [],
        },
    }
    observation = _base_observation(pipeline, artifact)
    _add_entities(observation, pipeline, artifact, 0.5)
    _add_egtr_relations(observation, artifact, 0.7, 0.5)
    assert all(row["relation"] != "riding" for row in _compile(observation)["graph"]["binary"])
    observation = _base_observation(pipeline, artifact)
    _add_entities(observation, pipeline, artifact, 0.5)
    _add_egtr_relations(observation, artifact, 0.7, 0.4)
    result = _compile(observation)
    assert any(row["relation"] == "riding" for row in result["graph"]["binary"])
