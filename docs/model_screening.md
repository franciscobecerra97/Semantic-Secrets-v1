# P4 model and backend screening

Date: 2026-08-24

Run: `p4-screen-v1`

Result: `results/p4/screen_v1.json`
Purpose: engineering feasibility and candidate elimination only; these observations are not paper results.

## Boundary and decision

P4 used the cheapest evidence capable of eliminating unsuitable backends. It did not generate P3 corpus images, download either production generator, tune a model, measure authentication performance, or make security, usability, or human-behaviour claims.

- **D1 provisional primary:** `stabilityai/sd-turbo`, conditional on a CUDA microbenchmark and semantic renderability check before corpus generation.
- **D1 retained alternative:** `stabilityai/stable-diffusion-xl-base-1.0`, only for a quality/model-drift comparison on documented stronger hardware.
- **Required P7 path:** no-image/direct-text remains mandatory.
- **D2 survivors for P5:** Florence-2-base (structured detector/caption/geometry hypothesis), SigLIP base 224 (dense image baseline), all-MiniLM-L6-v2 (dense text baseline), and the controlled parser v1 (structured text lower bound).
- **D2 rejection:** SmolVLM-256M-Instruct is rejected as a strict structured extractor under config v1. It was deterministic, but failed all six schema attempts, reached only 0.20 lexical probe coverage, and used about 3.7 GiB process RSS during roughly 29–31 second CPU runs.
- **Not selected:** no primary extractor or representation is selected in P4. P5 must compare the surviving families on identical cached inputs and may reject Florence-2 or the complete structured-image path.

## Documented machine

| Item | P4 environment |
|---|---|
| Host | Dell Precision 3571; Windows 11 `10.0.26200` |
| CPU | Intel Core i9-12900H; 14 physical / 20 logical cores |
| RAM | 31.7 GiB |
| GPU | NVIDIA T600 Laptop GPU; 4,096 MiB; driver 581.95; compute capability 7.5 |
| Free workspace volume | approximately 634.4 GiB before screening |
| Python | 3.13.9 |
| PyTorch | 2.13.0+cpu; CUDA build unavailable in this environment |
| Screening libraries | Transformers 4.57.1, Diffusers 0.35.2, Accelerate 1.10.1, Hugging Face Hub 0.36.2, safetensors 0.6.2, sentencepiece 0.2.1, protobuf 6.32.0, jsonschema 4.25.1 |

The physical GPU exists, but the installed PyTorch build is CPU-only. Therefore P4 does not claim that SD-Turbo fits or is fast enough locally. Downloading several gigabytes of production generator weights before repairing and measuring the CUDA path would not discriminate the choice cheaply.

## Candidate and licence screen

Exact revisions, acquisition rules, deterministic controls, expected resources, and statuses are machine-readable in `experiments/model_screening/model_manifest.json`.

| Backend | Role | Revision | Licence/source | P4 outcome |
|---|---|---|---|---|
| SD-Turbo | provisional generator | `b261bac6fd2cf515557d5d0707481eafa0485ec2` | [official card](https://huggingface.co/stabilityai/sd-turbo), Stability AI Community License | Retain conditionally. Its 512 px, one-to-four-step design is the least implausible production generator on the 4 GiB target, but it was not acquired or benchmarked. |
| SDXL base 1.0 | generator alternative | `462165984030d82259a11f4367a4eed129e94a7b` | [official card](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0), CreativeML Open RAIL++-M | Retain only for stronger hardware; the official standalone checkpoint is about 6.94 GB. |
| Florence-2-base | structured detector/caption/geometry | `5ca5edf5bd017b9919c05d08aebef5e4c7ac3bac` | [official card](https://huggingface.co/microsoft/Florence-2-base), MIT | Shortlist for P5. Pin and review any remote model code; use deterministic post-processing for geometry/relations. Not acquired in P4. |
| SmolVLM-256M-Instruct | constrained multimodal VLM | `7e3e67edbbed1bf9888184d9df282b700a323964` | [official card](https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct), Apache-2.0 | Reject under strict schema v1: `QF-SCHEMA`, `QF-COVERAGE`, `QF-LATENCY`. |
| SigLIP base patch16 224 | dense image baseline | `7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed` | [official card](https://huggingface.co/google/siglip-base-patch16-224), Apache-2.0 | Retain as mandatory dense image baseline. |
| all-MiniLM-L6-v2 | dense direct-text baseline | `1110a243fdf4706b3f48f1d95db1a4f5529b4d41` | [official card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2), Apache-2.0 | Retain as mandatory dense text baseline. |
| Controlled parser v1 | structured direct-text lower bound | no weights | project code; repository licence still to be declared | Retain as transparent lower bound, not as evidence of open-ended language coverage. |

The internal tiny Stable Diffusion checkpoint is an interface fixture only. Its outputs cannot be used for a model-quality or paper claim.

## Fixed smoke observations

The runner used two fixed repeats. Image extractors saw three programmatically drawn fixtures: red-square/blue-circle left-right, two green circles above a black rectangle, and a yellow triangle inside a purple square. Text baselines saw the 36 deduplicated P3 smoke text inputs. No fixture image was saved.

| Screen | Fixed-repeat result | Latency per measured call | Peak process RSS | Schema / coverage observation |
|---|---:|---:|---:|---|
| Tiny generator interface fixture | equal at seed 1101; seed 2202 differed | 0.116 s, 0.070 s | 400.75, 401.19 MiB | Semantic coverage deliberately not assessed. |
| SmolVLM structured VLM | byte-identical failures | 28.71–31.41 s per fixture | 3,710.27–3,755.38 MiB | 6/6 invalid JSON/schema attempts; aggregate probe coverage 0.20. |
| SigLIP dense image | identical embedding hash | 0.614 s, 0.412 s for three images/text labels | 1,228.35, 1,230.10 MiB | Correct top matching label for 3/3 simple fixtures; this is a plumbing/coverage probe, not an accuracy estimate. |
| MiniLM dense text | identical embedding hash | 0.069 s, 0.049 s for 36 texts | 566.53, 566.64 MiB | finite `36 × 384` embeddings. |
| Controlled structured parser | identical output hash | 0.912 s cold, 0.016 s warm for 36 texts | 521.04 MiB | 72/72 schema-valid repeat outputs; constrained vocabulary makes this a lower bound. |

Model loads took 0.72 s (tiny generator), 1.78 s (SmolVLM from warm cache), 50.82 s (SigLIP, including acquisition/load in this run), and 5.15 s (MiniLM, including acquisition/load). Process RSS is a sampled whole-process measure, not isolated model allocation. The first failed execution also established that SigLIP needs Protocol Buffers; `protobuf==6.32.0` is now pinned.

### Qualitative failure codes

| Code | Meaning |
|---|---|
| `QF-SCHEMA` | malformed JSON or output rejected by structured schema |
| `QF-COVERAGE` | missing required object, attribute, count, action, relation, or scene evidence |
| `QF-LATENCY` | runtime is unsuitable for the intended bounded local workflow |
| `QF-NONDET` | identical fixed input/config does not reproduce |
| `QF-HARDWARE` | documented target cannot execute the configuration without an unapproved dependency/offload change |
| `QF-REMOTE-CODE` | executable model code is not reviewed and revision-pinned |
| `QF-LICENSE` | licence or acceptable-use terms do not permit the planned research use/distribution |
| `QF-MISSING-ATOM` | an otherwise structured response omits a required semantic atom class |
| `QF-HALLUCINATION` | output adds unsupported atoms |
| `QF-OOM` | execution exceeds available memory |

## Artifact identity and reproduction

The result file stores every relevant cached model/config/tokenizer file hash. Aggregate tree hashes are:

| Artifact | Tree SHA-256 | Hashed size |
|---|---|---:|
| tiny generator fixture | `3640ca99c0ef7980dba7bc84d7fa8896887d45cf206923da502385a212ea8f3b` | 8,827,853 bytes |
| SmolVLM | `eba05ac0d4005a44ef8013d68006cd223b763b4c8bb7be4423c35f90f9742247` | 517,886,646 bytes |
| SigLIP | `768baeacb9bc5df185e854630060ba5516662ed5fda6cad848ee2e045219b36e` | 815,871,927 bytes |
| MiniLM | `48271ee26402424cf09bdfb648e379fd7ca9e08d4bcca8886f65203abb9d2091` | 91,567,205 bytes |

Create a project-local virtual environment, install the pinned screening requirements plus the platform-appropriate PyTorch build, and point `HF_HOME` to `artifacts/downloads/hf-p4`. Run `experiments/model_screening/run_screen.py`; use `--validate-only` to validate an existing result without loading models. Model weights and caches remain ignored by Git.

For a clean reproduction, do not substitute an unpinned revision. Hash mismatches create a new screen ID/result rather than overwriting `p4-screen-v1`. On Windows without Developer Mode, Hugging Face caching may duplicate files because symlinks are unavailable; this changes disk use, not the hashed artifact contents.

## P5 handoff and remaining uncertainty

P5 may proceed with schema `structured-extraction-v1` and backend interfaces in `prototype/semantic_secrets/backends/`. It must:

1. acquire Florence-2-base at the pinned revision, review/pin executable remote code if required, and test deterministic task outputs on cached smoke/pilot images;
2. retain SigLIP, MiniLM, and controlled-parser results as scientifically distinct baselines;
3. compare identical inputs, frozen preprocessing, versioned canonicalisation, missing-output behaviour, and atom-level errors;
4. repair and document the CUDA PyTorch environment before acquiring SD-Turbo, then run only a fixed-seed microbenchmark and controlled semantic renderability screen;
5. stop or reframe the structured-image path if Florence-2 also fails the schema/coverage gate rather than silently using a cloud model.

Generator quality, extractor accuracy on natural/generated images, positive/negative separability, calibration, privacy leakage, and authentication viability remain unmeasured.
