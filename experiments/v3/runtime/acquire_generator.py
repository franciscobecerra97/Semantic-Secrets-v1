"""Opt-in acquisition of the exact frozen SD-Turbo dataset generator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from huggingface_hub import HfApi, snapshot_download

from prototype.semantic_secrets.v3 import load_active_contract

from .acquire import inventory
from .io import atomic_write, canonical_bytes, sha256_file


def frozen_generator() -> dict:
    return dict(load_active_contract().base_prereg["dataset"]["strata"]["B_naturalistic_t2i"]["generator"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--permit-acquisition", action="store_true")
    parser.add_argument("--license-approved", action="store_true")
    args = parser.parse_args(argv)
    frozen = frozen_generator()
    plan = {"component_id": "sd-turbo", **frozen}
    if not args.permit_acquisition:
        print(json.dumps({"status": "dry-run-only", "would_acquire": plan}, sort_keys=True))
        return 0
    if not args.license_approved:
        raise SystemExit("SD-Turbo acquisition requires an explicit Stability AI Community License approval")
    info = HfApi().model_info(frozen["model_id"], revision=frozen["revision"], files_metadata=True)
    if info.sha != frozen["revision"]:
        raise RuntimeError("SD-Turbo resolved revision mismatch")
    target = args.models / "sd-turbo"
    snapshot_download(repo_id=frozen["model_id"], revision=frozen["revision"], local_dir=target, local_dir_use_symlinks=False)
    remote = {row.rfilename: row for row in info.siblings}
    files = inventory(target)
    for row in files:
        sibling = remote.get(row["relative_path"])
        if sibling is None or (sibling.size is not None and sibling.size != row["bytes"]):
            raise RuntimeError(f"SD-Turbo exact-revision metadata mismatch: {row['relative_path']}")
        lfs = getattr(sibling, "lfs", None)
        row["source_url"] = f"https://huggingface.co/{frozen['model_id']}/resolve/{frozen['revision']}/{row['relative_path']}"
        row["etag_or_lfs_oid"] = getattr(lfs, "sha256", None) or sibling.blob_id
        row["remote_bytes"] = sibling.size
    record = {
        "schema_version": "generator-acquisition-v3.0.0", "component_id": "sd-turbo",
        "model_id": frozen["model_id"], "revision": frozen["revision"], "license": frozen["license"],
        "license_approved": True, "source": f"https://huggingface.co/{frozen['model_id']}",
        "files": files, "verified": True,
    }
    if args.manifest.exists():
        raise ValueError("generator acquisition manifest already exists")
    atomic_write(args.manifest, canonical_bytes(record))
    print(json.dumps({"manifest": str(args.manifest), "sha256": sha256_file(args.manifest)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
