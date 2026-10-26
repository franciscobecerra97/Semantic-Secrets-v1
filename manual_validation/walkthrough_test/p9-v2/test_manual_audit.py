"""Regression checks for the manual auditor; no real model is loaded."""
from copy import deepcopy
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import audit_common as audit


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(audit, "OUTPUTS", tmp_path / "outputs")
    return audit.OUTPUTS


def raw_record(run, row, answer, backend="teaching_demo", pass_name="primary"):
    result = audit.parse_and_score(answer, row["graph"])
    return {"backend": backend, "fixture_id": row["fixture_id"], "pass": pass_name,
            "split": row["split"], "answer": answer, "parsed_graph": result["parsed_graph"],
            "schema_valid": result["schema_valid"], "error": result["error"],
            "image_sha256": row["image_sha256"],
            "audit_key": audit.observation_key(run, backend, row["fixture_id"], pass_name)}


def test_selections_and_repeat_counts():
    assert len(audit.select_records("all")) == 96
    assert len(audit.select_records("development")) == 64
    assert len(audit.select_records("validation")) == 32
    assert audit.select_records()[0]["fixture_id"] == "cap-v2-064"
    plan = audit.make_plan(audit.select_records("all"), audit.BACKENDS, True)
    assert all(len(tasks) == 128 for tasks in plan.values())
    with pytest.raises(ValueError, match="No images"):
        audit.select_records("one", "not-an-image")


def test_format_and_semantic_correctness_are_separate():
    row = audit.select_records()[0]
    perfect = audit.parse_and_score(json.dumps(row["graph"]), row["graph"])
    assert perfect["schema_valid"]
    assert perfect["metrics"]["macro"]["f1"] == 1
    wrong = deepcopy(row["graph"])
    wrong["scene"] = "office"
    result = audit.parse_and_score(json.dumps(wrong), row["graph"])
    assert result["schema_valid"]
    assert result["metrics"]["scene"]["f1"] == 0
    assert result["metrics"]["macro"]["f1"] < 1


def test_malformed_answer_counts_missed_reference_facts():
    row = audit.select_records()[0]
    result = audit.parse_and_score("not json", row["graph"])
    assert not result["schema_valid"]
    assert result["counts"]["object"]["fn"] == len(row["graph"]["nodes"])
    assert result["metrics"]["macro"]["f1"] == 0


def test_fences_and_missing_counts_expose_original_validator_behaviour():
    row = audit.select_records()[0]
    fenced = audit.parse_and_score("```json\n" + json.dumps(row["graph"]) + "\n```", row["graph"])
    assert fenced["schema_valid"] and not fenced["strict_raw_json"]
    graph = deepcopy(row["graph"])
    graph["counts"] = []
    result = audit.parse_and_score(json.dumps(graph), row["graph"])
    assert result["schema_valid"]
    assert result["metrics"]["count"]["recall"] == 0


def test_missing_images_do_not_become_observed_successes():
    rows = audit.select_records("validation")
    run = audit.receipt(rows, audit.make_plan(rows, ["teaching_demo"]), "test")
    observation = raw_record(run, rows[0], "bad")
    summary = audit.summarize(rows, [observation], "teaching_demo", "validation")
    assert summary["planned_images"] == 32
    assert summary["observed_images"] == 1
    assert len(summary["missing_image_ids"]) == 31
    assert summary["observed_schema_valid_rate"] == 0
    assert summary["hypothetical_format_check_only"]["maximum_possible_valid_rate"] == 31 / 32
    assert summary["complete_primary"] is False


def test_output_cannot_target_historical_results(sandbox):
    with pytest.raises(ValueError, match="Output must"):
        audit.output_path(audit.ROOT / "results/p9-v2")
    with pytest.raises(ValueError, match="Output must"):
        audit.output_path(sandbox)


def test_raw_duplicates_and_contents_changes_fail_closed(sandbox):
    row = audit.select_records()[0]
    run = audit.receipt([row], audit.make_plan([row], ["teaching_demo"]), "test")
    path = audit.prepare_run(sandbox / "records", run)
    raw = path / "teaching_demo.jsonl"
    record = raw_record(run, row, "bad")
    audit.append_observation(raw, record)
    assert len(audit.verified_observations(raw, run, "teaching_demo")) == 1
    audit.append_observation(raw, record)
    with pytest.raises(ValueError, match="duplicate"):
        audit.verified_observations(raw, run, "teaching_demo")
    lines = raw.read_text().splitlines()
    changed = json.loads(lines[0])
    changed["answer"] = "edited after capture"
    raw.write_text(json.dumps(changed) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="contents changed"):
        audit.verified_observations(raw, run, "teaching_demo")


def test_resume_requires_identical_receipt(sandbox):
    row = audit.select_records()[0]
    run = audit.receipt([row], audit.make_plan([row], ["teaching_demo"]), "test")
    path = audit.prepare_run(sandbox / "resume", run)
    assert audit.prepare_run(path, run, resume=True) == path
    changed = {**run, "source_hashes": {"changed": "hash"}}
    with pytest.raises(ValueError, match="Resume refused"):
        audit.prepare_run(path, changed, resume=True)
    with pytest.raises(ValueError, match="already exists"):
        audit.prepare_run(path, run)


def test_revalidation_detects_disagreement_and_invalid_repeats(sandbox):
    row = audit.select_records()[0]
    run = audit.receipt([row], audit.make_plan([row], ["teaching_demo"], True), "test")
    path = audit.prepare_run(sandbox / "disagreement", run)
    first = raw_record(run, row, "bad")
    first["schema_valid"] = True  # Deliberately inconsistent capture flag.
    audit.append_observation(path / "teaching_demo.jsonl", first)
    audit.append_observation(path / "teaching_demo.jsonl", raw_record(run, row, "bad", pass_name="repeat"))
    report = audit.read_json(audit.validate_run(path) / "validation.json")["backends"][0]
    assert report["revalidated_record_disagreements"] == [row["fixture_id"]]
    assert report["repeat_pairs_observed"] == 1
    assert report["valid_canonical_repeat_equal"] == 0


def test_fake_inference_both_models_resume_without_loading(sandbox, monkeypatch):
    row = audit.select_records()[0]
    original = audit.runner()
    loads = []
    def load(backend, prompt):
        loads.append(backend)
        assert prompt == original.extraction_prompt(audit.read_json(audit.GRAPH))
        def predict(image):
            assert image.mode == "RGB" and image.size == (512, 512)
            return json.dumps(row["graph"])
        return predict
    fake = SimpleNamespace(**{name: getattr(original, name) for name in (
        "extraction_prompt", "PeakRSS", "normalise_graph", "parse_json_answer")}, load_extractor=load)
    monkeypatch.setattr(audit, "runner", lambda: fake)
    monkeypatch.setattr(audit, "model_entries", lambda backends: {
        backend: {"model_id": "fake-for-test", "revision": "test"} for backend in backends})
    before = {path: audit.sha256(path) for path in (audit.MANIFEST, audit.CONFIG, audit.GRAPH, audit.ACQUISITION)}
    path, success = audit.run_inference([row], audit.BACKENDS, sandbox / "inference")
    assert success and loads == list(audit.BACKENDS)
    for backend in audit.BACKENDS:
        records = audit.verified_observations(path / f"{backend}.jsonl", audit.read_json(path / "run.json"), backend)
        assert len(records) == 1 and records[0]["schema_valid"]
    audit.run_inference([row], audit.BACKENDS, path, resume=True)
    assert loads == list(audit.BACKENDS)
    assert before == {path: audit.sha256(path) for path in before}


def test_loader_failure_stays_missing_not_invalid_model_answer(sandbox, monkeypatch):
    original = audit.runner()
    def fail(*_):
        raise RuntimeError("test loader unavailable")
    monkeypatch.setattr(audit, "runner", lambda: SimpleNamespace(extraction_prompt=original.extraction_prompt, load_extractor=fail))
    monkeypatch.setattr(audit, "model_entries", lambda backends: {backend: {} for backend in backends})
    path, success = audit.run_inference(audit.select_records(), ["moondream"], sandbox / "load-failure")
    assert not success
    assert not (path / "moondream.jsonl").exists()
    assert list(path.glob("execution_errors-*.json"))


def test_inspection_recreation_and_history_do_not_change_originals(sandbox):
    protected = [audit.MANIFEST, audit.CONFIG, audit.GRAPH, audit.ACQUISITION]
    protected += list((audit.ROOT / "results/p9-v2").rglob("*.json*"))
    before = {path: audit.sha256(path) for path in protected}
    inspection = audit.inspect_dataset(sandbox / "inspect", recreate=True)
    report = audit.read_json(inspection / "dataset_audit.json")
    assert report["images"] == 96
    assert not report["prompt_example_passes_original_validator"]
    assert all(len(family["splits"]) == 2 for family in report["template_families"].values())
    replay = audit.replay_history(sandbox / "replay")
    assert all(item["matches_historical_summary"] for item in audit.read_json(replay / "historical_gate_arithmetic.json"))
    assert before == {path: audit.sha256(path) for path in protected}
