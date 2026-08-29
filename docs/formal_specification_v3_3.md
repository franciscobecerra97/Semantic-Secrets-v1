# Formal specification v3.3 addendum: development-threshold calibration

Status: prospective P9-v3A.3 methodology freeze made before any capability image, perception-model acquisition, development score, or validation output. It supplies only the executable calibration rule absent from v3.0–v3.2. It changes no pipeline, model, revision, label, preprocessing, image/support count, compiler rule, metric, Gate V3-A1 criterion, uncertainty method, resource limit, or phase dependency.

## 1. Binding composition and boundary

P9-v3B composes v3.0.0, the explicit v3.1.0 pipeline/resource/support overrides, the v3.2.0 project-authored-ground-truth correction, and `semantic-secrets-preregistration-v3.3.0`. Historical text remains historical. The v3.3 amendment freezes only how already-declared component-local thresholds are selected from development scores.

Calibration consumes the development split and its predeclared support opportunities only. Validation and validation-repeat score artifacts are forbidden; both output directories must be empty. Authentication, reconstruction, P9-v3C, and acceptance outcomes cannot influence P9-v3B calibration. Scores and thresholds are never pooled across pipelines.

## 2. Threshold-independent score record

Development capture precedes thresholding and is content-addressed outside Git. Grounding DINO records raw logits, boxes, input IDs, the exact query/label order, target size and processor provenance, plus official postprocessor output for every candidate threshold. EGTR records every exact-intersection object proposal with object-softmax score and box, every eligible ordered-pair top predicate/connectivity score, and exact vocabulary provenance. SigLIP2 records the complete closed-label sigmoid score vector, label and prompt order, exact task template, crop rule, box/query identifiers, and scope.

Every artifact is marked `split=development`, bound to the Git commit, active config hashes, image, manifest, support opportunities, ground-truth freeze, model-acquisition manifest, and adapter source, and listed by byte length and SHA-256. These calibration records are not bounded observations or credential JSON. They exist solely to replay thresholds without rerunning a neural model.

## 3. Fixed grid and staged fit

The candidate set for every threshold and top-two margin is exactly:

```text
G = {0.00, 0.01, ..., 0.99, 1.00}
```

Comparison is inclusive. Grounding DINO uses one value as both box and text threshold and is fitted from entity opportunities only. EGTR entity threshold is fitted independently from entity opportunities only. Those entity settings are then frozen into an intermediate scope record before any downstream crop scoring.

After scope freeze, EGTR predicate and connectivity thresholds are fitted jointly over `G × G` from binary-interaction opportunities only. For each SigLIP task and pipeline, score threshold and minimum top-two margin are fitted jointly over `G × G` using only that task's opportunities. The complete label vector is sorted by descending score and then lexicographic label; acceptance requires both the top score and top-two margin to meet their candidates. Count and geometry remain compiler-derived, receive no threshold, and cannot influence entity selection.

## 4. Objective, ties, and fallback

Candidates are compiled and scored independently in controlled and naturalistic development strata under the frozen opportunity, abstention, correspondence, and typed-failure rules. The preferred criterion must hold in both strata: precision at least 0.90, recall at least 0.70, F1 at least 0.80, and coverage at least 0.75.

Selection maximizes this exact descending lexicographic tuple using integer counts and exact rational comparisons:

```text
preferred criterion met
minimum-stratum F1
mean-stratum F1
minimum-stratum coverage
mean-stratum coverage
minimum-stratum precision
mean-stratum precision
minimum-stratum recall
mean-stratum recall
threshold
secondary threshold or margin
```

Thus a higher threshold or margin wins only after every observed development metric ties. If no candidate meets the preferred criterion, the first field is false for every candidate; the remaining tuple selects deterministically and the report records `preferred_development_criterion_met=false`. A missing, malformed, non-development, or hash-inconsistent score artifact blocks calibration. A genuine typed component/compiler failure remains part of every affected candidate's scoring.

## 5. Abstention and integrated replay

A below-threshold or below-margin result abstains. Positive abstention is a false negative and uncovered opportunity; negative abstention produces no imputed false positive and is uncovered. A non-abstained type prediction is covered even when its value is wrong. Typed failure makes every positive opportunity on the image a false negative and every applicable opportunity uncovered. Scoring follows compiler normalization.

After all settings are selected, the exact component scores are assembled together and replayed through the unchanged compiler to produce 240 development pipeline/image records. Any integrated bounded-observation or compiler failure remains evidence and cannot trigger refitting. The threshold freeze binds the score manifest, inventory, entity scopes, complete candidate tables, fit report, selected settings, and replayed development tree before validation authorization.

## 6. Engineering smoke

`engineering-smoke-settings-v3.3.0` fixes every component threshold at 0.50 and every SigLIP top-two margin at 0.00. These are prospective plumbing constants, not development-fitted settings. Smoke results cannot enter the threshold freeze or alter calibration.

This addendum authorizes no image generation, model acquisition, smoke, development inference, validation, P9-v3C, P10, or cryptographic work by itself.
