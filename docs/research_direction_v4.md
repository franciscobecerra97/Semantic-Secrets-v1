# Research direction v4: semantic distinctions and authentication

Approved: 26 October 2026, decision DIRECTION-V4-01. This is the active direction, not a completed experiment or a frozen executable preregistration. AGENT.md governs authority; PLAN.md governs sequencing; docs/phase_workflow.md governs authorization.

## Central question

> Can users reconstruct a semantic credential reliably while keeping related but unauthorized alternatives distinguishable, and how do perception and normalization affect that balance?

The present experiments operationalize reconstruction with researcher-authored concepts and independent generations. They do not involve users or establish human recall or usability.

Working title: **Semantic Secrets: Reconstruction and Security-Relevant Semantic Distinctions in Visual Authentication**.

Keep the long-term authentication goal. The immediate study asks which differences survive perception, canonicalization and matching, and which disappear in ways that create accepted attacker alternatives. Extraction accuracy is supporting evidence, not an authentication-security claim.

## Contribution hypotheses and continuity

New identifiers avoid rewriting the scientific meanings of historical C1-C4.

| ID | Proposed contribution | Evidence needed |
|---|---|---|
| V4-C1 | A methodology connecting perception and normalization errors to authentication outcomes | Common task/compiler/evaluator, versioned interventions, reference and failure accounting, fresh reconstruction and attack trials |
| V4-C2 | An empirical account of which semantic distinctions survive or collapse | Paired pipeline comparison; identity, attribute binding, count, interaction and spatial contrasts; family-level uncertainty |
| V4-C3 | Reconstruction and finite-budget attacker outcomes under frozen acceptance rules | Independent enrolment/reconstruction, fixed policy/baselines, specified K0-K3 knowledge, attack costs/budgets, no held-out tuning |

These are hypotheses, not novelty or outcome claims. P8's earlier novelty gate applies to its earlier composition; v4 needs a focused review of its exact contribution. A model leaderboard, dataset collection, graph representation, synonym dictionary or LLM substitution alone is insufficient.

Historical C1 reconstruction and C3 acceptance-region analysis inform this study. Historical C2 mandatory/tolerant policy is a candidate mechanism and comparator, not an assumed winner. Historical C4 private verification remains a separate, deferred project goal requiring its own construction, threat model, proofs/analysis and experiments. V4-C1-C3 do not claim C4.

## The scientific pipeline

Intended concept -> independent image generation -> bounded observations -> versioned normalization -> common deterministic graph compiler -> frozen reference predicate -> reconstruction and attacker outcomes.

Photographs and controlled drawings also enter at the image stage for capability assessment. They are not automatically legitimate authentication reconstructions.

Compare one feasible generative VLM pipeline and one feasible specialized perception pipeline initially. Grounding DINO/SigLIP2 are also vision-language components; the distinction is generative extraction versus specialized perception, not VLM versus non-VLM. Exact model/service choices require prospective availability and output-interface review. Additional models require a specific unresolved question.

Models provide bounded instance-level facts. Code owns schema checks, identifiers, canonical ordering, duplicate handling and serialization. Flat bags of objects/colors/actions lose binding: red cup + blue book must remain distinguishable from blue cup + red book.

## Three image sources, distinct roles

- **Generated naturalistic images:** primary evidence for the proposed concept-to-image reconstruction workflow.
- **Controlled drawings:** isolate semantic distinctions and diagnose errors.
- **Photographs:** external visual generalization, with source/rights/training-overlap limits.

Create semantic families around identity, attribute binding, cardinality, agent-object interactions and spatial arrangement. Define controlled variations and related unauthorized contrasts within each family; split related originals, derivatives and alternatives together.

A photograph can motivate a manually authored intended concept. Generate the naturalistic version from that text specification and draw the controlled version from it. Direct image-to-image reproduction is not the primary free-language reconstruction experiment.

The author manually labels the actual visible content of each image, independently of model predictions. Keep intended concepts and observed image references separate. A generated bottle for an intended cup is a generation-fidelity failure; correctly extracting the bottle is not an extraction failure. Ambiguity and unsupported facts need explicit handling. Author re-review is not independent inter-annotator agreement.

## Normalization as a security question

Use deterministic case/format normalization and reviewed, versioned aliases in the primary arm. Canonical categories are explicit; open-ended words are not unrestricted credential semantics.

A development-time LLM may propose mappings, but the author reviews sense, context and permitted abstractions before freezing them. Distinguish aliases from broader categories: cat/kitty can be aliases in context; cat/dog -> animal is a deliberate loss of distinction. Unknowns should abstain or remain unsupported under a frozen rule.

An optional live LLM arm operates on the same cached observations. Measure correct mapping, false merges, false splits, abstention, repeatability and effects on acceptance. It must not infer new image facts or access intended labels. Freeze model/prompt/settings; temperature zero does not prove deterministic service behavior.

## API-first feasibility

Use approved API services on public or safely authorized non-secret research fixtures. Do not rent GPUs or perform local model inference in the immediate programme. API access and exact model availability are unresolved until reviewed; do not silently replace a frozen local checkpoint with a similarly named hosted model.

Record service/model identifiers, revisions when exposed, requested settings, raw responses, request/response hashes, timestamps, failures/retries, call counts, cost and observed latency. Distinguish attested identity from requested or unknown identity. Cached replay verifies downstream processing; fresh repeated calls measure hosted repeatability and drift.

API results do not establish local VRAM, model-only latency, offline reproducibility or privacy from the provider. Later approved local execution must test semantic parity as well as performance. Secret-bearing production processing remains within the trusted-client boundary for the strongest future privacy claim.

## Valid findings and progression

Separate three questions:

1. Was the measurement valid?
2. Does the tested approach support constructive authentication under the frozen criteria?
3. Does the evidence support a novel, complete paper?

A valid negative result can answer the first question without answering the second positively. Diagnostic continuation may be authorized without treating failed viability as a pass. Protocol engineering or deployment claims require their own positive prerequisites.

All failures receive diagnosis and alternatives under docs/phase_workflow.md. No automatic hypothesis rejection, approach abandonment or project termination follows an error. The author chooses among explained alternatives; frozen outcomes are preserved.

## Scope and paper boundary

Prioritize a small, credible comparison tied to authentication outcomes. Live LLM normalization, extra models and local performance are optional extensions. Private verification is deferred, not presumed achieved.

No human-subject study, natural secret-choice distribution, entropy estimate from pixels, memorability, password/passkey superiority, or deployment-ready authentication claim is authorized. Sampled attackers characterize specified distributions and budgets; they do not exhaust or prove security over the complete acceptance region.

The EuroS&P 2027 target remains: mandatory registration 25 November 2026 AoE and paper submission 2 December 2026 AoE. Readiness on 13 November is an evidence review, not a deadline-driven gate waiver. The original research must establish a security/privacy contribution; extraction comparisons alone do not establish venue fit.
