#!/usr/bin/env bash
set -euo pipefail
repo="${1:-/workspace/semantic-secrets}"
destination="${2:-/workspace/results-export}"
cd "$repo"
/opt/envs/modern/bin/python -m experiments.v3.runtime.results export \
  --results /workspace/results --destination "$destination" \
  --include capability_manifest_v3_2.json=/workspace/data/capability_manifest_v3_2.json \
  --include controlled_render_plan_v3.json=/workspace/data/controlled_render_plan_v3.json \
  --include naturalistic_prompt_plan_v3.json=/workspace/data/naturalistic_prompt_plan_v3.json \
  --include support_opportunities_v3_2.csv=/workspace/data/support_opportunities_v3_2.csv \
  --include ground_truth_freeze_v3_2.json=/workspace/environment/ground_truth_freeze_v3_2.json \
  --include threshold_freeze_v3_3.json=/workspace/environment/threshold_freeze_v3_3.json \
  --include development_entity_scopes_v3_3.json=/workspace/environment/development_entity_scopes_v3_3.json \
  --include development_threshold_settings_v3_3.json=/workspace/environment/development_threshold_settings_v3_3.json \
  --include model_acquisition_v3_1.json=/workspace/environment/model_acquisition_v3_1.json \
  --include generator_acquisition_v3.json=/workspace/environment/generator_acquisition_v3.json \
  --include sd_turbo_generation_receipt_v3.json=/workspace/environment/sd_turbo_generation_receipt_v3.json \
  --include gpu_environment_v3_1.json=/workspace/environment/gpu_environment_v3_1.json \
  --include formal_authorization_v3_2.json=/workspace/environment/formal_authorization_v3_2.json \
  --include compiler_invariant_report_v3.json=/workspace/environment/compiler_invariant_report_v3.json \
  --include p9_v3b_evaluation_v3_2.json=/workspace/results/p9_v3b_evaluation_v3_2.json \
  --include-tree scenarios=/workspace/data/scenarios \
  --include-tree controlled_assets=/workspace/data/controlled_assets \
  --include-tree images=/workspace/data/images
