#!/usr/bin/env bash
set -euo pipefail
if [[ "${P9_V3B_DEVELOPMENT_ALLOWED:-}" != "yes" ]]; then
  echo 'REFUSED: set P9_V3B_DEVELOPMENT_ALLOWED=yes only after the model-blind ground-truth freeze and explicit development authorization.' >&2
  exit 2
fi
repo="${1:-/workspace/semantic-secrets}"
cd "$repo"
/opt/envs/modern/bin/python -m experiments.v3.runtime.execution \
  --mode development \
  --pipeline v3.1-gdino-siglip2 --pipeline v3.1-egtr-siglip2 \
  --adapter-command 'v3.1-gdino-siglip2=/opt/envs/modern/bin/python -m experiments.v3.runtime.adapters.gdino_siglip2' \
  --adapter-command 'v3.1-egtr-siglip2=/opt/envs/modern/bin/python -m experiments.v3.runtime.adapters.egtr_siglip2' \
  --manifest /workspace/data/capability_manifest_v3_2.json \
  --opportunities /workspace/data/support_opportunities_v3_2.csv \
  --ground-truth /workspace/environment/ground_truth_freeze_v3_2.json \
  --thresholds /workspace/environment/development_threshold_settings_v3_1.json \
  --model-manifest /workspace/environment/model_acquisition_v3_1.json \
  --adapter-source experiments/v3/runtime/adapters \
  --models /workspace/models --data /workspace/data --results /workspace/results
