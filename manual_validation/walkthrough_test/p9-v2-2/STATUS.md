# P9-v2-2 execution status - 2026-10-20

**Status: awaiting naturalistic reference review and ground-truth freeze. Precision: not measured.**

All 240 shared images now exist in `artifacts/downloads/p9_v3`: 120 controlled PNGs with construction references, plus 120 naturalistic PNGs requested through the SD-Turbo remote API. The public API's actual model revision/settings are unverified and explicitly documented in the v3.4 generation amendment.

All image dimensions, retained raw responses, receipt hashes and PNG conversion hashes were checked. No exact duplicate or completely uniform images were found. This establishes file integrity, not semantic correctness or extraction precision.

Naturalistic reference boxes and visible facts still require project-author authoring without perception-model predictions. Open the dataset's `review.html`, export checked references, and use the import/finalize commands in `docs/p9_v3_remote_dataset.md`. Empty drafts are not ground truth. No capability manifest, support table, or ground-truth freeze is fabricated.

No Moondream/SmolVLM2 calls or precision measurement have been performed for this experiment. Updated-default-path preflight blocks on missing reference/freeze artifacts before any API call. Historical P9-v2 results remain unchanged.

Earlier preparation checks remain in `outputs/preparation-20261020/`. Data preparation additionally passed 377 v3 Python tests and six Node transport tests; receipts are in the shared dataset's `provenance/`. These are software checks. The full repository suite and live extraction APIs were not run for this task.
