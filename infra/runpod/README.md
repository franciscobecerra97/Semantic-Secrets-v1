# P9-v3B RunPod preparation

This package prepares—but does not authorise—the frozen P9-v3B capability execution. It contains no weights, capability images, ground-truth records, thresholds, or experimental outputs. The active contract is the composition of immutable v3.0, the v3.1 pipeline/resource/support amendment, and the prospective v3.2 project-authored-ground-truth correction. The final readiness audit found that project-authored scenario/prompt content and an outcome-independent development-threshold selection rule are still required before inference; the runbook fails closed rather than inventing either from model output.

The container preserves the required scientific boundary:

```text
modern environment                 legacy EGTR environment
Grounding DINO Tiny ─┐             EGTR official artifact ─┐
SigLIP2 Base ────────┴─> bounded observations <─────────────┘
                                      │
                                      v
                         deterministic v3.0 compiler
```

The base image is the EGTR repository's frozen `nvcr.io/nvidia/pytorch:21.11-py3`. Its system Python receives the official historical requirements and compiled FPN extension. `/opt/envs/modern` isolates current Transformers support for Grounding DINO Tiny and SigLIP2. The two environments communicate only through canonical JSON subprocess messages; EGTR and learned components cannot author graph or credential JSON.

Model acquisition is opt-in. A call without `--permit-acquisition` prints an exact plan and downloads nothing. Hugging Face snapshots use the frozen revisions. EGTR requires a separately reviewed provenance approval, a manually acquired official archive with a pre-recorded SHA-256, and an unambiguous extracted artifact; otherwise it fails closed.

Local Docker status on 2026-08-26: the Docker CLI and Buildx plugin were present, but the Linux Docker Desktop daemon was not running. No image was built locally. The manual GHCR workflow therefore supplies the reproducible prebuild path; it requires an `NGC_API_KEY` repository secret to pull the frozen NVIDIA base. The published image must be deployed by immutable digest, not a mutable tag.

Persistent data lives outside Git under `/workspace/{models,cache,data,results,environment}`. Use 100 GiB persistent storage (60 GiB hard preparation minimum) and expand only after the acquisition inventory records actual checkpoint and cache sizes.

See [ANNOTATION.md](ANNOTATION.md) for the deterministic model-blind ground-truth procedure, [RUNBOOK.md](RUNBOOK.md) for the guarded sequence, and [SHUTDOWN_CHECKLIST.md](SHUTDOWN_CHECKLIST.md) before terminating a Pod.
