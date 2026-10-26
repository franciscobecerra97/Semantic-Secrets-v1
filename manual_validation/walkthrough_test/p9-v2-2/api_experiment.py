"""API-only P9-v2-style extraction on the frozen P9-v3 capability dataset.

Default: preflight only. No dataset substitution, model downloads, or JSON repair.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import statistics
import sys
import time
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
TASKS = ("object", "attribute", "count", "action", "relation", "scene")
MODELS = ("moondream", "smolvlm2")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def append(path, value):
    with Path(path).open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps({**value, "record_sha256": fingerprint(value)}, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def graph_config():
    """The old graph shape/scoring, with the frozen v3 vocabulary for v3 labels."""
    source = read(ROOT / "experiments/v3/config/visual_observation_v3.json")
    return {
        "entity_categories": source["entity_categories"],
        "attributes": source["attributes"], "unary_actions": source["unary_actions"],
        "binary_actions": source["binary_interactions"],
        "spatial_relations": source["derived_spatial_relations"] + list(source["inverse_normalisation"]),
        "inverse_normalisation": source["inverse_normalisation"],
        "scenes": source["scenes"], "count_buckets": source["count_buckets"],
        "maximum_nodes": source["limits"]["maximum_credential_nodes"],
    }


def evaluator():
    # Importing the evaluator imports Torch, but never loads any model weights.
    from experiments.v2 import run_p9
    return run_p9


def reference_graph(scenario, config):
    """Lossless v3 reference -> v2-shaped graph; no label inference or filtering."""
    nodes = {e["reference_id"]: {"id": e["reference_id"], "category": e["category"],
             "bbox": e["bbox_xyxy"], "attributes": {}} for e in scenario["reference_entities"]}
    graph = {"nodes": list(nodes.values()), "unary": [], "binary": [], "counts": [], "scene": None}
    scenes = []
    for atom in scenario["reference_atoms"]:
        kind, value = atom["atom_type"], atom["value"]
        source, target = atom["source_reference_id"], atom["target_reference_id"]
        if kind == "entity":
            if nodes[source]["category"] != value:
                raise ValueError("Contradictory reference entity")
        elif kind in config["attributes"]:
            if kind in nodes[source]["attributes"]:
                raise ValueError("Repeated reference attribute")
            nodes[source]["attributes"][kind] = value
        elif kind == "unary_action":
            graph["unary"].append({"node": source, "action": value})
        elif kind in ("binary_interaction", "geometry_relation"):
            graph["binary"].append({"source": source, "type": value, "target": target})
        elif kind == "count":
            graph["counts"].append({"category": atom["scope_category"], "bucket": value})
        elif kind == "scene":
            scenes.append(value)
        else:
            raise ValueError(f"Unsupported reference atom: {kind}")
    if len(scenes) != 1:
        raise ValueError("The P9-v2 graph requires exactly one reference scene per image")
    graph["scene"] = scenes[0]
    if {c["category"] for c in graph["counts"]} != {n["category"] for n in nodes.values()}:
        raise ValueError("Reference needs an explicit count for every entity category")
    return evaluator().normalise_graph(graph, config)


def load_dataset(args, config):
    required = (args.manifest, args.ground_truth, args.opportunities)
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("P9-v3 dataset not available: " + ", ".join(missing))
    from experiments.v3.runtime.dataset import audit_ground_truth_freeze
    audit = audit_ground_truth_freeze(read(args.ground_truth), args.manifest,
                                     args.opportunities, args.data_root)
    manifest = read(args.manifest)
    rows = []
    # Audit and convert every reference before sending any image to either API.
    for row in manifest["images"]:
        scenario = read(args.data_root / row["scenario_specification_path"])
        rows.append({**row, "graph": reference_graph(scenario, config)})
    if args.scope != "all":
        rows = [row for row in rows if row["split"] == args.scope]
    if not rows:
        raise ValueError("Empty image selection")
    return rows, audit


def score_answer(answer, reference, config):
    module = evaluator()
    try:
        strict = isinstance(json.loads(answer), dict)
    except (ValueError, TypeError):
        strict = False
    try:
        prediction = module.normalise_graph(module.parse_json_answer(answer), config)
        error = None
    except Exception as exc:
        prediction, error = None, f"{type(exc).__name__}: {exc}"
    return {"schema_valid": prediction is not None, "strict_raw_json": strict,
            "validation_error": error,
            "counts": module.score_image(reference, prediction, config)}


def client(backend, args):
    if backend == "moondream":
        import moondream as md
        key = os.environ.get("MOONDREAM_API_KEY")
        if not key:
            raise ValueError("Set MOONDREAM_API_KEY in your terminal before execution")
        return md.vl(api_key=key, model=args.moondream_model)
    from gradio_client import Client
    return Client(args.smol_space)


def query(backend, model, image_path, prompt, args):
    if backend == "moondream":
        from PIL import Image
        with Image.open(image_path) as image:
            # Same query call and provider defaults as manual_validation/VLM/Moondream.py.
            response = model.query(image.convert("RGB"), prompt)
        if not isinstance(response, dict) or not isinstance(response.get("answer"), str):
            raise ValueError("Moondream response has no text answer")
        return response["answer"]
    from gradio_client import handle_file
    response = model.predict(input_dict={"text": prompt, "files": [handle_file(str(image_path))]},
                             max_tokens=args.smol_max_tokens, api_name="/chat")
    if not isinstance(response, str):
        raise ValueError("SmolVLM response is not text; inspect the provider API contract")
    return response


def runtime():
    result = {"python": sys.version, "platform": platform.platform()}
    for name in ("moondream", "gradio_client", "pillow", "torch", "numpy", "scipy", "jsonschema"):
        try:
            result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result[name] = "MISSING"
    return result


def safe_error(exc):
    message = f"{type(exc).__name__}: {exc}"
    for name in ("MOONDREAM_API_KEY", "HF_TOKEN"):
        key = os.environ.get(name)
        if key:
            message = message.replace(key, "<redacted>")
    return message[:1500]


def verify_records(path, run):
    records, seen = [], set()
    if not path.exists():
        return records
    expected = {(b, r["image_id"]): r for b in run["backends"] for r in run["rows"]}
    for line in path.read_text(encoding="utf-8").splitlines():
        value = json.loads(line)  # Truncated records deliberately fail closed.
        body = {k: v for k, v in value.items() if k != "record_sha256"}
        key = (value["backend"], value["image_id"])
        if (key not in expected or key in seen or value["record_sha256"] != fingerprint(body)
                or value["run_sha256"] != fingerprint(run)
                or value["image_sha256"] != expected[key]["image_sha256"]):
            raise ValueError("Unexpected, duplicate, or modified raw observation")
        seen.add(key)
        records.append(value)
    return records


def reports(path, run, records):
    by_key = {(r["backend"], r["image_id"]): r for r in records}
    details, groups = [], []
    for backend in run["backends"]:
        for row in run["rows"]:
            record = by_key.get((backend, row["image_id"]))
            if record is not None:
                details.append({"backend": backend, "image_id": row["image_id"],
                                "split": row["split"], "stratum": row["stratum"],
                                **score_answer(record["answer"], row["graph"], run["graph_config"])})
        for split in ("all", "development", "validation"):
            for stratum in ("all", "A_controlled_geometric", "B_naturalistic_t2i"):
                selected = [r for r in run["rows"] if (split == "all" or r["split"] == split)
                            and (stratum == "all" or r["stratum"] == stratum)]
                if not selected:
                    continue
                ids = {r["image_id"] for r in selected}
                observed = [d for d in details if d["backend"] == backend and d["image_id"] in ids]
                metrics = evaluator().aggregate([d["counts"] for d in observed]) if observed else None
                valid = sum(d["schema_valid"] for d in observed)
                group = {"backend": backend, "split": split, "stratum": stratum,
                         "planned": len(selected), "observed": len(observed),
                         "missing_image_ids": sorted(ids - {d["image_id"] for d in observed}),
                         "complete": len(observed) == len(selected), "schema_valid": valid,
                         "schema_valid_rate": valid / len(observed) if observed else None,
                         "strict_raw_json_count": sum(d["strict_raw_json"] for d in observed),
                         "metrics": metrics}
                if metrics is not None:
                    totals = {k: sum(metrics[t][k] for t in TASKS) for k in ("tp", "fp", "fn")}
                    group["micro"] = {**totals, **evaluator().f1(totals)}
                    group["macro_precision"] = statistics.mean(metrics[t]["precision"] for t in TASKS)
                    group["macro_recall"] = statistics.mean(metrics[t]["recall"] for t in TASKS)
                groups.append(group)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    target = path / "reports" / stamp
    target.mkdir(parents=True)
    write(target / "validation.json", {"evidence_kind": "supplementary_api_diagnostic",
          "official_gate_decision": "not_evaluated", "groups": groups, "per_image": details})
    with (target / "precision.csv").open("x", newline="", encoding="utf-8") as stream:
        fields = ["backend", "split", "stratum", "planned", "observed", "complete", "schema_valid_rate",
                  "task", "tp", "fp", "fn", "precision", "recall", "f1"]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for group in groups:
            for task in TASKS:
                values = group["metrics"][task] if group["metrics"] else {}
                writer.writerow({**{k: group[k] for k in fields[:7]}, "task": task, **values})
    lines = ["# P9-v2-2 API precision", "", "Supplementary diagnostic; historical gates are unchanged.", "",
             "| Model | Split | Stratum | Observed/planned | Schema valid | Micro precision | Micro recall | Micro F1 |",
             "|---|---|---|---|---|---|---|---|"]
    for group in groups:
        measured = group.get("micro")
        values = [f"{measured[k]:.4f}" if measured else "not measured" for k in ("precision", "recall", "f1")]
        lines.append(f"| {group['backend']} | {group['split']} | {group['stratum']} | "
                     f"{group['observed']}/{group['planned']} | {group['schema_valid']} | " + " | ".join(values) + " |")
    (target / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    data = ROOT / "artifacts" / "downloads" / "p9_v3"
    parser.add_argument("--manifest", type=Path, default=data / "capability_manifest_v3_2.json")
    parser.add_argument("--ground-truth", type=Path, default=data / "ground_truth_freeze_v3_2.json")
    parser.add_argument("--opportunities", type=Path, default=data / "support_opportunities_v3_2.csv")
    parser.add_argument("--data-root", type=Path, help="Defaults to the manifest's folder")
    parser.add_argument("--models", choices=("both", *MODELS), default="both")
    parser.add_argument("--scope", choices=("all", "development", "validation"), default="all")
    parser.add_argument("--moondream-model", default="moondream3.1-9B-A2B")
    parser.add_argument("--smol-space", default="HuggingFaceTB/SmolVLM2")
    parser.add_argument("--smol-max-tokens", type=int, default=500, choices=range(100, 501, 50))
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--report-only", action="store_true", help="Re-score a saved run without API calls")
    args = parser.parse_args(argv)
    if (args.resume or args.report_only) and args.run_dir is None:
        parser.error("--resume and --report-only require --run-dir")
    if args.report_only and (args.execute or args.resume):
        parser.error("--report-only cannot be combined with execution or resume")
    args.data_root = (args.data_root or args.manifest.parent).resolve()
    path = (args.run_dir or HERE / "outputs" / datetime.now(timezone.utc).strftime("run-%Y%m%dT%H%M%S%fZ")).resolve()
    if not path.is_relative_to((HERE / "outputs").resolve()) or path == (HERE / "outputs").resolve():
        parser.error("--run-dir must be below p9-v2-2/outputs")
    if args.report_only:
        run = read(path / "run.json")
        current = provenance()
        if current != run["source_hashes"]:
            parser.error("Source/config changed since capture; restore the captured version before re-scoring")
        print(reports(path, run, verify_records(path / "raw.jsonl", run)))
        return 0
    config = graph_config()
    try:
        rows, dataset_audit = load_dataset(args, config)
    except (FileNotFoundError, ValueError) as exc:
        print(f"BLOCKED: {exc}\nPrecision: not measured. No API calls were made.")
        return 2
    backends = list(MODELS) if args.models == "both" else [args.models]
    print(f"{len(rows)} labelled images; {len(rows) * len(backends)} planned API calls; output: {path}")
    if not args.execute:
        print("Preflight passed. Add --execute to run; no API calls or files created.")
        return 0
    run = {"experiment_version": "p9-v2-2", "evidence_kind": "supplementary_api_diagnostic",
           "backends": backends, "rows": rows, "dataset_audit": dataset_audit,
           "dataset_hashes": {"manifest": digest(args.manifest), "ground_truth": digest(args.ground_truth),
                              "opportunities": digest(args.opportunities)},
           "graph_config": config, "prompt": (HERE / "extraction_prompt.txt").read_text(encoding="utf-8").strip(),
           "source_hashes": provenance(), "runtime": runtime(), "model_settings": {
               "moondream": {"model": args.moondream_model, "decoding": "provider defaults, matching VLM/Moondream.py"},
               "smolvlm2": {"space": args.smol_space, "max_tokens": args.smol_max_tokens, "api_name": "/chat"}},
           "hosted_weight_revisions": "not immutable or authenticated; not an exact historical reproduction",
           "early_stop_on_invalid_answer": False}
    if args.resume:
        if read(path / "run.json") != run:
            parser.error("Resume refused: dataset, source, prompt, settings, or environment changed")
    else:
        path.mkdir(parents=True, exist_ok=False)
        write(path / "run.json", run)
        write(path / "graph_config.json", config)
        (path / "extraction_prompt.txt").write_text(run["prompt"], encoding="utf-8")
    raw_path = path / "raw.jsonl"
    records = verify_records(raw_path, run)
    done = {(r["backend"], r["image_id"]) for r in records}
    failed = False
    for backend in backends:
        pending = [r for r in rows if (backend, r["image_id"]) not in done]
        if not pending:
            continue
        model = None
        try:
            model = client(backend, args)
            for index, row in enumerate(pending, 1):
                image = args.data_root / row["relative_path"]
                if digest(image) != row["image_sha256"]:
                    raise ValueError("Image changed after preflight")
                started = time.perf_counter()
                answer = query(backend, model, image, run["prompt"], args)
                record = {"backend": backend, "image_id": row["image_id"],
                          "image_sha256": row["image_sha256"], "answer": answer,
                          "elapsed_seconds": time.perf_counter() - started,
                          "captured_at_utc": datetime.now(timezone.utc).isoformat(),
                          "run_sha256": fingerprint(run)}
                append(raw_path, record)  # Preserve raw text before parsing or scoring.
                records.append(record)
                print(f"{backend} {index}/{len(pending)} {row['image_id']}: captured", flush=True)
        except Exception as exc:
            failed = True
            append(path / "execution_errors.jsonl", {"backend": backend, "error": safe_error(exc),
                   "captured_at_utc": datetime.now(timezone.utc).isoformat()})
            print(f"{backend} interrupted: {safe_error(exc)}", flush=True)
        finally:
            if model is not None and callable(getattr(model, "close", None)):
                try:
                    model.close()
                except Exception as exc:
                    failed = True
                    append(path / "execution_errors.jsonl", {"backend": backend, "stage": "cleanup",
                           "error": safe_error(exc)})
    print(f"Reports: {reports(path, run, records)}")
    return 1 if failed else 0


def provenance():
    paths = [*sorted(HERE.glob("*.py")), HERE / "extraction_prompt.txt",
             ROOT / "experiments/v2/run_p9.py"]
    paths += sorted((ROOT / "experiments/v3/config").glob("*.json"))
    return {str(path.relative_to(ROOT)): digest(path) for path in paths}


if __name__ == "__main__":
    raise SystemExit(main())
