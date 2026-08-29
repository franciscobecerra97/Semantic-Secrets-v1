"""Create an explicit hash-bound P9-v3B formal authorization record."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from prototype.semantic_secrets.v3 import load_active_contract

from .guard import git_commit
from .io import atomic_write, canonical_bytes, sha256_file
from .schemas import validate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authorize-formal", action="store_true")
    parser.add_argument("--authorized-by", required=True)
    parser.add_argument("--container-image-digest", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--opportunities", type=Path, required=True)
    parser.add_argument("--ground-truth", type=Path, required=True)
    parser.add_argument("--thresholds", type=Path, required=True)
    parser.add_argument("--model-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if not args.authorize_formal:
        raise SystemExit("REFUSED: --authorize-formal is required")
    if args.output.exists():
        raise SystemExit("REFUSED: formal authorization output already exists")
    contract = load_active_contract()
    value = {
        "schema_version": "formal-authorization-v3.2.0", "scope": "P9-v3B-formal-execution",
        "expected_git_commit": git_commit(), "expected_container_image_digest": args.container_image_digest,
        "expected_config_hashes": dict(contract.config_hashes),
        "expected_manifest_sha256": sha256_file(args.manifest),
        "expected_opportunities_sha256": sha256_file(args.opportunities),
        "expected_ground_truth_freeze_sha256": sha256_file(args.ground_truth),
        "expected_threshold_freeze_sha256": sha256_file(args.thresholds),
        "expected_model_manifest_sha256": sha256_file(args.model_manifest),
        "pipeline_ids": list(contract.pipeline_ids), "authorized_by": args.authorized_by,
        "authorized_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    validate("formal_authorization_v3_2.schema.json", value)
    atomic_write(args.output, canonical_bytes(value))
    print(json.dumps({"output": str(args.output), "sha256": sha256_file(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
