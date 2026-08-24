# Semantic Secrets decision log

Important decisions use the record format defined in `PLAN.md`. Revisit a closed decision only if new evidence invalidates a stated assumption.

## P1-01 — Early novelty and PETS-scope checkpoint

**Decision:** Continue to P2 with a narrowed provisional contribution boundary; do not claim first visual-semantic or image-agnostic authentication.

**Date:** 2026-08-24

**Status:** Selected for planning; not an experimental result and not permission to execute P2.

**Question:** Does verified closest work leave a plausible novel, PETS-relevant contribution worth formalising before implementation?

**Candidates:**

1. Continue with the original broad “semantic image authentication” novelty story.
2. Continue with a narrower privacy/measurement story.
3. Stop the PETS research path because prior work already subsumes it.

**Evaluation criteria:** Verified closest work; core-overlap versus gap; real-world privacy relevance; feasibility of testing the gap without a human study; compatibility with the 12-page PoPETs story; whether the contribution is more than composition of known primitives.

**Evidence:**

- `docs/related_work.csv`, especially VSA 2026, RFC 9497, RFC 9807, Pinkas et al., Neural Fuzzy Extractors, HyDia, embedding leakage, and biometric unlinkability.
- `docs/pets_requirements.md` and official 2027 CFP/author rules.
- VSA DOI 10.13089/JKIISC.2026.36.3.935 establishes prior image-agnostic semantic authentication using Grounding DINO + CLIP, explicit semantic policies, FlexibleRange matching, hash-based binding, and COCO FAR/FRR evaluation.

**Selected option:** Candidate 2. Continue only around a conditional combination of:

- a formal acceptance-region model for noisy, user-chosen semantic knowledge secrets;
- private approximate/threshold verification with precisely stated leakage and compromise guarantees;
- database/server/key compromise, offline validation, inversion, and cross-service linkability analysis;
- realistic frequency/AI/partial-information semantic guessing;
- independently generated image re-creation and a mandatory paired text-only ablation; and
- an end-to-end reproducible implementation if earlier gates pass.

This is a provisional boundary, not a novelty or security claim. P2 must formalise it; Gates A–F can still reject or reframe it.

**Rejected alternatives:**

- Candidate 1 is rejected: VSA makes any “first semantic image authentication,” “first image-agnostic semantic policy,” or novelty based only on Grounding DINO/CLIP + approximate semantic rules untenable.
- Candidate 3 is not selected yet: no verified work in the focused screen subsumes the complete acceptance-region + private-verification + compromise/linkability + AI-guessing + generative-recreation question.

**Reason:** The project has a plausible PETS privacy question, but only if privacy properties and attacks—not AI image generation or semantic matching by themselves—are the core contribution. OPRF, OPAQUE, PSI, fuzzy extractors, FHE threshold matching, embedding inversion, and unlinkability analysis are all established prior art. Novelty must come from a rigorously justified construction/analysis for this specific noisy semantic-secret setting, not from renaming or merely composing primitives.

**Security/privacy assumptions:** None selected. Single-server, non-colluding service, threshold-key, and key-isolation hypotheses remain unresolved for P2/P9–P11. Hash binding is not assumed to prevent offline semantic dictionaries.

**Affected RQs:** RQ3, RQ4, RQ5, RQ6; indirectly RQ1/RQ2 because semantic viability is prerequisite.

**Experiments supporting decision:** No experiments were run. This checkpoint uses verified literature/standards only. Future support must come from E7–E16 and Gates A–E.

**Remaining uncertainty:**

- The authoritative VSA bibliography and abstract were verified, but its full detailed threat model and algorithm text could not be retrieved through the available HTTPS sources. Before implementing the mandatory VSA baseline, obtain and translate the full article and verify policy, binding, attacker, and evaluation details line-by-line.
- A focused P1 screen cannot prove global novelty. Search should be refreshed in P9 around the exact protocol selected and again in P15/P17.
- No evidence yet shows that semantic credentials are stable, separable, hard to guess, or valuable after removing the image stage.

**Revisit trigger:** Full VSA text or newly found work provides private semantic threshold authentication with equivalent compromise/guessing analysis; Gate A/B failure; P9 finds the protocol contribution already known; or venue scope changes.

## P1-02 — Submission issue planning

**Decision:** Do not target Issue 2; keep Issue 3 as aggressive and Issue 4 as the first credible planning target, pending user scheduling.

**Date:** 2026-08-24

**Status:** Proposed project-management decision; not a scientific gate.

**Question:** Which PoPETs 2027 issue can accommodate P2–P17 without weakening scientific gates?

**Candidates:** Issue 2 (2026-08-31), Issue 3 (2026-11-30), Issue 4 (2027-02-28), or later/non-PETS submission.

**Evidence:** Official dates and process in `docs/pets_requirements.md`; current repository has no implementation or experiments.

**Selected option:** Exclude Issue 2. Plan against Issue 4 unless progress through Gates A–D makes Issue 3 honestly achievable. User confirmation is still required.

**Rejected alternatives:** Issue 2 is seven days away and incompatible with the contract. Issue 3 is not rejected but is high risk.

**Reason:** A deadline cannot justify skipping semantic viability, image necessity, protocol comparison, compromise analysis, attacks, or reproducibility.

**Security/privacy assumptions:** None.

**Affected RQs:** All.

**Experiments supporting decision:** None.

**Remaining uncertainty:** Available compute, researcher time, revision strategy, and target issue.

**Revisit trigger:** User selects a schedule; major gate failure/reframe; or venue dates change.

## P2-01 — Freeze threat-model version v1 without selecting an architecture

**Decision:** Freeze the formal definitions, privacy goals, leakage classes, compromise states, A1–A8 evidence mapping, and inference/ethics boundaries in `docs/security_model.md` as threat-model version v1 for P3–P8 pilot design. Do not select a protocol or deployment architecture before D6/D7.

**Date:** 2026-08-24

**Status:** Selected.

**Question:** Is the project model precise enough for pilot design while preserving an evidence-based choice among single-service, separate-service, threshold, and isolated-key hypotheses?

**Candidates:** Freeze a protocol-neutral v1; select the preferred two-service direction now; retain the informal `AGENT.md` model without a freeze; or stop/reframe because every plausible architecture is already known to provide no benefit.

**Evaluation criteria:** Each central claim names an attacker, asset, compromise boundary, success condition, leakage class, and proof/experiment; A1–A8 can be walked through all four hypotheses; total compromise and collusion outcomes are explicit; no human inference or unmeasured privacy adjective is introduced; future D6/D7 evidence remains able to reject every candidate.

**Evidence:** `docs/security_model.md`; `docs/threat_claim_matrix.csv`; P1 closest-work and protocol/privacy anchors in `docs/related_work.csv`; the existing RQs, adversaries, exclusions, and decision gates in `AGENT.md` and `PLAN.md`.

**Selected option:** Freeze protocol-neutral v1. Treat H1 single service, H2 separate privacy service, H3 threshold services, and H4 isolated key as hypotheses. Use v1 definitions for P3–P8 methodology, then instantiate and compare exact views in P9–P11.

**Rejected alternatives:** Selecting H2 now would pre-empt D6/D7 without correctness, leakage, compromise, or performance evidence. Leaving the model informal would allow incompatible claims and experiments. Stopping is not justified analytically: conditional database-snapshot or partial-compromise benefits remain plausible, but unproved.

**Reason:** The same stored record can be benign in a database-only view and become a fast verifier once a colocated key is acquired. Similarly, non-collusion, threshold, and key isolation shift rather than eliminate trust and availability costs. A protocol-neutral compromise matrix is necessary before experiments and prevents later results from changing the attacker definition.

**Security/privacy assumptions:** Trusted legitimate client and pinned local models during use; public algorithms and non-uniform semantic source; authenticated confidential replay-resistant transport; exact service behaviour and cryptographic assumptions deferred to the candidate. No blanket protection after total service/key compromise. No silent fallback when an auxiliary service/share/key boundary is unavailable.

**Affected RQs/threats/claims:** RQ1–RQ6; A1–A8; G1–G9 defined in `docs/security_model.md`; E7–E13/E15.

**Experiments supporting decision:** None. P2 is an analytical definition phase. The matrix preregisters required proof/experiment families; it does not report security results.

**Remaining uncertainty:** Semantic representation/matcher, attacker distributions, leakage of concrete primitives and implementations, active-security support, realistic trust/deployment cost, threshold and rate-limit values, and whether any candidate improves meaningfully on plaintext/hash-bound baselines.

**Revisit trigger:** A pilot requires an undefined success condition; P9 identifies a candidate whose view cannot be expressed by v1; new closest work changes the relevant attacker; a protocol proof requires a different corruption model; or an ethics/data review changes allowed inputs. Semantic changes create v2 rather than silently rewriting v1.

## P3-01 — Approve controlled smoke/pilot methodology; forbid full scale

**Decision:** Approve controlled ontology/design v1, the 12-family smoke catalog, deterministic family-grouped splits, label-separated manifests, and a planned 60-family pilot. Keep pilot execution and every full-scale acquisition/generation step unapproved.

**Date:** 2026-08-24

**Status:** Selected.

**Question:** Does the proposed data methodology cover the semantic and attacker factors required by P2 without creating human-behaviour claims, cross-split leakage, or unjustified compute?

**Candidates:** Full Cartesian factorial generation; fractional one-factor-at-a-time controlled design; unstructured public prompts as the main evaluation set; or stop because a controlled non-human methodology is impossible.

**Evaluation criteria:** Coverage of objects/attributes/counts/actions/relations/scenes, complexity and planned frequency strata; targeted one-atom and unrelated negatives; paired text-only path; deterministic recreation; family-level split isolation; ground-truth separation from execution inputs; ethics/provenance; uncertainty-driven full sizing; compatibility with E1–E8/E12–E14/E16.

**Evidence:** `experiments/datasets/README.md`, `ontology_v1.json`, `config/design_v1.json`, `concepts/smoke_v1.json`, schemas, manifests, `power_and_uncertainty.md`, generator validation, and four passing unit tests. The smoke design has 12 families/24 concepts, covers all six atom types and complexity levels 1–5, and replaces exactly one atom in each targeted neighbour.

**Selected option:** Fractional controlled design. For each family, change one technical factor from enrolment at a time and generate canonical near-neighbour/unrelated comparisons. Use 12 families only for smoke validation and plan 60 families for variance/resource estimation; derive full `n` from pilot cluster-level uncertainty and preregistered precision.

**Rejected alternatives:** A full Cartesian product adds compute and interaction cells before their need is established. Public prompts lack controlled semantic ground truth and do not represent authentication choices. Stopping is not required because the smoke method passes its analytical and deterministic checks.

**Reason:** Family-grouped fractional trials preserve causal interpretability for seed/paraphrase/style/layout/model effects, support the mandatory text-only pairing, and prevent repeated images from masquerading as independent secrets. Label-separated inputs prevent pair/ground-truth metadata from influencing model execution.

**Security/privacy assumptions:** Controlled prompts are synthetic research inputs, not secrets. Frequency labels are design strata until P8 derives a separate training-only empirical measure. Public algorithms and labels may be released after licence review, but labels remain sealed during candidate/test evaluation.

**Affected RQs/threats/claims:** RQ1–RQ3/RQ6; A1/A4/A5/A8; G1/G9; E1–E8/E12–E14/E16; Gates A/B.

**Experiments supporting decision:** No AI/model experiment. Manifest generation produced 84 image-path inputs, 36 deduplicated text inputs, 84 labels, and 84 same/near/unrelated pairs. Outputs recreated byte-identically; schema/manual invariants, joins, quotas, atom edits, and split isolation passed.

**Remaining uncertainty:** Real generator/extractor failures, variance and clustering, frequency-band evidence, smallest technically meaningful image-versus-text effect, model licences/costs, pilot authoring workload, and full sample size.

**Revisit trigger:** P4 model constraints invalidate prompt controls; blind audit finds ambiguous concepts; pilot variance/coverage requires interaction cells or narrower ontology; or P6/P7 freezes a justified full design. Changes create a new catalog/design version.

## P3-02 — Public prompt source screen and acquisition boundary

**Decision:** Conditionally approve DiffusionDB metadata for a later, text-only A4 frequency ordering; approve PartiPrompts only for technical coverage; defer Pick-a-Pic v2; acquire none in P3.

**Date:** 2026-08-24

**Status:** Selected for planning; D8 attack-distribution selection remains open until P8.

**Question:** Which public prompt sources can add distinct evidence under documented licence, ethics, identifier, and distribution limits?

**Candidates:** DiffusionDB metadata; PartiPrompts; Pick-a-Pic v2; uncontrolled scraping; controlled synthetic distribution only.

**Evaluation criteria:** Authoritative source/card, current licence and revision pinning, minimisable identifiers, harmful-content handling, reproducibility, relation to A4, distinct role, and no claim that text-to-image prompts are authentication choices.

**Evidence:** `experiments/datasets/sources_v1.json`, `data_statement.md`, and `acquisition_plan.md`; official source repositories/cards checked on 2026-08-24. DiffusionDB exposes a metadata-only path and declares CC0, but contains contributor-linked fields to discard. PartiPrompts is an Apache-2.0 curated benchmark. The official live Pick-a-Pic v2 card/licence could not be fully retrieved and mirror-visible user-level fields are unnecessary.

**Selected option:** Plan a minimal, pinned DiffusionDB metadata pipeline only when P8 authorises it; use PartiPrompts separately for coverage if P4/P5 needs it; do not acquire Pick-a-Pic or scrape other services.

**Rejected alternatives:** Pick-a-Pic is deferred until its exact live revision/licence/removal terms and a distinct need are verified. Uncontrolled scraping lacks a bounded ethical/licence/reproducibility story. Synthetic-only remains the fallback if public acquisition fails closed.

**Reason:** DiffusionDB can order a clearly qualified empirical attacker without images or identity fields. PartiPrompts answers a different technical-coverage question. Neither can establish authentication-secret selection, and adding a user-level preference dataset without a distinct role would increase privacy burden without necessary evidence.

**Security/privacy assumptions:** Drop rather than rehash usernames/user IDs, timestamps, image IDs, session/ranking linkage, and URLs. Filter harmful/sensitive content before downstream models. Do not identify or target contributors. Release aggregates by default and recheck terms/removals before final runs.

**Affected RQs/threats/claims:** RQ3; A4/A5; G1/G2; D8; E8/E12/E13.

**Experiments supporting decision:** None; no public data was downloaded. This is a source/ethics/licence screen.

**Remaining uncertainty:** Exact future snapshots/hashes, filter performance, prompt language/content mix, source removals/terms, empirical coverage, and whether DiffusionDB materially changes attack ordering.

**Revisit trigger:** P8 attack pilot, a changed official source card/licence, a removal notice, filter failure, a distinct documented need for another distribution, or inability to strip identifiers at the parser boundary.
