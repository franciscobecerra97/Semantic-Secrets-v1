# P9-v3A modular visual-semantic extraction reframe

Status: complete design and preregistration phase on 2026-08-25. No v3 model, image, inference, authentication experiment, or cryptographic implementation was run.

## What P9-v2 tested and what failed

The frozen P9-v2 path was effectively:

`image -> general VLM -> complete exact credential JSON -> strict validator`

The VLM was responsible for both visual inference and every serialization invariant: exact keys, closed labels, node identifiers, references, inverse relations, counts, array termination, and valid JSON. Moondream2 returned non-JSON text. SmolVLM2 returned malformed, truncated JSON. Each candidate therefore produced one invalid result on its first formal validation fixture. With 32 planned validation fixtures, even 31 later valid results would yield `31/32 = 0.96875`, below the frozen `0.98` requirement.

P9-v2 correctly failed its conjunctive gate, but its evidentiary scope is narrow. Full atom precision/recall/F1, bootstrap intervals, determinism, error strata, and full-set latency were not measured. The result rejects the frozen monolithic VLM-to-credential-JSON architecture. It does not establish that every visual-semantic extractor is impossible.

Serialization correctness and semantic correctness are independent. A model can describe the image accurately while emitting malformed syntax; it can also emit perfect JSON containing hallucinated facts. The new design measures and controls those failure classes separately.

## New architecture

P9-v3 uses:

`I = G(P,r)`

`O = Observe(I)`

`S = C(O)`

`(M,T) = Pi(S)`

`Observe` is a modular perception pipeline. It emits bounded evidence: detections with category, box and component-local confidence; attributes; unary actions; binary interactions; scene hypotheses; component revision and provenance; abstentions; and typed component failures. It never authors a credential graph.

`C` is a deterministic semantic compiler. It validates versions and provenance, applies frozen thresholds and duplicate rules, assigns canonical identifiers, normalises inverse edges, derives counts and geometry, sorts every collection, and returns either a valid graph or a valid typed failure. It never returns malformed JSON. Models infer evidence; code enforces syntax and graph invariants.

`Pi` retains the mandatory/tolerant policy interface, but P9-v3A neither implements nor tunes it. P10 remains blocked.

## Visual language and credential language

`L_visual-v3.0.0` is the broad candidate observation language in `experiments/v3/config/visual_observation_v3.json`. It contains entities, colour/size/material/pattern attributes, unary actions, binary interactions, derived geometry, counts, and scenes.

`L_cred` is a strict subset. An atom type enters `L_cred` only if a frozen pipeline passes its independent P9-v3B capability thresholds in both the controlled and naturalistic validation strata. Reconstruction and authentication results cannot promote a type. Enrolment may be ineligible when too few eligible facts remain.

Actions and relations are not silently discarded, and they are not compulsory. Unary actions and binary interactions receive their own gates. Geometry relations and counts are separately evaluated even though the compiler derives them, because their end-to-end accuracy depends on perception. Gate V3-A1 requires entities plus at least two additional eligible types, including at least one structural type from count, geometry, unary action, or binary interaction.

## Two frozen candidate pipelines

The shortlist is literature-driven and limited to two scientifically distinct pipelines.

1. `v3-gdino-siglip2`: Grounding DINO Tiny localises open-set entity labels. SigLIP 2 Base scores closed attribute/action labels on crops, interactions on ordered pair crops, and scene labels on the full image. It tests a compositional detector-plus-contrastive hypothesis. Grounding DINO was designed for language-conditioned open-set detection, while SigLIP 2 provides released vision-language encoders with improved classification and localization capabilities.
2. `v3-sgtr-siglip2`: SGTR proposes entities and directed predicate triplets through end-to-end scene-graph assembly. SigLIP 2 independently supplies attributes and scene scores. It tests whether a graph-native perception model provides useful interaction structure that independent crop scoring misses.

Exact repository/model revisions and licences are frozen in the observation config. SGTR code is Apache-2.0, but the official checkpoint must have its own terms, URL, size, and SHA-256 recorded before acquisition. Missing or incompatible checkpoint terms are a pipeline failure; they do not authorize a replacement. No candidate may be replaced after validation output.

The first pipeline is expected to require roughly 2.1 GiB of downloads, 6-10 GiB peak VRAM, and 2-12 seconds per image. The second is expected to require roughly 2-3 GiB, 10-16 GiB VRAM, and 4-20 seconds per image. These are planning estimates, not measurements. Compiler tests and tiny plumbing checks fit the current development machine; full inference may use one documented GPU with at most 24 GiB VRAM and 32 GiB RAM. No secret-bearing cloud service is allowed.

## New capability dataset

P9-v3B will use 240 new images under `cap-v3-*` identifiers; none exists in P9-v3A.

- Stratum A: 120 deterministic, project-authored geometric/composited fixtures. These isolate boxes, duplicates, counts, inverse relations, graph normalization, malformed observations, and serialization behavior.
- Stratum B: 120 naturalistic images generated later from new project-authored prompts by the intended local authentication generator. Two project researchers independently label visible facts before perception output exists; disagreements are adjudicated and agreement is reported. This is technical annotation of non-sensitive research images, not a participant study.

Each stratum contains 24 independent semantic scenario families, with 12 families/60 images for development and 12 families/60 images for validation. Families, not images, are the split and bootstrap unit. Every evaluated atom type requires at least 60 validation positives and 60 applicable negatives in each stratum. Provenance, licence, prompt hash, generator revision, seed, image hash, and annotation version are mandatory. P9-v3C must use a separate reconstruction dataset.

## Compiler engineering gate

Compiler correctness is an engineering invariant, not a perception score. Before Gate V3-A1, at least 320 frozen tests must cover schema/version handling, boxes, duplicates, identifiers, inverse and geometric relations, derived counts, sorting, limits, typed failures, canonical serialization, repeatability, and seeded properties. Expected graphs and typed failures must match exactly; result-schema validity and byte-identical repeatability must be 100%; malformed outputs must be zero. Any failure blocks the gate regardless of model accuracy.

## Perception metrics and eligibility

Entities use category-equal one-to-one matching at IoU at least 0.50. Attribute/action/interaction metrics are reported both end-to-end and conditional on matched entities; eligibility uses end-to-end results. Counts and geometry are scored after compilation. Precision, recall, F1, coverage, abstention, failure, repeatability, component-local calibration diagnostics, latency, RAM, and VRAM are reported.

For an atom type to enter `L_cred`, each validation stratum must independently meet:

- precision at least 0.90 with family-bootstrap lower bound at least 0.85;
- recall at least 0.70 with lower bound at least 0.60;
- F1 at least 0.80 with lower bound at least 0.70; and
- coverage at least 0.75 with Wilson lower bound at least 0.65.

These asymmetric thresholds make false semantic assertions harder than omissions while allowing explicit abstention. They are capability thresholds, not security claims. The 60-image/12-family validation cells give auditable rate resolution and family-level uncertainty without pretending repeated images are independent.

## Gates and phase order

P9-v3A is this architecture and preregistration only.

P9-v3B will test component capability after explicit authorization. Gate V3-A1 passes only if all compiler invariants pass and at least one frozen pipeline meets operational/resource/repeatability rules and yields a meaningful `L_cred`: entity plus at least two further types, including one structural type. If no pipeline passes, the visual constructive path stops or requires another explicitly preregistered scientific reframe. P9-v3C may not run.

P9-v3C is a future independent-reconstruction study. Gate V3-A2 requires eligible enrolment, FRR, targeted-neighbour FAR, random FAR, same-versus-near AUC, and a material paired improvement of `M/T` over the strongest baseline under a separate freeze. Passing V3-A2 would establish only technical reconstruction viability. It would not establish memorability, entropy, attack resistance, or privacy.

P10 remains blocked until constructive Gate V3-A2. C1-C4 remain the scoped candidate claims; none receives new empirical support from P9-v3A.

## Evidence integrity

P9-v2 is immutable negative evidence. This reframe creates only `experiments/v3/` identifiers and appended governance. It does not modify, rerun, reinterpret as a pass, or select candidates from P9-v2 validation outcomes. The v3 rationale comes from separating learned perception from deterministic representation construction and from primary literature on open-set detection, contrastive vision-language encoders, and scene-graph generation.
