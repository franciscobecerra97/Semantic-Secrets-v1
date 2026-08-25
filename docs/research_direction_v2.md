# Research direction v2

Status: Gate V2-N passed with narrowing on 2026-08-25; no v2 experiment has run.

## Thesis

Semantic Secrets v2 studies whether a remembered visual concept can be reconstructed through independently generated images, converted locally into a canonical typed semantic graph, and verified under a system-derived tolerance policy without exposing a reusable semantic template or a practical guess-testing oracle.

The image is not a password object and its pixels do not supply entropy. It is a reconstruction medium. The prompt is an interface. The credential is the policy-constrained canonical semantics and, operationally, the full set of semantic inputs the verifier accepts.

## Scientific chain

Let a controlled concept be `C`, a reconstruction prompt be `P`, generator randomness be `r`, a frozen local generator be `G`, and a frozen local extractor be `E`:

```text
I = G(P,r)
S = E(I)
S = (V,E_S,A,C_S)
Π(S) = (M,T)
R = Protect(S,M,T,context)
```

`M` contains mandatory discriminative anchors; `T` contains explicitly tolerant secondary facts. At authentication, independently generated `I'` yields `S'` and `(M',T')`. A plaintext reference predicate first decides whether the mandatory constraints and tolerant threshold are satisfied. A private protocol must later reproduce that same bit without disclosing more than its stated leakage.

This creates two independent questions:

1. **Semantic correctness:** Does the reconstruction/extraction/policy pipeline accept independent same-concept generations and reject targeted alternatives under frozen rules?
2. **Cryptographic privacy:** Does the selected construction hide inputs, policy, records, and linkage under its declared compromise and interaction model while preserving the reference decision?

Passing one does not imply the other.

## Candidate contributions

- **C1:** technical stability of generatively reconstructable visual-semantic credentials, without human claims.
- **C2:** a frozen system-derived mandatory/tolerant policy over typed semantic graphs, evaluated only as part of the combined system.
- **C3:** acceptance-region security measured as success within attacker budgets under K0–K3 and AI/adaptive strategies.
- **C4:** construction-specific private and unlinkable verification, including database, transcript, policy, compromise, and offline-validation views.
- **C5:** not retained separately after P8. Adaptive verification-oracle leakage is a required attack/privacy dimension under C3/C4.

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

## Evidence boundaries

- No v2 performance, security, privacy, usability, or deployability result exists yet.
- No human recall, memorability, or user-choice inference is authorised.
- Technical reconstruction trials use researcher-controlled concepts and paraphrase/style/seed variation only.
- The twelve sealed v1 P6 test families remain untouched.
- VSA FAR/FRR values are baseline evidence from that paper, not project results; its positive FRR construction is not independent VLM re-inference.
- Hashing or encryption alone does not establish privacy or offline resistance for a small semantic space.

## Decision sequence

P8 completed only novelty refresh, formalisation, baseline definition, and preregistration. `docs/p8_novelty_review_v2.md`, `docs/formal_specification_v2.md`, and `experiments/v2/config/preregistration_v2.json` are the freeze. Gates V2-A, V2-B, V2-C, V2-D, V2-E, and V2-F prevent later cost from laundering an earlier scientific failure. The valid terminal outcomes include a narrowed factor, a policy-constrained credential, a negative/measurement paper, or stopping the project.
