#!/usr/bin/env bash
set -euo pipefail
if [[ "${P9_V3B_DEVELOPMENT_ALLOWED:-}" != "yes" ]]; then
  echo 'REFUSED: set P9_V3B_DEVELOPMENT_ALLOWED=yes only after the model-blind ground-truth freeze and explicit development authorization.' >&2
  exit 2
fi
repo="${1:-/workspace/semantic-secrets}"
cd "$repo"
common=(
  --adapter-command 'v3.1-gdino-siglip2=/opt/envs/modern/bin/python -m experiments.v3.runtime.adapters.gdino_siglip2' \
  --adapter-command 'v3.1-egtr-siglip2=/opt/envs/modern/bin/python -m experiments.v3.runtime.adapters.egtr_siglip2' \
  --manifest /workspace/data/capability_manifest_v3_2.json \
  --opportunities /workspace/data/support_opportunities_v3_2.csv \
  --ground-truth /workspace/environment/ground_truth_freeze_v3_2.json \
  --model-manifest /workspace/environment/model_acquisition_v3_1.json \
  --adapter-source experiments/v3/runtime/adapters \
  --data /workspace/data --results /workspace/results \
  --score-root /workspace/results/calibration/scores \
  --score-manifest /workspace/results/calibration/development_score_manifest_v3_3.json \
  --inventory /workspace/results/calibration/SCORE_SHA256_INVENTORY.json
)
/opt/envs/modern/bin/python -m experiments.v3.runtime.calibration capture --stage entity "${common[@]}"
/opt/envs/modern/bin/python -m experiments.v3.runtime.calibration fit-entities \
  --manifest /workspace/data/capability_manifest_v3_2.json \
  --opportunities /workspace/data/support_opportunities_v3_2.csv \
  --data /workspace/data --results /workspace/results \
  --score-root /workspace/results/calibration/scores \
  --score-manifest /workspace/results/calibration/development_score_manifest_v3_3.json \
  --candidate-metrics /workspace/results/calibration/candidate_metrics \
  --output /workspace/environment/development_entity_scopes_v3_3.json
/opt/envs/modern/bin/python -m experiments.v3.runtime.calibration capture --stage downstream \
  "${common[@]}" --entity-scopes /workspace/environment/development_entity_scopes_v3_3.json
/opt/envs/modern/bin/python -m experiments.v3.runtime.calibration fit \
  --manifest /workspace/data/capability_manifest_v3_2.json \
  --opportunities /workspace/data/support_opportunities_v3_2.csv \
  --ground-truth /workspace/environment/ground_truth_freeze_v3_2.json \
  --data /workspace/data --results /workspace/results \
  --score-root /workspace/results/calibration/scores \
  --score-manifest /workspace/results/calibration/development_score_manifest_v3_3.json \
  --entity-scopes /workspace/environment/development_entity_scopes_v3_3.json \
  --candidate-metrics /workspace/results/calibration/candidate_metrics \
  --settings /workspace/environment/development_threshold_settings_v3_3.json \
  --report /workspace/results/calibration/threshold_fit_report_v3_3.json \
  --inventory /workspace/results/calibration/SHA256_INVENTORY.json
/opt/envs/modern/bin/python -m experiments.v3.runtime.thresholds \
  --settings /workspace/environment/development_threshold_settings_v3_3.json \
  --manifest /workspace/data/capability_manifest_v3_2.json \
  --results /workspace/results \
  --score-manifest /workspace/results/calibration/development_score_manifest_v3_3.json \
  --inventory /workspace/results/calibration/SHA256_INVENTORY.json \
  --entity-scopes /workspace/environment/development_entity_scopes_v3_3.json \
  --fit-report /workspace/results/calibration/threshold_fit_report_v3_3.json \
  --output /workspace/environment/threshold_freeze_v3_3.json
