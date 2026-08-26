#!/usr/bin/env bash
set -euo pipefail
repo="${1:-/workspace/semantic-secrets}"
destination="${2:-/workspace/results-export}"
cd "$repo"
/opt/envs/modern/bin/python -m experiments.v3.runtime.results export \
  --results /workspace/results --destination "$destination"
