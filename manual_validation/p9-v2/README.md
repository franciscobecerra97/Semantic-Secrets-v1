# P9-v2: manual walkthrough and audit

This folder lets you understand and inspect the old experiment without modifying
its code, dataset, configuration, or saved results. All new files go under
`manual_validation/p9-v2/outputs/`, which is ignored by Git.

These are **supplementary diagnostics**, not a replacement for the historical
failed Gate V2-A. They do not start P9-v3B or authorise later research phases.

## What the experiment actually does

```text
Authored scene graph ---> Pillow draws an image
          |
          +------------> reference labels in capability_v2.jsonl

Image + the same fixed extraction prompt
                 |
                 v
         Pretrained VLM (no training)
                 |
                 v
             Raw answer
                 |
         JSON + graph validation
                 |
                 v
     Compare predicted facts with references
```

The 96 images are programmatic drawings, not diffusion-model outputs. The 64/32
split distinguishes development from evaluation; it does not train the models.
Only a few development images were used historically. Formal validation stopped
after the first invalid validation answer for each model: `31/32 < 0.98`.

The manual tools reuse the original prompt, loaders, parsing, normalisation, and
scoring functions. They never call the original `infer`, `analyze`,
`analyze-futility`, acquisition, or dataset-authoring command. Those commands can
write to historical paths. A drawing recreation here calls only the renderer and
saves its copy in a manual output directory.

## Start in PowerShell

From the project folder:

```powershell
Set-Location "C:\Users\francisco.becerra\Desktop\Semantic Secrets-v1"
$py = Join-Path $PWD ".venv\Scripts\python.exe"
$audit = Join-Path $PWD "manual_validation\p9-v2"
& $py "$audit\00_walkthrough.py"
```

Each script has `--help`. Use this project's existing environment. The historical
dependency records are `experiments/v2/requirements-p9.txt` and the model-acquisition
manifest; do not upgrade packages to make a reproduction appear to work. The
inference script installs no dependencies and downloads no models. Historical
fresh inference requires the existing local Moondream/SmolVLM2 snapshots. Replay and teaching examples import the
original evaluator and its Python dependencies, but do not load model weights.

## 1. Inspect the data and exact prompt

```powershell
& $py "$audit\01_inspect_dataset.py" --gallery --recreate
```

The printed output directory contains:

- `dataset_audit.json`: image hashes, split/style/template counts, structural checks, findings.
- `original.png`, `reference_boxes.png`, `reference.json`: the selected image and its references.
- `extraction_prompt.txt`: exactly what the model is instructed to return.
- `recreated.png`, `recreation_check.json`: a new drawing and its comparison with the old PNG.
- `gallery.html`: offline visual review of all 96 images with reference boxes and graphs.
- `label_review.csv`: blank fields for your audit notes. Blank is not a verified label.

Change the selected example with `--image-id cap-v2-001`. Recreation does not
change originals; Pillow/runtime differences can change encoded PNG bytes.

## 2. First check the saved historical answers: no model inference

```powershell
& $py "$audit\04_replay_history.py"
```

This copies and reparses the retained post-fix development answers for images
000/001 and the formal answer for 064, independently for both models. It excludes
Moondream's initial `KeyError: variant` loader records. It creates reports plus
`historical_gate_arithmetic.json`; both `matches_historical_summary` values should
be `true`. The historical arithmetic uses **32 planned validation images**, even
though the replay includes only three observed images per model.

This checks saved evidence; it does not reproduce model inference or estimate
performance on the 93 unobserved images per model.

## 3. Understand the evaluator using artificial answers

```powershell
& $py "$audit\05_teaching_examples.py"
```

| Example | What you should observe |
|---|---|
| `perfect_reference` | Valid graph, macro F1 = 1. This is an oracle demonstration, not a model result. |
| `valid_but_wrong_scene` | Valid graph but lower semantic accuracy. |
| `malformed_json` | Invalid graph; every reference fact is missed. |
| `fenced_valid_json` | Original parser accepts it; strict raw-JSON check is false. |
| `missing_counts_validator_gap` | Original validator accepts empty counts even when objects exist; count recall is zero. |

Every example has its own `answer.txt`, raw record, and report. Evidence is marked
`artificial_teaching_example_not_model_output`, so it cannot be mistaken for an
extractor observation. Changing these examples never changes the extraction prompt.

## 4. Run one image with both real models

Start with the plan; this creates no files and loads no weights:

```powershell
& $py "$audit\02_run_inference.py" --models both --scope one --image-id cap-v2-064
```

To execute, choose a new run directory and add `--execute`:

```powershell
$run = Join-Path $audit ("outputs\one-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
& $py "$audit\02_run_inference.py" --models both --scope one --image-id cap-v2-064 --run-dir $run --execute
& $py "$audit\03_validate_outputs.py" --run-dir $run
```

Use `--models moondream` or `--models smolvlm2` for only one model. The original
loaders explicitly use CPU; these tools preserve that behaviour. Earlier calls
took about 158 and 392 seconds per image, plus model loading. Timing and exact
answers can vary by environment. Setup/load failures are reported separately and
leave the selected images missing; they are not fabricated invalid model answers.

## 5. Run all 96 images and inspect both original splits

```powershell
$run = Join-Path $audit ("outputs\all-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
& $py "$audit\02_run_inference.py" --models both --scope all --run-dir $run --execute
& $py "$audit\03_validate_outputs.py" --run-dir $run
& $py "$audit\03_validate_outputs.py" --run-dir $run --scope development
& $py "$audit\03_validate_outputs.py" --run-dir $run --scope validation
```

This runs each model once per image, then scores the same saved predictions three
ways. It does not rerun inference merely to separate the results. At historical
timings, one full pass for both models is roughly 15 hours plus loading; this is
an estimate, not a measured full-set runtime.

Invalid answers are retained and the selected run continues. There is **no
automatic futility stop**: a full diagnostic profile is the purpose of this audit.

## 6. Execute the original splits separately

```powershell
$devRun = Join-Path $audit ("outputs\development-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
& $py "$audit\02_run_inference.py" --models both --scope development --run-dir $devRun --execute
& $py "$audit\03_validate_outputs.py" --run-dir $devRun

$valRun = Join-Path $audit ("outputs\validation-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
& $py "$audit\02_run_inference.py" --models both --scope validation --run-dir $valRun --execute
& $py "$audit\03_validate_outputs.py" --run-dir $valRun
```

The development command performs inference, not training. It does not change the
model subsequently loaded for validation. This recipe performs new calls; use the
all-images recipe instead when you only want split reports from one capture.

## 7. Optional repeated inference and resume

Add `--repeat-validation` when creating a run to repeat each selected validation
image once. An all-images run then has 96 primary + 32 repeat calls per model.
The report compares valid canonical graphs; two invalid responses do not count as
a successful deterministic graph pair. Zero repeat pairs means not measured.

After interruption, use the **same selection, models, repeat flag, and directory**:

```powershell
& $py "$audit\02_run_inference.py" --models both --scope all --run-dir $run --resume --execute
```

Only matching, complete raw records are skipped. A truncated JSONL line, changed
source hash, or changed Python/package/platform record blocks resume. Preserve the interrupted run and investigate; no tool
silently repairs or replaces its contents. A process interrupted before an answer
was saved will need to repeat that call. Reports may also be made on partial runs;
their missing image IDs and `complete_primary=false` remain explicit.

## Where the answers and reports are

```text
outputs/<your-run>/
  run.json                    selection, provenance, model identities, evidence kind
  environment.json            Python/package/platform versions
  extraction_prompt.txt       exact fixed prompt (fresh inference)
  moondream.jsonl              raw answers, parsed graphs, errors, timings, hashes
  smolvlm2.jsonl
  reports/<scope>-<timestamp>/
    report.md                 short readable summary
    per_image.csv             filtering and sorting in a spreadsheet
    validation.json           per-image details and aggregate metrics
```

Inference captures predictions; validation is a separate command. The validator
reparses answers instead of trusting saved `schema_valid` flags or parsed graphs.
It reports disagreement if those saved values differ from recomputation.
After adding or updating a manual tool, old captures can still be independently
revalidated. Reports list all manual source changes and current validation hashes.
Changes to historical scoring/configuration files block validation. Resume remains
stricter: it requires the exact original manual code and runtime as well.

Objects match by category and box IoU >= 0.50. Dependent facts require matched
objects; typed values must agree. Both reference and prediction use the original
inverse-relation normalisation. Precision, recall and F1 are computed from the
original true/false-positive/negative counts, with an unweighted mean across the
six task types. An invalid prediction contributes false negatives for every
reference fact. A second, explicitly conditional metric shows valid outputs only.
Missing observations are never silently treated as successful or included in the
observed denominator. The hypothetical 98% format calculation uses the **planned
selection**, not the number of successful calls; it is not the complete original gate.

No confidence intervals are supplied: the 96 images share eight templates, so
ordinary independent-image intervals would suggest unsupported precision. None of
these metrics measures authentication FAR/FRR, guessing resistance, or privacy.

## Audit findings to investigate

1. The prompt's illustrative graph defines `n1` but includes an edge to absent
   `n2`. The original graph validator rejects that example. This is a real prompt
   consistency issue; the audit does not prove it caused either model's failure.
2. The renderer does not read action/relation labels to set poses. Scenario labels
   such as `sleeping`/`riding` are not automatically visible ground truth.
3. There are eight templates reused across both splits. Each template also occurs
   in only one drawing style, confounding style with scene content.
4. Glyphs can extend beyond their declared boxes. Review localisation references
   before interpreting box-based accuracy.
5. The original parser strips code fences and may extract a JSON object from
   surrounding text. Its validity rate is not identical to pure raw-JSON validity.
6. Missing category-count entries can pass the original structural validator,
   despite the prompt requiring a count for each category. Semantic scoring still
   penalises their omission.
7. 98% validity over 32 images requires zero invalid responses. Over 96 images it
   permits one. The historical denominator must not be changed after output.
8. The original analysis functions write fixed historical summary filenames;
   these tools use independent output paths throughout.

The receipts hash source/config/manifest files and observations. Image hashes are
checked before use; reviewed Moondream Python files are checked before loading.
Model revisions and paths come from the historical acquisition manifest. The old
manifest does not contain independent hashes of every weight file; the audit does
not claim to authenticate every weight byte against an upstream release.

## Ready-to-run recipes and checks

The `examples/` PowerShell files work from any current directory:

```powershell
& "$audit\examples\01_no_model_audit.ps1"
& "$audit\examples\02_one_image_both.ps1"                 # plan only
& "$audit\examples\02_one_image_both.ps1" -Execute        # real inference
& "$audit\examples\03_full_dataset.ps1" -Execute
& "$audit\examples\04_separate_splits.ps1" -Execute
```

Run the focused audit tests without model inference:

```powershell
& $py -m pytest "$audit" -q
```

Tests cover scoring, missing observations, separate denominators, corrupt records,
safe output paths, source-bound resume, and fake-loader end-to-end execution.
Dataset-dependent checks require the existing local capability images. These
software tests are not new model-performance evidence.
