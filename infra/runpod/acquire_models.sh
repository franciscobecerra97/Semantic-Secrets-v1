#!/usr/bin/env bash
set -euo pipefail
repo="${1:-/workspace/semantic-secrets}"
shift || true
cd "$repo"
/opt/envs/modern/bin/python -m experiments.v3.runtime.acquire \
  --models /workspace/models \
  --manifest /workspace/environment/model_acquisition_v3_1.json \
  "$@"
