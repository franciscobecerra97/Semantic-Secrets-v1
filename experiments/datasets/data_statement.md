# Data statement and ethics note

Version: P3-v1, 2026-08-24.

## Controlled corpus

The controlled semantic corpus is authored by the researchers to exercise predefined semantic factors. It contains synthetic textual descriptions and structured ground truth, not observations of people and not authentication secrets selected by users.

The corpus is English-only in v1. Its vocabulary, Western-centric scene choices, finite atom types, and deliberately balanced strata limit generalisation. Model behaviour on it cannot establish natural prompt frequency, cross-cultural interpretation, accessibility, memorability, usability, or long-term recall.

## Public-prompt source screen

Source records and access decisions are machine-readable in `sources_v1.json`.

### DiffusionDB — conditionally approved for text-only acquisition planning

- Official repository: <https://github.com/poloclub/diffusiondb>
- Official datasheet: <https://github.com/poloclub/diffusiondb/blob/main/datasheet.md>
- Dataset paper: <https://arxiv.org/abs/2210.14896>
- Verified on: 2026-08-24
- Declared dataset licence: CC0 1.0; repository code: MIT.
- Relevant fields in the official metadata include prompt, generation parameters, hashed username, timestamp, image identifiers, and NSFW scores.

Approved intended use is limited to constructing a versioned text-only prompt/semantic frequency ordering for A4 and sensitivity analysis. The initial acquisition must request metadata only, immediately discard username, timestamp, image identifier, and other contributor-level fields, and retain only filtered normalised prompts, counts, coarse source/version provenance, and content hashes.

DiffusionDB prompts came from a text-to-image service, not authentication. The source authors report that usernames were transformed/removed and provide content rules/removal processes, but public availability and CC0 do not eliminate privacy, contextual-integrity, harmful-content, or representativeness concerns. Results must be described as “under the DiffusionDB-derived attacker distribution,” never as natural password or semantic-secret choice.

### PartiPrompts — approved only as a technical coverage benchmark

- Official repository: <https://github.com/google-research/parti>
- Verified on: 2026-08-24
- Repository licence: Apache-2.0.
- Composition: more than 1,600 English prompts created as a text-to-image capability benchmark.

PartiPrompts may test whether the ontology/parser covers complex objects, relations, text rendering, counts, and compositions. It is curated and not a frequency source, attacker-choice distribution, or human-authentication dataset. Prompts that invoke named artists, sensitive people, or excluded harmful categories are filtered before use.

### Pick-a-Pic v2 — deferred/not approved in P3

- Paper: <https://arxiv.org/abs/2305.01569>
- Project description: <https://stability.ai/research/pick-a-pic>
- Dataset location named by the paper: <https://huggingface.co/datasets/yuvalkirstain/pickapic_v2>
- Checked on: 2026-08-24

The paper describes explicit collection consent and acknowledges possible NSFW content and bias. The current official dataset card could not be retrieved through the available unauthenticated access path, so the exact live revision, licence, removal policy, and fields could not all be verified. Mirrored cards expose user-level identifiers that are unnecessary here. The source is therefore not approved for acquisition. Reconsider only if a distinct scientific need remains after DiffusionDB and the official card/revision/licence can be archived and verified.

## Data minimisation

For public prompts, the preprocessing boundary accepts only fields explicitly allowlisted for the approved analysis. Contributor identifiers are neither copied to the processed table nor hashed again; hashing an identifier would still preserve linkability. Raw source metadata stays outside version control in the ignored acquisition area and is deleted after the processed aggregate passes verification when source/reproducibility obligations permit.

Processed records may contain:

- normalised prompt text during internal filtering;
- a content-derived prompt hash;
- exact duplicate count;
- derived semantic atoms/frequency strata;
- source snapshot/version and processing-config hash; and
- exclusion reason counts in aggregate.

Public release should prefer aggregate token/atom/co-occurrence counts and attack dictionaries stripped of sensitive examples. Whether filtered prompt text itself can be released is a P16 decision after source terms and removal mechanisms are rechecked.

## Harmful and sensitive content policy

Reject or quarantine before model/API processing any prompt reasonably detected as:

- sexual content involving minors or ambiguous age;
- explicit sexual content;
- graphic violence or instructions facilitating violence;
- targeted hate or dehumanisation;
- self-harm encouragement;
- personal data, credential material, addresses, phone/email identifiers, or identity documents;
- non-consensual intimate imagery or sexualisation of identifiable people;
- instructions for wrongdoing; or
- other content forbidden by the selected local model's terms.

Automated filters are a first pass, not proof of safety. Record filter name/version/threshold, quarantine counts, and a small researcher-authored benign/adversarial validation set. Do not publish harmful examples merely to demonstrate filtering. Borderline records are excluded rather than escalated to unnecessary viewing.

## Annotation and human-subject boundary

P3 uses researcher authorship and audit as part of system construction, not participant research. No external annotators, recruited participants, scraped identity linkage, or behavioural inference is allowed. If later work proposes external annotation or studies people's selections, P3 approval no longer applies and ethics review plus an explicit scope change are required before collection.

## Attack ethics

All credential records and accounts used in attacks must be synthetic and local. Public prompt data orders guesses but is never used to target its contributors. Do not query real authentication services, infer contributor identities, or search for reuse by public users. Preserve attack code/configurations and aggregate negative results without retaining unnecessary sensitive source examples.

## Maintenance and removal

Record source snapshot identifiers and access dates. Before any full/final run, recheck the official source for licence, terms, errata, removals, and revised dataset cards. If a source removes records, regenerate the processed snapshot or document why a fixed research snapshot may lawfully and ethically remain; do not silently mix revisions.
