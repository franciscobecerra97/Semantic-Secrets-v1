# Experiments v3

P9-v3A is the immutable v3.0.0 design freeze. P9-v3A.1 is the prospective v3.1.0 pipeline/resource/support amendment. P9-v3A.2 is a narrow prospective ground-truth correction made before any model, image, or inference output: the two-human clause is historical and superseded because P9-v3B has no human participants or annotators. The active method uses project-authored reference scene specifications and deterministic support opportunities frozen before inference without model outputs.

The authoritative machine-readable files are:

- `config/visual_observation_v3.json`: `L_visual`, observation provenance, confidence boundaries, the compiler contract, and the two candidate pipelines.
- `config/preregistration_v3.json`: dataset/splits, component and compiler metrics, uncertainty, compute, caches, abstention, stop rules, and gates.
- `config/visual_observation_v3_1.json`: prospective Pipeline A/EGTR Pipeline B amendment and exact artifact/adapter/resource freeze.
- `config/preregistration_v3_1.json`: prospective hardware, support, annotation, and Gate V3-A1 amendment.
- `config/preregistration_v3_2.json`: active correction of only the ground-truth method and human-resource blocker.

The un-suffixed files remain the historical v3.0.0 meaning at commit `8e44caa`. Future execution composes v3.0.0, the explicit v3.1.0 overrides, and the narrow v3.2.0 ground-truth correction; it must not silently rewrite any record.

The fixed path is:

`I = G(P,r) -> O = Observe(I) -> S = C(O) -> (M,T) = Pi(S)`

Models emit bounded observations, never the final credential JSON. `C` returns a schema-valid canonical graph or a schema-valid typed failure. `L_cred` is not chosen in P9-v3A: an atom type enters it only after independent P9-v3B capability evidence passes in both controlled and naturalistic strata.

No model weights, images, manifests, raw outputs, or results belong here yet. P9-v3B requires explicit authorisation; image creation has no human-resource prerequisite, while every inference mode requires a valid `ground-truth-freeze-v3.2.0` binding the final images, project-authored scenario specifications, deterministic support opportunities, and active config hashes. P9-v3C additionally requires constructive Gate V3-A1 and a separate reconstruction preregistration. P10 remains blocked until Gate V3-A2.

Pre-execution engineering now lives in `prototype/semantic_secrets/v3/`, `experiments/v3/runtime/`, and `infra/runpod/`. The deterministic compiler has a locally passing 320-case matrix, but this is preparation evidence only: it does not start P9-v3B or satisfy Gate V3-A1, and the locked execution image must rerun it. Runtime commands isolate the modern Grounding DINO/SigLIP2 stack from historical EGTR, bind caches to hashes, record allocated/reserved GPU memory plus RSS/elapsed time, and refuse validation without external records that bind the exact commit, configs, ground-truth freeze, dataset/scenarios/opportunities, thresholds, weights, and GPU environment.

The obsolete annotation-resource blocker is resolved methodologically by v3.2; the actual project-authored capability data and ground-truth freeze do not yet exist. No capability image, weight, model output, or experimental result was created during this correction.

All `experiments/v2/` configs, manifests, outputs, and tests are immutable historical evidence. Do not copy validation outcomes or thresholds into v3 except where the new preregistration explicitly records and justifies a new rule.
