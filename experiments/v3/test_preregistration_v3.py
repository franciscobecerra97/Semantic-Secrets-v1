from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments" / "v3" / "config" / "preregistration_v3.json"
OBSERVATION = ROOT / "experiments" / "v3" / "config" / "visual_observation_v3.json"


class V3PreregistrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.prereg = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.observation = json.loads(OBSERVATION.read_text(encoding="utf-8"))

    def test_versions_and_pipeline_shortlist_match(self) -> None:
        self.assertEqual(self.prereg["versions"]["observation"], self.observation["$schema_version"])
        planned = self.prereg["candidate_shortlist"]["pipelines"]
        configured = [item["pipeline_id"] for item in self.observation["pipelines"]]
        self.assertEqual(planned, configured)
        self.assertLessEqual(len(planned), 2)

    def test_dataset_totals_and_family_isolation(self) -> None:
        strata = self.prereg["dataset"]["strata"].values()
        self.assertEqual(sum(item["images"] for item in strata), self.prereg["dataset"]["total_images"])
        self.assertEqual(sum(item["development_families"] * item["images_per_family"] for item in strata), self.prereg["dataset"]["development_images"])
        self.assertEqual(sum(item["validation_families"] * item["images_per_family"] for item in strata), self.prereg["dataset"]["validation_images"])
        self.assertEqual(self.prereg["dataset"]["split_unit"], "semantic scenario family")

    def test_compiler_case_count_is_exact(self) -> None:
        tests = self.prereg["compiler_tests"]
        self.assertEqual(sum(tests["case_counts"].values()), tests["minimum_cases"])
        self.assertEqual(tests["required_pass_rates"]["valid_result_schema"], 1.0)
        self.assertEqual(tests["required_pass_rates"]["malformed_json_outputs"], 0.0)

    def test_policy_and_execution_boundaries_remain_closed(self) -> None:
        self.assertFalse(self.prereg["policy_boundary"]["implementation_now"])
        self.assertFalse(self.prereg["policy_boundary"]["tuning_now"])
        self.assertTrue(self.prereg["policy_boundary"]["p10_blocked"])
        self.assertIn("P9-v3B", self.prereg["execution_boundary"]["forbidden_now"])
        self.assertIn("P10", self.prereg["execution_boundary"]["forbidden_now"])

    def test_confidence_is_component_local(self) -> None:
        contract = self.observation["confidence_contract"]
        self.assertFalse(contract["cross_component_comparison"])
        self.assertFalse(contract["calibrated_probability_claim"])
        canonical = self.observation["observation_canonicalisation"]
        self.assertIn("elapsed_seconds", canonical["exclude_from_repeat_equality"])
        self.assertEqual(canonical["confidence_round_decimal_places"], 6)


if __name__ == "__main__":
    unittest.main()
