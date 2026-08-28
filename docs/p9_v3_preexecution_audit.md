# P9-v3A.1 pre-execution suitability amendment

> **Historical-method note (2026-08-28):** This audit correctly records why v3.1 introduced a second-annotator blocker, but P9-v3A.2 supersedes that methodology before any capability image or model output. P9-v3B has no human annotators. Its active prerequisite is the deterministic project-authored, model-output-blind ground-truth freeze in `formal_specification_v3_2.md` and `preregistration_v3_2.json`. The pipeline, support, gate, and resource findings below remain binding.

Status: complete prospective design audit on 2026-08-25. This amendment was made before any v3 model weight, capability image, perception output, validation output, or authentication result existed. P9-v3B was not executed.

## Version boundary

- `v3.0.0` is the immutable initial P9-v3A freeze in commit `8e44caa`.
- `v3.1.0` is this prospective, outcome-independent suitability amendment.
- `experiments/v3/config/preregistration_v3.json` and `visual_observation_v3.json` retain their historical v3.0.0 meaning.
- Future P9-v3B execution is bound by `preregistration_v3_1.json`, `visual_observation_v3_1.json`, this document, and `formal_specification_v3_1.md`.

## GPU rule correction

Machine capacity is not pipeline consumption. Full inference may use any documented dedicated research GPU, including a device with more than 24 GiB installed memory. Before inference, record the GPU model and capacity, driver, CUDA or ROCm version, framework and environment lock, CPU, and system RAM.

Gate V3-A1 continues to require measured peak pipeline allocation of at most 24 GiB VRAM and measured peak process RSS of at most 32 GiB. A larger device does not increase either limit. The measurement method, warm-up, synchronization, allocator reset, and included components are frozen in the v3.1 config. Hardware may be selected for availability or implementation compatibility before validation; it may not be selected or changed after validation outcomes to alter semantic accuracy. No pre-output implementation evidence justified changing the numeric 24 GiB bound.

## Bounded graph-native suitability audit

The audit compared only SGTR, EGTR, and one newer artifact-visible candidate, ROBIN/Synthetic Visual Genome.

| Criterion | SGTR | EGTR | ROBIN/Synthetic Visual Genome |
|---|---|---|---|
| Primary publication | CVPR 2022 | CVPR 2024 | CVPR 2025 |
| Official code | `Scarecrow0/SGTR` at `03bdd6554f12d521807cf95fe6a7daa7d3bb01dc` | `naver-ai/egtr` at `7f87450f32758ed8583948847a8186f2ee8b21e3` | `jamespark3922/SyntheticVG` at `29146b9d81333e0af039c617b22ccf618031c07c` |
| Released weights | SGTR(VG) SharePoint link in official README | `egtr_vg.tar.gz`, official Google Drive file `18phcRxbrEI7HqIuM2OLAPuwAF5k3pUC2` | Stage-2 ROBIN-3B Hugging Face repository; other stages remain TBD |
| Licence/provenance | Repository `LICENSE` is Apache-2.0, but README badge says MIT; checkpoint has no separate terms | Repository and release page state Apache-2.0; checkpoint is linked by the official repository; acquisition record must still capture bytes and SHA-256 | Code is Apache-2.0; model card lacks complete licence metadata and several training/evaluation releases remain TODO |
| Data/vocabulary | Visual Genome and Open Images V6; ResNet-101 configuration | Visual Genome 150 objects/50 predicates and Open Images V6; v3 selects the VG checkpoint | Open-ended dense relationships from several datasets |
| Local inference path | Legacy Python 3.8/PyTorch 1.10/cvpods; official test command uses four GPUs | Frozen CUDA 11.3, PyTorch 1.12.1, Transformers 4.18 stack; official evaluation uses one V100 | Multi-component SAM/OpenCLIP/Qwen pipeline with a 4B autoregressive model and broad dependency surface |
| Output boundary | Entity/predicate proposals and graph assembly can be adapted | Direct `logits`, normalized `pred_boxes`, `pred_rel`, and `pred_connectivity` tensors map deterministically to bounded records | Autoregressively authors object and relation text/JSON; parsing and semantic-nearest-label mapping are part of the published evaluation |
| Adaptation risk | High: thin two-commit repository, older stack, licence presentation conflict | Moderate: old but explicit stack; shallow tensor adapter; checkpoint acquisition remains fail-closed | High: reintroduces structured generation, extra region models, open-ended labels, and serialization risk |

EGTR replaces SGTR before execution. This is not performance selection: no project image or model output exists. EGTR is more recent, has a clearer one-GPU evaluation path, officially released checkpoints, a single Apache-2.0 repository licence, and bounded tensor outputs that preserve the model/compiler separation. SGTR remains in the historical v3.0.0 record and is not an executable v3.1 candidate.

ROBIN is artifact-visible but is not retained. Its autoregressive multimodal path constructs scene-graph text/JSON and the published evaluation maps generated text to labels. That would recreate part of the monolithic structured-generation risk rejected by v3, while adding SAM/OpenCLIP dependencies and incomplete artifact metadata. DSGG was not added because no verified official reproducible source/checkpoint pair was established in this bounded audit.

## Final two-pipeline freeze

Pipeline A remains `v3.1-gdino-siglip2`. Grounding DINO Tiny supplies entity boxes; SigLIP2 Base supplies closed-label crop, pair-crop, and scene scores. Pair-crop unary/binary classification is explicitly an experimental compositional hypothesis, not an established relation detector. Its failure is a valid result.

Pipeline B is `v3.1-egtr-siglip2`. EGTR(VG) supplies bounded entity, box, relation, and connectivity tensors. Deterministic code applies the exact label intersection, thresholds, tuple construction, inverse normalization, and compiler rules. SigLIP2 supplies the same attribute and scene roles as Pipeline A. EGTR never writes credential JSON.

Both pipelines freeze repositories, revisions, checkpoint identities, licence records, acquisition hash rules, adapters, label intersections, development-only thresholds, resource limits, and fail-closed behavior in `visual_observation_v3_1.json`. No replacement is permitted after any v3.1 validation output.

## Dataset support-feasibility audit

An opportunity, not an image, is the support unit. A positive opportunity is one visible reference atom within its declared scope. An applicable negative is one predeclared false closed-label alternative for the same image, entity, ordered pair, category, or scene scope. The experiment does not count every absent vocabulary label as an independent negative.

The following validation design applies separately to the 60 controlled and 60 naturalistic validation images. `F01-F12` means all twelve five-image validation families; a six-family set contributes 30 images. Development mirrors the layout for threshold fitting but never contributes validation support.

| Atom type | Role | Positive opportunities | Applicable negatives | Families | Concentration on contributing images | Feasible in each stratum |
|---|---:|---:|---:|---|---|---|
| entity | primary | 120 | 120 | F01-F12 | 2 positive + 2 absent-category queries/image | yes |
| colour | primary | 60 | 60 | F01-F12 | 1 + 1 on a focal entity/image | yes |
| size | exploratory | 30 | 30 | F01-F06 | 1 + 1 on 30 images; 0 on 30 | not gate-evaluable |
| material | exploratory | 30 | 30 | F07-F12 | 1 + 1 on 30 images; 0 on 30 | not gate-evaluable |
| pattern | exploratory | 30 | 30 | F01-F06 | 1 + 1 on 30 images; 0 on 30 | not gate-evaluable |
| count | primary structural | 60 | 60 | F01-F12 | 1 true + 1 false bucket/image | yes |
| unary action | exploratory | 30 | 30 | F07-F12 | 1 + 1 on 30 images; 0 on 30 | not gate-evaluable |
| binary interaction | primary structural | 60 | 60 | F01-F12 | 1 true + 1 false predicate/ordered pair/image | yes |
| geometry relation | primary structural | 60 | 60 | F01-F12 | 1 true + 1 false relation/ordered pair/image | yes |
| scene | exploratory | 30 | 30 | F01-F06 | 1 + 1 on 30 images; 0 on 30 | not gate-evaluable |

The primary set is `entity`, `colour`, `count`, `binary_interaction`, and `geometry_relation`. All primary facts can share two to four visible entities; the naturalistic scene need not contain ten independent facts or dozens of objects. At most two entity positives plus four scoped primary facts are required per image, with optional facts concentrated in only half the families.

The v3.0 blanket minimum is superseded. A type is gate-evaluable only when its frozen validation manifest contains at least 60 positive and 60 applicable-negative opportunities in each stratum. Insufficient support yields `not_gate_evaluable`; it is neither a pass nor an automatic failure of other types. Exploratory types remain in `L_visual` but cannot enter `L_cred-v3.1.0` under the frozen 30/30 design. Support counts and family assignments are fixed before image creation and cannot be expanded after model output.

This amendment does not weaken Gate V3-A1: a complete pipeline must still qualify entity plus at least two further types, including one structural type. Pipeline types may not be unioned.

## Historical v3.1 annotation feasibility (superseded by P9-v3A.2)

Two independent, model-blind human annotations remain the target protocol for the naturalistic stratum. The repository contains no evidence that two project researchers are guaranteed. Therefore naturalistic image creation and P9-v3B execution are blocked until an annotation-resource record names both annotators and confirms availability.

The prospective replacement is one project researcher plus one qualified independent external annotator. Both receive the same frozen visibility rubric and randomized image identifiers, annotate independently without perception outputs or model-assisted labels, and sign a conflict/provenance record. Disagreements are resolved by documented consensus against the rubric before inference; raw annotations, agreement, and adjudication are retained. A second pass by the same person is not treated as independent annotation. Researcher annotation of project-authored non-sensitive images remains technical dataset work, not a human-subject usability study.

## Exact Gate V3-A1 after audit

For one complete frozen pipeline, all of the following must hold:

1. All 320 or more compiler invariants pass exactly, including 100% graph/failure oracle match, result-schema validity, and byte repeatability, with zero malformed output.
2. Pipeline failure rate is at most 0.05 and its Wilson 95% upper bound is at most 0.10.
3. Canonical observation and graph repeat equality are each at least 0.95 with Wilson lower bound at least 0.90.
4. Measured pipeline peak VRAM is at most 24 GiB, measured peak RSS at most 32 GiB, median latency at most 30 seconds/image, and p95 at most 60 seconds/image. Installed GPU capacity is not a gate.
5. Every eligible type has at least 60 positive and 60 applicable-negative validation opportunities in each stratum and independently passes, in both strata: precision point at least 0.90 and family-bootstrap lower bound at least 0.85; recall point at least 0.70 and lower bound at least 0.60; F1 point at least 0.80 and lower bound at least 0.70; and coverage point at least 0.75 with Wilson lower bound at least 0.65.
6. The one pipeline's `L_cred` includes entity, at least two additional eligible types, and at least one of count, geometry relation, unary action, or binary interaction.

Failure of one pipeline does not stop evaluation of the other unless the compiler gate or annotation/resource blocker makes the complete experiment invalid. Cross-pipeline union, validation-driven hardware/model/label changes, and post-output support expansion are forbidden.

## Execution boundary

No v3 inference, model-weight download, capability-image creation, validation output, P9-v3C, P10, policy tuning, or cryptographic work occurred in this audit. At the time of v3.1, P9-v3B was additionally blocked until the two-human resource was documented; P9-v3A.2 later superseded that blocker with the project-authored ground-truth freeze before any output.

The repository currently contains preregistration/configuration tests, not an implemented semantic compiler or 320 executed compiler cases. The audit verifies that the frozen eight-category case plan still totals exactly 320 and that its required pass rates remain unchanged. Actual execution of those 320 or more invariant cases belongs to P9-v3B; claiming that they already passed would exceed the available evidence.
