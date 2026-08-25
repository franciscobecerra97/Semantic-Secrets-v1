from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.v2 import author_p9


class P9AuthoringTests(unittest.TestCase):
    def test_scenarios_are_well_formed_and_balanced(self) -> None:
        graph_config = author_p9.read_json(author_p9.GRAPH_CONFIG)
        categories = set(graph_config["entity_categories"])
        actions = set(graph_config["unary_actions"] + graph_config["binary_actions"])
        relations = set(graph_config["spatial_relations"])
        for index in range(96):
            graph = author_p9.scenario(index)
            self.assertGreaterEqual(len(graph["nodes"]), 2)
            ids = [node["id"] for node in graph["nodes"]]
            self.assertEqual(len(ids), len(set(ids)))
            self.assertTrue(all(node["category"] in categories for node in graph["nodes"]))
            self.assertTrue(all(edge["type"] in actions | relations for edge in graph["binary"]))
            self.assertTrue(graph["unary"] or graph["binary"])
            self.assertTrue(graph["counts"])

    def test_render_is_deterministic(self) -> None:
        spec = {"fixture_style": "synthetic_raster", "seed": 123, "graph": author_p9.scenario(9)}
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.png"
            second = Path(tmp) / "second.png"
            author_p9.render_fixture(spec, first, 192)
            author_p9.render_fixture(spec, second, 192)
            self.assertEqual(author_p9.stable_hash(first), author_p9.stable_hash(second))

    def test_authoring_respects_frozen_counts_without_v1_reads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(author_p9, "MANIFEST_DIR", root / "manifests"), patch.object(author_p9, "IMAGE_DIR", root / "images"):
                audit = author_p9.author_capability()
                self.assertEqual(audit["record_count"], 96)
                self.assertEqual(audit["split_counts"], {"development": 64, "validation": 32})
                self.assertEqual(audit["style_counts"], {"procedural_composite": 48, "synthetic_raster": 48})
                self.assertEqual(audit["unique_image_hashes"], 96)
                self.assertTrue(audit["all_image_hashes_unique"])
                self.assertFalse(audit["v1_sources_accessed"])
                self.assertTrue(all(count >= 12 for count in audit["task_positive_counts_validation"].values()))
                self.assertTrue(all(count >= 12 for count in audit["task_applicable_negative_counts_validation"].values()))
                records = [json.loads(line) for line in (root / "manifests" / "capability_v2.jsonl").read_text(encoding="utf-8").splitlines()]
                self.assertEqual(len(records), 96)


if __name__ == "__main__":
    unittest.main()
