# AGENT.md - Semantic Secrets research contract (v4 direction)

## 1. Authority and active status

The project author approved the v4 direction and this documentation amendment on **26 October 2026**, recorded as **DIRECTION-V4-01** in DECISIONS.md. This contract supersedes conflicting active-direction, sequencing and automatic-stop instructions in older documents. It does not rewrite historical results, machine-readable freezes or their gate meanings.

Read this file, PLAN.md, docs/research_direction_v4.md, docs/p9_v4_study_design.md and docs/phase_workflow.md before project work. The active security scope is docs/security_model_v4.md and docs/threat_claim_matrix_v4.csv. The v2/v3 specifications remain authoritative for interpreting their own records, not for silently executing v4.

**Current permission:** update the project documentation, paper framing, research-description sources/PDFs and validate those edits. No experimental phase is started or completed by this amendment. No API calls, model execution/acquisition, GPU rental, dataset generation/acquisition, final reference authoring, evaluator repair or submission is authorized by it.

## 2. Mandatory author control

Before every phase or subphase, explain in detail **what will be done, how, why, inputs/dependencies, changed files, data and model/service choices, costs/call limits, evaluation criteria, possible outcomes and alternatives**. Then wait for the author's explicit authorization. Approval of the direction or a preceding phase is not execution approval. Once a fully explained phase is approved, work within that approved scope without repetitive permission requests.

Read-only inspection to prepare a proposal is permitted if it does not execute models, acquire data, expose held-out material or incur charges. Substantive changes after approval need a revised proposal and authorization. Full procedure: docs/phase_workflow.md.

If an error or experiment failure occurs, preserve evidence, diagnose known versus suspected causes, explain the scope of the finding, provide credible alternatives and recommend a next step. Do not automatically reject the hypothesis, abandon the approach, or terminate the project. Pause affected work when evidence integrity, approval limits or unresolved faults require it; explain the pause and obtain a decision for substantive continuation.

Failure handling does not authorize endless retries, favorable-case selection or post-hoc threshold changes. Respect an explicitly approved bounded retry policy; preserve valid negative results. New outcome-affecting methods require a new version and appropriately independent evaluation. Project termination or abandonment is the author's decision after explanation, not an automatic gate side effect.

## 3. Research question and contribution boundary

Working title:

> Semantic Secrets: Reconstruction and Security-Relevant Semantic Distinctions in Visual Authentication

Central question:

> Can users reconstruct a semantic credential reliably while keeping related but unauthorized alternatives distinguishable, and how do perception and normalization affect that balance?

The experiments use researcher-authored concepts and independent image generations, not human participants. They can measure technical reconstructability, not human recall, memorability, usability, preference, accessibility, natural secret choices or real authentication time.

Immediate proposed contributions:
- **V4-C1:** a methodology connecting perception/normalization errors to authentication outcomes.
- **V4-C2:** evidence about which semantic distinctions survive or collapse across named pipelines and image sources.
- **V4-C3:** independent reconstruction and finite-budget attacker outcomes under frozen acceptance rules.

All are hypotheses. Extraction accuracy alone, a model leaderboard, synonyms, graph notation, model assembly or a dataset is not assumed to be a novel security contribution. Refresh the exact v4 novelty claim; P8's prior gate does not automatically validate it.

Historical C1-C4 retain their original meanings. Reconstruction and acceptance-region security inform v4; the system-derived mandatory/tolerant policy is a candidate mechanism, not an assumed winner. C4 private verification is a distinct deferred goal and is not claimed by an API-based semantic study. A complete private system still needs its own functionality, construction, correctness, leakage, compromise and attack evidence.

## 4. Pipeline and data roles

Intended concept C -> reconstruction prompt P -> independent image I = G(P,r) -> bounded observations O -> versioned normalization N -> deterministic compiler -> graph S or typed failure -> frozen acceptance predicate.

The prompt is an interface, the image a transient medium, observations probabilistic evidence, and the canonical graph the predicate's representation. Generated pixels add no credential entropy. The attacker's winning surface is the full acceptance region A(S) = {S': Accept(S,S') = 1}, not the exact prompt, pixels or graph.

Initially compare one feasible generative VLM pipeline and one feasible specialized perception pipeline. Grounding DINO/SigLIP2 are also vision-language components. Exact APIs/models and their shared task contract are pending design and approval. Models emit bounded instance facts; code owns identifiers, validation, canonical ordering, deduplication and serialization. Preserve attribute ownership and relationship roles; flat word arrays cannot establish graph binding.

- Generated naturalistic images: primary reconstruction workflow evidence.
- Controlled drawings: isolated diagnostic contrasts.
- Photographs: external visual generalization, subject to provenance/rights and training-overlap limits.

Families center on identity, attribute binding, cardinality, interaction and spatial distinctions. Originals, derivatives and close alternatives stay in the same partition. The author manually labels actual visible image content without model predictions. Intended concepts and final-image references remain separate so generation errors are not scored as extraction errors. Author self-review is not independent annotation agreement.

Deterministic formatting and reviewed, frozen aliases are the primary normalization arm. Development-time LLM suggestions require review. Optional live LLM normalization uses the same cached observations, cannot add facts or access references, and must measure false merges/splits, coverage and stability as well as acceptance effects. Abstraction is not automatically synonymy; unknowns follow a frozen unsupported/abstention rule.

## 5. API-first execution and later deployment

Use approved APIs only on public or safely authorized non-secret research fixtures. Defer GPU rental and local model inference. A public model name does not establish API availability, pinned checkpoint identity, license compatibility or required output support.

Record service/model IDs, exposed revisions, requested versus attested settings, raw requests/responses and hashes, timestamps, failures/retries, calls, cost and observed latency. Do not silently substitute hosted models or infer GPU/model-only performance from API latency. Repeated hosted calls test service stability; replaying caches tests downstream determinism.

Local execution is a later separately authorized semantic-parity and performance milestone. For the strongest future private architecture, secret-bearing prompts, images, observations, graphs and embeddings remain within a trusted client. Providers used on public fixtures are not thereby trusted recipients of real authentication secrets.

## 6. Security and novelty discipline

Algorithms, model identities, canonicalization, vocabularies, policies and thresholds are public. An attacker succeeds with any accepted alternative. Specify candidate interface, K0 generic / K1 source-frequency / K2 partial-target / K3 near-secret information, auxiliary data, budget, duplicates, oracle and costs. Separate random FAR, conditional targeted-neighbor acceptance, adaptive success and offline tests. Do not claim to exhaust the acceptance region from sampled attacks.

VSA is the mandatory closest-work comparison. Separate its semantic-policy component from its full semantic-plus-password architecture. Image-independent semantic authentication, canonical tokens, object/attribute/count/quadrant rules, flexible quantities, conjunction and user-selected policy are prior art. See docs/vsa_2026_comparison.md and docs/p8_novelty_review_v2.md.

Never claim first semantic/image-independent/VLM/policy/generative authentication without a new scoped verified review. No novelty from M/T notation, dictionary/LLM normalization alone, or standard cryptographic primitives. Do not claim password/passkey superiority, human benefits, entropy from generated pixels, or private/offline-resistant/unlinkable verification from hashing, salting or encryption alone.

Private verification remains independent: define records, services/keys, transcripts, leakage, replay/context binding, collusion and total-compromise outcomes before any such claim. Rate limits are online assumptions, not an offline defense. Cryptography cannot repair an easily reached semantic acceptance region.

## 7. Evidence integrity and historical boundary

- Preserve P0-P7, P8, failed P9-v2 and v3.0-v3.4 freezes/results under their original identifiers.
- P9-v2 failed its direct complete-JSON schema gate by logical futility; it did not measure full semantic capability or establish universal VLM impossibility.
- P9-v3 methodology and engineering are reusable preparation, not empirical validation. Its branch is paused, not passed or rejected.
- The 26 October audit reported 240 v3 images, 120 controlled references and no completed naturalistic references/final freeze; formal v3 inference has not started. It also found one-to-one entity-scoring and moved-manual-path defects. They remain unfixed by this documentation update.
- The 421 passing core tests include 320 compiler cases; these are historical engineering evidence, not new validation or model results.
- The twelve sealed v1 families remain sealed. Existing inspected v3 images default to development/diagnostic use in v4; audit exposure before any approved reuse.
- Fresh v4 identifiers, splits, data roles, methods and criteria must be authorized/frozen before their formal outputs. No favorable post-hoc support, threshold, policy, pipeline or stratum selection.
- Same-image repeats, independent generations and fresh attack trials answer different questions. Do not select cached positive samples because they already match.
- Enforce one-to-one object correspondence, failure denominators, family-level uncertainty and raw-to-derived provenance.
- API engineering or measurement results do not pass the old V3 resource/capability gates. No cross-version relabeling.

## 8. Milestones and completion

PLAN.md defines the active path: P9-v4A design -> P9-v4B implementation/repair -> P9-v4C API pilot -> P9-v4D formal references/freeze -> P9-v4E capability comparison -> P10-v4A/B reconstruction/policy design and evaluation -> P11-v4A/B attack design and evaluation -> P17-v4 analysis -> P18-v4 manuscript -> P19-v4 artifact -> P20-v4 submission audit.

Every arrow requires dependency review and a separate phase explanation/authorization. Measurement validity, constructive viability and publication readiness are different decisions. A valid negative finding may support a completed measurement study after authorized diagnosis; it does not pass a constructive gate or unlock protocol engineering. Numeric v4 criteria are not yet fixed. The next action is to propose P9-v4A, not execute it.

Old P9-v3B/C and P10-P20 instructions in PLAN.md are archived/deferred reference, not active permission. A private-verification branch needs its own explained and approved v4-compatible plan; the old constructive security/privacy standards are not waived.

## 9. Engineering and delivery

Keep observation, normalization, compiler, policy, matcher, attacks and optional protocol modules separate. Version substantive changes; preserve raw evidence and failures. Use mature cryptographic libraries if future work is approved.

Keep secrets, credentials, models, raw datasets and recomputable large intermediates out of Git. Commit compact manifests, configurations, tests, aggregate evidence and provenance. Preserve unrelated user edits, especially the manual-validation reorganization. A completed authorized phase may follow the existing checkpoint instruction only for its own work; this direction amendment does not complete an experimental phase or authorize a new push.

## 10. EuroS&P 2027

Target: 12th IEEE European Symposium on Security and Privacy. Mandatory registration **25 November 2026 AoE**; paper **2 December 2026 AoE**. Official venue policies and provenance remain in docs/eurosp2027_requirements.md and docs/eurosp2027_submission.json. The date-only CFP does not specify an exact cutoff clock; verify HotCRP before submission.

Use the supplied IEEE A4 template and 13-body-page limit, anonymous authorship/artifacts, body harm analysis, Data Availability and anonymous AI-use acknowledgments. Internal targets remain evidence review 13 November, metadata 24 November, final audit 30 November, upload buffer 1 December. Dates authorize no action.

The active paper focuses on V4-C1-C3 with privacy as an explicitly deferred boundary. No submission-ready system or positive result is claimed. Missing a venue cycle is preferable to unsupported findings; non-submission does not terminate the research.
