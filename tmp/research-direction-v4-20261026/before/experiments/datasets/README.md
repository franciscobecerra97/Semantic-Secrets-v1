# Controlled semantic dataset methodology v1

Status: P3 methodology and smoke assets were approved on 2026-08-24. P6 froze and audited the 60-family pilot catalog and compact manifests on 2026-08-24. Pilot image/model execution remains unapproved outside a later explicit phase; full acquisition and full-scale generation are not approved.

This directory defines inputs for technical experiments on semantic representations. It does not contain authentication credentials, participant data, or evidence about human memory, usability, or natural secret selection.

## 1. Research roles

The controlled corpus supports:

- RQ1 technical stability across generator seeds, controlled paraphrases, styles, layouts, and model slots;
- RQ2 separation among same-concept, targeted one-atom-neighbour, and unrelated concepts;
- RQ3 construction of controlled random, partial-information, and later public-corpus/AI attacker distributions;
- RQ6 a paired `prompt -> image -> semantics` versus `prompt -> semantics` comparison;
- A1/A4/A5/A8 and E1–E8/E12–E14/E16 as mapped in `docs/security_model.md`.

It cannot support claims about what people remember, select, prefer, or reproduce.

## 2. Versioned assets

| Asset | Purpose |
|---|---|
| `ontology_v1.json` | Allowed atom types, value conventions, complexity strata, transformations, and harmful-content exclusions. |
| `schema/concept.schema.json` | Machine-readable family/base/one-atom-neighbour schema. |
| `schema/input_manifest.schema.json` | Label-free generator/extractor input row schema. |
| `schema/label_manifest.schema.json` | Ground-truth row schema held away from model execution. |
| `schema/pair_manifest.schema.json` | Same/near/unrelated comparison schema held away from model execution. |
| `config/design_v1.json` | Smoke/pilot/full scaling and deterministic split/transform settings. |
| `config/design_p6_v1.json` | Versioned P6 approval for pilot catalog/manifests; leaves the frozen P3 design unchanged. |
| `concepts/smoke_v1.json` | Twelve hand-audited concept families used only to validate the method. |
| `concepts/pilot_v1.json` / `pilot_v1.audit.json` | Sixty P6 pilot families and the model-output-independent lexical audit. |
| `sources_v1.json` | Public-source licence, ethics, identifier, and distribution screen. |
| `split_manifest.py` | Standard-library manifest generator and validator. |
| `manifests/smoke_v1.*` | Generated, compact P3 manifests; no images or model representations. |

Every later catalog or manifest must increment its version instead of overwriting a frozen artifact.

## 3. Factorial design

### Controlled factors

Each concept family has one base concept and at least one targeted negative that replaces exactly one atom. Across families, v1 covers:

- object identity;
- attributes including colour and material;
- explicit counts;
- actions;
- directional and non-directional spatial relations;
- scenes;
- planned object-frequency bands; and
- complexity levels 1–5.

The frequency labels in the smoke catalog are design strata (`common_candidate`, `mid_candidate`, and `rare_candidate`), not measured population frequencies. P8 may replace them with quantiles computed from a frozen training-only public-prompt corpus. Test data never defines frequency weights or bands.

### Positive transformations

The base concept is held semantically constant while one technical factor changes:

1. generator random seed;
2. researcher-authored controlled paraphrase;
3. non-artist-referential rendering style;
4. layout/aspect instruction that explicitly preserves declared relations; or
5. bound generator/model slot after D1.

This is a fractional factorial design. It varies one factor from the enrolment row at a time rather than generating the full Cartesian product. That makes effects interpretable and controls compute. Interaction cells may be added only through a versioned pilot amendment justified by observed variance.

### Negative transformations

- **Targeted near neighbour:** replace exactly one ground-truth atom while preserving all other atom signatures. The changed type/from/to values are stored only in the label manifest.
- **Unrelated negative:** pair enrolment with a base concept from a different family in the same split. The pairing rotates deterministically and prefers a different complexity/frequency stratum.
- **Adversarial negative:** reserved for P8; it uses the frozen A8 interface and never changes ground-truth labels after observing matcher output.

Near/unrelated labels, expected atoms, family grouping, and split membership are never passed to generator or extractor execution. The input and label manifests join only by opaque `row_id` during evaluation.

## 4. Scale ladder

| Stage | Families | Purpose | Approval |
|---|---:|---|---|
| Smoke | 12 | Hand-audit ontology, one-atom edits, schema, deterministic generation, split isolation, and pipeline interfaces. | Approved. No model/image execution is implied by P3. |
| Pilot | 60 | Estimate family-level variance, failure rates, clustering, effect sizes, and resource cost; eliminate weak candidates. | Catalog/manifests approved and frozen by P6; direct-text P6 run complete. Image execution is not implied. |
| Full | Not fixed | Confirmatory evidence with a frozen family count derived from pilot uncertainty and resource feasibility. | Forbidden until P6/P7 requests it and a decision record freezes the size. |

The full size is deliberately `null` in `design_v1.json`. Choosing a convenient round number is not acceptable.

## 5. Manifest row construction

For each family, the generator emits these image-path rows:

```text
1 enrolment row
+ (number of seeds - 1) seed-only rows
+ (number of prompt variants - 1) paraphrase-only rows
+ (number of styles - 1) style-only rows
+ (number of layouts - 1) layout-only rows
+ (number of generator slots - 1) model-only rows
+ one canonical row per targeted near neighbour
```

Each image-path input references a deduplicated `text_input_id` derived from the unstyled core prompt. The text-only path therefore receives the same semantic text without image-only style, layout, or random-seed controls. This preserves the paired RQ6 comparison without pretending that rendering nuisance variables exist in text-only processing.

Outputs are separated as:

- `*.inputs.jsonl`: execution fields only;
- `*.text_inputs.jsonl`: deduplicated text-only inputs;
- `*.labels.jsonl`: concepts, atoms, relationships, splits, and provenance;
- `*.pairs.jsonl`: same/near/unrelated evaluation pairs; and
- `*.provenance.json`: content hashes and generator parameters.

## 6. Splits and leakage controls

- The independent grouping unit is `family_id`, not an image, prompt, or trial.
- Every base, paraphrase, style/layout/seed/model trial, and one-atom neighbour in a family remains in one split.
- Split assignment is a deterministic SHA-256 ordering of `split_seed || family_id`, followed by frozen stage quotas.
- Smoke quotas are 6 train, 3 validation, and 3 test families. Pilot quotas are 36/12/12.
- Thresholds, canonicalisation choices, empirical frequency bands, attack ordering, and any learned weights use train/validation only.
- Test labels stay sealed from model/candidate selection until the relevant full protocol is frozen.
- Near-neighbour and unrelated pairs are constructed inside a split only.
- Prompt text itself necessarily carries semantics; “label leakage” here means that ground-truth atoms, same/negative relationship, changed-atom metadata, family grouping, and evaluation split are absent from execution inputs.

## 7. Annotation and quality control

Smoke concepts are researcher-authored, not participant-provided. Two passes are required before model execution:

1. **Authoring pass:** create the base atoms, controlled prompts, and exactly one replacement for each near neighbour.
2. **Blind audit pass:** check that prompts express every listed atom, contain no undeclared semantic change, avoid ambiguous pronouns, avoid named living-artist imitation, and comply with harmful-content exclusions.

Automated validation then checks:

- schema and required fields;
- unique IDs;
- referential integrity for atom subjects/objects;
- exactly one atom replacement per targeted neighbour;
- coverage of every atom type, complexity level, and planned frequency band;
- deterministic content hashes and manifests;
- no family across multiple splits;
- input/label/pair join integrity; and
- no forbidden label fields in execution inputs.

If an image fails to depict an intended atom, that is an observed generator/extractor outcome; the ground truth is not retroactively edited. A genuinely ambiguous or erroneous authored concept is corrected only in a new catalog version with an amendment record.

## 8. Provenance and deduplication

- Canonical JSON uses UTF-8, sorted keys, and compact separators before SHA-256 hashing.
- `catalog_sha256`, `ontology_sha256`, and `design_sha256` identify the exact inputs to a manifest.
- `row_id` and `text_input_id` are deterministic opaque SHA-256 prefixes over versioned canonical fields.
- Public prompts will be Unicode-normalised, whitespace-collapsed, case-folded only for a deduplication key, and retained in original normalised form only when allowed.
- Exact duplicate prompts are represented once for dictionary ranking with a frequency count. Near-duplicate clustering, if used, must be versioned and sensitivity-tested rather than silently merging semantic distinctions.
- Model-generated images and representations later use content hashes plus complete model/configuration identifiers; regeneration never overwrites mismatched content.

## 9. Cache, release, storage, and compute

Allowed local caches after their producing phase authorises them:

- project-authored prompts and labels;
- generated images whose model licence permits research storage/release;
- structured representations and embeddings when their model terms permit it;
- compact public-prompt frequency tables with no contributor identifiers; and
- hashes, manifests, configurations, metrics, and aggregate results.

Not approved for release:

- public-source usernames/user IDs, timestamps, image UUIDs, or contributor linkage;
- unfiltered harmful/NSFW or sensitive prompt examples;
- third-party images unless redistribution is separately verified;
- raw public prompt corpora when the source terms or removal requests make redistribution inappropriate; and
- model weights not licensed for redistribution.

For `N` planned generated images, budget using measured P4 values:

```text
generation GPU-hours = N * measured_seconds_per_image / 3600
image storage range   = N * measured_low/high_bytes_per_image
representation bytes  = N * measured_bytes_per_representation
```

Before generation, write the measured values and total into a decision record. Planning bounds use 2–6 MiB per lossless 1024×1024 image only for storage reservation, not as a measured outcome:

- smoke: 84 image-path rows, approximately 0.16–0.49 GiB;
- pilot: 660 planned image-path rows, approximately 1.29–3.87 GiB;
- full: unresolved until the pilot-derived family count and transformation cells are frozen.

No compute-time estimate is asserted before P4 measures a generator.

## 10. Reproduction commands

From the repository root:

```text
python experiments/datasets/split_manifest.py generate --stage smoke
python experiments/datasets/split_manifest.py validate --stage smoke
python -m unittest experiments.datasets.test_dataset_design
```

Running `generate` twice must produce byte-identical manifest files and provenance hashes. Pilot/full generation fails closed until their versioned catalogs exist and full approval is recorded.

## 11. Phase boundary

P3 approved the ontology, smoke catalog, pilot methodology, source screen, and manifest machinery. P6 subsequently froze the pilot catalog/manifests and produced direct-text pilot results. Neither phase approves public-corpus acquisition, pilot image generation, annotation by participants, full scale, or any security/usability claim.
