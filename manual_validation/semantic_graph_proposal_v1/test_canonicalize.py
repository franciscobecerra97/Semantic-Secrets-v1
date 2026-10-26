"""Synthetic compiler invariants only: these tests do not measure VLM accuracy."""

import copy
import itertools
import json
from pathlib import Path
import tempfile
import unittest

from canonicalize import Canonicalizer, DEFAULT_VOCABULARY, parse_json


HERE = Path(__file__).parent


class CanonicalizerTests(unittest.TestCase):
    def setUp(self):
        self.compiler = Canonicalizer()
        self.example = json.loads((HERE / "example.json").read_text(encoding="utf-8"))

    def compile(self, document):
        result = self.compiler.canonicalize(json.dumps(document))
        self.assertEqual(result["status"], "ok", result)
        return result

    def fingerprint(self, document):
        return self.compile(document)["fingerprint_sha256"]

    def fails(self, document, code):
        result = self.compiler.canonicalize(json.dumps(document))
        self.assertEqual(result.get("code"), code, result)
        self.assertNotIn("fingerprint_sha256", result)

    def test_approved_synonyms_and_different_ids_produce_identical_bytes(self):
        second = json.loads((HERE / "example_synonyms.json").read_text(encoding="utf-8"))
        self.assertEqual(self.compile(self.example), self.compile(second))

    def test_all_object_and_fact_orderings_are_invariant(self):
        expected = self.fingerprint(self.example)
        for objects in itertools.permutations(self.example["objects"]):
            for facts in itertools.permutations(self.example["facts"]):
                changed = {**self.example, "objects": list(objects), "facts": list(facts)}
                self.assertEqual(expected, self.fingerprint(changed))

    def test_indistinguishable_labels_with_different_roles_are_canonical(self):
        graph = {
            "objects": [{"id": "a", "label": "cat", "color": "red"},
                        {"id": "b", "label": "cat", "color": "red"},
                        {"id": "c", "label": "sofa", "color": "blue"}],
            "facts": [{"subject": "a", "predicate": "sleeping", "object": None},
                      {"subject": "b", "predicate": "sitting", "object": None},
                      {"subject": "a", "predicate": "on", "object": "c"}],
            "scene": None,
        }
        expected = self.fingerprint(graph)
        for replacements in itertools.permutations(["x", "y", "z"]):
            mapping = dict(zip(["a", "b", "c"], replacements))
            changed = copy.deepcopy(graph)
            for node in changed["objects"]:
                node["id"] = mapping[node["id"]]
            for fact in changed["facts"]:
                fact["subject"] = mapping[fact["subject"]]
                if fact["object"] is not None:
                    fact["object"] = mapping[fact["object"]]
            for objects in itertools.permutations(changed["objects"]):
                self.assertEqual(expected, self.fingerprint({**changed, "objects": list(objects)}))

    def test_disconnected_objects_are_preserved(self):
        first = copy.deepcopy(self.example)
        first["facts"] = first["facts"][:1]
        second = copy.deepcopy(first)
        second["objects"] = second["objects"][:2]
        self.assertNotEqual(self.fingerprint(first), self.fingerprint(second))

    def test_distinct_objects_are_not_merged(self):
        changed = copy.deepcopy(self.example)
        changed["objects"].append({"id": "cat2", "label": "cat", "color": "red"})
        self.assertNotEqual(self.fingerprint(self.example), self.fingerprint(changed))
        self.assertEqual(len(self.compile(changed)["graph"]["objects"]), 4)

    def test_color_binding_and_color_changes_matter(self):
        changed = copy.deepcopy(self.example)
        changed["objects"][0]["color"], changed["objects"][2]["color"] = "yellow", "red"
        self.assertNotEqual(self.fingerprint(self.example), self.fingerprint(changed))

    def test_missing_color_is_not_a_wildcard(self):
        changed = copy.deepcopy(self.example)
        changed["objects"][0]["color"] = None
        self.assertNotEqual(self.fingerprint(self.example), self.fingerprint(changed))

    def test_scene_disagreement_is_preserved(self):
        changed = {**self.example, "scene": "living room"}
        self.assertNotEqual(self.fingerprint(self.example), self.fingerprint(changed))

    def test_broad_scene_is_not_silently_equal_to_specific_scene(self):
        changed = {**self.example, "scene": "indoor"}
        self.assertNotEqual(self.fingerprint(self.example), self.fingerprint(changed))

    def test_book_and_notebook_are_different(self):
        changed = copy.deepcopy(self.example)
        changed["objects"][2]["label"] = "notebook"
        self.assertNotEqual(self.fingerprint(self.example), self.fingerprint(changed))

    def test_directed_relations_preserve_participants(self):
        changed = copy.deepcopy(self.example)
        changed["facts"][1]["subject"], changed["facts"][1]["object"] = "sofa1", "cat1"
        self.assertNotEqual(self.fingerprint(self.example), self.fingerprint(changed))

    def test_identical_repeated_facts_are_deduplicated(self):
        changed = copy.deepcopy(self.example)
        changed["facts"].append(copy.deepcopy(changed["facts"][0]))
        self.assertEqual(self.fingerprint(self.example), self.fingerprint(changed))

    def test_explicit_inverse_predicate_is_normalized(self):
        first = copy.deepcopy(self.example)
        first["facts"][1]["predicate"] = "inside"
        second = copy.deepcopy(first)
        second["facts"][1] = {"subject": "sofa1", "predicate": "contains", "object": "cat1"}
        self.assertEqual(self.fingerprint(first), self.fingerprint(second))

    def test_symmetric_relation_is_normalized(self):
        first = copy.deepcopy(self.example)
        first["facts"][1]["predicate"] = "touching"
        second = copy.deepcopy(first)
        second["facts"][1]["subject"], second["facts"][1]["object"] = "sofa1", "cat1"
        self.assertEqual(self.fingerprint(first), self.fingerprint(second))

    def test_case_spacing_and_color_aliases(self):
        first = copy.deepcopy(self.example)
        first["objects"][0]["color"] = "gray"
        second = copy.deepcopy(first)
        second["objects"][0]["label"] = "  DOMESTIC-CAT  "
        second["objects"][0]["color"] = " GREY "
        self.assertEqual(self.fingerprint(first), self.fingerprint(second))

    def test_typo_and_ambiguous_category_are_not_guessed(self):
        for label in ("felim", "feline", "bike"):
            with self.subTest(label=label):
                changed = copy.deepcopy(self.example)
                changed["objects"][0]["label"] = label
                self.fails(changed, "UNKNOWN_LABEL")

    def test_non_equivalent_predicates_are_not_invented(self):
        for predicate in ("staying", "under", "above", "carrying"):
            with self.subTest(predicate=predicate):
                changed = copy.deepcopy(self.example)
                changed["facts"][1]["predicate"] = predicate
                self.fails(changed, "UNKNOWN_LABEL")

    def test_cross_type_aliases_are_rejected(self):
        changed = copy.deepcopy(self.example)
        changed["objects"][0]["label"] = "red"
        self.fails(changed, "UNKNOWN_LABEL")

    def test_extra_keys_are_rejected(self):
        changed = {**self.example, "confidence": 0.99}
        self.fails(changed, "INVALID_SCHEMA")

    def test_duplicate_object_ids_are_rejected(self):
        changed = copy.deepcopy(self.example)
        changed["objects"][1]["id"] = "cat1"
        self.fails(changed, "DUPLICATE_ID")

    def test_dangling_references_are_rejected(self):
        changed = copy.deepcopy(self.example)
        changed["facts"][0]["subject"] = "absent"
        self.fails(changed, "DANGLING_REFERENCE")

    def test_wrong_predicate_arities_are_rejected(self):
        changed = copy.deepcopy(self.example)
        changed["facts"][0]["object"] = "sofa1"
        self.fails(changed, "INVALID_ARITY")
        changed = copy.deepcopy(self.example)
        changed["facts"][1]["object"] = None
        self.fails(changed, "INVALID_ARITY")

    def test_self_relations_are_rejected(self):
        changed = copy.deepcopy(self.example)
        changed["facts"][1]["object"] = "cat1"
        self.fails(changed, "SELF_RELATION")

    def test_limits_are_enforced_without_silent_truncation(self):
        changed = copy.deepcopy(self.example)
        changed["objects"] *= 2
        self.fails(changed, "LIMIT_EXCEEDED")
        changed = copy.deepcopy(self.example)
        changed["facts"] *= 2
        self.fails(changed, "LIMIT_EXCEEDED")

    def test_empty_graph_produces_no_fingerprint(self):
        self.fails({"objects": [], "facts": [], "scene": None}, "EMPTY_GRAPH")

    def test_person_labels_are_coarse_types_without_demographic_attributes(self):
        first = {"objects": [{"id": "p", "label": "man", "color": None}],
                 "facts": [], "scene": None}
        second = copy.deepcopy(first)
        second["objects"][0]["label"] = "human"
        self.assertEqual(self.fingerprint(first), self.fingerprint(second))
        second["objects"][0]["color"] = "red"
        self.fails(second, "INVALID_COLOR")

    def test_malformed_json_and_duplicate_json_keys_fail_closed(self):
        for raw in ('{"objects":', '{"objects":[],"objects":[],"facts":[],"scene":null}',
                    '\ud800',
                    '```json\n{}\n```', '{"objects":[],"facts":[],"scene":NaN}'):
            with self.subTest(raw=raw):
                result = self.compiler.canonicalize(raw)
                self.assertEqual(result["status"], "failure")
                self.assertNotIn("fingerprint_sha256", result)

    def test_five_nodes_are_supported(self):
        changed = copy.deepcopy(self.example)
        changed["objects"].extend([
            {"id": "a", "label": "cat", "color": "red"},
            {"id": "b", "label": "cup", "color": None},
        ])
        first = self.compile(changed)
        self.assertEqual(len(first["graph"]["objects"]), 5)
        for order in itertools.permutations(changed["objects"]):
            self.assertEqual(first, self.compile({**changed, "objects": list(order)}))

    def test_prompt_lists_all_canonical_model_labels(self):
        vocabulary = parse_json(DEFAULT_VOCABULARY.read_text(encoding="utf-8"))
        lines = (HERE / "extraction_prompt.txt").read_text(encoding="utf-8").splitlines()
        prefixes = {"Objects: ": set(vocabulary["objects"]),
                    "Colors: ": set(vocabulary["colors"]),
                    "Predicates with object=null: ": set(vocabulary["unary_predicates"]),
                    "Predicates requiring another object ID: ": set(vocabulary["binary_predicates"]),
                    "Scene: ": set(vocabulary["scenes"])}
        for prefix, expected in prefixes.items():
            line = next(line for line in lines if line.startswith(prefix))
            listed = line[len(prefix):].split(";")[0].rstrip(".").split(", ")
            self.assertEqual(set(listed), expected)

    def test_vocabulary_content_hash_prevents_silent_mapping_changes(self):
        vocabulary = parse_json(DEFAULT_VOCABULARY.read_text(encoding="utf-8"))
        vocabulary["objects"]["cat"].append("house cat")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "vocabulary.json"
            path.write_text(json.dumps(vocabulary), encoding="utf-8")
            changed = Canonicalizer(path).canonicalize(json.dumps(self.example))
            self.assertNotEqual(self.compile(self.example)["fingerprint_sha256"],
                                changed["fingerprint_sha256"])


if __name__ == "__main__":
    unittest.main()
