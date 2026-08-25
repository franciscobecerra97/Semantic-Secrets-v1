# Semantic Secrets v2 formal and evaluation specification

Status: P8 freeze, version `semantic-graph-v2.0.0` / `semantic-policy-v2.0.0`. Changes affecting outcomes require a new version, decision record, and preregistration before viewing held-out results.

## 1. Frozen research questions

- **RQ1 — Reconstruction:** Can independently generated images representing the same controlled visual concept produce stable canonical semantic credentials?
- **RQ2 — Policy-aware matching:** Can a system-derived `S=(M,T)` policy preserve legitimate technical reconstruction variation while rejecting security-critical semantic differences?
- **RQ3 — Acceptance-region security:** How vulnerable is the induced accepted region under K0-K3 attackers and finite budgets?
- **RQ4 — Template/privacy leakage:** What semantics can be inferred from stored records, policies, and authentication transcripts under named compromise views?
- **RQ5 — Private verification:** Can the frozen policy be evaluated while hiding the semantic credential and resisting practical database-only validation and cross-domain linkage under stated assumptions?
- **RQ6 — Practicality:** What computation, bandwidth, latency, storage, trust, and deployment assumptions are required?

These are technical questions. They do not authorise participant, memorability, recall, usability, preference, or natural-choice claims.

## 2. Typed semantic graph

An extracted graph is `S=(V,E_s,A,C_s,X)`:

- `V`: at most eight entity nodes, each with one category;
- `E_s`: typed unary action or binary action/spatial-relation atoms;
- `A`: typed node attributes;
- `C_s`: category-count atoms;
- `X`: at most one scene/context atom.

Extractors also return normalised node bounding boxes as local provenance. Boxes are not credential atoms and are not protected-record entropy; they support relation derivation, capability scoring, and the VSA quadrant baseline. A box is `[x_min,y_min,x_max,y_max]` in `[0,1]`, with positive area.

The closed P9-P11 vocabulary is:

- entity categories: `person`, `cat`, `dog`, `bird`, `horse`, `bicycle`, `motorcycle`, `car`, `bus`, `train`, `boat`, `airplane`, `chair`, `bench`, `table`, `sofa`, `bottle`, `cup`, `book`, `laptop`, `backpack`, `umbrella`, `tree`, `flower`;
- colours: `red`, `orange`, `yellow`, `green`, `blue`, `purple`, `black`, `white`, `brown`, `gray`;
- sizes: `small`, `medium`, `large`, used only when visually explicit relative to same-category instances or fixed scene scale;
- unary actions/states: `standing`, `sitting`, `running`, `flying`, `sleeping`;
- binary actions: `holding`, `riding`, `eating`;
- spatial relations: `left_of`, `right_of`, `above`, `below`, `in_front_of`, `behind`, `next_to`, `on`, `under`, `inside`;
- scenes: `indoor`, `outdoor`, `road`, `park`, `beach`, `kitchen`, `office`, `bedroom`;
- count buckets: `1`, `2`, `3`, `4`, `5_plus`.

Only these atom forms are valid:

```text
entity(node, category)
attribute(node, colour|size, value)
unary(node, action)
binary(source, action|relation, target)
count(category, bucket)
scene(value)
```

Unknown labels are represented as extraction failure, not silently mapped. Self-edges, contradictory single-valued attributes, duplicate node IDs, invalid arity, unsupported labels, more than eight nodes, and count/entity contradictions are malformed and fail closed.

## 3. Canonicalisation and graph correspondence

Labels are lowercase ASCII vocabulary tokens; Unicode is NFKC-normalised before validation. Inverse spatial relations are normalised to the lexicographically preferred direction (`right_of`→reversed `left_of`, `below`→reversed `above`, `behind`→reversed `in_front_of`). Exact duplicate atoms collapse once; conflicting atoms are malformed.

Canonical node IDs are assigned by taking the lexicographically least complete serialisation over every permutation within equal-category node groups. The eight-node cap makes exact canonicalisation finite and avoids relying on extractor instance order. The serialisation includes schema/model/policy versions.

Comparison enumerates injective category-preserving node correspondences and selects the correspondence that lexicographically maximises: (1) number of enrolled mandatory atoms matched, (2) tolerant weighted F1, and (3) the negative canonical correspondence string. This defines deterministic tie-breaking and permits corresponding instances to receive different extractor-local IDs.

An atom matches only when its type and canonical value match under the chosen node correspondence. There is no embedding or synonym tolerance inside the reference predicate; synonyms must map to the closed vocabulary before graph construction.

## 4. System-derived policy `Π(S)=(M,T)`

Policy statistics are fitted on development families only. For atom type `t`, `r_t` is its independently measured P9A capability-validation recall estimate. An atom's frequency signature removes canonical instance IDs but retains its typed content (for example `attribute(cat,colour,red)` or `binary(person,holding,cup)`); `f(a)=(n_signature(a)+1)/(N+2)` is the smoothed development-family frequency of that signature. An atom is policy-eligible only when its type has point recall at least `0.60` and a family-bootstrap 95% lower bound at least `0.45`.

Each eligible enrolled atom receives:

```text
information(a) = clip(-log2(f(a)), 1, 8)
priority(a)    = information(a) * r_type(a)
```

`M` is selected by enumerating feasible eligible-atom subsets, first maximising cardinality up to three, then total priority, then choosing the lexicographically least sorted atom list, subject to:

1. at least one entity/category or count anchor;
2. at least one action/relation when an eligible one exists;
3. no inverse duplicate relation; after ranking, an `entity(v,c)` is skipped as redundant when another selected attribute, unary, or binary atom already references `v` (counts are not treated as implied);
4. at least two total mandatory atoms, otherwise enrolment is ineligible.

`T` contains every remaining eligible atom. Its weight is `priority(a)`. Users do not select or edit `M`, `T`, weights, or thresholds in the primary study. Candidate `(M',T')` must equal a fresh deterministic application of the same policy version, but an enrolled mandatory atom may match any eligible atom in the candidate graph; it need not have been ranked into candidate `M'`.

## 5. Plaintext reference functionality

After removing candidate atoms paired to mandatory matches, tolerant precision and recall under the selected node correspondence are:

```text
R_T = matched enrolled T weight / enrolled T weight
P_T = matched candidate eligible weight / candidate eligible weight
F_T = 2 * P_T * R_T / (P_T + R_T)
```

An empty denominator is defined as `1` only when both corresponding sets are empty, otherwise `0`. Boundary equality passes. The reference decision is:

```text
Accept_ref = ValidAndVersionEqual
             AND every enrolled atom in M is matched
             AND F_T >= tau_T
```

`tau_T` is selected once in P10 from `{0.50,0.55,...,0.90}` on development families. The selector minimises `max(FRR, targeted-near FAR)`, then random FAR, then FRR, then chooses the largest threshold. It is applied unchanged to validation and sealed test. Missing mandatory atoms, malformed graphs, schema/model/policy mismatch, unsupported operations, NaN, overflow, or migration ambiguity reject. No score, match count, anchor identity, or failure reason is part of the desired external output.

## 6. Required baselines

- `B0-dense`: cosine similarity from one frozen image embedding family, with its threshold chosen by the same development-only minimax rule.
- `B1-global`: weighted graph F1 over all eligible atoms without a mandatory partition.
- `B2-vsa-policy`: the closest feasible VSA semantic-policy component: two or three highest-priority object/attribute/count/quadrant facts, conjunction, and supported quantity equality/range behavior. Quadrants are deterministically derived from local node-box centroids with boundaries at `0.5` (equality maps right/bottom). Unsupported or paper-underspecified behavior is documented, not invented.
- `B3-vsa-full`: VSA's semantic-plus-password SHA-256 architecture as a security comparator only. It is not compared as if its password were absent and is not the policy-value baseline.
- `P1-mt`: the proposed frozen policy and reference predicate above.

Direct-text structured and dense processing are ablations. Pixels, random seeds, prompt strings, and model stochasticity are never counted as credential entropy.

## 7. P9 capability and reconstruction scoring

Capability object true positives require the correct category and box IoU at least `0.50` under maximum bipartite matching. Attributes, unary actions, and binary actions/relations are correct only when their referenced nodes are correctly matched and the closed-vocabulary value/type is exact. Counts require exact bucket equality; scenes require exact label equality. Report per-type micro precision/recall/F1 and macro-over-label F1. The gate's `macro atom F1` is the unweighted mean of object, attribute, count, action, relation, and scene F1; missing required task output scores zero. Schema validity, failure, calibration/confidence where available, latency, peak GPU/RAM, and exact canonical repeat equality are separate metrics.

P9B uses a policy-free `graph_compatibility`: unweighted atom F1 over every valid entity, attribute, count, action, relation, and scene atom under the deterministic best graph correspondence in section 3. Candidate extras reduce precision. This metric is frozen solely to decide whether reconstruction signal exists before `M/T`; P10 may not replace it. AUC treats same-concept pairs as positive and targeted-near or unrelated pairs as the named negative class. The same-minus-near gap is the family median same score minus its median targeted-near score.

## 8. Controlled v2 data design

The representation study contains 72 new concept families grouped into 24 three-member hard-negative clusters. Allocation is cluster-disjoint: 36 development families, 18 validation families, and 18 sealed-test families. The split seed is `82025`; allocation is stratified by primary semantic task and then fixed before any model output. P9 may use only development and validation; the sealed test remains inaccessible until the later end-to-end phase authorises it. No v1 family, prompt, threshold, or sealed P6 test record may be copied or inspected.

Each family is specified before generation with two to five entities, at least one count/attribute fact, and at least one action or spatial relation. The two siblings of each cluster are separately designated single-edit alternatives affecting structural/action and attribute/count facts; unrelated negatives are assigned cyclically across different clusters. Content is balanced so every frozen task type has at least 12 positive and 12 negative capability instances in validation.

Each concept has six independently generated images:

1. enrolment wording and seed;
2. lexical paraphrase and new seed;
3. compositional paraphrase and new seed;
4. fact-preserving layout wording and new seed;
5. fact-preserving style wording (`photographic` or `watercolor`) and new seed;
6. enrolment wording with a new seed.

All wordings, semantic labels, equivalence decisions, near edits, seeds, and pairings are frozen before generating any image. A failed generation is retained as failure; it is never replaced because its semantics are inconvenient. A 12-development-family smoke subset precedes the full P9 pilot and cannot change the gate or shortlist.

P9A uses a separate 96-image capability set: 64 development and 32 validation fixtures, half researcher-authored procedural/composite scenes and half researcher-authored or licence-compatible synthetic/curated scenes with visibly audited ground truth. It is independent of authentication outcomes. Each security-critical atom type has at least 12 validation positives and 12 applicable negatives.

## 9. Licence, ethics, and retention

- Use only researcher-authored material, CC0, CC BY, or model outputs whose licence and acceptable-use terms permit the research and required artifact release. Record source URL, creator, licence/version, acquisition date, and file hash.
- Do not use public authentication credentials, leaked passwords, private prompts, participant data, identifiable private persons, minors, sensitive traits, or biometric identity labels. A generic `person` category is allowed only in non-identifying synthetic/stock-style scenes.
- No human-subject inference is permitted. Researcher-authored paraphrases estimate technical invariance only.
- Prompts and images remain local. Raw images, models, and large caches stay out of Git. Publish only when licences and content review permit it; otherwise publish generation specifications, hashes, and aggregate evidence.
- Delete transient client-style prompts/images only after immutable experimental provenance is recorded; research caches are access-controlled and retention is declared in the data statement.

## 10. Versioning and cache rules

Every model, remote-code file, tokenizer, generation setting, schema, policy, prompt/specification, seed, dependency lock, hardware description, and output receives an immutable ID and SHA-256 hash. Cache keys cover all of those inputs. Content-addressed outputs are reused only on an exact key match; stale or partial entries fail closed. No successful artifact is overwritten. Re-inference/drift uses a new manifest and remains separately labelled.

Before any output, repository commit, config hash, split-manifest hash, and model revisions are recorded. The sealed-test manifest contains only IDs and commitment hashes in the development workspace; its content/labels are stored outside the accessible P9/P10 path. Exclusions and failures remain in append-only manifests.

## 11. Uncertainty and gate rules

All rates report numerator/denominator and two-sided 95% Wilson intervals. Paired differences, AUCs, medians, and success curves use 5,000 family-cluster bootstrap resamples with seed `8202501`. Family/cluster, not image pair, is the independence unit. Multiple strata are descriptive; the gates below are the preregistered primary tests.

### Gate V2-A after P9

At least one extractor/generator representation must satisfy all of:

- P9A schema-valid rate at least `0.98`, failure rate at most `0.05`, overall macro atom F1 at least `0.70` with bootstrap lower bound at least `0.65`, and each of object/count/action/relation F1 at least `0.60` with lower bound at least `0.45`;
- deterministic repeated-inference canonical equality at least `0.95`;
- P9B valid non-empty graph rate family-cluster bootstrap lower bound at least `0.90` (Wilson interval also reported descriptively);
- validation same-versus-targeted-near AUC bootstrap lower bound at least `0.65`, and median same-minus-near compatibility gap lower bound at least `0.05`;
- validation same-versus-unrelated AUC lower bound at least `0.80`, with no preregistered primary task stratum having point same-versus-near AUC below `0.55`.

Failure stops P10; there is no replacement-model search.

### Gate V2-B after P10

On validation, `P1-mt` must have point FRR at most `0.25`, targeted-near FAR at most `0.25`, random FAR at most `0.05`, and eligible-enrolment rate at least `0.80`. Its minimax error must improve on the best of `B0`, `B1`, and `B2` by at least `0.10` absolute, with the 95% paired-bootstrap lower bound above zero. Otherwise P11 is blocked.

### Gate V2-C after P11

The attack budgets are online `{1,5,10,20}` accepted queries and plaintext/offline `{1,10,100,1000,10000}` candidate evaluations. The finite family count cannot support a one-percent confidence upper bound, so point limits and uncertainty limits are both explicit. A standalone-factor hypothesis survives only if K0/K1 success@10 has point estimate at most `0.01` and 95% upper bound at most `0.07`; K2 success@10 has point at most `0.10` and upper bound at most `0.25`; K3 success@10 has point at most `0.25` and upper bound at most `0.45`; and K1 success@10000 has point at most `0.25` and upper bound at most `0.45`. A restricted/second-factor hypothesis may survive if K0/K1 success@10 has point at most `0.10` and upper bound at most `0.25`, while K2 success@10 has point at most `0.25` and upper bound at most `0.45`; K3 is then a reported limitation and no standalone claim is permitted. If neither case holds, the constructive cryptographic path stops unless a separately recorded measurement-only privacy question justifies it.

These thresholds are research stop rules for controlled data, not real-population security guarantees.
