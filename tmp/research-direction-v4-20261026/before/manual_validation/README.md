# Manual experiment audits

Start with [p9-v2/README.md](p9-v2/README.md). These are learning and diagnostic
tools, not new formal research phases. Historical experiments are read-only inputs.
Each audit keeps its own provenance, predictions, and reports inside its ignored
`outputs/` directory. No script changes the original experiment's pass/fail decision.

[p9-v2-2/README.md](p9-v2-2/README.md) prepares a separate Moondream/SmolVLM2 API
experiment using the planned shared P9-v3 controlled and naturalistic dataset.
All 240 shared images are now in `artifacts/downloads/p9_v3`. Naturalistic project-author references and the ground-truth freeze remain pending; precision has not been measured. See [the dataset guide](../docs/p9_v3_remote_dataset.md).
