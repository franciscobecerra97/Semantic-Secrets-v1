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

## 6. Model acquisition

First perform the no-download plan:

```bash
bash infra/runpod/acquire_models.sh /workspace/semantic-secrets
```

Only after acquisition is explicitly permitted, licence/provenance review is recorded, and storage is mounted may `--permit-acquisition` be added. EGTR also requires `--egtr-archive` and `--egtr-approved-provenance`. Its archive is never fetched automatically. Missing checkpoint terms, multiple checkpoints, absent label/config metadata, an unpinned Deformable-DETR base/transform, or any hash mismatch is a frozen typed pipeline failure—not permission to substitute a model or silently download an upstream default.

## 7. Allowed smoke procedure

Smoke is forbidden before all final images, scenario specifications, manifest rows, and support opportunities are frozen in a valid `ground_truth_freeze_v3_2.json`. This record must predate every perception output and must assert that no prediction contributed to ground truth. After that prerequisite and an explicit smoke permission:

```bash
export P9_V3B_SMOKE_ALLOWED=yes
bash infra/runpod/smoke_run.sh /workspace/semantic-secrets
```

This runs at most two development images per pipeline. It may expose plumbing, licence, compatibility, or OOM failure. It may not tune labels, prompts, candidates, input resolution, preprocessing, or validation behavior.

## 8. Formal execution

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
bash infra/runpod/formal_run.sh --formal /workspace/semantic-secrets
```

The guard rejects a missing `--formal`, either missing pipeline, any revision/hash mismatch, unfrozen or model-dependent ground truth, unfrozen thresholds, incorrect manifest/opportunity/scenario linkage, absent GPU record, or unexpected existing validation output. It runs validation once and then the one frozen validation repeat. Development output cannot be relabelled as formal output.

## 9. Cache and resume

Each cache key binds mode/repeat, image bytes, pipeline/config revision, model manifest, threshold freeze, and the adapter source bundle. Outputs are atomic and never silently overwritten. Before using `--resume`, run:

```bash
bash infra/runpod/verify_resume.sh
```

A mismatched key or partial/unparseable record blocks resume. After `verify_resume.sh` succeeds, resume with `bash infra/runpod/formal_run.sh --formal --resume /workspace/semantic-secrets`. Every existing record is rechecked against the authorised model/threshold/config/image/adapter provenance before it can be skipped. A validation repeat starts only after exactly 240 first-pass pipeline/image records exist.

## 10. Result verification and export

```bash
bash infra/runpod/verify_resume.sh
bash infra/runpod/export_results.sh /workspace/semantic-secrets /workspace/results-export
```

Copy the export off the Pod and independently verify `SHA256_INVENTORY.json`. Preserve bounded observations, compiler results, per-component allocated/reserved GPU peaks, RSS, elapsed time, failures, acquisition records, environment records, and logs.

## 11. Shutdown

Follow `infra/runpod/SHUTDOWN_CHECKLIST.md`. Verify the persistent volume and off-Pod export before terminating the Pod. Do not delete the persistent volume in the same action.
