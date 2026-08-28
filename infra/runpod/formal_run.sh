#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" != "--formal" ]]; then
  echo 'REFUSED: explicit --formal is required.' >&2
  exit 2
fi
resume=()
if [[ "${2:-}" == "--resume" ]]; then
  resume=(--resume)
  repo="${3:-/workspace/semantic-secrets}"
else
  repo="${2:-/workspace/semantic-secrets}"
fi
cd "$repo"
common=(
  --formal
  "${resume[@]}"
  --pipeline v3.1-gdino-siglip2 --pipeline v3.1-egtr-siglip2
  --adapter-command 'v3.1-gdino-siglip2=/opt/envs/modern/bin/python -m experiments.v3.runtime.adapters.gdino_siglip2'
  --adapter-command 'v3.1-egtr-siglip2=/opt/envs/modern/bin/python -m experiments.v3.runtime.adapters.egtr_siglip2'
  --manifest /workspace/data/capability_manifest_v3_2.json
  --opportunities /workspace/data/support_opportunities_v3_2.csv
  --thresholds /workspace/environment/threshold_freeze_v3_1.json
  --model-manifest /workspace/environment/model_acquisition_v3_1.json
  --adapter-source experiments/v3/runtime/adapters
  --models /workspace/models --data /workspace/data --results /workspace/results
  --authorization /workspace/environment/formal_authorization_v3_2.json
  --ground-truth /workspace/environment/ground_truth_freeze_v3_2.json
  --gpu-environment /workspace/environment/gpu_environment_v3_1.json
)
/opt/envs/modern/bin/python -m experiments.v3.runtime.execution --mode validation "${common[@]}"
/opt/envs/modern/bin/python -m experiments.v3.runtime.execution --mode validation-repeat "${common[@]}"
/opt/envs/modern/bin/python -m experiments.v3.runtime.results verify-repeat --results /workspace/results
