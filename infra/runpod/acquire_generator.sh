#!/usr/bin/env bash
set -euo pipefail
repo="${1:-/workspace/semantic-secrets}"
shift || true
cd "$repo"
/opt/envs/modern/bin/python -m experiments.v3.runtime.acquire_generator \
  --models /workspace/models \
  --manifest /workspace/environment/generator_acquisition_v3.json \
  "$@"
