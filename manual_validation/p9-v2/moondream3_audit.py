"""Optional Moondream 3 comparison. Never changes the frozen P9-v2 backend.

Local execution uses an explicitly prepared, hashed snapshot on a suitable CUDA
GPU. Cloud execution is explicit, uses only the selected capability image/prompt,
and reads its credential from an environment variable without saving it.
"""
from __future__ import annotations

import base64
import io
import json
import os
from pathlib import Path
import re
import shutil
import urllib.error
import urllib.request

MODEL_ID = "moondream/moondream3-preview"
MODEL_REVISION = "5112966d1a723413b1c9a1e8bea272b72e647b35"
TOKENIZER_ID = "moondream/starmie-v1"
TOKENIZER_REVISION = "35192e10a54e36eabe0a7cc57a2c1aab371cafc5"
CLOUD_MODEL = "moondream3-preview"
CLOUD_ENDPOINT = "https://api.moondream.ai/v1/query"
CLOUD_USER_AGENT = "semantic-secrets-manual-audit/1.0"


class CloudRequestError(RuntimeError):
    """Transport/authentication failures are not model predictions."""


def cloud_http_error(error, key):
    """Keep bounded provider diagnostics, never headers, payloads or credentials."""
    def safe(value):
        text = str(value).replace(key, "[REDACTED]")
        text = re.sub(r"(?i)\bbearer\s+[^\s\"',;]+", "Bearer [REDACTED]", text)
        return " ".join(text.split())[:400]

    parts = [f"Moondream Cloud returned HTTP {error.code}"]
    try:
        body = error.read(16384).decode("utf-8", "replace")
    except (OSError, ValueError):
        body = ""
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        data = None
    # Read only named diagnostic fields. Do not dump arbitrary response content:
    # gateways can return HTML and providers can echo submitted request values.
    if isinstance(data, dict):
        detail = data.get("error", data)
        if isinstance(detail, str):
            parts.append(safe(detail))
        elif isinstance(detail, dict):
            for name in ("code", "error_code", "title", "message", "detail"):
                value = detail.get(name)
                if isinstance(value, (str, int)):
                    parts.append(f"{name}={safe(value)}")
        if data.get("cloudflare_error") is True or data.get("error_code") == 1010:
            parts.append("Gateway rejected the HTTP client before model inference; this does not establish an API-key problem")
    elif "error code: 1010" in body.lower() or "error 1010" in body.lower():
        parts.append("Gateway error 1010: HTTP client signature rejected before model inference")
    else:
        parts.append("No structured provider explanation was returned; check API access or contact Moondream support")
    headers = error.headers or {}
    request_id = headers.get("x-request-id") or headers.get("cf-ray")
    if request_id:
        parts.append(f"request_id={safe(request_id)}")
    return CloudRequestError("; ".join(parts))


def describe_backend(options):
    """No network or weight loading: describe exactly which new test will run."""
    if options["transport"] == "cloud":
        return {"backend": "moondream3", "model_id": CLOUD_MODEL,
                "revision": "hosted_alias_not_an_immutable_weight_revision",
                "endpoint": CLOUD_ENDPOINT, "transport": "cloud"}, "cloud"
    import audit_common as audit
    if not options.get("snapshot"):
        raise ValueError("Local Moondream 3 requires --snapshot from 06_prepare_moondream3.py")
    snapshot = Path(options["snapshot"]).resolve()
    manifest = audit.read_json(snapshot / "manual_snapshot.json")
    if (manifest.get("model_id") != MODEL_ID or manifest.get("revision") != MODEL_REVISION
            or manifest.get("tokenizer_revision") != TOKENIZER_REVISION):
        raise ValueError("Moondream 3 snapshot does not match this comparison's pinned artifacts")
    for item in manifest["files"]:
        path = (snapshot / item["path"]).resolve()
        if not path.is_relative_to(snapshot) or not path.is_file() or audit.sha256(path) != item["sha256"]:
            raise ValueError(f"Moondream 3 snapshot hash mismatch: {item['path']}")
    return {"backend": "moondream3", "model_id": MODEL_ID, "revision": MODEL_REVISION,
            "snapshot": str(snapshot), "snapshot_manifest_sha256": audit.sha256(snapshot / "manual_snapshot.json"),
            "tokenizer_id": TOKENIZER_ID, "tokenizer_revision": TOKENIZER_REVISION,
            "transport": "local", "weight_bytes_verified_against_preparation_inventory": True}, "cuda"


class CloudQuery:
    def __init__(self, prompt, options):
        self.prompt, self.options = prompt, options
        self.key = os.environ.get(options["api_key_env"])
        if not self.key:
            raise ValueError(f"Set {options['api_key_env']} in your terminal; do not put the key in code or chat")

    def __call__(self, image):
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        payload = {"model": CLOUD_MODEL, "question": self.prompt,
                   "image_url": "data:image/png;base64," + base64.b64encode(image_bytes.getvalue()).decode("ascii"),
                   "reasoning": self.options["reasoning"], "stream": False,
                   "settings": {"temperature": 0.0, "max_tokens": self.options["max_tokens"]}}
        request = urllib.request.Request(CLOUD_ENDPOINT, data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json",
                     "User-Agent": CLOUD_USER_AGENT, "X-Moondream-Auth": self.key}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                result = json.loads(response.read().decode("utf-8"))
                request_id = response.headers.get("x-request-id")
        except urllib.error.HTTPError as exc:
            raise cloud_http_error(exc, self.key) from None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            raise CloudRequestError("Moondream Cloud request/response failed; inspect connectivity and retry with --resume") from None
        if not isinstance(result, dict) or not isinstance(result.get("answer"), str):
            raise CloudRequestError("Cloud response lacks a text 'answer'; no model prediction was recorded")
        return {"answer": result["answer"], "reasoning": result.get("reasoning"),
                "server_request_id": result.get("request_id", request_id), "usage": result.get("usage")}


class LocalQuery:
    def __init__(self, prompt, options):
        import torch
        if not torch.cuda.is_available():
            raise ValueError("Local Moondream 3 uses the upstream CUDA/bfloat16 path; CUDA is unavailable")
        capacity = torch.cuda.get_device_properties(0).total_memory
        # The pinned index declares ~18.5 GB of weight tensors before caches.
        if capacity < 20 * 1024 ** 3:
            raise ValueError(f"GPU has {capacity / 1024**3:.1f} GiB. This unquantized 9B model needs "
                             "more space for weights and caches; use a suitable larger GPU or explicit --transport cloud")
        if not torch.cuda.is_bf16_supported():
            raise ValueError("This GPU does not support the upstream bfloat16 configuration")
        import audit_common as audit
        self.prompt, self.options = prompt, options
        snapshot = Path(options["snapshot"]).resolve()
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        cache = audit.OUTPUTS / "moondream3-module-cache"
        os.environ["HF_MODULES_CACHE"] = str(cache)
        from tokenizers import Tokenizer
        from transformers import AutoModelForCausalLM
        from transformers.dynamic_module_utils import _sanitize_module_name
        module_path = cache / "transformers_modules" / _sanitize_module_name(snapshot.name)
        module_path.mkdir(parents=True, exist_ok=True)
        (module_path / "__init__.py").touch()
        for source in snapshot.glob("*.py"):
            shutil.copy2(source, module_path / source.name)
        original = Tokenizer.from_pretrained
        def tokenizer_from_local(model_id, *args, **kwargs):
            if model_id != TOKENIZER_ID:
                raise ValueError(f"Unexpected tokenizer requested: {model_id}")
            return Tokenizer.from_file(str(snapshot / "tokenizer/tokenizer.json"))
        Tokenizer.from_pretrained = staticmethod(tokenizer_from_local)
        try:
            self.model = AutoModelForCausalLM.from_pretrained(str(snapshot), trust_remote_code=True,
                local_files_only=True, dtype=torch.bfloat16, device_map={"": "cuda"}, low_cpu_mem_usage=True)
        finally:
            Tokenizer.from_pretrained = original
        self.model.eval()
        self.model.compile()  # Upstream FlexAttention recipe; includes compilation/warmup.

    def __call__(self, image):
        import torch
        with torch.inference_mode():
            return self.model.query(image=image, question=self.prompt, reasoning=self.options["reasoning"],
                stream=False, settings={"temperature": 0.0, "max_tokens": self.options["max_tokens"]})


def load_query(prompt, options):
    return CloudQuery(prompt, options) if options["transport"] == "cloud" else LocalQuery(prompt, options)


def prepare_snapshot(destination):
    """Explicit opt-in download, separate from inference and historical manifests."""
    from huggingface_hub import snapshot_download
    import audit_common as audit
    from experiments.v2.acquire_p9 import static_remote_code_review
    destination = audit.output_path(destination, "moondream3-snapshot")
    destination.mkdir(parents=True, exist_ok=False)
    # The pinned index points at modelv2 shards. Avoid downloading other weight sets.
    snapshot_download(repo_id=MODEL_ID, revision=MODEL_REVISION, local_dir=destination,
        allow_patterns=["*.py", "config.json", "model.safetensors.index.json", "modelv2-*.safetensors", "LICENSE.md", "README.md"])
    snapshot_download(repo_id=TOKENIZER_ID, revision=TOKENIZER_REVISION,
        local_dir=destination / "tokenizer", allow_patterns=["tokenizer.json"])
    review = static_remote_code_review(destination, allowed_findings={("lora.py", "network_access")})
    audit.write_json(destination / "source_review.json", review)
    if not review["approved"]:
        raise ValueError("Source scan found unexpected execution/network operations; inspect source_review.json before loading")
    index = audit.read_json(destination / "model.safetensors.index.json")
    files = sorted({*destination.glob("*.py"), *destination.glob("*.json"),
                    destination / "LICENSE.md", destination / "tokenizer/tokenizer.json",
                    *(destination / name for name in set(index["weight_map"].values()))})
    manifest = {"model_id": MODEL_ID, "revision": MODEL_REVISION, "tokenizer_id": TOKENIZER_ID,
                "tokenizer_revision": TOKENIZER_REVISION, "source_review": review,
                "files": [{"path": file.relative_to(destination).as_posix(), "bytes": file.stat().st_size,
                           "sha256": audit.sha256(file)} for file in files]}
    audit.write_json(destination / "manual_snapshot.json", manifest)
    return destination
