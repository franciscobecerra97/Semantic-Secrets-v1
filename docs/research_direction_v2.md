# Research direction v2

Status: Gate V2-N passed with narrowing; P9-v2 failed its monolithic extractor gate; P9-v3A completed an architecture/preregistration reframe on 2026-08-25 without running a v3 experiment.

## Exact reproduction versus semantic reconstruction

Most authentication requires exact secret reproduction or proof of exact cryptographic possession. It can be idealised as accepting one enrolled value:

```text
A(s) = {s}
```

Semantic Secrets studies a different authentication primitive: an intended semantic concept may be independently reconstructed into different textual and visual realizations while still producing sufficiently compatible canonical semantics for authentication. For a controlled intended concept `C`:

```text
C -> P1 -> I1 -> O1 -> S1
C -> P2 -> I2 -> O2 -> S2
```

Normally `P1 != P2` and `I1 != I2`; the technical hypothesis is that `S1 ≈ S2` under a frozen authentication predicate while targeted semantic alternatives remain distinguishable. The study uses researcher-controlled concepts, prompts, and variation. It tests reconstruction stability, not whether people remember or reproduce concepts over time.

The central research question is whether independently reconstructed visual concepts can yield stable and discriminative canonical semantic credentials whose complete acceptance region remains sufficiently resistant to realistic and AI-assisted guessing, and whose predicate can be privately verified without exposing a reusable semantic template, practical offline guess-testing oracle, or cross-domain linkage.

## Generative reconstruction as a normalisation boundary

The local image generator is an experimental **semantic reconstruction / normalisation boundary**. Different natural-language descriptions of the same intended concept may produce visibly different images; the project asks whether those independent visual realizations preserve enough underlying semantics to authenticate. Image generation is not justified by a memorability claim.

The roles are deliberately separated:

```text
prompt             = reconstruction interface
generated image    = transient reconstruction medium
observations       = probabilistic visual evidence
canonical graph    = security-sensitive semantic representation
acceptance region  = operational secret surface
```

Thus `prompt != credential`, `generated image != credential`, and `generated pixels != credential entropy`. In the strongest target, all prompt, image, observation, plaintext graph, and raw-embedding processing stays on the trusted client.

## Canonical semantic representation

Let a controlled concept be `C`, a reconstruction prompt be `P`, generator randomness be `r`, a frozen local generator be `G`, a modular observation pipeline be `Observe`, and a deterministic semantic compiler be `C_s`:

```text
I = G(P,r)
O = Observe(I)
S = C_s(O)
S = (V,E_S,A,C_S)
Π(S) = (M,T)
R = Protect(S,M,T,context)
```

The invariant technical path is:

```text
C -> P -> I -> O -> S -> (M,T) -> protected/private verification
```

Models infer bounded evidence with local confidence and provenance; they do not author credential JSON. `C_s` deterministically validates, deduplicates, assigns canonical IDs, derives counts/geometry, normalises edges, and returns a valid graph or typed failure. `M` contains mandatory discriminative anchors; `T` contains explicitly tolerant secondary facts. At authentication, independently generated `I'` yields `S'` and `(M',T')`. A plaintext reference predicate first decides whether the mandatory constraints and tolerant threshold are satisfied. A private protocol must later reproduce that same bit without disclosing more than its stated leakage.

`L_visual` is broad. `L_cred` contains only atom types independently qualifying in both controlled and naturalistic P9-v3B strata. Action and interaction types are evaluated independently; neither is mandatory nor discarded.

## Acceptance-region security and the reconstruction trade-off

Semantic authentication induces

```text
A(S) = {S' : Accept(S,S') = 1}.
```

An attacker need not recover the original prompt, original image, or exact enrolled graph. Success requires any `S' ∈ A(S)`. The complete region is therefore the security object, and random FAR alone is not a security result.

The core tension is fundamental:

```text
too strict    -> legitimate independent reconstructions fail
too tolerant  -> attackers gain more accepted semantic alternatives
```

C3 measures how reachable the region is under explicit budgets and K0–K3 random, frequency-informed, semantic-neighbour, partial-information, LLM-assisted, generator/VLM-assisted, and adaptive one-bit-oracle strategies. The resulting evidence, rather than a desired product story, determines whether any standalone, factor, constrained, restricted-use, negative, or stop positioning survives.

## Privacy of fuzzy semantic verification

Even a stable and discriminative semantic credential may reveal the underlying concept. Plaintext or deterministic stored graphs, policies, and transcripts may enable semantic inversion, database-only candidate validation, policy inference, adaptive probing, or cross-account/service linkage. The project therefore separately asks whether the frozen predicate can be evaluated while limiting template, policy, transcript, compromise, and linkage leakage.

This creates two independent questions:

1. **Semantic correctness:** Does the reconstruction/extraction/policy pipeline accept independent same-concept generations and reject targeted alternatives under frozen rules?
2. **Cryptographic privacy:** Does the selected construction hide inputs, policy, records, and linkage under its declared compromise and interaction model while preserving the reference decision?

Passing one does not imply the other:

```text
semantic correctness != cryptographic privacy
```

Secure/private computation cannot repair an easily guessed acceptance region, and good semantic discrimination does not automatically provide template privacy.

## Candidate contributions

- **C1 — Reconstructability:** determine whether independent generated realizations of the same controlled concept yield compatible canonical semantics while remaining distinguishable from targeted alternatives. This is technical reconstruction stability, not a human-memory result.
- **C2 — System-derived policy-aware semantics:** determine whether a deterministic `Π(S)=(M,T)` can separate mandatory/discriminative anchors from secondary semantics under bounded tolerance without accepting important semantic differences.
- **C3 — Acceptance-region security:** measure complete-region reachability within explicit budgets under K0–K3 random, frequency-informed, near, partial-information, LLM-assisted, VLM/generator-assisted, and adaptive strategies.
- **C4 — Private and unlinkable verification:** evaluate the frozen predicate while limiting template leakage, semantic inversion, database-only validation, policy/transcript/adaptive-query leakage, cross-domain linkage, and leakage under explicit compromise scenarios.
- **C5:** not retained separately after P8. Adaptive verification-oracle leakage is a required attack/privacy dimension under C3/C4.

C1 and C2 are enabling contributions. If the constructive semantic path survives, C3 and C4 remain the strongest eventual security/privacy contributions. Their scientific meaning is unchanged by this narrative reframe.

## Practicality is measured, not assumed

RQ6 asks what client-side computation, bandwidth, latency, storage, trust, and deployment assumptions the primitive requires. P9-v3B has not established actual resource needs. Access to a powerful research GPU is experimental infrastructure and does not make that hardware part of the intended architecture. If trusted-client execution is impractical, that is a valid deployment limitation, restricted-use result, failed practicality gate, or negative outcome.

Practicality may not be “repaired” by sending secret-bearing prompts, images, observations, or graphs to an untrusted cloud. This project also does not replace the visual reconstruction path with direct prompt/text authentication without a separately authorised research change.

## Why this is a new version

P6 and P7 concern `visual-semantic-pipeline-v1`: a fixed untyped/weighted representation, matcher families selected before the pilot, and a paired image-versus-text diagnostic. P6 found a targeted-neighbour failure; P7 found no material benefit from the tested image pathways. Neither phase tested the v2 typed graph, system-derived `M/T`, independent generative reconstruction contract, or private verifier.

The v2 direction is therefore not a retune. It requires a new hypothesis, new data, new preregistration, new identifiers, and new gates. The v1 artifacts remain frozen formative evidence.

## Closest-work boundary

VSA already establishes image-independent visual-semantic authentication based on canonical objects, attributes, quantities, quadrant location, quantity operators, conjunction, and a semantic-plus-password hash binding. The v2 project cannot claim novelty for those components or for policy-based semantic authentication.

The candidate gap is the complete composition:

```text
independent generative reconstruction
+ canonical typed visual-semantic graph
+ system-derived mandatory/tolerant acceptance policy
+ explicit acceptance-region and budgeted guessing analysis
+ private, policy-hiding, domain-separated verification
```

P8 tested this combination against visual/graphical authentication, VSA, semantic/story authentication, generative graphical authentication, fuzzy extractors and PAKE, exact/fuzzy/circuit/committed PSI, private fuzzy records and graph/vector/biometric matching, protected templates, OPRF/OPAQUE, AI guessing, and adaptive-oracle attacks. All component mechanisms are prior art. The remaining combined empirical/systems question was not found in the focused verified corpus, so Gate V2-N passed with narrowed claims. This is not an exhaustive absence or “first” claim.

## P9 evidence and reframe boundary

P9-v2 tested `image -> general VLM -> exact complete graph JSON -> strict validator`. Moondream emitted non-JSON and SmolVLM2 emitted malformed/truncated JSON. One invalid among 32 made the 0.98 validity threshold unreachable, so the frozen path correctly failed. Full semantic F1, determinism, error strata, and full latency were not estimated. The conclusion is architectural and bounded, not universal.

P9-v3A separates perception from deterministic compilation. It freezes two modular pipelines, 240 new future capability images across controlled and naturalistic strata, at least 320 exact compiler tests, type-level statistical eligibility, and Gate V3-A1. A later, separately preregistered P9-v3C and Gate V3-A2 would test independent reconstruction. P10 remains blocked until V3-A2. No v3 performance result exists.

## Evidence boundaries

- P9-v2 provides only the bounded negative structured-output result above. No v3 performance, security, privacy, usability, or deployability result exists yet.
- No human recall, memorability, usability, preference, accessibility, natural secret-selection entropy, or real-world authentication-time inference is authorised.
- The project does not establish that images are easier to remember, that the primitive should replace passwords, or that it is superior to passwords, passkeys, biometrics, or hardware authenticators.
- Technical reconstruction trials use researcher-controlled concepts and paraphrase/style/seed variation only.
- The twelve sealed v1 P6 test families remain untouched.
- VSA FAR/FRR values are baseline evidence from that paper, not project results; its positive FRR construction is not independent VLM re-inference.
- Hashing or encryption alone does not establish privacy or offline resistance for a small semantic space.

## Decision sequence

P8 completed novelty refresh and the original v2 freeze. P9-v2 failed Gate V2-A and remains immutable. P9-v3A is an explicit new-version reframe governed by `docs/formal_specification_v3.md` and `experiments/v3/config/*.json`; it is not a retune or bypass. Gate V3-A1 controls modular extraction, Gate V3-A2 controls independent reconstruction, and only V3-A2 can unlock P10. Later V2-B–V2-F gates remain. Valid outcomes include standalone authentication, a narrowed factor, a policy-constrained or restricted/high-value setting, another bounded deployment, a negative/measurement paper, or stopping the project.
