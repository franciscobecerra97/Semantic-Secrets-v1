# Semantic Secrets execution plan

Status: **v4 direction approved, 26 October 2026; execution not started.** Authority: AGENT.md and decision DIRECTION-V4-01. The current work updates documentation and manuscript framing only.

## Active objective and approval rule

Study whether perception and normalization preserve the semantic distinctions needed for technical reconstruction and resistance to accepted attacker alternatives. Proposed contributions V4-C1-C3 are defined in docs/research_direction_v4.md; privacy is a separate deferred goal.

Before **every phase/subphase**, explain what, how and why; inputs/dependencies; exact scope and outputs; models/services/data; cost/call/retry limits; checks; interpretation and alternatives. **Wait for explicit authorization.** Overall direction approval and successful completion of a prior phase are not execution authorization. Follow docs/phase_workflow.md.

On failure, preserve evidence, explain known/suspected causes, distinguish implementation/API/data failures from scientific findings, offer alternatives and obtain a decision for substantive continuation. Never automatically abandon the hypothesis or project. Do not retune frozen criteria or erase negative evidence. A pause in an affected run is not project termination.

## Current evidence and blockers

Historical P0-P7 and failed P9-v2 remain unchanged. P8's novelty pass concerns the previous composition. P9-v3.0-v3.4 freezes and preparation remain intact; its empirical branch is **paused**, not failed, passed or completed.

The prior audit found 240 v3 images, 120 controlled references, no finished naturalistic reference set or final freeze, and no formal perception result. It reported 421 passing core tests including 320 compiler cases, but reproduced a one-to-one entity-scoring defect and moved manual-script root-path errors. These defects remain unfixed. No v4 implementation, reference set, capability result, authentication policy, attacker result or private verifier exists.

Do not access the twelve sealed v1 families. Existing v3 material defaults to development/diagnostic use in v4 pending an exposure/provenance review. V4 formal data needs its own identifiers, splits and pre-output rules.

## Active phases

The following is the approved direction-level roadmap, **not approval to execute any phase**. Detailed parameters and budgets remain decisions for the corresponding explained proposal. No numerical v4 gate is invented here.

### P9-v4A - Common study contract and feasibility design

**Status:** Awaiting detailed proposal and author authorization; next phase.

**Why:** Establish a fair, security-relevant comparison before implementation or paid calls.

**Planned work:** Review exact novelty and API documentation; identify one generative VLM and one specialized perception candidate; specify common instance/attribute/relation observations, compiler interface and grounding policy; define semantic families, source strata, reference rubric, split/exposure rules, normalization arms and metric/uncertainty design. Determine support/sample-size rationale, API budget and reproducibility limits. Explain unavailable-model alternatives rather than silently substitute.

**Outputs:** Reviewable study protocol, candidate/interface table, draft schemas, author annotation instructions, task/claim map and costed pilot proposal. Exact choices require author review; no model calls, acquisition, generation or labels are produced by this design phase.

**Validation:** No answer leakage; distinct generation/extraction/reconstruction outcomes; same-image and independent-generation roles separated; exact unresolved decisions recorded. Gate V4-DESIGN means an approved design, not empirical viability.

### P9-v4B - Evaluator repair and common pipeline implementation

**Status:** Awaiting P9-v4A decisions, detailed proposal and authorization.

**Why:** Ensure the common comparison is measured correctly.

**Planned work:** Fix the one-to-one evaluator bug and moved manual roots with focused regressions; implement approved API adapters, normalization contract, compiler compatibility/versioning, provenance/cost/error records, author reference validation and shared evaluator. Use deterministic fixtures and mocked API outputs. Keep frozen historical configs/results unchanged.

**Outputs:** Reviewed code, tests, reference-authoring tools and a smoke-ready runner.

**Validation:** One prediction cannot match two reference instances; attributes/relations retain ownership; malformed/missing/API-failure cases remain counted; cached compilation is deterministic; no live API/model run. Engineering pass is not extraction success.

### P9-v4C - Small API pilot

**Status:** Awaiting implementation checks, author-completed pilot references and explicit call/data/budget authorization.

**Why:** Check hosted interface feasibility and estimate errors, support and cost before formal scale.

**Planned work:** Run a few development families with exactly approved endpoints/prompts/settings; retain all raw responses, failures and bounded retries; compare output support, repeatability, binding and cost. Use public or safely authorized non-secret fixtures. Review limited photograph/generated/drawing examples only within the approved acquisition/generation scope.

**Outputs:** Pilot report, failure diagnosis, revised protocol recommendations, exact projected formal cost and author decision. Pilot data is development-only.

**Validation:** Label blindness, provenance, complete denominators, paired task coverage, service identity limits and separation of intended versus observed image content. No renting GPUs or local model inference by default.

### P9-v4D - Formal capability data and preregistration freeze

**Status:** Awaiting pilot review, detailed proposal and authorization.

**Why:** Prevent formal results from choosing their own task, labels, criteria or favorable strata.

**Planned work:** Prepare the approved new families and three source strata; the author manually labels actual visible facts. Validate references, ambiguity rules, support, rights, duplicates and family splits. Freeze endpoints/prompts, compiler/schema, aliases, normalization arms, repeats/retries, metrics, minimum support, numeric qualification rules, uncertainty, exclusions, cost limits and raw-to-derived provenance before formal calls.

**Outputs:** Author-completed references, exposure/provenance inventory, formal manifest and hash-bound capability preregistration. No final labels are invented to complete this phase.

**Validation:** Generated naturalistic primary/controlled diagnostic/photographic external roles fixed; no cross-split family derivatives; no model-derived truth. Gate V4-FREEZE establishes readiness for authorized measurement, not a positive result.

### P9-v4E - Shared capability and graph comparison

**Status:** Awaiting V4-FREEZE and execution authorization.

**Why:** Measure which semantic distinctions survive each complete named pipeline.

**Planned work:** Run the approved formal comparison and repeat protocol; evaluate generation fidelity separately, then extraction, instance binding, counts/relations, coverage, hallucination, raw-schema failures, compiler behavior, normalization and family uncertainty. Optional live LLM arm changes normalization only on identical cached observations if approved.

**Outputs:** Immutable run records, per-stratum/per-task comparisons, eligible versus unsupported task inventory, failure analyses and claim-limited report.

**Validation:** Frozen methods and budgets, failure accounting, paired comparisons, no cross-pipeline union or favorable-case-only metrics. Review measurement validity separately from constructive semantic viability. A valid negative result is retained and explained; it does not pass old V3 gates or authorize automatic abandonment.

### P10-v4A - Reconstruction and policy design/development

**Status:** Awaiting interpreted P9-v4E evidence and a separately authorized scope.

**Why:** Connect semantic observations to acceptance rather than infer authentication from extraction F1.

**Planned work:** Propose separate fresh reconstruction families and enrolment/authentication roles; define technical enrollment failure, FRR, random and targeted contrasts. Compare a frozen exact/strict semantic reference, global overlap and the closest reproducible VSA-style policy with a system-derived mandatory/tolerant candidate where justified. Select a bounded baseline set and development-only policy/threshold rules. Add a matched direct-text control if claiming the image stage adds value.

**Outputs:** New reconstruction manifest/reference protocol, exact reference predicate and policy freeze, supported-language rules and analysis plan. Private verification remains deferred.

**Validation:** No favorable cached-positive selection, no task promotion from authentication outcomes, fixed correspondence/malformed/missing-anchor behavior, independent development/evaluation families. A diagnosed weak pipeline can be studied only under an explicitly approved bounded diagnostic scope, without a constructive viability claim.

### P10-v4B - Frozen independent reconstruction evaluation

**Status:** Awaiting P10-v4A freeze, final references and execution authorization.

**Planned work:** Evaluate fresh independent enrolment/reconstruction generations and unauthorized contrasts under the fixed predicate; distinguish generator, extractor, normalization and matcher failures. Report enrolment rejection separately from conditional FRR and unconditional success, plus targeted/random acceptance and family/account uncertainty.

**Outputs:** Reconstruction-security trade-off report with immutable pipeline/policy versions. No human memorability or sampled-attacker security conclusion follows from this stage alone.

### P11-v4A - Budgeted attacker design and freeze

**Status:** Awaiting P10-v4B interpretation, detailed proposal and authorization.

**Why:** Random or selected-neighbor FAR is not end-to-end guessing success.

**Planned work:** Define K0-K3 knowledge, source/auxiliary data, candidate interface, simple/frequency/near and justified AI-assisted/adaptive strategies, Accept/Reject feedback, duplicates, generation/extraction/verification budgets and costs. Bind target data independently of attacker development.

**Outputs:** Frozen attacker protocol, cost limits, success@1/5/10/B and censored guesses-to-success analysis. Graph-level and prompt/image attacks must be distinguished.

### P11-v4B - Finite-budget attack evaluation

**Status:** Awaiting attacker freeze and execution authorization.

**Planned work:** Evaluate only approved simulated/local targets, preserve all outcomes, report baseline-relative success/cost curves and uncertainty. Explain exactly which knowledge/distributions were tested.

**Outputs:** Bounded acceptance-region evidence and scope recommendations. Sampled attacks do not exhaust the region or establish privacy/offline resistance.

**Validation:** No target leakage or budget changes after outcomes; fixed policy, controlled oracle, complete accounting. A negative security finding triggers diagnosis and alternatives, not automatic termination or cryptographic rescue.

### P17-v4 - Evidence consolidation and scope decision

**Status:** Awaiting relevant frozen capability, reconstruction and attack evidence, plus authorization.

**Planned work:** Recompute paired/family uncertainty, failure strata, costs, figures and claim-to-run mappings; refresh novelty for the actual findings. Distinguish valid measurement, constructive viability and publication readiness.

**Outputs:** Reproducible analysis and a recommendation for a constructive, restricted or negative/measurement paper. The author approves the final scope. A narrower story must stand on complete suitable evidence, not an unfinished experiment.

### P18-v4 - Evidence-backed manuscript

**Status:** Awaiting P17-v4 scope/evidence and phase authorization. Planning-source editing is permitted under the present documentation amendment; this phase is not complete.

**Planned work:** Follow docs/eurosp2027_paper_plan.md, lead with authentication consequences of lost distinctions, report actual contributions and limitations, distinguish historical evidence, and keep privacy deferred unless independently established.

**Outputs/checks:** Anonymous IEEE manuscript, verified citations, figures tied to immutable runs, harm/availability/AI disclosures and no unsupported findings.

### P19-v4 - Research artifact

**Status:** Awaiting stable manuscript evidence and authorization.

**Planned work:** Package reproducible mocked/cached and optional API modes, versions/hashes, licensed data or acquisition instructions, raw-to-derived processing, costs and endpoint-drift limits. Separate cached reproducibility from unavailable live service reproduction.

**Outputs/checks:** Reviewed anonymous artifact, clean reproduction, secrets/rights audit. No public release or license grant without the corresponding explained authorization.

### P20-v4 - Submission audit and author decision

**Status:** Awaiting P18-v4/P19-v4 and authorization.

**Planned work:** Check every claim, reference, run, limitation, anonymity/rights/AI disclosure, final CFP/HotCRP rules, registration metadata and 13-body-page A4 PDF. Report readiness and alternatives if incomplete.

**Outputs:** Reviewable submission package or documented non-readiness. Actual registration/upload needs explicit instruction. Non-submission does not terminate the project.

## Deferred branches

- **Local parity/performance:** only after convincing API evidence and a separately explained, costed authorization. Check semantic behavior as well as resources.
- **Private verification (historical C4/P12-P16):** separate future v4-compatible plan mapping a frozen predicate to exact functionality, construction, leakage/compromise claims and evidence. No cryptography shortcut around a weak acceptance region.
- **Additional models/live LLM normalization:** optional experiments justified by a specific open question, not required to keep the main path moving.
- **Legacy P9-v3B/C:** paused; resuming requires a detailed proposal and author decision. Its original resource and semantic gates retain their old meanings.

## EuroS&P 2027 calendar

Official requirements: docs/eurosp2027_requirements.md and docs/eurosp2027_submission.json. Dates rechecked against the official CFP on 26 October. AoE is UTC-12; the date-only CFP gives no exact clock time. Internal dates below use Luxembourg calendar dates.

| Date / interval | Planning target | Required evidence / decision |
|---|---|---|
| 26 October | Document approved direction and phase-control rules | Documentation/build validation only; no experimental phase complete |
| 27 October-12 November, conditional | Propose and, only after approval, progress through bounded design/engineering/pilot/formal work | Pace determined by author approvals, labels, API feasibility and valid evidence; no promised full completion |
| **13 November** | Evidence-readiness review | Explain achieved evidence, remaining cost/dependencies and viable paper scope; author decides how to proceed |
| **24 November** | Internal registration-metadata target | Accurate title/abstract, authors, conflicts and topics |
| **25 November AoE** | Mandatory registration deadline | Actual registration only if explicitly instructed |
| **30 November** | Internal final evidence/PDF/artifact audit | Complete claim support, anonymous artifact, formatting and disclosures |
| **1 December** | Internal upload buffer | Reviewed package and explicit submission instruction |
| **2 December AoE** | Full-paper deadline | Submit only evidence-complete work; otherwise explain non-readiness and continuation options |

Thirty days to registration and thirty-seven to submission from this amendment is a high-risk schedule. Approval waits, label work and diagnosis are real dependencies; do not compress them into assumed completion. Missing this cycle is not a decision to abandon the research.

## Evidence controls and phase records

Use docs/phase_workflow.md. Each record identifies the explanation and approving instruction, phase/version, scope, limits, inputs, outputs, validation, deviations, failures and next decision. Preserve raw-to-derived hashes, APIs/model settings, labels, splits, policies and prompts. No phase approval is invented from a plan entry.

The standing checkpoint instruction recorded in the previous plan was to commit and push each completed authorized Px phase as its own checkpoint, never a partial/failed phase or force-push. Include checkpoint scope in the phase explanation; preserve unrelated user changes. This documentation amendment does not declare a phase complete or perform a commit/push.

## Archived programme reference - not active execution instructions

The following P0-P20 material is retained verbatim from the plan immediately before DIRECTION-V4-01. Completed phases, historical gates and numerical results keep their meaning. Unexecuted v3 and old downstream tasks are paused/deferred reference; wording such as "next", "active", "stop" or "execute" below applies to that prior programme only. It cannot override the v4 roadmap or the author's explain-and-authorize/failure-diagnosis rules above. No archived gate is relabelled as passed.

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
5. Historically preserved two-human model-blind annotation and recorded the unconfirmed second annotator as a blocker; P9-v3A.2 later superseded only this methodology before any output.
6. Created v3.1 configs/addendum without modifying the meaning of v3.0.0.

**Outputs:** `docs/p9_v3_preexecution_audit.md`; `docs/formal_specification_v3_1.md`; `experiments/v3/config/preregistration_v3_1.json`; `experiments/v3/config/visual_observation_v3_1.json`; v3.1 config tests; governance, literature, bibliography, and manuscript amendments.

**Validation:** Primary-source traceability; exactly two final pipelines; support arithmetic; unchanged 320-case compiler floor and Gate language requirement; JSON/CSV/BibTeX/LaTeX checks; P9-v2 protection; no weights/images/outputs.

**Decision / gate:** No empirical gate passed. The executable shortlist is exactly `v3.1-gdino-siglip2` and `v3.1-egtr-siglip2`.

**Dependencies:** Immutable P9-v3A commit `8e44caa`.

**Stop / fallback:** Historical v3.1 text blocked image creation on an annotation resource; P9-v3A.2 removes that mismatched human-resource gate. Do not run perception inference until the project-authored scenarios, images, manifest, and support opportunities are audited and frozen. Do not restore SGTR, add another pipeline, or change hardware for semantic outcomes after validation.

## P9-v3A.2 — Project-authored ground-truth correction

**Status:** Completed prospectively on 2026-08-28 before any P9-v3B image, weight, or model output. Documentation, schema, and fail-closed preparation only; no experiment authorised.

**Objective:** Correct the accidental human-annotation dependency while preserving model-blind ground-truth separation and every frozen scientific parameter.

**Method:** Retain the 240-image manifest and v3.1 support-opportunity design. For each final controlled/naturalistic image, create a versioned project-authored reference scene specification containing exact closed labels, normalized reference boxes, and semantic atoms. Link every positive/applicable-negative opportunity deterministically to that specification. Audit all identifiers, hashes, splits, boxes, scopes, polarities, and frozen per-type/per-stratum/per-split counts, then bind the manifest, scenarios, opportunities, and active config hashes in `ground-truth-freeze-v3.2.0` before any perception inference. No human participant, human annotator, agreement/adjudication step, or model-derived label is part of P9-v3B.

**Outputs:** `docs/formal_specification_v3_2.md`; `experiments/v3/config/preregistration_v3_2.json`; v3.2 manifest/scenario/freeze/authorization schemas and tests; updated runtime guards and RunPod procedures; decision `P9-v3A.2-00`.

**Unchanged:** The exact two v3.1 pipelines, model revisions, preprocessing, resolution, labels, threshold semantics, metrics, Gate V3-A1, hardware/resource limits, dataset/image/family/split counts, opportunity counts, compiler, and phase dependency chain.

**Execution boundary:** This correction does not authorise image generation, acquisition, smoke, development inference, validation, P9-v3C, P10, or cryptography. Model acquisition may be separately authorised without a ground-truth freeze; any inference requires the complete ground-truth freeze, and formal validation additionally requires explicit authorization plus every existing model/threshold/GPU/commit/container record.

### P9-v3A.3 — Prospective development-threshold calibration freeze

**Status:** Completed prospectively on 2026-08-29 before any capability image, perception-model acquisition, score capture, fitted threshold, or validation output. Engineering and methodology only; no experiment authorised.

**Objective:** Supply the deterministic selection rule required by v3.0/v3.1 “fit on development, then freeze” language without rewriting the historical freezes or changing Gate V3-A1.

**Method:** Use the fixed inclusive grid `0.00,0.01,...,1.00`. Capture development-only threshold-independent Grounding DINO, EGTR, and complete SigLIP score records with exact scope/vocabulary/prompt/crop/model/config provenance. Fit entity independently per pipeline from entity opportunities, freeze entity scopes, fit EGTR predicate/connectivity jointly from binary-interaction opportunities, and fit each SigLIP threshold/margin pair independently from its own task. Rank candidates by the exact both-strata preferred criterion and lexicographic objective in `preregistration_v3_3.json`; use its deterministic recorded fallback when no preferred candidate exists. Count and geometry remain compiler-derived and cannot tune entity thresholds. Validation artifacts and authentication/reconstruction outcomes are forbidden.

**Outputs:** `docs/formal_specification_v3_3.md`; `experiments/v3/config/preregistration_v3_3.json`; fixed smoke settings; development score/manifest/entity-scope/settings/report/freeze schemas; capture, fitting, replay, inventory, formal-guard, RunPod, and deterministic tests; decision `P9-v3A.3-00`.

**Unchanged:** Models, revisions, preprocessing, resolution, labels, image/support counts, compiler, metrics, Gate V3-A1 criteria and intervals, resource limits, and phase dependencies.

**Execution boundary:** The complete workflow is ground-truth freeze → development entity-score capture → entity fit/scope freeze → downstream-score capture → offline component calibration → integrated development replay → `threshold-freeze-v3.3.0` → formal authorization → validation → repeat → Gate V3-A1. V3.3 authorises none of those inference stages by itself.

### P9-v3B — Modular component capability and `L_cred` eligibility

**Status (2026-10-26):** Data preparation in progress; formal perception evaluation not started. All 240 final images, prompt/render plans and 120 controlled references exist under `artifacts/downloads/p9_v3`. Author the remaining 120 naturalistic references without perception predictions, audit final manifest/support opportunities and create `ground-truth-freeze-v3.2.0`. Correct the entity-scoring and moved manual-path defects identified in the current audit before calibration/evaluation. The human-resource and threshold-method blockers are resolved by v3.2/v3.3. Model acquisition and inference retain their explicit authorization requirements; no inference precedes the ground-truth freeze. The remote-generation v3.4 amendment records unattested actual weights/settings.

**Prepared execution boundary (updated 2026-08-29):** `prototype/semantic_secrets/v3/` implements the frozen compiler. `experiments/v3/runtime/` supplies deterministic dataset/freezing tools, persistent isolated adapters, threshold-independent development score capture, exact staged v3.3 fitting and offline replay, content/provenance inventories, complete validation metrics/uncertainty/independent-pipeline `L_cred`, Gate evaluation, and formal guards. `infra/runpod/` supplies the pinned dual-environment image and executable order. The compiler matrix passes 320/320 locally and must pass again in the locked image. This preparation created no image, acquired no weight, ran no model, selected no empirical threshold, started no P9-v3B experiment, and passed no gate. EGTR artifact terms/layout/base-transform provenance remain acquisition-time fail-closed checks.

**Objective:** Test perception and compiler capability on new controlled and naturalistic data before any reconstruction/authentication study.

**Tasks:** With explicit authorization, author the frozen `cap-v3-*` images, project reference scenarios, and deterministic support opportunities without perception outputs; audit and freeze their hashes; acquire only the two v3.1 pipelines after licence/hash checks; run bounded smoke only after the ground-truth freeze; freeze development thresholds; execute validation and repeat; compute per-type/stratum support, metrics, uncertainty, measured resources, and exact compiler checks.

**Outputs:** immutable manifests, observations, compiler cases/results, aggregate report, eligible `L_cred` per complete pipeline, and Gate V3-A1 decision.

**Decision / gate:** **Gate V3-A1 — Modular extraction viability.** Pass only under the complete conjunction formed by historical `preregistration_v3.json` plus prospective `preregistration_v3_1.json`. Do not union eligible types across pipelines. Installed GPU capacity is irrelevant; measured pipeline consumption is gated.

**Dependencies:** Complete P9-v3A.1–P9-v3A.3 and explicit instruction. Image creation has no human-resource dependency. Any model inference additionally requires the complete `ground-truth-freeze-v3.2.0`; formal validation requires the provenance-bound `threshold-freeze-v3.3.0` plus every acquisition, GPU, commit, container, authorization, and empty-output guard.

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

**Decision / gate:** **Gate V2-F — End-to-end evidence/paper story.** Decide whether the evidence supports an original EuroS&P security/privacy paper under the selected scope, a separately justified narrowed/negative paper, or stop.

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

### P18 — EuroS&P manuscript

**Status:** Not started; blocked on Gate V2-F and P17.

**Objective:** Build the evidence-backed manuscript.

**Tasks:** Follow `docs/eurosp2027_paper_plan.md` and the supplied IEEE template. Lead with acceptance-region security under approximate reconstruction, state the attacker and finite-budget success event early, then analyze private verification separately. Position C3/C4 as expected principal security/privacy contributions and C1/C2 as enabling application/mechanism contributions; differentiate VSA prominently and fairly; describe both VSA baselines; report all gates and negative results; align every claim/citation/number with evidence; include practicality, limitations, ethics, and future human study without human claims or password-replacement superiority claims.

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

### P20 — EuroS&P submission audit

**Status:** Not started; blocked on P18/P19.

**Objective:** Perform the final novelty, privacy, threat-model, evidence, citation, artifact, ethics, open-science, AI-use, anonymisation, and page-budget audit.

**Tasks:** Re-run consistency/reproducibility checks; verify every gate and limitation; recheck the EuroS&P 2027 CFP/HotCRP and official dates; verify mandatory registration, complete author/COI/topic metadata, anonymous artifact hosting, no concurrent overlap, A4 venue-template layout, 13 body pages, body harm analysis, Data Availability and anonymous AI-use acknowledgments; freeze submission/artifact identifiers and record the final submit-or-stop decision. A passed formatting check does not satisfy missing research evidence.

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

No later expensive phase may bypass its corresponding gate. P9-v3A/P9-v3A.1/P9-v3A.2 pass no empirical gate. P9-v3B remains the next empirical phase only after explicit authorisation and the required project-authored model-blind ground-truth freeze; P9-v3C remains blocked on constructive V3-A1; P10 is blocked until constructive V3-A2. Cryptographic implementation remains blocked until a constructive Gate V2-C and a defined Gate V2-D functionality. Participant research is outside P0–P20.
