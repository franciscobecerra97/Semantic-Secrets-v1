# Semantic Secrets execution plan

Status: P0–P7 are historical v1 evidence; P8 passed Gate V2-N; P9-v2 failed immutably; P9-v3A froze v3.0.0; and P9-v3A.1 completed a prospective v3.1.0 pipeline/resource/support audit on 2026-08-25 without weights, images, or inference. On 2026-08-26, pre-execution engineering prepared the deterministic compiler, exact two-pipeline subprocess boundary, dataset/annotation checks, formal guards, and reproducible RunPod package; its local 320-case pass is not Gate evidence. P9-v3B remains not started and awaits explicit formal authorisation plus a confirmed two-human annotation resource. P9-v3C is blocked on Gate V3-A1, and P10–P20 remain blocked on Gate V3-A2.
Authority: `AGENT.md` is the active scientific and engineering contract. This plan operationalises it and may not silently weaken it.
Scope: prospective PoPETs/PETS 2027 study of reconstructable semantic authentication, the security of its induced acceptance region, and private verification of the frozen fuzzy predicate; no human-subject study. The primary motivation is approximate semantic reconstruction rather than password memorability or password replacement. P7's image-stage rejection remains valid for `visual-semantic-pipeline-v1`; v2 is a new generative-reconstruction hypothesis requiring new evidence.

## How to execute this plan

When asked to “Execute Pn” or “Continue with Pn”:

1. Read `AGENT.md`, this plan, the relevant decision records, and the phase inputs.
2. Confirm earlier dependencies and gates. Do not spend full-scale compute before the required gate passes.
3. State the RQ, threat, claim, or decision the work supports.
4. Perform only the numbered phase tasks, using the smallest useful dataset/configuration first.
5. Save configurations, provenance, raw observations, and negative results. Never substitute invented values or citations.
6. Run the listed validation and evaluate the acceptance criteria.
7. Update the phase status and persistent decision record; record a stop/reframe outcome as faithfully as a positive result.
8. Report changes, evidence, failed checks, unresolved uncertainty, and the next permitted phase. Per the user's standing instruction of 2026-08-24, commit and push each completed `Px` phase as its own checkpoint; never commit a partial/failed phase or force-push.

Phase status values are `not started`, `in progress`, `blocked by gate`, `complete`, or `stopped/reframed`. A phase is complete only when its outputs, validation, and acceptance criteria are satisfied.

## Non-negotiable research controls

- Treat all current model, representation, matching, protocol, and architecture preferences as hypotheses.
- Do not claim memorability, usability, human preference, recall, accessibility, natural secret-selection entropy, human authentication speed, superiority to passwords/passkeys, or that images are easier to remember.
- Treat the prompt as a reconstruction interface, the generated image as a transient reconstruction medium, bounded observations as probabilistic evidence, the canonical graph as the security-sensitive representation, and the whole acceptance region as the operational secret surface. Neither prompts nor pixels provide credential entropy.
- Model security over the whole acceptance region, not image pixels, the enrolled prompt/graph, or exact semantic equality. An attacker wins with any accepted semantic alternative.
- Keep the strictness/tolerance tension explicit: strict predicates reject benign independent reconstructions, while tolerant predicates expand the attacker's accepted alternatives.
- Use `docs/threat_claim_matrix_v2.csv`; state which data, keys, services, records, policies, and transcripts each attacker obtains.
- Keep prompts, images, plaintext atoms, raw embeddings, and exact scores client-side in the strongest target architecture; document every deviation.
- Measure client-side practicality under RQ6 rather than assume it. A research GPU is experimental infrastructure, not automatically a deployment requirement; impractical trusted-client execution is a valid limitation, restricted-use result, failed practicality gate, or negative outcome. Do not move secret-bearing reconstruction/semantic processing to an untrusted cloud to rescue feasibility.
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

## Decision investigations

The former D1–D5 generator/extractor/representation/matcher/image investigations belong to the completed v1 history recorded in P4–P7 and `DECISIONS.md`. The former unexecuted D6–D9 path is superseded by P7-R2 and must not control v2.

Active v2 decisions are phase-gated:

| Decision | Phase | Cheapest valid evidence | Required outcome |
|---|---|---|---|
| V2-DN combined novelty and scope | P8 | Verified primary literature and formal comparison | C1–C4 remain jointly defensible or are narrowed before implementation |
| V2-D1 failed monolithic capability | P9-v2 | Immutable formal capability fixture | Gate V2-A failed; no reinterpretation or rerun |
| V3-D1 modular extraction architecture | P9-v3A | Primary literature plus formal/preregistered design | Freeze model-evidence/compiler separation, two candidates, data, metrics, and gates |
| V3-D1.1 pre-execution suitability | P9-v3A.1 | Bounded primary-artifact and support-feasibility audit | Freeze v3.1 hardware semantics, EGTR comparator, support opportunities, and annotation prerequisite before output |
| V3-D2 modular component capability | P9-v3B | New controlled/naturalistic capability data | One whole pipeline passes V3-A1; no cross-pipeline type union |
| V3-D3 independent reconstruction | P9-v3C | Separate preregistered reconstruction data | Frozen eligible language and M/T interface pass V3-A2 |
| V2-D2 policy and baselines | P10 | Training-only derivation and new pilot against B0/B1/B2 | Proposed policy passes V2-B without held-out tuning after V3-A2 |
| V2-D3 attack distributions/positioning | P11 | Frozen K0–K3 strategies and budget curves | V2-C selects standalone, factor, constrained, negative, or stop |
| V2-D4 private functionality | P12 | Primary-source/security/leakage comparison | V2-D identifies a property beyond VSA/hash/plaintext baselines |
| V2-D5 protocol and architecture | P13 | Minimal mature-library POCs under common fixtures | V2-E selects one primary and meaningful baselines or stops |
| V2-D6 paper positioning | P16–P20 | Frozen end-to-end evidence and claim matrix | V2-F supports only the strongest evidence-backed story |

The eventual paper should lead with the transition from exact reproduction to approximate semantic reconstruction, then the induced acceptance-region security problem and the separate privacy problem. C1/C2 remain enabling contributions; C3/C4 remain the strongest eventual security/privacy contributions if the constructive path survives. Evidence may support standalone, second-factor, policy-constrained, restricted-use, another bounded setting, negative/measurement, or stop positioning; universal password replacement is not presumed.

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

**Status:** Complete on 2026-08-24. Threat-model version v1 is frozen for pilot design; protocol and deployment architecture remain unselected until D6/D7.

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

**Status:** Complete on 2026-08-24. Smoke/pilot methodology is approved; no public corpus, model output, or image was acquired/generated, and full-scale acquisition remains forbidden until P6/P7 justifies it from pilot uncertainty.

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

**Status:** Complete on 2026-08-24. D1 provisionally selects SD-Turbo subject to a CUDA feasibility/renderability screen, retains SDXL base as the sole stronger-hardware alternative, and preserves the no-image path. D2 retains Florence-2, SigLIP, MiniLM, and the controlled parser for P5; SmolVLM is rejected under structured schema v1. A primary extractor waits for P5.

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

**Status:** Complete on 2026-08-24 with a negative uncertainty outcome. `canonical-semantics-v1` and training-only `oracle-train-idf-v1` are frozen. Controlled weighted direct-text semantics is the primary P6 hypothesis; unweighted text, MiniLM, and SigLIP remain baselines. Florence structured fusion is rejected. No real representation has uncertainty-supported near-neighbour separation at smoke scale, so Gate A remains closed and P6 must be a preregistered pilot/negative confirmation.

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

**Status:** Complete on 2026-08-24; interpretation amended by P6-R on 2026-08-25. The preregistered 60-family pilot evaluated 36 train and 12 validation families while leaving 12 test families unevaluated. Weighted controlled-text overlap had validation FRR 0.208, conditional targeted-neighbour acceptance 0.750, random FAR 0.030, and same-minus-neighbour 95% family-bootstrap interval `[0.000, 0.063]`. These unchanged results fail the frozen conditional separation/reliability criteria, but do not estimate practical attack success within a guess budget. Gate A is therefore a **conditional failure / unresolved security viability**, neither a pass nor evidence of impossibility. P9/P10 remain blocked pending a constructive Gate A2 result after P8.

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

**Decision / gate:** **Gate A — Conditional semantic representation viability.** P6 asks whether already-constructed same and near-neighbour samples separate at a frozen threshold. Its failure is a conditional failure: it blocks a viability claim but cannot by itself establish budgeted attacker success. P7 and P8 may proceed as bounded diagnostics; P9/P10 remain forbidden until Gate A2.

**Dependencies:** P5.

**Cost:** AI-token Medium; compute Medium; storage Medium.

**Stop / fallback:** Preserve P6 unchanged. Measure the missing attacker-budget quantity in P8, then let Gate A2 decide standalone, second-factor, policy-constrained, negative/measurement, or stop positioning before any protocol optimisation.

### P7 — Image-stage versus text-only experiment

**Status:** Complete on 2026-08-25 with **Gate B outcome B**: remove the image stage from the authentication core and retain it only as an optional/measurement baseline. `p7-cached-v1` reused the 27 P5 train/validation rows and existing SD-Turbo, Florence, SigLIP, controlled-text, and MiniLM artifacts; it executed no model and accessed no P6 artifact or held-out test row. No image comparison met the frozen material-benefit rule. Image-minus-text same-minus-near effects were `-0.076` (95% family-bootstrap `[-0.274, 0.091]`) for structured Jaccard, `-0.022` (`[-0.189, 0.134]`) for weighted structured matching, and `-0.005` (`[-0.056, 0.042]`) for dense cosine. All image paths also had materially worse same-minus-random effects. Florence macro atom F1 was 0.375 versus 0.638 for direct text; every validation pathway had worst minimax error 0.667. This is evidence about the tested pipelines, not universal extractor impossibility.

**Objective:** Determine whether image generation contributes measurable non-human technical value.

**Supports:** RQ1–RQ3/RQ5/RQ6; E1–E8/E13/E14/E16; D5; Gate B.

**Tasks:**

1. Freeze a paired design using identical P5 concepts, paraphrases, splits, and pair definitions. Compare Florence structured atoms with controlled-text structured atoms under identical Jaccard and frozen weighted-overlap rules; compare SigLIP image embeddings with MiniLM text embeddings under cosine while explicitly treating model capacity/modality as a confound.
2. Reuse only cached P5 outputs. Compare non-empty rate, same stability, random and near-neighbour separation, paired same-minus-near and same-minus-random effects with family-bootstrap intervals, near-only and all-negative AUC, equivalent training-selected threshold rules evaluated on validation, atom precision/recall/F1 and changed-atom failures, latency, memory, storage, and privacy exposure. Drift remains unavailable because P5 contains one frozen revision per model.
3. Apply the frozen material-benefit rule in `experiments/image_stage_ablation/config/p7_cached_v1.json`: the image path must show uncertainty-supported improvement in same-minus-near separation without a material threshold trade-off, and structured extraction must not lose atom fidelity. Added compute/storage/privacy exposure counts against retention. This is a bounded diagnostic, not a new Gate A test.
4. Audit attribution: dense image/text results cannot isolate the image transformation from encoder differences; structured results share canonicalisation and matching but Florence extraction quality can bottleneck the image path.
5. Record D5 and exactly one Gate B disposition: (A) retain image as core, (B) make it optional/reposition/remove from the authentication core, or (C) leave the question unresolved because extraction is the bottleneck. Do not implement any semantic-policy redesign in P7.

**Inputs:** P6-R conditional-failure interpretation; P3 smoke paired manifest; P4/P5 cached outputs. P6 metrics provide context only and are not pooled with or tuned against P7.

**Outputs:** paired ablation run/report, technical-cost table, D5 record, approved pipeline thesis.

**Tests / validation:** Same split and concept IDs; paired statistical analysis; equivalent threshold-selection procedure; resource accounting; confound audit.

**Acceptance criteria:** The disposition is supported by the frozen paired metrics, uncertainty, atom errors, costs, and confound audit, with no human inference and no claim that K3 conditional FAR must be zero. Both paths remain reported as scientifically meaningful baselines where applicable.

**Decision / gate:** **Gate B — Image-stage justification.** Retain as core, make optional/auxiliary, remove, or reframe the thesis.

**Dependencies:** P6-R amendment and unchanged P6 evidence.

**Cost:** AI-token Medium; compute Medium (low if caches suffice); storage Medium.

**Stop / fallback:** Continue with text semantics or a measurement paper if the image stage adds no meaningful benefit.

> **v2 transition note (2026-08-25):** P0–P7 above are preserved verbatim as the historical `visual-semantic-pipeline-v1` plan and evidence. Their forward references to the former P8/Gate A2/P9/P10 path are superseded by decision P7-R2. They do not authorise or describe the active v2 phases below.

### P8 — v2 novelty, formalisation, and preregistration design

**Status:** Complete on 2026-08-25. The focused primary-source review found all component mechanisms in prior art and therefore narrowed C1–C4, folded C5 into C3/C4, and prohibited primitive/"first" claims. The exact combined reconstruction/attack/private-verification question remained distinguishable in the verified corpus, so Gate V2-N **passes with narrowing**. The typed graph, reference predicate, controlled-data design, screening limits, baselines, uncertainty, attack budgets and V2-A/V2-B/V2-C thresholds are frozen in `docs/formal_specification_v2.md` and `experiments/v2/config/preregistration_v2.json`. No model, dataset, v2 output, cryptographic implementation, or sealed v1 family was accessed.

**Objective:** Establish a defensible v2 gap and freeze the research design before any expensive implementation or experiment.

**Execution boundary:** No expensive experiment, model or dataset acquisition, or cryptographic implementation is permitted in P8.

**Supports:** RQ1–RQ6; C1–C5; Gate V2-N.

**Tasks:**

1. Complete a focused primary-source novelty refresh covering graphical/image authentication, SemanticLock, VSA, generative-AI authentication, fuzzy authentication/extractors/secure sketches/PAKE, OPAQUE/PAKE, OPRF/VOPRF, PSI/PSI-cardinality/Circuit-PSI and committed/input-consistent variants, private biometrics/vector/graph matching, cancelable templates, unlinkability/inversion, oracle leakage, and AI-assisted guessing.
2. Update `docs/related_work.csv`, `paper/references.bib`, and `docs/novelty_matrix_v2.csv`; narrow C1–C4 if verified work subsumes any part. Treat C5 as optional.
3. Freeze RQ1–RQ6, the typed graph and `S=(M,T)` semantics, the plaintext reference functionality, and the two required VSA baselines.
4. Define the v2 controlled concepts, ground-truth semantic tasks, train/validation/sealed-test splits, independent-generation trial structure, and licence/ethics rules. Do not access the twelve sealed v1 P6 test families.
5. Freeze generator/extractor capability screening before model execution: few justified candidates, independent capability criteria, model/revision/resource limits, failure rules, and no outcome-driven search.
6. Freeze system-derived policy methodology, planned baselines, attack budgets/K0–K3 distributions, uncertainty methods, viability thresholds, caching/versioning, and the P9–P11 preregistrations.

**Inputs:** v1 P0–P7 evidence; complete VSA review; v2 research/security contracts.

**Outputs:** verified novelty record; formal specification; data/split and screening plans; P9–P11 preregistration; Gate V2-N decision.

**Validation:** Primary-source traceability; no unsupported “first” language; all thresholds and selection rules fixed before expensive outputs; no model/dataset acquisition or experiment.

**Decision / gate:** **Gate V2-N — Novelty viability.** Proceed only if C1–C4 retain a defensible combined gap relative to VSA and broader prior art. Otherwise narrow/reframe before implementation.

**Dependencies:** P7-R2 direction amendment.

**Cost:** AI-token Medium–High; compute None/Low; storage Low.

**Stop / fallback:** A novelty failure blocks P9. Preserve the review as evidence and select a narrower measurement or privacy question.

### P9 — Canonical visual-semantic credential derivation

**Status:** Complete on 2026-08-25 with a negative result. Both frozen extractors produced an invalid graph on their first formal validation fixture. Because one invalid among 32 caps best-case schema validity at 0.96875 below the frozen 0.98 threshold, P9A stopped for exact logical futility. No extractor survived; P9B was not executed; Gate V2-A failed; P10 is blocked. Full F1, determinism, error-stratum, and latency-median estimates were not made. See `docs/p9_capability_screen_v2.md`.

**Objective:** Determine whether the image-derived representation required by C1 is technically viable before authentication-policy optimisation.

**Supports:** RQ1/RQ2/RQ6; C1/C2; Gate V2-A.

**P9A — Extractor capability:**

1. Evaluate only preregistered visual-semantic extraction families on controlled images with known ground truth.
2. Measure objects, attributes, counts, actions, relationships, and scene/context separately where required by the frozen graph.
3. Report atom/predicate precision, recall, F1, calibration/failure, determinism, latency, memory, model/revision drift, and structured error strata.
4. Eliminate any extractor that cannot reliably represent frozen security-critical dimensions; do not tune on authentication outcomes.

**P9B — Generative reconstruction:**

1. For the surviving generator/extractor pair(s), run independent images from semantically equivalent reconstructions across paraphrases, seeds, stochasticity, layout, justified styles, and selected version/model drift.
2. Canonicalise graphs under the frozen v2 specification and quantify same-concept stability, extraction fidelity, targeted separation, failure rates, and uncertainty.
3. Include direct-text processing only as an ablation/baseline. Cache images and graphs; never treat pixels or prompts as credential entropy.

**Outputs:** capability screen; v2 representation/version selection or negative result; immutable pilot evidence.

**Validation:** Split isolation; independent generation/re-inference; fixed model budget; no policy/threshold optimisation; repeatability and provenance.

**Decision / gate:** **Gate V2-A — Visual-semantic reconstruction viability.** Advance only if at least one image-based representation has uncertainty-supported technical reconstruction signal suitable for policy evaluation.

**Dependencies:** Constructive Gate V2-N.

**Cost:** AI-token Medium; compute Medium; storage Medium.

**Stop / fallback:** Do not search indefinitely. Preserve negative evidence and reconsider whether the visual-reconstruction hypothesis can continue.

### P9-v3A — Modular visual-semantic extraction architecture and preregistration

**Status:** Complete on 2026-08-25. This phase created only architecture, formal specification, literature traceability, machine-readable configs, deterministic config tests, governance, and manuscript updates. No model weights, images, model inference, P9-v3B/P9-v3C/P10 work, or cryptography was executed. P9-v2 remains byte-unchanged failed evidence.

**Objective:** Replace the rejected monolithic VLM-to-credential-JSON assumption with a testable separation between learned observations and deterministic credential compilation.

**Supports:** RQ1/RQ2/RQ6; preserves C1–C4 without adding empirical support; preregisters Gates V3-A1/V3-A2.

**Tasks completed:**

1. Diagnose P9-v2's architecture and evidence boundary without altering its artifacts.
2. Freeze `I=G(P,r)`, `O=Observe(I)`, `S=C(O)`, `(M,T)=Pi(S)`.
3. Define `L_visual`, component-local confidence/provenance, abstention, compiler invariants, typed failures, canonical IDs, duplicates, derived counts/geometry, and serialization.
4. Freeze at most two literature-justified modular pipelines with exact revisions/licence preconditions and compute estimates.
5. Freeze a 240-image, family-split two-stratum future capability design, type-level metrics/uncertainty/eligibility, 320 compiler cases, cache rules, stop rules, V3-A1 and future V3-A2.

**Outputs:** `docs/p9_v3_reframe.md`; `docs/formal_specification_v3.md`; `experiments/v3/README.md`; `experiments/v3/config/*.json`; config audit test; updated contract, plan, decision log, related work, bibliography, and planning manuscript.

**Validation:** JSON/config consistency; exactly two distinct pipelines; exact compiler-test count; critical rules numeric; v2 protected paths unchanged; no large artifacts; repository tests; LaTeX/PDF build and visual inspection.

**Decision / gate:** No empirical gate is passed in P9-v3A. It authorises only a later P9-v3B when explicitly requested.

**Dependencies:** Immutable P9-v2 failure and explicit scientific direction change.

**Cost:** AI-token Medium–High; compute Low; storage Low.

**Stop / fallback:** If the design cannot separate perception from compilation or cannot be licensed/reproduced, stop rather than run a vague model search.

### P9-v3A.1 — Pre-execution pipeline and resource suitability audit

**Status:** Complete on 2026-08-25. Prospective amendment only; no model weights, capability images, perception inference, validation output, P9-v3B, P9-v3C, or P10 work occurred.

**Objective:** Correct the resource wording, choose one artifact-suitable graph-native comparator, and ensure the planned support/annotation design is executable before any v3 output.

**Tasks completed:**

1. Separated installed GPU capacity from measured complete-pipeline VRAM consumption while preserving the 24 GiB numeric gate.
2. Compared only SGTR, EGTR, and ROBIN/Synthetic Visual Genome from primary papers and official repositories; selected EGTR before output.
3. Preserved Grounding DINO + SigLIP2 and explicitly classified pair-crop relation scoring as an experimental hypothesis.
4. Defined positive/applicable-negative opportunities, five primary gate types, exploratory `not_gate_evaluable` handling, and feasible family concentration.
5. Preserved two-human model-blind annotation and recorded the unconfirmed second annotator as a blocker with an external-human replacement protocol.
6. Created v3.1 configs/addendum without modifying the meaning of v3.0.0.

**Outputs:** `docs/p9_v3_preexecution_audit.md`; `docs/formal_specification_v3_1.md`; `experiments/v3/config/preregistration_v3_1.json`; `experiments/v3/config/visual_observation_v3_1.json`; v3.1 config tests; governance, literature, bibliography, and manuscript amendments.

**Validation:** Primary-source traceability; exactly two final pipelines; support arithmetic; unchanged 320-case compiler floor and Gate language requirement; JSON/CSV/BibTeX/LaTeX checks; P9-v2 protection; no weights/images/outputs.

**Decision / gate:** No empirical gate passed. The executable shortlist is exactly `v3.1-gdino-siglip2` and `v3.1-egtr-siglip2`.

**Dependencies:** Immutable P9-v3A commit `8e44caa`.

**Stop / fallback:** Do not create images until the annotation blocker is resolved. Do not restore SGTR, add another pipeline, or change hardware for semantic outcomes after validation.

### P9-v3B — Modular component capability and `L_cred` eligibility

**Status:** Not started; requires explicit user authorisation and resolution of the v3.1 two-human annotation-resource blocker.

**Prepared execution boundary (2026-08-26):** `prototype/semantic_secrets/v3/` implements the frozen compiler; `experiments/v3/runtime/` supplies schemas, manifest/annotation tooling, isolated adapter orchestration, content-addressed caches, telemetry, and fail-closed formal guards; `infra/runpod/` supplies the pinned dual-environment container and runbook. The pre-execution compiler matrix passes 320/320 locally and must pass again in the locked image. This preparation did not create a capability image, acquire a weight, inspect a model output, freeze a development threshold, start P9-v3B, or pass V3-A1. EGTR artifact terms/layout/base-transform provenance remain acquisition-time fail-closed checks.

**Objective:** Test perception and compiler capability on new controlled and naturalistic data before any reconstruction/authentication study.

**Tasks:** After the annotation-resource record exists, author the frozen `cap-v3-*` dataset and labels; implement/test the compiler; acquire only the two v3.1 pipelines after licence/hash checks; run bounded smoke; freeze development thresholds; execute validation and repeat; compute per-type/stratum support, metrics, uncertainty, measured resources, and exact compiler checks.

**Outputs:** immutable manifests, observations, compiler cases/results, aggregate report, eligible `L_cred` per complete pipeline, and Gate V3-A1 decision.

**Decision / gate:** **Gate V3-A1 — Modular extraction viability.** Pass only under the complete conjunction formed by historical `preregistration_v3.json` plus prospective `preregistration_v3_1.json`. Do not union eligible types across pipelines. Installed GPU capacity is irrelevant; measured pipeline consumption is gated.

**Dependencies:** Complete P9-v3A.1, explicit instruction, and a confirmed two-independent-human annotation record before image creation.

**Stop / fallback:** If no pipeline passes, stop the visual constructive path or preregister a genuinely new reframe. Do not execute P9-v3C.

### P9-v3C — Independent visual reconstruction

**Status:** Not started; blocked on constructive Gate V3-A1 and a separate preregistration.

**Objective:** Determine whether independently generated images yield stable, discriminative credentials using only V3-A1-eligible atom types.

**Tasks:** Freeze separate concepts/data/splits/generation roles; implement the still-untuned `M/T` interface and baselines using development only; evaluate enrolment eligibility, FRR, targeted-neighbour FAR, random FAR, same/near AUC, paired policy improvement, failure, and uncertainty.

**Outputs:** independent reconstruction evidence and Gate V3-A2 decision. This phase cannot claim memorability, entropy, attack resistance, or privacy.

**Decision / gate:** **Gate V3-A2 — Independent visual reconstruction viability.** All numeric checks in the v3 preregistration must pass. A constructive result unlocks P10; failure preserves a negative result and blocks P10.

**Dependencies:** Constructive V3-A1 and a new pre-output freeze.

**Stop / fallback:** No policy repair from validation, no cross-pipeline union, and no cryptographic work after failure.

### P10 — Policy-aware semantic credential design `S=(M,T)`

**Status:** Not started; blocked on constructive Gate V3-A2.

**Objective:** Freeze and evaluate a system-derived semantic policy independently of held-out outcomes.

**Supports:** RQ2/RQ3; C2/C3; Gate V2-B.

**Tasks:**

1. Compare: `B0` dense semantic similarity, `B1` global fuzzy overlap, `B2` closest feasible VSA-style semantic-policy component, and `P1` proposed policy-aware `S=(M,T)`.
2. Derive `M` mandatory structural predicates and `T` tolerant secondary predicates deterministically from independent semantic rationale, training-only statistics, extractor reliability, attacker-frequency evidence, and protocol compatibility.
3. Do not ask users to select `M/T` in the primary study. Document any non-reproducible VSA detail and keep the full VSA semantic-plus-password architecture separate.
4. Freeze missing-anchor, count/operator, relation, tolerance, duplicate, malformed, version-mismatch, and boundary behaviour.
5. Evaluate a technical enrolment-strength policy that may reject insufficiently distinctive concepts. Do not call rejection usability.
6. Use only the V3-A1-eligible language and the separate P9-v3C development data/identifiers allowed by a constructive V3-A2; do not tune from P7, P9-v2, or held-out results.

**Outputs:** frozen reference predicate; policy derivation spec; baseline implementations; pilot report; Gate V2-B decision.

**Validation:** Training-only fitting; sealed evaluation; baseline fidelity; ablations; family-level uncertainty; no manual primary policy.

**Decision / gate:** **Gate V2-B — Policy-aware semantic viability.** Proceed only if `P1` preserves legitimate independent reconstruction variation while materially improving security-relevant discrimination over B0–B2.

**Dependencies:** Constructive Gate V3-A2.

**Cost:** AI-token Medium; compute Medium; storage Medium.

**Stop / fallback:** Preserve the negative/conditional result and do not repair the policy from held-out errors.

### P11 — Acceptance-region and budgeted attacker evaluation

**Status:** Not started; blocked on Gate V2-B.

**Objective:** Measure C3 over the complete accepted region rather than infer security from random FAR.

**Supports:** RQ3; C3 and optional C5; Gate V2-C.

**Tasks:**

1. Freeze K0–K3 strategy inputs and budgets; include random, frequency, targeted neighbours, valid public-prompt-derived distributions, LLM-assisted, generator/VLM-assisted, partial-information, and adaptive semantic search where justified.
2. Report `success@1`, `success@5`, `success@10`, `success@B`, guesses-to-success, acceptance-region mass, accounts compromised, duplicates, cost, and uncertainty.
3. Separate bounded online `Accept/Reject` attacks from offline attacks requiring a stolen verifier view. P11 measures semantic viability; construction-specific offline validation follows later.
4. Compare increasingly knowledgeable attackers to simple controls and keep target data separate from attacker auxiliary/training data.
5. Preserve P6's 75% targeted-neighbour conditional v1 result as a formative K3-like baseline, not a v2 result or total success estimate.
6. Determine whether adaptive verification-oracle leakage is distinct enough to retain C5 separately.

**Outputs:** frozen attack framework; budgeted attack report; C5 disposition; Gate V2-C positioning.

**Validation:** Determinism; budget monotonicity checks; auxiliary/target separation; reproducible model prompts/seeds/costs; ethical local targets only.

**Decision / gate:** **Gate V2-C — Acceptance-region security viability.** Select exactly one: standalone, second factor, policy-constrained, measurement/negative contribution, or stop. Only a constructive result unlocks protocol engineering.

**Dependencies:** Constructive Gate V2-B.

**Cost:** AI-token Medium–High; compute Medium; storage Medium.

**Stop / fallback:** Rate limiting cannot rescue an efficiently enumerable offline semantic region. Stop or narrow rather than force cryptography.

### P12 — Private-verification functionality and protocol comparison

**Status:** Not started; blocked on constructive Gate V2-C.

**Objective:** Define the ideal C4 functionality and compare mature constructions before choosing primitives.

**Supports:** RQ4–RQ6; C4/C5; Gate V2-D.

**Tasks:**

1. Specify `PrivateSemanticVerify(protected M,T; candidate M',T'; domain; session) -> Accept/Reject`, party outputs, policy privacy, metadata, malicious-input behaviour, and exact compromise views.
2. Compare justified OPRF/VOPRF and threshold variants, PSI/PSI-cardinality/Circuit-PSI, MPC, fuzzy extractors/secure sketches, PAKE/OPAQUE/fuzzy PAKE, HE/vector matching, and compositions.
3. Analyse database-only validation, AS/PS/share compromise, collusion/total compromise, policy leakage, input consistency, transcript leakage, domain separation, linking, adaptive-query controls, correctness, cost, and deployment assumptions.
4. Ask whether each candidate is merely an obvious wrapper around an established primitive. Do not claim cryptographic novelty without a distinct property and evidence.
5. Select at most a small set for P13 using predeclared elimination criteria.

**Outputs:** ideal functionality; leakage/compromise matrix; theoretical comparison; P13 shortlist or stop.

**Validation:** Primary-source grounding; explicit assumptions; reference-function mapping; no prototype or benchmark used to mask an undefined property.

**Decision / gate:** **Gate V2-D — Private-functionality viability.** Proceed only if a candidate provides a concrete property beyond VSA's hash-based server-opaque design and plaintext/hash baselines.

**Dependencies:** Constructive Gate V2-C.

**Cost:** AI-token High; compute Low; storage Low.

**Stop / fallback:** If all constructions are trivial wrappers without a defensible system/privacy contribution, narrow C4 or stop before P13.

### P13 — Minimal privacy-protocol proofs of concept and selection

**Status:** Not started; blocked on Gate V2-D.

**Objective:** Implement only the surviving candidates with mature libraries and select one research direction.

**Supports:** RQ4–RQ6; C4; Gate V2-E.

**Tasks:**

1. Implement minimal candidates against the frozen plaintext predicate and identical fixtures.
2. Compare correctness, explicit leakage, database compromise, server/key/share compromise, collusion, offline guess testing, linkage, bandwidth, latency, storage, and artifact complexity.
3. Test boundary values, duplicates, malformed graphs, policy/version mismatch, replay/context binding, and failure behaviour.
4. Record any construction change as a new version; do not optimise a failed privacy property away by changing the semantic predicate.

**Outputs:** reproducible POCs; differential/security tests; benchmark and leakage report; primary/baseline selection.

**Validation:** Mature pinned libraries; no custom cryptography; exact reference agreement; attackable records/transcripts retained only as safe synthetic evidence.

**Decision / gate:** **Gate V2-E — Protocol selection/privacy viability.** Select one primary protocol plus meaningful baselines only if the named privacy property, functional correctness, and feasibility survive.

**Dependencies:** Constructive Gate V2-D.

**Cost:** AI-token High; compute Medium; storage Low–Medium.

**Stop / fallback:** Preserve the POCs and select no protocol if every candidate exposes a disqualifying oracle/leakage or cost.

### P14 — Selected private and unlinkable verifier

**Status:** Not started; blocked on Gate V2-E.

**Objective:** Implement and analyse the selected verifier to research quality.

**Supports:** RQ4–RQ6; C4/C5; evidence for Gate V2-F.

**Tasks:** Add domain separation, session binding, transcript minimisation, replay/downgrade handling, key rotation, explicit failure/collusion behaviour, compromise tests, policy/privacy attacks, cross-service unlinkability games, and adaptive-query analysis if retained. Formalise construction-specific claims where appropriate.

**Outputs:** selected verifier library/service; tests; proof/argument; threat-view and performance evidence.

**Validation:** Differential, property, security-regression, compromise, linking, and transcript tests; external primitive test vectors where available.

**Dependencies:** Constructive Gate V2-E.

**Cost:** AI-token High; compute Medium; storage Low.

**Stop / fallback:** Narrow claims to the strongest passing compromise/leakage scope; never silently downgrade.

### P15 — End-to-end reconstructable visual-semantic prototype

**Status:** Not started; blocked on P14.

**Objective:** Integrate `prompt -> generated image -> canonical semantic graph -> policy derivation -> private verification` in a scientific CLI/API.

**Supports:** RQ1–RQ6; C1–C4.

**Tasks:** Integrate versioned modules, local-only prompt/image/plaintext-graph handling, deletion/retention rules, enrolment/authentication state machines, observability without semantic leakage, error handling, and reproducible smoke mode. A UI is not required.

**Outputs:** end-to-end prototype; integration tests; deployment diagram; resource trace.

**Validation:** Local-data boundary audit; reference/private equivalence; fresh independent generations; replay/version/failure tests.

**Dependencies:** P9–P14 constructive outputs.

**Cost:** AI-token Medium–High; compute Medium; storage Medium.

**Stop / fallback:** Keep components separable and report an integration limitation rather than weaken privacy or semantic rules.

### P16 — Full held-out evaluation

**Status:** Not started; blocked on completed P15 and all prior gates.

**Objective:** Execute the frozen full manifests once and evaluate all contributions and baselines.

**Supports:** RQ1–RQ6; C1–C5; Gate V2-F.

**Tasks:** Evaluate reconstruction stability, extraction fidelity, M/T policy behaviour, random/near negatives, K0–K3 attacks, acceptance-region security, offline attacks, template inference, database and service/key/share compromise, linking/domain separation, adaptive queries if retained, model drift, protocol cost, VSA baselines where feasible, and text-only ablation.

**Outputs:** immutable raw/aggregate evidence; complete failure/uncertainty analyses; audit trail.

**Validation:** Sealed-test access log; frozen configs/hashes; independent reproduction checks; no result-dependent exclusions or retuning.

**Decision / gate:** **Gate V2-F — End-to-end evidence/paper story.** Decide whether the evidence supports a PETS privacy paper, a narrowed/negative paper, or stop.

**Dependencies:** Constructive V2-N through V2-E and completed P15.

**Cost:** AI-token High; compute High; storage High but bounded.

**Stop / fallback:** Preserve all results. A failed V2-F cannot be repaired on the held-out test; redesign requires v3 and new data.

### P17 — Statistical analysis and evidence consolidation

**Status:** Not started; blocked on P16.

**Objective:** Produce reproducible figures, tables, uncertainty estimates, and claim-to-evidence mappings without changing frozen decisions.

**Tasks:** Consolidate primary/secondary outcomes, family/account-cluster uncertainty, multiplicity and sensitivity analyses, attack curves, leakage/compromise tables, resource costs, negative results, and machine-readable claim provenance.

**Outputs:** final figures/tables; statistics report; claim-evidence matrix; result hashes.

**Validation:** Independent recomputation from immutable results; table/figure cross-checks; no unsupported causal or human inference.

**Dependencies:** P16.

**Cost:** AI-token Medium; compute Low–Medium; storage Low.

### P18 — PETS manuscript

**Status:** Not started; blocked on Gate V2-F and P17.

**Objective:** Build the evidence-backed manuscript.

**Tasks:** Lead with exact reproduction versus approximate semantic reconstruction, then the induced acceptance-region and private-verification problems. Position C3/C4 as expected primary PETS contributions and C1/C2 as enabling application/mechanism contributions; differentiate VSA prominently and fairly; describe both VSA baselines; report all gates and negative results; align every claim/citation/number with evidence; include practicality, limitations, ethics, and future human study without human claims or password-replacement superiority claims.

**Outputs:** submission manuscript; appendix/supplement; rebuttal-risk audit.

**Validation:** Claim-evidence and citation audit; anonymisation; no novelty overclaim; no invented v2 number.

**Dependencies:** Constructive/narrowed Gate V2-F and P17.

**Cost:** AI-token High; compute Low; storage Low.

### P19 — Research artifact

**Status:** Not started; blocked on stable P18 evidence.

**Objective:** Package reproducible smoke and full modes with minimal sensitive/large data.

**Tasks:** Provide acquisition instructions, hashes, licences, manifests, configs, scripts, environment capture, expected outputs, runtime/storage estimates, safe synthetic tests, and artifact-evaluation guide.

**Outputs:** versioned artifact package and archival metadata.

**Validation:** Clean-environment smoke reproduction; hash/licence/secrets scan; documented optional/full resources.

**Dependencies:** P15–P18.

**Cost:** AI-token Medium; compute Medium; storage Medium.

### P20 — PETS submission audit

**Status:** Not started; blocked on P18/P19.

**Objective:** Perform the final novelty, privacy, threat-model, evidence, citation, artifact, ethics, open-science, AI-use, anonymisation, and page-budget audit.

**Tasks:** Re-run consistency/reproducibility checks; verify every gate and limitation; check venue requirements; freeze submission and artifact identifiers; record the final decision.

**Outputs:** submission-readiness report; final manuscript/artifact checkpoint or explicit stop.

**Validation:** No unresolved critical claim/evidence/citation/security issue; clean build and artifact smoke; branch/tag policy documented.

**Dependencies:** P18 and P19.

**Cost:** AI-token Medium; compute Low; storage Low.

**Decision / gate:** Final enforcement of **Gate V2-F — End-to-end evidence/paper story.** No submission if the paper story exceeds the evidence.

## Active gate order and anti-bypass rule

```text
Gate V2-N — Novelty viability (passed with narrowing, P8)
        ↓
Gate V2-A — Failed monolithic extractor path (immutable P9-v2 result)
        ↓ explicit v3 reframe, not a bypass
Gate V3-A1 — Modular extraction viability
        ↓
Gate V3-A2 — Independent reconstruction viability
        ↓
Gate V2-B — Policy-aware semantic viability
        ↓
Gate V2-C — Acceptance-region security viability
        ↓
Gate V2-D — Private-functionality viability
        ↓
Gate V2-E — Protocol selection/privacy viability
        ↓
Gate V2-F — End-to-end evidence/paper story
```

No later expensive phase may bypass its corresponding gate. P9-v3A passes no empirical gate. P9-v3B remains the next empirical phase only after explicit authorisation and resolution of its annotation prerequisite; P9-v3C remains blocked on constructive V3-A1; P10 is blocked until constructive V3-A2. Cryptographic implementation remains blocked until a constructive Gate V2-C and a defined Gate V2-D functionality. Participant research is outside P0–P20.
