"""Create a provenance-bound report for the frozen 320 compiler cases."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from prototype.semantic_secrets.v3 import load_active_contract

from .guard import git_commit
from .io import atomic_write, canonical_bytes, sha256_file


def run(output: Path, python: str) -> dict:
    command = [python, "-m", "pytest", "-q", "experiments/v3/test_semantic_compiler_v3.py"]
    process = subprocess.run(command, capture_output=True, text=True)
    transcript = process.stdout + process.stderr
    match = re.search(r"(?:^|\s)(\d+) passed(?:,|\s|$)", transcript)
    passed = int(match.group(1)) if match else 0
    value = {
        "schema_version": "compiler-invariant-report-v3.0.0",
        "compiler_id": load_active_contract().compiler_id,
        "config_hashes": dict(load_active_contract().config_hashes),
        "git_commit": git_commit(),
        "cases_passed": passed,
        "passed": process.returncode == 0 and passed >= 320,
        "command": command,
        "completed_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "transcript": transcript[-8000:],
    }
    if output.exists():
        raise ValueError("compiler report output already exists")
    atomic_write(output, canonical_bytes(value))
    if not value["passed"]:
        raise RuntimeError(f"compiler invariant suite failed or reported only {passed} cases")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--python", default="python")
    args = parser.parse_args(argv)
    value = run(args.output, args.python)
    print(json.dumps({"cases_passed": value["cases_passed"], "output": str(args.output), "sha256": sha256_file(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
