# Semantic Secrets execution plan

Status: P0–P1 complete; P2–P17 not started.
Authority: `AGENT.md` is the scientific and engineering contract. This plan operationalises it and may not silently weaken it.  
Scope: prospective PoPETs/PETS 2027 paper, prototype, experiments, and research artifact; no human-subject study.

## How to execute this plan

When asked to “Execute Pn” or “Continue with Pn”:

1. Read `AGENT.md`, this plan, the relevant decision records, and the phase inputs.
2. Confirm earlier dependencies and gates. Do not spend full-scale compute before the required gate passes.
3. State the RQ, threat, claim, or decision the work supports.
4. Perform only the numbered phase tasks, using the smallest useful dataset/configuration first.
5. Save configurations, provenance, raw observations, and negative results. Never substitute invented values or citations.
6. Run the listed validation and evaluate the acceptance criteria.
7. Update the phase status and persistent decision record; record a stop/reframe outcome as faithfully as a positive result.
8. Report changes, evidence, failed checks, unresolved uncertainty, and the next permitted phase. Do not commit or push unless explicitly requested.

Phase status values are `not started`, `in progress`, `blocked by gate`, `complete`, or `stopped/reframed`. A phase is complete only when its outputs, validation, and acceptance criteria are satisfied.

## Non-negotiable research controls

- Treat all current model, representation, matching, protocol, and architecture preferences as hypotheses.
- Do not claim memorability, usability, human preference, recall, natural secret-selection entropy, or human authentication speed.
- Model security over the whole acceptance region, not image pixels or exact semantic equality.
- Distinguish A1–A8 and state which data, keys, services, and transcripts each attacker obtains.
- Keep prompts, images, plaintext atoms, raw embeddings, and exact scores client-side in the strongest target architecture; document every deviation.
- Use mature maintained cryptographic libraries. Never invent or reimplement a standard primitive merely for convenience.
- Verify references against primary papers, standards, official specifications, publisher records, or trusted bibliographic indexes before adding them to `paper/references.bib`.
- Label preprints and peer-reviewed work distinctly. Preserve negative/null results and distinguish hypotheses, measured observations, inferences, and cited facts.
- Every paper number must trace to an immutable run and every paper figure/table to a deterministic generation script.
- Do not pass a gate by selecting a favourable subset, tuning on the test set, or defining the criterion after viewing full results.

## Evidence and budget policy

Use this escalation order for every unresolved choice:

```text
verified literature/standard/licence and analytical feasibility
→ tiny deterministic test
→ small paired pilot
→ eliminate weak candidates
→ minimal proof-of-concept for remaining uncertainty
→ full experiment only after its gate
```

Dataset scales are deliberately progressive:

- **Smoke:** 8–12 controlled concepts and a few fixed seeds; detects schema, runtime, and gross viability failures.
- **Pilot:** approximately 50–100 concepts with stratified near-neighbours; fixes methodology, preregisters metrics/gates, and supports candidate elimination. Exact size follows variance/power assessment.
- **Full:** sized from pilot uncertainty and planned comparisons, not an arbitrary round number. Frozen before final evaluation.

Expensive images and model outputs are content-addressed and generated once per frozen manifest. Downstream extractors, representations, similarity matrices, thresholds, attacks, and plots reuse them where scientifically valid. Smoke/pilot/full outputs must be separated. A change to model, prompt, seed, canonicalisation, or preprocessing creates a new version rather than overwriting evidence.

## Persistent decision records

Create `DECISIONS.md` in P1 and append one record per consequential decision. Revisit a closed decision only when new evidence invalidates a recorded assumption.

```text
Decision:
Date:
Status: proposed | selected | rejected | superseded
Question:
Candidates:
Evaluation criteria:
Evidence (citations, analysis, run IDs):
Selected option:
Rejected alternatives:
Reason:
Security/privacy assumptions:
Affected RQs/threats/claims:
Experiments supporting decision:
Remaining uncertainty:
Revisit trigger:
```

Experiment manifests and decision records are concise sources of truth; do not duplicate long summaries across files.

## Mandatory decision investigations

Each decision uses the evidence ladder above. No row preselects its first candidate.

| ID / phase | Candidates | Criteria and cheapest useful screen | Minimal experiment if still uncertain | Evidence and decision rule | Fallback |
|---|---|---|---|---|---|
| D1 generator, P4 | Locally deployable SDXL-class model; one newer/leaner open-weight alternative; no-image path for P7 | Reproducible pinned version/hash, licence and redistribution/acquisition terms, local hardware fit, deterministic seeds, quality sufficient to render controlled atoms, stable availability, latency/storage cost. First reject on licence, availability, determinism, or infeasible hardware; benchmark no more than 2–3 justified finalists on smoke concepts. | Paired smoke generations with identical concept/seed manifest; score atom renderability, failures, latency, memory, and reproducibility. | Record model cards/licences/hashes/configs and run IDs. Select one primary generator if it meets preregistered feasibility and semantic-coverage criteria; retain at most one scientifically useful drift/comparison model. | Reduce resolution/model size, use an acquisition script for weights, or stop/reposition the image path if no local model is reproducible and adequate. |
| D2 extractor, P4–P5 | Open-vocabulary detector + VLM encoder/geometry; constrained local multimodal VLM with fixed JSON; captioning/parsing pipeline if justified; dense embedding baseline | Objects, attributes, actions, counts, relations, schema validity, determinism, stability, separability, calibration, latency/memory, licensing, portability/versioning. Reject gross schema/coverage/runtime failures on a hand-auditable smoke set before pilot generation. | Run surviving families on the same cached smoke/pilot images and annotated semantic atoms; measure atom-level coverage/error, run-to-run determinism, failure rate, and downstream separation. | Keep the smallest set that represents materially different scientific approaches. Select primary only after P5 paired results and uncertainty intervals; dense embeddings remain a baseline even if not primary. | Narrow atom vocabulary, combine deterministic geometry with a model, or report extractor limitations/reframe if no structured approach is reliable. |
| D3 representation/canonicalisation, P5 | Structured set; weighted structured set; dense embedding; text-derived structured/embedding representation | Stability, negative/near-neighbour separation, interpretability, deterministic versioned canonicalisation, portability, leakage/inversion surface, private-matching compatibility, performance. Analytically reject representations incompatible with required semantics or realistic private evaluation; never reject embedding/text baselines merely because another is preferred. | Apply all surviving representations to the identical cached pilot outputs. Compare positive/negative score distributions, atom errors, drift, inversion/linkage probes, and compute/storage. | Freeze schema and canonicaliser version before P6. Select the primary representation only if its preregistered technical and privacy/protocol constraints pass; weighting must derive from frozen training/corpus statistics, not test labels or intuition. | Simplify vocabulary/relations, use unweighted sets, make embeddings primary if evidence warrants, or fail Gate A/reframe. |
| D4 plaintext matcher and threshold, P6 | Cardinality threshold; Jaccard; weighted overlap; cosine for embeddings | Discrimination, calibration, acceptance-region mass, stability across strata/models, private computability, threshold leakage and complexity. Reuse one similarity matrix and analytically exclude metrics that cannot support a credible selected protocol except as baselines. | Nested/frozen train-validation-test threshold sweep on pilot; random and targeted near-neighbours; bootstrap CIs and sensitivity analysis. | Predeclare operating-point selection and maximum tolerable security/reliability bounds before the held-out full test. Select jointly with representation and protocol constraints; report the full trade-off rather than one favourable threshold. | Change representation/canonicalisation and repeat the pilot once, require a second factor, or fail Gate A. |
| D5 image-stage necessity, P7 | Prompt→image→semantics; prompt→semantics; image as optional interface/augmentation | Paired technical stability, separability, acceptance-region mass/guessability, privacy exposure, model drift, latency/memory/storage. Human memorability/usability cannot be a criterion. | Same concepts/paraphrases/splits and downstream metrics in a paired ablation; control extractor capacity and avoid giving one path extra information without disclosure. | Retain the image stage as core only if preregistered paired evidence shows a meaningful technical/security benefit commensurate with added cost and failure modes. | Remove it, make it optional, treat it as a perturbation/measurement mechanism, or revise title/thesis. |
| D6 privacy protocol, P9–P10 | Structured OPRF/PSI/PSI-CA/private threshold variants; fuzzy recovery/secure sketch + OPAQUE/PAKE; embedding + MPC/HE similarity | Security assumptions/proof model, noisy correctness, offline verification, database and server/key compromise, helper leakage, transcript leakage, linkability/domain separation, Accept/Reject-only capability, maturity, novelty, dependency/implementation complexity, latency/bandwidth/storage, artifact reproducibility, 12-page explainability. Stage 1 literature/security matrix eliminates candidates that violate essential goals. | Implement only uncertain operations for genuinely competitive survivors: representative set/vector sizes, synthetic credentials, correctness vectors, leakage surface, and microbenchmarks. Do not build full systems. | P9 produces signed-off theoretical shortlist; P10 uses common benchmark conditions and selects one primary plus justified baseline(s). Selection requires a precise claim stronger than plaintext/hash binding under a stated compromise model and acceptable uncertainty/cost. | Weaken and label the claim, choose a simpler protocol, reposition as measurement/negative result, or stop PETS protocol framing. |
| D7 architecture/compromise assumptions, P9–P11 | Single server; separate privacy service with non-collusion; threshold keying; hardware/key isolation; another justified design | Concrete protection gained under A2/A3/A7 versus deployment/trust burden, collusion result, availability, key rotation/recovery, transcripts, rate-limiting, and operational realism. First construct a data/key/compromise matrix; reject components that add no measurable property. | Minimal failure/collusion/key-compromise tests for shortlisted protocol architectures. | Select the least-assumptive architecture that achieves the recorded privacy claim. Every trusted component and collusion boundary appears in protocol spec, code, experiments, and paper. | State weaker protection under full compromise, use operational isolation only as a clearly weaker variant, or fail Gate D. |
| D8 attack distributions, P3/P8 | Random; empirical frequency/public prompt corpus; LLM-ordered; generator/VLM-assisted; partial-information and adversarial search | Ethical/licence fit, relation to A1/A4/A5/A8, reproducibility, realistic capability without claiming real authentication-choice distribution. Reject sources that cannot be documented or lawfully used. | Pilot dictionary coverage and attack ordering on frozen synthetic accounts; compare against random/frequency controls. | Retain attacks that add a distinct capability or alter conclusions. Report success by budget and acceptance-region mass with limitations. | Use controlled synthetic distributions and bounds; narrow claims rather than treating public prompts as password choices. |
| D9 paper positioning, Gates B/D/E/F | Private authentication system; second-factor construction; measurement/limitations paper; image-stage optional or removed | Novelty versus verified 2026 VSA and related work, strength of privacy claim, semantic viability, attack results, deployment assumptions, page-budget coherence. | No separate experiment: use frozen evidence/claim matrix. | Choose the strongest story for which every contribution maps to evidence and limitations; never force the original title/thesis. | Reframe, narrow, or do not submit to PETS. |

## Phase plan

### P0 — Project/repository setup and contract validation

**Status:** Complete on 2026-08-24.

**Objective:** Establish a minimal, non-destructive research workspace and translate the contract into an executable plan without beginning research implementation.

**Supports:** All RQs, threats, experiments, reproducibility, and scientific integrity.

**Tasks:**

1. Inspect the full repository, Git state, environment/dependency files, manuscript sources, and rendered-draft metadata.
2. Read `AGENT.md` and `paper/draft.tex` completely; treat `AGENT.md` as authority.
3. Preserve the PoPETs template example (`paper/main.tex`, `sample-base.bib`, styles/assets) without treating it as research evidence.
4. Initialise local Git on `main` without commits; add only the minimal directories, README, verified-reference placeholder, artifact placeholder, and protective `.gitignore`.
5. Write and cross-check this plan. Do not install dependencies, download data/models, implement protocols, or run experiments.

**Inputs:** `AGENT.md`, `paper/draft.tex`, `paper/draft.pdf`, existing template files, user task.

**Outputs:** `PLAN.md`, `README.md`, `.gitignore`, `paper/references.bib`, `artifacts/README.md`, minimal directories, initialized uncommitted Git repository.

**Tests / validation:** File inventory; `git status --short --branch`; coverage matrices below; confirm no model/data/code/result additions.

**Acceptance criteria:** Contract and draft read; meaningful differences recorded; every mandatory decision/gate/RQ/threat/experiment/baseline mapped; only lightweight setup changes exist.

**Decision / gate:** None; authorisation is required before P1.

**Dependencies:** None.

**Cost:** AI-token Low–Medium; compute Low; storage Low.

**Stop / fallback:** If the contract conflicts internally, preserve files, record the conflict, and request direction instead of silently resolving it.

### P1 — PETS scope, novelty, and focused related-work validation

**Status:** Complete on 2026-08-24. Early novelty decision: continue to P2 only with the narrowed privacy/measurement boundary recorded in `DECISIONS.md`.

**Objective:** Verify whether the proposed contribution is novel and PETS-relevant before engineering investment.

**Supports:** RQ3–RQ6; privacy contribution; Background/Related Work, Introduction, and D9.

**Tasks:**

1. Verify current PoPETs/PETS 2027 scope, page/template/anonymisation/ethics/open-science/AI-use requirements from official sources and record access dates.
2. Identify and verify the asserted 2026 Image-Agnostic VSA work first; extract its representation, policy, binding, threat model, attacks, evaluation, and exact gap.
3. Search primary sources/standards narrowly across semantic/graphical authentication, fuzzy extractors/secure sketches, OPAQUE/PAKE, OPRF/VOPRF, PSI/private threshold matching, encrypted biometric/vector comparison, template inversion/linkability, DiffusionDB, and AI-assisted guessing.
4. Create a compact related-work matrix with: work, year/venue/status, problem, representation, matcher, privacy mechanism, threat model, offline-attack property, approximate matching, limitation, and relation to this project.
5. Create `DECISIONS.md`; record verified novelty risks and a provisional contribution boundary without final contribution claims.
6. Add only verified entries to `paper/references.bib`; label preprints.

**Inputs:** Contract/draft; official venue pages; primary papers, RFCs/specifications, publisher/bibliographic records.

**Outputs:** `docs/related_work.csv` (or equivalent compact machine-readable matrix), `docs/pets_requirements.md`, `DECISIONS.md`, verified `paper/references.bib` entries, novelty-risk record.

**Tests / validation:** Every matrix row has a resolvable authoritative source; every BibTeX entry matches that source; explicit VSA comparison exists; no generic uncited summary or fabricated reference.

**Acceptance criteria:** The closest work and plausible contribution gap are documented; official submission constraints are verified; no known prior work already subsumes all proposed novelty. Human-study claims remain excluded.

**Decision / gate:** Early novelty checkpoint. Continue to P2 if a defensible privacy/measurement gap remains; otherwise invoke D9 and reframe/stop before implementation.

**Dependencies:** P0.

**Cost:** AI-token Medium; compute Low; storage Low.

**Stop / fallback:** Narrow to an empirically testable limitation or protocol gap; if none is novel/PETS-relevant, stop the submission path and preserve the review.

### P2 — Threat model, privacy goals, and formal research definitions

**Objective:** Make claims and experiments falsifiable under precise adversaries and compromise states.

**Supports:** RQ1–RQ6; A1–A8; E7–E13/E15; System/Threat Model and Security Analysis.

**Tasks:**

1. Define credential space, semantic distance/similarity, threshold, acceptance region, attacker distribution, success budget, correctness, and technical stability.
2. Define security/privacy goals separately: online resistance, database-only offline verification, server/key compromise, representation leakage/inversion, transcript leakage, unlinkability, replay/session security, and availability boundaries.
3. Create actor/data-flow and data-key-compromise matrices for single-, two-server-, threshold-, and isolation hypotheses; distinguish honest-but-curious/malicious behaviour where relevant.
4. Map A1–A8 to attacker knowledge, oracle access, keys/services compromised, observable outputs, metric, and experiment/proof.
5. Refine RQ wording and contribution hypotheses only where verified P1 evidence requires it; update `AGENT.md` only with explicit user approval, otherwise record proposed amendments.
6. Define no-human-study inference limits and ethical boundaries for public prompts and attack generation.

**Inputs:** P1 matrices/requirements; `AGENT.md`; `paper/draft.tex`.

**Outputs:** `docs/security_model.md`, machine-readable threat/claim matrix, proposed paper definitions/notation, decision records.

**Tests / validation:** Walk each architecture through A1–A8; each privacy adjective maps to a definition and evidence plan; full compromise/collusion outcomes are explicit; Accept/Reject versus score/intersection leakage is classified.

**Acceptance criteria:** No central claim lacks an attacker, protected asset, compromise boundary, success condition, and evaluation/proof method; assumptions are internally consistent and reviewer-auditable.

**Decision / gate:** Freeze threat-model version v1 for pilot design; architecture remains unselected until D7.

**Dependencies:** P1.

**Cost:** AI-token Medium; compute Low; storage Low.

**Stop / fallback:** If no plausible architecture offers a meaningful benefit under a realistic attacker, reframe to a limitation/measurement question before P3.

### P3 — Dataset and controlled semantic-concept methodology

**Objective:** Build a reproducible, ethically suitable input methodology that separates technical behaviour from human claims.

**Supports:** RQ1–RQ3/RQ6; A1/A4/A5/A8; E1–E8/E12–E14/E16.

**Tasks:**

1. Specify a controlled concept ontology and factorial design for objects, frequency bands, attributes, counts, actions, spatial relations, scenes, complexity, and targeted near-neighbours.
2. Define positive transformations: seeds, controlled paraphrases, styles, layout/orientation, and model versions; define one-atom negative perturbations and unrelated negatives without label leakage.
3. Define smoke, pilot, and full manifests, account/concept grouping, train/validation/test partitioning, and power/uncertainty plan. Keep all variants of a base concept in one split.
4. Screen public prompt sources under D8 for licence, ethics, content filtering, identifiers, and distribution limitations; design acquisition/preprocessing scripts rather than downloading the full corpus now.
5. Define schema, provenance, hashes, deduplication, harmful-content policy, annotation procedure, quality checks, and frozen versioning.
6. Predefine which generated images/representations may be cached and released; estimate storage and compute before acquisition.

**Inputs:** P2 definitions; verified dataset documentation from P1; extractor/generator requirements.

**Outputs:** `experiments/datasets/README.md`, ontology/schema, smoke/pilot/full manifest specifications, split generator, data statement/ethics note, acquisition plan, power/uncertainty rationale.

**Tests / validation:** Schema validation; deterministic manifest/split recreation from seeds; no cross-split concept-family leakage; hand audit of smoke concepts/near-neighbours; licence/source fields complete.

**Acceptance criteria:** The design covers each semantic atom type and difficulty stratum; supports all mapped experiments; states non-human limitations; full scale is justified by uncertainty rather than convenience.

**Decision / gate:** Approve the smoke/pilot methodology; full data acquisition remains forbidden until P6/P7 needs it.

**Dependencies:** P2.

**Cost:** AI-token Medium; compute Low; storage Low.

**Stop / fallback:** Narrow the ontology or use synthetic controlled distributions if public data is unsuitable; narrow attacker-distribution claims accordingly.

### P4 — AI/model candidate screening and selection

**Objective:** Select reproducible, locally feasible generator/extractor candidates with the cheapest discriminating evidence.

**Supports:** RQ1/RQ5/RQ6; E1–E4/E14/E16; D1/D2.

**Tasks:**

1. Inventory target hardware/software and define backend interfaces without installing large models.
2. Verify model licences, exact versions/hashes, deterministic controls, acquisition stability, supported hardware, and expected resources.
3. Limit generator finalists to one primary candidate plus at most one justified alternative; keep the no-image path for P7.
4. Screen the distinct extractor families in D2 using smoke fixtures and a fixed structured schema; include dense embeddings and text-derived semantics as mandatory baselines.
5. Record generation/extraction latency, peak memory, deterministic repeatability, schema failure, semantic coverage, and qualitative failure codes—not publication results.
6. Select candidates for P5 and freeze backend/config versioning; do not run the full corpus.

**Inputs:** P3 smoke manifest; verified model documentation/licences; hardware inventory.

**Outputs:** `docs/model_screening.md`, model manifest, backend interface/config skeletons, smoke outputs/run metadata, D1/D2 records.

**Tests / validation:** Repeated fixed-seed/fixed-input runs; schema validation; dependency/model hashes captured; clean acquisition instructions; smoke config completes on documented hardware.

**Acceptance criteria:** At least one feasible path for each mandatory baseline and one structured extractor survives, or its exact infeasibility is evidenced; selected finalists are few and scientifically distinct.

**Decision / gate:** D1 provisional primary generator; D2 extractor shortlist. Primary extractor waits for P5.

**Dependencies:** P3.

**Cost:** AI-token Medium; compute Medium; storage Low–Medium.

**Stop / fallback:** Use a smaller local model/narrower schema, or stop/reposition the affected image/structured path rather than moving to an undisclosed cloud dependency.

### P5 — Semantic representation and canonicalisation comparison

**Objective:** Determine which representation/canonicalisation offers the best stability, separability, interpretability, privacy compatibility, portability, and cost.

**Supports:** RQ1/RQ2/RQ4/RQ6; E1–E6/E10/E14/E16; D2/D3.

**Tasks:**

1. Implement versioned schema validation and deterministic canonicalisation rules for Unicode/case, number, singular/plural, synonyms/aliases, colours/attributes, counts, relation direction, confidence, duplicates, ordering, and unsupported output.
2. Implement structured set, weighted structured set (weights learned only from training/corpus statistics), dense embedding, and text-derived baseline representations behind common interfaces.
3. Run all representations on the same cached pilot inputs; measure determinism, atom-level errors, positive stability, random/near-neighbour separation, model drift, storage/latency, and missing-output behaviour.
4. Run cheap inversion/linkability probes and analyse private-matching compatibility before selecting a primary representation.
5. Freeze schema/canonicaliser/model versions and log every rule; maintain migration/version-mismatch behaviour as an open requirement.
6. Record D2/D3 outcomes; retain meaningful embedding and text-only baselines regardless of primary choice.

**Inputs:** P3 pilot manifest; P4 cached model outputs and shortlist; P2 privacy requirements.

**Outputs:** semantic modules, canonicalisation specification, versioned schemas/configs, unit tests, pilot comparison tables/plots, D2/D3 records.

**Tests / validation:** Golden vectors; property tests for idempotence/order invariance; malformed/low-confidence handling; repeat-run determinism; no test-set-derived weights; paired CIs/sensitivity by semantic stratum.

**Acceptance criteria:** Every canonicalisation rule is deterministic/versioned; at least one representation reaches P6 with non-degenerate positive/negative score separation and a credible private-evaluation path, or failure is documented.

**Decision / gate:** Select representation/canonicalisation finalists and primary extractor hypothesis. Gate A is not passed until P6 matching results.

**Dependencies:** P4.

**Cost:** AI-token Medium–High; compute Medium; storage Medium.

**Stop / fallback:** Simplify atoms/canonicalisation, use embeddings if justified, or prepare a Gate A negative result rather than hiding unstable dimensions.

### P6 — Plaintext matching, thresholds, and acceptance-region analysis

**Objective:** Demonstrate useful technical separation and quantify the tolerance–guessability trade-off before cryptography.

**Supports:** RQ1–RQ3; A1/A4/A5/A8; E1–E8; D4; Gate A.

**Tasks:**

1. Implement cardinality, Jaccard, weighted overlap, and embedding cosine matchers with deterministic score export.
2. Generate one reusable pilot similarity/overlap matrix covering positives, random negatives, near-neighbours, and controlled perturbations.
3. Predeclare threshold-selection rule and minimum viability bounds using pilot variance and intended use; use grouped/nested splits and reserve held-out test data.
4. Sweep thresholds and report FAR, FRR, EER, ROC/AUC, stability, subgroup/model sensitivity, uncertainty intervals, and calibration where meaningful.
5. Estimate acceptance-region size/probability under controlled and provisional empirical distributions; show security–reliability curves rather than only an optimum.
6. Evaluate private-computability/expected leakage/cost of each competitive matcher and record D4.

**Inputs:** P5 frozen representations; P3 splits; P2 definitions.

**Outputs:** matcher modules/tests, immutable pilot run, reusable matrices, threshold/acceptance-region report, preregistered full-evaluation criteria, D4 record.

**Tests / validation:** Hand-computed metric vectors; threshold-boundary tests; grouped resampling; leakage checks; deterministic rerun; CIs and multiple-comparison policy; no held-out tuning.

**Acceptance criteria:** A preregistered matcher/representation operating region simultaneously satisfies the documented technical-reliability and attack-surface bounds with uncertainty, and remains plausibly private-computable. Numeric bounds must be frozen before full data, not invented after it.

**Decision / gate:** **Gate A — Semantic representation viability.** Pass, repeat one justified pilot revision, or stop/reframe as a negative/measurement result. P9/P10 protocol engineering is forbidden on a failed Gate A.

**Dependencies:** P5.

**Cost:** AI-token Medium; compute Medium; storage Medium.

**Stop / fallback:** Tighten the use case or require a second factor; if no useful operating region exists, do not optimise cryptography for it.

### P7 — Image-stage versus text-only experiment

**Objective:** Determine whether image generation contributes measurable non-human technical value.

**Supports:** RQ1–RQ3/RQ5/RQ6; E1–E8/E13/E14/E16; D5; Gate B.

**Tasks:**

1. Freeze a paired design using identical concepts, paraphrases, splits, attacker inputs, and comparable downstream representations for image and direct-text paths.
2. Compare stability, random/near-neighbour separation, thresholds, acceptance-region mass, drift, semantic failure modes, latency, memory, storage, and new privacy exposure.
3. Use paired effect sizes/CIs and the preregistered “meaningful benefit versus added cost” rule; do not use human memorability/usability as an explanation.
4. Test whether any apparent gain is due to extra information/model capacity rather than the image transformation itself.
5. Record D5 and update title/architecture/experiment scope if the stage is removed or repositioned.

**Inputs:** Gate A survivors; P3 paired manifest; P4/P5 cached outputs; P6 metrics.

**Outputs:** paired ablation run/report, technical-cost table, D5 record, approved pipeline thesis.

**Tests / validation:** Same split and concept IDs; paired statistical analysis; equivalent threshold-selection procedure; resource accounting; confound audit.

**Acceptance criteria:** The decision is supported by preregistered paired evidence and all costs/failure modes, with no human inference. Both paths remain reported as scientifically meaningful baselines where applicable.

**Decision / gate:** **Gate B — Image-stage justification.** Retain as core, make optional/auxiliary, remove, or reframe the thesis.

**Dependencies:** P6 Gate A disposition.

**Cost:** AI-token Medium; compute Medium (low if caches suffice); storage Medium.

**Stop / fallback:** Continue with text semantics or a measurement paper if the image stage adds no meaningful benefit.

### P8 — Attack framework and semantic-guessing methodology

**Objective:** Build reproducible attacker models before selecting a privacy protocol, so protocol claims address realistic semantic guessing.

**Supports:** RQ2–RQ4; A1/A4–A8; E8/E10–E13 and inputs to E9; D8.

**Tasks:**

1. Implement common guess-candidate and account interfaces with fixed budgets and online rate-limit scenarios.
2. Build random, frequency-ordered, public-prompt-derived, LLM-assisted, generator/VLM-assisted, partial-information (`k` atoms), inversion/linkage, and adversarial-collision strategies only where D8 finds distinct value.
3. Separate attacker training/auxiliary data from target test accounts; log model prompts, versions, seeds, costs, and deduplication.
4. Measure success@budgets, guesses-to-success, accounts compromised, acceptance-region probability, benefit over simpler ordering, and sensitivity to partial knowledge.
5. Add cheap attack smoke tests and ethical/licensing controls; do not attack third-party services.
6. Freeze attack interfaces/distributions for protocol comparison while allowing explicitly versioned stronger attacks later.

**Inputs:** P2 adversaries; P3 data design; P6/P7 selected pipeline and thresholds.

**Outputs:** attack modules/configs/tests, attacker-distribution manifests, pilot attack report, D8 record.

**Tests / validation:** Fixed-seed determinism; target/auxiliary separation; monotonic budget and `k` checks where expected; random/frequency controls; no external target; traceable costs.

**Acceptance criteria:** A1/A4/A5/A6/A7/A8 each has a concrete analysis/experiment path or documented inapplicability; attack methods are reproducible and do not overclaim public prompts as secret choices.

**Decision / gate:** Freeze attack suite v1 and identify threats any protocol must materially improve.

**Dependencies:** P7 decision.

**Cost:** AI-token Medium–High; compute Medium; storage Medium.

**Stop / fallback:** Use controlled synthetic distributions/bounds and narrow claims if public/AI resources are unsuitable; if guessing already defeats the standalone use case, record this for Gate E and consider second-factor/measurement positioning.

### P9 — Privacy-protocol and architecture theoretical comparison

**Objective:** Eliminate unsuitable cryptographic candidates through literature, security, correctness, and feasibility analysis before implementation.

**Supports:** RQ4/RQ5; A2/A3/A6/A7; E9–E11/E15; D6/D7.

**Tasks:**

1. Verify primary sources/specifications and mature implementations for OPRF/VOPRF/threshold OPRF, PSI/PSI-CA/private threshold matching, secure sketches/fuzzy extractors + OPAQUE/PAKE, and MPC/HE similarity.
2. Define each construction concretely enough to analyse inputs, record format, keys, parties, outputs, leakage, correctness under noise, domain separation, and authentication/session binding.
3. Compare database-only, server/key, one-service, collusion/full-compromise, transcript, helper-data, inversion, linkability, and offline-dictionary outcomes.
4. Compare maturity, proof assumptions, novelty, set/vector compatibility, expected latency/bandwidth/storage, dependency health, implementation risk, and 12-page/artifact burden.
5. Reject candidates on documented essential failures; identify uncertain properties requiring only a minimal P10 proof-of-concept.
6. Produce D6/D7 shortlist; do not claim ordinary encrypted representations support approximate comparison.

**Inputs:** Gate A representation/matcher; Gate B architecture path; P2 model; P8 attacks; P1 literature.

**Outputs:** protocol/security comparison matrix, data/key/compromise diagrams, candidate specifications, rejection records, P10 microbenchmark plan.

**Tests / validation:** Each claim cites a primary source or is labelled inference; adversary walk-throughs cover A2/A3/A6/A7; leakage is explicit; no candidate is described only by a primitive name.

**Acceptance criteria:** Clearly unsuitable candidates are eliminated; each survivor has a precise unresolved question testable by a minimal POC; at least one plausible construction offers a concrete benefit over plaintext/hash-bound baselines, or a negative outcome is recorded.

**Decision / gate:** Stage-1 protocol shortlist and architecture hypotheses. No full protocol implementation.

**Dependencies:** P6 Gate A, P7 Gate B, P8 v1.

**Cost:** AI-token High; compute Low; storage Low.

**Stop / fallback:** If none survives, fail the protocol thesis and invoke D9 rather than implementing every candidate.

### P10 — Minimal protocol candidate proofs-of-concept and selection

**Objective:** Resolve only empirical uncertainties left by P9 and select the main protocol/baselines.

**Supports:** RQ4/RQ5; A2/A3/A7; E9/E11/E15; D6/D7; Gate C.

**Tasks:**

1. Implement mature-library wrappers only for shortlisted uncertain operations using synthetic semantic sets/vectors at observed representative sizes.
2. Create common correctness vectors for exact threshold boundaries, duplicates, malformed input, domain separation, and protocol failure.
3. Benchmark client/server time, bandwidth, record size, memory, and scaling under identical hardware/network assumptions; separate setup/preprocessing/online costs.
4. Demonstrate stored-record guess-validation and linkability capabilities under each P2 compromise state; test one-service/collusion failures where relevant.
5. Compare results against P9 predictions and P6 plaintext matcher needs; record implementation/dependency risk.
6. Select one main construction and justified baselines using the frozen D6/D7 rule; preserve rejections and uncertainty.

**Inputs:** P9 shortlist/specs; P6 set sizes/thresholds; P2 threat model; P8 attack interfaces.

**Outputs:** minimal POCs/wrappers/tests, common benchmark results, leakage/compromise report, D6/D7 records.

**Tests / validation:** Known-answer/library vectors where available; threshold edge cases; repeated benchmarks with uncertainty; transcript/serialization tests; no homemade cryptographic primitive.

**Acceptance criteria:** Remaining uncertain properties are measured; selection has a precise security claim, deployment assumptions, and reproducible performance evidence; retained baselines answer distinct reviewer questions.

**Decision / gate:** **Gate C — Protocol selection.** Select primary protocol, architecture hypothesis, and baselines; otherwise stop/reframe. Do not fully implement rejected candidates.

**Dependencies:** P9.

**Cost:** AI-token Medium–High; compute Medium; storage Low–Medium.

**Stop / fallback:** Choose a weaker but accurately labelled construction only if it still supports a worthwhile claim; otherwise pursue a measurement/negative paper.

### P11 — Selected privacy protocol implementation and security analysis

**Objective:** Implement and analyse the selected construction to research quality under the exact threat model.

**Supports:** RQ4/RQ5; A1–A3/A6/A7; E9–E11/E15; Gate D.

**Tasks:**

1. Write a versioned protocol specification: setup, registration, authentication, message formats, authentication/session binding, error behaviour, key/domain separation, rotation/migration, parties, outputs, and leakage.
2. Implement modular client/server/privacy-service components with mature primitives, input validation, replay/session protections, rate-limit hooks, and safe failure.
3. State and prove/reduce security/correctness claims where appropriate; clearly separate formal guarantees, operational assumptions, and empirical privacy evidence.
4. Evaluate database-only, server/key, one-service, collusion/full compromise; offline validation; record/transcript inversion; linkability; exact-score/intersection leakage.
5. Benchmark representative sizes and compare plaintext/hash-bound and retained candidate baselines.
6. Add unit, integration, security-regression, malformed-message, and known-answer tests; commission later expert review rather than treating tests as a cryptographic audit.

**Inputs:** Gate C record/spec; P2 threat model; P8 attacks; P10 wrappers/results.

**Outputs:** selected protocol modules/spec, security analysis/proofs, tests, benchmark/leakage runs, deployment assumption record.

**Tests / validation:** Correctness and threshold boundary; replay/malformed messages; domain separation; persistence/restart; compromise experiments; dependency/version scan; reproducible benchmarks.

**Acceptance criteria:** Implementation matches the spec; claims survive all scoped compromise cases or are narrowed; compared with baselines, the construction provides a concrete measurable/formal privacy benefit at documented cost and realistic assumptions.

**Decision / gate:** **Gate D — Privacy contribution viability.** Continue PETS privacy framing only if a defensible advantage exists; freeze protocol/architecture version for integration.

**Dependencies:** Gate C.

**Cost:** AI-token High; compute Medium; storage Medium.

**Stop / fallback:** Narrow protection claims, revise architecture, or reframe/stop if benefit depends on unrealistic trust or leakage/offline testing remains equivalent to baselines.

### P12 — End-to-end research prototype

**Objective:** Integrate the approved semantic and privacy components into a runnable non-UI scientific prototype.

**Supports:** RQ1–RQ5; all relevant threats; E1–E16 integration; prototype contribution.

**Tasks:**

1. Implement stable backend interfaces for generation/text path, extraction, canonicalisation, matching, protocol, account storage, and optional privacy service.
2. Build enrolment/authentication CLIs/APIs; keep prompt/image/plaintext semantics local in the strong mode and label debug/plaintext baselines.
3. Persist scheme/model/canonicaliser/protocol versions; reject or safely handle mismatches and specify re-enrolment/migration.
4. Add rate limiting, replay/session handling, restart/persistence, unavailability, malformed input, and audit-safe logging.
5. Integrate immutable experiment runner/config/provenance capture. A UI may be added only after the scientific CLI works.
6. Document local smoke use and resource expectations without implying production readiness.

**Inputs:** P5/P7 frozen pipeline; Gate D protocol; P3 schemas; P8 attacks.

**Outputs:** modular prototype, CLI/API, experiment runner, configs, end-to-end tests, architecture documentation.

**Tests / validation:** Enrol/auth success; incorrect rejection; restart; version mismatch; privacy-service failure; malformed/replay; server-visible-data audit; deterministic smoke run.

**Acceptance criteria:** A fresh documented environment can run enrolment/authentication and a smoke experiment without UI; server observables match the protocol claim; all integration tests pass.

**Decision / gate:** Freeze end-to-end interface v1 for full experiments.

**Dependencies:** Gate D.

**Cost:** AI-token High; compute Medium; storage Medium.

**Stop / fallback:** Ship a research CLI without UI; if integration invalidates protocol/privacy assumptions, return to P11 and version the correction before P13.

### P13 — Full experiment and attack matrix

**Objective:** Produce held-out evidence for all RQs, threats, required experiments, and baselines after viability gates justify the cost.

**Supports:** RQ1–RQ6; A1–A8; E1–E16; Gate E.

**Tasks:**

1. Freeze full manifests, hypotheses, primary/secondary outcomes, thresholds, models, attacks, baselines, sample-size rationale, exclusions, and compute/storage budget before the test run.
2. Execute E1–E7 stability/separability/threshold tests across semantic strata and required baselines using cached generation and representations.
3. Execute E8/E12/E13 acceptance-region, partial-information, and AI-assisted guessing at defined budgets; distinguish online rate-limited and offline settings.
4. Execute E9–E11 database/server/key compromise, offline validation, inversion, and cross-service linkability for every stored-record baseline and selected protocol.
5. Execute E14 model drift matrix and migration/re-enrolment analysis.
6. Execute E15 performance with repeated client/server/network conditions and scaling; execute E16 paired text-only comparison.
7. Execute A8 adversarial semantic collision search and other approved failure analyses.
8. Preserve all valid runs, failures, exclusions, and deviations; deviations require a versioned amendment before rerun.

**Inputs:** Frozen P12 prototype; P3 full manifest; P6/P7 preregistration; P8 attacks; Gate D protocol.

**Outputs:** Immutable raw/full runs with manifests/provenance, compact metric tables, failure/deviation log, Gate E evidence package.

**Tests / validation:** Smoke before each expensive run; configuration hashes; completeness checker; seed/split audit; baseline parity; repeated measurements/CIs; no overwritten runs; spot reproduction from raw data.

**Acceptance criteria:** Every E1–E16 item and A1–A8 has valid evidence or an explicit, justified inapplicability/failure; all RQs have interpretable held-out outcomes; negative results are retained.

**Decision / gate:** **Gate E — Attack resistance and honest limitations.** Keep standalone, require second factor, reposition as measurement/limitation, revise claims, or stop. No result is forced positive.

**Dependencies:** P12; all prior gates.

**Cost:** AI-token High; compute High; storage High.

**Stop / fallback:** Stop further costly runs once a preregistered decisive failure answers the question unless a smaller follow-up is necessary to localise the cause; reframe transparently.

### P14 — Statistical analysis, consolidation, figures, and tables

**Objective:** Convert immutable evidence into statistically defensible, reproducible answers and publication visuals.

**Supports:** RQ1–RQ6; A1–A8; E1–E16; all empirical claims.

**Tasks:**

1. Lock analysis scripts and apply the predeclared estimands, grouped resampling/CIs, threshold policy, multiple-comparison handling, and missing/failure policy.
2. Produce ROC/DET and FAR–FRR curves, acceptance-region/security–reliability plots, success-versus-budget curves, partial-information effects, drift matrices, inversion/linkability metrics, compromise/leakage tables, and performance scaling.
3. Report effect sizes and uncertainty, not only point estimates or p-values; distinguish exploratory from confirmatory analyses.
4. Audit subgroup/model sensitivity and unexpected failures without cherry-picking.
5. Generate every final figure/table from compact saved results; maintain a claim→run→analysis→figure/table traceability matrix.
6. Draft concise RQ answers and limitations based only on evidence.

**Inputs:** P13 immutable runs; preregistration/amendments; P2 definitions.

**Outputs:** Versioned analysis code, compact final result tables, `paper/figures/*`, traceability matrix, RQ answer/limitation summary.

**Tests / validation:** Rebuild all figures/tables from clean compact inputs; independent metric spot checks; CI/resampling unit tests; no manual plot edits; provenance links resolve.

**Acceptance criteria:** Every reported number is reproducible and traceable; uncertainty and negative results are visible; no machine metric is interpreted as human evidence.

**Decision / gate:** Freeze evidence version for manuscript; new analyses are labelled exploratory or require an amendment.

**Dependencies:** Gate E disposition.

**Cost:** AI-token Medium–High; compute Medium; storage Medium.

**Stop / fallback:** Remove unsupported claims/visuals; if analysis reveals leakage or invalid design, correct and rerun only affected phases with versioned justification.

### P15 — PETS manuscript construction and evidence-backed writing

**Objective:** Build a coherent, anonymised, page-budgeted manuscript whose contributions exactly match the evidence.

**Supports:** All RQs/threats/experiments; privacy positioning; Gate F.

**Tasks:**

1. Reverify official PoPETs 2027 template/requirements and migrate validated content from `draft.tex`; do not assume the current sample `main.tex` remains authoritative.
2. Write Introduction/Related Work/System & Threat Model/Semantic Construction/Protocol/Security/Implementation/Evaluation/Limitations/Conclusion within the 12-page main-body target.
3. Make real-world privacy relevance explicit on page 1 and distinguish this work precisely from verified VSA/closest work.
4. State every assumption, leakage, compromise result, negative outcome, deployment limitation, and absence of human evidence.
5. Add mandatory Ethical Considerations, Open Science, and AI Use sections; maintain anonymisation and citation verification.
6. Create a claim-evidence checklist for abstract, contribution bullets, protocol claims, and conclusion; use `TODO_RESULT` rather than invented numbers while drafting.
7. Build/lint the paper in a clean supported TeX environment and review rendered pages, figures, references, accessibility/readability, and appendix dependence.

**Inputs:** P1 references/requirements; P2 model; P14 evidence/figures; protocol spec/proof; decision records.

**Outputs:** Submission manuscript source/PDF, verified bibliography, appendices/supplement as permitted, claim-evidence matrix, build instructions.

**Tests / validation:** Clean build; page count; unresolved TODO/citation/reference scan; all BibTeX verified; anonymisation scan; figure/table provenance; internal consistency of claims and threat model.

**Acceptance criteria:** Every major claim maps to measured evidence, formal reasoning/proof, a figure/table, or a verified citation; main contribution is understandable without appendices; mandatory sections and page rules pass.

**Decision / gate:** **Gate F — Paper story.** Select D9 positioning and approve substantive manuscript only when the evidence supports it.

**Dependencies:** P14.

**Cost:** AI-token High; compute Low; storage Low.

**Stop / fallback:** Narrow/rewrite contribution claims or choose the negative/measurement story; do not polish an unsupported thesis.

### P16 — Research artifact and reproducibility package

**Objective:** Enable evaluators to reproduce core evidence legally and within documented resource tiers.

**Supports:** Reproducibility/artifact contribution; RQ1–RQ6 evidence.

**Tasks:**

1. Freeze source, dependency lock/container, model/dataset acquisition and verification scripts, configs/seeds, attack/analysis scripts, compact results, and figure/table regeneration.
2. Provide minimal/smoke and full modes with expected time, CPU/GPU, memory, storage, network, licences, and expected outputs.
3. Exclude non-redistributable weights/data and secrets; test fresh acquisition hashes and document licences/filters.
4. Add one-command or short staged validation for core claims; ensure the scientific pipeline needs no UI.
5. Produce artifact README, component map, troubleshooting, provenance/SBOM, archival plan, and badges/DOIs only when actually obtained.
6. Test on a clean supported environment and, if feasible, a second machine/runtime.

**Inputs:** P12 code/tests; P13/P14 runs/analysis; P15 paper mapping.

**Outputs:** Complete artifact package, environment lock/container, minimal/full scripts, verified instructions, release manifest.

**Tests / validation:** Clean-room setup; smoke reproduction; selected full/representative reproduction; figure/table hash/semantic checks; licence/secret/large-file scan; broken-link and dependency checks.

**Acceptance criteria:** A fresh evaluator can reproduce the core paper evidence using documented resources; restricted materials are acquired rather than redistributed; outputs trace to paper claims.

**Decision / gate:** Artifact-ready checkpoint; record unavoidable non-reproducible items and their effect.

**Dependencies:** P15 evidence story substantially frozen; P12–P14 complete.

**Cost:** AI-token Medium–High; compute Medium–High; storage Medium–High.

**Stop / fallback:** Provide validated compact/precomputed mode plus acquisition/full instructions when full compute is impractical; remove any claim whose only evidence cannot be preserved or explained.

### P17 — PETS 2027 submission-readiness audit

**Objective:** Perform a final adversarial audit of science, privacy claims, submission compliance, and artifact readiness.

**Supports:** Entire submission.

**Tasks:**

1. Recheck current official deadline, template, page, anonymisation, conflicts, ethics, open-science, AI-use, supplemental, and artifact rules.
2. Audit RQ1–RQ6, A1–A8, E1–E16, baselines, decision gates, claim-evidence traceability, proofs/assumptions, statistics, and limitations.
3. Conduct citation-to-source and BibTeX audit; confirm peer-review/preprint labels and VSA comparison.
4. Perform fresh manuscript/artifact builds, secret/personal-data/licence/large-file scans, and anonymisation review.
5. Seek domain review of cryptographic reasoning and statistical methodology where possible; triage findings without hiding limitations.
6. Freeze archival hashes/version, submission PDF, source, and artifact; record exact submitted state. Submission itself requires explicit user authorisation.

**Inputs:** P15 manuscript; P16 artifact; all decision/evidence records; official current requirements.

**Outputs:** `SUBMISSION_CHECKLIST.md`, audit findings/resolutions, frozen candidate manuscript/artifact and hashes.

**Tests / validation:** Two clean builds; automated TODO/reference/anonymity/secret/licence/size scans; manual page-one/privacy/claim review; all checklist items signed or explicitly waived with risk.

**Acceptance criteria:** No unsupported major claim, unresolved critical compliance issue, unverified citation, missing mandatory section, or irreproducible core result remains; residual limitations are disclosed.

**Decision / gate:** Submit, revise, defer, reframe, or stop. Never submit automatically.

**Dependencies:** P15 and P16.

**Cost:** AI-token Medium; compute Low–Medium; storage Low.

**Stop / fallback:** Defer submission or narrow claims if a critical issue cannot be resolved honestly before the deadline.

## Coverage cross-check

### Research questions

| RQ | Primary phases | Required outcome |
|---|---|---|
| RQ1 semantic stability | P3–P7, P13–P15 | Seed/paraphrase/style/perturbation/drift evidence with uncertainty. |
| RQ2 separability | P5–P8, P13–P15 | Random/near-neighbour discrimination, thresholds, FAR/FRR/EER/ROC/AUC. |
| RQ3 AI-assisted guessability | P3, P6–P8, P13–P15 | Budgeted empirical/AI/partial-information attacks and acceptance-region mass. |
| RQ4 template/protocol privacy | P2, P5, P8–P11, P13–P15 | Offline validation, leakage/inversion, linkability, compromise-specific claims. |
| RQ5 practicality | P4, P7, P9–P15 | Generation/extraction/crypto/end-to-end time, memory, bandwidth, storage, scaling. |
| RQ6 image necessity | P3–P7, P13–P15 | Paired text-only ablation and Gate B decision without human claims. |

### Threats

| Threat | Defined | Framework/design | Full evidence |
|---|---|---|---|
| A1 online guesser | P2 | P6/P8/P12 | P13/P14 |
| A2 database attacker | P2 | P9–P11 | P13/P14 |
| A3 server/key compromise | P2 | P9–P11 | P13/P14 |
| A4 AI-assisted attacker | P2 | P3/P6/P8 | P13/P14 |
| A5 partial information | P2 | P3/P8 | P13/P14 |
| A6 representation inversion | P2 | P5/P8/P9/P11 | P13/P14 |
| A7 cross-service linking | P2 | P5/P8–P11 | P13/P14 |
| A8 adversarial semantic collision | P2 | P3/P6/P8 | P13/P14 |

### Experiments

| Experiment | Design/pilot | Full execution/reporting |
|---|---|---|
| E1 seed stability | P3–P6 | P13/P14 |
| E2 paraphrase stability | P3–P7 | P13/P14 |
| E3 style variation | P3–P7 | P13/P14 |
| E4 semantic perturbation | P3–P7 | P13/P14 |
| E5 random impostors | P3–P7 | P13/P14 |
| E6 near-neighbour impostors | P3–P7 | P13/P14 |
| E7 threshold sweep | P6/P7 | P13/P14 |
| E8 acceptance-region security | P6–P8 | P13/P14 |
| E9 offline dictionary attack | P8–P11 | P13/P14 |
| E10 representation inversion | P5/P8/P9/P11 | P13/P14 |
| E11 cross-service linkability | P5/P8–P11 | P13/P14 |
| E12 partial-information attack | P3/P8 | P13/P14 |
| E13 AI-assisted guessing | P3/P7/P8 | P13/P14 |
| E14 model drift | P3–P5/P7 | P13/P14 |
| E15 protocol performance | P9–P11 | P13/P14 |
| E16 text-only baseline | P3–P7 | P13/P14 |

### Mandatory baselines

| Baseline | Selection/implementation | Evaluation |
|---|---|---|
| Plain embedding + cosine | P4–P6 | P7/P13/P14 |
| Plain structured matching | P5/P6 | P7/P13/P14 |
| Closest verified visual-semantic/VSA policy | P1/P4–P6 | P13/P14; exact documented reason if infeasible |
| Fuzzy recovery/secure sketch candidate | P1/P9/P10 | P13 if retained; explicit rejection evidence otherwise |
| Selected privacy-preserving protocol | P9–P11 | P13/P14 |
| Text-only semantic authentication | P4–P7 | P13/P14 |

### Decision gates

| Gate | Evidence | Permitted outcomes |
|---|---|---|
| A semantic viability, P6 | Frozen representation/matcher pilot; positive/random/near-neighbour distributions; acceptance-region trade-off; private-computability | Pass; one justified redesign; second-factor/narrowing; negative result/stop. |
| B image justification, P7 | Paired image/text technical/security/cost ablation | Core; optional/auxiliary; remove; revise thesis. |
| C protocol selection, P10 | P9 theoretical screen + survivor POCs under common compromise/performance criteria | Select primary/baselines; weaken accurately; reframe/stop. |
| D privacy contribution, P11 | Concrete privacy benefit versus plaintext/hash-bound prior baselines under explicit assumptions | PETS privacy framing; architecture/claim revision; reframe/stop. |
| E attacks/limitations, P13 | Full A1–A8/E1–E16 held-out evidence | Standalone; second factor; measurement/limitations; revise/stop. |
| F paper story, P15 | Claim→proof/run→figure/table/citation matrix and page-budgeted manuscript | Approve supported positioning; narrow/rewrite; do not submit. |

## Initial consistency and risk register

1. `AGENT.md` and `paper/draft.tex` agree on RQ1–RQ6, A1–A8, no human study, acceptance-region security, mandatory baselines, the three protocol families, and the need for evidence gates.
2. `AGENT.md` is slightly more operational: it explicitly lists cardinality threshold as a plaintext matcher and E1–E16 as named requirements. This plan follows it while preserving the draft’s Jaccard/weighted/cosine candidates.
3. Both documents describe structured semantics and OPRF/PSI as current preferred directions, but explicitly call them hypotheses. D3/D6 and Gates A/C prevent premature selection.
4. `paper/draft.tex` is an 18-page research-direction article, not a submission manuscript. `paper/main.tex` plus `sample-base.bib` are PoPETs template examples with sample authors/references, not project evidence. P15 must verify the then-current official template before migration.
5. The asserted closely related 2026 VSA work is the most immediate novelty risk and has not yet been bibliographically verified in this initialization; P1 begins with that verification. No citation from the template bibliography is treated as verified.
6. The image stage has no allowed human-factors justification in this project. A negative Gate B could require changing the title and central thesis.
7. Low/nonuniform semantic entropy and a large acceptance region may defeat standalone authentication even if matching is accurate. P6/P8/P13 allow a second-factor or measurement-paper outcome.
8. A single server holding both protected records and tokenisation keys may remain an offline oracle after full compromise. D6/D7 and Gates C/D require the actual benefit to justify any non-collusion, threshold, or hardware-isolation assumption.
9. The repository began without Git, README, ignore rules, environment/dependencies, verified research bibliography, code, datasets, or results. Environment selection is deliberately deferred until P4 requirements are known, preventing premature dependency/model installation.

No phase assumes a positive result. Failure, narrowing, second-factor positioning, measurement/limitation framing, and stopping are first-class outcomes.
