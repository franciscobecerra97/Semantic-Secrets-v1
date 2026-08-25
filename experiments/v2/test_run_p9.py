from __future__ import annotations

import unittest

from experiments.v2 import author_p9, run_p9


class P9RunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = run_p9.read_json(run_p9.GRAPH_PATH)

    def test_schema_normalises_inverse_relation(self) -> None:
        graph = author_p9.scenario(8)
        clean = run_p9.normalise_graph(graph, self.config)
        self.assertTrue(all(edge["type"] != "right_of" for edge in clean["binary"]))

    def test_schema_rejects_count_contradiction(self) -> None:
        graph = author_p9.scenario(0)
        graph["counts"][0]["bucket"] = "4"
        with self.assertRaisesRegex(ValueError, "contradiction"):
            run_p9.normalise_graph(graph, self.config)

    def test_canonicalisation_ignores_instance_ids(self) -> None:
        first = run_p9.normalise_graph(author_p9.scenario(2), self.config)
        second = run_p9.normalise_graph(author_p9.scenario(2), self.config)
        replacement = {node["id"]: f"renamed{index}" for index, node in enumerate(second["nodes"])}
        for node in second["nodes"]:
            node["id"] = replacement[node["id"]]
        for item in second["unary"]:
            item["node"] = replacement[item["node"]]
        for item in second["binary"]:
            item["source"], item["target"] = replacement[item["source"]], replacement[item["target"]]
        self.assertEqual(run_p9.canonical_graph(first), run_p9.canonical_graph(second))

    def test_perfect_capability_score(self) -> None:
        ground = author_p9.scenario(4)
        predicted = run_p9.normalise_graph(ground, self.config)
        score = run_p9.score_image(ground, predicted, self.config)
        metrics = run_p9.aggregate([score])
        self.assertEqual(metrics["macro"]["f1"], 1.0)

    def test_json_answer_parser_handles_fence(self) -> None:
        self.assertEqual(run_p9.parse_json_answer("```json\n{\"nodes\": []}\n```"), {"nodes": []})

    def test_futility_math_requires_one_invalid_validation_item(self) -> None:
        total = 32
        threshold = 0.98
        self.assertEqual(total / total, 1.0)
        self.assertLess((total - 1) / total, threshold)


if __name__ == "__main__":
    unittest.main()
