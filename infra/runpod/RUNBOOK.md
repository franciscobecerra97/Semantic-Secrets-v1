# P9-v3B RunPod runbook

This runbook cannot authorise P9-v3B. P9-v3B has no human participants or human annotators. Model acquisition still requires explicit permission; any inference additionally requires a complete, model-output-blind project-authored ground-truth freeze and the applicable smoke/formal authorization.

## 1. GPU characteristics

Prefer one NVIDIA A10 or RTX A5000-class GPU with 24 GiB VRAM and a CUDA driver compatible with both the legacy CUDA 11.3 EGTR wheel stack and the modern environment. A larger GPU is allowed, but the frozen gate still uses measured framework peak allocation (maximum 24 GiB), process RSS (maximum 32 GiB), and latency—not installed capacity. Allocate at least 32 GiB system RAM. The official EGTR evaluation reference was one V100; this is provenance, not a deployment requirement.

## 2. Exact container

Build the repository commit using `.github/workflows/build-p9-v3b-runpod.yml`. Deploy:

```text
ghcr.io/franciscobecerra97/semantic-secrets-p9-v3b@sha256:<digest-from-the-completed-build>
```

Never deploy `latest` or an unrecorded tag. Record the image digest in `/workspace/environment` and in the GPU environment record. The image contains code and environments only; no weights or datasets.

## 3. Persistent storage

Attach 100 GiB at `/workspace` (60 GiB minimum before actual acquisition sizes are known). Keep these persistent directories:

```text
/workspace/semantic-secrets  repository checkout
/workspace/models            verified model snapshots/artifacts
/workspace/cache             Hugging Face and framework caches
/workspace/data              capability images/manifests/scenario specifications
/workspace/results           raw observations/compiler results/logs
/workspace/environment       hashes, approvals, thresholds, GPU records
```

Run `bash infra/runpod/setup_workspace.sh`. None of the large/sensitive directories belongs in Git.

## 4. Repository checkout

Clone only on the Pod into the persistent code path, then detach at the exact authorised commit:

```bash
git clone https://github.com/franciscobecerra97/Semantic-Secrets-v1 /workspace/semantic-secrets
cd /workspace/semantic-secrets
git checkout --detach <authorised-40-character-commit>
git status --porcelain
```

The last command must be empty. This Pod checkout does not replace the local authoritative working copy; it executes the published commit.

## 5. Environment verification

```bash
bash infra/runpod/verify_environment.sh /workspace/semantic-secrets
export P9_V3B_IMAGE_DIGEST='sha256:<digest-from-the-completed-build>'
bash infra/runpod/verify_gpu.sh
```

The first command reruns the config checks and all 320 compiler cases. Any failure blocks execution. The second records CUDA, driver, framework, GPU, package, config, and `nvidia-smi` provenance.

## 6. Dataset inputs and materialization

Do not start a Pod merely to discover missing authoring inputs. Before image work, prepare off-Pod and review:

- 120 final controlled `capability-scenario-specification-v3.2.0` records;
- the exact 120-row naturalistic prompt/seed plan;
- after SD-Turbo rendering, 120 model-output-blind naturalistic scenario records with final visible boxes/atoms.

The repository cannot infer the naturalistic reference boxes from a prompt and must never obtain them from a perception model. Once those project-authored inputs exist, the executable materialization/audit sequence is:

```bash
/opt/envs/modern/bin/python -m experiments.v3.runtime.dataset materialize-scenarios --stratum A --plan /workspace/data/controlled_scenario_plan_v3_2.json --data-root /workspace/data
/opt/envs/modern/bin/python -m experiments.v3.runtime.images controlled --scenarios /workspace/data/scenarios --render-plan /workspace/data/controlled_render_plan_v3.json --asset-root /workspace/data/controlled_assets --output /workspace/data/images
/opt/envs/modern/bin/python -m experiments.v3.runtime.images naturalistic --prompt-plan /workspace/data/naturalistic_prompt_plan_v3.json --model /workspace/models/sd-turbo --generator-manifest /workspace/environment/generator_acquisition_v3.json --output /workspace/data/images --receipt /workspace/environment/sd_turbo_generation_receipt_v3.json
/opt/envs/modern/bin/python -m experiments.v3.runtime.dataset materialize-scenarios --stratum B --plan /workspace/data/naturalistic_final_scenario_plan_v3_2.json --data-root /workspace/data
/opt/envs/modern/bin/python -m experiments.v3.runtime.dataset build-manifest /workspace/data/capability_manifest_v3_2.json --data-root /workspace/data --prompt-plan /workspace/data/naturalistic_prompt_plan_v3.json --generation-receipt /workspace/environment/sd_turbo_generation_receipt_v3.json
/opt/envs/modern/bin/python -m experiments.v3.runtime.dataset build-opportunities /workspace/data/support_opportunities_v3_2.csv --manifest /workspace/data/capability_manifest_v3_2.json --data-root /workspace/data
/opt/envs/modern/bin/python -m experiments.v3.runtime.dataset create-ground-truth-freeze /workspace/environment/ground_truth_freeze_v3_2.json --manifest /workspace/data/capability_manifest_v3_2.json --opportunities /workspace/data/support_opportunities_v3_2.csv --data-root /workspace/data --results /workspace/results --frozen-by '<project-author-identity>'
```

The naturalistic command is GPU generation and requires separate authorization. These commands create no perception output. Any scenario/prompt authoring decision must be complete before the ground-truth freeze.
If naturalistic generation is interrupted, rerun that same command with `--resume`; every existing PNG must match the atomic partial receipt or the command refuses to continue.

## 7. Model acquisition

First perform the no-download plan:

```bash
bash infra/runpod/acquire_models.sh /workspace/semantic-secrets
bash infra/runpod/acquire_generator.sh /workspace/semantic-secrets
```

Only after acquisition is explicitly permitted, licence/provenance review is recorded, and storage is mounted may `--permit-acquisition` be added. EGTR also requires `--egtr-archive` and `--egtr-approved-provenance`. Its archive is never fetched automatically. Missing checkpoint terms, multiple checkpoints, absent label/config metadata, an unpinned Deformable-DETR base/transform, or any hash mismatch is a frozen typed pipeline failure—not permission to substitute a model or silently download an upstream default.

`acquire_generator.sh` is also dry-run-only unless both `--permit-acquisition` and `--license-approved` are supplied. It resolves only `stabilityai/sd-turbo@b261bac6fd2cf515557d5d0707481eafa0485ec2` and writes a separate inventory; it is not a perception candidate and does not alter the three-component v3.1 acquisition manifest.

## 8. Allowed smoke procedure

Smoke is forbidden before all final images, scenario specifications, manifest rows, and support opportunities are frozen in a valid `ground_truth_freeze_v3_2.json`. This record must predate every perception output and must assert that no prediction contributed to ground truth. After that prerequisite and an explicit smoke permission:

```bash
export P9_V3B_SMOKE_ALLOWED=yes
bash infra/runpod/smoke_run.sh /workspace/semantic-secrets
```

This runs at most two development images per pipeline using the versioned engineering-only constants: every component threshold is 0.50 and every SigLIP top-two margin is 0.00. They are not development-fitted and cannot enter the final freeze. Smoke may expose plumbing, licence, compatibility, or OOM failure; its semantic output may not tune labels, prompts, candidates, thresholds, input resolution, preprocessing, or validation behavior.

## 9. Development score capture, calibration, replay, and threshold freeze

V3.3 freezes the inclusive `0.00,0.01,...,1.00` grid, both-strata objective, ties, fallback, entity-first staging, EGTR predicate/connectivity joint fit, per-task SigLIP threshold/margin fit, and validation isolation. `development_run.sh` executes exactly:

```text
threshold-independent entity score capture
→ entity-only fit and intermediate scope freeze
→ complete downstream SigLIP score capture
→ offline task-local fitting
→ integrated 240-record development replay
→ provenance-complete threshold freeze
```

All score artifacts are development-only and content-addressed under `/workspace/results/calibration`. Candidate evaluation never reruns a neural model. Count and geometry receive no threshold. Neither validation output nor P9-v3C/authentication outcomes can enter calibration. The script refuses existing validation or validation-repeat JSON.

```bash
export P9_V3B_DEVELOPMENT_ALLOWED=yes
bash infra/runpod/development_run.sh /workspace/semantic-secrets
```

The command produces `development_score_manifest_v3_3.json`, score and final SHA-256 inventories, complete candidate JSONL tables, `development_entity_scopes_v3_3.json`, `development_threshold_settings_v3_3.json`, `threshold_fit_report_v3_3.json`, the 240-record replay tree, and `threshold_freeze_v3_3.json`. Inspect and preserve all of them. A preferred-development-criterion failure is recorded but does not permit dropping or replacing a pipeline; the deterministic fallback still freezes its settings.

## 10. Formal execution

Formal validation requires all of the following external, schema-valid records:

- frozen project-authored ground-truth record;
- exact 240-image manifest, image hashes, and scenario-specification hashes;
- exact development/validation support-opportunity table;
- verified acquisition manifest;
- development-only threshold freeze created before validation;
- recorded GPU environment;
- formal authorization binding the exact Git commit and every record/config SHA-256.

The command has no implicit formal mode:

```bash
/opt/envs/modern/bin/python -m experiments.v3.runtime.authorization \
  --authorize-formal --authorized-by '<authorizing-identity>' \
  --container-image-digest "$P9_V3B_IMAGE_DIGEST" \
  --manifest /workspace/data/capability_manifest_v3_2.json \
  --opportunities /workspace/data/support_opportunities_v3_2.csv \
  --ground-truth /workspace/environment/ground_truth_freeze_v3_2.json \
  --thresholds /workspace/environment/threshold_freeze_v3_3.json \
  --model-manifest /workspace/environment/model_acquisition_v3_1.json \
  --output /workspace/environment/formal_authorization_v3_2.json
bash infra/runpod/formal_run.sh --formal /workspace/semantic-secrets
```

The guard rejects a missing `--formal`, either missing pipeline, any revision/hash mismatch, unfrozen or model-dependent ground truth, unfrozen thresholds, incorrect manifest/opportunity/scenario linkage, absent GPU record, or unexpected existing validation output. It runs validation once and then the one frozen validation repeat. Development output cannot be relabelled as formal output.

## 11. Cache and resume

Each cache key binds mode/repeat, image bytes, pipeline/config revision, model manifest, threshold freeze, and the adapter source bundle. Outputs are atomic and never silently overwritten. Before using `--resume`, run:

```bash
bash infra/runpod/verify_resume.sh
```

A mismatched key or partial/unparseable record blocks resume. After `verify_resume.sh` succeeds, resume with `bash infra/runpod/formal_run.sh --formal --resume /workspace/semantic-secrets`. Every existing record is rechecked against the authorised model/threshold/config/image/adapter provenance before it can be skipped. A validation repeat starts only after exactly 240 first-pass pipeline/image records exist.

## 12. Gate evaluation, result verification, and export

```bash
bash infra/runpod/verify_resume.sh
bash infra/runpod/evaluate_gate.sh /workspace/semantic-secrets
bash infra/runpod/export_results.sh /workspace/semantic-secrets /workspace/results-export
```

The evaluator computes every frozen point metric, Wilson interval, 5,000-repeat family bootstrap interval, repeatability check, complete-pipeline latency/RSS/allocated-and-reserved-VRAM summary, independent per-pipeline `L_cred`, and the conjunctive Gate V3-A1 decision. Copy the export off the Pod and independently verify `SHA256_INVENTORY.json`. The package includes raw results plus the manifest, opportunity table, ground-truth/threshold/model/GPU/authorization/compiler records, evaluation, and a SHA-256 inventory.

## 13. Shutdown

Follow `infra/runpod/SHUTDOWN_CHECKLIST.md`. Verify the persistent volume and off-Pod export before terminating the Pod. Do not delete the persistent volume in the same action.
