"""Record and verify the frozen controller/EGTR software environments."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import subprocess
from pathlib import Path
from typing import Any

from prototype.semantic_secrets.v3 import load_active_contract

from .io import atomic_write, canonical_bytes, sha256_file
from .telemetry import environment_record


MODERN = {
    "torch": "2.4.1", "torchvision": "0.19.1", "transformers": "4.49.0",
    "huggingface-hub": "0.28.1", "safetensors": "0.5.2", "tokenizers": "0.21.0",
    "Pillow": "11.1.0", "numpy": "1.26.4", "jsonschema": "4.23.0", "psutil": "6.1.1",
}


def package_versions(expected: dict[str, str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for package, version in expected.items():
        actual = importlib.metadata.version(package)
        if actual != version:
            raise RuntimeError(f"{package}: expected {version}, found {actual}")
        result[package] = actual
    return result


def verify_only() -> dict[str, Any]:
    contract = load_active_contract()
    return {
        "config_hashes": dict(contract.config_hashes),
        "packages": package_versions(MODERN),
        "pipeline_ids": list(contract.pipeline_ids),
        "pipeline_revisions": {pipeline: contract.expected_pipeline_revision(pipeline) for pipeline in contract.pipeline_ids},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--gpu-record", type=Path)
    parser.add_argument("--nvidia-smi", type=Path)
    parser.add_argument("--image-digest")
    args = parser.parse_args(argv)
    verified = verify_only()
    if args.verify_only and args.gpu_record is None:
        print(json.dumps(verified, sort_keys=True))
        return 0
    if args.gpu_record is None or args.nvidia_smi is None or not args.nvidia_smi.is_file() or not args.image_digest:
        raise SystemExit("GPU recording requires --gpu-record, --image-digest, and an existing --nvidia-smi capture")
    if not args.image_digest.startswith("sha256:") or len(args.image_digest) != 71:
        raise SystemExit("container image must be recorded by immutable sha256 digest")
    record = environment_record()
    if not record.get("cuda_available"):
        raise SystemExit("CUDA is not available; formal GPU environment cannot be recorded")
    record.update(
        schema_version="gpu-environment-v3.1.0",
        container_image_digest=args.image_digest,
        nvidia_smi_sha256=sha256_file(args.nvidia_smi),
        verified_environment=verified,
    )
    atomic_write(args.gpu_record, canonical_bytes(record))
    print(json.dumps({"gpu_record": str(args.gpu_record), "sha256": sha256_file(args.gpu_record)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
