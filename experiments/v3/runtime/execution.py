"""Deterministic controller for development, validation, and validation repeat.

Pipeline adapters are isolated subprocesses. Each receives one canonical JSON
request on stdin and must emit exactly one bounded observation JSON object on
stdout. Only the deterministic compiler writes graph results.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

from prototype.semantic_secrets.v3 import SemanticCompilerV3, load_active_contract

from .guard import FormalPaths, verify_formal
from .io import atomic_write, canonical_bytes, read_json, sha256_file, sha256_tree
from .schemas import validate
from .thresholds import validate_settings


class PipelineFailure(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code


def cache_key(request: dict[str, Any]) -> str:
    projection = {key: value for key, value in request.items() if key not in {"image_path", "timeout_seconds"}}
    return hashlib.sha256(canonical_bytes(projection)).hexdigest()


def run_adapter(command: str, request: dict[str, Any]) -> dict[str, Any]:
    try:
        process = subprocess.run(
            shlex.split(command), input=canonical_bytes(request), capture_output=True, timeout=request["timeout_seconds"]
        )
    except subprocess.TimeoutExpired as exc:
        raise PipelineFailure("COMPONENT_TIMEOUT", str(exc)) from exc
    if process.returncode != 0:
        stderr = process.stderr.decode("utf-8", errors="replace")[-2000:]
        code = "COMPONENT_OOM" if process.returncode in {9, 137} or "out of memory" in stderr.casefold() else "COMPONENT_FAILURE"
        raise PipelineFailure(code, stderr)
    try:
        value = json.loads(process.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PipelineFailure("MALFORMED_ADAPTER_OUTPUT", str(exc)) from exc
    if not isinstance(value, dict):
        raise PipelineFailure("MALFORMED_ADAPTER_OUTPUT", "adapter output is not one JSON object")
    return value


def execute(args: argparse.Namespace) -> int:
    contract = load_active_contract()
    manifest = read_json(args.manifest)
    validate("capability_manifest_v3_1.schema.json", manifest)
    thresholds = read_json(args.thresholds)
    if args.mode == "development":
        if thresholds.get("schema_version") != "development-threshold-settings-v3.1.0" or not isinstance(thresholds.get("pipelines"), dict):
            raise SystemExit("REFUSED: development requires explicitly versioned development threshold settings")
    else:
        validate("threshold_freeze_v3_1.schema.json", thresholds)
    for pipeline_id in args.pipeline:
        try:
            validate_settings(pipeline_id, thresholds["pipelines"][pipeline_id], exact_tasks=True)
        except (KeyError, ValueError) as exc:
            raise SystemExit(f"REFUSED: {exc}") from exc
    model_manifest_sha = sha256_file(args.model_manifest)
    threshold_sha = sha256_file(args.thresholds)
    adapter_sha = sha256_tree(args.adapter_source)

    if args.mode != "development":
        if not args.formal:
            raise SystemExit("REFUSED: validation and repeat require --formal")
        verify_formal(
            FormalPaths(args.authorization, args.annotation, args.manifest, args.opportunities, args.thresholds, args.model_manifest, args.gpu_environment, args.models, args.results),
            pipeline_ids=tuple(args.pipeline), mode=args.mode, resume=args.resume,
        )
    elif args.formal:
        raise SystemExit("REFUSED: --formal is reserved for validation modes")

    images = [row for row in manifest["images"] if row["split"] == ("development" if args.mode == "development" else "validation")]
    if args.limit is not None:
        images = images[: args.limit]
    compiler = SemanticCompilerV3(contract)
    output_dir = args.results / args.mode
    if output_dir.exists() and any(output_dir.iterdir()) and not args.resume:
        raise SystemExit(f"REFUSED: {output_dir} is not empty; use a verified --resume")

    for pipeline_id in args.pipeline:
        command = args.adapter_command[pipeline_id]
        for image in images:
            image_path = args.data / image["relative_path"]
            if not image_path.is_file() or sha256_file(image_path) != image["image_sha256"]:
                raise SystemExit(f"REFUSED: missing or hash-mismatched image {image['image_id']}")
            request = {
                "adapter_protocol": "bounded-observation-adapter-v3.1.0",
                "adapter_source_sha256": adapter_sha,
                "image_id": image["image_id"],
                "image_path": str(image_path.resolve()),
                "image_sha256": image["image_sha256"],
                "mode": args.mode,
                "model_manifest_sha256": model_manifest_sha,
                "pipeline_id": pipeline_id,
                "pipeline_revision": contract.expected_pipeline_revision(pipeline_id),
                "repeat_index": 1 if args.mode == "validation-repeat" else 0,
                "threshold_freeze_sha256": threshold_sha,
                "thresholds": thresholds["pipelines"][pipeline_id],
                "timeout_seconds": args.timeout_seconds,
            }
            key = cache_key(request)
            destination = output_dir / pipeline_id / f"{image['image_id']}.{key}.json"
            if destination.exists() and args.resume:
                existing = read_json(destination)
                if existing.get("cache_key") != key:
                    raise SystemExit(f"REFUSED: cache key mismatch for {destination}")
                continue
            try:
                observation = run_adapter(command, request)
                compiled = json.loads(compiler.compile(observation))
                record = {"cache_key": key, "compiler_result": compiled, "observation": observation, "pipeline_failure": None, "request": request}
            except PipelineFailure as exc:
                record = {"cache_key": key, "compiler_result": None, "observation": None, "pipeline_failure": {"code": exc.code, "detail": str(exc)}, "request": request}
            atomic_write(destination, canonical_bytes(record))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="P9-v3B isolated pipeline controller")
    result.add_argument("--mode", choices=["development", "validation", "validation-repeat"], required=True)
    result.add_argument("--formal", action="store_true")
    result.add_argument("--resume", action="store_true")
    result.add_argument("--limit", type=int)
    result.add_argument("--timeout-seconds", type=int, default=300)
    result.add_argument("--pipeline", action="append", choices=list(load_active_contract().pipeline_ids), required=True)
    result.add_argument("--adapter-command", action="append", metavar="PIPELINE=COMMAND", required=True)
    for name in ("manifest", "thresholds", "model-manifest", "adapter-source", "models", "data", "results"):
        result.add_argument(f"--{name}", type=Path, required=True)
    for name in ("authorization", "annotation", "opportunities", "gpu-environment"):
        result.add_argument(f"--{name}", type=Path)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    parsed: dict[str, str] = {}
    for item in args.adapter_command:
        if "=" not in item:
            raise SystemExit("adapter commands must use PIPELINE=COMMAND")
        pipeline, command = item.split("=", 1)
        parsed[pipeline] = command
    if set(args.pipeline) != set(parsed):
        raise SystemExit("every and only requested pipelines need an adapter command")
    args.adapter_command = parsed
    if args.mode != "development" and any(value is None for value in (args.authorization, args.annotation, args.opportunities, args.gpu_environment)):
        raise SystemExit("formal validation requires authorization, annotation, opportunity, and GPU environment records")
    return execute(args)


if __name__ == "__main__":
    raise SystemExit(main())
