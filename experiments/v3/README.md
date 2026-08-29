# Experiments v3

P9-v3A is the immutable v3.0.0 design freeze. P9-v3A.1 is the prospective v3.1.0 pipeline/resource/support amendment. P9-v3A.2 narrowly supplies project-authored model-blind ground truth. P9-v3A.3 narrowly freezes deterministic development-threshold calibration before any output. Historical clauses remain historical and are never silently rewritten.

The authoritative machine-readable files are:

- `config/visual_observation_v3.json`: `L_visual`, observation provenance, confidence boundaries, the compiler contract, and the two candidate pipelines.
- `config/preregistration_v3.json`: dataset/splits, component and compiler metrics, uncertainty, compute, caches, abstention, stop rules, and gates.
- `config/visual_observation_v3_1.json`: prospective Pipeline A/EGTR Pipeline B amendment and exact artifact/adapter/resource freeze.
- `config/preregistration_v3_1.json`: prospective hardware, support, annotation, and Gate V3-A1 amendment.
- `config/preregistration_v3_2.json`: active correction of only the ground-truth method and human-resource blocker.
- `config/preregistration_v3_3.json`: active prospective fixed-grid, entity-first, task-local development calibration method.
- `config/engineering_smoke_settings_v3_3.json`: fixed 0.50/0.00 plumbing constants that can never enter the threshold freeze.

The un-suffixed files remain the historical v3.0.0 meaning at commit `8e44caa`. Future execution composes v3.0.0, the explicit v3.1.0 overrides, and the narrow v3.2.0/v3.3.0 corrections; it must not silently rewrite any record.

The fixed path is:

`I = G(P,r) -> O = Observe(I) -> S = C(O) -> (M,T) = Pi(S)`

Models emit bounded observations, never the final credential JSON. `C` returns a schema-valid canonical graph or a schema-valid typed failure. `L_cred` is not chosen in P9-v3A: an atom type enters it only after independent P9-v3B capability evidence passes in both controlled and naturalistic strata.

No model weights, images, manifests, raw outputs, or results belong here yet. P9-v3B requires explicit authorisation; image creation has no human-resource prerequisite, while every inference mode requires a valid `ground-truth-freeze-v3.2.0` binding the final images, project-authored scenario specifications, deterministic support opportunities, and active config hashes. P9-v3C additionally requires constructive Gate V3-A1 and a separate reconstruction preregistration. P10 remains blocked until Gate V3-A2.

Pre-execution engineering now lives in `prototype/semantic_secrets/v3/`, `experiments/v3/runtime/`, and `infra/runpod/`. The deterministic compiler has a locally passing 320-case matrix, but this is preparation evidence only: it does not start P9-v3B or satisfy Gate V3-A1, and the locked execution image must rerun it. Runtime commands materialize controlled images and exact-revision SD-Turbo images from project-authored inputs, build/audit/freeze manifests and support opportunities, retain each learned pipeline in persistent isolated processes, bind caches to hashes, record warmup-aware complete-pipeline allocated/reserved GPU memory plus RSS/elapsed time, compute the frozen metrics and Gate decision, and export a provenance-complete package. Formal validation still refuses to run without external records binding the exact commit, configs, ground-truth freeze, dataset/scenarios/opportunities, development thresholds, weights, and GPU environment.

The obsolete annotation-resource blocker is resolved by v3.2 and the threshold-method blocker is resolved prospectively by v3.3. The actual project-authored scenario/prompt content, capability data, and ground-truth freeze do not yet exist. No capability image, weight, model output, fitted threshold, or experimental result was created during preparation.

All `experiments/v2/` configs, manifests, outputs, and tests are immutable historical evidence. Do not copy validation outcomes or thresholds into v3 except where the new preregistration explicitly records and justifies a new rule.
