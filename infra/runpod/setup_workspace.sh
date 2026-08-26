#!/usr/bin/env bash
set -euo pipefail
for path in \
  /workspace/semantic-secrets \
  /workspace/models \
  /workspace/cache \
  /workspace/data \
  /workspace/results \
  /workspace/environment; do
  mkdir -p "$path"
done
chmod 700 /workspace/models /workspace/cache /workspace/data /workspace/results /workspace/environment
printf '%s\n' 'Persistent P9-v3B paths are ready.'
