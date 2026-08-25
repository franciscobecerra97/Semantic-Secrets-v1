# P7 cached image-stage ablation

This experiment reuses only the frozen P5 train/validation outputs. It executes no generator, extractor, or embedding model and reads no P6 artifact or held-out test row.

Run and validate:

```powershell
python -m experiments.image_stage_ablation.run_p7
python -m experiments.image_stage_ablation.run_p7 --validate-only
python -m unittest experiments.image_stage_ablation.test_p7
```

The config hashes every permitted source. The result is a bounded engineering diagnostic, not a new Gate A evaluation and not a human usability study.
