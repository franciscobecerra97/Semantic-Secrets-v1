from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE_PREREG = ROOT / "experiments" / "v3" / "config" / "preregistration_v3.json"
BASE_OBSERVATION = ROOT / "experiments" / "v3" / "config" / "visual_observation_v3.json"
PREREG = ROOT / "experiments" / "v3" / "config" / "preregistration_v3_1.json"
OBSERVATION = ROOT / "experiments" / "v3" / "config" / "visual_observation_v3_1.json"


class V31PreregistrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base_prereg = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
        self.base_observation = json.loads(BASE_OBSERVATION.read_text(encoding="utf-8"))
        self.prereg = json.loads(PREREG.read_text(encoding="utf-8"))
        self.observation = json.loads(OBSERVATION.read_text(encoding="utf-8"))

    def test_v30_history_is_explicit_and_v31_versions_match(self) -> None:
        self.assertEqual(self.base_prereg["$schema_version"], "semantic-secrets-preregistration-v3.0.0")
        self.assertEqual(self.base_observation["$schema_version"], "visual-observation-v3.0.0")
        self.assertEqual(self.prereg["amends"]["base_commit"], "8e44caa71ae724e032822b40a1af4e4dc8190d31")
        self.assertEqual(self.prereg["versions"]["observation"], self.observation["$schema_version"])

    def test_exactly_two_final_pipelines_and_egtr_replaces_sgtr(self) -> None:
        planned = self.prereg["candidate_shortlist"]["pipelines"]
        configured = [item["pipeline_id"] for item in self.observation["pipelines"]]
        self.assertEqual(planned, configured)
        self.assertEqual(len(planned), 2)
        self.assertEqual(planned, ["v3.1-gdino-siglip2", "v3.1-egtr-siglip2"])
        self.assertNotIn("v3-sgtr-siglip2", planned)

    def test_machine_capacity_is_not_the_resource_gate(self) -> None:
        compute = self.prereg["compute"]
        self.assertFalse(compute["gpu_capacity_is_gate"])
        self.assertTrue(compute["larger_machine_does_not_raise_limits"])
        self.assertEqual(compute["pipeline_peak_vram_gib_max"], 24)
        self.assertEqual(compute["pipeline_peak_rss_gib_max"], 32)

    def test_primary_support_is_feasible_and_exploratory_types_fail_closed(self) -> None:
        support = self.prereg["dataset_support"]
        plan = support["validation_plan_each_stratum"]
        self.assertEqual(set(plan), set(self.base_prereg["perception_metrics"]["reported_by_atom_type"]))
        for atom_type in support["primary_gate_types"]:
            self.assertGreaterEqual(plan[atom_type]["positive"], support["minimum_positive_opportunities_per_type_per_stratum"])
            self.assertGreaterEqual(plan[atom_type]["negative"], support["minimum_applicable_negative_opportunities_per_type_per_stratum"])
            self.assertTrue(plan[atom_type]["gate_evaluable"])
        for atom_type, item in plan.items():
            if atom_type not in support["primary_gate_types"]:
                self.assertFalse(item["gate_evaluable"])
        self.assertEqual(support["insufficient_support_status"], "not_gate_evaluable")

    def test_gate_language_and_compiler_invariants_are_not_weakened(self) -> None:
        minimum = self.prereg["gate_v3_a1"]["minimum_eligible_language"]
        self.assertEqual(minimum, self.base_prereg["gate_v3_a1"]["minimum_eligible_language"])
        self.assertGreaterEqual(self.base_prereg["compiler_tests"]["minimum_cases"], 320)
        self.assertEqual(sum(self.base_prereg["compiler_tests"]["case_counts"].values()), 320)
        self.assertFalse(self.prereg["gate_v3_a1"]["cross_pipeline_union"])

    def test_annotation_and_execution_remain_blocked(self) -> None:
        self.assertEqual(self.prereg["annotation"]["status"], "unresolved execution blocker")
        self.assertFalse(self.prereg["annotation"]["model_assisted_ground_truth"])
        self.assertFalse(self.prereg["execution_boundary"]["authorized_by_this_amendment"])
        for forbidden in ("model weight acquisition", "capability image creation or generation", "perception inference", "P9-v3B", "P9-v3C", "P10"):
            self.assertIn(forbidden, self.prereg["execution_boundary"]["forbidden_now"])

    def test_pipeline_freeze_fields_are_complete(self) -> None:
        required = {"adapter", "components", "acquisition_hash_rule", "threshold_fit", "resource_envelope", "failure_behavior"}
        for pipeline in self.observation["pipelines"]:
            self.assertTrue(required.issubset(pipeline))
        egtr = self.observation["pipelines"][1]
        self.assertEqual(egtr["components"][0]["revision"], "7f87450f32758ed8583948847a8186f2ee8b21e3")
        self.assertIn("pred_rel", egtr["adapter"]["tensor_inputs"])
        self.assertIn("pred_connectivity", egtr["adapter"]["tensor_inputs"])


if __name__ == "__main__":
    unittest.main()
