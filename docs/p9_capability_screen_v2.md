# P9 visual-semantic capability screen

## Outcome

P9 is complete with a negative result. Neither preregistered extractor survived P9A, P9B was therefore not executed, and Gate V2-A fails. P10 remains blocked. This result rejects the tested frozen representation path; it does not establish that every visual-semantic extractor is impossible.

## Frozen capability set

The screen authored 96 new 512×512 controlled images: 64 development and 32 validation fixtures. The set contains 48 procedural/composite and 48 researcher-authored synthetic-raster scenes, covers objects, attributes, counts, actions, spatial relations, and scene labels, and contains no participant data or v1 family. A deterministic authoring audit verifies split/style counts, graph validity, file hashes, image uniqueness, and the absence of v1 access. The manifest SHA-256 is `43f89f0012520865b2d780ee19fbc4f2d27c1eb279edadf37342ee6074db8c76`.

Only the two frozen candidates were acquired and run:

- `vikhyatk/moondream2` at revision `9a7d4024050840e001defacec2b00727e89149e6`;
- `HuggingFaceTB/SmolVLM2-2.2B-Instruct` at revision `c0a7af506d0f71a771f24216ade491dec52ff6c5`.

Weights and generated images remain outside Git. Moondream's repository-root Python files were hashed and statically reviewed before `trust_remote_code` execution. Its optional LoRA downloader was recorded as an allowed finding because the frozen run supplies no variant identifier; inference additionally used offline/local-only loading and a snapshot-local tokenizer. SmolVLM2 used standard Transformers code and local-only loading. Both ran on CPU because the declared NVIDIA T600 has only 4 GiB VRAM; measured process memory remained below the 24 GiB limit.

## Plumbing smoke

Smoke outputs are preserved separately from formal evidence. The first Moondream smoke exposed two implementation-only compatibility errors (`variant` was omitted); no semantic observation from those records was used. After the loader was corrected without changing the model, prompt, candidate list, or gate, two development fixtures produced non-JSON text in 153.61 and 165.05 seconds. Two SmolVLM2 development fixtures reached the frozen 384-token cap, emitted malformed/truncated JSON, and took 393.19 and 400.84 seconds.

These timings motivated no gate change. They are descriptive only and do not estimate the preregistered full-set median.

## Formal validation and logical futility

The formal run evaluated the first frozen validation fixture, `cap-v2-064`, for each candidate under deterministic decoding and the unchanged 384-token cap:

| Extractor | Schema result | Error | Seconds | Peak process RSS |
|---|---:|---|---:|---:|
| Moondream2 | invalid | no JSON object | 157.57 | 4.58 GiB |
| SmolVLM2-2.2B | invalid | malformed/truncated JSON | 392.10 | 5.62 GiB |

P9A requires validation schema validity of at least `0.98`, and all gate checks must pass. With 32 frozen validation fixtures, one observed invalid output fixes the best possible completed rate at

`31 / 32 = 0.96875`,

even if every unobserved fixture passed. The schema-valid check is therefore mathematically impossible for each candidate. The best-case failure rate is `1 / 32 = 0.03125`, which does not itself violate the separate `0.05` ceiling; the early stop rests only on the fatal schema-valid check.

The preregistration did not state this logical-futility early-stop rule. It was added after plumbing smoke and before viewing formal validation output. This is a procedural deviation, recorded explicitly. It cannot turn a failing candidate into a pass or inflate pass probability because the gate is conjunctive and no possible unobserved result can raise the maximum validity above `31/32`. It does reduce the scope of the negative evidence: atom precision/recall/F1 and bootstrap intervals, determinism, structured error strata, and full-set latency medians were not estimated.

## Gate V2-A decision

No extractor survived P9A. The frozen execution order therefore forbids P9B generative reconstruction, and Gate V2-A fails without a generator/reconstruction claim. No candidate replacement, prompt repair, output repair, fine-tuning, authentication-outcome selection, or model search was performed.

The permitted scientific disposition is to preserve this negative result and reconsider the visual-reconstruction hypothesis. P10 policy optimisation cannot proceed because private computation or policy tuning cannot repair a representation that failed its independent capability gate.

## Evidence map

- `experiments/v2/manifests/capability_v2.jsonl` and `.audit.json`: frozen fixture labels and integrity audit;
- `experiments/v2/manifests/model_acquisition_v2.json`: model revisions, local snapshots, and remote-code review;
- `results/p9-v2/raw/*_futility.jsonl`: append-only formal observations;
- `results/p9-v2/aggregate/*_capability_v2.json`: exact best-case futility calculations;
- `results/p9-v2/raw/*_smoke*.jsonl`: excluded plumbing/development smoke evidence.
