# P5 semantic representation and canonicalisation comparison

Date: 2026-08-24

Run: `p5-smoke-v1`

Result: `results/p5/smoke_v1.json`

Purpose: bounded engineering smoke evidence for D2/D3 and a P6 hypothesis. This is not a pilot, held-out test, Gate A pass, or publication result.

## Outcome

P5 freezes `canonical-semantics-v1` and `oracle-train-idf-v1`, but no measured representation has uncertainty-supported near-neighbour separation. The only rows whose 95% paired gap interval stays above zero are oracle ground-truth diagnostics, which are not deployable extractors.

- **Primary P6 representation hypothesis:** controlled direct-text extraction with the training-only IDF-weighted structured set. It is selected only as the clearest falsifiable hypothesis: overall medians were 1.00 for paraphrase positives, 0.80 for one-atom neighbours, and 0.00 for unrelated pairs. Its same-minus-near 95% bootstrap interval was `[-0.0166, 0.3917]`, so viability is unproved.
- **Dense finalists retained:** MiniLM direct-text and SigLIP image embeddings. Both distinguish unrelated pairs, but their near-neighbour gaps are small and their intervals cross zero.
- **Structured image decision:** reject Florence-2-base plus deterministic caption/geometry fusion as primary. It recovered no expected action, count, or relation atoms, had macro F1 0.375, and validation same-concept median Jaccard (0.308) was below near-neighbour median (0.600).
- **Unweighted structured set:** retained as an interpretable baseline, not a primary; its same and near medians were both 0.67.
- **Gate status:** Gate A remains closed. P6 may perform one bounded pilot/negative confirmation using the frozen finalists, but must not claim semantic viability from P5 smoke data.
- **Image-stage status:** SD-Turbo is numerically usable only in float32 on this machine, oversubscribing the physical GPU. P7 still owns the image-stage decision.

## Dataset boundary

P3 planned but did not author the 60-family pilot catalog. P5 therefore used the complete approved roles needed for cheapest discrimination on train/validation smoke families:

| Boundary | Value |
|---|---:|
| Families | 9: six train, three validation |
| Image/text rows | 27 |
| Roles per family | enrolment, one paraphrase positive, one one-atom near neighbour |
| Diagnostic pairs | 9 same, 9 near, 9 unrelated |
| Test rows/labels evaluated | 0 |
| Full/pilot/public inputs | 0 |

Unrelated pairs rotate enrolment rows within each split. IDF weights use only the six training-family enrolment oracle sets. Validation and test labels do not define weights. Bootstrap intervals resample the nine family units with a fixed seed and are coarse because this is smoke scale.

## Frozen canonicalisation

`canonical-semantics-v1` applies these deterministic rules before constructing sorted, deduplicated atom signatures:

- Unicode NFKC, Unicode case-folding, whitespace/punctuation collapse, and underscore separators;
- conservative singularisation plus a frozen irregular/alias map;
- object-label resolution before attributes, counts, actions, and relations;
- positive integer counts;
- directional normalisation by swapping endpoints for `right_of`, `below`, `behind`, and `under`;
- endpoint sorting for symmetric `beside`;
- minimum confidence 0.25, with typed warnings for dropped atoms;
- empty output represented by an empty tuple plus `empty_representation`;
- strict failure on source-schema or representation-version mismatch; and
- no implicit migration between versions.

The exact rules are in `prototype/semantic_secrets/semantics/canonical_scheme_v1.json`. Golden vectors cover order invariance, duplicates, low confidence, malformed versions, aliases, plural handling, relations, and controlled text.

The weighted variant uses smoothed IDF, `log((N+1)/(df+1))+1`, fitted to six training enrolment oracle documents. The weight-file hash is `130b2cec205c3f3d67acafa07718688495bb5175df489b6e06a4a2fee162dd17`. This is a research weight hypothesis, not a population-frequency or security weight.

## Model/runtime configuration

The local environment uses official PyTorch `2.12.1+cu126` and torchvision `0.27.1+cu126` wheels on the NVIDIA T600. PyTorch documents this paired CUDA 12.6 installation for Windows/Linux. [Official PyTorch versions](https://pytorch.org/get-started/previous-versions/)

### SD-Turbo

The pinned [SD-Turbo](https://huggingface.co/stabilityai/sd-turbo) revision is `b261bac6fd2cf515557d5d0707481eafa0485ec2`, one step, guidance 0, 512×512, explicit per-row seeds. The repository’s fp16 components were loaded as float32 because fp16 UNet execution produced all-NaN latents under both PyTorch 2.13/CUDA 13.0 and PyTorch 2.12.1/CUDA 12.6. The frozen float32 path produced non-degenerate, fixed-seed-repeatable images but used WDDM oversubscription.

| Generator observation | Value |
|---|---:|
| Completed images | 27 |
| Median latency | 25.80 s/image |
| Range | 25.60–26.47 s/image |
| Peak CUDA allocated | 5,716.78 MiB on a physical 4,096 MiB card |
| Cached PNG size | 11.33 MiB total |
| Fixed-seed repeat | byte-identical RGB |
| Artifact tree SHA-256 | `208879b16f12f4f2d0a89e607dad0a51954447285fda819115b20c6de03e6e66` |

Failure codes: `QF-NUMERIC-FP16`, `QF-HARDWARE-OVERSUBSCRIPTION`. Generated images remain in the ignored cache; the manifest stores their RGB/PNG hashes, prompt hashes, seeds, pixel ranges, latency, memory, and model file hashes.

### Florence-2

The pinned [Florence-2-base](https://huggingface.co/microsoft/Florence-2-base) revision is `5ca5edf5bd017b9919c05d08aebef5e4c7ac3bac`. P5 reviewed and hashed its pinned remote code and used float32 CUDA, eager attention, `do_sample=false`, three beams, and `use_cache=false`. Disabling the KV cache is required because this older remote code is incompatible with Transformers 4.57’s changed cache API. The model card identifies caption and object-detection task outputs used here.

| Florence observation | Value |
|---|---:|
| Rows / tasks | 27 / object detection plus detailed caption |
| Combined median latency | 10.64 s/image |
| Combined range | 6.61–17.78 s/image |
| Peak measured CUDA allocation after load | 1,210.65 MiB |
| Repeat samples | 2/2 raw-task bundles identical |
| Artifact tree SHA-256 | `cdf82d1e6a6bab49ca186a0106719ea0ffa3317feda1513b4fb587453e9049ab` |

Florence detected objects reasonably often (object recall 0.771) but produced extra object labels and deterministic geometric relations unsupported by ground truth. Expected action/count/relation recall was zero. Failure codes: `QF-COVERAGE`, `QF-MISSING-ATOM`, `QF-HALLUCINATION`.

### Dense baselines

| Backend | Shape | Two run times | Peak CUDA | Repeat | Artifact tree SHA-256 |
|---|---:|---:|---:|---:|---|
| [SigLIP base 224](https://huggingface.co/google/siglip-base-patch16-224) | `27 × 768` | 1.153 s, 0.988 s | 829.97 MiB | exact | `92079363cb7f2d1b62aa64b851ed573081862e8a8b56bd9544eec0ac5b33450e` |
| [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) | `27 × 384` | 0.180 s, 0.104 s | 101.27 MiB | exact | `519954597750afc0525099fc66839a750b69ec4879cefd47b44b36728255ccb3` |

## Diagnostic separation

These scores only eliminate/retain hypotheses. No matcher or threshold is selected in P5.

| Representation | Same median | Near median | Unrelated median | Same−near paired gap, 95% bootstrap | Uncertainty supports positive near separation? |
|---|---:|---:|---:|---:|---:|
| Oracle structured diagnostic | 1.000 | 0.667 | 0.000 | `[0.344, 0.632]` | yes, diagnostic only |
| Oracle weighted diagnostic | 1.000 | 0.800 | 0.000 | `[0.211, 0.539]` | yes, diagnostic only |
| Controlled text structured | 0.667 | 0.667 | 0.000 | `[-0.068, 0.296]` | no |
| Controlled text weighted | 1.000 | 0.800 | 0.000 | `[-0.017, 0.392]` | no |
| Florence structured | 0.333 | 0.300 | 0.000 | `[-0.114, 0.186]` | no |
| Florence weighted | 0.773 | 0.563 | 0.000 | `[-0.108, 0.416]` | no |
| SigLIP image | 0.935 | 0.916 | 0.588 | `[-0.017, 0.091]` | no |
| MiniLM text | 0.935 | 0.922 | 0.104 | `[-0.002, 0.084]` | no |

Split sensitivity reinforces the caution. Florence validation same median was lower than near median. Controlled weighted validation near median was 1.0, meaning all three validation neighbours could be as similar as positives under this representation. The machine-readable result also breaks near scores down by the changed atom type; cells are too small for a claim.

## Atom fidelity

| Extractor | Macro precision | Macro recall | Macro F1 | Empty rows |
|---|---:|---:|---:|---:|
| Controlled direct-text parser | 0.786 | 0.626 | 0.638 | 0 |
| Florence caption/detection/geometry | 0.335 | 0.533 | 0.375 | 0 |

The controlled parser deliberately derives its object lexicon only from training labels. Its lower validation coverage is recorded as `QF-TRAIN-LEXICON-OOV`, not repaired with validation/test vocabulary. It has high scene recall but weak relation, attribute, and action coverage.

## Leakage and private-comparison boundary

Cheap probes establish that none of the raw representations is private:

- structured atoms disclose their contents directly and identical raw sets are linkable across services;
- each dense vector retrieved its exact candidate from the 27-entry known dictionary;
- SigLIP and MiniLM linked all 9 enrolments to the correct family paraphrase at top-1;
- these are known-candidate/linkability probes, not general model inversion results.

Unweighted structured sets have a plausible PSI/PSI-cardinality/private-threshold path. Weighted sets need private weighted intersection plus a policy for public/protected weights. Dense cosine requires approximate dot-product evaluation using MPC/HE or related machinery. P5 selects no protocol and rejects plaintext storage for every family.

## D2/D3 and P6 handoff

1. Freeze `canonical-semantics-v1`; changes create v2 and require an explicit migration/re-enrolment policy.
2. Reject Florence-2 fusion as the structured primary under P5 config v1; retain raw outputs as a negative result.
3. Use controlled weighted direct-text semantics as the primary P6 hypothesis, with unweighted structured text, MiniLM, and SigLIP as mandatory baselines.
4. Do not treat oracle representations as candidates; they validate the canonicaliser and show the designed pairs are separable when atoms are known.
5. Before P6 can estimate a defensible operating region, author and blind-audit the planned pilot catalog or approve a versioned smaller pilot justified by cluster-level precision. Test labels remain sealed.
6. P6 must preregister its threshold/viability rule before that pilot and may produce a Gate A negative result. It may not pass Gate A using this smoke run.
7. Do not run another structured-image VLM family without a distinct documented reason; the present evidence favors testing whether the direct-text path makes image generation unnecessary.

Model drift remains unmeasured because P5 used one generator and one extractor revision. General inversion, calibration, FAR/FRR/EER, acceptance-region mass, protocol leakage, and authentication security remain unmeasured.
