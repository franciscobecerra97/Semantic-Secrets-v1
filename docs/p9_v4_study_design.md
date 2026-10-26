# P9-v4 common evaluation: approved direction, pending protocol

Status: direction approved on 26 October 2026; detailed phase proposal, endpoint selection, implementation, data acquisition and experiment execution await authorization. No numeric v4 gate, sample size, endpoint or budget is frozen by this document.

## 1. Comparison and estimands

Start with one generative VLM and one specialized perception pipeline, chosen for verified API access and task support. Compare complete named pipelines on identical inputs. Do not infer universal architectural superiority from two models. Preserve P9-v2 as a bounded historical direct-JSON failure; never pool it with the new comparison.

Common path: image -> adapter observations -> normalization -> deterministic compiler -> shared graph evaluator. Reuse v3 components only after interface and correctness review. A revised compiler/schema receives a new version; existing compiler goldens/configurations stay untouched.

The primary graph must retain entity instances, attribute ownership, action/relationship subject and object, and counts. Flat word arrays may be diagnostic outputs but cannot establish graph binding.

Define a shared semantic task and an explicit grounding task. The contract must decide whether normalized boxes are required for every arm or evaluated as a separate declared extension. Missing grounding is reported as unsupported/failure under that task, never silently dropped. Geometry cannot be inferred from absent boxes. No advantage from hidden per-image reference objects, expected counts, intended prompts or labels: extractors receive the same allowed public ontology/task context and the image.

Raw-output schema compliance, adapter validity, compiler validity, semantic fidelity, coverage and abstention are separate quantities. Converting a failure into valid typed JSON does not count as successful perception. No reference-assisted JSON/semantic repair. Any automated parsing repair is predefined, logged and counted.

## 2. Data and labels

Generated images are the primary workflow stratum; controlled drawings diagnose distinctions; photographs test external generalization. Report each stratum separately. Fix weighting and primary/secondary endpoints before formal results; never promote a favorable stratum afterward.

Candidate families:
- object identity: dog beside car versus cat beside car;
- attribute binding: red cup/blue book versus blue cup/red book;
- counts: one dog versus two;
- interactions: person holding cup versus person beside cup on table;
- spatial relations: cat on chair versus cat under chair.

Use these as examples, not an already selected dataset. P9-v4A must define the actual semantic inventory, complexity, support and negatives. Photograph source selection must address permission, personal-data handling, redistribution, duplicates and known/unknown training overlap. No collection of participant authentication behavior or new participant study is authorized.

Maintain separate records for intended concept, actual final-image content, provenance, family, source stratum, variant, exposure and split. References are manually authored by the project author without perception predictions. Provide a rubric and validation tool later; never fabricate final references. Delayed self-review is useful but not an independent annotator.

Keep originals, generated/procedural derivatives, perceptual near-duplicates and close security contrasts in one family partition. Authentication development and final evaluation use separate families from capability tuning as specified prospectively. The twelve sealed v1 families remain untouched.

Existing v3 images are candidate development/diagnostic material only by default; audit prior inspection and model exposure before any approved reuse. Never describe reused inspected data as a fresh held-out v4 test. Preserve its hashes, labels and results under the original identifiers; new manifests reference provenance rather than overwrite them.

## 3. Evaluation layers

| Layer | Measures and interpretation |
|---|---|
| Generation | Intended facts preserved, omitted or changed in the actual image; separate from perception |
| Extraction | Instance-aligned entity/attribute/relation precision, recall, F1, coverage, missing/spurious facts and binding errors |
| Graph | Schema success, typed failure, determinism on cached observations, graph correspondence and count/geometry correctness |
| Normalization | Correct aliases, false merges, false splits, unsupported terms, abstention and repeatability |
| Independent reconstruction | Enrolment eligibility/failure, agreement, technical FRR and failure strata across fresh generated instances |
| Authentication contrasts | Random/independent negative acceptance and targeted-neighbor acceptance under named trial distributions |
| Attacks | success@1/5/10/B, accounts reached, guesses to success with censored failures, duplicate proposals, API/generation/verification cost and K0-K3 knowledge |

The evaluator must enforce one-to-one object matching and explicit denominators. The audited v3 entity scorer overcounts overlapping references; fix and regression-test the relevant implementation before reusing it. Missing outputs, invalid API responses, timeouts, abstentions and unsupported tasks remain in the run accounting under the frozen rule; no favorable-case-only denominator.

Use paired comparisons on the same images and family-cluster uncertainty; images within a family are not independent replicates. Specify minimum support, sample-size rationale, uncertainty method, multiple-comparison handling, enrollment conditioning, repeat counts, exclusions and practical-effect criteria before formal evaluation.

Same-image repeats test service stability. Independent image generations test reconstruction. Merely selecting already matching cached samples is not a legitimate reconstruction trial. A claim about the image stage's added value also requires a prospectively matched direct-text control.

## 4. Normalization arms

Primary: deterministic formatting and reviewed, frozen semantic mappings. Development-only LLM assistance may propose mappings; it cannot supply final image truth.

Optional live LLM arm: consume exactly the same cached observations, with no intended labels or image-reference access; change only normalization. Pin all exposed identifiers/settings and preserve raw mapping responses. Count invalid responses, unjustified generalization and added facts. A live model is not assumed deterministic.

Record alias equivalence separately from permitted abstraction; never automatically erase identity, binding, count or role differences to improve matching. Unknown terms follow a predefined abstention/unsupported rule. Any change after formal output requires a new version and an appropriately independent evaluation.

## 5. API protocol

A model name or public demo is not proof of stable API availability or checkpoint identity. P9-v4A reviews endpoint documentation and licensing; P9-v4C tests bounded calls after separate authorization.

Before calls, approve exact endpoints, images/data disclosure, request schema, model identifiers, retry/backoff policy, budget and stopping conditions. Use no credentials in committed files. Record request identifiers where exposed, timestamps, requested and attested settings, output hashes, parsing events, failures, duplicates, costs and end-to-end latency. Report queues/network/provider overhead separately where observable; do not invent provider GPU telemetry.

If an exact modular endpoint is unavailable, explain alternatives: a documented compatible hosted pipeline with a new identity; a smaller supported task with explicit scope; or deferral of that arm. A self-hosted GPU service is not the default workaround for this API-first stage. No silent model substitution or use of old v3 gate names for API results.

## 6. Milestones and safeguards

- P9-v4A: detailed design, novelty/availability review and decisions; no calls.
- P9-v4B: authorized implementation/evaluator repairs and deterministic/mocked verification.
- P9-v4C: small approved API pilot with author labels and development-only analysis.
- P9-v4D: author-completed final labels, provenance/support audit and formal capability preregistration.
- P9-v4E: authorized frozen common capability comparison.
- P10-v4A/B: separately proposed reconstruction/policy design and development, then frozen held-out evaluation.
- P11-v4A/B: separately proposed attacker design/freeze, then finite-budget attack evaluation.

Each phase needs explanation and approval. P9-v4E may establish valid negative measurements without constructive viability. Unsupported credential types cannot be promoted by favorable authentication outcomes. Measuring a diagnosed weakness requires an explicit bounded diagnostic proposal; it is not evidence that an old gate passed.

## 7. Open decisions for P9-v4A

Choose exact API candidates; shared task and grounding contract; ontology and aliases; optional normalization arm; photograph source and rights; new family/split inventory; label rubric; endpoint repeat/drift handling; budget/cost limits; numeric support/quality criteria; baseline and policy selection rules; stage-specific freeze boundaries.

This document deliberately does not invent those choices or mark the design phase complete. The next deliverable is a detailed P9-v4A proposal for the author's authorization.
