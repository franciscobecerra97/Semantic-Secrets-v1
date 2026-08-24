from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

import numpy as np

from experiments.datasets.author_pilot_catalog import author_catalog, blind_audit, canonical_bytes
from experiments.datasets.split_manifest import validate_outputs
from experiments.plaintext_matching import run_p6


class P6PilotContractTests(unittest.TestCase):
    def test_pilot_catalog_reauthors_identically_and_passes_audit(self) -> None:
        catalog = blind_audit(author_catalog()).pop("catalog")
        saved = json.loads(
            (run_p6.REPO_ROOT / "experiments" / "datasets" / "concepts" / "pilot_v1.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(catalog, saved)
        self.assertEqual(hashlib.sha256(canonical_bytes(catalog)).hexdigest(), "adfd9bf03953353ea2a9f07e5f2d4c2165d0e5ba6637fd1169a267bec37016dd")

    def test_pilot_manifests_are_deterministic_and_split_safe(self) -> None:
        report = validate_outputs(
            "pilot",
            design_path=run_p6.REPO_ROOT / "experiments" / "datasets" / "config" / "design_p6_v1.json",
        )
        self.assertTrue(report["deterministic"])
        self.assertFalse(report["cross_split_family_leakage"])
        self.assertEqual(report["families_by_split"], {"train": 36, "validation": 12, "test": 12})

    def test_saved_run_fails_closed_and_contains_no_test_rows(self) -> None:
        config = run_p6.read_json(run_p6.CONFIG)
        run_p6.validate_saved(config)
        result = run_p6.read_json(run_p6.FINAL_RESULT)
        self.assertFalse(result["gate_a"]["pass"])
        self.assertFalse(result["gate_a"]["protocol_engineering_allowed"])
        self.assertEqual(result["boundaries"]["pilot_test_rows_evaluated"], 0)
        self.assertEqual(np.load(run_p6.WEIGHTED_MATRIX, allow_pickle=False).shape, (192, 192))


if __name__ == "__main__":
    unittest.main()
