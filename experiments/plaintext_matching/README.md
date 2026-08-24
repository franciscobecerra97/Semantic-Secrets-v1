# P6 plaintext matching pilot

`p6-pilot-v1` evaluates the frozen P5 direct-text representation on 36 training and 12 validation concept families. Twelve pilot test families remain unevaluated. This is pilot design evidence, not a publication result or human authentication study.

## Frozen order

1. Author and label-only audit `controlled-pilot-v1`.
2. Generate deterministic, label-separated pilot manifests.
3. Freeze `config/p6_pilot_v1.json`, including threshold selection and Gate A bounds.
4. Run exact-repeat MiniLM embeddings and deterministic plaintext analysis.
5. Validate all artifact hashes, matrix dimensions, threshold provenance, and the test boundary.

The failed local-cache lookup recorded during development occurred before any model output. The frozen config explicitly points to the ignored P5 cache and forbids network fallback.

## Reproduction

From the repository root with the P5 environment installed:

```text
python -m experiments.datasets.author_pilot_catalog
python experiments/datasets/split_manifest.py generate --stage pilot --design experiments/datasets/config/design_p6_v1.json
python experiments/datasets/split_manifest.py validate --stage pilot --design experiments/datasets/config/design_p6_v1.json
python -m experiments.plaintext_matching.run_p6 --stage all
python -m experiments.plaintext_matching.run_p6 --validate-only
python -m unittest experiments.plaintext_matching.test_p6 tests.test_matching
```

The runner exports four reusable 192×192 matrices, scored evaluation pairs, canonical representations, a threshold/acceptance-region result, and an SVG trade-off curve. MiniLM is the only model executed in P6. P7 owns any pilot image generation.

## Boundary

The training split selects thresholds; validation evaluates them. The primary decision uses only weighted controlled-text overlap. Cardinality, Jaccard, and MiniLM are exploratory baselines. Scores are not calibrated probabilities. Controlled dictionary and 80/20 mixture results are provisional attack distributions, not estimates of human secret selection or real population guessability.

Gate A failed under the frozen criteria. P9/P10 protocol engineering is therefore forbidden unless the project is explicitly reframed and a new decision authorises a scientifically distinct path.
