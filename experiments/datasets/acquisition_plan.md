# Public prompt acquisition and preprocessing plan

Status: design only. No public corpus was downloaded in P3.

## 1. Approved source roles

| Source | Role | P3 state |
|---|---|---|
| Project-controlled concepts | Technical ground truth, near neighbours, same-concept transformations | Smoke catalog approved. |
| DiffusionDB metadata | Conditional empirical A4 ordering and training-only frequency bands | Acquisition deferred until P8 needs it. |
| PartiPrompts | Technical ontology/parser coverage only | Acquisition deferred until P4/P5 needs it. |
| Pick-a-Pic v2 | Possible distinct prompt distribution | Not approved; official live card/licence verification incomplete and no distinct need yet. |

## 2. Script interfaces to implement when authorised

P8 should implement narrow scripts with these interfaces rather than a general web scraper:

```text
acquire_prompts.py plan \
  --source sources_v1.json#diffusiondb \
  --snapshot <immutable revision or recorded ETag> \
  --output experiments/datasets/raw/<source>/<snapshot>/acquisition-plan.json

acquire_prompts.py fetch-metadata \
  --plan <plan.json> \
  --expected-sha256 <verified hash> \
  --acknowledge-terms

preprocess_prompts.py \
  --input <local metadata file> \
  --config config/public_prompt_filter_v1.json \
  --output experiments/datasets/processed/<source>/<version>/
```

`plan` performs no network write. `fetch-metadata` refuses moving URLs, missing expected hashes, unverified licence fields, unapproved sources, or image archives. `preprocess_prompts` reads only allowlisted columns and never writes contributor identifiers.

## 3. DiffusionDB minimal path

1. Recheck official repository, datasheet, licence, terms reference, removal mechanism, and Hugging Face dataset revision.
2. Pin an immutable revision/commit when supported and record URL, ETag/size, SHA-256, access date, tool version, and operator.
3. Acquire only the smallest text metadata table needed. Do not use the 1.6/6.5 TB image archives for frequency modelling.
4. Load only the prompt and content-score fields required for filtering. Explicitly reject username, timestamp, image UUID/name, and generation/session linkage columns at the parser boundary.
5. Apply Unicode normalisation, control-character removal, whitespace collapse, language/length rules, and harmful/sensitive-content filters.
6. Compute a case-folded exact-dedup key and a separate salted internal content hash; aggregate counts before discarding row-level linkage.
7. Derive atom/token/co-occurrence frequencies on the training partition only. Freeze vocabulary, quantile boundaries, and processing hash before validation/test evaluation.
8. Produce aggregate exclusion counts, not a gallery of rejected examples.
9. Delete or retain the local raw metadata only according to source obligations and the approved reproducibility plan; never commit it.

## 4. PartiPrompts minimal path

1. Pin the official Google Research repository commit and verify its Apache-2.0 licence.
2. Acquire `PartiPrompts.tsv` only.
3. Preserve official category/challenge fields for coverage analysis, but do not treat them as population weights.
4. Apply the same sensitive/harmful-content policy and separately flag named-artist/person references.
5. Report ontology coverage and parser failures; do not merge prompt counts into the DiffusionDB empirical ordering.

## 5. Preprocessing output contract

The internal processed prompt record is:

```json
{
  "prompt_hash": "sha256:<content-derived value>",
  "normalised_prompt": "internal-only filtered text",
  "exact_duplicate_count": 1,
  "language": "en",
  "source_id": "diffusiondb",
  "source_snapshot": "<immutable revision>",
  "filter_version": "public-prompt-filter-v1",
  "semantic_atoms_version": "<filled after P5>"
}
```

No user ID, username hash, timestamp, image ID/URL, session/ranking ID, or source-row neighbours are permitted. The release form omits `normalised_prompt` by default and contains aggregate statistics/dictionaries only.

## 6. Required quality report

Every acquisition run must produce:

- source/licence/terms verification record and access date;
- requested/downloaded byte counts and SHA-256;
- input and retained row counts;
- exact duplicate counts;
- missing/invalid/overlength/language exclusion counts;
- every harmful/sensitive filter name, version, threshold, and exclusion count;
- identifier-column rejection test result;
- processed schema and config hashes;
- frequency-band boundaries derived without test data; and
- known limitations and any deviations from this plan.

## 7. Failure policy

Fail closed if the source licence/revision cannot be verified, if expected fields change, if identifiers leak into processed output, if filtering cannot be audited, or if source terms conflict with the intended use. The fallback is the controlled synthetic distribution with correspondingly narrower attacker claims, not a less documented scrape.
