from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "prototype"))

from semantic_secrets.semantics import (  # noqa: E402
    CANONICAL_SCHEME_VERSION,
    CanonicalizationError,
    StructuredSet,
    WeightedStructuredSet,
    canonicalize_extraction,
    canonicalize_label_atoms,
    extract_controlled_text,
    fit_idf_weights,
)


class CanonicalizationTests(unittest.TestCase):
    def fixture(self) -> dict:
        return {
            "schema_version": "structured-extraction-v1",
            "objects": [
                {"id": "Cat_1", "label": "Cats", "confidence": 0.9},
                {"id": "BOX", "label": "Boxes", "confidence": None},
            ],
            "attributes": [
                {"subject": "Cat_1", "name": "Colour", "value": "Scarlet", "confidence": 0.8},
                {"subject": "Cat_1", "name": "size", "value": "small", "confidence": 0.1},
            ],
            "counts": [{"object_id": "Cat_1", "value": 2, "confidence": 1.0}],
            "actions": [{"subject": "Cat_1", "verb": "Carrying", "object": "BOX", "confidence": 0.7}],
            "relations": [{"subject": "BOX", "predicate": "right_of", "object": "Cat_1", "confidence": 1.0}],
            "scenes": [{"label": "Living Room", "confidence": 0.8}],
            "warnings": ["fixture warning"],
        }

    def test_golden_vector(self) -> None:
        result = canonicalize_extraction(self.fixture())
        self.assertEqual(result.scheme_version, CANONICAL_SCHEME_VERSION)
        self.assertEqual(
            result.atoms,
            (
                "action:cat:carrying:box",
                "attribute:cat:color:red",
                "count:cat:2",
                "object:box",
                "object:cat",
                "relation:cat:left_of:box",
                "scene:living_room",
            ),
        )
        self.assertIn("low_confidence_attribute_dropped", result.warnings)

    def test_idempotent_and_order_invariant(self) -> None:
        left = self.fixture()
        right = dict(left)
        right["objects"] = list(reversed(left["objects"]))
        right["attributes"] = list(reversed(left["attributes"])) + [left["attributes"][0]]
        self.assertEqual(canonicalize_extraction(left), canonicalize_extraction(right))

    def test_label_atoms_use_same_scheme(self) -> None:
        result = canonicalize_label_atoms(
            [
                {"type": "object", "id": "cat", "value": "cats"},
                {"type": "object", "id": "mat", "value": "mat"},
                {"type": "relation", "subject": "cat", "value": "on", "object": "mat"},
            ]
        )
        self.assertEqual(result.atoms, ("object:cat", "object:mat", "relation:cat:on:mat"))

    def test_version_mismatch_fails_closed(self) -> None:
        value = self.fixture()
        value["schema_version"] = "future-v2"
        with self.assertRaises(CanonicalizationError):
            canonicalize_extraction(value)

    def test_empty_and_low_confidence_handling(self) -> None:
        value = self.fixture()
        value["objects"] = [{"id": "cat", "label": "cat", "confidence": 0.01}]
        for key in ("attributes", "counts", "actions", "relations", "scenes"):
            value[key] = []
        result = canonicalize_extraction(value)
        self.assertEqual(result.atoms, ())
        self.assertIn("empty_representation", result.warnings)


class RepresentationTests(unittest.TestCase):
    def test_structured_set_and_version_guard(self) -> None:
        result = canonicalize_label_atoms([{"type": "object", "id": "cat", "value": "cat"}])
        value = StructuredSet.from_result(result)
        self.assertEqual(value.jaccard(value), 1.0)
        with self.assertRaises(CanonicalizationError):
            value.jaccard(StructuredSet("future-v2", frozenset(value.atoms)))

    def test_weights_are_training_document_idf(self) -> None:
        weights = fit_idf_weights([{"object:cat", "scene:kitchen"}, {"object:cat"}], weights_version="train-v1")
        self.assertGreater(weights["scene:kitchen"], weights["object:cat"])
        left = WeightedStructuredSet(CANONICAL_SCHEME_VERSION, frozenset({"object:cat"}), weights, "train-v1")
        self.assertEqual(left.overlap(left), 1.0)

    def test_controlled_text_is_deterministic(self) -> None:
        text = "Exactly two red cats carrying a wooden box to the left of a chair in a living room."
        first = extract_controlled_text(text, object_lexicon=["cat", "box", "chair"])
        second = extract_controlled_text(text, object_lexicon=["chair", "box", "cat"])
        self.assertEqual(first, second)
        atoms = canonicalize_extraction(first, minimum_confidence=0).atoms
        self.assertIn("attribute:cat:color:red", atoms)
        self.assertIn("count:cat:2", atoms)
        self.assertIn("action:cat:carry:box", atoms)
        self.assertIn("relation:cat:left_of:chair", atoms)
        self.assertIn("scene:living_room", atoms)


if __name__ == "__main__":
    unittest.main()
