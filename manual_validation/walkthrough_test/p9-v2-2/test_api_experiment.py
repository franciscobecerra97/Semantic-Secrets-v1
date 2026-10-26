"""Software checks only: no real API calls or model loading."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

spec = importlib.util.spec_from_file_location("p9_v2_2_api", Path(__file__).with_name("api_experiment.py"))
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)


def scenario():
    def atom(kind, value, source=None, target=None, category=None):
        return {"atom_type": kind, "value": value, "source_reference_id": source,
                "target_reference_id": target, "scope_category": category}
    return {"reference_entities": [
        {"reference_id": "cat1", "category": "cat", "bbox_xyxy": [0.1, 0.1, 0.4, 0.5]},
        {"reference_id": "hat1", "category": "hat", "bbox_xyxy": [0.5, 0.1, 0.8, 0.4]}],
        "reference_atoms": [atom("entity", "cat", "cat1"), atom("entity", "hat", "hat1"),
            atom("colour", "pink", "hat1"), atom("material", "fabric", "hat1"),
            atom("pattern", "striped", "hat1"), atom("unary_action", "walking", "cat1"),
            atom("binary_interaction", "wearing", "cat1", "hat1"),
            atom("geometry_relation", "left_of", "cat1", "hat1"),
            atom("count", "1", category="cat"), atom("count", "1", category="hat"),
            atom("scene", "shop")]}


def test_conversion_and_scoring_preserve_new_v3_labels():
    config = api.graph_config()
    graph = api.reference_graph(scenario(), config)
    result = api.score_answer(json.dumps(graph), graph, config)
    assert result["schema_valid"] and result["strict_raw_json"]
    assert all(api.evaluator().f1(counts)["f1"] == 1 for counts in result["counts"].values())
    assert graph["nodes"][1]["attributes"] == {"colour": "pink", "material": "fabric", "pattern": "striped"}
    assert graph["scene"] == "shop"


def test_prompt_vocabulary_matches_scoring_config():
    config = api.graph_config()
    prompt = (api.HERE / "extraction_prompt.txt").read_text(encoding="utf-8").strip()
    groups = {part.split("=", 1)[0].strip(): part.split("=", 1)[1].rstrip(".").split(",")
              for part in prompt[prompt.index("categories="):].split("; ")}
    for label, expected in (("categories", config["entity_categories"]),
                            ("colours", config["attributes"]["colour"]),
                            ("sizes", config["attributes"]["size"]),
                            ("materials", config["attributes"]["material"]),
                            ("patterns", config["attributes"]["pattern"]),
                            ("unary", config["unary_actions"]),
                            ("binary", config["binary_actions"] + config["spatial_relations"]),
                            ("count buckets", config["count_buckets"]), ("scenes", config["scenes"])):
        assert groups[label] == expected
    example = prompt.split("using exactly this shape: ", 1)[1].split(". The example", 1)[0]
    api.evaluator().normalise_graph(json.loads(example), config)


def test_reference_incompatibility_blocks_instead_of_excluding_facts():
    config = api.graph_config()
    value = scenario()
    value["reference_atoms"] = [a for a in value["reference_atoms"] if a["atom_type"] != "scene"]
    with pytest.raises(ValueError, match="exactly one reference scene"):
        api.reference_graph(value, config)
    value = scenario()
    value["reference_atoms"] = [a for a in value["reference_atoms"] if a["atom_type"] != "count"]
    with pytest.raises(ValueError, match="explicit count"):
        api.reference_graph(value, config)


def test_invalid_and_wrong_graphs_are_not_schema_successes_or_perfect_scores():
    config = api.graph_config()
    graph = api.reference_graph(scenario(), config)
    invalid = api.score_answer("not JSON", graph, config)
    assert not invalid["schema_valid"]
    assert invalid["counts"]["object"] == {"tp": 0, "fp": 0, "fn": 2}
    wrong = deepcopy(graph)
    wrong["scene"] = "park"
    result = api.score_answer(json.dumps(wrong), graph, config)
    assert result["schema_valid"] and result["counts"]["scene"] == {"tp": 0, "fp": 1, "fn": 1}


def test_missing_dataset_blocks_before_any_client_is_created(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(api, "client", lambda *_: pytest.fail("Must not contact API"))
    code = api.main(["--manifest", str(tmp_path / "missing.json"), "--execute"])
    assert code == 2 and "Precision: not measured" in capsys.readouterr().out


@pytest.fixture
def fake_run(tmp_path, monkeypatch):
    home = tmp_path / "p9-v2-2"
    home.mkdir()
    (home / "extraction_prompt.txt").write_text("test prompt", encoding="utf-8")
    config = api.graph_config()
    graph = api.reference_graph(scenario(), config)
    rows = []
    for i, (split, stratum) in enumerate((("development", "A_controlled_geometric"),
                                         ("validation", "B_naturalistic_t2i"))):
        image = home / f"{i}.png"
        image.write_bytes(b"fake image bytes for mocked transport")
        rows.append({"image_id": f"fake-{i}", "relative_path": image.name,
                     "image_sha256": api.digest(image), "split": split, "stratum": stratum, "graph": graph})
    for name in ("manifest.json", "freeze.json", "opportunities.csv"):
        (home / name).write_text("test input", encoding="utf-8")
    monkeypatch.setattr(api, "HERE", home)
    monkeypatch.setattr(api, "provenance", lambda: {"test": "frozen"})
    monkeypatch.setattr(api, "runtime", lambda: {"test": "runtime"})
    monkeypatch.setattr(api, "load_dataset", lambda *_: (rows, {"images": 2}))
    argv = ["--manifest", str(home / "manifest.json"), "--ground-truth", str(home / "freeze.json"),
            "--opportunities", str(home / "opportunities.csv"), "--run-dir", str(home / "outputs/run"), "--execute"]
    return home, rows, argv


def test_mocked_capture_invalid_continues_reports_and_resume_skips_completed(fake_run, monkeypatch):
    home, rows, argv = fake_run
    calls = []
    monkeypatch.setattr(api, "client", lambda *_: object())
    def query(backend, model, image, prompt, args):
        calls.append((backend, image.name))
        assert prompt == "test prompt"
        return "invalid model answer" if image.name == "0.png" else json.dumps(rows[1]["graph"])
    monkeypatch.setattr(api, "query", query)
    assert api.main(argv) == 0 and len(calls) == 4
    path = home / "outputs/run"
    run = api.read(path / "run.json")
    assert len(api.verify_records(path / "raw.jsonl", run)) == 4
    report = api.read(next((path / "reports").glob("*/validation.json")))
    for group in report["groups"]:
        assert group["complete"]
        if group["stratum"] == "A_controlled_geometric":
            assert group["schema_valid"] == 0 and group["micro"]["recall"] == 0
        if group["stratum"] == "B_naturalistic_t2i":
            assert group["schema_valid"] == 1 and group["micro"]["precision"] == 1
    assert api.main(argv + ["--resume"]) == 0 and len(calls) == 4
    monkeypatch.setattr(api, "provenance", lambda: {"test": "changed"})
    with pytest.raises(SystemExit):
        api.main(argv + ["--resume"])


def test_transport_error_stays_missing_and_key_is_redacted(fake_run, monkeypatch):
    home, rows, argv = fake_run
    monkeypatch.setenv("MOONDREAM_API_KEY", "fake-private-key")
    def client(backend, args):
        if backend == "moondream":
            raise RuntimeError("transport failed fake-private-key")
        return object()
    monkeypatch.setattr(api, "client", client)
    monkeypatch.setattr(api, "query", lambda *_: json.dumps(rows[0]["graph"]))
    assert api.main(argv) == 1
    path = home / "outputs/run"
    assert "fake-private-key" not in (path / "execution_errors.jsonl").read_text()
    report = api.read(next((path / "reports").glob("*/validation.json")))
    groups = [g for g in report["groups"] if g["backend"] == "moondream"]
    assert all(g["observed"] == 0 and g["metrics"] is None and not g["complete"] for g in groups)


def test_raw_capture_detects_tampering(fake_run, monkeypatch):
    home, rows, argv = fake_run
    monkeypatch.setattr(api, "client", lambda *_: object())
    monkeypatch.setattr(api, "query", lambda *_: json.dumps(rows[0]["graph"]))
    assert api.main(argv) == 0
    path = home / "outputs/run"
    raw = path / "raw.jsonl"
    lines = raw.read_text().splitlines()
    changed = json.loads(lines[0])
    changed["answer"] = "edited"
    lines[0] = json.dumps(changed)
    raw.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="modified"):
        api.verify_records(raw, api.read(path / "run.json"))


def test_transports_send_only_image_and_prompt(monkeypatch):
    captured = {}
    class Image:
        def __enter__(self):
            return self
        def __exit__(self, *_):
            pass
        def convert(self, mode):
            assert mode == "RGB"
            return "image-only"
    monkeypatch.setitem(sys.modules, "PIL", SimpleNamespace(Image=SimpleNamespace(open=lambda _: Image())))
    def md_query(image, prompt):
        captured["md"] = (image, prompt)
        return {"answer": "raw moondream answer"}
    args = SimpleNamespace(smol_max_tokens=500)
    assert api.query("moondream", SimpleNamespace(query=md_query), Path("test.png"), "prompt-only", args) == "raw moondream answer"
    assert captured["md"] == ("image-only", "prompt-only")
    monkeypatch.setitem(sys.modules, "gradio_client", SimpleNamespace(handle_file=lambda p: f"upload:{p}"))
    def predict(**kwargs):
        captured["smol"] = kwargs
        return "raw smol answer"
    assert api.query("smolvlm2", SimpleNamespace(predict=predict), Path("test.png"), "prompt-only", args) == "raw smol answer"
    assert captured["smol"] == {"input_dict": {"text": "prompt-only", "files": ["upload:test.png"]},
                                 "max_tokens": 500, "api_name": "/chat"}
