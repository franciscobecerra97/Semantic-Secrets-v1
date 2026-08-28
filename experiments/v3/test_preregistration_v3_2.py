from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments" / "v3" / "config" / "preregistration_v3.json"
V31 = ROOT / "experiments" / "v3" / "config" / "preregistration_v3_1.json"
V32 = ROOT / "experiments" / "v3" / "config" / "preregistration_v3_2.json"


class V32GroundTruthCorrectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = json.loads(BASE.read_text(encoding="utf-8"))
        self.v31 = json.loads(V31.read_text(encoding="utf-8"))
        self.v32 = json.loads(V32.read_text(encoding="utf-8"))

    def test_only_human_annotation_method_is_superseded(self) -> None:
        self.assertEqual(self.v32["$schema_version"], "semantic-secrets-preregistration-v3.2.0")
        self.assertFalse(self.v32["ground_truth"]["human_participants"])
        self.assertFalse(self.v32["ground_truth"]["human_annotators"])
        self.assertFalse(self.v32["ground_truth"]["derived_from_model_predictions"])
        self.assertTrue(self.v32["execution_boundary"]["smoke_or_formal_inference_requires_ground_truth_freeze"])
        self.assertFalse(self.v32["execution_boundary"]["authorized_by_this_amendment"])

    def test_pipelines_gate_support_and_resources_remain_v31(self) -> None:
        unchanged = set(self.v32["inherited_unchanged"])
        for phrase in (
            "pipelines and model candidates", "model revisions", "support-opportunity counts",
            "metrics and Gate V3-A1 criteria", "hardware and measured-resource limits",
        ):
            self.assertIn(phrase, unchanged)
        self.assertEqual(self.v32["versions"]["observation"], self.v31["versions"]["observation"])
        self.assertEqual(self.v32["versions"]["compiler"], self.v31["versions"]["compiler"])
        self.assertEqual(self.v31["candidate_shortlist"]["pipelines"], ["v3.1-gdino-siglip2", "v3.1-egtr-siglip2"])
        self.assertEqual(self.v31["compute"]["pipeline_peak_vram_gib_max"], 24)
        self.assertEqual(self.v31["dataset_support"]["validation_images_per_stratum"], 60)
        self.assertEqual(self.v31["gate_v3_a1"]["minimum_eligible_language"], self.base["gate_v3_a1"]["minimum_eligible_language"])

    def test_model_blind_freeze_precedes_inference(self) -> None:
        ground_truth = self.v32["ground_truth"]
        self.assertFalse(ground_truth["model_output_access_before_freeze"])
        self.assertIn("before any perception inference", ground_truth["freeze_timing"])
        self.assertFalse(self.v32["execution_boundary"]["model_acquisition_requires_ground_truth_freeze"])


if __name__ == "__main__":
    unittest.main()
