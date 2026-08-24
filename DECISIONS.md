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
