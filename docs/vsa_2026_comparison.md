# Complete comparison with Jeong 2026 VSA

Status: complete-paper review performed from the 16-page local paper on 2026-08-25. This document separates what VSA establishes from what Semantic Secrets v2 proposes to test.

## VSA system, as reported

During enrolment, VSA takes a reference image, extracts semantic information with Grounding DINO and CLIP, and lets the user select two or three facts plus quantity operators. During authentication, the user supplies an arbitrary image satisfying the policy and a password. The system extracts semantics again and evaluates the selected rules.

The representation includes:

- 22 predefined object categories;
- CLIP-derived visual attributes from predefined candidates;
- object quantities;
- 2×2 quadrant spatial location with independent quadrant crops;
- visibility/full-partial status;
- canonical fields for category, core concept, position, visibility, feature, and count.

Flexible Range Logic supports equality, lower/upper bounds, and strict greater/less-than operators. Rules are combined with AND. VSA serializes canonical semantic tokens, hashes category/concept/location/visibility/attribute together with the password using SHA-256, and stores quantity operators and targets separately because they are needed for range evaluation.

## VSA security boundary

VSA describes this binding as **server-opaque**, explicitly weaker than strict zero knowledge. It argues that the server does not store original semantic names, while acknowledging that:

- the semantic-token input space is small (including 22 object categories);
- general-purpose SHA-256 permits very high-rate offline trials;
- practical deployment should use Argon2id and a user-specific random salt;
- the server still stores logical structure such as operators and quantities.

Accordingly, VSA is not evidence that hashing semantics prevents a database attacker from testing likely candidates. It also does not formulate private computation of the rule predicate, policy privacy, record/transcript unlinkability, inversion games, or partial/total-compromise guarantees.

## VSA evaluation boundary

The paper evaluates 16 policies across five declared difficulty levels in global and quadrant modes. Its negative set is 1,009 images (1,000 sampled from COCO 2017 validation plus nine manually collected images). Reported global FAR ranges from 51.73% for `Person >= 1` to 0% for selected stricter policies; it presents Clopper–Pearson intervals and policy/image-availability comparisons.

The paper's positive FRR evaluation does **not** independently regenerate or re-infer positive trials. It automatically selects images that already satisfy each policy from cached COCO detections, then rechecks them from the cache. It reports 0% observed FRR on those selected positives, with very wide upper confidence bounds for scarce policies. The authors explicitly list the missing non-deterministic re-inference evaluation as a limitation.

The paper also reports no empirical user study. It treats image availability as an indirect usability indicator and proposes a future study of at least 30 participants. Human memorability/usability results therefore cannot be attributed to VSA. Semantic Relationship Logic is explicitly future work rather than part of the evaluated system.

## Required two-baseline comparison

| Dimension | VSA semantic-policy component | Full VSA semantic + password architecture | Semantic Secrets v2 hypothesis |
|---|---|---|---|
| User input | Arbitrary satisfying image | Satisfying image plus password | Free reconstruction prompt to local independent generation; prompt is interface |
| Enrolment origin | Reference image | Reference image plus password | Controlled concept reconstructed through independent generated images |
| Semantics | Objects, attributes, counts, quadrant, visibility | Same | Typed graph nodes, edges, attributes, counts |
| Policy source | User selects 2–3 facts/operators | Same | Frozen system-derived mandatory/tolerant policy; user does not choose primary anchors |
| Tolerance | Flexible Range Logic and AND | Same | Mandatory anchors plus bounded secondary tolerance; exact predicate must be frozen |
| Canonical tokens | Yes | Yes | Yes; not claimed as novelty |
| Relationship edges | Future work | Future work | Candidate typed relation edges, subject to extraction evidence |
| Positive trial | Policy-satisfying cached COCO image | Same plus password | Independent generation and fresh extraction under controlled reconstruction variants |
| Stored/protocol state | Policy semantics for functional comparison | SHA-256 bindings; operator/quantity metadata separate | Construction-specific protected record; plaintext prompt/image/graph/embedding local |
| Claimed privacy boundary | Not a private-computation target | Server-opaque, explicitly not strict ZK | Formal construction-specific template, policy, transcript, compromise, and unlinkability goals |
| Offline guessing | Not solved | Small input space acknowledged; Argon2id + salt recommended | Must measure database-view validation/ranking and budgeted success; no privacy-by-hash claim |
| Unlinkability/domain separation | Not targeted | Not established | Explicit target and attack game |
| Acceptance-region attacks | FAR on COCO policy distribution | Same | K0–K3 random/frequency/near/partial/LLM/VLM/adaptive success within budget |
| Human evidence | None | None | None planned; technical stability only |
| Authentication workflow | Extract candidate image semantics and evaluate selected rules | Same, with password included in bindings | Independently generate locally, freshly extract, derive policy, privately evaluate |
| Role of images | Carrier of semantics; may differ each session | Same | Local reconstruction medium; never the record or entropy source |
| Generated vs. externally selected | No generator; reference/arbitrary images | Same | Explicitly AI-generated independent images from free reconstructions |
| Role of prompts | None | None | Local generator interface, explicitly not the secret |
| Auxiliary textual password | Outside semantic component | Required in reported binding/entropy architecture | Not assumed in the primary semantic hypothesis; any factor composition analysed separately |
| Object vocabulary | Fixed 22 categories | Same | Frozen v2 vocabulary/tasks to be justified in P8; not yet selected |
| Attributes | Predefined CLIP candidate labels | Same | Typed attributes, only if extractor capability passes |
| Quantities/counts | Count per canonical fact with range operator | Same | Typed count/cardinality facts with frozen mandatory/tolerant semantics |
| Actions | Not an evaluated semantic field | Same | Candidate required task subject to P9 capability evidence |
| Spatial representation | Global and independent 2×2 quadrant modes | Same | Typed relations/scene geometry to be specified; VSA quadrant is mandatory baseline |
| Policy definition | Manual user choice from extracted facts | Same | Deterministic system derivation; notation/policy alone not novel |
| Server-visible metadata | Functional policy structure required | Operator and quantity targets remain separate; hashes stored | Must enumerate and minimise graph/policy/operator/threshold/size leakage |
| Database compromise | Not a protected-record construction | Paper argues hashes hide names but acknowledges offline trials; exact compromise game absent | Candidate-testing throughput and residual disclosure required for each stolen view |
| Server/key compromise | Not formalised | Server compromise discussed qualitatively; no separate key/service/collusion matrix | Database, AS, PS/share, sub-threshold, collusion, and total compromise separated |
| Policy hiding | No | Not established; operator/quantity structure visible | Explicit target where feasible; leakage must be measured |
| Adaptive-query leakage | Not evaluated | Not evaluated | Explicit attack dimension; C5 only if distinct |
| Attacker model | COCO/nonmatching-image frequency plus qualitative attacks | Same plus qualitative hash/server claims | K0–K3, online/offline, passive/malicious, compromise and adaptive views |
| Random vs. targeted negatives | Mainly COCO distribution; policies include common/rare facts; no target-conditioned semantic-neighbour suite | Same | Random, frequency, targeted near, and full budgeted strategies separated |
| AI-assisted attacks | VLM adversarial manipulation mentioned as future robustness work | Same | LLM/VLM/generator-assisted candidate ordering under fixed budgets |
| Partial-information attacks | Not evaluated | Not evaluated | K2/K3 with frozen known-fact rules |
| Model drift | Not evaluated | Not evaluated | Generator and extractor version/model drift planned after base viability |
| Independent regeneration/re-inference | Arbitrary images are conceptually allowed, but positive FRR is cache-selected/rechecked | Same | Required independent generation and fresh extraction for positive trials |
| Computational cost | Global 1.32 s mean; quadrant 4.78 s; about 800 MB model and 4 GB inference memory on reported setup | Same plus negligible hash comparison relative to VLM | Must report generator, extractor, protocol, bandwidth, storage and trust costs; no value exists yet |
| Claimed contribution | Image-independent semantic authentication, multidimensional extraction, quadrant analysis, Flexible Range Logic, security gradient | Same with hash-based server-opaque binding and combined password-space analysis | Conditional combined C1–C4 hypothesis; no present result or “first” claim |
| Main limitations/future work | Cached positive FRR, no users, compute; relationships, spatial variants, lightweight models future | Small semantic space/offline hashing risk plus same empirical limitations | Novelty, reconstruction, policy value, guessing region, privacy construction, leakage, cost and human validity all unresolved |

## What VSA removes from the novelty space

Semantic Secrets must not claim novelty for semantic authentication, image independence, VLM use, canonical tokens, object/attribute/count/quadrant facts, quantity operators, conjunction, policy-based acceptance, or hash binding. A notation such as `S=(M,T)` is also insufficient novelty by itself because VSA already distinguishes selected required rules from the rest of an image's semantics.

## Candidate remaining gap

The defensible hypothesis is not one semantic mechanism. It is whether the following combination can be made technically viable and private:

1. independent generative reconstruction of a concept;
2. canonical typed visual-semantic graphs including evaluated relations;
3. deterministic, system-derived mandatory/tolerant policy selection;
4. full acceptance-region and budgeted AI-assisted attack measurement;
5. private predicate evaluation with policy privacy, offline-validation resistance under declared views, and domain-separated unlinkability.

P8 must verify this gap against broader primary literature. Until Gate V2-N passes, this is a research hypothesis rather than a novelty claim.

## Bibliographic identity

Pil-seong Jeong, “Design and Security Validation of Image-Agnostic Visual Semantic Authentication (VSA) Framework Based on Vision-Language Model,” *Journal of The Korea Institute of Information Security and Cryptology*, 36(3):935–948, 2026. DOI: 10.13089/JKIISC.2026.36.3.935.
