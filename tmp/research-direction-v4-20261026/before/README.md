# Semantic Secrets

Research project for a prospective EuroS&P 2027 paper on reconstructable semantic authentication, acceptance-region security, and private verification.

## Target venue

**12th IEEE European Symposium on Security and Privacy (EuroS&P 2027), Madrid, 5–9 July 2027.** Mandatory abstract registration: **25 November 2026 AoE**. Full paper: **2 December 2026 AoE**. The official template allows 13 body pages in A4. See [verified requirements](docs/eurosp2027_requirements.md), [dates/template provenance](docs/eurosp2027_submission.json), and [paper narrative/structure](docs/eurosp2027_paper_plan.md). The active source is an anonymous planning draft, not a completed submission.

## Active research goal

Most authentication relies on exact secret reproduction or exact cryptographic possession. Semantic Secrets studies a different primitive: independently reconstructing an intended concept into different prompts and images that may nevertheless produce compatible canonical semantics.

```text
exact reproduction
        ↓
approximate semantic reconstruction
        ↓
fuzzy semantic acceptance region
        ↓
guessing and privacy questions
```

The central question is whether independently reconstructed visual concepts can yield stable and discriminative canonical semantic credentials, whether their complete acceptance region withstands realistic and AI-assisted guessing under finite budgets, and whether the frozen predicate can be privately verified without exposing a reusable semantic template, practical offline guess-testing oracle, or cross-domain linkage.

The generator is an experimental semantic reconstruction and normalisation boundary, not a memorability mechanism. The natural-language prompt is the reconstruction interface; the generated image is a transient reconstruction medium; bounded observations are probabilistic evidence; the deterministic canonical graph is the security-sensitive representation; and the complete acceptance region is the operational secret surface. Neither prompts nor generated pixels supply credential entropy. The strongest target keeps prompts, images, observations, plaintext graphs, and raw embeddings on the trusted client.

This controlled technical study does not establish human memorability, recall, usability, preference, accessibility, natural secret-selection entropy, real-world authentication time, proof that images are easier to remember, or superiority to passwords, passkeys, biometrics, or hardware authenticators. It does not assume universal password replacement. Evidence may support standalone, second-factor, policy-constrained, restricted-use, negative/measurement, or stop outcomes.

## Current status

P8 passed Gate V2-N with narrowed claims. P9-v2 then completed negatively: neither frozen monolithic VLM-to-credential-JSON extractor survived the 98% schema-validity requirement, P9B was not executed, and Gate V2-A failed. That result is immutable and does not establish universal extractor impossibility.

P9-v3A and v3.1–v3.3 froze the modular architecture, support, model-blind reference method and development calibration. The compiler, dataset/freezing tools, isolated adapters, score capture, calibration/replay, provenance guards and evaluation/export software are implemented. On 26 October, all 421 core tests and all 320 compiler cases passed locally; this is engineering evidence, not a model-capability gate result.

The October dataset work produced **240 images: 120 controlled and 120 naturalistic**, with 120 controlled references. Naturalistic references, complete support table/manifest and the ground-truth freeze remain pending. The remote API's actual weights/settings are unattested. P9-v3B data preparation is in progress; formal perception evaluation has not started. The entity scorer's one-to-one matching defect and moved manual-script paths must be corrected before relying on evaluation. No v3 capability metric, reconstruction result or private verifier is established. P9-v3C remains blocked on V3-A1 and P10 on V3-A2; later security/privacy gates remain binding.

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
10. `docs/p9_v3_preexecution_audit.md` and `docs/formal_specification_v3_1.md` — historical v3.1.0 suitability amendment; its human prerequisite is superseded by v3.2.
11. `docs/formal_specification_v3_2.md` and `experiments/v3/config/preregistration_v3_2.json` — active project-authored-ground-truth correction; v3.0/v3.1 pipelines, support, gates, and limits remain binding.
12. `docs/formal_specification_v3_3.md` and `experiments/v3/config/preregistration_v3_3.json` — prospective development-only threshold-calibration rule and provenance boundary.
13. `experiments/v3/config/preregistration_v3_1.json` and `visual_observation_v3_1.json` — machine-readable pipeline/resource/support freeze; the un-suffixed configs preserve v3.0.0.
14. `experiments/v2/config/preregistration_v2.json` — immutable historical v2 freeze and failed path.
15. `paper/draft.tex` — planning manuscript with the bounded P9-v2 result and no false v3 findings.

`docs/security_model.md` remains the frozen v1 model. `paper/main.tex` now builds the active IEEE planning manuscript in `paper/draft.tex`. The old sample and pre-migration draft are archived in `paper/templates/popets-2027/`; root ACM support files and `sample-base.bib` are legacy material. Use `paper/README.md` for build instructions.

## Scientific boundaries

- No participant study is authorised. Do not claim memorability, recall, usability, preference, or learning effort.
- Reconstructable semantic authentication is the object of study; C1/C2 enable the central C3 acceptance-region and C4 private-verification questions.
- Algorithms, model identities, canonicalisation, policies, and thresholds are public. An attacker succeeds with any accepted semantic alternative, not only the enrolled prompt, image, or graph.
- VSA already covers image-independent visual-semantic authentication, VLM extraction, canonical tokens, object/attribute/count/quadrant facts, Flexible Range Logic, and user-selected policies. These are not v2 novelty.
- Semantic correctness and cryptographic privacy are separate gates. Hashing, salting, or encryption alone does not establish template privacy, offline resistance, or unlinkability.
- Client-side feasibility is measured under RQ6 rather than assumed. Research-GPU availability is not a deployment result, and secret-bearing prompt/image/semantic processing must not be moved to an untrusted cloud to rescue an impractical client design.
- Execute one numbered phase at a time. P9-v2's V2-A failure remains historical evidence; the explicit v3 reframe must pass V3-A1 and V3-A2 before P10. Never bypass later V2-B–V2-F gates.

Large models, raw datasets, generated images, secrets, caches, and recomputable intermediates must not be committed. Version compact manifests, configs, tests, aggregate evidence, and exact provenance required for claims.
