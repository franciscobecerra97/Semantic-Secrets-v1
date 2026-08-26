#!/usr/bin/env bash
set -euo pipefail
repo="${1:-/workspace/semantic-secrets}"
cd "$repo"
/opt/envs/modern/bin/python -m experiments.v3.runtime.results verify-cache \
  --results /workspace/results \
  --manifest /workspace/data/capability_manifest_v3_1.json
if [[ -d /workspace/results/validation-repeat ]]; then
  /opt/envs/modern/bin/python -m experiments.v3.runtime.results verify-repeat --results /workspace/results
fi
