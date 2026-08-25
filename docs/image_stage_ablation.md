# P7 image-stage versus text-only ablation

**Experiment:** `p7-cached-v1`

**Date:** 2026-08-25
**Gate B:** **B — remove the image stage from the authentication core; retain it as an optional/measurement baseline**

## Boundary and design

P7 is a bounded engineering diagnostic over the existing P5 cache. It evaluates nine families and 27 paired train/validation relationships. It executes no model, downloads no model, reads no P6 artifact, and evaluates no held-out test row. It makes no human memorability, usability, preference, or authentication claim.

The design compares:

1. Florence image-derived atoms against controlled-text atoms using the same canonical schema and Jaccard matcher;
2. the same structured pathways using the same frozen P5 training-only IDF weights and directional overlap matcher;
3. SigLIP image embeddings against MiniLM text embeddings using cosine, with encoder capacity, training, and dimension explicitly recorded as an attribution confound.

Thresholds use the unchanged P6 deterministic minimax rule on the six P5 training families and are evaluated unchanged on the three validation families. Family-cluster percentile intervals use 4,000 fixed-seed resamples. Because the dataset is a smoke-scale cache, the results decide pipeline disposition, not authentication viability or publication-level performance.

## Paired results

| Comparison | Image gap minus text gap, same vs near (95% CI) | Image gap minus text gap, same vs random (95% CI) | Validation worst error, image − text |
|---|---:|---:|---:|
| Structured Jaccard | -0.076 `[-0.274, 0.091]` | -0.346 `[-0.541, -0.164]` | 0.000 |
| Structured weighted overlap | -0.022 `[-0.189, 0.134]` | -0.275 `[-0.483, -0.080]` | 0.000 |
| Dense cosine | -0.005 `[-0.056, 0.042]` | -0.468 `[-0.537, -0.385]` | 0.000 |

No same-minus-near improvement has a lower confidence bound above zero. All three image pathways materially reduce same-versus-random separation relative to their paired text pathways. Every pathway's validation minimax worst error is 0.667, so the image stage provides no threshold-trade-off improvement on the three-family validation slice.

Non-empty rate is 1.0 for both structured pathways and both dense arrays, but non-empty output is not semantic fidelity. Florence macro precision/recall/F1 is 0.335/0.533/0.375, compared with 0.786/0.626/0.638 for controlled text. Florence recall is zero for action, count, and relation atoms and it introduces many false objects, counts, relations, and attributes. Thus Florence is a clear structured extraction bottleneck.

The dense result is directionally consistent with the structured results but cannot isolate the image transformation: SigLIP and MiniLM differ in modality, model training, capacity, and vector size. It is evidence about the two complete tested pathways, not a controlled comparison of identical encoders.

## Cost and privacy exposure

The cached image generator required a median 25.80 seconds per row and reported 5,716.78 MiB peak CUDA allocation. Florence then required a median 10.64 seconds per row and 1,210.65 MiB peak allocation. SigLIP encoded all 27 images in 0.99–1.15 seconds per repeat at 829.97 MiB, while MiniLM encoded all 27 texts in 0.10–0.18 seconds at 101.27 MiB. P5 did not time the controlled-text parser, so no invented parser latency is reported. The 27 PNGs occupy 11,877,601 bytes; SigLIP vectors occupy 83,072 bytes versus 41,600 bytes for MiniLM.

The image path also creates a local visual artifact containing semantic content and adds generator and image-model supply-chain, runtime, and drift surfaces. Raw structured atoms and both raw embedding families remain readable/linkable plaintext baselines; none is a privacy-preserving storage design. Images can be discarded after local extraction, but that reduces persistence rather than eliminating runtime exposure.

Model drift is unavailable in P7 because P5 contains only one frozen revision per model.

## Frozen decision

Outcome A (retain as core) fails every paired material-benefit rule. Outcome C (unresolved extractor bottleneck) is not selected: although Florence is inadequate, the cache still supplies comparable structured downstream matchers and a second dense pathway comparison, enough to conclude that **the tested image pathways have no demonstrated benefit commensurate with their cost and exposure**. This supports outcome B without claiming that all future image extractors are impossible.

Accordingly:

- direct-text semantics becomes the only authentication-path hypothesis entering P8;
- image generation/extraction remains a documented optional perturbation and measurement baseline;
- the working paper title and central thesis must be reconsidered at Gate A2/D9 rather than continuing to imply that images are essential;
- P9/P10 remain blocked until Gate A2 constructively integrates P6 quality and P8 budgeted attacks.

## Semantic-policy hypothesis

The oracle-versus-real-extractor gap and changed-atom failures motivate—but do not establish—a future hypothesis: require one or more discriminative semantic anchors while tolerating secondary attributes. P7 does not implement or tune this policy, does not replace semantic tolerance with exact prompt/set equality, and does not reuse P6 validation observations to choose anchors. Any evaluation requires a new scheme/version, independent rationale, new data, preregistration, and a new gate.

## Artifacts

- frozen configuration: `experiments/image_stage_ablation/config/p7_cached_v1.json`
- deterministic runner and tests: `experiments/image_stage_ablation/run_p7.py`, `test_p7.py`
- compact result: `results/p7/cached_ablation_v1.json`
- paired scores: `results/p7/paired_scores_v1.jsonl`
- generated figure: `results/p7/image_text_tradeoff_v1.svg`
