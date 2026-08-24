from __future__ import annotations

import math
import unittest

from prototype.semantic_secrets.matching import (
    cardinality_score,
    cosine_score,
    jaccard_score,
    select_threshold,
    threshold_decision,
    weighted_overlap_score,
)


class PlaintextMatcherTests(unittest.TestCase):
    def test_hand_computed_set_scores(self) -> None:
        left = {"a", "b", "c"}
        right = {"b", "c", "d"}
        self.assertEqual(cardinality_score(left, right), 2)
        self.assertAlmostEqual(jaccard_score(left, right), 0.5)
        self.assertAlmostEqual(
            weighted_overlap_score(left, right, {"a": 4.0, "b": 2.0, "c": 1.0}),
            3 / 7,
        )

    def test_empty_set_boundaries(self) -> None:
        self.assertEqual(jaccard_score([], []), 1.0)
        self.assertEqual(weighted_overlap_score([], [], {}), 1.0)
        self.assertEqual(weighted_overlap_score([], ["x"], {}), 0.0)

    def test_cosine_vectors(self) -> None:
        self.assertAlmostEqual(cosine_score([1, 0], [1, 0]), 1.0)
        self.assertAlmostEqual(cosine_score([1, 0], [0, 1]), 0.0)
        self.assertAlmostEqual(cosine_score([1, 0], [-1, 0]), -1.0)
        with self.assertRaises(ValueError):
            cosine_score([0, 0], [1, 0])
        with self.assertRaises(ValueError):
            cosine_score([math.nan], [1])

    def test_threshold_is_inclusive(self) -> None:
        decision = threshold_decision(0.8, [0.8, 0.9], [0.8, 0.7], [0.1])
        self.assertEqual(decision.false_reject_rate, 0.0)
        self.assertEqual(decision.near_false_accept_rate, 0.5)

    def test_threshold_selection_is_deterministic_and_strict_on_tie(self) -> None:
        first = select_threshold([0.9, 1.0], [0.7, 0.8], [0.0, 0.1])
        second = select_threshold([0.9, 1.0], [0.7, 0.8], [0.0, 0.1])
        self.assertEqual(first, second)
        self.assertEqual(first.threshold, 0.9)
        self.assertEqual(first.objective[0], 0.0)


if __name__ == "__main__":
    unittest.main()
