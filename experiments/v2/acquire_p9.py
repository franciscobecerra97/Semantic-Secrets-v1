from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from huggingface_hub import snapshot_download


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments" / "v2" / "config" / "preregistration_v2.json"
MANIFEST = ROOT / "experiments" / "v2" / "manifests" / "model_acquisition_v2.json"
MODEL_ROOT = ROOT / "artifacts" / "downloads" / "p9_v2" / "models"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def candidate(backend: str) -> dict[str, Any]:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    for item in config["extractor_screen"]["candidates"]:
        if backend == "moondream" and item["model_id"] == "vikhyatk/moondream2":
            return item
        if backend == "smolvlm2" and item["model_id"] == "HuggingFaceTB/SmolVLM2-2.2B-Instruct":
            return item
    raise ValueError(f"unknown frozen backend: {backend}")


def static_remote_code_review(snapshot: Path, allowed_findings: set[tuple[str, str]] | None = None) -> dict[str, Any]:
    allowed_findings = allowed_findings or set()
    python_files = sorted(snapshot.glob("*.py"))
    patterns = {
        "process_execution": re.compile(r"\b(subprocess|os\.system|Popen)\b"),
        "network_access": re.compile(r"\b(requests|urllib|httpx|socket)\b"),
        "dynamic_execution": re.compile(r"\b(eval|exec)\s*\("),
        "filesystem_deletion": re.compile(r"\b(rmtree|unlink|remove)\s*\("),
    }
    findings: list[dict[str, Any]] = []
    files = []
    for path in python_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        files.append({"name": path.name, "sha256": sha256(path), "bytes": path.stat().st_size})
        for label, pattern in patterns.items():
            matches = sorted(set(match.group(0) for match in pattern.finditer(text)))
            if matches:
                findings.append({"file": path.name, "category": label, "matches": matches})
    blocking = [
        item for item in findings
        if item["category"] in {"process_execution", "network_access", "dynamic_execution", "filesystem_deletion"}
        and (item["file"], item["category"]) not in allowed_findings
    ]
    return {
        "review_method": "static scan of every repository-root Python file before trust_remote_code execution",
        "python_files": files,
        "findings": findings,
        "allowed_findings": [
            {"file": file_name, "category": category}
            for file_name, category in sorted(allowed_findings)
        ],
        "blocking_findings": blocking,
        "approved": not blocking,
        "limitation": "Static review is not a formal sandbox or proof; inference is subsequently run offline/local-files-only.",
    }


def acquire(backend: str) -> dict[str, Any]:
    item = candidate(backend)
    target = MODEL_ROOT / backend / item["revision"]
    target.mkdir(parents=True, exist_ok=True)
    snapshot = Path(snapshot_download(repo_id=item["model_id"], revision=item["revision"], local_dir=target))
    files = sorted(path for path in snapshot.rglob("*") if path.is_file())
    entry: dict[str, Any] = {
        "backend": backend,
        "model_id": item["model_id"],
        "revision": item["revision"],
        "snapshot_relpath": snapshot.relative_to(ROOT).as_posix(),
        "file_count": len(files),
        "total_bytes": sum(path.stat().st_size for path in files),
        "config_sha256": sha256(CONFIG),
        "weights_committed": False,
    }
    if backend == "moondream":
        entry["remote_code_review"] = static_remote_code_review(
            snapshot,
            allowed_findings={("lora.py", "network_access")},
        )
        entry["remote_code_review"]["mitigations"] = [
            "P9 never supplies a variant identifier, so cached_variant_path/urlopen is unreachable.",
            "HF_HUB_OFFLINE and TRANSFORMERS_OFFLINE are enforced during inference.",
            "Tokenizer.from_pretrained is temporarily redirected to the pinned snapshot tokenizer.json during construction.",
            "All model and processor loads use local_files_only=True.",
        ]
        if not entry["remote_code_review"]["approved"]:
            raise RuntimeError(f"remote-code static review failed: {entry['remote_code_review']['findings']}")
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    existing: dict[str, Any] = {"schema_version": "p9-model-acquisition-v2", "models": []}
    if MANIFEST.exists():
        existing = json.loads(MANIFEST.read_text(encoding="utf-8"))
    existing["models"] = [model for model in existing["models"] if model["backend"] != backend] + [entry]
    existing["models"].sort(key=lambda model: model["backend"])
    MANIFEST.write_text(json.dumps(existing, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return entry


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("backend", choices=["moondream", "smolvlm2"])
    args = parser.parse_args()
    print(json.dumps(acquire(args.backend), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
