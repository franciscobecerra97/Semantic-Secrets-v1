"""Bounded, offline scene-graph proposal; not the active P9 compiler.

Python 3.10+; standard library only. No model calls or authentication storage.
Local IDs, list order, and approved aliases do not affect the fingerprint.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import re
import sys
import unicodedata


SCHEME = "semantic-graph-proposal-v1"
LIMIT = 5
MAX_INPUT_BYTES = 32_768
DEFAULT_VOCABULARY = Path(__file__).with_name("vocabulary.json")


class GraphError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def compact_json(value: object) -> str:
    """Deterministic encoding for this restricted schema, not general RFC 8785."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def _unique_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise GraphError("DUPLICATE_KEY", f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    raise GraphError("MALFORMED_JSON", f"non-JSON numeric constant: {value}")


def parse_json(raw: str) -> object:
    if not isinstance(raw, str):
        raise GraphError("MALFORMED_JSON", "input must be a JSON string")
    try:
        size = len(raw.encode("utf-8"))
    except UnicodeError as exc:
        raise GraphError("MALFORMED_JSON", "input must be valid Unicode") from exc
    if size > MAX_INPUT_BYTES:
        raise GraphError("INPUT_TOO_LARGE", "input exceeds 32768 bytes")
    try:
        return json.loads(raw, object_pairs_hook=_unique_keys,
                          parse_constant=_invalid_constant)
    except (json.JSONDecodeError, RecursionError) as exc:
        raise GraphError("MALFORMED_JSON", "invalid JSON; no automatic repair") from exc


def normalize(value: object) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= 64:
        raise GraphError("UNKNOWN_LABEL", "labels must be short strings")
    token = unicodedata.normalize("NFKC", value).casefold().strip()
    token = re.sub(r"[\s_-]+", "_", token)
    if not re.fullmatch(r"[a-z]+(?:_[a-z]+)*", token):
        raise GraphError("UNKNOWN_LABEL", f"invalid vocabulary token: {value!r}")
    return token


def _record(value: object, keys: set[str], context: str) -> dict:
    if not isinstance(value, dict) or set(value) != keys:
        raise GraphError("INVALID_SCHEMA", f"{context} requires exactly {sorted(keys)}")
    return value


def _bounded_list(value: object, context: str) -> list:
    if not isinstance(value, list):
        raise GraphError("INVALID_SCHEMA", f"{context} must be an array")
    if len(value) > LIMIT:
        raise GraphError("LIMIT_EXCEEDED", f"{context} has more than {LIMIT} entries")
    return value


class Canonicalizer:
    """A fixed instance is deterministic over a fixed, versioned vocabulary."""

    def __init__(self, vocabulary_path: Path = DEFAULT_VOCABULARY):
        vocabulary = parse_json(Path(vocabulary_path).read_text(encoding="utf-8"))
        expected = {"version", "objects", "colors", "predicates", "scenes",
                    "unary_predicates", "binary_predicates", "inverse_predicates",
                    "symmetric_predicates"}
        _record(vocabulary, expected, "vocabulary")
        self.version = vocabulary["version"]
        if not isinstance(self.version, str) or not re.fullmatch(r"[a-z0-9-]{1,64}", self.version):
            raise GraphError("INVALID_VOCABULARY", "invalid vocabulary version")
        self.vocabulary_sha256 = hashlib.sha256(
            compact_json(vocabulary).encode("utf-8")).hexdigest()
        self.aliases = {}
        for field in ("objects", "colors", "predicates", "scenes"):
            table = vocabulary[field]
            if not isinstance(table, dict) or not table:
                raise GraphError("INVALID_VOCABULARY", f"{field} requires a nonempty map")
            aliases = {}
            for canonical, alternatives in table.items():
                if normalize(canonical) != canonical or not isinstance(alternatives, list):
                    raise GraphError("INVALID_VOCABULARY", f"invalid {field} entry")
                for label in [canonical, *alternatives]:
                    token = normalize(label)
                    if token in aliases and aliases[token] != canonical:
                        raise GraphError("INVALID_VOCABULARY", f"ambiguous alias: {label}")
                    aliases[token] = canonical
            self.aliases[field] = aliases
        for field in ("unary_predicates", "binary_predicates", "symmetric_predicates"):
            values = vocabulary[field]
            if not isinstance(values, list) or any(
                    not isinstance(value, str) or normalize(value) != value for value in values):
                raise GraphError("INVALID_VOCABULARY", f"{field} requires canonical token arrays")
        self.unary = frozenset(vocabulary["unary_predicates"])
        self.binary = frozenset(vocabulary["binary_predicates"])
        self.inverse = vocabulary["inverse_predicates"]
        self.symmetric = frozenset(vocabulary["symmetric_predicates"])
        if not isinstance(self.inverse, dict) or any(
                not isinstance(value, str) or normalize(key) != key or normalize(value) != value
                for key, value in self.inverse.items()):
            raise GraphError("INVALID_VOCABULARY", "inverse predicates require canonical token mappings")
        labels = set(vocabulary["predicates"])
        if (self.unary & self.binary or not self.symmetric <= self.binary
                or set(self.inverse) & (self.unary | self.binary)
                or not set(self.inverse.values()) <= self.binary
                or labels != self.unary | self.binary | set(self.inverse)):
            raise GraphError("INVALID_VOCABULARY", "invalid predicate arities or inverse rules")

    def _label(self, field: str, value: object) -> str:
        token = normalize(value)
        if token not in self.aliases[field]:
            raise GraphError("UNKNOWN_LABEL", f"unsupported {field} label: {value!r}")
        return self.aliases[field][token]

    def canonicalize(self, raw: str) -> dict:
        """Return a graph and diagnostic fingerprint, or a typed failure."""
        try:
            return self._compile(parse_json(raw))
        except GraphError as exc:
            return {"status": "failure", "code": exc.code, "detail": str(exc)}

    def _compile(self, document: object) -> dict:
        _record(document, {"objects", "facts", "scene"}, "extraction")
        objects = _bounded_list(document["objects"], "objects")
        facts = _bounded_list(document["facts"], "facts")
        scene = None if document["scene"] is None else self._label("scenes", document["scene"])
        nodes = {}
        for item in objects:
            _record(item, {"id", "label", "color"}, "object")
            local_id = item["id"]
            if not isinstance(local_id, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,31}", local_id):
                raise GraphError("INVALID_ID", "object IDs must be short ASCII identifiers")
            if local_id in nodes:
                raise GraphError("DUPLICATE_ID", f"duplicate object ID: {local_id}")
            label = self._label("objects", item["label"])
            color = None if item["color"] is None else self._label("colors", item["color"])
            if label == "person" and color is not None:
                raise GraphError("INVALID_COLOR", "person color must be null")
            nodes[local_id] = (label, color)

        def reference(value: object) -> str:
            if not isinstance(value, str) or value not in nodes:
                raise GraphError("DANGLING_REFERENCE", "fact references an absent object")
            return value

        normalized_facts = set()
        for item in facts:
            _record(item, {"subject", "predicate", "object"}, "fact")
            subject = reference(item["subject"])
            predicate = self._label("predicates", item["predicate"])
            target = None if item["object"] is None else reference(item["object"])
            if predicate in self.inverse:
                if target is None:
                    raise GraphError("INVALID_ARITY", "inverse predicate requires two objects")
                subject, target = target, subject
                predicate = self.inverse[predicate]
            if (predicate in self.unary) != (target is None):
                raise GraphError("INVALID_ARITY", "unary facts require null; binary facts require an ID")
            if subject == target:
                raise GraphError("SELF_RELATION", "self relations are outside this proposal")
            normalized_facts.add((subject, predicate, target))
        if not nodes:
            raise GraphError("EMPTY_GRAPH", "no supported object; no fingerprint issued")

        # All <= 5! bijections are tried. This also resolves equal-label nodes
        # using their complete incidence structure, rather than VLM ID order.
        best = None
        for order in itertools.permutations(nodes):
            ids = {old: f"n{index + 1}" for index, old in enumerate(order)}
            edges = set()
            for subject, predicate, target in normalized_facts:
                source_id = ids[subject]
                target_id = None if target is None else ids[target]
                if predicate in self.symmetric and target_id < source_id:
                    source_id, target_id = target_id, source_id
                edges.add((source_id, predicate, target_id))
            graph = {
                "scheme_version": SCHEME,
                "vocabulary_version": self.version,
                "vocabulary_sha256": self.vocabulary_sha256,
                "objects": [{"id": ids[old], "label": nodes[old][0], "color": nodes[old][1]}
                            for old in order],
                "facts": sorted(({
                    "subject": source, "predicate": predicate, "object": target
                } for source, predicate, target in edges), key=compact_json),
                "scene": scene,
            }
            candidate = compact_json(graph)
            if best is None or candidate < best:
                best = candidate
        fingerprint = hashlib.sha256(
            b"semantic-graph-fingerprint/v1\0" + best.encode("utf-8")).hexdigest()
        return {"status": "ok", "graph": json.loads(best),
                "canonical_json": best, "fingerprint_sha256": fingerprint}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="raw VLM JSON; no markdown")
    parser.add_argument("--vocabulary", type=Path, default=DEFAULT_VOCABULARY)
    args = parser.parse_args()
    try:
        raw = args.input.read_text(encoding="utf-8")
        result = Canonicalizer(args.vocabulary).canonicalize(raw)
    except (OSError, UnicodeError, GraphError) as exc:
        result = {"status": "failure", "code": getattr(exc, "code", "FILE_ERROR"),
                  "detail": str(exc)}
    # print(json.dumps(result, indent=2, ensure_ascii=True))
    # return 0 if result["status"] == "ok" else 2
    output = json.dumps(result, indent=2, ensure_ascii=True)
    print(output)

    # Save output using the input filename + .json
    output_path = args.input.with_name(args.input.name + ".json")
    output_path.write_text(output, encoding="utf-8")

    return 0 if result["status"] == "ok" else 2

if __name__ == "__main__":
    sys.exit(main())
