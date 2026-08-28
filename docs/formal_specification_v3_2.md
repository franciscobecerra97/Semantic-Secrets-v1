# Formal specification v3.2 addendum: project-authored ground truth

Status: prospective P9-v3A.2 correction frozen before any P9-v3B capability image, model acquisition, or inference. It amends only the ground-truth method and associated execution blocker in v3.0/v3.1. Every pipeline, model, revision, label, preprocessing rule, resolution, threshold, metric, Gate V3-A1 criterion, resource limit, image/support count, and phase dependency remains unchanged.

## 1. Binding composition

The active capability contract is the composition of `semantic-secrets-preregistration-v3.0.0`, the v3.1 suitability amendment, and `semantic-secrets-preregistration-v3.2.0`. The v3.0 and v3.1 human-annotation clauses remain historical records but are superseded for execution by v3.2.

P9-v3B is technical dataset and model evaluation. It has no human participants and no human annotators. The missing-second-annotator condition is therefore not an execution prerequisite.

## 2. Project-authored reference semantics

Each `cap-v3-*` image has one versioned, project-authored reference scene specification. It records the image/family/split identity, closed-label reference entities, normalized reference boxes, and applicable semantic atoms. The controlled stratum derives these facts from its authored scene construction. The naturalistic stratum uses the same closed schema: the project author records the final image reference without consulting any perception output.

The existing support-opportunity table remains the scored ground-truth surface. Every positive or applicable-negative opportunity links to its image, scenario specification, reference entity scope, normalized boxes where applicable, atom type, polarity, and exact closed-label value. Opportunity IDs and ordering are deterministic. The frozen v3.1 opportunity counts and type roles do not change.

## 3. Model-blind freeze

Before any development smoke or formal inference, the following must be complete:

1. all 240 final image hashes and manifest rows;
2. all 240 scenario specifications and their hashes;
3. the complete development/validation support-opportunity table;
4. deterministic manifest, split, reference, box, label, and opportunity-count audits; and
5. a `ground-truth-freeze-v3.2.0` record binding the active config hashes and aggregate SHA-256 values.

The freeze record asserts that ground truth was project-authored, was not derived from model predictions, and was completed before any perception output was produced or inspected. The formal guard independently verifies every available file/hash/link and fails closed. The assertion is provenance evidence, not permission to modify ground truth after output.

## 4. Execution boundary

Model acquisition may be separately authorised before the ground-truth freeze because acquisition produces no image prediction. Any smoke, development inference, validation inference, or repeat requires the frozen ground-truth record. Formal validation additionally requires the existing threshold, model-acquisition, GPU-environment, exact-commit/container, and explicit authorization records.

This correction authorises no model acquisition, image generation, inference, P9-v3C, P10, or later cryptographic work by itself.
