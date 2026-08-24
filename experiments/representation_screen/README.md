# P5 representation smoke runner

This directory reproduces `p5-smoke-v1`, a bounded engineering comparison over 27 train/validation rows. It does not evaluate test families, implement authentication, choose a threshold, or produce publication evidence.

## Environment

Create a project-local virtual environment and install the repository's existing P4 requirements followed by `requirements-p5.txt`. Install the platform-specific PyTorch wheels separately. The measured Windows/NVIDIA environment used:

```text
python -m pip install torch==2.12.1 torchvision==0.27.1 --index-url https://download.pytorch.org/whl/cu126
```

Set `HF_HOME` to `artifacts/downloads/hf-p5` so all model weights and remote-code caches remain outside Git. Exact model revisions are in `config/p5_smoke_v1.json`; do not substitute revisions or allow network access after acquisition.

## Stages

Run these stages from the repository root:

```text
python experiments/representation_screen/run_p5.py --stage generate
python experiments/representation_screen/run_p5.py --stage florence
python experiments/representation_screen/run_p5.py --stage embeddings
python experiments/representation_screen/run_p5.py --stage analyze
python experiments/representation_screen/run_p5.py --validate-only
```

Generation and Florence extraction checkpoint each row in `results/p5/cache/`, which is ignored. Re-running a model stage resumes existing checkpoints. Do not rerun `generate` merely to validate a result because cached rows intentionally lack fresh latency observations; use `--validate-only`.

Compact versioned outputs include generation/model provenance, Florence raw task output, canonical atoms, dense arrays, metrics, and the deterministic SVG. Generated PNGs and model weights remain ignored.

## Scientific boundary

- The selection is fixed to enrolment, paraphrase, and near-negative rows from train/validation families.
- Test labels are rejected by the runner.
- IDF weights use six training-family enrolment oracle documents only.
- The median-only smoke rule is reported separately from family-bootstrap uncertainty.
- Oracle representations are diagnostics and can never be selected as deployed extractors.
- Gate A remains closed regardless of `advance_to_p6_by_smoke_rule`; consult `uncertainty_supports_positive_separation` and the P5 decision record.
