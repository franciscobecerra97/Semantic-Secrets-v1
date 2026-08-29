#!/usr/bin/env bash
set -euo pipefail
repo="${1:-/workspace/semantic-secrets}"
cd "$repo"
/opt/envs/modern/bin/python -m experiments.v3.runtime.environment --verify-only
/opt/envs/modern/bin/python -m pytest -q \
  experiments/v3/test_preregistration_v3.py \
  experiments/v3/test_preregistration_v3_1.py \
  experiments/v3/test_preregistration_v3_2.py \
  experiments/v3/test_calibration_v3_3.py
/opt/envs/modern/bin/python -m experiments.v3.runtime.compiler_report \
  --python /opt/envs/modern/bin/python \
  --output /workspace/environment/compiler_invariant_report_v3.json
test "$(git -C /opt/egtr rev-parse HEAD)" = "7f87450f32758ed8583948847a8186f2ee8b21e3"
/opt/conda/bin/python - <<'PY'
import importlib.metadata
import sys

expected = {
    "torch": "1.12.1+cu113", "torchvision": "0.13.1+cu113", "transformers": "4.18.0",
    "pytorch-lightning": "1.6.4", "timm": "0.5.4", "pycocotools": "2.0.5",
    "ninja": "1.10.2", "matplotlib": "3.4.3", "pandas": "1.2.5", "psutil": "5.9.8",
}
for package, version in expected.items():
    actual = importlib.metadata.version(package)
    if actual != version:
        raise SystemExit(f"{package}: expected {version}, found {actual}")
sys.path.insert(0, "/opt/egtr")
from model.egtr import DetrForSceneGraphGeneration  # noqa: F401
PY
