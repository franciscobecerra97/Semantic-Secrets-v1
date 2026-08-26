# Frozen component compatibility audit

Audit date: 2026-08-26. This is pre-execution engineering evidence only. No model artifact was downloaded or executed.

## Grounding DINO Tiny and SigLIP2 Base

The active configuration identifies Hugging Face snapshots, not mutable default branches:

| Component | Frozen source | Revision | Licence recorded upstream/config |
|---|---|---|---|
| Grounding DINO Tiny | `IDEA-Research/grounding-dino-tiny` | `a2bb814dd30d776dcf7e30523b00659f4f141c71` | Apache-2.0 |
| SigLIP2 Base 384 | `google/siglip2-base-patch16-384` | `f775b65a79762255128c981547af89addcfe0f88` | Apache-2.0 |

Both are consumed through local-only Transformers APIs in `/opt/envs/modern`. This avoids compiling the separate GroundingDINO repository extension, which is not the artifact frozen by v3.1. The modern lock uses Python 3.10, PyTorch 2.4.1, torchvision 0.19.1, and Transformers 4.49.0. The container build, local-only load, exact preprocessing objects, CUDA smoke, and full file inventory remain mandatory verification; the versions are not permission to fall back to a hub default.

Before any output, the adapters name and bound their component-local `[0,1]` score domains: Grounding DINO postprocessed score; SigLIP2 sigmoid of `logits_per_image`; EGTR object softmax, relation sigmoid, and connectivity sigmoid. SigLIP2 tasks require both a development-fitted threshold and top-two margin. The preparation code freezes these score meanings but no numeric threshold; all numeric values still come only from development and are frozen before validation.

## EGTR official artifact

The exact official repository revision `7f87450f32758ed8583948847a8186f2ee8b21e3` declares this historical stack:

```text
torch==1.12.1+cu113
torchvision==0.13.1+cu113
transformers==4.18.0
tensorboard==2.9.1
pytorch-lightning==1.6.4
timm==0.5.4
pycocotools==2.0.5
ninja==1.10.2
matplotlib==3.4.3
pandas==1.2.5
```

The official README names `nvcr.io/nvidia/pytorch:21.11-py3`, compiles `lib/fpn`, evaluates with one V100, and links the VG checkpoint as Google Drive file `18phcRxbrEI7HqIuM2OLAPuwAF5k3pUC2`. The Dockerfile retains that base and stack in the system environment. EGTR runs in a subprocess and returns only object/relation/connectivity evidence.

### `pycocotools==2.0.5` build compatibility

The frozen EGTR dependency `pycocotools==2.0.5` declares the unbounded build requirement `cython>=0.27.3`. Under PEP 517 build isolation, current installers can therefore select Cython 3, which is incompatible with this release's `pycocotools/_mask.pyx` and fails during Cythonization. This is a build-tool incompatibility, not a scientific dependency failure.

`requirements-egtr-build.lock` pins the build-only compiler to `Cython==0.29.36`. The Dockerfile installs that pin first and installs the unchanged `pycocotools==2.0.5` with `--no-deps --no-build-isolation`, forcing compilation to use the pinned compatible Cython without resolving a separate runtime dependency set. The subsequent official EGTR lock still contains and verifies `pycocotools==2.0.5` and its dependencies; no EGTR runtime package, model, revision, preprocessing rule, or scientific parameter is substituted.

The modern Transformers stack cannot safely coexist with EGTR's old Torch/Transformers ABI in one Python environment. Separate processes avoid import/library upgrades crossing the boundary. CUDA-driver compatibility must be verified on the selected Pod; no model substitution, quantization, or input/preprocessing change is an allowed compatibility remedy.

## Fail-closed artifact questions

The archive bytes have not been acquired, so its extracted layout, byte size, SHA-256, embedded category metadata, exact checkpoint count, and separate checkpoint terms remain unknown. The official evaluation code also initializes `SenseTime/deformable-detr` and constructs the official feature extractor. v3.1 does not authorise resolving a mutable upstream dependency implicitly. The prepared worker therefore requires reviewed local config, transform, category metadata, base-model provenance, and exactly one checkpoint. Missing material is a pipeline-blocking acquisition/provenance result and may require a prospective project decision before inference; it is never repaired with an online download.

## Scientific boundary

```text
component-local model output
        -> exact closed-label intersection and frozen threshold adapter
        -> bounded visual-observation-v3.1.0 record
        -> semantic-compiler-v3.0.0
```

The compiler owns canonical IDs, duplicate handling, counts, geometry, inverse relations, graph invariants, and credential serialization. Neither learned environment can write final graph JSON.

Primary upstream records audited:

- <https://github.com/naver-ai/egtr/tree/7f87450f32758ed8583948847a8186f2ee8b21e3>
- <https://raw.githubusercontent.com/naver-ai/egtr/7f87450f32758ed8583948847a8186f2ee8b21e3/requirements.txt>
- <https://huggingface.co/IDEA-Research/grounding-dino-tiny/tree/a2bb814dd30d776dcf7e30523b00659f4f141c71>
- <https://huggingface.co/google/siglip2-base-patch16-384/tree/f775b65a79762255128c981547af89addcfe0f88>
