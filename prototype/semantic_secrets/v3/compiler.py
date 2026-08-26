"""Deterministic semantic compiler frozen by v3.0 and v3.1.

The compiler is total over bytes: every input produces canonical UTF-8 JSON
containing either a graph or a typed failure. Learned components never call or
replace graph construction logic.
"""

from __future__ import annotations

import json
import math
import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, MutableMapping, Sequence

from .contract import (
    ActiveV31Contract,
    canonical_json_bytes as _contract_canonical_json_bytes,
    load_active_contract,
)


HEX_64 = re.compile(r"^[0-9a-f]{64}$")
TOKEN = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")


@dataclass(frozen=True)
class _CompilerFailure(Exception):
    code: str
    detail: str
    audit: tuple[Mapping[str, Any], ...] = ()


@dataclass(frozen=True)
class _Detection:
    local_id: str
    category: str
    bbox: tuple[float, float, float, float]
    confidence: float
    score_domain: tuple[Any, ...]
    component_id: str
    component_revision: str
    source_index: int

    @property
    def area(self) -> float:
        return (self.bbox[2] - self.bbox[0]) * (self.bbox[3] - self.bbox[1])

    @property
    def source_tuple(self) -> tuple[Any, ...]:
        return (
            self.component_id,
            self.component_revision,
            self.local_id,
            *self.bbox,
            self.source_index,
        )


def canonical_json_bytes(value: Any) -> bytes:
    """Public canonical serialization helper."""

    return _contract_canonical_json_bytes(value)


def _normalise_token(value: Any) -> str:
    if not isinstance(value, str):
        raise _CompilerFailure("UNKNOWN_LABEL", "label is not a string")
    text = unicodedata.normalize("NFKC", value).strip().casefold()
    text = re.sub(r"[\s-]+", "_", text)
    if not TOKEN.fullmatch(text):
        raise _CompilerFailure("UNKNOWN_LABEL", f"invalid closed token {value!r}")
    return text


def _finite_number(value: Any, detail: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _CompilerFailure("MALFORMED_OBSERVATION", detail)
    result = float(value)
    if not math.isfinite(result):
        raise _CompilerFailure("MALFORMED_OBSERVATION", detail)
    return 0.0 if result == 0 else result


def _box(value: Any) -> tuple[float, float, float, float]:
    if not isinstance(value, list) or len(value) != 4:
        raise _CompilerFailure("INVALID_BOUNDING_BOX", "bbox must contain four xyxy values")
    box = tuple(_finite_number(item, "bbox values must be finite numbers") for item in value)
    x1, y1, x2, y2 = box
    if any(item < 0 or item > 1 for item in box) or x2 <= x1 or y2 <= y1:
        raise _CompilerFailure("INVALID_BOUNDING_BOX", "bbox must be positive-area normalized xyxy")
    return box


def _iou(a: Sequence[float], b: Sequence[float]) -> float:
    left = max(a[0], b[0])
    top = max(a[1], b[1])
    right = min(a[2], b[2])
    bottom = min(a[3], b[3])
    intersection = max(0.0, right - left) * max(0.0, bottom - top)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    union = area_a + area_b - intersection
    return 0.0 if union <= 0 else intersection / union


def _intersection(a: Sequence[float], b: Sequence[float]) -> tuple[float, float, float]:
    width = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    height = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    return width, height, width * height


class SemanticCompilerV3:
    """Compile bounded v3.1 observations into deterministic v3 graph results."""

    def __init__(self, contract: ActiveV31Contract | None = None) -> None:
        self.contract = contract or load_active_contract()
        self.base = self.contract.base_observation
        self.compiler_config = self.base["compiler"]
        self.failure_codes = frozenset(self.compiler_config["typed_failure_codes"])
        self.entity_labels = frozenset(self.base["entity_categories"])
        self.attributes = {key: frozenset(values) for key, values in self.base["attributes"].items()}
        self.unary_labels = frozenset(self.base["unary_actions"])
        self.interaction_labels = frozenset(self.base["binary_interactions"])
        self.geometry_labels = frozenset(self.base["derived_spatial_relations"])
        self.inverse = self.base["inverse_normalisation"]
        self.scene_labels = frozenset(self.base["scenes"])
        self.maximum_observations = int(self.base["limits"]["maximum_observations_per_image"])
        self.maximum_nodes = int(self.base["limits"]["maximum_credential_nodes"])

    def compile(self, value: bytes | bytearray | memoryview | Mapping[str, Any], *, eligible_types: Iterable[str] | None = None) -> bytes:
        audit: list[Mapping[str, Any]] = []
        source: dict[str, Any] = {}
        try:
            if isinstance(value, Mapping):
                observation = dict(value)
            else:
                try:
                    decoded = bytes(value).decode("utf-8")
                    observation = json.loads(decoded)
                except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
                    raise _CompilerFailure("MALFORMED_OBSERVATION", "input is not one UTF-8 JSON object")
                if not isinstance(observation, dict):
                    raise _CompilerFailure("MALFORMED_OBSERVATION", "top-level observation must be an object")
            source = self._source_projection(observation)
            graph, graph_audit = self._compile_observation(observation, eligible_types=eligible_types)
            audit.extend(graph_audit)
            result = {
                "audit": {"events": self._sort_dicts(audit), "node_boxes": graph.pop("_node_boxes")},
                "compiler_id": self.contract.compiler_id,
                "graph": graph,
                "result_schema": self.contract.result_schema,
                "source": source,
                "status": "graph",
            }
        except _CompilerFailure as failure:
            code = failure.code if failure.code in self.failure_codes else "MALFORMED_OBSERVATION"
            result = {
                "audit": {"events": self._sort_dicts([*audit, *failure.audit])},
                "compiler_id": self.contract.compiler_id,
                "failure": {"code": code, "detail": failure.detail},
                "result_schema": self.contract.result_schema,
                "source": source,
                "status": "typed_failure",
            }
        except (KeyError, TypeError, ValueError, OverflowError) as failure:
            result = {
                "audit": {"events": self._sort_dicts(audit)},
                "compiler_id": self.contract.compiler_id,
                "failure": {"code": "MALFORMED_OBSERVATION", "detail": f"invalid observation structure: {type(failure).__name__}"},
                "result_schema": self.contract.result_schema,
                "source": source,
                "status": "typed_failure",
            }
        try:
            return _contract_canonical_json_bytes(result)
        except (TypeError, ValueError, UnicodeError):
            fallback = {
                "audit": {"events": []},
                "compiler_id": self.contract.compiler_id,
                "failure": {"code": "SERIALIZATION_FAILURE", "detail": "canonical serialization failed"},
                "result_schema": self.contract.result_schema,
                "source": {},
                "status": "typed_failure",
            }
            return _contract_canonical_json_bytes(fallback)

    def compile_object(self, observation: Mapping[str, Any], *, eligible_types: Iterable[str] | None = None) -> dict[str, Any]:
        return json.loads(self.compile(observation, eligible_types=eligible_types))

    def _source_projection(self, observation: Mapping[str, Any]) -> dict[str, Any]:
        keys = ("observation_version", "pipeline_id", "pipeline_revision", "image_id", "image_sha256")
        return {key: observation[key] for key in keys if isinstance(observation.get(key), str)}

    def _compile_observation(
        self,
        observation: MutableMapping[str, Any],
        *,
        eligible_types: Iterable[str] | None,
    ) -> tuple[dict[str, Any], list[Mapping[str, Any]]]:
        required = self.base["observation_record"]["required_fields"]
        missing = [field for field in required if field not in observation]
        if missing:
            raise _CompilerFailure("MALFORMED_OBSERVATION", f"missing required fields: {','.join(missing)}")
        if observation["observation_version"] != self.contract.observation_version:
            raise _CompilerFailure("UNSUPPORTED_OBSERVATION_VERSION", "observation version is not active v3.1")

        pipeline_id = observation["pipeline_id"]
        if pipeline_id not in self.contract.pipeline_ids:
            raise _CompilerFailure("UNDECLARED_COMPONENT", "pipeline is not in the frozen v3.1 shortlist")
        if observation["pipeline_revision"] != self.contract.expected_pipeline_revision(pipeline_id):
            raise _CompilerFailure("UNDECLARED_COMPONENT", "pipeline revision does not match frozen config")
        if not isinstance(observation["image_id"], str) or not observation["image_id"]:
            raise _CompilerFailure("MALFORMED_OBSERVATION", "image_id must be a non-empty string")
        if not isinstance(observation["image_sha256"], str) or not HEX_64.fullmatch(observation["image_sha256"]):
            raise _CompilerFailure("MALFORMED_OBSERVATION", "image_sha256 must be lowercase SHA-256")

        array_fields = ("detections", "attributes", "unary_actions", "binary_interactions", "scenes", "component_events")
        for field in array_fields:
            if not isinstance(observation[field], list):
                raise _CompilerFailure("MALFORMED_OBSERVATION", f"{field} must be an array")
        observation_count = sum(len(observation[field]) for field in array_fields[:-1])
        if observation_count > self.maximum_observations:
            raise _CompilerFailure("MALFORMED_OBSERVATION", "observation count exceeds frozen limit")

        components = self.contract.component_map(pipeline_id)
        self._validate_component_events(observation["component_events"], components)
        audit: list[Mapping[str, Any]] = []

        all_ids: set[str] = set()
        accepted_detections: list[_Detection] = []
        for index, raw in enumerate(observation["detections"]):
            if not isinstance(raw, dict):
                raise _CompilerFailure("MALFORMED_OBSERVATION", f"detections[{index}] must be an object")
            local_id = raw.get("local_id")
            if not isinstance(local_id, str) or not local_id:
                raise _CompilerFailure("MALFORMED_OBSERVATION", f"detections[{index}].local_id is invalid")
            if local_id in all_ids:
                raise _CompilerFailure("DUPLICATE_LOCAL_ID", f"duplicate local_id {local_id}")
            all_ids.add(local_id)
            confidence, score_domain, keep = self._confidence(raw, f"detections[{index}]")
            if not keep:
                audit.append({"code": "OMITTED_BY_FROZEN_THRESHOLD", "path": f"detections[{index}]"})
                continue
            component_id, component_revision = self._provenance(raw, components, f"detections[{index}]")
            category = self._closed(raw.get("category"), self.entity_labels)
            accepted_detections.append(
                _Detection(
                    local_id=local_id,
                    category=category,
                    bbox=_box(raw.get("bbox")),
                    confidence=confidence,
                    score_domain=score_domain,
                    component_id=component_id,
                    component_revision=component_revision,
                    source_index=index,
                )
            )

        survivors, remap, duplicate_audit = self._resolve_duplicates(accepted_detections)
        audit.extend(duplicate_audit)
        if len(survivors) > self.maximum_nodes:
            raise _CompilerFailure("TOO_MANY_CREDENTIAL_ENTITIES", "accepted credential entities exceed eight", tuple(audit))

        ordered = sorted(survivors, key=lambda item: (item.category, *item.bbox, item.source_tuple))
        node_ids = {item.local_id: f"n{index:03d}" for index, item in enumerate(ordered, start=1)}
        for original, winner in tuple(remap.items()):
            remap[original] = node_ids[winner]
        for item in ordered:
            remap[item.local_id] = node_ids[item.local_id]

        eligible = self._eligible_types(eligible_types)
        nodes = [] if "entity" not in eligible else [
            {"category": item.category, "id": node_ids[item.local_id]} for item in ordered
        ]
        if "entity" not in eligible:
            audit.append({"code": "OMITTED_INELIGIBLE_TYPE", "type": "entity"})

        attributes = self._compile_attributes(observation["attributes"], components, remap, eligible, audit)
        unary = self._compile_unary(observation["unary_actions"], components, remap, eligible, audit)
        binary = self._compile_binary(observation["binary_interactions"], components, remap, eligible, audit)
        scenes = self._compile_scenes(observation["scenes"], components, eligible, audit)
        counts = self._derive_counts(ordered) if "count" in eligible else []
        if "count" not in eligible:
            audit.append({"code": "OMITTED_INELIGIBLE_TYPE", "type": "count"})
        if "geometry_relation" in eligible:
            binary.extend(self._derive_geometry(ordered, node_ids))
        else:
            audit.append({"code": "OMITTED_INELIGIBLE_TYPE", "type": "geometry_relation"})

        graph = {
            "_node_boxes": [
                {"bbox": list(item.bbox), "id": node_ids[item.local_id]} for item in ordered
            ],
            "attributes": self._sort_dicts(attributes),
            "binary": self._sort_dicts(self._dedupe_dicts(binary)),
            "counts": self._sort_dicts(counts),
            "nodes": self._sort_dicts(nodes),
            "scenes": self._sort_dicts(scenes),
            "unary": self._sort_dicts(unary),
        }
        return graph, audit

    def _validate_component_events(self, events: list[Any], components: Mapping[str, Mapping[str, Any]]) -> None:
        seen: set[str] = set()
        for index, raw in enumerate(events):
            if not isinstance(raw, dict):
                raise _CompilerFailure("MALFORMED_OBSERVATION", f"component_events[{index}] must be an object")
            component_id, revision = self._provenance(raw, components, f"component_events[{index}]")
            if component_id in seen:
                raise _CompilerFailure("MALFORMED_OBSERVATION", f"duplicate component event {component_id}")
            seen.add(component_id)
            status = raw.get("status")
            if not isinstance(status, str) or status not in {"ok", "abstain", "failure"}:
                raise _CompilerFailure("MALFORMED_OBSERVATION", f"invalid component status for {component_id}")
            for field in ("elapsed_seconds", "peak_rss_bytes", "peak_gpu_bytes"):
                if _finite_number(raw.get(field), f"invalid {field} for {component_id}") < 0:
                    raise _CompilerFailure("MALFORMED_OBSERVATION", f"negative {field} for {component_id}")
            failure_code = raw.get("failure_code")
            if status == "failure":
                if not isinstance(failure_code, str) or not failure_code:
                    raise _CompilerFailure("MALFORMED_OBSERVATION", f"missing failure code for {component_id}")
                raise _CompilerFailure("REQUIRED_COMPONENT_FAILURE", f"required component {component_id} failed: {failure_code}")
            if failure_code is not None:
                raise _CompilerFailure("MALFORMED_OBSERVATION", f"unexpected failure code for {component_id}")
        if seen != set(components):
            missing = sorted(set(components) - seen)
            raise _CompilerFailure("REQUIRED_COMPONENT_FAILURE", f"missing required component events: {','.join(missing)}")

    def _provenance(
        self,
        raw: Mapping[str, Any],
        components: Mapping[str, Mapping[str, Any]],
        path: str,
    ) -> tuple[str, str]:
        component_id = raw.get("component_id")
        component_revision = raw.get("component_revision")
        if not isinstance(component_id, str) or component_id not in components:
            raise _CompilerFailure("UNDECLARED_COMPONENT", f"{path} uses undeclared component")
        expected = components[component_id].get("revision")
        if expected is None:
            expected = components[component_id].get("model_revision")
        if component_revision != expected:
            raise _CompilerFailure("UNDECLARED_COMPONENT", f"{path} component revision mismatch")
        return str(component_id), str(component_revision)

    def _confidence(self, raw: Mapping[str, Any], path: str) -> tuple[float, tuple[Any, ...], bool]:
        confidence = raw.get("confidence")
        if not isinstance(confidence, dict):
            raise _CompilerFailure("UNDECLARED_SCORE_DOMAIN", f"{path}.confidence lacks frozen score metadata")
        required = self.base["confidence_contract"]["required_metadata"]
        if "value" not in confidence or any(field not in confidence for field in required):
            raise _CompilerFailure("UNDECLARED_SCORE_DOMAIN", f"{path}.confidence metadata is incomplete")
        score_name = confidence["score_name"]
        score_range = confidence["score_range"]
        source = confidence["threshold_source"]
        if not isinstance(score_name, str) or not score_name or not isinstance(score_range, list) or len(score_range) != 2:
            raise _CompilerFailure("UNDECLARED_SCORE_DOMAIN", f"{path}.confidence domain is invalid")
        low = _finite_number(score_range[0], f"{path}.score_range is invalid")
        high = _finite_number(score_range[1], f"{path}.score_range is invalid")
        value = _finite_number(confidence["value"], f"{path}.confidence value is invalid")
        threshold = _finite_number(confidence["threshold"], f"{path}.confidence threshold is invalid")
        if high <= low or not low <= value <= high or not low <= threshold <= high or source != "development":
            raise _CompilerFailure("UNDECLARED_SCORE_DOMAIN", f"{path}.confidence domain is not frozen-development valid")
        rounded = round(value, int(self.base["observation_canonicalisation"]["confidence_round_decimal_places"]))
        domain = (score_name, low, high, threshold, source)
        keep = not bool(raw.get("abstained", False)) and rounded >= threshold
        return rounded, domain, keep

    def _closed(self, value: Any, allowed: frozenset[str]) -> str:
        token = _normalise_token(value)
        if token not in allowed:
            raise _CompilerFailure("UNKNOWN_LABEL", f"label {token!r} is outside L_visual")
        return token

    def _resolve_duplicates(
        self, detections: list[_Detection]
    ) -> tuple[list[_Detection], dict[str, str], list[Mapping[str, Any]]]:
        for index, first in enumerate(detections):
            for second in detections[index + 1 :]:
                if (
                    first.category == second.category
                    and _iou(first.bbox, second.bbox) >= 0.80
                    and (
                        first.component_id != second.component_id
                        or first.component_revision != second.component_revision
                        or first.score_domain != second.score_domain
                    )
                ):
                    raise _CompilerFailure("AMBIGUOUS_IDENTITY", "duplicate candidates use incomparable component-local score domains")
        ranked = sorted(detections, key=lambda item: (-item.confidence, item.area, item.source_tuple))
        survivors: list[_Detection] = []
        remap: dict[str, str] = {}
        audit: list[Mapping[str, Any]] = []
        for candidate in ranked:
            winner = next(
                (
                    kept
                    for kept in survivors
                    if kept.category == candidate.category and _iou(kept.bbox, candidate.bbox) >= 0.80
                ),
                None,
            )
            if winner is None:
                survivors.append(candidate)
                remap[candidate.local_id] = candidate.local_id
            else:
                remap[candidate.local_id] = winner.local_id
                audit.append({"code": "DUPLICATE_RESOLVED", "dropped": candidate.local_id, "winner": winner.local_id})
        return survivors, remap, audit

    def _eligible_types(self, values: Iterable[str] | None) -> frozenset[str]:
        all_types = {"entity", "colour", "size", "material", "pattern", "unary_action", "binary_interaction", "geometry_relation", "count", "scene"}
        if values is None:
            return frozenset(all_types)
        selected = frozenset(values)
        if not selected <= all_types:
            raise _CompilerFailure("UNSUPPORTED_CREDENTIAL_TYPE", "eligible type set contains an unsupported type")
        return selected

    def _resolve_reference(self, value: Any, remap: Mapping[str, str], path: str) -> str:
        if not isinstance(value, str) or value not in remap:
            raise _CompilerFailure("DANGLING_REFERENCE", f"{path} references an unknown detection")
        return remap[value]

    def _compile_attributes(self, rows: list[Any], components: Mapping[str, Mapping[str, Any]], remap: Mapping[str, str], eligible: frozenset[str], audit: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
        output: list[dict[str, Any]] = []
        for index, raw in enumerate(rows):
            if not isinstance(raw, dict):
                raise _CompilerFailure("MALFORMED_OBSERVATION", f"attributes[{index}] must be an object")
            _, _, keep = self._confidence(raw, f"attributes[{index}]")
            if not keep:
                audit.append({"code": "OMITTED_BY_FROZEN_THRESHOLD", "path": f"attributes[{index}]"})
                continue
            self._provenance(raw, components, f"attributes[{index}]")
            subtype = self._closed(raw.get("attribute_type"), frozenset(self.attributes))
            value = self._closed(raw.get("value"), self.attributes[subtype])
            node = self._resolve_reference(raw.get("detection_id"), remap, f"attributes[{index}]")
            if subtype not in eligible:
                audit.append({"code": "OMITTED_INELIGIBLE_TYPE", "path": f"attributes[{index}]", "type": subtype})
                continue
            output.append({"node": node, "type": subtype, "value": value})
        return self._dedupe_dicts(output)

    def _compile_unary(self, rows: list[Any], components: Mapping[str, Mapping[str, Any]], remap: Mapping[str, str], eligible: frozenset[str], audit: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
        output: list[dict[str, Any]] = []
        for index, raw in enumerate(rows):
            if not isinstance(raw, dict):
                raise _CompilerFailure("MALFORMED_OBSERVATION", f"unary_actions[{index}] must be an object")
            _, _, keep = self._confidence(raw, f"unary_actions[{index}]")
            if not keep:
                audit.append({"code": "OMITTED_BY_FROZEN_THRESHOLD", "path": f"unary_actions[{index}]"})
                continue
            self._provenance(raw, components, f"unary_actions[{index}]")
            action = self._closed(raw.get("action"), self.unary_labels)
            node = self._resolve_reference(raw.get("detection_id"), remap, f"unary_actions[{index}]")
            if "unary_action" not in eligible:
                audit.append({"code": "OMITTED_INELIGIBLE_TYPE", "path": f"unary_actions[{index}]", "type": "unary_action"})
                continue
            output.append({"action": action, "node": node})
        return self._dedupe_dicts(output)

    def _compile_binary(self, rows: list[Any], components: Mapping[str, Mapping[str, Any]], remap: Mapping[str, str], eligible: frozenset[str], audit: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
        allowed = self.interaction_labels | self.geometry_labels | frozenset(self.inverse)
        output: list[dict[str, Any]] = []
        for index, raw in enumerate(rows):
            if not isinstance(raw, dict):
                raise _CompilerFailure("MALFORMED_OBSERVATION", f"binary_interactions[{index}] must be an object")
            _, _, keep = self._confidence(raw, f"binary_interactions[{index}]")
            if not keep:
                audit.append({"code": "OMITTED_BY_FROZEN_THRESHOLD", "path": f"binary_interactions[{index}]"})
                continue
            self._provenance(raw, components, f"binary_interactions[{index}]")
            relation = self._closed(raw.get("interaction"), allowed)
            source = self._resolve_reference(raw.get("source_detection_id"), remap, f"binary_interactions[{index}]")
            target = self._resolve_reference(raw.get("target_detection_id"), remap, f"binary_interactions[{index}]")
            if source == target:
                raise _CompilerFailure("AMBIGUOUS_IDENTITY", f"binary_interactions[{index}] collapses to a self edge")
            if relation in self.inverse:
                rule = self.inverse[relation]
                relation = rule["canonical"]
                if rule["swap_nodes"]:
                    source, target = target, source
            kind = "geometry_relation" if relation in self.geometry_labels else "binary_interaction"
            if kind not in eligible:
                audit.append({"code": "OMITTED_INELIGIBLE_TYPE", "path": f"binary_interactions[{index}]", "type": kind})
                continue
            if relation in {"overlap", "near"} and target < source:
                source, target = target, source
            output.append({"relation": relation, "source": source, "target": target})
        return self._dedupe_dicts(output)

    def _compile_scenes(self, rows: list[Any], components: Mapping[str, Mapping[str, Any]], eligible: frozenset[str], audit: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
        output: list[dict[str, Any]] = []
        for index, raw in enumerate(rows):
            if not isinstance(raw, dict):
                raise _CompilerFailure("MALFORMED_OBSERVATION", f"scenes[{index}] must be an object")
            _, _, keep = self._confidence(raw, f"scenes[{index}]")
            if not keep:
                audit.append({"code": "OMITTED_BY_FROZEN_THRESHOLD", "path": f"scenes[{index}]"})
                continue
            self._provenance(raw, components, f"scenes[{index}]")
            value = self._closed(raw.get("value"), self.scene_labels)
            if "scene" not in eligible:
                audit.append({"code": "OMITTED_INELIGIBLE_TYPE", "path": f"scenes[{index}]", "type": "scene"})
                continue
            output.append({"value": value})
        return self._dedupe_dicts(output)

    def _derive_counts(self, detections: Sequence[_Detection]) -> list[dict[str, Any]]:
        counts: dict[str, int] = {}
        for item in detections:
            counts[item.category] = counts.get(item.category, 0) + 1
        return [
            {"bucket": str(count) if count <= 4 else "5_plus", "category": category}
            for category, count in sorted(counts.items())
        ]

    def _derive_geometry(self, detections: Sequence[_Detection], node_ids: Mapping[str, str]) -> list[dict[str, Any]]:
        output: list[dict[str, Any]] = []
        for first_index, first in enumerate(detections):
            for second_index, second in enumerate(detections):
                if first_index == second_index:
                    continue
                source = node_ids[first.local_id]
                target = node_ids[second.local_id]
                ax = (first.bbox[0] + first.bbox[2]) / 2
                ay = (first.bbox[1] + first.bbox[3]) / 2
                bx = (second.bbox[0] + second.bbox[2]) / 2
                by = (second.bbox[1] + second.bbox[3]) / 2
                width_overlap, _, intersection = _intersection(first.bbox, second.bbox)
                if ax + 0.05 <= bx:
                    output.append({"relation": "left_of", "source": source, "target": target})
                if ay + 0.05 <= by:
                    output.append({"relation": "above", "source": source, "target": target})
                if intersection / first.area >= 0.90:
                    output.append({"relation": "inside", "source": source, "target": target})
                if abs(first.bbox[3] - second.bbox[1]) <= 0.08 and width_overlap / (first.bbox[2] - first.bbox[0]) >= 0.50:
                    output.append({"relation": "on", "source": source, "target": target})
                if abs(first.bbox[1] - second.bbox[3]) <= 0.08 and width_overlap / (first.bbox[2] - first.bbox[0]) >= 0.50:
                    output.append({"relation": "under", "source": source, "target": target})
                if source < target:
                    if _iou(first.bbox, second.bbox) >= 0.20:
                        output.append({"relation": "overlap", "source": source, "target": target})
                    if math.dist((ax, ay), (bx, by)) <= 0.25:
                        output.append({"relation": "near", "source": source, "target": target})
        return self._dedupe_dicts(output)

    @staticmethod
    def _dedupe_dicts(values: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
        unique = {json.dumps(value, sort_keys=True, separators=(",", ":")): value for value in values}
        return [unique[key] for key in sorted(unique)]

    @staticmethod
    def _sort_dicts(values: Iterable[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
        return sorted(values, key=lambda value: json.dumps(value, sort_keys=True, separators=(",", ":")))
