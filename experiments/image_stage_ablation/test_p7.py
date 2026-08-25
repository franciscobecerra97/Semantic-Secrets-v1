from __future__ import annotations

import unittest

from prototype.semantic_secrets.matching import select_threshold

from experiments.image_stage_ablation.run_p7 import (
    RESULT,
    auc,
    load_config,
    read_json,
    validate_saved,
    verify_sources,
)


class P7ContractTests(unittest.TestCase):
    def test_auc_ties_are_half_credit(self) -> None:
        self.assertEqual(auc([1.0, 0.5], [0.5, 0.0]), 0.875)

    def test_threshold_rule_is_inclusive_and_minimax(self) -> None:
        selected = select_threshold([0.9, 0.8], [0.8, 0.2], [0.1, 0.0])
        # The 0.8 and 0.9 candidates tie on worst/total error; the frozen
        # rule then prefers less accepted-negative mass and the stricter 0.9.
        self.assertEqual(selected.threshold, 0.9)
        self.assertEqual(selected.false_reject_rate, 0.5)
        self.assertEqual(selected.near_false_accept_rate, 0.0)

    def test_frozen_sources(self) -> None:
        config = load_config()
        verify_sources(config)
        self.assertFalse(config["execution_boundary"]["new_model_execution"])
        self.assertFalse(config["execution_boundary"]["p6_artifact_access"])

    def test_saved_result_contract(self) -> None:
        if not RESULT.exists():
            self.skipTest("P7 result has not been generated")
        validate_saved()
        result = read_json(RESULT)
        self.assertEqual(result["boundaries"]["test_rows_evaluated"], 0)
        self.assertEqual(result["boundaries"]["human_participants"], 0)
        self.assertFalse(result["semantic_policy"]["implemented_or_tuned"])


if __name__ == "__main__":
    unittest.main()
