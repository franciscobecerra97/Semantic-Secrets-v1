from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "prototype"))

from experiments.representation_screen.run_p5 import (  # noqa: E402
    FINAL_RESULT,
    build_pairs,
    load_config,
    read_json,
    selected_rows,
    validate_saved,
)


class P5ContractTests(unittest.TestCase):
    def test_selection_keeps_test_sealed(self) -> None:
        rows = selected_rows(load_config())
        self.assertEqual(len(rows), 27)
        self.assertEqual(len({row["label"]["family_id"] for row in rows}), 9)
        self.assertEqual({row["label"]["split"] for row in rows}, {"train", "validation"})
        self.assertEqual(len(build_pairs(rows)), 27)

    def test_weighting_is_training_only(self) -> None:
        config = load_config()
        self.assertEqual(config["weighting"]["fit_split"], "train")
        self.assertIs(config["weighting"]["validation_or_test_labels_used"], False)

    def test_saved_result_contract(self) -> None:
        if not FINAL_RESULT.exists():
            self.skipTest("P5 result has not been generated")
        validate_saved()
        result = read_json(FINAL_RESULT)
        real = {
            name: value
            for name, value in result["representations"].items()
            if not name.startswith("oracle_")
        }
        self.assertTrue(real)
        self.assertFalse(any(value["uncertainty_supports_positive_separation"] for value in real.values()))
        self.assertTrue(result["representations"]["oracle_structured"]["uncertainty_supports_positive_separation"])

    def test_structured_rows_exclude_test(self) -> None:
        path = ROOT / "results" / "p5" / "structured_v1.jsonl"
        if not path.exists():
            self.skipTest("P5 structured output has not been generated")
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
        self.assertEqual(len(rows), 27)
        self.assertNotIn("test", {row["split"] for row in rows})


if __name__ == "__main__":
    unittest.main()
