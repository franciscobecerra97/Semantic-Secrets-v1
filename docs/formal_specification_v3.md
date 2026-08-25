# Formal specification v3: modular visual-semantic extraction

Status: P9-v3A freeze. This document specifies a future capability and reconstruction design; it reports no v3 result.

## 1. System functions

For remembered concept `C*`, reconstruction prompt `P`, generator randomness `r`, generator `G`, observation pipeline `Observe`, compiler `C`, and later policy derivation `Pi`:

`I = G(P,r)`

`O = Observe(I)`

`R_C = C(O)`

`R_C = Graph(S) or TypedFailure(code, audit)`

`(M,T) = Pi(S)` only when `R_C = Graph(S)` and enrolment is eligible.

The prompt and pixels are reconstruction inputs, not entropy. `Observe` is learned perception. `C` is deterministic representation construction. `Pi` is future training-only policy derivation. No function may infer a privacy property from serialization or hashing.

## 2. Observation object `O`

`O` is versioned and contains image identity/hash, pipeline identity/revision, component events, and zero or more typed observations:

- detection `(local_id, category, bbox, confidence, component_id, component_revision)`;
- attribute `(detection_id, attribute_type, value, confidence, provenance)`;
- unary action `(detection_id, action, confidence, provenance)`;
- binary interaction `(source_detection_id, interaction, target_detection_id, confidence, provenance)`;
- scene hypothesis `(value, confidence, provenance)`.

A component event records `ok`, `abstain`, or a typed failure plus elapsed time and memory. Confidence is meaningful only inside the producing component's declared score domain. Cross-component comparisons and calibrated-probability claims are forbidden unless a later development-only calibration version explicitly supplies evidence.

Repeat equality uses the canonical evidence projection: confidence is rounded to six decimals and evidence collections are sorted; volatile timing, memory, timestamps, and host paths are excluded. Resources remain reported separately and may never affect semantic equality.

`L_visual-v3.0.0`, fields, labels, bounds, and component revisions are exactly those in `experiments/v3/config/visual_observation_v3.json`.

## 3. Compiler `C`

`C` is a total function over bytes: it returns either a schema-valid `Graph(S)` envelope or a schema-valid `TypedFailure` envelope. Parser failure, exceptions, and unsupported versions are converted at the outer boundary to typed failures. Malformed JSON is never an output.

The compiler executes this fixed order:

1. parse and validate observation/version/provenance;
2. validate component-local score metadata and predeclared thresholds;
3. apply explicit abstentions and below-threshold omissions;
4. validate labels and normalized positive-area boxes;
5. resolve same-category duplicates at IoU at least 0.80 using confidence, smaller area, then lexicographic provenance;
6. reject dangling references, ambiguous identities, undeclared components, and more than eight accepted credential entities;
7. assign canonical IDs after category/box ordering;
8. attach eligible attributes/actions/interactions;
9. derive counts only from accepted nodes;
10. derive geometry only from accepted boxes under the frozen numeric rules;
11. normalize inverse edges and collapse exact duplicates;
12. sort and serialize canonical UTF-8 JSON.

Counts are never authored by a model. Right/below/contains are inverse-normalized. Unknown labels fail; known but Gate-V3-A1-ineligible types are omitted from the credential with an audit event. Silent truncation and syntax repair are forbidden.

## 4. Graph and atom forms

For successful compilation:

`S = (V, A, U, B, Q, Z)`

where `V` is the canonical entity set, `A` attributes, `U` unary actions, `B` binary interactions or derived spatial relations, `Q` derived count buckets, and `Z` scene facts.

Canonical atom forms are:

- `entity(node, category)`;
- `attribute(node, attribute_type, value)`;
- `unary(node, action)`;
- `binary(source, interaction_or_relation, target)`;
- `count(category, bucket)`;
- `scene(value)`.

Bounding boxes and confidence/provenance remain audit metadata, not credential atoms. Exact output schemas and sorting are implemented from the machine-readable config; the implementation may not invent a repair or tie-break.

## 5. `L_visual` and `L_cred`

`L_visual` is the complete candidate atom language. Let `type(a)` identify the atom family and, for attributes, the named attribute subtype. For pipeline `p`, stratum `d`, and type `t`, let `Eligible(p,d,t)` mean that every preregistered precision, recall, F1, coverage, support, and uncertainty check passes on P9-v3B validation.

`Eligible(p,t) = Eligible(p,A,t) and Eligible(p,B,t)`.

`L_cred(p) = { a in L_visual : Eligible(p,type(a)) }`.

Pooled performance cannot rescue a failed stratum. Reconstruction or authentication outcomes cannot add a type. Entity must be eligible. Gate V3-A1 additionally requires at least two other types, including one of count, geometry relation, unary action, or binary interaction. Action and interaction are independently eligible, neither mandatory nor discarded.

If compilation succeeds but too few eligible facts exist for the future policy, enrolment is ineligible. The system must not weaken `M` or substitute an unvalidated type.

## 6. Compiler invariants versus perception estimands

Compiler invariants require exact correctness: graph/failure oracle match, valid result schema, canonical ordering, byte-identical repeatability, derived counts/geometry, duplicate handling, and zero malformed output across at least 320 cases. One failure blocks V3-A1.

Perception is statistical. Entities match category-equal ground truth one-to-one at IoU at least 0.50. Dependent facts match only after entity correspondence. End-to-end precision/recall/F1 controls eligibility; conditional metrics diagnose whether errors arise from localization or typing. Typed failures and invalid observations count every reference fact as a false negative. Abstentions reduce recall and coverage but are not crashes.

Rates use Wilson 95% intervals. Metric intervals use 5,000 family-cluster bootstrap samples with seed `925032`. Each type must pass separately in both strata. Exact thresholds are machine-readable in `preregistration_v3.json`.

## 7. Dataset and isolation

The future P9-v3B dataset has 240 new `cap-v3-*` images:

- A: 120 controlled geometric/composited fixtures;
- B: 120 naturalistic local text-to-image outputs representative of the authentication generator.

Each stratum has 24 semantic families, five images per family, divided at the family level into 60 development and 60 validation images. Labels are fixed before model output. Validation is used once for gating. No v1 or v2 image, manifest, output, threshold, or held-out family is a v3 datum. P9-v3C uses separate data.

## 8. Gate V3-A1

For pipeline `p`, `V3-A1(p)=1` iff:

- every compiler invariant passes;
- pipeline failure point rate is at most 0.05 and Wilson upper bound at most 0.10;
- validation observation and graph repeat equality are each at least 0.95 with Wilson lower bound at least 0.90;
- peak VRAM is at most 24 GiB, peak RSS at most 32 GiB, median latency at most 30 seconds/image, and p95 at most 60 seconds/image; and
- `L_cred(p)` includes entity, at least two other types, and at least one structural type.

Gate V3-A1 passes iff one frozen pipeline passes. Candidate unioning is forbidden: eligible types from different pipelines may not be combined into a synthetic survivor.

## 9. Future `Pi`, reference acceptance, and Gate V3-A2

The `M/T` interface is preserved, not implemented. A future `Pi` may use only development statistics and Gate-V3-A1-eligible types. `M` contains mandatory anchors; `T` contains bounded-tolerance secondary facts. Insufficient anchors make enrolment ineligible.

P9-v3C must freeze its own graph correspondence, `Pi`, tolerant similarity, threshold selector, baselines, independent-generation roles, and new data before output. Gate V3-A2 then requires the exact eligible-enrolment, FRR, targeted-neighbour FAR, random FAR, AUC, and paired-improvement bounds in `preregistration_v3.json`.

V3-A2 is a technical reconstruction gate, not a security or privacy result. P10 is blocked until V3-A2 passes. C1-C4 remain candidate claims subject to all later gates.

## 10. Stop, cache, and revision rules

All artifacts are versioned and content-addressed by SHA-256; overwrite is forbidden. Failures, abstentions, exclusions, component identities, score domains, thresholds, resources, and deviations are retained. Large model/image artifacts stay outside Git.

Licensing ambiguity fails closed. Smoke is limited to two development images per pipeline and cannot tune anything. No candidate replacement follows validation output. A compiler, label, threshold, NMS, geometry, dataset, or gate change creates a new version before affected validation output. Exact logical futility may stop a conjunctive run only with best-case arithmetic and a list of unestimated metrics.

P9-v2 remains a failed immutable experiment. P9-v3A does not rerun, repair, or reinterpret it.
