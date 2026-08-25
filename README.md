# Semantic Secrets

Research project for a prospective PoPETs/PETS 2027 paper on private authentication from reconstructable visual semantics.

## Active research goal

The project asks whether a remembered visual concept can be reconstructed through independently generated images, converted locally into a canonical typed semantic graph, and verified under a system-derived mandatory/tolerant policy without exposing a practical semantic guess-testing or linking oracle.

The natural-language prompt is a reconstruction interface, not the secret. Generated pixels are transient and do not supply credential entropy. The strongest target keeps prompts, images, plaintext graphs, and raw embeddings on the trusted client.

## Current status

P8 passed Gate V2-N with narrowed claims. P9-v2 then completed negatively: neither frozen monolithic VLM-to-credential-JSON extractor survived the 98% schema-validity requirement, P9B was not executed, and Gate V2-A failed. That result is immutable and does not establish universal extractor impossibility.

P9-v3A froze the explicit modular reframe as v3.0.0. P9-v3A.1 has now prospectively frozen v3.1.0: any documented dedicated GPU may be used while measured pipeline VRAM remains capped at 24 GiB; EGTR replaces SGTR as the graph-native comparator; support is defined by predeclared opportunities with five primary gate types; and the unavailable guaranteed second human annotator is an execution blocker. No v3 weight, capability image, inference, or validation output exists. P9-v3B awaits explicit authorisation and resolution of the annotation blocker; P9-v3C is blocked on V3-A1; P10 and cryptography are blocked on V3-A2.

P0–P7 remain frozen evidence for `visual-semantic-pipeline-v1`:

- P6 failed its original Gate A: the primary weighted matcher accepted 75% of targeted validation neighbours at its training-selected threshold; the twelve v1 test families remain sealed.
- P7 found no material benefit from its tested image pathways over paired text pathways and removed that image stage from the v1 authentication core.

Those findings remain valid and have not been retuned. The v2 image hypothesis is scientifically distinct and requires new representation, data, preregistration, pilot, and gates.

## Read first

1. `AGENT.md` — authoritative scientific and engineering contract, including the v3 extraction boundary.
2. `PLAN.md` — preserved P0–P7 history and gated P8–P20 execution plan.
3. `DECISIONS.md` — immutable decisions, including P7-R2 direction amendment.
4. `docs/research_direction_v2.md` — concise v2 thesis and evidence boundary.
5. `docs/vsa_2026_comparison.md` — complete closest-work comparison.
6. `docs/security_model_v2.md` and `docs/threat_claim_matrix_v2.csv` — active v2 security contract.
7. `docs/p8_novelty_review_v2.md` and `docs/formal_specification_v2.md` — Gate V2-N outcome and P9–P11 freeze.
8. `docs/p9_capability_screen_v2.md` — P9A negative evidence, logical-futility boundary, and failed Gate V2-A decision.
9. `docs/p9_v3_reframe.md` and `docs/formal_specification_v3.md` — immutable v3.0.0 architecture freeze.
10. `docs/p9_v3_preexecution_audit.md` and `docs/formal_specification_v3_1.md` — binding prospective v3.1.0 suitability amendment.
11. `experiments/v3/config/preregistration_v3_1.json` and `visual_observation_v3_1.json` — machine-readable future-experiment amendment; the un-suffixed configs preserve v3.0.0.
12. `experiments/v2/config/preregistration_v2.json` — immutable historical v2 freeze and failed path.
13. `paper/draft.tex` — planning manuscript with the bounded P9-v2 result and no false v3 findings.

`docs/security_model.md` remains the frozen v1 model. `paper/main.tex` and `paper/sample-base.bib` are venue/template examples, not the research manuscript or evidence bibliography.

## Scientific boundaries

- No participant study is authorised. Do not claim memorability, recall, usability, preference, or learning effort.
- Algorithms, model identities, canonicalisation, policies, and thresholds are public.
- VSA already covers image-independent visual-semantic authentication, VLM extraction, canonical tokens, object/attribute/count/quadrant facts, Flexible Range Logic, and user-selected policies. These are not v2 novelty.
- Semantic correctness and cryptographic privacy are separate gates. Hashing, salting, or encryption alone does not establish template privacy, offline resistance, or unlinkability.
- Execute one numbered phase at a time. P9-v2's V2-A failure remains historical evidence; the explicit v3 reframe must pass V3-A1 and V3-A2 before P10. Never bypass later V2-B–V2-F gates.

Large models, raw datasets, generated images, secrets, caches, and recomputable intermediates must not be committed. Version compact manifests, configs, tests, aggregate evidence, and exact provenance required for claims.
