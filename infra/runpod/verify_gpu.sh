#!/usr/bin/env bash
set -euo pipefail
destination="${1:-/workspace/environment/gpu_environment_v3_1.json}"
repo="${2:-/workspace/semantic-secrets}"
: "${P9_V3B_IMAGE_DIGEST:?Set P9_V3B_IMAGE_DIGEST to the deployed sha256 image digest}"
cd "$repo"
nvidia-smi -q > /workspace/environment/nvidia-smi-q.txt
/opt/envs/modern/bin/python -m experiments.v3.runtime.environment \
  --gpu-record "$destination" \
  --nvidia-smi /workspace/environment/nvidia-smi-q.txt \
  --image-digest "$P9_V3B_IMAGE_DIGEST"
