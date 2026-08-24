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

## P4-01 / D1 — Provisional local generator shortlist

**Decision:** Provisionally select SD-Turbo as the primary generator hypothesis, retain SDXL base 1.0 as the sole stronger-hardware alternative, and preserve the direct-text/no-image path. Production generator acquisition remains conditional.

**Date:** 2026-08-24

**Status:** Selected provisionally; generator quality and local CUDA feasibility are not established.

**Question:** Which smallest generator shortlist is reproducible, licensable for the research, scientifically useful, and plausibly executable on the documented local hardware?

**Candidates:** SD-Turbo; SDXL base 1.0; unrestricted additional generator finalists; no-image/direct-text; or stop the image path.

**Evaluation criteria:** Official availability and licence; immutable revision/acquisition identity; deterministic controls; expected weight, VRAM, RAM, latency, and storage cost; controlled-atom renderability; stable local execution; one primary plus at most one distinct alternative; no full-corpus spend before feasibility.

**Evidence:** `docs/model_screening.md`; `experiments/model_screening/model_manifest.json`; `p4-screen-v1`; official SD-Turbo and SDXL model cards/licences. The machine has a 4 GiB NVIDIA T600 but PyTorch 2.13.0 is CPU-only. A pinned tiny Diffusers fixture reproduced the same RGB hash under a fixed seed and differed under a second seed, validating only the interface/configuration plumbing.

**Selected option:** SD-Turbo is the provisional primary because its 512 px, one-to-four-step distilled configuration is the least implausible production generator for the target. SDXL base is retained only as a quality/model-drift comparison on documented stronger hardware. The no-image path remains mandatory for P7.

**Rejected alternatives:** Expanding the shortlist is rejected because it adds acquisition and tuning cost without a distinct scientific role. SDXL base is rejected as the default local generator because its roughly 6.94 GB standalone checkpoint and expected runtime exceed the present 4 GiB/CPU-only configuration. Stopping the image path is premature until a repaired CUDA environment and controlled renderability screen provide direct evidence.

**Reason:** P4 is a feasibility gate, not a model leaderboard. Downloading production generator weights before the platform can exercise CUDA would not cheaply resolve fit or semantic quality. The conditional selection preserves one credible small candidate and one scientifically useful SDXL-class comparison without committing corpus compute.

**Security/privacy assumptions:** All generation remains local in the strongest architecture. Model, prompt, seed, scheduler, and preprocessing identities are public; prompts and outputs are not sent to a cloud service. Model acquisition is not secret processing. Licence/AUP compliance remains mandatory.

**Affected RQs/threats/claims:** RQ1/RQ5/RQ6; E1–E4/E14/E16; D1/D5; A5/A7 where model availability or compromise affects recreation; no security or authentication claim is supported by the fixture.

**Experiments supporting decision:** `p4-screen-v1` generator interface/determinism fixture only. No SD-Turbo or SDXL weights were acquired and no semantic coverage was measured.

**Remaining uncertainty:** CUDA installation compatibility, actual VRAM/RAM/latency, deterministic behaviour on GPU, licence changes, atom renderability, generator failures, output drift, and whether the image stage adds technical value.

**Revisit trigger:** Before any P3 corpus generation, repair and freeze the CUDA environment, acquire SD-Turbo at the pinned revision, record file hashes, and run a fixed-seed resource/renderability smoke test. Reject or resize/offload it if the target fails; stop/reframe the image path if no local candidate meets the frozen criterion. SDXL runs require separately documented stronger hardware.

## P4-02 / D2 — Extractor and semantic-baseline shortlist

**Decision:** Advance Florence-2-base, SigLIP base 224, all-MiniLM-L6-v2, and controlled parser v1 as four scientifically distinct P5 hypotheses/baselines. Reject SmolVLM-256M-Instruct as a strict structured extractor under schema/config v1. Do not select a primary extractor until P5.

**Date:** 2026-08-24

**Status:** Selected shortlist; primary extractor open.

**Question:** Which small set covers structured image semantics, dense image semantics, dense direct-text semantics, and transparent structured direct-text semantics without carrying candidates that already show gross schema, coverage, or runtime failure?

**Candidates:** Florence-2 detector/caption/geometry; SmolVLM constrained JSON; SigLIP dense image embeddings; MiniLM dense text embeddings; controlled lexicon parser; additional unbounded VLM/captioning families; or exact infeasibility/reframe of structured image extraction.

**Evaluation criteria:** Exact revision/licence/acquisition identity; fixed-input repeatability; strict schema validity; simple object/attribute/count/relation probe coverage; latency and peak process RSS; scientific distinctness; versionable local execution; compatibility with P5 canonicalisation and later private-matching analysis.

**Evidence:** `results/p4/screen_v1.json` and `docs/model_screening.md`. SmolVLM produced byte-identical but invalid outputs in all 6/6 attempts, covered 0.20 of expected lexical probes, required approximately 28.7–31.4 seconds per CPU fixture, and peaked around 3.7 GiB process RSS. SigLIP exactly repeated its `3 × 768` embedding hash, selected the matching label for 3/3 procedural fixtures, and used about 0.41–0.61 seconds per three-image batch after load. MiniLM exactly repeated finite `36 × 384` embeddings in 0.05–0.07 seconds. The controlled parser exactly repeated 36 schema-valid outputs twice; its vocabulary is intentionally constrained. Every acquired artifact file hash is stored in the run.

**Selected option:** Retain Florence-2 as the one structured image-family hypothesis because its task-specific detection, dense-caption, grounding, and geometry outputs differ materially from unconstrained JSON generation; it must still be acquired and screened in P5. Retain SigLIP and MiniLM as mandatory dense baselines and parser v1 as a transparent structured text lower bound.

**Rejected alternatives:** SmolVLM is rejected under config/schema v1 with `QF-SCHEMA`, `QF-COVERAGE`, and `QF-LATENCY`; deterministic repetition of the same malformed template is not semantic viability. More VLMs are rejected from the P4 shortlist because they do not add a necessary family before Florence is tested. Treating the controlled parser as the only text representation is rejected because its ontology-tuned vocabulary overstates open-ended coverage.

**Reason:** The shortlist spans four materially different approaches while preserving mandatory image/text dense baselines. It records the structured-VLM negative result instead of repairing JSON after generation or changing the schema post hoc. A task-specific detector/geometry path remains worth one bounded paired test; no evidence yet supports a primary representation.

**Security/privacy assumptions:** All extraction occurs locally; raw images, prompts, atoms, embeddings, and scores remain client-side in the strongest target. Dense representations may create inversion/linkability surfaces and receive no privacy presumption. Executable remote model code must be reviewed and revision-pinned before Florence runs.

**Affected RQs/threats/claims:** RQ1/RQ2/RQ4/RQ5/RQ6; E1–E6/E10/E14/E16; D2/D3; A1/A3/A5/A7/A8; Gate A remains unopened.

**Experiments supporting decision:** `p4-screen-v1`, two fixed repeats over three procedural image fixtures and 36 controlled text inputs. These are engineering observations, not publication accuracy, security, or reliability results.

**Remaining uncertainty:** Florence schema/atom coverage and remote-code requirements; behaviour on generated and natural images; atom-level error; positive/negative separation; calibration; drift; canonicalisation; embedding inversion/linkability; GPU performance; and compatibility/cost of private evaluation.

**Revisit trigger:** P5 paired outputs and uncertainty estimates. If Florence fails the frozen schema/coverage criteria, narrow the ontology or record exact infeasibility and reframe the structured-image path; do not silently replace it with a cloud dependency. Any new family must have a documented scientific role and pass the same fixed screen.
