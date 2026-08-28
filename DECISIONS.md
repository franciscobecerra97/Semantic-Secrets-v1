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

## P5-00 / D1 update — SD-Turbo is numerically feasible only through float32 oversubscription

**Decision:** Retain SD-Turbo only as the measured image-path backend for bounded experiments; freeze the P5 configuration as float32 CUDA with WDDM oversubscription and do not approve pilot/full generation from this result.

**Date:** 2026-08-24

**Status:** Selected conditionally for bounded image-path evidence; not approved as a scalable local generator.

**Question:** Did the P4 provisional SD-Turbo candidate pass the required local CUDA/resource/renderability check?

**Candidates:** fp16 CUDA on PyTorch 2.13/CUDA 13.0; fp16 CUDA on PyTorch 2.12.1/CUDA 12.6; float32 CUDA using the pinned fp16 files upcast at load; undisclosed cloud generation; or stop the image path.

**Evaluation criteria:** Finite latent and non-degenerate pixels, exact fixed-seed repetition, immutable model/config identity, documented memory/latency, no cloud secret processing, and bounded cost before pilot scale.

**Evidence:** `p5-smoke-v1`, `results/p5/generation_manifest_smoke_v1.json`, and `docs/representation_screening.md`. Both official CUDA builds executed the fp16 path but produced all-NaN UNet latents and black images. Float32 produced 27 non-degenerate images and an identical fixed-seed repeat, with median 25.80 seconds/image and 5,716.78 MiB peak allocation on a physical 4,096 MiB T600 through WDDM oversubscription.

**Selected option:** Use float32 only for the bounded P5 image screen. Keep the exact one-step, guidance-zero, 512×512, explicit-seed configuration and pinned revision. Treat `QF-NUMERIC-FP16` and `QF-HARDWARE-OVERSUBSCRIPTION` as unresolved scalability failures.

**Rejected alternatives:** fp16 is rejected on this machine because both justified runtime variants produced non-finite latents. A cloud fallback is rejected because it changes the privacy/deployment boundary. Pilot/full generation is not approved because physical VRAM is exceeded and the image stage has not shown a technical benefit.

**Reason:** The float32 path was sufficient to obtain the cheapest image representation evidence, but resource feasibility is marginal and dependent on Windows memory virtualization. It cannot support a scalable-local claim.

**Security/privacy assumptions:** Generation is local over project-authored benign prompts. Model acquisition is public. No prompt or image is sent to a service. Raw images remain in an ignored cache.

**Affected RQs/threats/claims:** RQ1/RQ5/RQ6; E1–E4/E14/E16; D1/D5; local deployment/resource claim only.

**Experiments supporting decision:** One production fixed-seed contract image under each attempted dtype/runtime plus the frozen 27-row P5 generation screen and one repeat.

**Remaining uncertainty:** Linux/non-WDDM behavior, other supported GPUs, SDXL comparison, larger-run failure rate, model drift, semantic renderability by atom type, and image-stage necessity.

**Revisit trigger:** P7 paired image/text evidence shows a credible technical benefit, new documented hardware is available, or a distinct generator backend can meet the same frozen local criterion. Any change creates a new backend/config ID.

## P5-01 / D2 — Reject Florence structured fusion; use direct text as the primary extractor hypothesis

**Decision:** Reject Florence-2-base caption/detection/geometry fusion as the structured primary under config v1. Use the controlled direct-text parser as the primary P6 extractor hypothesis, keep SigLIP as the mandatory image baseline, and keep MiniLM as the mandatory dense text baseline.

**Date:** 2026-08-24

**Status:** Selected for P6 hypothesis testing; no extractor is Gate A viable.

**Question:** Which P4 extractor survivors provide sufficiently faithful, deterministic, distinct outputs to enter P6?

**Candidates:** Florence structured fusion; controlled direct-text structured extraction; SigLIP dense image; MiniLM dense text; revive SmolVLM; add another unbounded VLM; or record structured-image infeasibility.

**Evaluation criteria:** Fixed-input repeatability; object/attribute/action/count/relation/scene fidelity; same/near/unrelated diagnostic separation with family uncertainty; versioning; latency/memory; leakage; private-comparison plausibility; and distinct scientific role.

**Evidence:** `p5-smoke-v1` over 27 train/validation rows. Florence repeated 2/2 samples but had macro precision 0.335, recall 0.533, F1 0.375, zero expected action/count/relation recall, 46 extra objects, 28 extra counts, and 81 extra relations. Its validation same median Jaccard (0.308) was below its near median (0.600). Controlled text F1 was 0.638 but retained train-lexicon OOV and weak relation/action coverage. SigLIP and MiniLM repeated exactly and distinguished unrelated pairs, but near-gap intervals crossed zero.

**Selected option:** Controlled text parser v1 is the primary extractor hypothesis because it is deterministic, transparent, schema-native, and compatible with a structured private-threshold path. SigLIP and MiniLM remain mandatory dense baselines. Florence raw outputs remain versioned as a negative result; the image path has no structured primary.

**Rejected alternatives:** Florence is rejected for `QF-COVERAGE`, `QF-MISSING-ATOM`, and `QF-HALLUCINATION`. SmolVLM remains rejected from P4. Adding another VLM before Gate A is rejected because no distinct role justifies the compute. The controlled parser is not declared reliable; training-only vocabulary prevents validation/test leakage but creates `QF-TRAIN-LEXICON-OOV`.

**Reason:** Determinism alone is insufficient when a backend repeats missing or hallucinated semantics. The direct-text path offers the clearest interpretable hypothesis for one bounded P6 test, while dense baselines preserve a check against parser limitations.

**Security/privacy assumptions:** Extraction remains local. Raw atoms and embeddings are not private and are directly readable/linkable without a protocol. No cloud fallback is allowed. Florence remote code was pinned/hashed, run unedited with eager attention and cache disabled, and is not needed for the primary path.

**Affected RQs/threats/claims:** RQ1/RQ2/RQ4/RQ5/RQ6; E1–E6/E10/E14/E16; D2/D3/D5; Gate A remains closed.

**Experiments supporting decision:** P5 two-task Florence outputs on all 27 rows, two Florence repeat samples, two full SigLIP/MiniLM embedding passes, deterministic parser execution, atom-level comparison, and family bootstrap diagnostics.

**Remaining uncertainty:** Pilot-scale OOV/fidelity, morphology/alias robustness, prompt paraphrase variation, near-neighbour discrimination, natural/generated image drift, dense inversion, and whether any image representation helps after controlling information.

**Revisit trigger:** A preregistered P6 pilot shows the parser cannot support a viable operating region; P7 supplies evidence that an image-specific structured extractor is necessary; or a new family has a distinct role and passes the identical frozen screen.

## P5-02 / D3 — Freeze canonical semantics v1 and choose weighted structured text as a conditional primary

**Decision:** Freeze `canonical-semantics-v1` and training-only `oracle-train-idf-v1`. Advance controlled weighted direct-text semantics as the primary P6 representation hypothesis, with unweighted structured text, MiniLM, and SigLIP as baselines. Do not claim positive separation or pass Gate A.

**Date:** 2026-08-24

**Status:** Selected conditionally; negative uncertainty outcome.

**Question:** Which representation/canonicalisation should P6 test for a non-degenerate operating region and plausible private evaluation?

**Candidates:** unweighted structured set; training-IDF weighted structured set; Florence-derived structured variants; SigLIP image embedding; MiniLM text embedding; oracle diagnostics; or no viable representation.

**Evaluation criteria:** Deterministic/versioned canonicalisation; same/near/unrelated diagnostic scores and family uncertainty; atom fidelity; interpretability; training-only weight provenance; storage/runtime; inversion/linkability surface; migration behavior; and private-matching compatibility.

**Evidence:** Controlled weighted text medians were 1.00 same, 0.80 near, and 0.00 unrelated, with same-minus-near bootstrap 95% interval `[-0.0166, 0.3917]`. Unweighted same/near medians were both 0.67. MiniLM medians were 0.935/0.922/0.104 and SigLIP 0.935/0.916/0.588; both near intervals crossed zero. Only oracle diagnostics had intervals strictly above zero. All raw families were trivially candidate-retrievable/linkable in cheap probes.

**Selected option:** Weighted structured direct-text semantics is the conditional primary because it gives the largest interpretable real near-neighbour median gap and has a plausible structured private-threshold path. Its weights are smoothed IDF fitted only to six training-family enrolment oracle documents. The unweighted set provides interpretability sensitivity; MiniLM and SigLIP remain dense baselines.

**Rejected alternatives:** Oracle sets are diagnostics, not extractors. Florence structured variants inherit extractor failure. Dense vectors are not selected as primary because their near gaps are smaller, raw vectors are linkable/candidate-retrievable, and private approximate dot product is more complex. No-representation/stop is not final because smoke uncertainty permits one properly sized pilot, but it remains a valid Gate A outcome.

**Reason:** The phase acceptance permits an evidenced failure. P5 establishes deterministic machinery and a falsifiable ranking of hypotheses, but does not provide sufficient uncertainty evidence for viability. Selecting a conditional primary keeps P6 bounded and prevents post-pilot representation switching.

**Security/privacy assumptions:** Raw structured atoms disclose semantics; raw embeddings are not private. PSI/PSI-cardinality/private weighted threshold and MPC/HE cosine are compatibility hypotheses only. Plaintext storage is rejected. Version mismatch fails closed and migration remains unresolved.

**Affected RQs/threats/claims:** RQ1/RQ2/RQ4/RQ6; A1/A3/A5/A7/A8; E1–E6/E10/E14/E16; D3/D4; Gate A.

**Experiments supporting decision:** `p5-smoke-v1`, 27 diagnostic pairs, 2,000 fixed-seed family bootstraps, split/changed-atom sensitivity, atom metrics, repeatability, resource/storage accounting, and cheap leakage probes.

**Remaining uncertainty:** Pilot sample size/catalog, stability under seed/style/layout, test performance, threshold/FAR/FRR/EER, acceptance-region mass, empirical weights, general inversion/linkability, private-protocol cost, model drift, and migration/re-enrolment.

**Revisit trigger:** P6 preregistered pilot/negative confirmation. A canonical rule change creates v2; a weight-source change creates a new weights version. Gate A cannot pass on P5 smoke evidence.

## P6-00 / D4 — Select no authentication matcher; Gate A fails and protocol engineering stops

**Decision:** Select no plaintext matcher for an authentication pipeline under the present evidence. Record Gate A outcome `stop-or-reframe`. Preserve weighted overlap as the least-complex conditional private-computation mapping for documentation only; forbid P9/P10 protocol engineering unless an explicit scientific reframe authorises a distinct objective.

**Date:** 2026-08-24

**Status:** Gate A failed; negative pilot result frozen.

**Question:** Does any P5 finalist provide a threshold operating region that simultaneously meets preregistered technical-reliability, targeted-neighbour, random-impostor, uncertainty, completeness, and plausible-private-computation bounds?

**Candidates:** controlled-text cardinality; controlled-text Jaccard; frozen-IDF weighted enrolled overlap; MiniLM cosine; revive a rejected structured-image extractor; choose no matcher; or perform one justified pilot revision.

**Evaluation criteria:** Training-only threshold selection; unchanged validation evaluation; FRR, targeted-neighbour FAR, random FAR, EER, all-negative and near-only AUC, family-cluster uncertainty, same-minus-neighbour gap, non-empty rate, controlled acceptance-region mass, deterministic score export, test sealing, and plausible private computation. All primary bounds were frozen in `p6_pilot_v1.json` before successful model output or score calculation.

**Evidence:** `p6-pilot-v1` used 36 training and 12 validation families from the audited 60-family catalog; 12 test families remained unevaluated. Weighted overlap selected threshold 0.84007072 on training. Validation FRR was 0.208 (95% family-bootstrap `[0.000, 0.458]`), targeted-neighbour FAR 0.750 (`[0.500, 1.000]`), random FAR 0.030 (`[0.008, 0.053]`), all-negative AUC 0.869 (`[0.747, 0.956]`), near-only AUC 0.517 (`[0.500, 0.557]`), and same-minus-neighbour gap 0.021 (`[0.000, 0.063]`). Validation non-empty rate was 0.75. Cardinality, Jaccard, and MiniLM also failed targeted-neighbour separation.

**Selected option:** Choose no authentication matcher and freeze the negative result. Weighted overlap remains only a conditional mapping to private weighted intersection plus threshold comparison; it is not selected for implementation. Existing matrices and curves remain reusable measurement artifacts.

**Rejected alternatives:** Cardinality rejected all validation positives at its training threshold. Jaccard accepted 75% of validation neighbours. MiniLM had FRR 0.625, near FAR 0.583, and negative same-minus-near gap. A parser revision after viewing validation is rejected as post-hoc and would not repair the broad near-only failure. Reviving Florence is rejected by P5. Increasing sample size cannot repair a point estimate showing 75% targeted-neighbour acceptance.

**Reason:** Random negatives were easy, but the security-relevant one-atom neighbours overlapped positives across matcher families. An all-negative AUC dominated by random pairs would conceal this failure. Privacy-preserving computation can reduce representation exposure but cannot create plaintext discriminative information that is absent.

**Security/privacy assumptions:** Raw atoms and embeddings remain readable/linkable and were used only as local plaintext baselines. No cryptographic construction was executed or benchmarked. Controlled attack mixtures and finite dictionaries are not population priors. No participant, public prompt, test-family, or real credential data was used.

**Affected RQs/threats/claims:** RQ1–RQ4/RQ6; A1/A4/A5/A8; E1–E8; D4; Gate A. The current standalone/second-factor authentication hypothesis is unsupported under the frozen representation. P9/P10 are blocked; P7 may only decide whether the cached image stage supports a bounded measurement/reframing contribution.

**Experiments supporting decision:** Deterministic 192×192 cardinality, Jaccard, weighted-overlap, and MiniLM matrices; 1,536 scored pilot pairs; exact two-pass MiniLM embeddings; training-selected thresholds; 4,000 fixed-seed family-cluster bootstraps; subgroup/missingness analysis; threshold/acceptance-region sweep; partial-information finite-dictionary probe; and byte-identical analysis rerun.

**Remaining uncertainty:** General-vocabulary extractors, a scientifically distinct semantic representation, image-path paired behavior, generator/extractor drift, real attacker priors, public-prompt frequency, full held-out performance, population guessing, and private-protocol costs. These uncertainties do not convert the failed P6 candidate into a Gate A survivor.

**Revisit trigger:** An explicit project reframe with a new representation rationale, independent vocabulary source, new version, new preregistration, and new data; or a P7 bounded paired diagnostic demonstrating a distinct measurement contribution. `p6-pilot-v1` itself can never be reclassified as a pass.

## P6-R — Amend Gate A interpretation; preserve the P6 result

**Decision:** Preserve every P6 artifact and numeric result, but correct the security interpretation. P6 measured conditional acceptance for candidates already drawn from frozen same, random, near-neighbour, and finite-dictionary conditions. It did not measure `P(success within B attempts | K_i)`. Gate A is now recorded as **conditional failure / unresolved security viability**: not a pass, not a conclusive impossibility result. P9/P10 remain blocked until a constructive Gate A2 after P8.

**Date:** 2026-08-25

**Status:** Interpretive amendment frozen; no P6 rerun, tuning, threshold change, artifact change, or held-out test access.

**Question:** What conclusion is licensed by P6's high targeted-neighbour acceptance when the experiment conditioned on a near neighbour already having been constructed?

**Candidates:** retain the original conclusive `stop-or-reframe` interpretation; reinterpret P6 as a pass because random FAR is low; or separate conditional boundary failure from budgeted attack success and defer the integrated positioning decision to Gate A2.

**Evaluation criteria:** Preserve preregistration integrity; distinguish `P(accept | already near)` from `P(success within B attempts | K_i)`; keep failed conditional quality checks visible; avoid model-security-by-obscurity; avoid requiring K3 FAR=0; and do not authorise protocol engineering without integrated attack evidence.

**Evidence:** The unchanged P6 weighted-overlap result has FRR 0.208, conditional targeted-neighbour acceptance 0.750, random FAR 0.030, and near-only AUC 0.517. P6 evaluated no ordered attacker strategy, discovery process, guesses-to-success, or success@budget. Its finite candidate dictionaries were explicitly not population priors.

**Selected option:** Separate the estimands. Introduce K0 generic/random, K1 population/distribution, K2 partial-target, and K3 strong-near-secret knowledge. Treat P6 random negatives as incomplete K0-like evidence and frozen one-atom near negatives as K3-like conditional evidence. Require P8 budgeted attacks and Gate A2 integration before choosing standalone, second-factor, policy-constrained, negative/measurement, or stop positioning.

**Rejected alternatives:** Reclassifying P6 as a pass is rejected because its frozen reliability and targeted-separation checks failed. Treating 0.750 conditional near acceptance as direct practical attack success is rejected because candidate discovery and ordering were not measured. Requiring near/K3 FAR=0 is rejected as an absolute criterion unsupported by the intended tolerant semantics. Reopening P6 or viewing its held-out test families is rejected.

**Reason:** Conditional vulnerability and practical exploitability are different quantities. The former is adverse evidence about the acceptance boundary; the latter also depends on how an attacker reaches and orders candidates within a fixed budget and knowledge condition.

**Security/privacy assumptions:** Algorithms, model identities, canonicalisation, thresholds, and future protocol code are public. Online rate limits must be stated and measured but cannot rescue a trivially enumerable space. A trusted third party provides benefit only through explicit keys, protocol/rate-limit enforcement, and non-collusion/isolation assumptions.

**Affected RQs/threats/claims:** RQ1–RQ4; A1/A4/A5/A8; E1–E8/E12/E13; D4/D8; Gates A and A2. P7 is authorised only as a bounded image-stage diagnostic. P9/P10 remain blocked.

**Experiments supporting decision:** Interpretive audit of the immutable `p6-pilot-v1` aggregate report and its frozen estimands; no new experiment and no held-out test-family access.

**Remaining uncertainty:** Budgeted K0–K3 success, real candidate ordering, population priors, online/offline compromise views, and whether any operational positioning remains constructive.

**Revisit trigger:** Completed preregistered P8 attack suite and Gate A2 review. P6 itself remains immutable.

## P7-00 / D5 — Remove the image stage from the authentication core

**Decision:** Select Gate B outcome B. The prompt→image→representation path is removed from the authentication core and retained only as an optional perturbation/measurement baseline. Direct-text semantics is the sole pathway hypothesis entering P8. This is a decision about the tested P5/P7 pipelines, not a universal claim that every possible image extractor must fail.

**Date:** 2026-08-25

**Status:** Selected; `p7-cached-v1` complete and frozen.

**Question:** Does the existing image transformation provide a material non-human technical or privacy benefit over paired direct-text processing that justifies its compute, storage, failure modes, and added exposure?

**Candidates:** (A) retain image as core; (B) make image optional/reposition/remove it from the authentication core; (C) leave the decision unresolved because extraction is the bottleneck.

**Evaluation criteria:** Same cached concepts, roles, families, splits, and pair definitions; comparable matchers; non-empty rate; same/near/random separation; family-bootstrap paired effects; AUC; identical training-only threshold rule and validation evaluation; atom errors; changed-atom sensitivity; latency/memory/storage; privacy exposure; model drift availability; attribution confounds; no human claims; no requirement that K3 FAR equal zero.

**Evidence:** Across nine families, image-minus-text improvements in same-minus-near gap were -0.076 (95% CI `[-0.274, 0.091]`) for structured Jaccard, -0.022 (`[-0.189, 0.134]`) for weighted structured matching, and -0.005 (`[-0.056, 0.042]`) for dense cosine. Corresponding same-minus-random effects were -0.346, -0.275, and -0.468 with all upper interval bounds below zero. Every validation pathway had worst minimax error 0.667. Florence macro F1 was 0.375 versus 0.638 for controlled text, with zero action/count/relation recall. The image path added median 25.80-second generation, median 10.64-second Florence extraction, 11.88 MB of cached PNGs, and additional local semantic/model exposure.

**Selected option:** B. Remove image processing from the authentication core; preserve the cached image path as a scientific baseline and possible future measurement mechanism.

**Rejected alternatives:** A is rejected because no comparison met any complete frozen material-benefit case and costs/exposure increased. C is rejected because Florence's clear bottleneck does not erase the available evidence: structured pathways use comparable downstream rules and the distinct dense pathway independently shows no measured advantage. A new extractor is rejected in P7 because existing evidence is sufficient for the bounded disposition and a post-result model search would expand/tune the question.

**Reason:** The tested image transformation adds stochastic/model processing and exposure without uncertainty-supported near separation, random separation, validation error, atom fidelity, or privacy benefit. Keeping it central would be unsupported by the evidence.

**Security/privacy assumptions:** Images and representations stay local only in the strongest hypothetical architecture; raw artifacts are not private storage. Algorithms and models are public. No protocol or trusted-third-party privacy benefit was evaluated. P9/P10 remain blocked by Gate A2.

**Affected RQs/threats/claims:** RQ1–RQ3/RQ5/RQ6; A1/A4/A5/A8; E1–E8/E13/E14/E16; D5/D9; Gate B. The original image-essential title/thesis is no longer supported and must be reconsidered at Gate A2/D9.

**Experiments supporting decision:** `p7-cached-v1`; 27 paired P5 train/validation relationships; structured Jaccard and weighted-overlap pathway comparisons; dense cosine pathway comparison; 4,000 fixed-seed family bootstraps per effect; equivalent threshold rule; P5 atom/resource/determinism evidence; deterministic cache hash checks.

**Remaining uncertainty:** A future independently justified extractor, new model revisions/drift, larger/new data, budgeted K0–K3 attack success, and whether direct-text semantics supports any constructive Gate A2 positioning.

**Revisit trigger:** Only a new-version study with an independent extractor rationale, new data, preregistration, and gate. P7 cannot be retuned or relabelled as outcome A.

**Semantic-policy note:** Mandatory discriminative anchors plus tolerant secondary attributes are scientifically motivated as a future hypothesis by oracle/real and changed-atom gaps, but were neither implemented nor tuned. Testing requires a new scheme/version, independent rationale, new data, preregistration, and gate; exact prompt/set equality remains outside the design.

## P7-R2 — Research direction amendment after complete VSA review

**Decision:** Adopt reconstructable visual-semantic authentication v2 as the active constructive hypothesis. Preserve `visual-semantic-pipeline-v1` and every P0–P7 result as immutable historical evidence.

**Date:** 2026-08-25

**Status:** Selected by explicit user direction; documentation migration only. P8 and all v2 experiments remain unexecuted.

**Reason:** The original project description conflated prompt/text semantics with the intended remembered visual concept. The prompt is an interface for reconstructing that concept; neither the prompt nor generated pixels are the credential. P7 validly rejected the tested v1 SD-Turbo/Florence/SigLIP image pathways, but it did not test a pipeline designed around independent visual reconstruction, a security-capable typed scene representation, system-derived mandatory/tolerant policy, and private verification.

**Evidence:** Immutable P6 and P7 results; the complete 16-page 2026 VSA paper; `docs/vsa_2026_comparison.md`; `docs/novelty_matrix_v2.csv`. No model, dataset, held-out v1 family, cryptographic implementation, or new experiment was used.

**VSA overlap:** VSA already enrols a reference image; uses arbitrary policy-satisfying images plus a password at authentication; extracts objects, attributes, quantities, visibility, and 2×2 quadrant location; serialises canonical semantic tokens; lets users select two or three facts and quantity operators; evaluates Flexible Range Logic conjunctions; and creates SHA-256 semantic/password bindings while retaining operator/quantity metadata. It calls this server-opaque rather than strict zero knowledge, acknowledges offline guessing from the small semantic space, recommends Argon2id with a user-specific salt, evaluates mainly COCO FAR/FRR without independent positive re-inference or a human study, and leaves Semantic Relationship Logic as future work. These features are not project novelty.

**Remaining candidate novelty:** C1, technical stability of independent generative visual reconstruction; C2, typed graphs with a frozen system-derived mandatory/tolerant policy as part of the combined system; C3, full acceptance-region security under budgeted K0–K3 and AI/adaptive attackers; C4, construction-specific private, policy-hiding, offline-resistant-under-declared-views, domain-separated and unlinkable verification. C5 adaptive semantic verification-oracle leakage remains optional pending a distinct novelty/evidence finding.

**Scientific rule:** v2 is not a retune or relabelling. It requires new representation and policy versions, new data/splits, independent screening criteria, new preregistration, and Gates V2-N through V2-F. P7 data may motivate questions but may not tune v2 policy. The twelve sealed P6 test families remain untouched. A failed earlier gate cannot be bypassed by later implementation cost.

**Affected RQs/threats/claims:** Replaces the active RQs with v2 RQ1–RQ6 and the threat/claim model in `docs/security_model_v2.md`; supersedes the old constructive path after P7 without changing any v1 evidence. Removes novelty claims for semantic/image-independent/VLM/policy/canonical-token/flexible-range authentication and forbids privacy-by-hash reasoning.

**Next permitted action:** Execute P8 only after explicit user instruction. P8 is literature, formalisation, and preregistration; it may not run the expensive v2 experiment.

**Revisit trigger:** Gate V2-N finds the C1–C4 combination substantially subsumed, or a later preregistered gate requires a narrower positioning. Any revision must append a new decision rather than rewrite this record.

## P8-00 — Gate V2-N passes with narrowed claims and frozen P9–P11 design

**Decision:** Pass Gate V2-N with mandatory narrowing. Authorise P9 only under the frozen v2 formal specification and preregistration. C5 is folded into C3/C4 and is not a standalone contribution.

**Date:** 2026-08-25

**Status:** P8 complete and frozen; no v2 model, dataset, generation, inference, authentication experiment, cryptographic implementation, or sealed-v1 access occurred.

**Question:** After verified broader prior art is included, does a defensible combined v2 research gap remain, and can the technical design be frozen before expensive outputs?

**Candidates:** stop because individual mechanisms are prior art; proceed with the broad original C1–C5 language; or proceed only with a narrowed combined empirical/systems question and preregistered stop rules.

**Evaluation criteria:** Primary/authoritative-source traceability across every P8 literature family; no unsupported first/primitive claims; an exact typed graph and plaintext decision; new split isolation; few fixed model candidates; no outcome-driven search; fixed baselines, attacks, budgets, uncertainty, thresholds, cache/version rules, and gates; no expensive P8 execution.

**Evidence:** The focused review added PassStyles and Omokage for generative graphical authentication; fuzzy aPAKE; foundational, fuzzy, circuit, committed and input-consistent private matching; private fuzzy-record and graph computation; and biometric hill-climbing/oracle attacks. VSA remains the closest semantic-policy baseline. `docs/p8_novelty_review_v2.md` records the comparison; `docs/related_work.csv`, `paper/references.bib`, and `docs/novelty_matrix_v2.csv` provide traceability and claim dispositions.

**Selected option:** Proceed with narrowing. C1 concerns only the technical behavior of free-language reconstruction through independent local text-to-image generation and fresh typed extraction. C2 is an incremental systems-component ablation, not standalone novelty. C3 is a system-specific finite-budget acceptance-region characterization. C4 is a construction-specific composition/privacy evaluation, never primitive novelty. Adaptive Accept/Reject leakage remains mandatory under C3/C4 but C5 is rejected as standalone.

**Frozen design:** `semantic-graph-v2.0.0`, `semantic-policy-v2.0.0`, and `accept-ref-v2.0.0`; a closed 24-entity typed vocabulary; exact graph canonicalisation/correspondence; deterministic training-only mandatory-anchor derivation; weighted-F1 tolerant predicate; dense/global/VSA/proposed baselines; 72 new cluster-split concept families plus a separate 96-image capability set; independent six-image generation roles; two extractor candidates and at most two generator slots; family-cluster uncertainty; online budgets 1/5/10/20 and offline plaintext budgets 1/10/100/1000/10000; K0–K3 and fixed AI/adaptive strategies; numeric Gates V2-A/V2-B/V2-C; immutable content-addressed caches. Full details are in `docs/formal_specification_v2.md` and `experiments/v2/config/preregistration_v2.json`.

**Rejected alternatives:** Stopping solely because components are known is rejected because the focused verified corpus did not contain the complete scoped composition and its proposed empirical questions. Broad C1–C5 language is rejected because generative authentication, semantic policies, private fuzzy matching, input consistency, AI guessing, and adaptive verifier attacks are established. Treating the focused search as proof of global firstness is rejected. Selecting or replacing models after authentication outcomes is rejected.

**Reason:** A useful research gap can be a carefully evaluated composition and measurement question even when every component is known, but only if the contribution wording and gates make that boundary explicit. The cheapest remaining falsifier is now P9: determine whether the required image-derived typed representation works at all.

**Security/privacy assumptions:** Algorithms, schemas, policy rules, thresholds, model identities and attack code are public. Pixels and prompts provide no entropy. No human-choice distribution is inferred. Cryptography cannot repair a cheaply reachable semantic acceptance region. Normal target leakage is a context-bound bit plus enumerated metadata, and all compromise claims remain construction-specific and unachieved.

**Affected RQs/threats/claims:** RQ1–RQ6; C1–C4 narrowed; C5 folded; A1–A8; V2-G1–V2-G10; Gates V2-N through V2-C. Gate V2-N authorises only P9. P10 requires V2-A, P11 requires V2-B, and protocol work remains blocked on V2-C.

**Experiments supporting decision:** None. P8 is literature, formalisation, and preregistration only. JSON/CSV/BibTeX/LaTeX and repository audits validate the artifacts, not the research hypotheses.

**Remaining uncertainty:** Whether either frozen extractor meets capability bounds; whether independent generations preserve graph facts; whether M/T beats VSA/global baselines; whether the accepted region survives K0–K3 budgets; whether any private construction preserves the predicate with acceptable leakage/cost; and whether later literature subsumes the remaining combination.

**Revisit trigger:** A new primary source substantially combining the remaining properties; Gate V2-A/B/C failure; or an outcome-independent design flaw discovered before the affected held-out output. Revisions require a new version and appended decision.

## P9-00 — Gate V2-A fails at extractor capability

**Decision:** Stop the frozen v2 constructive path at P9A. Neither preregistered extractor advances; do not execute P9B and do not begin P10.

**Date:** 2026-08-25

**Status:** P9 complete and frozen with a negative result; Gate V2-A failed.

**Question:** Can either frozen local extractor reliably produce the security-critical typed graph required before visual reconstruction and policy evaluation?

**Candidates:** advance a passing extractor to P9B; replace/repair/tune candidates after observing outputs; or preserve a negative result and stop the frozen path.

**Evaluation criteria:** Frozen 96-image capability manifest with 32 validation fixtures; schema validity at least 0.98; failure at most 0.05; the preregistered F1, bootstrap, determinism, latency, and memory checks; all checks conjunctive; no authentication-outcome selection or replacement search.

**Evidence:** On formal validation fixture `cap-v2-064`, Moondream2 revision `9a7d4024050840e001defacec2b00727e89149e6` emitted no JSON in 157.57 seconds at 4.58 GiB peak RSS. SmolVLM2-2.2B-Instruct revision `c0a7af506d0f71a771f24216ade491dec52ff6c5` emitted malformed/truncated JSON in 392.10 seconds at 5.62 GiB. One invalid validation result fixes the best possible completed validity at `31/32 = 0.96875`, below 0.98, even if every unobserved item passed.

**Selected option:** Preserve the negative result and stop. P9B is inapplicable because it is restricted to P9A survivors. Gate V2-A fails and P10 remains blocked.

**Rejected alternatives:** Candidate replacement, prompt/output repair, longer decoding, fine-tuning, and outcome-driven model search are rejected by the frozen design. Running the remaining expensive fixtures after pass became mathematically impossible is rejected as unnecessary; the post-smoke logical-futility deviation is explicitly recorded and cannot create a pass.

**Reason:** A private protocol or policy layer cannot repair an image-derived representation that fails its independent structured-output capability prerequisite. Continuing to P9B or P10 would bypass the gate rather than answer it.

**Security/privacy assumptions:** Models, schemas, prompts, and decisions remain public; images and prompts provide no credential entropy. Model weights and generated images stay local and outside Git. No participant or sealed-v1 data was used.

**Affected RQs/threats/claims:** C1 lacks constructive support under the frozen extractor path; C2–C4 cannot be evaluated in this path. Gate V2-A fails; Gates V2-B/V2-C and P10 onward remain blocked. This is not universal extractor impossibility.

**Experiments supporting decision:** `p9a-capability-futility-v2`; separate excluded plumbing/development smoke; frozen capability and model-acquisition manifests; exact best-case gate calculations.

**Remaining uncertainty:** Full atom F1, determinism, error strata, and latency medians were not estimated; other independently justified future extractors or a non-visual research question may behave differently.

**Revisit trigger:** Only an explicit scientific reframe with a new representation/version, independent rationale, new preregistration, new data, and a new gate. P9 cannot be relabelled or tuned into a pass.

## P9-v3A-00 — Reframe extraction as modular observation plus deterministic compilation

**Decision:** Preserve P9-v2 as a failed immutable experiment and adopt a new v3 extraction architecture: `I=G(P,r)`, `O=Observe(I)`, `S=C(O)`, `(M,T)=Pi(S)`. Learned components emit bounded evidence and provenance; a deterministic compiler emits a canonical graph or typed failure. Freeze P9-v3B capability and future P9-v3C reconstruction gates without running either phase.

**Date:** 2026-08-25

**Status:** Selected and preregistered; architecture only. Gate V3-A1 has not been evaluated.

**Question:** Does P9-v2 justify stopping every visual-semantic path, or does it justify a new independently testable architecture that separates perception from exact credential construction?

**Candidates:** Stop the project; repair/rerun P9-v2; replace its VLMs within the same full-JSON architecture; or create a new modular observation/compiler version with new data, metrics, candidates, and gates.

**Evaluation criteria:** Faithfulness to the negative record; no outcome-driven repair; precise separation of semantic and serialization failure; deterministic graph invariants; per-type capability eligibility; controlled and naturalistic evidence; reproducible model/revision/licence/compute plan; bounded shortlist; explicit abstention/failure; no P10 or cryptographic work before reconstruction viability.

**Evidence:** P9-v2's formal observations show Moondream non-JSON and SmolVLM2 malformed/truncated JSON. One invalid validation output makes `31/32=0.96875<0.98`, so the frozen gate failed, but full semantic F1, determinism, error strata, and full latency were not estimated. Grounding DINO supplies language-conditioned open-set detections; SigLIP 2 supplies released contrastive encoders for closed-label image scoring; SGTR supplies end-to-end entity/predicate proposals and graph assembly. `docs/p9_v3_reframe.md`, `docs/formal_specification_v3.md`, and `experiments/v3/config/*.json` freeze the new design.

**Selected option:** Create v3. Freeze `L_visual-v3.0.0`; derive `L_cred` only from per-type P9-v3B evidence in both strata. Shortlist exactly `v3-gdino-siglip2` and `v3-sgtr-siglip2`. Require 320 exact compiler cases, 240 new capability images, family-level uncertainty, exact operational/resource rules, and no cross-pipeline union. Actions/interactions are independently gated, neither mandatory nor discarded.

**Rejected alternatives:** Repairing, extending decoding, or replacing candidates inside P9-v2 would violate its freeze. Treating its syntax failures as universal perception impossibility exceeds the evidence. Stopping is not selected yet because deterministic compilation removes the failed serialization responsibility while preserving a falsifiable independent capability gate. A broad model search is rejected.

**Reason:** The v2 model was asked to solve visual inference, schema construction, canonical identifiers, counts, references, and serialization in one generative response. Those are separable responsibilities. Moving invariants into deterministic code creates independently measurable perception estimands and prevents valid semantics from failing solely due to arbitrary JSON generation, without assuming the perception problem will pass.

**Security/privacy assumptions:** This phase adds no security or privacy result. Observation, graph, prompt, and image remain sensitive client-side data. Confidence is component-local. Pixels/prompts provide no entropy. Compiler validity does not imply semantic correctness, discriminability, attack resistance, or template privacy.

**Affected RQs/threats/claims:** RQ1/RQ2/RQ6; C1/C2 remain conditional; C3/C4 remain blocked. P9-v3B evaluates V3-A1. P9-v3C and V3-A2 are future. P10 requires constructive V3-A2.

**Experiments supporting decision:** None. P9-v3A performed literature review, architecture/formalisation, preregistration, config tests, and manuscript/governance updates only. It acquired no model/image and ran no inference.

**Remaining uncertainty:** Whether checkpoint terms permit SGTR acquisition; whether either complete pipeline meets object/type/stratum thresholds; whether action or interaction types qualify; naturalistic annotation reliability; actual GPU cost; reconstruction stability; M/T value; acceptance-region security; and private-protocol feasibility.

**Revisit trigger:** A primary source invalidates a component rationale; a licence blocks a frozen pipeline; an outcome-independent design flaw is found before validation; Gate V3-A1 or V3-A2 fails; or new work subsumes C1–C4. Changes require an appended decision and new version, never a rewrite of P9-v2 or this record.

## P9-v3A.1-00 — Pre-execution pipeline and resource suitability audit

**Decision:** Freeze prospective v3.1.0 before any v3 output. Correct GPU-machine semantics, replace SGTR with EGTR as the only graph-native alternative to Grounding DINO + SigLIP2, predeclare support opportunities and primary gate types, and block image creation until two independent human annotators are confirmed.

**Date:** 2026-08-25

**Status:** Selected and preregistered prospectively. P9-v3B remains unexecuted and unauthorised.

**Question:** Does the v3.0.0 design contain outcome-independent resource, artifact, support, or annotation defects that should be corrected before any model/image output exists?

**Candidates:** Keep the v3.0 wording and SGTR; replace SGTR with EGTR; use newer ROBIN/Synthetic Visual Genome; weaken the support gate after data; or make a prospective versioned amendment with no empirical execution.

**Evaluation criteria:** Primary paper and official artifact availability; exact code revision and checkpoint identity; licence clarity; reproducible local inference; bounded tensor/graph output; relation vocabulary overlap; adaptation complexity; compute; naturalistic T2I suitability; support arithmetic over 60 validation images/12 families; annotation independence; no outcome-based model or hardware selection.

**Evidence:** SGTR CVPR 2022 and official repository commit `03bdd6554f12d521807cf95fe6a7daa7d3bb01dc`; EGTR CVPR 2024 and official repository commit `7f87450f32758ed8583948847a8186f2ee8b21e3`; ROBIN/Synthetic Visual Genome CVPR 2025 and official repository commit `29146b9d81333e0af039c617b22ccf618031c07c`; static review of released checkpoint links, licences, dependency files, evaluation commands, tensor interfaces, and the v3.0 semantic plan. No checkpoint or project image was acquired and no inference occurred.

**Selected option:** Create `semantic-secrets-preregistration-v3.1.0` and `visual-observation-v3.1.0`. Preserve Pipeline A as the compositional hypothesis. Select EGTR(VG) + SigLIP2 as Pipeline B. Preserve the measured 24 GiB VRAM/32 GiB RSS limits while allowing any documented dedicated GPU capacity. Guarantee support for entity, colour, count, binary interaction, and geometry relation; classify the remaining five types as exploratory and `not_gate_evaluable` under their frozen 30/30 support. Require two independent model-blind human annotators before image creation.

**Rejected alternatives:** SGTR is superseded because EGTR has a newer graph-native design, clearer single-GPU evaluation path, official released checkpoint, one Apache-2.0 repository licence, and directly adaptable object/relation/connectivity tensors; SGTR's thin older artifact and README/licence presentation conflict increase reproducibility risk. ROBIN is rejected because its autoregressive graph text/JSON and semantic label mapping reintroduce structured-generation risk and additional region-model complexity. Post-output support expansion, cross-pipeline union, model-assisted ground truth, a fabricated second annotator, and validation-driven hardware selection are forbidden.

**Reason:** Installed memory and measured allocation are different variables. The former should not exclude an A100; the latter remains a reproducibility and deployability gate. Likewise, 60 positive and 60 negative opportunities are feasible for a limited predeclared primary set but not for all ten types without artificial density. EGTR best preserves the intended learned-observation/deterministic-compiler boundary among the audited graph-native artifacts.

**Security/privacy assumptions:** No security, privacy, reconstruction, or authentication evidence is added. Model and label selection remain public and pre-output. Prompts, images, observations, and graphs remain local sensitive data. A larger GPU does not authorize more pipeline memory or a semantic-accuracy-driven environment change.

**Affected RQs/threats/claims:** RQ1/RQ2/RQ6 and Gate V3-A1 methodology only. C1-C4 remain conditional and unsupported. P9-v3C remains blocked on constructive V3-A1; P10 remains blocked on constructive V3-A2.

**Experiments supporting decision:** None. This was literature/artifact inspection, formal arithmetic, configuration, and document validation only.

**Remaining uncertainty:** EGTR checkpoint bytes/hash and extracted label metadata cannot be recorded until authorised acquisition; actual resource use and semantic accuracy are unmeasured; a second independent annotator is not yet guaranteed; primary-type feasibility still requires successful authored scenes under the frozen manifest.

**Revisit trigger:** Before output, official EGTR checkpoint/licence/artifact metadata fails closed or a documented implementation requirement proves incompatibility. After validation begins, no candidate, support, hardware-for-accuracy, or threshold change is permitted; a genuinely new question requires a new version and decision.

## NARRATIVE-01 — Reframe motivation around reconstructable semantic authentication

**Decision:** Make the transition from exact secret reproduction to approximate semantic reconstruction the primary project motivation. Present acceptance-region security and private verification as the central security/privacy problems. Treat the earlier password-memorability motivation as historical context rather than an active justification.

**Date:** 2026-08-26

**Status:** Selected research-direction and paper-positioning guidance; documentation only. This decision is not empirical evidence and authorises no experiment.

**Question:** What motivation accurately describes the technical evidence the controlled Semantic Secrets programme can produce without implying unmeasured human-memory or password-replacement benefits?

**Candidates:** Retain password memorability as the primary motivation; frame the project around reconstructable semantic authentication and its acceptance-region/privacy consequences; or stop describing a constructive authentication hypothesis.

**Evaluation criteria:** Alignment with the frozen C1–C4 and RQ1–RQ6 scope; fidelity to the no-human-study boundary; prominence of the complete accepted semantic region; separation of semantic correctness from cryptographic privacy; preservation of v3.1 architecture, gates, thresholds, data, candidates, and phase dependencies; accurate practicality and status statements.

**Evidence:** The active local research contract, `docs/research_direction_v2.md`, `docs/security_model_v2.md`, the frozen v2/v3/v3.1 formal specifications, P8 novelty record, immutable P9-v2 negative result, v3.0 reframe, and v3.1 pre-execution audit. This is a synthesis of existing scope and evidence boundaries; no new empirical observation was made.

**Selected option:** Reframe the active narrative around a reconstructable semantic authentication primitive. A natural-language prompt is the reconstruction interface; a generated image is a transient semantic reconstruction/normalisation medium; observations are probabilistic visual evidence; the canonical graph is the security-sensitive representation; and the complete fuzzy acceptance region is the operational secret surface. C1 tests technical reconstructability, C2 tests system-derived mandatory/tolerant semantics, C3 measures acceptance-region reachability under budgeted attackers, and C4 evaluates private and unlinkable verification.

**Rejected alternatives:** Password memorability is rejected as the primary justification because the project does not measure recall, memorability, usability, preference, accessibility, natural secret selection, or real-world authentication time. Universal password replacement is rejected as a presumed outcome because the evidence may instead support a factor, constrained/restricted setting, negative/measurement result, or stop. Removing the constructive hypothesis is not selected because its existing prospective gates remain well-defined and unexecuted.

**Reason:** Approximate reconstruction changes the security object from one exact enrolled value to a set of accepted semantic alternatives. A predicate that is too strict rejects legitimate independent reconstructions; one that is too tolerant expands attacker opportunity. Even a stable and discriminative predicate may expose semantic templates, policy structure, offline candidate-validation capability, adaptive leakage, or cross-domain linkage. These are the technical security/privacy questions that the current controlled design can actually test.

**Security/privacy assumptions:** Unchanged. Public algorithms, models, schemas, policies, thresholds, and attack code remain assumed. Prompts, images, observations, plaintext graphs, and raw embeddings remain local in the strongest target. Semantic correctness does not imply cryptographic privacy, and private computation cannot repair an easily guessed accepted region. Client-side practicality is measured rather than assumed; an untrusted cloud is not an authorised secret-processing fallback.

**Affected RQs/threats/claims:** C1–C4 remain scientifically unchanged. RQ1–RQ6 remain materially unchanged. C1/C2 remain enabling contributions; C3/C4 remain the strongest eventual security/privacy contributions if the constructive path survives. No novelty, security, privacy, memorability, usability, password-superiority, or deployment claim is added.

**Experiments supporting decision:** None. No model, dataset, threshold, gate, capability image, inference, private protocol, or sealed evidence was accessed or changed. No experiment is authorised by this record.

**Remaining uncertainty:** Every existing empirical uncertainty remains: v3.1 component capability and measured resources, independent reconstruction, policy value, acceptance-region reachability, private-construction leakage/cost, and viable deployment positioning. Human memorability/usability remain possible future human-subject questions outside the current evidence.

**Revisit trigger:** New empirical evidence or verified prior work materially changes the C1–C4 scope; a gate selects a narrower deployment/negative position; or a separately authorised human-subject programme changes the evidence boundary. Any change must append a new decision rather than rewrite this record.

**Frozen-material confirmation:** No model candidate, dataset, threshold, support opportunity, annotation requirement, gate, v3.1 architectural rule, or phase dependency changes. The binding order remains P9-v3B → V3-A1 → P9-v3C → V3-A2 → P10 and later gated phases.

## P9-v3B-PREP-01 — Prepare isolated, fail-closed GPU execution

**Decision:** Prepare deterministic compiler and RunPod execution software before paid GPU use while preserving the v3.0 + v3.1 freeze and keeping P9-v3B experimentally unstarted.

**Date:** 2026-08-26

**Status:** Selected engineering preparation; no experiment authorised or executed.

**Question:** How can formal P9-v3B later use paid GPU time mainly for permitted acquisition verification, smoke, and inference without resolving software or reproducibility problems interactively on a Pod?

**Candidates:** Build interactively during paid GPU time; combine modern and historical dependencies in one mutable Python environment; isolate EGTR and modern components behind the frozen bounded-observation schema; or change the frozen models to obtain an easier stack.

**Evaluation criteria:** Exact candidate/revision preservation; no weight/image/output access; deterministic compiler invariants; historical EGTR compatibility; local-only model loading; content/provenance hashing; per-component allocated/reserved GPU, RSS, and elapsed telemetry; resumability; explicit formal authorization; annotation/data/threshold/GPU guards; no learned final-graph authorship.

**Evidence:** Static review of the active v3.0/v3.1 configs and specifications; official exact-revision EGTR requirements/evaluation code; exact Hugging Face snapshot records; local deterministic tests; local Docker availability check. Docker CLI/Buildx existed but the Linux daemon was stopped, so no local image build occurred. No weight, capability image, or model output was accessed.

**Selected option:** Keep EGTR's official `nvcr.io/nvidia/pytorch:21.11-py3` base and historical dependency stack separate from a pinned modern Grounding DINO/SigLIP2/controller environment. Communicate by canonical bounded-observation subprocess records, then invoke the unchanged deterministic compiler. Before any model output, name the component-local `[0,1]` domains as Grounding DINO postprocessed score, SigLIP2 sigmoid logit, EGTR object softmax, relation sigmoid, and connectivity sigmoid; require the already-frozen SigLIP2 top-two-margin rule, but set no numeric threshold. Require external records binding the exact commit, configs, annotation resource, manifest, development threshold freeze, acquisition inventory, and GPU environment before formal validation. Provide a manual digest-addressed GHCR build path.

**Rejected alternatives:** Interactive environment construction wastes paid GPU time and weakens reproducibility. A combined mutable environment risks ABI/version contamination. Model substitution, quantization, resizing, changed preprocessing, mutable revisions, direct prompt authentication, cloud secret processing, and a third pipeline violate the freeze. Baking weights into the image is unnecessary and creates provenance/licence/storage risk.

**Reason:** The modern Transformers components and EGTR's Torch 1.12.1/Transformers 4.18.0 stack have incompatible dependency requirements, while the scientific interface is already a bounded observation record. Process isolation preserves the model/compiler responsibility boundary and permits deterministic caching and fail-closed acquisition checks.

**Security/privacy assumptions:** Unchanged. The future dedicated research Pod is experimental infrastructure, not the intended untrusted service architecture. Capability data and outputs remain controlled research data in persistent storage. No security, privacy, reconstruction, acceptance-region, or deployment result follows from preparation or compiler validity.

**Affected RQs/threats/claims:** RQ1/RQ2/RQ6 execution readiness only. C1–C4 and RQ1–RQ6 remain scientifically unchanged. Gate V3-A1 remains unevaluated; P9-v3C and all later phases remain blocked exactly as before.

**Experiments supporting decision:** None. The 320/320 deterministic local compiler cases, schema/config checks, and command guard checks are pre-execution engineering validation, not formal P9-v3B output or Gate evidence.

**Remaining uncertainty:** The human annotation resource remains unresolved. EGTR archive bytes, terms, hash, extracted vocabulary/config/checkpoint layout, and immutable base-model/feature-transform provenance require permitted acquisition-time verification and fail closed if ambiguous. The container must be built in GHCR or a running Linux Docker daemon and smoke-tested on the permitted GPU. Actual memory, time, and semantic capability are unmeasured.

**Revisit trigger:** A locked-image test fails; the official EGTR artifact cannot satisfy provenance/compatibility checks; an explicit authorization record permits formal execution; or a genuinely prospective amendment is required before any validation output. Never repair ambiguity by silently changing the frozen candidate.

**Frozen-material confirmation:** No v2/v3/v3.1 config, model, revision, resolution, preprocessing, label, threshold, dataset size, opportunity count, gate, compiler identity, or phase dependency changed. No P9-v3B/P9-v3C/P10 execution or cryptographic work occurred.

## P9-v3A.2-00 — Replace human annotation prerequisite with project-authored ground truth

**Decision:** Prospectively supersede only the v3.0/v3.1 two-human annotation method and resource blocker. P9-v3B is a technical capability experiment with no human participants or human annotators. Its reference semantics will be project-authored in a closed, versioned scenario schema, linked to deterministic support opportunities, audited, and SHA-256-frozen before any perception inference.

**Date:** 2026-08-28

**Status:** Selected and preregistered prospectively before any v3 capability image, model acquisition, inference, threshold output, or validation result. This is methodology/governance and engineering evidence only; it authorises no execution.

**Question:** How should P9-v3B obtain reproducible model-blind ground truth when its intended controlled technical methodology has no human-annotation study, but v3.0/v3.1 accidentally required two independent annotators?

**Candidates:** Retain the two-human blocker; silently remove the guard; derive labels from the evaluated models; use one unversioned free-form reference file; or add a prospective project-authored, schema-bound and hash-frozen ground-truth amendment.

**Evaluation criteria:** Preserve the controlled/naturalistic capability objective, exact v3.1 support opportunities and counts, IoU/entity scope, family/split isolation, model-blind separation, pre-inference freezing, fail-closed provenance, and every frozen pipeline/gate/resource parameter; add no participant or annotator dependency and create no empirical output.

**Evidence:** Repository audit of the v3.0 dataset text, v3.1 suitability amendment, pre-execution audit, RunPod guards, manifest/support templates, and tests. The human dependency originated as a conservative response to naturalistic visibility ambiguity in v3.0 and became an explicit v3.1 resource blocker when a second researcher was not guaranteed. RunPod preparation faithfully encoded that blocker, but it did not originate the scientific mismatch. No image, weight, prediction, or validation output was inspected.

**Selected option:** Add `semantic-secrets-preregistration-v3.2.0` and `formal_specification_v3_2.md` without rewriting v3.0/v3.1 history. Each final image receives a project-authored `capability-scenario-specification-v3.2.0` containing exact closed-label reference entities, normalized boxes, and semantic atoms. The existing positive/applicable-negative support-opportunity surface is retained and expanded only in provenance fields: each row deterministically binds its scenario, entity/pair scope, boxes, value, polarity, split, and ground-truth version. `ground-truth-freeze-v3.2.0` binds active config, manifest, opportunity, and aggregate scenario hashes and asserts that no model prediction was produced or accessed before freezing. Formal authorization binds that freeze record.

**Rejected alternatives:** Retaining human annotation conflicts with the intended non-human technical methodology. Removing the guard without a replacement weakens provenance. Model-assisted ground truth is circular and forbidden. An unversioned table cannot establish exact file, reference, or timing integrity. Rewriting v3.0/v3.1 would erase the historical reason the blocker existed.

**Reason:** The manifest and support-opportunity design already provides the correct dataset/split/count skeleton, but it lacked a complete non-human reference representation and formal provenance binding. Project-authored scenario records supply the missing exact reference entities/boxes/atoms; deterministic audits and the freeze record preserve model blindness and fail closed on any later change.

**Security/privacy assumptions:** Unchanged. Capability ground truth is controlled technical data, not a credential or human-subject record. Model outputs may never author or revise reference semantics. Ground-truth integrity does not establish authentication security, semantic privacy, or deployment feasibility.

**Affected RQs/threats/claims:** RQ1/RQ2/RQ6 execution methodology only. C1–C4, RQ1–RQ6, the scientific objective, and all claim boundaries remain materially unchanged. Gate V3-A1 remains unevaluated.

**Experiments supporting decision:** None. Local schema, deterministic data-audit, guard, configuration, and compiler tests are preparation checks, not P9-v3B evidence.

**Remaining uncertainty:** The 240 capability images, scenario specifications, manifest, opportunities, and ground-truth freeze must still be authored and audited. EGTR acquisition provenance, container/GPU smoke, thresholds, actual resources, and all model capability remain unmeasured. Naturalistic project-authored reference quality remains a dataset-construction limitation to report, not permission to use model predictions.

**Revisit trigger:** Before inference, the project-authored reference schema proves insufficient for a frozen metric or cannot express an intended support opportunity; the official model artifact fails acquisition; or an audit detects ambiguity. Any correction must be prospective and model-output blind. After inference, ground truth may not be changed in place.

**Frozen-material confirmation:** The exact two pipelines, models, revisions, preprocessing, input resolution, labels, threshold semantics, metrics, Gate V3-A1 criteria, hardware/resource limits, 240-image design, family/split structure, support-opportunity counts, compiler, and P9-v3B → V3-A1 → P9-v3C → V3-A2 → P10 dependency remain unchanged. No image was generated, no model was acquired or run, and no later phase or cryptographic implementation started.
