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
import threading
import time
from pathlib import Path
from typing import Any

from prototype.semantic_secrets.v3 import SemanticCompilerV3, load_active_contract

from .dataset import audit_ground_truth_freeze
from .guard import FormalPaths, verify_formal
from .io import atomic_write, canonical_bytes, read_json, sha256_file, sha256_tree
from .schemas import validate
from .telemetry import Telemetry
from .thresholds import validate_settings


class PipelineFailure(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code


class AdapterSession:
    """One persistent model process per pipeline; requests remain one JSON line."""

    def __init__(self, command: str) -> None:
        self._stderr: list[bytes] = []
        self.process = subprocess.Popen(
            shlex.split(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        assert self.process.stderr is not None
        self._thread = threading.Thread(target=self._drain_stderr, daemon=True)
        self._thread.start()

    def _drain_stderr(self) -> None:
        assert self.process.stderr is not None
        for block in iter(lambda: self.process.stderr.read1(4096), b""):
            self._stderr.append(block)
            if sum(map(len, self._stderr)) > 16000:
                self._stderr = [b"".join(self._stderr)[-8000:]]

    def request(self, request: dict[str, Any]) -> dict[str, Any]:
        if self.process.poll() is not None:
            raise PipelineFailure("COMPONENT_FAILURE", b"".join(self._stderr)[-2000:].decode(errors="replace"))
        assert self.process.stdin is not None and self.process.stdout is not None
        self.process.stdin.write(canonical_bytes(request))
        self.process.stdin.flush()
        value: list[bytes] = []
        failure: list[BaseException] = []

        def read() -> None:
            try:
                value.append(self.process.stdout.readline())
            except BaseException as exc:  # pragma: no cover - operating-system pipe failure
                failure.append(exc)

        reader = threading.Thread(target=read, daemon=True)
        reader.start()
        reader.join(request["timeout_seconds"])
        if reader.is_alive():
            self.close(kill=True)
            raise PipelineFailure("COMPONENT_TIMEOUT", "persistent adapter request timed out")
        if failure or not value or not value[0]:
            detail = b"".join(self._stderr)[-2000:].decode(errors="replace")
            code = "COMPONENT_OOM" if self.process.poll() in {9, 137, -9} or "out of memory" in detail.casefold() else "COMPONENT_FAILURE"
            raise PipelineFailure(code, detail or repr(failure))
        try:
            decoded = json.loads(value[0].decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PipelineFailure("MALFORMED_ADAPTER_OUTPUT", str(exc)) from exc
        if not isinstance(decoded, dict):
            raise PipelineFailure("MALFORMED_ADAPTER_OUTPUT", "adapter output is not one JSON object")
        return decoded

    def close(self, *, kill: bool = False) -> None:
        if self.process.poll() is not None:
            return
        if kill:
            self.process.kill()
        else:
            assert self.process.stdin is not None
            self.process.stdin.close()
            try:
                self.process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                self.process.kill()

    def __enter__(self) -> "AdapterSession":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


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
    validate("capability_manifest_v3_2.schema.json", manifest)
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
    ground_truth_sha = sha256_file(args.ground_truth)
    opportunities_sha = sha256_file(args.opportunities)

    if args.mode != "development":
        if not args.formal:
            raise SystemExit("REFUSED: validation and repeat require --formal")
        verify_formal(
            FormalPaths(args.authorization, args.ground_truth, args.manifest, args.opportunities, args.thresholds, args.model_manifest, args.gpu_environment, args.models, args.results),
            pipeline_ids=tuple(args.pipeline), mode=args.mode, resume=args.resume,
        )
    elif args.formal:
        raise SystemExit("REFUSED: --formal is reserved for validation modes")
    else:
        audit_ground_truth_freeze(
            read_json(args.ground_truth), args.manifest, args.opportunities, args.data
        )

    images = [row for row in manifest["images"] if row["split"] == ("development" if args.mode == "development" else "validation")]
    if args.limit is not None:
        images = images[: args.limit]
    compiler = SemanticCompilerV3(contract)
    output_dir = args.results / args.mode
    if output_dir.exists() and any(output_dir.iterdir()) and not args.resume:
        raise SystemExit(f"REFUSED: {output_dir} is not empty; use a verified --resume")

    for pipeline_id in args.pipeline:
        command = args.adapter_command[pipeline_id]
        with AdapterSession(command) as session:
          for image_index, image in enumerate(images):
            image_path = args.data / image["relative_path"]
            if not image_path.is_file() or sha256_file(image_path) != image["image_sha256"]:
                raise SystemExit(f"REFUSED: missing or hash-mismatched image {image['image_id']}")
            request = {
                "adapter_protocol": "bounded-observation-adapter-v3.1.0",
                "adapter_source_sha256": adapter_sha,
                "image_id": image["image_id"],
                "image_path": str(image_path.resolve()),
                "image_sha256": image["image_sha256"],
                "ground_truth_freeze_sha256": ground_truth_sha,
                "mode": args.mode,
                "model_manifest_sha256": model_manifest_sha,
                "pipeline_id": pipeline_id,
                "pipeline_revision": contract.expected_pipeline_revision(pipeline_id),
                "opportunities_sha256": opportunities_sha,
                "repeat_index": 1 if args.mode == "validation-repeat" else 0,
                "threshold_freeze_sha256": threshold_sha,
                "thresholds": thresholds["pipelines"][pipeline_id],
                "timeout_seconds": args.timeout_seconds,
                "resource_warmup": args.mode == "development" and image_index < int(contract.amend_prereg["compute"]["measurement_protocol"]["warmup_images"]),
            }
            key = cache_key(request)
            destination = output_dir / pipeline_id / f"{image['image_id']}.{key}.json"
            if destination.exists() and args.resume:
                existing = read_json(destination)
                if existing.get("cache_key") != key:
                    raise SystemExit(f"REFUSED: cache key mismatch for {destination}")
                continue
            try:
                with Telemetry() as controller_meter:
                    started = time.perf_counter()
                    observation = session.request(request)
                    compiled = json.loads(compiler.compile(observation))
                    controller_telemetry = controller_meter.finish()
                record = {
                    "cache_key": key, "compiler_result": compiled, "observation": observation,
                    "pipeline_failure": None, "request": request,
                    "complete_pipeline_elapsed_seconds": round(time.perf_counter() - started, 6),
                    "controller_telemetry": controller_telemetry,
                }
            except PipelineFailure as exc:
                record = {"cache_key": key, "compiler_result": None, "observation": None, "pipeline_failure": {"code": exc.code, "detail": str(exc)}, "request": request, "complete_pipeline_elapsed_seconds": None, "controller_telemetry": None}
            atomic_write(destination, canonical_bytes(record))
    expected_records = len(images) * len(args.pipeline)
    actual_records = len(list(output_dir.rglob("*.json")))
    if actual_records != expected_records:
        raise SystemExit(f"REFUSED: {args.mode} produced {actual_records} records, expected {expected_records}")
    atomic_write(
        output_dir / ".complete",
        canonical_bytes({
            "mode": args.mode,
            "pipelines": sorted(args.pipeline),
            "records": actual_records,
            "manifest_sha256": sha256_file(args.manifest),
            "thresholds_sha256": threshold_sha,
        }),
    )
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
    for name in ("authorization", "ground-truth", "opportunities", "gpu-environment"):
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
    if args.ground_truth is None or args.opportunities is None:
        raise SystemExit("all inference modes require a frozen ground-truth record and opportunity table")
    if args.mode != "development" and any(value is None for value in (args.authorization, args.gpu_environment)):
        raise SystemExit("formal validation requires authorization and GPU environment records")
    return execute(args)


if __name__ == "__main__":
    raise SystemExit(main())
