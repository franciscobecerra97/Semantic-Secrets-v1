"""Small, inspectable helpers for a supplementary audit of immutable P9-v2.

The original prompt, parser, graph validator, and scorer are reused. The original
loaders handle the two historical models on CPU.
The original infer/analyze functions are NEVER called: their output locations are
fixed to the historical evidence directory. This module owns only manual outputs.
"""
from __future__ import annotations

import csv
import gc
import hashlib
import html
import importlib.metadata
import json
import platform
import statistics
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUTS = HERE / "outputs"
MANIFEST = ROOT / "experiments/v2/manifests/capability_v2.jsonl"
CONFIG = ROOT / "experiments/v2/config/preregistration_v2.json"
GRAPH = ROOT / "experiments/v2/config/semantic_graph_v2.json"
ACQUISITION = ROOT / "experiments/v2/manifests/model_acquisition_v2.json"
BACKENDS = ("moondream", "smolvlm2")
SCOPES = ("one", "all", "development", "validation")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def runner():
    """Importing Torch is slow; inspection/help should not load neural libraries."""
    from experiments.v2 import run_p9
    return run_p9


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write_json(path, value):
    """Exclusive creation makes accidental replacement visible."""
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def output_path(path=None, prefix="audit"):
    result = Path(path).resolve() if path else OUTPUTS / f"{prefix}-{stamp()}"
    if not result.is_relative_to(OUTPUTS.resolve()) or result == OUTPUTS.resolve():
        raise ValueError(f"Output must be a new subdirectory of {OUTPUTS}")
    return result


def source_hashes():
    paths = [MANIFEST, CONFIG, GRAPH, ACQUISITION,
             ROOT / "experiments/v2/run_p9.py", ROOT / "experiments/v2/author_p9.py"]
    paths.extend(sorted(HERE.glob("*.py")))
    return {str(path.relative_to(ROOT)): sha256(path) for path in paths}


def select_records(scope="one", image_id="cap-v2-064"):
    if scope not in SCOPES:
        raise ValueError(f"Unknown scope {scope}")
    rows = read_jsonl(MANIFEST)
    ids = [row["fixture_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate fixture IDs in source manifest")
    if scope == "one":
        selected = [row for row in rows if row["fixture_id"] == image_id]
    elif scope == "all":
        selected = rows
    else:
        selected = [row for row in rows if row["split"] == scope]
    if not selected:
        raise ValueError(f"No images selected: scope={scope}, image_id={image_id}")
    return selected


def image_path(row):
    path = (ROOT / row["image_relpath"]).resolve()
    if not path.is_relative_to((ROOT / "artifacts/downloads/p9_v2/capability").resolve()):
        raise ValueError("Manifest image path escapes the P9-v2 capability folder")
    if not path.is_file() or sha256(path) != row["image_sha256"]:
        raise ValueError(f"Missing or hash-mismatched image: {row['fixture_id']}")
    return path


def model_entries(backends):
    entries = {row["backend"]: row for row in read_json(ACQUISITION)["models"]}
    result = {}
    for backend in backends:
        entry = entries[backend]
        path = (ROOT / entry["snapshot_relpath"]).resolve()
        if not path.is_relative_to((ROOT / "artifacts/downloads/p9_v2/models").resolve()):
            raise ValueError("Model snapshot escapes the P9-v2 model folder")
        if entry["config_sha256"] != sha256(CONFIG):
            raise ValueError("Model acquisition config hash mismatch")
        if not path.is_dir() or not list(path.glob("*.safetensors")):
            raise ValueError(f"Local weights missing for {backend}: {path}. No download is attempted.")
        if backend == "moondream":
            review = entry.get("remote_code_review", {})
            if not review.get("approved"):
                raise ValueError("Moondream source review is not approved")
            for item in review["python_files"]:
                if sha256(path / item["name"]) != item["sha256"]:
                    raise ValueError(f"Reviewed Moondream source changed: {item['name']}")
        result[backend] = entry
    return result


def runtime_versions():
    versions = {"python": sys.version, "platform": platform.platform()}
    for package in ("torch", "transformers", "tokenizers", "numpy", "pillow", "psutil", "scipy", "accelerate"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "MISSING"
    return versions


def make_plan(rows, backends, repeat_validation=False):
    tasks = [{"fixture_id": row["fixture_id"], "pass": "primary"} for row in rows]
    if repeat_validation:
        tasks += [{"fixture_id": row["fixture_id"], "pass": "repeat"}
                  for row in rows if row["split"] == "validation"]
    return {backend: tasks for backend in backends}


def receipt(rows, plan, kind, **extra):
    return {"schema_version": "manual-p9-v2-audit-v1", "evidence_kind": kind,
            "official_gate_decision": "not_evaluated_by_manual_audit",
            "source_hashes": source_hashes(), "plan": plan,
            "image_hashes": {row["fixture_id"]: row["image_sha256"] for row in rows},
            **extra}


def prepare_run(path, expected, resume=False):
    path = output_path(path)
    if path.exists():
        if not resume:
            raise ValueError(f"Run already exists: {path}. Choose a new directory or use --resume.")
        if read_json(path / "run.json") != expected:
            raise ValueError("Resume refused: selection, source, configuration, or provenance changed")
    else:
        if resume:
            raise ValueError("Cannot resume a run that does not exist")
        path.mkdir(parents=True)
        write_json(path / "run.json", expected)
        write_json(path / "environment.json", runtime_versions())
    return path


def observation_key(run, backend, fixture_id, pass_name):
    return fingerprint({"receipt": fingerprint(run), "backend": backend,
                        "fixture_id": fixture_id, "pass": pass_name})


def verified_observations(path, run, backend):
    path = Path(path)
    observations = read_jsonl(path) if path.exists() else []
    expected = {(item["fixture_id"], item["pass"]) for item in run["plan"][backend]}
    seen = set()
    for item in observations:
        pair = (item["fixture_id"], item["pass"])
        if pair not in expected or pair in seen or item["backend"] != backend:
            raise ValueError("Unexpected or duplicate observation; inspect the raw file")
        if item.get("audit_key") != observation_key(run, backend, *pair):
            raise ValueError("Observation provenance key mismatch")
        if item.get("image_sha256") != run["image_hashes"][pair[0]]:
            raise ValueError("Observation image hash mismatch")
        body = {key: value for key, value in item.items() if key != "record_sha256"}
        if item.get("record_sha256") != fingerprint(body):
            raise ValueError("Observation contents changed after capture")
        seen.add(pair)
    return observations


def append_observation(path, value):
    value = {**value, "record_sha256": fingerprint(value)}
    with Path(path).open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, sort_keys=True) + "\n")
        stream.flush()


def parse_and_score(answer, reference, module=None):
    """Format validation precedes semantic scoring. Invalid output stays a failure."""
    module = module or runner()
    config = read_json(GRAPH)
    try:
        json.loads(answer)
        strict_json = True
    except (ValueError, TypeError):
        strict_json = False
    try:
        prediction = module.normalise_graph(module.parse_json_answer(answer), config)
        error = None
    except Exception as exc:
        prediction = None
        error = f"{type(exc).__name__}: {exc}"
    # Both sides need inverse-relation normalization before comparison.
    ground = module.normalise_graph(reference, config)
    scores = module.score_image(ground, prediction, config)
    return {"schema_valid": prediction is not None, "strict_raw_json": strict_json,
            "error": error, "parsed_graph": prediction, "counts": scores,
            "metrics": module.aggregate([scores])}


def run_inference(rows, backends, path, repeat_validation=False, resume=False):
    """Step 1 verify -> Step 2 load once -> Step 3 predict -> Step 4 save raw text.

    Labels are never passed to the extractor. This deliberately completes the
    selected tasks after invalid responses instead of using the old early stop.
    """
    entries, device = model_entries(backends), "cpu"
    for row in rows:
        image_path(row)
    plan = make_plan(rows, backends, repeat_validation)
    run = receipt(rows, plan, "fresh_model_inference", models=entries,
                  model_weight_bytes_independently_authenticated=False,
                  device=device, early_stop_on_invalid=False,
                  runtime=runtime_versions())
    path = prepare_run(path, run, resume)
    module = runner()
    from PIL import Image
    prompt = module.extraction_prompt(read_json(GRAPH))
    prompt_path = path / "extraction_prompt.txt"
    if not prompt_path.exists():
        prompt_path.write_text(prompt, encoding="utf-8")
    by_id = {row["fixture_id"]: row for row in rows}
    load_errors = []
    for backend in backends:
        raw_path = path / f"{backend}.jsonl"
        cached = verified_observations(raw_path, run, backend)
        done = {(item["fixture_id"], item["pass"]) for item in cached}
        pending = [task for task in plan[backend] if (task["fixture_id"], task["pass"]) not in done]
        print(f"\n{backend}: {len(pending)} pending, {len(done)} cached; weights stay unchanged", flush=True)
        if not pending:
            continue
        extractor = None
        try:
            started = time.perf_counter()
            extractor = module.load_extractor(backend, prompt)
            print(f"Loaded in {time.perf_counter() - started:.1f}s. Starting image inference.", flush=True)
            for index, task in enumerate(pending, 1):
                row = by_id[task["fixture_id"]]
                source = image_path(row)
                started = time.perf_counter()
                answer, error, graph, stage = "", None, None, "inference"
                with module.PeakRSS() as memory:
                    try:
                        with Image.open(source) as image:
                            answer = extractor(image.convert("RGB"))
                        if not isinstance(answer, str):
                            raise ValueError("Extractor did not return a text answer")
                        stage = "output_validation"
                        graph = module.normalise_graph(module.parse_json_answer(answer), read_json(GRAPH))
                    except Exception as exc:
                        error = f"{type(exc).__name__}: {exc}"
                observation = {"backend": backend, **task, "split": row["split"],
                               "fixture_style": row["fixture_style"], "answer": answer,
                               "parsed_graph": graph, "schema_valid": graph is not None,
                               "error": error, "failure_stage": stage if error else None,
                               "elapsed_seconds": time.perf_counter() - started,
                               "peak_rss_bytes": memory.peak,
                               "peak_gpu_allocated_bytes": 0,
                               "model_id": entries[backend]["model_id"], "revision": entries[backend]["revision"],
                               "image_sha256": row["image_sha256"],
                               "audit_key": observation_key(run, backend, task["fixture_id"], task["pass"])}
                append_observation(raw_path, observation)
                print(f"{index}/{len(pending)} {row['fixture_id']} {task['pass']}: "
                      f"valid={graph is not None}, seconds={observation['elapsed_seconds']:.1f}, error={error}", flush=True)
        except Exception as exc:
            # Setup failures must not masquerade as a model's answer on every image.
            load_errors.append({"backend": backend, "error": f"{type(exc).__name__}: {exc}"})
            print(f"Backend interrupted; incomplete run retained: {exc}", flush=True)
        finally:
            del extractor
            gc.collect()
    if load_errors:
        write_json(path / f"execution_errors-{stamp()}.json", load_errors)
    return path, not load_errors


def summarize(rows, observations, backend, scope, module=None):
    """Score observed primary answers; missing images remain explicit, never successes."""
    module = module or runner()
    selected = {row["fixture_id"]: row for row in rows}
    primary = {item["fixture_id"]: item for item in observations
               if item["pass"] == "primary" and item["fixture_id"] in selected}
    repeat = {item["fixture_id"]: item for item in observations
              if item["pass"] == "repeat" and item["fixture_id"] in selected}
    details, scores, repeat_checks = [], [], []
    mismatches = []
    for fixture_id, observation in primary.items():
        result = parse_and_score(observation["answer"], selected[fixture_id]["graph"], module)
        if observation["schema_valid"] != result["schema_valid"] or observation.get("parsed_graph") != result["parsed_graph"]:
            mismatches.append(fixture_id)
        if fixture_id in repeat:
            second = parse_and_score(repeat[fixture_id]["answer"], selected[fixture_id]["graph"], module)
            equal = (result["schema_valid"] and second["schema_valid"] and
                     module.canonical_graph(result["parsed_graph"]) == module.canonical_graph(second["parsed_graph"]))
            repeat_checks.append(bool(equal))
        scores.append(result["counts"])
        details.append({"backend": backend, "fixture_id": fixture_id, "split": selected[fixture_id]["split"],
                        "fixture_style": selected[fixture_id]["fixture_style"], **result,
                        "elapsed_seconds": observation.get("elapsed_seconds"),
                        "failure_stage": observation.get("failure_stage"),
                        "original_execution_error": observation.get("error")})
    valid = sum(item["schema_valid"] for item in details)
    invalid = len(details) - valid
    denominator = len(selected)
    threshold = read_json(CONFIG)["extractor_screen"]["advance"]["schema_valid_rate_min"]
    metrics = module.aggregate(scores) if scores else None
    valid_scores = [item["counts"] for item in details if item["schema_valid"]]
    times = [item["elapsed_seconds"] for item in details if isinstance(item["elapsed_seconds"], (int, float))]
    return {"backend": backend, "scope": scope, "planned_images": denominator,
            "observed_images": len(details), "complete_primary": len(details) == denominator,
            "missing_image_ids": sorted(set(selected) - set(primary)),
            "valid": valid, "invalid": invalid,
            "observed_schema_valid_rate": valid / len(details) if details else None,
            "strict_raw_json_count": sum(item["strict_raw_json"] for item in details),
            "metrics_on_observed_images_failures_count_as_false_negatives": metrics,
            "metrics_on_valid_outputs_only_diagnostic": module.aggregate(valid_scores) if valid_scores else None,
            "revalidated_record_disagreements": mismatches,
            "repeat_pairs_observed": len(repeat_checks),
            "valid_canonical_repeat_equal": sum(repeat_checks),
            "median_observed_seconds": statistics.median(times) if times else None,
            "hypothetical_format_check_only": {"threshold": threshold,
                "denominator": denominator, "maximum_possible_valid_rate": (denominator - invalid) / denominator,
                "pass_still_possible": (denominator - invalid) / denominator >= threshold,
                "official_gate_result": "not_recomputed_or_changed"},
            "details": details}


def validate_run(path, scope="all"):
    path = output_path(path)
    run = read_json(path / "run.json")
    current_sources = source_hashes()
    source_changes = {name: {"captured": run["source_hashes"].get(name), "current": current_sources.get(name)}
                      for name in set(run["source_hashes"]) | set(current_sources)
                      if run["source_hashes"].get(name) != current_sources.get(name)}
    if any(not name.replace("\\", "/").startswith("manual_validation/") for name in source_changes):
        raise ValueError("Historical scoring/configuration source changed; restore it before validation")
    module = runner()
    all_rows = read_jsonl(MANIFEST)
    by_id = {row["fixture_id"]: row for row in all_rows}
    reports = []
    for backend, tasks in run["plan"].items():
        ids = {task["fixture_id"] for task in tasks if task["pass"] == "primary"}
        selected = [row for row in all_rows if row["fixture_id"] in ids and (scope == "all" or row["split"] == scope)]
        if not selected:
            continue
        for row in selected:
            image_path(row)
        observations = verified_observations(path / f"{backend}.jsonl", run, backend)
        if any(item["split"] != by_id[item["fixture_id"]]["split"] for item in observations):
            raise ValueError("Observation split disagrees with the source manifest")
        reports.append(summarize(selected, observations, backend, scope, module))
    if not reports:
        raise ValueError("No planned images match this report scope")
    report_dir = path / "reports" / f"{scope}-{stamp()}"
    report_dir.mkdir(parents=True)
    write_json(report_dir / "validation.json", {"evidence_kind": run["evidence_kind"],
               "official_gate_decision": "unchanged_historical_failure", "backends": reports,
               "manual_validator_source_changes_since_capture": source_changes,
               "validation_source_hashes": current_sources,
               "uncertainty": "No confidence intervals: images share eight templates; point diagnostics only."})
    fields = ["backend", "fixture_id", "split", "fixture_style", "schema_valid", "strict_raw_json",
              "failure_stage", "original_execution_error", "error", "elapsed_seconds"]
    with (report_dir / "per_image.csv").open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(item for report in reports for item in report["details"])
    lines = ["# Manual P9-v2 validation", "", f"Evidence: {run['evidence_kind']}", "",
             "Historical P9-v2 remains failed. These are supplementary point diagnostics.", "",
             f"Manual-tool source changes since capture: {len(source_changes)} (recorded in validation.json).", "",
             "| Backend | Planned | Observed | Valid | Invalid | Complete |", "|---|---:|---:|---:|---:|---|"]
    for report in reports:
        lines.append(f"| {report['backend']} | {report['planned_images']} | {report['observed_images']} | "
                     f"{report['valid']} | {report['invalid']} | {report['complete_primary']} |")
        lines.extend(["", f"{report['backend']} missing images: {report['missing_image_ids']}",
                      f"Revalidation disagreements: {report['revalidated_record_disagreements']}"])
    lines.extend(["", "Invalid responses count every reference fact as a false negative. Missing images are listed,",
                  "not silently scored or dropped. Valid-output-only metrics are conditional diagnostics.",
                  "No confidence intervals, official full gate, or generalisation claim is produced.", ""])
    (report_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"\nDetailed reports: {report_dir}")
    return report_dir


def inspect_dataset(path, fixture_id="cap-v2-064", gallery=False, recreate=False):
    """Inspect source data without inference; rendering creates only a manual copy."""
    from PIL import Image, ImageDraw
    from experiments.v2 import author_p9
    rows = read_jsonl(MANIFEST)
    module = runner()
    config = read_json(GRAPH)
    selected = next((row for row in rows if row["fixture_id"] == fixture_id), None)
    if selected is None:
        raise ValueError(f"Unknown fixture ID: {fixture_id}")
    for row in rows:
        image_path(row)
        module.normalise_graph(row["graph"], config)
    path = output_path(path, "dataset")
    path.mkdir(parents=True, exist_ok=False)
    prompt = module.extraction_prompt(config)
    example = prompt.split("using exactly this shape: ", 1)[1].split(". Boxes", 1)[0]
    try:
        module.normalise_graph(json.loads(example), config)
        example_error = None
    except Exception as exc:
        example_error = f"{type(exc).__name__}: {exc}"
    families = defaultdict(lambda: {"splits": set(), "styles": set(), "images": 0})
    for row in rows:
        # This is the author's index % 8 template rule, not an invented cluster.
        template = int(row["fixture_id"].rsplit("-", 1)[1]) % 8
        families[template]["splits"].add(row["split"])
        families[template]["styles"].add(row["fixture_style"])
        families[template]["images"] += 1
    family_report = {str(key): {name: sorted(value) if isinstance(value, set) else value
                               for name, value in facts.items()} for key, facts in families.items()}
    report = {"images": len(rows), "split_counts": dict(Counter(row["split"] for row in rows)),
              "style_counts": dict(Counter(row["fixture_style"] for row in rows)),
              "image_hashes_verified": True, "reference_graphs_pass_original_validator": True,
              "creation_method": "Python/Pillow drawings, not text-to-image AI",
              "template_families": family_report,
              "prompt_example_passes_original_validator": example_error is None,
              "prompt_example_validation_error": example_error,
              "findings": [
                  "Prompt's illustrative graph references n2 but declares only n1. No causal effect is established.",
                  "Eight authored templates occur in both splits; images are not independent scene families.",
                  "Each template has one drawing style, so style and template are confounded.",
                  "Action labels are declared in scenarios; renderer does not use unary/binary fields to set poses.",
                  "Declared boxes can differ from full visible glyph extents. Audit localisation references visually.",
                  "The original parser can accept fenced or surrounding text: strict raw JSON is a separate check.",
                  "A 384-token ceiling is fixed; truncation is retained, not silently repaired.",
                  "Reference validity is a structural check, not proof that labels describe the rendered image."],
              "source_hashes": source_hashes()}
    write_json(path / "dataset_audit.json", report)
    write_json(path / "reference.json", selected)
    (path / "extraction_prompt.txt").write_text(prompt, encoding="utf-8")
    with Image.open(image_path(selected)) as source:
        source.convert("RGB").save(path / "original.png")
    def overlay(row, destination):
        with Image.open(image_path(row)) as source:
            image = source.convert("RGB")
        draw = ImageDraw.Draw(image)
        for node in row["graph"]["nodes"]:
            box = [int(round(value * 512)) for value in node["bbox"]]
            draw.rectangle(box, outline="magenta", width=2)
            draw.text((box[0], max(0, box[1] - 13)), f"{node['id']}: {node['category']}", fill="black")
        image.save(destination)
    overlay(selected, path / "reference_boxes.png")
    if recreate:
        recreated = path / "recreated.png"
        author_p9.render_fixture(selected, recreated)
        write_json(path / "recreation_check.json", {
            "matches_original_png_hash": sha256(recreated) == selected["image_sha256"],
            "original_sha256": selected["image_sha256"], "recreated_sha256": sha256(recreated),
            "note": "Different Pillow/runtime versions can change encoded bytes; original is untouched."})
    if gallery:
        thumbs = path / "gallery_images"
        thumbs.mkdir()
        cards = []
        for row in rows:
            destination = thumbs / f"{row['fixture_id']}.png"
            overlay(row, destination)
            cards.append(f"<article><h2>{html.escape(row['fixture_id'])} ({row['split']})</h2>"
                         f"<img width='300' src='gallery_images/{destination.name}' alt='Reference boxes'>"
                         f"<pre>{html.escape(json.dumps(row['graph'], indent=2))}</pre></article>")
        (path / "gallery.html").write_text("<!doctype html><meta charset='utf-8'><title>P9-v2 reference audit</title>"
            "<style>body{font:15px sans-serif;margin:24px}main{display:flex;flex-wrap:wrap;gap:24px}"
            "article{border:1px solid #bbb;padding:12px;width:330px}pre{white-space:pre-wrap}</style>"
            "<h1>Reference labels beside the rendered images</h1><p>Magenta boxes are declared reference boxes. "
            "Check visible facts manually; these are not model predictions.</p><main>" + "".join(cards) + "</main>", encoding="utf-8")
    with (path / "label_review.csv").open("x", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["fixture_id", "split", "objects_visible", "boxes_appropriate", "actions_visible", "scene_supported", "notes"])
        writer.writerows([row["fixture_id"], row["split"], "", "", "", "", ""] for row in rows)
    print(json.dumps(report, indent=2))
    print(f"\nInspection files: {path}")
    return path


def replay_history(path):
    """Reparse the retained answers, without neural inference or historical writes."""
    source = ROOT / "results/p9-v2/raw"
    files = {"moondream": [source / "moondream_smoke2.jsonl", source / "moondream_futility.jsonl"],
             "smolvlm2": [source / "smolvlm2_smoke.jsonl", source / "smolvlm2_futility.jsonl"]}
    originals = {backend: [row for file in paths for row in read_jsonl(file)] for backend, paths in files.items()}
    ids = {row["fixture_id"] for rows in originals.values() for row in rows}
    rows = [row for row in read_jsonl(MANIFEST) if row["fixture_id"] in ids]
    plan = {backend: [{"fixture_id": row["fixture_id"], "pass": row["pass"]} for row in records]
            for backend, records in originals.items()}
    run = receipt(rows, plan, "reparsed_historical_answers_not_new_inference",
                  historical_sources={str(file.relative_to(ROOT)): sha256(file) for paths in files.values() for file in paths},
                  excluded="moondream_smoke.jsonl contains pre-fix loader errors, not completed model answers")
    path = prepare_run(path, run)
    for backend, records in originals.items():
        for row in records:
            append_observation(path / f"{backend}.jsonl", {**row, "audit_key": observation_key(run, backend, row["fixture_id"], row["pass"])})
    validate_run(path)
    # Historical gate denominator must stay 32, even though this replay has 3/image.
    checks = []
    threshold = read_json(CONFIG)["extractor_screen"]["advance"]["schema_valid_rate_min"]
    total = sum(row["split"] == "validation" for row in read_jsonl(MANIFEST))
    for backend, records in originals.items():
        validation = [row for row in records if row["split"] == "validation" and row["pass"] == "primary"]
        invalid = sum(not row["schema_valid"] for row in validation)
        saved = read_json(ROOT / f"results/p9-v2/aggregate/{backend}_capability_v2.json")
        best = (total - invalid) / total
        matches = (saved["validation_images_planned"] == total and saved["schema_invalid_observed"] == invalid
                   and saved["best_case_if_every_unobserved_image_passed"]["schema_valid_rate"] == best
                   and saved["fatal_checks"]["schema_valid_rate"]["threshold"] == threshold
                   and saved["advance"] is False and best < threshold)
        checks.append({"backend": backend, "planned_validation_images": total, "observed": len(validation),
                       "invalid": invalid, "maximum_possible_validity": best,
                       "required": threshold, "matches_historical_summary": matches})
    write_json(path / "historical_gate_arithmetic.json", checks)
    print(json.dumps(checks, indent=2))
    return path


def teaching_examples(path):
    """Artificial answers test the evaluator, not the models."""
    from copy import deepcopy
    row = select_records()[0]
    perfect = deepcopy(row["graph"])
    wrong = deepcopy(perfect)
    wrong["scene"] = "office" if perfect["scene"] != "office" else "beach"
    missing_count = deepcopy(perfect)
    missing_count["counts"] = []
    answers = {"perfect_reference": json.dumps(perfect), "valid_but_wrong_scene": json.dumps(wrong),
               "malformed_json": '{"nodes":[', "fenced_valid_json": "```json\n" + json.dumps(perfect) + "\n```",
               "missing_counts_validator_gap": json.dumps(missing_count)}
    path = output_path(path, "examples")
    path.mkdir(parents=True, exist_ok=False)
    index = []
    for name, answer in answers.items():
        run = receipt([row], make_plan([row], ["teaching_demo"]), "artificial_teaching_example_not_model_output", case=name)
        case_path = prepare_run(path / name, run)
        result = parse_and_score(answer, row["graph"])
        (case_path / "answer.txt").write_text(answer, encoding="utf-8")
        append_observation(case_path / "teaching_demo.jsonl", {"backend": "teaching_demo", "fixture_id": row["fixture_id"],
            "pass": "primary", "split": row["split"], "answer": answer, "parsed_graph": result["parsed_graph"],
            "schema_valid": result["schema_valid"], "error": result["error"], "image_sha256": row["image_sha256"],
            "audit_key": observation_key(run, "teaching_demo", row["fixture_id"], "primary")})
        validate_run(case_path)
        index.append({"case": name, "schema_valid": result["schema_valid"], "strict_raw_json": result["strict_raw_json"],
                      "macro_f1": result["metrics"]["macro"]["f1"]})
    write_json(path / "examples_index.json", index)
    print(json.dumps(index, indent=2))
    return path
