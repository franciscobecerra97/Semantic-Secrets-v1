"""Deterministic capability-manifest and model-blind annotation checks."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from prototype.semantic_secrets.v3 import load_active_contract

from .io import canonical_bytes, read_json, sha256_file
from .schemas import validate


def expected_image_ids() -> list[str]:
    ids: list[str] = []
    for stratum_code in ("A", "B"):
        for family in range(1, 25):
            for image in range(1, 6):
                ids.append(f"cap-v3-{stratum_code}-F{family:02d}-{image:02d}")
    return ids


def audit_manifest(manifest: dict[str, Any], data_root: Path | None = None) -> dict[str, Any]:
    validate("capability_manifest_v3_1.schema.json", manifest)
    rows = manifest["images"]
    ids = [row["image_id"] for row in rows]
    if len(ids) != len(set(ids)) or sorted(ids) != sorted(expected_image_ids()):
        raise ValueError("manifest IDs do not equal the deterministic 240-image identifier set")
    family_split: dict[tuple[str, str], set[str]] = defaultdict(set)
    counts = Counter((row["stratum"], row["split"]) for row in rows)
    for row in rows:
        family_split[(row["stratum"], row["family_id"])].add(row["split"])
        expected_stratum = "A_controlled_geometric" if "-A-" in row["image_id"] else "B_naturalistic_t2i"
        if row["stratum"] != expected_stratum:
            raise ValueError(f"stratum/identifier mismatch for {row['image_id']}")
        if data_root is not None:
            image = data_root / row["relative_path"]
            if not image.is_file() or sha256_file(image) != row["image_sha256"]:
                raise ValueError(f"missing or hash-mismatched image {row['image_id']}")
    if any(len(splits) != 1 for splits in family_split.values()):
        raise ValueError("semantic scenario family crosses development/validation")
    expected_counts = {
        ("A_controlled_geometric", "development"): 60,
        ("A_controlled_geometric", "validation"): 60,
        ("B_naturalistic_t2i", "development"): 60,
        ("B_naturalistic_t2i", "validation"): 60,
    }
    if counts != Counter(expected_counts):
        raise ValueError(f"split counts mismatch: {dict(counts)}")
    return {"images": len(rows), "sha256": hashlib.sha256(canonical_bytes(manifest)).hexdigest(), "split_counts": {"|".join(key): value for key, value in sorted(counts.items())}}


def audit_opportunities(path: Path) -> dict[str, Any]:
    config = load_active_contract().amend_prereg["dataset_support"]["validation_plan_each_stratum"]
    counts: Counter[tuple[str, str, str]] = Counter()
    seen: set[str] = set()
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            opportunity_id = row["opportunity_id"]
            if opportunity_id in seen:
                raise ValueError(f"duplicate opportunity_id {opportunity_id}")
            seen.add(opportunity_id)
            polarity = row["polarity"]
            if polarity not in {"positive", "negative"}:
                raise ValueError(f"invalid polarity {polarity}")
            counts[(row["stratum"], row["atom_type"], polarity)] += 1
    for stratum in ("A_controlled_geometric", "B_naturalistic_t2i"):
        for atom_type, rule in config.items():
            for polarity in ("positive", "negative"):
                expected = int(rule[polarity])
                actual = counts[(stratum, atom_type, polarity)]
                if actual != expected:
                    raise ValueError(f"{stratum}/{atom_type}/{polarity}: expected {expected}, found {actual}")
    return {"opportunities": len(seen), "sha256": sha256_file(path)}


def randomized_assignment(manifest: dict[str, Any], seed: int) -> list[dict[str, str]]:
    ids = sorted(row["image_id"] for row in manifest["images"])
    rng = random.Random(seed)
    shuffled = ids[:]
    rng.shuffle(shuffled)
    return [
        {"blind_id": f"blind-v3-{index:03d}", "image_id": image_id}
        for index, image_id in enumerate(shuffled, start=1)
    ]


def agreement(first: Path, second: Path) -> dict[str, Any]:
    def load(path: Path) -> dict[str, str]:
        with path.open("r", encoding="utf-8", newline="") as handle:
            return {row["opportunity_id"]: row["visible"] for row in csv.DictReader(handle)}

    a, b = load(first), load(second)
    if set(a) != set(b):
        raise ValueError("annotators did not label the same opportunity IDs")
    allowed = {"yes", "no", "uncertain"}
    if not set(a.values()) <= allowed or not set(b.values()) <= allowed:
        raise ValueError("visible must be yes, no, or uncertain")
    total = len(a)
    matches = sum(a[key] == b[key] for key in a)
    labels = sorted(allowed)
    observed = matches / total if total else 0.0
    expected = sum(
        (sum(value == label for value in a.values()) / total) * (sum(value == label for value in b.values()) / total)
        for label in labels
    ) if total else 0.0
    kappa = (observed - expected) / (1 - expected) if total and expected < 1 else None
    return {"agreements": matches, "cohen_kappa": kappa, "disagreements": total - matches, "items": total, "raw_agreement": observed}


def adjudication(first: Path, second: Path, consensus: Path) -> dict[str, Any]:
    def load(path: Path, value_field: str) -> dict[str, dict[str, str]]:
        with path.open("r", encoding="utf-8", newline="") as handle:
            return {row["opportunity_id"]: row for row in csv.DictReader(handle) if row.get(value_field)}

    a, b, resolved = load(first, "visible"), load(second, "visible"), load(consensus, "adjudicated_visible")
    if set(a) != set(b):
        raise ValueError("annotator opportunity sets differ")
    disagreements = {key for key in a if a[key]["visible"] != b[key]["visible"]}
    if set(resolved) != disagreements:
        raise ValueError("adjudication rows must equal the exact disagreement set")
    for key, row in resolved.items():
        if row["adjudicated_visible"] not in {"yes", "no", "uncertain"} or not row.get("adjudicator_notes", "").strip():
            raise ValueError(f"invalid adjudication for {key}")
    return {
        "adjudicated_conflicts": len(resolved),
        "annotator_1_sha256": sha256_file(first),
        "annotator_2_sha256": sha256_file(second),
        "consensus_sha256": sha256_file(consensus),
        "raw_records_retained": True,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="P9-v3B dataset/annotation preparation")
    sub = parser.add_subparsers(dest="command", required=True)
    manifest = sub.add_parser("audit-manifest")
    manifest.add_argument("path", type=Path)
    manifest.add_argument("--data-root", type=Path)
    opportunities = sub.add_parser("audit-opportunities")
    opportunities.add_argument("path", type=Path)
    randomize = sub.add_parser("randomize")
    randomize.add_argument("manifest", type=Path)
    randomize.add_argument("--seed", type=int, default=925031)
    compare = sub.add_parser("agreement")
    compare.add_argument("first", type=Path)
    compare.add_argument("second", type=Path)
    adjudicate = sub.add_parser("adjudicate")
    adjudicate.add_argument("first", type=Path)
    adjudicate.add_argument("second", type=Path)
    adjudicate.add_argument("consensus", type=Path)
    args = parser.parse_args(argv)
    if args.command == "audit-manifest":
        result = audit_manifest(read_json(args.path), args.data_root)
    elif args.command == "audit-opportunities":
        result = audit_opportunities(args.path)
    elif args.command == "randomize":
        result = randomized_assignment(read_json(args.manifest), args.seed)
    elif args.command == "agreement":
        result = agreement(args.first, args.second)
    else:
        result = adjudication(args.first, args.second, args.consensus)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
