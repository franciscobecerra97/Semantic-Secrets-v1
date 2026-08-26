"""Verify deterministic caches and export an integrity inventory."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from .execution import cache_key
from .io import atomic_write, canonical_bytes, read_json, sha256_file


def verify_cache(results: Path) -> dict[str, int]:
    files = sorted(results.rglob("*.json"))
    checked = 0
    for path in files:
        row = read_json(path)
        if "cache_key" not in row or "request" not in row:
            continue
        if row["cache_key"] != cache_key(row["request"]):
            raise ValueError(f"cache key mismatch: {path}")
        checked += 1
    if checked == 0:
        raise ValueError("no result cache records found")
    return {"cache_records": checked}


def observation_projection(value: dict) -> dict:
    keys = ("observation_version", "pipeline_id", "pipeline_revision", "image_id", "image_sha256", "detections", "attributes", "unary_actions", "binary_interactions", "scenes")
    projection = {key: value[key] for key in keys}
    projection["component_events"] = [
        {key: row.get(key) for key in ("component_id", "component_revision", "status", "failure_code")}
        for row in value["component_events"]
    ]
    for key in ("detections", "attributes", "unary_actions", "binary_interactions", "scenes", "component_events"):
        projection[key] = sorted(projection[key], key=lambda row: canonical_bytes(row))
    return projection


def verify_repeat(results: Path) -> dict[str, int]:
    def load(directory: Path) -> dict[tuple[str, str], dict]:
        rows: dict[tuple[str, str], dict] = {}
        for path in directory.rglob("*.json"):
            record = read_json(path)
            request = record.get("request", {})
            key = (request.get("pipeline_id"), request.get("image_id"))
            if None not in key:
                if key in rows:
                    raise ValueError(f"duplicate repeat key {key}")
                rows[key] = record
        return rows

    first, repeat = load(results / "validation"), load(results / "validation-repeat")
    if len(first) != 240 or set(first) != set(repeat):
        raise ValueError("repeat verification requires the same 240 pipeline/image keys in both passes")
    observation_equal = graph_equal = 0
    for key in first:
        a, b = first[key], repeat[key]
        if (a["pipeline_failure"] is None) != (b["pipeline_failure"] is None):
            continue
        if a["pipeline_failure"] is not None:
            if a["pipeline_failure"]["code"] == b["pipeline_failure"]["code"]:
                observation_equal += 1
                graph_equal += 1
            continue
        if observation_projection(a["observation"]) == observation_projection(b["observation"]):
            observation_equal += 1
        if a["compiler_result"] == b["compiler_result"]:
            graph_equal += 1
    return {"pairs": len(first), "canonical_observation_equal": observation_equal, "canonical_graph_equal": graph_equal}


def export(results: Path, destination: Path) -> dict[str, int]:
    verified = verify_cache(results)
    if destination.exists():
        raise ValueError("export destination must not already exist")
    shutil.copytree(results, destination)
    inventory = [
        {"relative_path": path.relative_to(destination).as_posix(), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted(destination.rglob("*")) if path.is_file()
    ]
    atomic_write(destination / "SHA256_INVENTORY.json", canonical_bytes({"files": inventory}))
    return {**verified, "exported_files": len(inventory)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    verify = sub.add_parser("verify-cache")
    verify.add_argument("--results", type=Path, required=True)
    verify.add_argument("--manifest", type=Path, required=False)
    repeat_parser = sub.add_parser("verify-repeat")
    repeat_parser.add_argument("--results", type=Path, required=True)
    export_parser = sub.add_parser("export")
    export_parser.add_argument("--results", type=Path, required=True)
    export_parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "verify-cache":
        result = verify_cache(args.results)
    elif args.command == "verify-repeat":
        result = verify_repeat(args.results)
    else:
        result = export(args.results, args.destination)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
