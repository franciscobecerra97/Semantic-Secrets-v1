"""Deterministic canonicalisation for structured semantic atoms."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Iterable, Mapping


CANONICAL_SCHEME_VERSION = "canonical-semantics-v1"
SOURCE_SCHEMA_VERSION = "structured-extraction-v1"


class CanonicalizationError(ValueError):
    """Raised when an input cannot be interpreted under the frozen scheme."""


@dataclass(frozen=True)
class CanonicalResult:
    scheme_version: str
    atoms: tuple[str, ...]
    warnings: tuple[str, ...]


_ALIASES = {
    "colour": "color",
    "colours": "color",
    "colors": "color",
    "grey": "gray",
    "scarlet": "red",
    "crimson": "red",
    "next_to": "beside",
    "alongside": "beside",
    "in_aquarium": "aquarium",
    "at_coast_at_sunrise": "coastal_sunrise",
    "at_coast_at_night": "coastal_night",
}

_IRREGULAR_SINGULAR = {
    "children": "child",
    "geese": "goose",
    "mice": "mouse",
    "people": "person",
    "teeth": "tooth",
}

_REVERSE_RELATIONS = {
    "below": "above",
    "right_of": "left_of",
    "behind": "in_front_of",
    "under": "on",
}
_SYMMETRIC_RELATIONS = {"beside"}


def normalise_token(value: Any, *, singular: bool = False) -> str:
    text = unicodedata.normalize("NFKC", str(value)).casefold().strip()
    text = re.sub(r"[^\w]+", "_", text, flags=re.UNICODE).strip("_")
    text = re.sub(r"_+", "_", text)
    text = _ALIASES.get(text, text)
    if singular:
        text = singularise(text)
    return _ALIASES.get(text, text)


def singularise(value: str) -> str:
    if value in _IRREGULAR_SINGULAR:
        return _IRREGULAR_SINGULAR[value]
    if value.endswith("ies") and len(value) > 4:
        return value[:-3] + "y"
    if value.endswith(("sses", "shes", "ches", "xes", "zes")) and len(value) > 4:
        return value[:-2]
    if value.endswith("s") and not value.endswith(("ss", "us", "is")) and len(value) > 3:
        return value[:-1]
    return value


def _confidence_ok(item: Mapping[str, Any], minimum: float) -> bool:
    confidence = item.get("confidence")
    return confidence is None or float(confidence) >= minimum


def _require_token(value: Any, context: str, *, singular: bool = False) -> str:
    token = normalise_token(value, singular=singular)
    if not token:
        raise CanonicalizationError(f"empty canonical token for {context}")
    return token


def _resolve_object(reference: Any, object_labels: Mapping[str, str]) -> str:
    ref = normalise_token(reference)
    return object_labels.get(ref, _require_token(reference, "object reference", singular=True))


def canonicalize_extraction(
    extraction: Mapping[str, Any],
    *,
    minimum_confidence: float = 0.25,
) -> CanonicalResult:
    if extraction.get("schema_version") != SOURCE_SCHEMA_VERSION:
        raise CanonicalizationError(
            f"schema mismatch: expected {SOURCE_SCHEMA_VERSION!r}, got {extraction.get('schema_version')!r}"
        )
    if not 0 <= minimum_confidence <= 1:
        raise CanonicalizationError("minimum_confidence must be in [0, 1]")

    atoms: set[str] = set()
    warnings = {normalise_token(value) for value in extraction.get("warnings", []) if normalise_token(value)}
    object_labels: dict[str, str] = {}

    for item in extraction.get("objects", []):
        if not _confidence_ok(item, minimum_confidence):
            warnings.add("low_confidence_object_dropped")
            continue
        object_id = _require_token(item.get("id"), "object id")
        label = _require_token(item.get("label"), "object label", singular=True)
        object_labels[object_id] = label
        atoms.add(f"object:{label}")

    for item in extraction.get("attributes", []):
        if not _confidence_ok(item, minimum_confidence):
            warnings.add("low_confidence_attribute_dropped")
            continue
        subject = _resolve_object(item.get("subject"), object_labels)
        name = _require_token(item.get("name"), "attribute name")
        value = _require_token(item.get("value"), "attribute value", singular=True)
        atoms.add(f"attribute:{subject}:{name}:{value}")

    for item in extraction.get("counts", []):
        if not _confidence_ok(item, minimum_confidence):
            warnings.add("low_confidence_count_dropped")
            continue
        subject = _resolve_object(item.get("object_id"), object_labels)
        value = int(item.get("value"))
        if value < 1:
            raise CanonicalizationError("count must be positive")
        atoms.add(f"count:{subject}:{value}")

    for item in extraction.get("actions", []):
        if not _confidence_ok(item, minimum_confidence):
            warnings.add("low_confidence_action_dropped")
            continue
        subject = _resolve_object(item.get("subject"), object_labels)
        verb = _require_token(item.get("verb"), "action verb", singular=True)
        object_ref = item.get("object")
        target = "_" if object_ref is None else _resolve_object(object_ref, object_labels)
        atoms.add(f"action:{subject}:{verb}:{target}")

    for item in extraction.get("relations", []):
        if not _confidence_ok(item, minimum_confidence):
            warnings.add("low_confidence_relation_dropped")
            continue
        subject = _resolve_object(item.get("subject"), object_labels)
        target = _resolve_object(item.get("object"), object_labels)
        predicate = _require_token(item.get("predicate"), "relation predicate")
        if predicate in _REVERSE_RELATIONS:
            subject, target = target, subject
            predicate = _REVERSE_RELATIONS[predicate]
        if predicate in _SYMMETRIC_RELATIONS and target < subject:
            subject, target = target, subject
        atoms.add(f"relation:{subject}:{predicate}:{target}")

    for item in extraction.get("scenes", []):
        if not _confidence_ok(item, minimum_confidence):
            warnings.add("low_confidence_scene_dropped")
            continue
        atoms.add(f"scene:{_require_token(item.get('label'), 'scene label')}")

    if not atoms:
        warnings.add("empty_representation")
    return CanonicalResult(CANONICAL_SCHEME_VERSION, tuple(sorted(atoms)), tuple(sorted(warnings)))


def canonicalize_label_atoms(atoms: Iterable[Mapping[str, Any]]) -> CanonicalResult:
    items = list(atoms)
    object_labels = {
        normalise_token(item["id"]): _require_token(item["value"], "label object", singular=True)
        for item in items
        if item.get("type") == "object"
    }
    extraction: dict[str, Any] = {
        "schema_version": SOURCE_SCHEMA_VERSION,
        "objects": [],
        "attributes": [],
        "counts": [],
        "actions": [],
        "relations": [],
        "scenes": [],
        "warnings": [],
    }
    for item in items:
        atom_type = item.get("type")
        if atom_type == "object":
            extraction["objects"].append(
                {"id": normalise_token(item["id"]), "label": item["value"], "confidence": 1.0}
            )
        elif atom_type == "attribute":
            extraction["attributes"].append(
                {
                    "subject": normalise_token(item["subject"]),
                    "name": item.get("subtype", "attribute"),
                    "value": item["value"],
                    "confidence": 1.0,
                }
            )
        elif atom_type == "count":
            extraction["counts"].append(
                {"object_id": normalise_token(item["subject"]), "value": int(item["value"]), "confidence": 1.0}
            )
        elif atom_type == "action":
            extraction["actions"].append(
                {
                    "subject": normalise_token(item["subject"]),
                    "verb": item["value"],
                    "object": normalise_token(item["object"]) if item.get("object") else None,
                    "confidence": 1.0,
                }
            )
        elif atom_type == "relation":
            extraction["relations"].append(
                {
                    "subject": normalise_token(item["subject"]),
                    "predicate": item["value"],
                    "object": normalise_token(item["object"]),
                    "confidence": 1.0,
                }
            )
        elif atom_type == "scene":
            extraction["scenes"].append({"label": item["value"], "confidence": 1.0})
        else:
            raise CanonicalizationError(f"unsupported label atom type: {atom_type!r}")
    result = canonicalize_extraction(extraction, minimum_confidence=0)
    unresolved = [key for key in object_labels if key not in {normalise_token(x["id"]) for x in extraction["objects"]}]
    if unresolved:
        raise CanonicalizationError(f"unresolved object labels: {unresolved}")
    return result
