# Capability data and project-authored ground truth

P9-v3B has no human participants or human annotators. This file retains its historical name so existing links remain usable; the active v3.2 procedure is deterministic technical dataset construction. The v3.0/v3.1 two-human clauses are superseded by `preregistration_v3_2.json` and `formal_specification_v3_2.md`.

1. Author the family assignments and planned positive/applicable-negative opportunities without acquiring or consulting either perception model. The v3.1 counts, type roles, strata, splits, and family isolation remain exact.
2. Create each controlled or naturalistic `cap-v3-*` image and one `capability-scenario-specification-v3.2.0` record. The scenario record uses exact closed labels, project reference IDs, normalized reference boxes, and semantic atoms; each count atom also names its entity-category scope. It is dataset ground truth, not a model output.
3. Build the 240-row `capability_manifest_v3_2.json`. Each row binds its final image and scenario specification by path and SHA-256. Naturalistic rows additionally require the frozen prompt hash, seed, and generator revision.
4. Populate `support_opportunities_v3_2.csv`. Every row links to one manifest/scenario, uses a content-derived deterministic opportunity ID, identifies the exact entity or ordered-pair scope and normalized boxes where applicable, and declares one positive or applicable-negative closed-label value.
5. Run the complete audits:

   ```bash
   python -m experiments.v3.runtime.dataset audit-manifest /workspace/data/capability_manifest_v3_2.json --data-root /workspace/data
   python -m experiments.v3.runtime.dataset audit-opportunities /workspace/data/support_opportunities_v3_2.csv --manifest /workspace/data/capability_manifest_v3_2.json --data-root /workspace/data
   ```

   The audits fail on any missing/hash-mismatched file, split/ID mismatch, invalid box or reference, positive/negative contradiction, non-deterministic opportunity ID, or deviation from the frozen per-type/per-stratum/per-split support counts.
6. Before any smoke or formal inference, create the external `/workspace/environment/ground_truth_freeze_v3_2.json` from the schema. Record the exact active config hashes, manifest hash, opportunity hash, scenario aggregate hash, author/time, and the required model-output-blind declarations. Validate it with:

   ```bash
   python -m experiments.v3.runtime.dataset audit-ground-truth /workspace/environment/ground_truth_freeze_v3_2.json --manifest /workspace/data/capability_manifest_v3_2.json --opportunities /workspace/data/support_opportunities_v3_2.csv --data-root /workspace/data --results /workspace/results
   ```

7. Only after that command succeeds may an explicitly authorised smoke or formal inference command run. Formal authorization independently binds the freeze record and every other execution artifact.

Ground truth must never be derived from Grounding DINO, SigLIP2, EGTR, another perception model, or later validation output. After the freeze, any semantic, box, opportunity, image, or provenance change creates a new hash and invalidates authorization; it is not an in-place correction.
