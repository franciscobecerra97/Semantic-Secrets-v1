"""Explicitly gated exact-revision model acquisition and provenance hashing."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from prototype.semantic_secrets.v3 import load_active_contract

from .io import atomic_write, canonical_bytes, read_json, sha256_file


def inventory(root: Path) -> list[dict[str, Any]]:
    return [
        {"relative_path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted(root.rglob("*")) if path.is_file() and ".cache" not in path.relative_to(root).parts
    ]


def plan() -> list[dict[str, Any]]:
    contract = load_active_contract()
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for pipeline_id in contract.pipeline_ids:
        for component_id, component in contract.component_map(pipeline_id).items():
            key = (component_id, component["revision"])
            if key in seen:
                continue
            seen.add(key)
            rows.append({"component_id": component_id, "pipeline_ids": [p for p in contract.pipeline_ids if component_id in contract.component_map(p)], **dict(component)})
    return rows


def acquire_hf(component: dict[str, Any], destination: Path) -> dict[str, Any]:
    from huggingface_hub import HfApi, snapshot_download

    target = destination / component["component_id"]
    info = HfApi().model_info(component["model_id"], revision=component["revision"], files_metadata=True)
    if info.sha != component["revision"]:
        raise RuntimeError(f"resolved revision mismatch for {component['component_id']}")
    card_license = str((info.card_data or {}).get("license", "")) if isinstance(info.card_data, dict) else str(getattr(info.card_data, "license", ""))
    if card_license and card_license.casefold().replace("-", "") != str(component["license"]).casefold().replace("-", ""):
        raise RuntimeError(f"licence metadata mismatch for {component['component_id']}")
    snapshot_download(
        repo_id=component["model_id"], revision=component["revision"], local_dir=target,
        local_dir_use_symlinks=False,
    )
    remote = {row.rfilename: row for row in info.siblings}
    files = inventory(target)
    for row in files:
        sibling = remote.get(row["relative_path"])
        if sibling is None:
            raise RuntimeError(f"downloaded file is absent from exact-revision metadata: {row['relative_path']}")
        if sibling.size is not None and sibling.size != row["bytes"]:
            raise RuntimeError(f"remote byte-size mismatch: {row['relative_path']}")
        lfs = getattr(sibling, "lfs", None)
        row["source_url"] = f"https://huggingface.co/{component['model_id']}/resolve/{component['revision']}/{row['relative_path']}"
        row["etag_or_lfs_oid"] = getattr(lfs, "sha256", None) or sibling.blob_id
        row["remote_bytes"] = sibling.size
    return {**component, "files": files, "resolved_revision": info.sha, "source": f"https://huggingface.co/{component['model_id']}", "verified": True}


def approve_egtr(component: dict[str, Any], archive: Path, approval: Path, destination: Path) -> dict[str, Any]:
    record = read_json(approval)
    required = {
        "schema_version": "egtr-provenance-approval-v3.1.0",
        "official_file_id": "18phcRxbrEI7HqIuM2OLAPuwAF5k3pUC2",
        "repository_revision": component["revision"],
        "license_compatible": True,
        "checkpoint_terms_reviewed": True,
    }
    for key, expected in required.items():
        if record.get(key) != expected:
            raise RuntimeError(f"EGTR approval mismatch for {key}; acquisition fails closed")
    if archive.name != "egtr_vg.tar.gz" or not archive.is_file():
        raise RuntimeError("the manually acquired official EGTR archive is missing or ambiguously named")
    expected_sha = record.get("archive_sha256")
    if expected_sha != sha256_file(archive):
        raise RuntimeError("EGTR archive hash does not match the separately reviewed approval")
    target = destination / component["component_id"]
    if not target.is_dir():
        raise RuntimeError("EGTR archive must be extracted outside this script after review; expected verified directory is absent")
    files = inventory(target)
    if not any(row["relative_path"].startswith("checkpoints/") and row["relative_path"].endswith(".ckpt") for row in files):
        raise RuntimeError("EGTR artifact contains no unambiguous official checkpoint")
    if not any(row["relative_path"].endswith("config.json") for row in files):
        raise RuntimeError("EGTR artifact lacks required config metadata; fail closed")
    return {**component, "archive_bytes": archive.stat().st_size, "archive_sha256": expected_sha, "files": files, "source": component["checkpoint_url"], "verified": True}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--permit-acquisition", action="store_true")
    parser.add_argument("--egtr-archive", type=Path)
    parser.add_argument("--egtr-approved-provenance", type=Path)
    args = parser.parse_args(argv)
    acquisition_plan = plan()
    if not args.permit_acquisition:
        print(json.dumps({"status": "dry-run-only", "would_acquire": acquisition_plan}, sort_keys=True))
        return 0
    args.models.mkdir(parents=True, exist_ok=True)
    acquired: list[dict[str, Any]] = []
    for component in acquisition_plan:
        if "model_id" in component:
            acquired.append(acquire_hf(component, args.models))
        elif component["component_id"] == "egtr-vg":
            if args.egtr_archive is None or args.egtr_approved_provenance is None:
                raise SystemExit("EGTR is ambiguous until both a reviewed approval and manually acquired archive are supplied")
            acquired.append(approve_egtr(component, args.egtr_archive, args.egtr_approved_provenance, args.models))
    manifest = {"schema_version": "model-acquisition-v3.1.0", "components": acquired}
    atomic_write(args.manifest, canonical_bytes(manifest))
    print(json.dumps({"manifest": str(args.manifest), "sha256": sha256_file(args.manifest)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
