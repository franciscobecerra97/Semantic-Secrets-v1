# P6 plaintext matching, thresholds, and acceptance-region pilot

Date: 2026-08-24

Run: `p6-pilot-v1`

Result: `results/p6/pilot_v1.json`

Purpose: preregistered pilot evidence for D4 and Gate A. This is not a publication result, held-out test result, protocol benchmark, population guessing estimate, or human-subject authentication study.

## Outcome

Gate A fails with outcome **stop or reframe**. The frozen controlled weighted direct-text primary did not distinguish intended paraphrases from one-atom targeted neighbours with useful uncertainty. Cardinality, Jaccard, and MiniLM likewise failed the targeted-neighbour comparison. P9/P10 protocol engineering is forbidden on this failed gate: private computation cannot repair a matcher whose plaintext acceptance region is non-viable.

At the training-selected weighted-overlap threshold `0.84007072`, validation results were:

| Metric | Point estimate | 95% family-cluster bootstrap |
|---|---:|---:|
| False rejection rate | 0.208 | `[0.000, 0.458]` |
| Targeted-neighbour FAR | 0.750 | `[0.500, 1.000]` |
| Random-impostor FAR | 0.030 | `[0.008, 0.053]` |
| AUC, positives vs all negatives | 0.869 | `[0.747, 0.956]` |
| AUC, positives vs targeted neighbours | 0.517 | `[0.500, 0.557]` |
| Mean same-minus-neighbour score gap | 0.021 | `[0.000, 0.063]` |

Only the FRR point, random-FAR point/upper bound, and neither uncertainty-sensitive separation bound nor representation-completeness bound passed. The validation non-empty representation rate was 0.75 versus the frozen 0.90 minimum. Broad failure—not one isolated subgroup—supports stop/reframe rather than a post-hoc parser revision.

## Pilot and sealing boundary

`controlled-pilot-v1` contains 60 project-authored families and exactly one same-type atom replacement per targeted neighbour. It was created from twelve audited structural templates using five disjoint lexical transformation cycles. A separate label-only audit checked 120 concepts and 360 prompt variants without model or matcher outputs. Schema and ontology validation covered all atom types, complexity levels, and planned frequency bands.

| Split | Families | P6 use |
|---|---:|---|
| Train | 36 | Object lexicon and threshold selection |
| Validation | 12 | Frozen-rule evaluation and Gate A decision |
| Test | 12 | Unevaluated and reserved |

P6 evaluated four direct-text rows per train/validation family: enrolment, two paraphrases, and one targeted near neighbour. It also formed all cross-family enrolment comparisons within each evaluated split. The reusable pair export therefore contains 1,536 rows: 96 positives, 48 targeted neighbours, and 1,392 random negatives. No image model, test-family row, public prompt, or participant input entered the run.

The design labels `common_candidate`, `mid_candidate`, and `rare_candidate` remain controlled strata, not measured human or population frequencies.

## Preregistered decision rule

`experiments/plaintext_matching/config/p6_pilot_v1.json` was frozen before successful model output or score calculation. Training selected an inclusive threshold by lexicographically minimising:

1. the maximum of FRR, targeted-neighbour FAR, and random FAR;
2. their sum;
3. accepted-negative mass; and
4. on a tie, the stricter threshold.

Gate A required every frozen weighted-primary bound to pass on validation: FRR point/upper, targeted-neighbour FAR point/upper, random FAR point/upper, all-negative AUC lower bound, same-minus-neighbour gap lower bound, and non-empty representation rate. Baselines, subgroups, threshold sweeps, and oracle knowledge were not allowed to pass the gate.

The independent uncertainty unit is the concept family. Intervals use 4,000 fixed-seed family-cluster bootstrap repetitions. A zero observed rate receives an upper guard of at least `3 / 12 = 0.25`; the quadratic number of random pairs is not treated as hundreds of independent secrets. Baseline and subgroup intervals are exploratory under the frozen multiplicity policy.

## Matcher comparison

Each threshold was selected on training and then applied unchanged to validation.

| Matcher | Threshold | Validation FRR | Near FAR | Random FAR | Near AUC | Same−near gap |
|---|---:|---:|---:|---:|---:|---:|
| Cardinality | 3.000 | 1.000 | 0.000 | 0.000 | 0.514 | 0.042 |
| Jaccard | 0.714 | 0.292 | 0.750 | 0.030 | 0.488 | 0.007 |
| Weighted enrolled overlap | 0.840 | 0.208 | 0.750 | 0.030 | 0.517 | 0.021 |
| MiniLM cosine | 0.912 | 0.625 | 0.583 | 0.000 | 0.295 | −0.036 |

Random concepts are mostly easy, which inflates all-negative AUC. The technically relevant targeted neighbours overlap the positive distribution: near-only AUC is approximately chance for structured variants and below chance for MiniLM. A high headline AUC against mostly random negatives would therefore be misleading.

At the primary threshold, relation changes were accepted in all five validation relation families. The single validation action, attribute, and object changes were also accepted; one of two count changes was accepted, while neither scene change was accepted. These cells are exploratory and small, but the aggregate near failure is not driven by one cell.

## Representation stability and missingness

All 144 selected training rows produced non-empty controlled representations. Validation produced 36 non-empty rows out of 48. The training-only object lexicon generated 24 `no_known_object` warnings and 12 empty representations on validation. This confirms the P5 `QF-TRAIN-LEXICON-OOV` concern.

OOV alone does not explain the decision: among recognized concepts, the deterministic parser frequently mapped the intended paraphrase and the changed neighbour to the same atoms. The weighted near-only AUC was 0.517 and the positive-minus-near interval started at zero. Expanding a lexicon after viewing validation would violate the frozen pilot and would not address relation/action insensitivity without changing the extractor hypothesis.

MiniLM embeddings were exact across two complete passes. Raw vectors remain candidate-retrievable/linkable by the P5 probes and are not treated as private.

## Acceptance-region and provisional attack analysis

The threshold sweep reports reliability and controlled attacker acceptance together. At the nearest reported grid point (`0.85`), validation FRR was 0.208, neighbour acceptance was 0.750, random acceptance was 0.030, and the explicitly provisional 80%-random/20%-targeted mixture acceptance was 0.174. The finite validation dictionary accepted a mean of one and a maximum of two negative candidates per enrolled concept.

Conditioning random candidates on at least one shared extracted atom left only two finite-dictionary pairs, both accepted. There were no candidates with two or three shared extracted atoms. These counts illustrate acceptance-region concentration; they are not a general partial-information or population attack estimate.

No score is called calibrated because no score is asserted to be a probability. Human secret-choice mass, real attacker priors, public-prompt frequency, LLM guessing, and held-out attack success remain unmeasured.

## Runtime and storage

With the model already present in the pinned local cache, MiniLM loaded in 0.84 seconds and encoded 192 prompts in 0.325 and 0.122 seconds on its two exact-repeat GPU passes, peaking at 109.97 MiB allocated. The embedding array is 295,040 bytes. Each 192×192 matrix is 147,584 bytes; scored pairs are 615,627 bytes and canonical representations 58,726 bytes. These are engineering observations on the documented P5 machine, not deployment benchmarks.

No cryptographic latency, bandwidth, or implementation cost was measured because Gate A failed before protocol engineering.

## D4 and phase boundary

1. Select no plaintext matcher for authentication deployment under P6 evidence.
2. Record weighted overlap as the least complex *conditional* private-computation mapping—private weighted intersection plus threshold comparison—but do not implement it on a failed Gate A.
3. Treat exact cardinality/Jaccard as PSI-style candidates and cosine as a substantially heavier private dot-product candidate only in comparative documentation.
4. Preserve the negative pilot and reusable matrices as measurement evidence.
5. Do not perform P9/P10 protocol selection/engineering unless an explicit reframe creates a scientifically distinct objective and decision record.
6. P7 may use existing P5 caches for a bounded paired diagnostic to decide whether the image stage has measurement value, but there is no Gate A survivor to advance as an authentication pipeline.
7. A future extractor revision requires a new version, a source of vocabulary independent of validation/test labels, new preregistration, and new data; it cannot reinterpret `p6-pilot-v1` as a pass.
