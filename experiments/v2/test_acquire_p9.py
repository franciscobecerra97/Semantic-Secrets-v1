from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.v2.acquire_p9 import static_remote_code_review


class AcquisitionTests(unittest.TestCase):
    def test_static_review_allows_plain_model_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "modeling.py"
            path.write_text("def forward(x):\n    return x\n", encoding="utf-8")
            report = static_remote_code_review(Path(tmp))
            self.assertTrue(report["approved"])
            self.assertEqual(len(report["python_files"]), 1)

    def test_static_review_blocks_execution_and_network_imports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "modeling.py"
            path.write_text("import requests\nimport subprocess\n", encoding="utf-8")
            report = static_remote_code_review(Path(tmp))
            self.assertFalse(report["approved"])

    def test_static_review_records_narrowly_allowed_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lora.py"
            path.write_text("from urllib.request import urlopen\n", encoding="utf-8")
            report = static_remote_code_review(Path(tmp), {("lora.py", "network_access")})
            self.assertTrue(report["approved"])
            self.assertEqual(len(report["findings"]), 1)
            self.assertEqual(report["blocking_findings"], [])


if __name__ == "__main__":
    unittest.main()
