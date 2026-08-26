"""Pre-execution engineering tests for the frozen v3 semantic compiler.

These 320 deterministic cases mirror the category counts frozen in v3.1. They
must be rerun in the locked execution environment; passing here is preparation
evidence and does not satisfy Gate V3-A1.
"""

from __future__ import annotations

import copy
import hashlib
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import jsonschema
import pytest

from prototype.semantic_secrets.v3 import SemanticCompilerV3, load_active_contract


ROOT = Path(__file__).resolve().parents[2]
RESULT_SCHEMA = json.loads(
    (ROOT / "prototype" / "semantic_secrets" / "v3" / "semantic_compiler_result_v3.schema.json").read_text(
        encoding="utf-8"
    )
)
GOLDEN_SHA256 = json.loads(
    (ROOT / "experiments" / "v3" / "fixtures" / "semantic_compiler_v3_golden_sha256.json").read_text(encoding="utf-8")
)
CONTRACT = load_active_contract()
COMPILER = SemanticCompilerV3(CONTRACT)


@dataclass(frozen=True)
class Case:
    category: str
    name: str
    value: Any
    status: str = "graph"
    failure: str | None = None
    eligible_types: tuple[str, ...] | None = None

    @property
    def test_id(self) -> str:
        return f"{self.category}-{self.name}"


def confidence(value: float = 0.9, *, name: str = "score", threshold: float = 0.5) -> dict[str, Any]:
    return {
        "value": value,
        "score_name": name,
        "score_range": [0.0, 1.0],
        "threshold": threshold,
        "threshold_source": "development",
    }


def observation(pipeline_index: int = 0) -> dict[str, Any]:
    pipeline_id = CONTRACT.pipeline_ids[pipeline_index]
    components = CONTRACT.component_map(pipeline_id)
    detection_component = next(iter(components))
    return {
        "observation_version": CONTRACT.observation_version,
        "pipeline_id": pipeline_id,
        "pipeline_revision": CONTRACT.expected_pipeline_revision(pipeline_id),
        "image_id": f"fixture-{pipeline_index}",
        "image_sha256": "0" * 64,
        "detections": [
            {
                "local_id": "d1",
                "category": "person",
                "bbox": [0.10, 0.10, 0.20, 0.30],
                "confidence": confidence(),
                "component_id": detection_component,
                "component_revision": components[detection_component]["revision"],
            }
        ],
        "attributes": [],
        "unary_actions": [],
        "binary_interactions": [],
        "scenes": [],
        "component_events": [
            {
                "component_id": component_id,
                "component_revision": component["revision"],
                "status": "ok",
                "failure_code": None,
                "elapsed_seconds": 0,
                "peak_rss_bytes": 0,
                "peak_gpu_bytes": 0,
            }
            for component_id, component in components.items()
        ],
    }


def changed(base: dict[str, Any], mutate: Callable[[dict[str, Any]], None]) -> dict[str, Any]:
    result = copy.deepcopy(base)
    mutate(result)
    return result


def add_detection(row: dict[str, Any], local_id: str, category: str, bbox: list[float], value: float = 0.9) -> None:
    item = copy.deepcopy(row["detections"][0])
    item.update(local_id=local_id, category=category, bbox=bbox, confidence=confidence(value))
    row["detections"].append(item)


def add_binary(row: dict[str, Any], relation: str, source: str = "d1", target: str = "d2") -> None:
    component_id = row["detections"][0]["component_id"]
    component_revision = row["detections"][0]["component_revision"]
    row["binary_interactions"].append(
        {
            "source_detection_id": source,
            "interaction": relation,
            "target_detection_id": target,
            "confidence": confidence(),
            "component_id": component_id,
            "component_revision": component_revision,
        }
    )


def make_cases() -> list[Case]:
    cases: list[Case] = []

    # 40 schema/version cases.
    for index in range(20):
        row = observation(index % 2)
        row["image_id"] = f"schema-valid-{index:02d}"
        cases.append(Case("schema_version", f"valid-{index:02d}", row))
    for index in range(10):
        row = observation()
        row["observation_version"] = f"visual-observation-v{index}.invalid"
        cases.append(Case("schema_version", f"unsupported-{index:02d}", row, "typed_failure", "UNSUPPORTED_OBSERVATION_VERSION"))
    required = CONTRACT.base_observation["observation_record"]["required_fields"]
    for index, field in enumerate(required[:10]):
        row = observation()
        del row[field]
        cases.append(Case("schema_version", f"missing-{index:02d}-{field}", row, "typed_failure", "MALFORMED_OBSERVATION"))

    # 48 detection/box cases: every closed entity label plus invalid boxes.
    for index, label in enumerate(CONTRACT.base_observation["entity_categories"]):
        row = observation(index % 2)
        row["detections"][0]["category"] = label
        row["detections"][0]["bbox"] = [0.01, 0.01, 0.20 + (index % 4) * 0.01, 0.25]
        cases.append(Case("detection_box", f"label-{index:02d}-{label}", row))
    bad_boxes: list[Any] = [
        None, [], [0, 0, 1], [0, 0, 1, 1, 2], [-0.1, 0, 1, 1], [0, -0.1, 1, 1],
        [0, 0, 1.1, 1], [0, 0, 1, 1.1], [0.5, 0, 0.5, 1], [0.6, 0, 0.5, 1],
        [0, 0.5, 1, 0.5], [0, 0.6, 1, 0.5], [True, 0, 1, 1], [0, 0, "1", 1],
        [0, 0, float("inf"), 1], [0, 0, float("nan"), 1],
    ]
    for index, bbox in enumerate(bad_boxes):
        row = observation()
        row["detections"][0]["bbox"] = bbox
        expected = "MALFORMED_OBSERVATION" if index >= 12 else "INVALID_BOUNDING_BOX"
        cases.append(Case("detection_box", f"invalid-{index:02d}", row, "typed_failure", expected))

    # 48 duplicate/ID cases.
    for index in range(16):
        row = observation()
        row["detections"][0]["confidence"] = confidence(0.70 + index / 1000)
        add_detection(row, "d2", "person", [0.101, 0.101, 0.199, 0.299], 0.90)
        cases.append(Case("duplicate_ids", f"resolved-{index:02d}", row))
    for index in range(16):
        row = observation()
        add_detection(row, "d1", "cat", [0.5, 0.5, 0.7, 0.7])
        cases.append(Case("duplicate_ids", f"duplicate-local-{index:02d}", row, "typed_failure", "DUPLICATE_LOCAL_ID"))
    for index in range(8):
        row = observation()
        for number in range(2, 10):
            x = (number - 1) * 0.09
            add_detection(row, f"d{number}", "person", [x, 0.4, x + 0.05, 0.5])
        cases.append(Case("duplicate_ids", f"too-many-{index:02d}", row, "typed_failure", "TOO_MANY_CREDENTIAL_ENTITIES"))
    for index in range(8):
        row = observation()
        add_detection(row, "d2", "person", [0.101, 0.101, 0.199, 0.299])
        row["detections"][1]["confidence"] = confidence(name=f"other-domain-{index}")
        cases.append(Case("duplicate_ids", f"ambiguous-{index:02d}", row, "typed_failure", "AMBIGUOUS_IDENTITY"))

    # 48 inverse/geometry cases.
    geometry_boxes = [
        ([0.10, 0.10, 0.20, 0.20], [0.50, 0.50, 0.70, 0.70]),
        ([0.10, 0.10, 0.40, 0.40], [0.20, 0.20, 0.50, 0.50]),
        ([0.20, 0.20, 0.30, 0.30], [0.10, 0.10, 0.50, 0.50]),
        ([0.20, 0.10, 0.50, 0.20], [0.25, 0.22, 0.55, 0.40]),
        ([0.20, 0.30, 0.50, 0.40], [0.25, 0.10, 0.55, 0.28]),
        ([0.10, 0.10, 0.20, 0.20], [0.22, 0.10, 0.32, 0.20]),
    ]
    for index in range(24):
        row = observation()
        first, second = geometry_boxes[index % len(geometry_boxes)]
        row["detections"][0]["bbox"] = first
        add_detection(row, "d2", "cat", second)
        cases.append(Case("inverse_geometry", f"derived-{index:02d}", row))
    inverse_labels = ("right_of", "below", "contains")
    for index in range(24):
        row = observation()
        add_detection(row, "d2", "cat", [0.60, 0.60, 0.75, 0.75])
        add_binary(row, inverse_labels[index % 3])
        cases.append(Case("inverse_geometry", f"inverse-{index:02d}", row))

    # 48 count/sorting/limit cases.
    for index in range(24):
        row = observation(index % 2)
        count = 1 + index % 8
        for number in range(2, count + 1):
            x = number * 0.10
            add_detection(row, f"d{number}", "cat" if number % 2 else "dog", [x, 0.60, x + 0.04, 0.68])
        cases.append(Case("count_sort_limit", f"count-{index:02d}", row))
    for index in range(24):
        row = observation()
        for number, category in enumerate(("dog", "cat", "book"), start=2):
            add_detection(row, f"d{number}", category, [number * 0.15, 0.55, number * 0.15 + 0.06, 0.65])
        random.Random(index).shuffle(row["detections"])
        cases.append(Case("count_sort_limit", f"ordering-{index:02d}", row))

    # 40 malformed/unsupported cases.
    for index in range(8):
        cases.append(Case("malformed_unsupported", f"bytes-{index:02d}", b"not-json" + bytes([index]), "typed_failure", "MALFORMED_OBSERVATION"))
    for index in range(8):
        row = observation()
        row["detections"][0]["category"] = f"unknown_{index}"
        cases.append(Case("malformed_unsupported", f"label-{index:02d}", row, "typed_failure", "UNKNOWN_LABEL"))
    for index in range(8):
        row = observation()
        row["component_events"][0]["component_revision"] = f"wrong-{index}"
        cases.append(Case("malformed_unsupported", f"component-{index:02d}", row, "typed_failure", "UNDECLARED_COMPONENT"))
    for index in range(8):
        row = observation()
        row["detections"][0]["confidence"].pop("score_name")
        cases.append(Case("malformed_unsupported", f"score-{index:02d}", row, "typed_failure", "UNDECLARED_SCORE_DOMAIN"))
    for index in range(8):
        row = observation()
        cases.append(Case("malformed_unsupported", f"eligible-{index:02d}", row, "typed_failure", "UNSUPPORTED_CREDENTIAL_TYPE", (f"bad_{index}",)))

    # 24 serialization/repeat cases.
    for index in range(24):
        row = observation(index % 2)
        row["image_id"] = f"repeat-{'é' if index % 2 else 'ascii'}-{index:02d}"
        row["detections"][0]["confidence"]["value"] = 0.9000001 + index / 10_000_000
        cases.append(Case("serialization_repeat", f"canonical-{index:02d}", row))

    # 24 deterministic seeded property cases.
    for seed in range(24):
        row = observation(seed % 2)
        rng = random.Random(seed)
        labels = rng.sample(["cat", "dog", "book", "cup", "chair"], 4)
        for number, label in enumerate(labels, start=2):
            x = 0.10 * number
            add_detection(row, f"d{number}", label, [x, 0.70, x + 0.05, 0.80], 0.6 + rng.random() * 0.3)
        rng.shuffle(row["detections"])
        cases.append(Case("seeded_property", f"seed-{seed:02d}", row))

    expected = {
        "schema_version": 40,
        "detection_box": 48,
        "duplicate_ids": 48,
        "inverse_geometry": 48,
        "count_sort_limit": 48,
        "malformed_unsupported": 40,
        "serialization_repeat": 24,
        "seeded_property": 24,
    }
    actual = {name: sum(case.category == name for case in cases) for name in expected}
    assert actual == expected
    assert len(cases) == 320
    return cases


CASES = make_cases()
assert set(GOLDEN_SHA256) == {case.test_id for case in CASES}


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.test_id)
def test_frozen_compiler_case(case: Case) -> None:
    first = COMPILER.compile(case.value, eligible_types=case.eligible_types)
    second = COMPILER.compile(case.value, eligible_types=case.eligible_types)
    assert first == second
    assert hashlib.sha256(first).hexdigest() == GOLDEN_SHA256[case.test_id]
    assert first.endswith(b"\n")
    result = json.loads(first.decode("utf-8"))
    jsonschema.validate(result, RESULT_SCHEMA)
    assert result["status"] == case.status
    if case.failure is not None:
        assert result["failure"]["code"] == case.failure
