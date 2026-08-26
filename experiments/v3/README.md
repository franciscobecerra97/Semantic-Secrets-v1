# Experiments v3

P9-v3A is the immutable v3.0.0 design freeze. P9-v3A.1 is a prospective v3.1.0 suitability amendment made before any model, image, or inference output. It corrects hardware semantics, selects EGTR as the sole graph-native comparator, freezes support opportunities, and records the two-human annotation prerequisite.

The authoritative machine-readable files are:

- `config/visual_observation_v3.json`: `L_visual`, observation provenance, confidence boundaries, the compiler contract, and the two candidate pipelines.
- `config/preregistration_v3.json`: dataset/splits, component and compiler metrics, uncertainty, compute, caches, abstention, stop rules, and gates.
- `config/visual_observation_v3_1.json`: prospective Pipeline A/EGTR Pipeline B amendment and exact artifact/adapter/resource freeze.
- `config/preregistration_v3_1.json`: prospective hardware, support, annotation, and Gate V3-A1 amendment.

The un-suffixed files remain the historical v3.0.0 meaning at commit `8e44caa`. Future execution composes v3.0.0 with the explicit v3.1.0 overrides; it must not silently rewrite either record.

The fixed path is:

`I = G(P,r) -> O = Observe(I) -> S = C(O) -> (M,T) = Pi(S)`

Models emit bounded observations, never the final credential JSON. `C` returns a schema-valid canonical graph or a schema-valid typed failure. `L_cred` is not chosen in P9-v3A: an atom type enters it only after independent P9-v3B capability evidence passes in both controlled and naturalistic strata.

No model weights, images, manifests, raw outputs, or results belong here yet. P9-v3B requires explicit authorisation and a completed two-independent-human annotation-resource record before image creation. P9-v3C additionally requires constructive Gate V3-A1 and a separate reconstruction preregistration. P10 remains blocked until Gate V3-A2.

Pre-execution engineering now lives in `prototype/semantic_secrets/v3/`, `experiments/v3/runtime/`, and `infra/runpod/`. The deterministic compiler has a locally passing 320-case matrix, but this is preparation evidence only: it does not start P9-v3B or satisfy Gate V3-A1, and the locked execution image must rerun it. Runtime commands isolate the modern Grounding DINO/SigLIP2 stack from historical EGTR, bind caches to hashes, record allocated/reserved GPU memory plus RSS/elapsed time, and refuse validation without external records that bind the exact commit, configs, annotation resource, dataset, thresholds, weights, and GPU environment.

The annotation resource remains unresolved as of 2026-08-26. No capability image, weight, model output, or experimental result was created during execution preparation.

All `experiments/v2/` configs, manifests, outputs, and tests are immutable historical evidence. Do not copy validation outcomes or thresholds into v3 except where the new preregistration explicitly records and justifies a new rule.
