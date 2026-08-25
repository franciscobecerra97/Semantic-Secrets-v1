# AGENT.md — Semantic Secrets v2 research contract

## 1. Authority and status

This file is the authoritative scientific and engineering contract for **Semantic Secrets v2**, a prospective PoPETs/PETS 2027 project. Read it before changing the research design, prototype, experiments, manuscript, or artifact.

The project changed direction after the completed `visual-semantic-pipeline-v1` P0–P7 programme and a complete review of Jeong's 2026 Visual Semantic Authentication (VSA) paper. P0–P7 remain immutable historical evidence. Their negative and formative findings are not v2 results, must not be retuned into v2, and must not be erased.

No human-subject study is authorised. The project may measure technical reconstruction stability, not human recall, memorability, usability, preference, or natural secret choice.

## 2. Working title and central question

**Working title:**

> Semantic Secrets: Private Authentication from Reconstructable Visual Semantics

**Central research question:**

> Can a user reconstruct a remembered visual concept through independently generated images and authenticate using its canonical semantics while preventing the authentication infrastructure or a database attacker from learning, linking, reconstructing, or efficiently testing guesses about that semantic secret?

The remembered concept is the intended credential. A natural-language prompt is an input interface, not the credential. Generated pixels are transient local observations, not the credential.

## 3. v2 system path and notation

```text
remembered visual concept C
        ↓ free natural-language reconstruction
prompt P (interface, not secret)
        ↓ local generation with randomness r
independently generated image I = G(P, r) (transient, not secret)
        ↓ local canonical extraction E
typed visual-semantic graph S = E(I)
        ↓ frozen system policy Π
(M, T) = Π(S)
        ↓ construction-specific protection
protected record R
```

At authentication, the client independently obtains `I'`, extracts `S'`, derives `(M',T')`, and privately evaluates the frozen acceptance predicate against `R`.

Notation:

- `C`: remembered visual concept represented by a controlled technical specification;
- `P`: free natural-language reconstruction supplied to the local generator;
- `G`: versioned local image generator;
- `r`: generation randomness;
- `I = G(P,r)`: transient generated image;
- `E`: versioned canonical visual-semantic extractor;
- `S = E(I)`: typed semantic graph;
- `S = (V,E_S,A,C_S)`: nodes, typed edges, attributes, and count/cardinality facts;
- `Π`: frozen, system-derived credential policy;
- `Π(S) = (M,T)`: mandatory security anchors and tolerant secondary semantics;
- `R = Protect(S,M,T,context)`: construction-specific protected enrolment record;
- `B`: attacker attempt or computation budget;
- `K0`–`K3`: attacker-knowledge levels.

The overloading of `E` for extraction and `E_S` for graph edges is intentional only in prose; code and formal text must use unambiguous names.

## 4. Intended contributions

These are hypotheses to be validated, not present claims.

### C1 — Generatively reconstructable visual-semantic credentials

Establish whether independent generated images produced from controlled reconstructions of the same concept yield sufficiently stable canonical semantics while remaining distinguishable from targeted alternatives. This is a technical reconstruction question only. It does not establish that people can remember or reproduce concepts.

### C2 — System-derived policy-aware typed semantic graphs

Represent a visual secret as `S=(V,E_S,A,C_S)` and derive `Π(S)=(M,T)`:

- `M`: mandatory, discriminative security anchors whose absence rejects;
- `T`: secondary semantics with explicitly bounded tolerance.

The primary policy must be system-derived, deterministic, versioned, and frozen before held-out evaluation. Users do not manually nominate the primary anchors. Policy design alone is not novel: VSA already provides user-selected semantic facts, quantity operators, conjunction, canonical tokens, and spatial rules. The candidate novelty is the evaluated combination of generative reconstruction, typed canonical graphs, system-derived `M/T`, acceptance-region analysis, and private verification.

### C3 — Acceptance-region and budgeted guessing analysis

The secret is the full acceptance region, not one prompt, image, or graph. For enrolment state `S`, define

```text
A(S) = { S' : Accept(S,S',Π) = 1 }.
```

Evaluate success within budget for random, frequency-informed, near, partial-information, LLM-assisted, VLM/generator-assisted, and adaptive attackers. Report `success@1`, `success@5`, `success@10`, `success@B`, guesses-to-success, uncertainty, duplicate handling, and online/offline access separately.

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

Cryptography can hide a comparison without making a small semantic space strong. Semantic correctness and cryptographic privacy are separate gates.

### C5 — Adaptive verification-oracle leakage (optional)

Retain this as a standalone contribution only if P8 shows that adaptive query leakage is technically distinct from ordinary online guessing and from standard private-matching security. Otherwise it remains an evaluation dimension under C3/C4.

## 5. Relationship to 2026 VSA

VSA is the closest mandatory baseline. It enrols a reference image, lets the user choose two or three semantic facts with quantity operators, and accepts an arbitrary image satisfying those rules together with a password. It extracts objects, CLIP-derived attributes, quantities, and 2×2 quadrant location; canonicalises tokens; evaluates Flexible Range Logic; and binds most semantic fields plus the password with SHA-256 while storing quantity/operator metadata separately.

Therefore the following are prior art, not project novelty: visual-semantic authentication, image independence, VLM-based extraction, canonical semantic tokens, objects/attributes/counts/quadrants, flexible quantity operators, conjunctions, semantic-policy matching, user-chosen two/three-fact policies, and hash-based semantic binding.

VSA calls its construction server-opaque and explicitly distinguishes it from strict zero knowledge. It acknowledges that its small semantic space permits fast offline guessing with general-purpose SHA-256 and recommends Argon2id plus a user-specific salt. Its COCO evaluation reports FAR/FRR, but positive FRR samples are automatically selected from cached detections rather than independently re-inferred; it reports no human study and leaves semantic relationships to future work. It does not target private/unlinkable verification.

The maintained comparison is `docs/vsa_2026_comparison.md`.

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
- New v2 evidence requires new version identifiers, data, splits, configs, and gates. Do not reuse v1 thresholds as v2 evidence.
- Keep a sealed held-out test partition. Fit vocabulary, policy rules, weights, thresholds, attacker orderings, and all selection decisions on permitted development data only.
- Use independent generations for enrolment and authentication trials. A cached sample selected because it already satisfies a policy is not a positive reconstruction trial.
- Report extraction failure, non-empty rate, semantic graph fidelity, same-concept stability, targeted separation, FAR/FRR with uncertainty, and subgroup/failure analyses.
- Distinguish benign same-concept reconstruction, independent negative concepts, targeted near alternatives, and adaptive attacks.
- Preserve raw-to-derived provenance, hashes, model IDs/revisions, prompts/specifications, seeds, environment, and exclusions.
- Never access the twelve sealed v1 P6 test families for v2 planning or development.

## 10. Gates and stop rules

- **V2-N — Novelty/formalisation:** C1–C4 remain jointly distinguishable from verified prior work; definitions, baselines, and preregistration are frozen.
- **V2-A — Reconstruction viability:** independent-image semantic reconstruction meets preregistered technical completeness and targeted-separation bounds.
- **V2-B — Policy value:** system-derived `M/T` materially improves the security–reconstruction trade-off over VSA-style and non-policy baselines without post-hoc tuning.
- **V2-C — Acceptance-region viability:** budgeted K0–K3 and AI/adaptive success supports the selected positioning.
- **V2-D — Cryptographic feasibility:** at least one construction preserves the frozen plaintext predicate with acceptable leakage, correctness, and cost.
- **V2-E — Privacy/security evidence:** database, transcript, inversion, linking, compromise, and oracle claims survive their preregistered evaluations.
- **V2-F — End-to-end/publication readiness:** integrated evidence, reproducibility, limitations, and claim audit are complete.

An expensive later phase cannot bypass an earlier failed gate. Valid outcomes include standalone authentication, second factor, policy-constrained credential, negative/measurement contribution, or stop. A failed gate is evidence, not permission to retune.

## 11. Engineering and reproducibility contract

- Follow the budget sequence: primary literature/analysis → deterministic smoke test → small preregistered pilot → eliminate weak candidates → full experiment only after its gate.
- Do not benchmark many generators or VLMs. Screen extractor capabilities before authentication trials, freeze a small justified shortlist, and never search until a favourable result appears.
- Cache generated images and canonical graphs, reuse valid version-matched outputs, and create new-version manifests instead of overwriting evidence.
- Prefer mature cryptographic libraries and implement only the small set of candidates surviving theoretical elimination; do not build every possible protocol.
- Keep semantic extraction, policy derivation, plaintext decision, protocol, attack, and analysis modules separable.
- Implement a deterministic plaintext reference predicate before private evaluation.
- Fail closed on malformed graphs, unsupported operators, version mismatch, missing mandatory anchors, and migration ambiguity.
- Pin dependencies and model revisions; record licences and acquisition provenance.
- Keep models, raw datasets, generated images, credentials, secrets, caches, and recomputable large intermediates out of Git.
- Commit compact configs, manifests, tests, aggregate tables, figures, decision records, and evidence required to reproduce claims.
- Never commit credentials, tokens, private keys, personal data, or identifiable user examples.

## 12. Historical v1 boundary

P0–P7 tested `visual-semantic-pipeline-v1`. P6 failed Gate A because all tested matchers poorly separated same-concept from targeted-neighbour pairs; the primary weighted matcher accepted 75% of targeted validation neighbours at its training-selected threshold. P7 then found no material technical benefit from its tested image pathways over paired text pathways and selected removal of that image stage from the v1 authentication core.

Those results motivate, but do not validate or invalidate, v2. The v2 image path is part of the new scientific hypothesis: independent image generation is the reconstruction medium from which a typed graph and system-derived policy are obtained. It requires new data and Gates V2-A/V2-B. No v1 result may be relabelled as evidence that this new mechanism works.

## 13. Immediate execution boundary

The next executable phase is **P8 — v2 novelty refresh, formalisation, and preregistration**. Do not start P9 or any expensive experiment until P8 is complete and Gate V2-N has a recorded constructive outcome.
