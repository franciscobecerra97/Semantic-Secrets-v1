# Semantic Secrets

Research project for a prospective PoPETs/PETS 2027 paper on private authentication from reconstructable visual semantics.

## Active v2 goal

The project asks whether a remembered visual concept can be reconstructed through independently generated images, converted locally into a canonical typed semantic graph, and verified under a system-derived mandatory/tolerant policy without exposing a practical semantic guess-testing or linking oracle.

The natural-language prompt is a reconstruction interface, not the secret. Generated pixels are transient and do not supply credential entropy. The strongest target keeps prompts, images, plaintext graphs, and raw embeddings on the trusted client.

## Current status

The v2 research-contract migration is complete; no v2 experiment or implementation has run. The next permitted phase is **P8 — v2 novelty, formalisation, and preregistration design**. P9 and all expensive/model/cryptographic work remain blocked until their preceding gates pass.

P0–P7 remain frozen evidence for `visual-semantic-pipeline-v1`:

- P6 failed its original Gate A: the primary weighted matcher accepted 75% of targeted validation neighbours at its training-selected threshold; the twelve v1 test families remain sealed.
- P7 found no material benefit from its tested image pathways over paired text pathways and removed that image stage from the v1 authentication core.

Those findings remain valid and have not been retuned. The v2 image hypothesis is scientifically distinct and requires new representation, data, preregistration, pilot, and gates.

## Read first

1. `AGENT.md` — authoritative v2 scientific and engineering contract.
2. `PLAN.md` — preserved P0–P7 history and gated P8–P20 execution plan.
3. `DECISIONS.md` — immutable decisions, including P7-R2 direction amendment.
4. `docs/research_direction_v2.md` — concise v2 thesis and evidence boundary.
5. `docs/vsa_2026_comparison.md` — complete closest-work comparison.
6. `docs/security_model_v2.md` and `docs/threat_claim_matrix_v2.csv` — active v2 security contract.
7. `paper/draft.tex` — planning manuscript; hypotheses are not results.

`docs/security_model.md` remains the frozen v1 model. `paper/main.tex` and `paper/sample-base.bib` are venue/template examples, not the research manuscript or evidence bibliography.

## Scientific boundaries

- No participant study is authorised. Do not claim memorability, recall, usability, preference, or learning effort.
- Algorithms, model identities, canonicalisation, policies, and thresholds are public.
- VSA already covers image-independent visual-semantic authentication, VLM extraction, canonical tokens, object/attribute/count/quadrant facts, Flexible Range Logic, and user-selected policies. These are not v2 novelty.
- Semantic correctness and cryptographic privacy are separate gates. Hashing, salting, or encryption alone does not establish template privacy, offline resistance, or unlinkability.
- Execute one numbered phase at a time and never bypass Gate V2-N, V2-A, V2-B, V2-C, V2-D, V2-E, or V2-F.

Large models, raw datasets, generated images, secrets, caches, and recomputable intermediates must not be committed. Version compact manifests, configs, tests, aggregate evidence, and exact provenance required for claims.
