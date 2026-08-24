"""Transparent controlled-English extraction lower bound."""

from __future__ import annotations

import re
from typing import Iterable

from .canonicalize import normalise_token


COLORS = ("black", "blue", "brown", "green", "gray", "orange", "purple", "red", "white", "yellow")
MATERIALS = ("glass", "metal", "paper", "wooden", "wood")
ACTIONS = ("carry", "catch", "hold", "juggle", "read", "ride", "sleep", "watch")
ACTION_FORMS = {
    "carry": ("carry", "carries", "carrying"),
    "catch": ("catch", "catches", "catching"),
    "hold": ("hold", "holds", "holding"),
    "juggle": ("juggle", "juggles", "juggling"),
    "read": ("read", "reads", "reading"),
    "ride": ("ride", "rides", "riding"),
    "sleep": ("sleep", "sleeps", "sleeping"),
    "watch": ("watch", "watches", "watching"),
}
RELATIONS = (
    ("in front of", "in_front_of"),
    ("to the left of", "left_of"),
    ("to the right of", "right_of"),
    ("next to", "beside"),
    ("inside", "inside"),
    ("between", "between"),
    ("above", "above"),
    ("below", "below"),
    ("under", "under"),
    ("beside", "beside"),
    ("behind", "behind"),
    (" on ", "on"),
)
SCENES = (
    "aquarium",
    "coastal night",
    "coastal sunrise",
    "desert",
    "forest",
    "kitchen",
    "library",
    "living room",
    "lunar",
    "warehouse",
)
NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4}


def _mentions(text: str, values: Iterable[str]) -> list[str]:
    return [value for value in values if re.search(rf"\b{re.escape(value)}s?\b", text)]


def extract_controlled_text(text: str, *, object_lexicon: Iterable[str]) -> dict:
    normalized = " " + re.sub(r"\s+", " ", text.casefold()).strip() + " "
    object_values = sorted({normalise_token(value, singular=True) for value in object_lexicon})
    objects = [value for value in object_values if re.search(rf"\b{re.escape(value)}(?:s|es)?\b", normalized)]
    object_ids = {value: f"o_{index + 1}" for index, value in enumerate(objects)}
    extraction = {
        "schema_version": "structured-extraction-v1",
        "objects": [
            {"id": object_ids[value], "label": value, "confidence": 1.0} for value in objects
        ],
        "attributes": [],
        "counts": [],
        "actions": [],
        "relations": [],
        "scenes": [],
        "warnings": [],
    }
    for value in objects:
        for color in _mentions(normalized, COLORS):
            if re.search(rf"\b{re.escape(color)}\b(?:\s+\w+){{0,2}}\s+{re.escape(value)}(?:s|es)?\b", normalized):
                extraction["attributes"].append(
                    {"subject": object_ids[value], "name": "color", "value": color, "confidence": 1.0}
                )
        for material in _mentions(normalized, MATERIALS):
            if re.search(rf"\b{re.escape(material)}\b(?:\s+\w+){{0,2}}\s+{re.escape(value)}(?:s|es)?\b", normalized):
                extraction["attributes"].append(
                    {"subject": object_ids[value], "name": "material", "value": material, "confidence": 1.0}
                )
        for word, number in NUMBER_WORDS.items():
            if re.search(
                rf"\b(?:exactly\s+)?{word}\s+(?:\w+\s+){{0,2}}{re.escape(value)}(?:s|es)?\b",
                normalized,
            ):
                extraction["counts"].append(
                    {"object_id": object_ids[value], "value": number, "confidence": 1.0}
                )
        digit = re.search(
            rf"\b(?:exactly\s+)?([1-4])\s+(?:\w+\s+){{0,2}}{re.escape(value)}(?:s|es)?\b",
            normalized,
        )
        if digit:
            extraction["counts"].append(
                {"object_id": object_ids[value], "value": int(digit.group(1)), "confidence": 1.0}
            )

    for scene in SCENES:
        if re.search(rf"\b{re.escape(scene)}\b", normalized):
            extraction["scenes"].append(
                {"label": normalise_token(scene), "confidence": 1.0}
            )

    for verb in ACTIONS:
        match = re.search(rf"\b(?:{'|'.join(map(re.escape, ACTION_FORMS[verb]))})\b", normalized)
        if match:
            before, after = normalized[: match.start()], normalized[match.end() :]
            subject_value = next(
                (value for value in reversed(objects) if re.search(rf"\b{re.escape(value)}(?:s|es)?\b", before)),
                None,
            )
            target_value = next(
                (value for value in objects if re.search(rf"\b{re.escape(value)}(?:s|es)?\b", after)),
                None,
            )
            if subject_value:
                extraction["actions"].append(
                    {
                        "subject": object_ids[subject_value],
                        "verb": verb,
                        "object": object_ids[target_value] if target_value else None,
                        "confidence": 1.0,
                    }
                )

    for phrase, predicate in RELATIONS:
        position = normalized.find(phrase)
        if position >= 0 and len(objects) >= 2:
            before = normalized[:position]
            after = normalized[position + len(phrase) :]
            subject = next((value for value in reversed(objects) if re.search(rf"\b{re.escape(value)}s?\b", before)), objects[0])
            target = next((value for value in objects if re.search(rf"\b{re.escape(value)}s?\b", after)), objects[1])
            extraction["relations"].append(
                {
                    "subject": object_ids[subject],
                    "predicate": predicate,
                    "object": object_ids[target],
                    "confidence": 1.0,
                }
            )
            break
    if not objects:
        extraction["warnings"].append("no_known_object")
    return extraction
