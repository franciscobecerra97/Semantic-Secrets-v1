# AGENT.md — Semantic Secrets research contract (v3.2 ground-truth correction)

## 1. Authority and status

This file is the authoritative scientific and engineering contract for **Semantic Secrets**, a prospective PoPETs/PETS 2027 project about **reconstructable semantic authentication, acceptance-region security, and private verification**. P9-v3A replaces only the failed extraction architecture and its gates; the narrowed v2 C1–C4 contribution boundary and security model remain active. Read this file before changing the research design, prototype, experiments, manuscript, or artifact.

The project changed direction after the completed `visual-semantic-pipeline-v1` P0–P7 programme and a complete review of Jeong's 2026 Visual Semantic Authentication (VSA) paper. P0–P7 remain immutable historical evidence. Their negative and formative findings are not v2 results, must not be retuned into v2, and must not be erased.

The primary motivation is the security transition from exact secret reproduction to approximate semantic reconstruction. Traditional authentication usually requires an exact value or exact cryptographic possession. This project instead asks whether independent reconstructions of one intended concept can yield compatible canonical semantics, what complete fuzzy acceptance region that creates, and whether the predicate can be evaluated without exposing a reusable semantic template, practical offline guess-testing oracle, or cross-domain linkage. It does not assume that the primitive will replace passwords or passkeys; standalone, second-factor, policy-constrained, restricted-use, negative/measurement, and stop outcomes remain possible.

No human-subject study is authorised. The project may measure technical reconstruction stability under researcher-controlled inputs, not human recall, memorability, usability, preference, accessibility, natural secret choice, or real-world authentication time. It cannot establish that visual concepts are easier to remember than passwords or that this primitive is superior to passwords, passkeys, biometrics, or hardware authenticators.

## 2. Working title and central question

**Working title:**

> Semantic Secrets: Private Authentication from Reconstructable Visual Semantics

**Central research question:**

> Can independently reconstructed visual concepts yield stable and discriminative canonical semantic credentials whose complete acceptance region remains sufficiently resistant to realistic and AI-assisted guessing, and whose authentication predicate can be privately verified without exposing a reusable semantic template, practical offline guess-testing oracle, or cross-domain linkage?

The intended semantic concept is reconstructed rather than reproduced exactly. The natural-language prompt is a reconstruction interface, not the credential. A generated image is a transient reconstruction medium, not the credential, and generated pixels provide no credential entropy. Probabilistic observations are evidence; the deterministic canonical graph is the security-sensitive semantic representation; operationally, the secret surface is the complete acceptance region.

## 3. Active v3 extraction path and notation

```text
intended reconstructable semantic concept C
        ↓ natural-language reconstruction interface
prompt P (interface, not secret)
        ↓ local generation with randomness r
independently generated image I = G(P, r) (transient, not secret)
        ↓ modular local observation
typed evidence O = Observe(I)
        ↓ deterministic semantic compiler C_s
typed visual-semantic graph or typed failure S = C_s(O)
        ↓ frozen system policy Π
(M, T) = Π(S)
        ↓ construction-specific protection
protected record R
```

At authentication, the client independently obtains `I'`, extracts `S'`, derives `(M',T')`, and privately evaluates the frozen acceptance predicate against `R`.

Notation:

- `C`: intended semantic concept represented by a controlled technical specification; this is researcher-controlled ground truth, not evidence of human memory;
- `P`: natural-language reconstruction interface supplied to the local generator;
- `G`: versioned local image generator;
- `r`: generation randomness;
- `I = G(P,r)`: transient generated image;
- `Observe`: one of at most two versioned modular perception pipelines; it emits bounded evidence and provenance, never credential JSON;
- `O = Observe(I)`: detections, attributes, actions/interactions, scene hypotheses, component-local confidence, provenance, abstentions, and typed component failures;
- `C_s`: deterministic semantic compiler that emits a schema-valid canonical graph or a schema-valid typed failure, never malformed JSON;
- `S = C_s(O)`: typed semantic graph on compiler success;
- `S = (V,E_S,A,C_S)`: nodes, typed edges, attributes, and count/cardinality facts;
- `Π`: frozen, system-derived credential policy;
- `Π(S) = (M,T)`: mandatory security anchors and tolerant secondary semantics;
- `R = Protect(S,M,T,context)`: construction-specific protected enrolment record;
- `B`: attacker attempt or computation budget;
- `K0`–`K3`: attacker-knowledge levels.

`L_visual` is the broad candidate observation language. `L_cred` is the subset of atom types independently qualifying in P9-v3B in both controlled and naturalistic strata. Reconstruction or authentication outcomes may not promote a type. Actions and interactions receive their own gates: neither is automatically discarded nor required for extraction viability.

## 4. Intended contributions

These are hypotheses to be validated, not present claims.

### C1 — Technical reconstructability of visual-semantic credentials

Establish whether independent generated images produced from controlled reconstructions of the same concept yield sufficiently stable canonical semantics while remaining distinguishable from targeted alternatives. This is a technical reconstruction question only. It does not establish that people can remember or reproduce concepts.

### C2 — System-derived policy-aware typed semantic graphs

Represent a visual secret as `S=(V,E_S,A,C_S)` and derive `Π(S)=(M,T)`:

- `M`: mandatory, discriminative security anchors whose absence rejects;
- `T`: secondary semantics with explicitly bounded tolerance.

The primary policy must be system-derived, deterministic, versioned, and frozen before held-out evaluation. Users do not manually nominate the primary anchors. Policy design alone is not novel: VSA already provides user-selected semantic facts, quantity operators, conjunction, canonical tokens, and spatial rules. The candidate novelty is the evaluated combination of generative reconstruction, typed canonical graphs, system-derived `M/T`, acceptance-region analysis, and private verification.

### C3 — Acceptance-region and budgeted guessing analysis

Exact authentication can be idealised as a singleton acceptance set, `A(s)={s}`. Semantic authentication instead induces a fuzzy region. The secret surface is the full acceptance region, not one prompt, image, or graph. For enrolment state `S`, define

```text
A(S) = { S' : Accept(S,S',Π) = 1 }.
```

An attacker succeeds with any `S' ∈ A(S)` and need not recover the enrolment prompt, image, or exact graph. This creates the central security trade-off: a predicate that is too strict rejects legitimate independent reconstructions, while one that is too tolerant gives attackers more accepted alternatives. Evaluate success within budget for random, frequency-informed, near, partial-information, LLM-assisted, VLM/generator-assisted, and adaptive attackers. Report `success@1`, `success@5`, `success@10`, `success@B`, guesses-to-success, uncertainty, duplicate handling, and online/offline access separately.

Knowledge levels are:

- `K0`: public system information and generic/random candidates;
- `K1`: population or frequency knowledge, without target-specific facts;
- `K2`: partial target-specific semantic information;
- `K3`: strong near-secret knowledge sufficient to form close candidates.

P6 remains valid evidence that the v1 matcher accepted many already-near candidates under a conditional K3-like stress. It did not measure end-to-end success within a guessing budget and does not decide v2.

### C4 — Private and unlinkable verification

Keep `P`, `I`, plaintext `S`, and raw embeddings local. For each candidate construction, define and evaluate:

- template confidentiality and inversion resistance;
- database-only offline validation resistance;
- policy privacy, including whether `M/T`, graph size, operators, weights, or thresholds leak;
- cross-service and cross-account unlinkability through domain separation;
- transcript privacy and adaptive verification-oracle leakage;
- exact compromise views and residual guarantees.

Cryptography can hide a comparison without making a small or easily reached semantic region strong. Conversely, good semantic discrimination does not provide template, policy, transcript, or linkage privacy. Semantic correctness and cryptographic privacy are separate gates.

C1 and C2 are enabling contributions. If the constructive path survives, C3 and C4 are the strongest eventual security/privacy contributions and should lead the paper positioning. Their scientific meanings may not be redesigned by narrative edits.

### C5 — Adaptive verification-oracle leakage (folded into C3/C4)

P8 found established adaptive verifier/hill-climbing and active-security prior art and no separately defensible mechanism claim. C5 is therefore folded into C3/C4. Adaptive one-bit query attacks remain mandatory evidence, but are not a standalone contribution. Reopening C5 requires a new distinct estimand and novelty review.

## 5. Relationship to 2026 VSA

VSA is the closest mandatory baseline. It enrols a reference image, lets the user choose two or three semantic facts with quantity operators, and accepts an arbitrary image satisfying those rules together with a password. It extracts objects, CLIP-derived attributes, quantities, and 2×2 quadrant location; canonicalises tokens; evaluates Flexible Range Logic; and binds most semantic fields plus the password with SHA-256 while storing quantity/operator metadata separately.

Therefore the following are prior art, not project novelty: visual-semantic authentication, image independence, VLM-based extraction, canonical semantic tokens, objects/attributes/counts/quadrants, flexible quantity operators, conjunctions, semantic-policy matching, user-chosen two/three-fact policies, and hash-based semantic binding.

VSA calls its construction server-opaque and explicitly distinguishes it from strict zero knowledge. It acknowledges that its small semantic space permits fast offline guessing with general-purpose SHA-256 and recommends Argon2id plus a user-specific salt. Its COCO evaluation reports FAR/FRR, but positive FRR samples are automatically selected from cached detections rather than independently re-inferred; it reports no human study and leaves semantic relationships to future work. It does not target private/unlinkable verification.

Generative graphical authentication is also prior art: PassStyles and Omokage use StyleGAN-generated changing face candidates and visual recognition criteria. They differ from free-language reconstruction into independent text-to-image scenes, but block broad generative/changing-image authentication claims.

The maintained comparison is `docs/vsa_2026_comparison.md`; the broader P8 closure is `docs/p8_novelty_review_v2.md`.

## 6. Required novelty discipline

Never claim or imply any of the following without a new, verified, scoped prior-art review that supports the exact wording:

- first semantic authentication;
- first image-independent or image-agnostic visual authentication;
- first policy-based visual or graphical authentication;
- first VLM-based authentication;
- first use of canonical semantic tokens;
- first flexible semantic or quantity matching;
- novelty from object, count, attribute, quadrant, spatial, or conjunction rules;
- novelty from the notation `S=(M,T)` or mandatory/tolerant policy alone;
- novelty of PSI, OPRF, PAKE, fuzzy extraction, secure computation, FHE, or other standard primitives;
- entropy or unpredictability from AI-generated pixels;
- human memorability, reproducibility, preference, or usability;
- accessibility, natural secret-selection entropy, or real-world authentication time;
- superiority to passwords, passkeys, biometrics, or hardware authenticators;
- proof that generated images or visual concepts are easier to remember than passwords;
- privacy, zero knowledge, offline resistance, unlinkability, or irreversibility merely because values are hashed, salted, encoded, or encrypted.

Every novelty statement must identify the combined system property, closest prior work, exact difference, evidence, and limitation. If P8 finds prior work that subsumes C1–C4 in combination, narrow the contribution before implementation.

## 7. Two VSA baselines

Do not collapse VSA into one comparator:

1. **VSA semantic-policy component:** its canonical extraction, user-selected rules, quantities/operators, conjunction, and global/quadrant matching. This is the mandatory functional policy baseline.
2. **Full VSA semantic-plus-password architecture:** semantic policy combined with a password and SHA-256 binding, including its stated server-opaque boundary and offline-guessing limitation. This is an architectural security comparator, not a private-verification gold standard.

## 8. Security and privacy boundary

`docs/security_model_v2.md` and `docs/threat_claim_matrix_v2.csv` are authoritative for v2. At minimum, analyse:

- online guesser and adaptive authenticating client;
- database snapshot attacker;
- honest-but-curious and malicious authentication infrastructure;
- key/service compromise and declared collusion thresholds;
- AI-assisted and partial-information attackers;
- inversion/reconstruction and candidate validation;
- record and transcript linking across accounts/services;
- replay, malformed inputs, version mismatch, downgrade, and selective failure.

No design may claim protection after total compromise unless its exact construction and proof justify that scope. If stolen state enables candidate validation, report the throughput and budgeted success. Rate limiting is an online assumption, not an offline defence.

Normal verification should reveal no more than an authorised, context-bound `Accept/Reject` bit plus explicitly enumerated metadata. Scores, intersection cardinality, matched anchors, failure reasons, policy shape, timing, and message length are leakage unless hidden or justified.

## 9. Data and evaluation rules

- P8 is novelty refresh, formalisation, and preregistration only. It may not execute the expensive v2 experiment.
- P8 completed on 2026-08-25. `docs/formal_specification_v2.md` and `experiments/v2/config/preregistration_v2.json` remain the binding historical freeze for the failed P9-v2 path; they may not be edited after its output.
- P9-v2 completed negatively and is immutable. Its monolithic VLM-to-credential-JSON path failed schema validity; it did not measure full semantic capability and is not a universal extractor-impossibility result.
- P9-v3A completed on 2026-08-25 as architecture and preregistration only. Its v3.0.0 files remain the immutable initial freeze. P9-v3A.1 then completed a prospective pre-execution suitability audit before any v3 output. P9-v3A.2 prospectively corrected only the ground-truth method on 2026-08-28: the two-human clause is historical and superseded. The active P9-v3B contract composes v3.0, v3.1, and v3.2; no v3 model, weight, capability image, inference, policy, authentication, or cryptographic experiment has run.
- P9-v3B requires explicit authorisation and new `cap-v3-*` data. It has no human participants or human annotators. Each final image must have a project-authored closed-label reference scene specification; the manifest, scenario specifications, image hashes, and deterministic support opportunities must be audited and frozen before any perception inference, without consulting model predictions. Pre-execution code (compiler, 320-case local matrix, isolated adapters, ground-truth checks, RunPod package, and formal guards) is engineering evidence only: it did not start P9-v3B or pass Gate V3-A1. The formal locked environment must rerun every compiler case. P9-v3C requires constructive Gate V3-A1 and a separate preregistration/data freeze. P10 requires constructive Gate V3-A2.
- New v2 evidence requires new version identifiers, data, splits, configs, and gates. Do not reuse v1 thresholds as v2 evidence.
- Keep a sealed held-out test partition. Fit vocabulary, policy rules, weights, thresholds, attacker orderings, and all selection decisions on permitted development data only.
- Use independent generations for enrolment and authentication trials. A cached sample selected because it already satisfies a policy is not a positive reconstruction trial.
- Report extraction failure, non-empty rate, semantic graph fidelity, same-concept stability, targeted separation, FAR/FRR with uncertainty, and subgroup/failure analyses.
- Distinguish benign same-concept reconstruction, independent negative concepts, targeted near alternatives, and adaptive attacks.
- Preserve raw-to-derived provenance, hashes, model IDs/revisions, prompts/specifications, seeds, environment, and exclusions.
- Never access the twelve sealed v1 P6 test families for v2 planning or development.

## 10. Gates and stop rules

- **V2-N — Novelty/formalisation:** C1–C4 remain jointly distinguishable from verified prior work; definitions, baselines, and preregistration are frozen.
- **V2-A — Failed historical extractor gate:** the frozen P9-v2 monolithic representation path failed and can never be relabelled as a pass.
- **V3-A1 — Modular extraction viability:** compiler invariants pass exactly and at least one frozen observation pipeline yields an independently evidenced, support-complete `L_cred` containing entity plus at least two additional types, including a structural type. Installed GPU capacity is not a gate; measured complete-pipeline consumption remains capped at 24 GiB VRAM and 32 GiB RSS.
- **V3-A2 — Independent reconstruction viability:** using only V3-A1-eligible types on separate data, independent-image reconstruction meets preregistered enrolment, FRR/FAR, separation, and policy-improvement bounds.
- **V2-B — Policy value:** system-derived `M/T` materially improves the security–reconstruction trade-off over VSA-style and non-policy baselines without post-hoc tuning.
- **V2-C — Acceptance-region viability:** budgeted K0–K3 and AI/adaptive success supports the selected positioning.
- **V2-D — Cryptographic feasibility:** at least one construction preserves the frozen plaintext predicate with acceptable leakage, correctness, and cost.
- **V2-E — Privacy/security evidence:** database, transcript, inversion, linking, compromise, and oracle claims survive their preregistered evaluations.
- **V2-F — End-to-end/publication readiness:** integrated evidence, reproducibility, limitations, and claim audit are complete.

An expensive later phase cannot bypass an earlier failed gate. Valid outcomes include standalone authentication, second factor, policy-constrained or restricted/high-value authentication, another bounded deployment setting, negative/measurement contribution, or stop. A failed gate is evidence, not permission to retune.

## 11. Engineering and reproducibility contract

- Follow the budget sequence: primary literature/analysis → deterministic smoke test → small preregistered pilot → eliminate weak candidates → full experiment only after its gate.
- Do not benchmark many generators or VLMs. The executable v3.1 shortlist is exactly the two pipelines frozen in `visual_observation_v3_1.json`; v3.0.0 remains historical. Models emit evidence, not final credential JSON. Never search until a favourable result appears.
- Treat client-side computational feasibility as an empirical RQ6 outcome, not an assumption. P9-v3B has established no actual resource requirement. A powerful research GPU is experimental infrastructure, not automatically part of a deployment architecture; impractical trusted-client requirements are a valid limitation, restricted-use result, failed practicality gate, or negative outcome.
- Do not move prompt, image, observation, graph, or other secret-bearing processing to an untrusted cloud to repair a practicality failure, and do not replace the visual path with direct prompt/text authentication without a new authorised research decision.
- Cache generated images and canonical graphs, reuse valid version-matched outputs, and create new-version manifests instead of overwriting evidence.
- Prefer mature cryptographic libraries and implement only the small set of candidates surviving theoretical elimination; do not build every possible protocol.
- Keep observation, deterministic compilation, policy derivation, plaintext decision, protocol, attack, and analysis modules separable.
- Implement a deterministic plaintext reference predicate before private evaluation.
- Fail closed on malformed graphs, unsupported operators, version mismatch, missing mandatory anchors, and migration ambiguity.
- Pin dependencies and model revisions; record licences and acquisition provenance.
- Keep models, raw datasets, generated images, credentials, secrets, caches, and recomputable large intermediates out of Git.
- Commit compact configs, manifests, tests, aggregate tables, figures, decision records, and evidence required to reproduce claims.
- Never commit credentials, tokens, private keys, personal data, or identifiable user examples.

## 12. Historical v1 boundary

P0–P7 tested `visual-semantic-pipeline-v1`. P6 failed Gate A because all tested matchers poorly separated same-concept from targeted-neighbour pairs; the primary weighted matcher accepted 75% of targeted validation neighbours at its training-selected threshold. P7 then found no material technical benefit from its tested image pathways over paired text pathways and selected removal of that image stage from the v1 authentication core.

Those results motivate, but do not validate or invalidate, the active hypothesis. The image path is an independently tested reconstruction medium. No v1 result may be relabelled as evidence that the v3 modular mechanism works.

## 13. Immediate execution boundary

P9-v3A.1 completed on 2026-08-25 as a pre-execution audit. It corrected machine-capacity wording, selected EGTR, declared support opportunities and primary gate types, and historically introduced a two-human annotation blocker. P9-v3A.2 superseded only that annotation method before any v3 image or model output. P9-v3B now requires explicit instruction plus a hash-bound `ground-truth-freeze-v3.2.0` record before inference; image construction itself has no human-resource gate. The project-authored reference semantics must remain model-output blind. P9-v3C is blocked on constructive V3-A1; P10 and every cryptographic phase are blocked on constructive V3-A2. See `docs/formal_specification_v3_2.md` and decision `P9-v3A.2-00`.
