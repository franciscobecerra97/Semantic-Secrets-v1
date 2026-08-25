# Experiments v3

P9-v3A is a design and preregistration phase. It defines a modular visual-observation interface, a deterministic semantic compiler, a two-pipeline shortlist, a new two-stratum capability dataset, and Gates V3-A1/V3-A2. It reports no v3 model or authentication result.

The authoritative machine-readable files are:

- `config/visual_observation_v3.json`: `L_visual`, observation provenance, confidence boundaries, the compiler contract, and the two candidate pipelines.
- `config/preregistration_v3.json`: dataset/splits, component and compiler metrics, uncertainty, compute, caches, abstention, stop rules, and gates.

The fixed path is:

`I = G(P,r) -> O = Observe(I) -> S = C(O) -> (M,T) = Pi(S)`

Models emit bounded observations, never the final credential JSON. `C` returns a schema-valid canonical graph or a schema-valid typed failure. `L_cred` is not chosen in P9-v3A: an atom type enters it only after independent P9-v3B capability evidence passes in both controlled and naturalistic strata.

No model weights, images, manifests, raw outputs, or results belong here yet. P9-v3B requires explicit authorisation. P9-v3C additionally requires constructive Gate V3-A1 and a separate reconstruction preregistration. P10 remains blocked until Gate V3-A2.

All `experiments/v2/` configs, manifests, outputs, and tests are immutable historical evidence. Do not copy validation outcomes or thresholds into v3 except where the new preregistration explicitly records and justifies a new rule.
