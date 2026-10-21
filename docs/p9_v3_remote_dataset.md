# P9-v3 shared dataset: remote generation

The project author's 2026-10-20 instruction authorizes generating public capability
fixtures following `manual_validation/VLM/SD-Turbo.py`. The shared destination is
`artifacts/downloads/p9_v3`, already excluded from Git. Actual counts and missing
references are recorded in that folder's `STATUS.json`.

## Generation amendment

`experiments/v3/config/remote_generation_v3_4.json` records this narrow amendment
and is included in active contract hashes. Original v3.0-v3.3 frozen files and the
local exact-revision SD-Turbo generator remain unchanged. The remote client selects
`stabilityai/sd-turbo`, rather than the SDXL-Turbo model in the standalone example.

The endpoint is `Ntdeseb/ntia`, API `/generate_image`. Requests use 512x512, one
step, guidance 0, empty negative prompt, and seeds `925031 + 100*family + image`.
These are **requested settings**. The service does not attest actual weights,
execution settings, or internal fallbacks. A Space commit is not a verified model
revision. Retain and disclose this limitation in later experiments. No private
authentication secret is sent; this does not authorize cloud-based authentication.

Each stratum has 120 images: 24 families with five images each. F01-F12 are
development and F13-F24 validation. The naturalistic prompt/seed plan, controlled
construction plan, and support layout are written before remote requests. This is
a capability dataset, not a reconstruction or authentication experiment.

Controlled images use project-authored pictograms and the existing renderer.
References derive from construction. An umbrella shaft was corrected during
pre-inference visual construction QA; the initial affected images/assets/render
plan are retained under `pre_freeze_revisions/controlled-v1`. No perception output
informed the correction.

## Generate

Use Python with Pillow and jsonschema, plus Node >=20. The dependency-free Node
transport uses Gradio REST submission and SSE, with the same arguments as the
user's `Client.predict` example. No local generation weights or GPU are required.

```powershell
python -m experiments.v3.prepare_api_dataset prepare
node experiments/v3/generate_remote_dataset.mjs --execute
# If interrupted, explicitly verify and resume:
node experiments/v3/generate_remote_dataset.mjs --execute --resume
python -m experiments.v3.prepare_api_dataset materialize-remote
python -m experiments.v3.prepare_api_dataset inventory
python -m experiments.v3.prepare_api_dataset previews
python -m experiments.v3.prepare_api_dataset review-page
```

Both scripts accept `--data-root <path>`; the default is the requested folder.
Optional `P9_HF_TOKEN` authenticates requests. Credentials are never copied from
example scripts. Quota/service failures stop generation; there are no automatic
retries, quality-based replacements, alternative seeds, or silent overwrites.
Resume verifies existing raw-file and receipt hashes. A crash orphan blocks resume
and must be investigated, not silently replaced.

Gradio may return WebP. Exact response bytes remain in `raw_images/`; Pillow
materializes RGB PNGs in `images/` without resizing/cropping/content changes. Both
hashes and the decoding operation are recorded separately in provenance receipts.

## Author final references

Prompts describe intended scenes, not observed facts or boxes. Empty
`reference_drafts/` files are deliberately not valid final references.

After generation/materialization, open `artifacts/downloads/p9_v3/review.html`.
The project author draws boxes, records visible closed-label facts, checks each
image without perception-model predictions, and exports JSON. Entity/count/geometry
facts derive deterministically from authored boxes. The page does not show prompts
or call a model. Browser drafts should be exported regularly. Later calibration
may use development only; held-out image authoring does not authorize model tuning
on validation outputs.

If an image lacks predeclared support, flag it. Do not invent facts, obtain VLM
labels, or replace images to improve scores. A shortfall may prevent gate
evaluation. The audits report it rather than manufacture a passing dataset.

```powershell
python -m experiments.v3.prepare_api_dataset import-references `
  --review-plan path/to/naturalistic_reviewed_scenarios_v3_4.json `
  --author 'Project author'
python -m experiments.v3.prepare_api_dataset finalize --author 'Project author'
```

Finalization refuses missing images/references, changed hashes, insufficient
support, and invalid labels/boxes. It writes `capability_manifest_v3_2.json`,
`support_opportunities_v3_2.csv`, a remote-provenance binding, and
`ground_truth_freeze_v3_2.json`. This does not execute an extraction model or
authorize formal validation. All existing execution guards remain required.
`manual_validation/p9-v2-2` can consume the same completed, frozen dataset.

## Software checks

```powershell
python -m unittest experiments.v3.test_api_dataset -v
node --test experiments/v3/test_remote_generation.mjs
```

These checks are not measured model precision. Primary endpoint source:
https://huggingface.co/spaces/Ntdeseb/ntia/blob/9fe9983040fac167f621a62d413e3d3ba19571c7/app.py
