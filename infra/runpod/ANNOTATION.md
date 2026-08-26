# Capability data and annotation procedure

This procedure remains blocked until a real two-person resource satisfies `annotation_resource_v3_1.schema.json`. The example record is intentionally invalid and cannot unlock any command.

1. Confirm one project researcher and one qualified independent external human, their availability, independence/model blindness, rubric version, randomized-ID procedure, conflict provenance, and adjudication procedure. Validate the completed external record against the schema.
2. Only then author the frozen `cap-v3-*` images. Do not use any perception output in image design or ground truth.
3. Create exactly the deterministic IDs emitted by `python -m experiments.v3.runtime.dataset randomize ...`; retain the real-ID mapping with the coordinator and provide annotators only blinded image packages.
4. Build the 240-row capability manifest and run `audit-manifest --data-root /workspace/data`. Families may not cross splits; each stratum/split must contain 60 images and every image hash must match.
5. Populate the predeclared support opportunities from `support_opportunities_v3_1.csv`. Run `audit-opportunities`; counts must match every frozen type/stratum/polarity cell exactly.
6. Give each annotator an independent copy of `annotation_labels_v3_1.csv`. Never provide model detections, scores, observations, graphs, predictions, or another annotator's labels.
7. Run `agreement` on the two immutable raw files. Retain them byte-for-byte and report raw agreement and Cohen's kappa descriptively.
8. Create `adjudication_v3_1.csv` for exactly the disagreement set. Every adjudicated row needs a rubric-grounded note. Run `adjudicate`, which binds all three files by SHA-256 and refuses missing or extra conflicts.
9. Freeze the adjudicated reference opportunities and their hash before any validation-model output. The later formal authorization binds this opportunity hash and the manifest, annotation-resource, threshold, model, commit, config, and environment hashes.

The same person's second pass is never independent annotation. Model-assisted ground truth is forbidden. Annotators may not see validation output before ground truth is frozen.
