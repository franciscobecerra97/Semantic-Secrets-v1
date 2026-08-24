from __future__ import annotations

import json
import unittest
from pathlib import Path

from experiments.model_screening import run_screen


class ScreeningContractTests(unittest.TestCase):
    def test_structured_schema_accepts_controlled_parser(self) -> None:
        config = run_screen.read_json(run_screen.CONFIG_PATH)
        schema_path = run_screen.resolve_config_path(config["structured_schema"])
        output = run_screen.controlled_text_extract("A red cat is left of a blue book in a library.")
        run_screen.validate_structure(output, schema_path)

    def test_controlled_parser_repeats(self) -> None:
        config = run_screen.read_json(run_screen.CONFIG_PATH)
        schema_path = run_screen.resolve_config_path(config["structured_schema"])
        report = run_screen.screen_controlled_text(config["structured_text"], schema_path)
        self.assertTrue(report["fixed_input_repeat_equal"])
        self.assertEqual(report["schema_failures"], 0)

    def test_model_manifest_has_pinned_revisions_or_no_model(self) -> None:
        manifest = json.loads((run_screen.SCREEN_ROOT / "model_manifest.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(manifest["models"]), 7)
        for model in manifest["models"]:
            if model["model_id"] is not None:
                self.assertRegex(model["hub_revision"], r"^[0-9a-f]{40}$")
                self.assertTrue(model["licence"])
                self.assertTrue(model["acquisition"])

    def test_saved_report_if_present(self) -> None:
        if run_screen.DEFAULT_OUTPUT.exists():
            report = run_screen.read_json(run_screen.DEFAULT_OUTPUT)
            run_screen.validate_report(report)


if __name__ == "__main__":
    unittest.main()
