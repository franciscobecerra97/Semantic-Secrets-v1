from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from experiments.datasets import split_manifest


class DatasetDesignTests(unittest.TestCase):
    def test_smoke_catalog_and_outputs_validate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            provenance = split_manifest.generate("smoke", output)
            report = split_manifest.validate_outputs("smoke", output)
        self.assertEqual(provenance["counts"]["families"], 12)
        self.assertEqual(provenance["counts"]["image_inputs"], 84)
        self.assertEqual(report["families_by_split"], {"test": 3, "train": 6, "validation": 3})
        self.assertTrue(report["label_separation"])
        self.assertFalse(report["cross_split_family_leakage"])

    def test_recreation_is_byte_identical(self) -> None:
        split_manifest.deterministic_recreation_check("smoke")

    def test_full_and_pilot_fail_closed(self) -> None:
        for stage in ("pilot", "full"):
            with self.subTest(stage=stage), self.assertRaises(split_manifest.DesignError):
                split_manifest.load_stage(stage)

    def test_public_source_registry_is_complete_and_conservative(self) -> None:
        registry_path = Path(split_manifest.ROOT) / "sources_v1.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        required = {
            "source_id",
            "name",
            "kind",
            "authoritative_url",
            "licence",
            "revision_policy",
            "identifiers_present",
            "harmful_content_risk",
            "intended_use",
            "distribution_limit",
            "p3_status",
            "acquisition",
        }
        self.assertGreaterEqual(len(registry["sources"]), 3)
        for source in registry["sources"]:
            self.assertFalse(required - set(source), source["source_id"])
        status = {source["source_id"]: source["p3_status"] for source in registry["sources"]}
        self.assertEqual(status["pickapic_v2"], "deferred-not-approved")
        diffusion = next(source for source in registry["sources"] if source["source_id"] == "diffusiondb")
        self.assertTrue(diffusion["identifiers_present"])
        self.assertIn("user_name", diffusion["identifier_fields_to_drop"])


if __name__ == "__main__":
    unittest.main()
