"""Moondream 3 transport/settings regression tests: no API call or real weights."""
import io
import json
from pathlib import Path
import subprocess
import sys
import urllib.error
from types import SimpleNamespace

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import audit_common as audit
import moondream3_audit as md3


def options(**changes):
    return {"transport": "cloud", "reasoning": True, "max_tokens": 384,
            "snapshot": None, "api_key_env": "MOONDREAM_API_KEY", **changes}


def test_cloud_payload_uses_explicit_model_reasoning_and_separate_answer(monkeypatch):
    monkeypatch.setenv("MOONDREAM_API_KEY", "test-secret-never-save")
    captured = []
    class Response(io.BytesIO):
        headers = {"x-request-id": "test-request"}
    def fake_open(request, timeout):
        captured.append(request)
        assert timeout == 300
        return Response(json.dumps({"answer": "final answer", "reasoning": {"text": "separate trace"}}).encode())
    monkeypatch.setattr(md3.urllib.request, "urlopen", fake_open)
    from PIL import Image
    result = md3.CloudQuery("fixed prompt", options())(Image.new("RGB", (5, 5)))
    payload = json.loads(captured[0].data)
    assert captured[0].full_url == md3.CLOUD_ENDPOINT
    assert captured[0].get_header("User-agent") == md3.CLOUD_USER_AGENT
    assert captured[0].get_header("Accept") == "application/json"
    assert payload["model"] == "moondream3-preview" and payload["reasoning"] is True
    assert payload["settings"] == {"temperature": 0.0, "max_tokens": 384}
    assert payload["image_url"].startswith("data:image/png;base64,")
    assert "graph" not in payload and "reference" not in payload
    assert result["answer"] == "final answer" and result["reasoning"]["text"] == "separate trace"
    assert "test-secret-never-save" not in json.dumps(result)


def test_cloud_key_missing_or_http_error_is_not_a_model_answer(monkeypatch):
    monkeypatch.delenv("MOONDREAM_API_KEY", raising=False)
    with pytest.raises(ValueError, match="Set MOONDREAM_API_KEY"):
        md3.CloudQuery("prompt", options())
    monkeypatch.setenv("MOONDREAM_API_KEY", "test-secret-never-save")
    def fail(*args, **kwargs):
        raise urllib.error.HTTPError(md3.CLOUD_ENDPOINT, 401, "secret echoed in remote reason", {}, None)
    monkeypatch.setattr(md3.urllib.request, "urlopen", fail)
    from PIL import Image
    with pytest.raises(md3.CloudRequestError) as caught:
        md3.CloudQuery("prompt", options())(Image.new("RGB", (2, 2)))
    assert "HTTP 401" in str(caught.value)
    assert "secret" not in str(caught.value)


def test_cloud_provider_error_retains_diagnostics_and_redacts_key(monkeypatch):
    key = "test-secret-never-save"
    monkeypatch.setenv("MOONDREAM_API_KEY", key)
    def fail(*args, **kwargs):
        body = json.dumps({"error": {"code": "access_denied", "message": f"Model access denied for {key}"},
                           "request": {"X-Moondream-Auth": key}}).encode()
        raise urllib.error.HTTPError(md3.CLOUD_ENDPOINT, 403, "unused remote reason",
                                     {"x-request-id": "test-request"}, io.BytesIO(body))
    monkeypatch.setattr(md3.urllib.request, "urlopen", fail)
    from PIL import Image
    with pytest.raises(md3.CloudRequestError) as caught:
        md3.CloudQuery("prompt", options())(Image.new("RGB", (2, 2)))
    message = str(caught.value)
    assert "HTTP 403" in message and "access_denied" in message
    assert "Model access denied" in message and "request_id=test-request" in message
    assert key not in message and "[REDACTED]" in message
    assert "X-Moondream-Auth" not in message


@pytest.mark.parametrize("body", [
    json.dumps({"error_code": 1010, "title": "Error 1010: Access denied", "cloudflare_error": True}).encode(),
    b"<html>Error code: 1010; private unstructured response</html>",
])
def test_cloud_gateway_error_is_identified_without_dumping_body(body):
    error = urllib.error.HTTPError(md3.CLOUD_ENDPOINT, 403, "unused reason", {}, io.BytesIO(body))
    message = str(md3.cloud_http_error(error, "test-secret"))
    assert "1010" in message and "before model inference" in message
    assert "private unstructured response" not in message


def test_small_local_gpu_fails_before_loading_weights(monkeypatch):
    import torch
    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    monkeypatch.setattr(torch.cuda, "get_device_properties", lambda _: SimpleNamespace(total_memory=4 * 1024**3))
    with pytest.raises(ValueError, match="GPU has 4.0 GiB"):
        md3.LocalQuery("prompt", options(transport="local"))


def test_cloud_run_retains_reasoning_and_validator_accepts_answer_only(tmp_path, monkeypatch):
    monkeypatch.setattr(audit, "OUTPUTS", tmp_path / "outputs")
    row = audit.select_records()[0]
    monkeypatch.setattr(md3, "load_query", lambda prompt, config: lambda image: {
        "answer": json.dumps(row["graph"]), "reasoning": {"text": "trace is not credential JSON"}})
    path, success = audit.run_inference([row], ["moondream3"], audit.OUTPUTS / "md3", experimental=options())
    assert success
    run = audit.read_json(path / "run.json")
    raw = audit.verified_observations(path / "moondream3.jsonl", run, "moondream3")[0]
    assert raw["reasoning"]["text"] == "trace is not credential JSON"
    assert raw["schema_valid"] and raw["reasoning_requested"]
    assert run["models"]["moondream3"]["revision"] == "hosted_alias_not_an_immutable_weight_revision"
    report = audit.read_json(audit.validate_run(path) / "validation.json")
    assert report["backends"][0]["valid"] == 1


def test_cloud_auth_failure_stops_without_fabricating_invalid_predictions(tmp_path, monkeypatch):
    monkeypatch.setattr(audit, "OUTPUTS", tmp_path / "outputs")
    def unavailable(image):
        raise md3.CloudRequestError("HTTP 401")
    monkeypatch.setattr(md3, "load_query", lambda prompt, config: unavailable)
    path, success = audit.run_inference(audit.select_records(), ["moondream3"], audit.OUTPUTS / "auth", experimental=options())
    assert not success and not (path / "moondream3.jsonl").exists()
    report = audit.read_json(audit.validate_run(path) / "validation.json")["backends"][0]
    assert report["observed_images"] == 0 and report["invalid"] == 0
    assert report["missing_image_ids"] == ["cap-v2-064"]


def test_earlier_captures_can_be_revalidated_with_manual_source_changes(tmp_path, monkeypatch):
    monkeypatch.setattr(audit, "OUTPUTS", tmp_path / "outputs")
    row = audit.select_records()[0]
    run = audit.receipt([row], audit.make_plan([row], ["demo"]), "test")
    manual_name = next(name for name in run["source_hashes"] if "audit_common.py" in name)
    run["source_hashes"][manual_name] = "previous-manual-code"
    path = audit.prepare_run(audit.OUTPUTS / "old", run)
    record = {"backend": "demo", "fixture_id": row["fixture_id"], "pass": "primary", "split": row["split"],
              "answer": "bad json", "schema_valid": False, "parsed_graph": None,
              "image_sha256": row["image_sha256"], "audit_key": audit.observation_key(run, "demo", row["fixture_id"], "primary")}
    audit.append_observation(path / "demo.jsonl", record)
    report = audit.read_json(audit.validate_run(path) / "validation.json")
    assert manual_name in report["manual_validator_source_changes_since_capture"]
    frozen_name = next(name for name in run["source_hashes"] if "preregistration_v2.json" in name)
    run["source_hashes"][frozen_name] = "wrong-frozen-config"
    (path / "run.json").write_text(json.dumps(run), encoding="utf-8")
    with pytest.raises(ValueError, match="Historical scoring/configuration"):
        audit.validate_run(path)


def test_moondream3_cli_plan_is_nonexecuting_and_old_options_stay_separate():
    script = str(HERE / "02_run_inference.py")
    plan = subprocess.run([sys.executable, script, "--models", "moondream3", "--transport", "cloud", "--reasoning"],
                          capture_output=True, text=True)
    assert plan.returncode == 0, plan.stderr
    assert "reasoning=True" in plan.stdout and "Plan only" in plan.stdout
    old = subprocess.run([sys.executable, script, "--models", "moondream", "--reasoning"], capture_output=True, text=True)
    assert old.returncode != 0 and "require --models moondream3" in old.stderr
