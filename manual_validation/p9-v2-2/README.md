# P9-v2-2: VLM API experiment on P9-v3 images

**Current status: prepared, not run. Precision is not measured.** All 240 shared images now exist under `artifacts/downloads/p9_v3`. Controlled construction references are included. The 120 naturalistic references still require project-author review before manifest/support/ground-truth finalization. See [STATUS.md](STATUS.md) and [the dataset guide](../../docs/p9_v3_remote_dataset.md). The historical P9-v2 failure remains unchanged.

This is a new supplementary experiment, not a rerun of the original gate and not
an execution of v3's Grounding DINO / EGTR pipelines. It sends each image and a
fixed extraction prompt to a hosted VLM and scores its JSON graph with the
original P9-v2 parser, validator, box matching, and six-task scorer.

## Models and conditions

| Backend | API | Settings |
|---|---|---|
| Moondream | `moondream.vl(api_key=..., model="moondream3.1-9B-A2B")` | `query(image, prompt)`, provider defaults, matching `VLM/Moondream.py` |
| SmolVLM2 | `gradio_client.Client("HuggingFaceTB/SmolVLM2")` | `/chat`, `max_tokens=500`, matching `VLM/SmolVLM.py` |

Set `MOONDREAM_API_KEY` in the terminal. No key is embedded or copied from the VLM
script. The SmolVLM2 public demo does not require a Moondream key. Calls can incur
Moondream charges or hit public-demo quotas. Neither backend loads weights on
this computer. Hosted model aliases/defaults can change; their exact deployed
weight revisions cannot be claimed as pinned. These are different conditions
from historical CPU inference, including a newer Moondream model.

The graph shape and scorer follow P9-v2. To score **all** P9-v3 reference labels
without silently dropping facts, the new experiment uses v3's frozen vocabulary,
including material, pattern, additional actions, scenes, and entities.
`extraction_prompt.txt` declares this vocabulary before any new outputs. Its
illustrative graph fixes the dangling `n2` reference in the old prompt. This is
an explicit prospective prompt change, not a pure API-versus-CPU comparison.
P9-v2's original prompt and labels are unchanged. New numeric pass/fail thresholds
are not introduced, and the original 98% gate is not reapplied or relabelled.

## Dataset needed before execution

Use the **same completed, frozen P9-v3 dataset**, with:

- `capability_manifest_v3_2.json`: 240 images, 120 controlled + 120 naturalistic;
  60 development and 60 validation images per stratum, with separated families.
- The actual image files and model-output-blind scenario specifications referenced
  by that manifest, with normalized reference boxes and semantic labels.
- `support_opportunities_v3_2.csv` and `ground_truth_freeze_v3_2.json`.

These filenames default to the shared `artifacts/downloads/p9_v3/` folder;
explicit paths can override them. The runner calls the existing v3 ground-truth audit, checks all image
and reference hashes, and converts **all references before any API call**.
Each reference must have one scene, at most eight entities, and explicit category
counts for the P9-v2-shaped graph. Incompatible references block the run instead
of being filtered or fabricated. The runner does not generate or annotate data.

## Run in PowerShell

From the repository root, use your working Python interpreter. For example:

```powershell
$py = Join-Path $PWD '.venv\Scripts\python.exe'
$exp = Join-Path $PWD 'manual_validation\p9-v2-2'
$data = Join-Path $PWD 'artifacts\downloads\p9_v3'
$datasetArgs = @(
    '--manifest', "$data\capability_manifest_v3_2.json",
    '--ground-truth', "$data\ground_truth_freeze_v3_2.json",
    '--opportunities', "$data\support_opportunities_v3_2.csv",
    '--data-root', $data
)

# Preflight only: verify dataset, no API calls.
& $py "$exp\api_experiment.py" @datasetArgs

$env:MOONDREAM_API_KEY = [System.Net.NetworkCredential]::new('', (Read-Host 'Moondream API key' -AsSecureString)).Password
$run = Join-Path $exp ('outputs\api-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
& $py "$exp\api_experiment.py" @datasetArgs --models both --scope all --run-dir $run --execute
```

The API packages used by your VLM examples (`moondream`, `gradio_client`, Pillow)
and the existing v2/v3 evaluation dependencies must be available. The script
installs nothing. Use `--models moondream` or `--models smolvlm2` to isolate one
backend. `--scope development` or `--scope validation` selects an existing split.
With both models and all images, the plan is **480 primary calls**. No automatic
repeat or retry consumes additional credits.

Resume with exactly the same arguments, directory, and environment, adding
`--resume`. Complete records are skipped. Source/config, prompt, dataset, or
runtime changes reject resume; truncated, altered, and duplicate records reject
resume too. API/setup failures interrupt that backend and leave its uncaptured
images explicitly missing; the other backend is still attempted. Invalid model
answers are saved and do not cause early stopping.

Re-score saved raw answers without API calls:

```powershell
& $py "$exp\api_experiment.py" --run-dir $run --report-only
```

## Outputs and precision

Everything stays in `p9-v2-2/outputs/<run>/`:

- `run.json`, `graph_config.json`, `extraction_prompt.txt`: selection, source and
  dataset hashes, model settings, runtime, reference graphs, exact prompt.
- `raw.jsonl`: unchanged answer text, image hashes, record hashes, UTC capture
  times, and client-observed latency. Labels are never sent to a model.
- `execution_errors.jsonl`: transport/setup errors, with environment keys redacted.
- `reports/<timestamp>/report.md`, `precision.csv`, `validation.json`: combined
  results and separate development/validation and controlled/naturalistic results.

The six tasks are object, attribute, count, action, relation, and scene. An object
must have the right category and box IoU >= 0.50. Attributes, actions, and relations
depend on object matches. Inverse relations are normalized on both sides.
Precision = TP/(TP+FP); recall = TP/(TP+FN). Reports include per-task values,
pooled micro precision/recall/F1, and unweighted macro precision/recall/F1.
The old scorer's empty-set convention is retained (precision is 1 when TP=FP=FN=0).

An invalid graph misses all reference facts. Missing API observations are reported
as missing, never scored as successful observations. Precision alone does not
adequately describe failures: read recall, schema validity, and completion too.
Strict raw JSON and the original parser's more permissive schema validity are
reported separately. The original validator's missing-count acceptance behaviour
is preserved; omitted reference counts still reduce count recall.

No confidence intervals or authentication/security claims are made. New API
results will be descriptive diagnostics, not evidence that v3's formal gates
passed. No dataset or original result files are edited.

## Verification

```powershell
& $py -m pytest manual_validation/p9-v2 manual_validation/p9-v2-2 -q
```

Tests use synthetic answers and mocked API clients, not paid API calls. They are
software checks, not measured model precision. The full pytest suite has not run:
the project's Python 3.13 launch failed with `Access is denied`; an available
Python 3.12 lacked the scientific/test dependencies, and isolated dependency
installation was blocked by network access.

Using Python 3.12 and the standard library, nine focused checks passed: compilation,
prompt/vocabulary agreement, validity of the prompt example under the original
validator, v3 reference conversion, invalid-answer false negatives, missing-data
blocking, raw-record integrity, both mocked API call shapes, and error redaction.
The dependency-free historical functions were loaded directly from their unchanged
source for these checks; the full object matcher and pytest suite were not run.
The restored p9-v2 CPU plan also ran successfully. No live model call was made.
Reproduction code and the check receipt are in `outputs/preparation-20261020/`.

The removed p9-v2 Moondream 3 additions were preserved in the ignored
`archive/p9-v2-before-restoration/`. Earlier output folders were left untouched.
Git contains only the combined walkthrough commit, so p9-v2 was restored to its
original two-backend CPU behaviour rather than claimed byte-identical to an
unavailable earlier snapshot.

API references checked 2026-10-20:

- https://docs.moondream.ai/skills/query/
- https://github.com/m87-labs/moondream-python
- https://huggingface.co/spaces/HuggingFaceTB/SmolVLM2/blob/main/app.py
