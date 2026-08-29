#!/usr/bin/env bash
set -euo pipefail
repo="${1:-/workspace/semantic-secrets}"
cd "$repo"
test -s /workspace/environment/compiler_invariant_report_v3.json
test -s /workspace/results/validation/.complete
test -s /workspace/results/validation-repeat/.complete
/opt/envs/modern/bin/python -m experiments.v3.runtime.evaluation \
  --results /workspace/results \
  --manifest /workspace/data/capability_manifest_v3_2.json \
  --opportunities /workspace/data/support_opportunities_v3_2.csv \
  --data-root /workspace/data \
  --compiler-report /workspace/environment/compiler_invariant_report_v3.json \
  --output /workspace/results/p9_v3b_evaluation_v3_2.json
