# P8 focused novelty review and Gate V2-N

Status: frozen on 2026-08-25. This is a focused primary-source review, not a systematic-review claim and not proof of global novelty.

## Decision

**Gate V2-N passes with mandatory narrowing.** The reviewed literature contains every major component separately, but no verified source in the focused search combines all of the following in one evaluated authentication system:

```text
free natural-language reconstruction of a remembered visual concept
+ independent local text-to-image generations and fresh typed extraction
+ deterministic system-derived mandatory/tolerant graph policy
+ finite-budget K0-K3 semantic acceptance-region attacks
+ construction-specific policy-hiding, domain-separated private verification
```

This remaining difference is sufficient to justify the bounded P9 representation study. It does not establish that the mechanism works, that people can reproduce such concepts, that the resulting credential is strong, or that a later cryptographic composition is novel or feasible.

## What the review removed from the novelty space

- VSA already establishes image-independent visual-semantic authentication, canonical visual tokens, object/attribute/count/quadrant facts, quantity operators, conjunction, user-selected semantic rules, and semantic-plus-password hash binding.
- SemanticLock, PassPoints, PassStyles, and Omokage establish semantic/graphical authentication, tolerant visual entry, and generative graphical authentication. PassStyles and Omokage are especially important: generated images and changing visual instances are not new authentication ideas.
- Fuzzy extractors, fuzzy PAKE/fuzzy aPAKE, OPRF/OPAQUE, exact/fuzzy/circuit PSI, committed-set PSI, private fuzzy-record computation, encrypted vector matching, and private graph operations establish the cryptographic building blocks. C4 cannot claim a new primitive.
- Protected biometric templates establish that irreversibility and unlinkability require explicit attack evidence; hashing, salting, encoding, or encryption are insufficient arguments.
- Password-generating language models and biometric hill-climbing attacks establish AI-assisted guessing and adaptive verifier-oracle attacks. Adaptive Accept/Reject leakage is therefore not a standalone C5 contribution.

## Narrowed contribution hypotheses

| ID | P8 disposition | Permitted prospective wording |
|---|---|---|
| C1 | Retained, narrowed | Measure whether free-language reconstructions passed through independent text-to-image generation and fresh extraction yield stable, separable typed semantics. Never claim first generative, graphical, semantic, image-independent, or image-changing authentication. |
| C2 | Retained only as a systems component | Measure whether a deterministic system-derived mandatory/tolerant graph policy improves a frozen trade-off over dense, global-fuzzy, and VSA-style baselines. The notation, graph representation, policy idea, and matching operators are not standalone novelty. |
| C3 | Retained as a principal empirical contribution hypothesis | Characterise this system's semantic acceptance region under frozen K0-K3 distributions, finite budgets, AI assistance, and adaptive Accept/Reject feedback. Guessing, FAR, AI generation, and oracle attacks are prior art. |
| C4 | Retained as a principal systems/privacy contribution hypothesis | Select and analyse a construction-specific composition that preserves the frozen predicate while measuring exact stored/transcript/compromise leakage, offline validation, policy inference, and cross-domain linkage. No primitive novelty is claimed. |
| C5 | Rejected as standalone; folded into C3/C4 | Adaptive queries remain a required attack dimension and protocol-leakage test only. Reopening C5 requires a later distinct estimand and a new novelty review. |

## Closest-work comparison

| Work/family | Established overlap | Remaining project-specific question |
|---|---|---|
| VSA (Jeong 2026) | Image-independent VLM semantics, canonical tokens, quantities/operators, conjunction, user-selected rules, password/hash binding, FAR/FRR | Independent generative reconstruction with fresh extraction; system-derived typed relations; budgeted acceptance-region attacks; private/domain-separated verification |
| SemanticLock; PassPoints | Semantic graphical stories and tolerant graphical entry | No generative reconstruction, typed scene graph, or private policy verifier |
| PassStyles; Omokage | StyleGAN-generated changing authentication images, recognition rules, observation/shoulder-surfing evaluation | Different interaction: recognition among displayed candidates, not free prompt reconstruction followed by independent T2I generation and canonical semantic comparison |
| Fuzzy extractors; fuzzy PAKE/aPAKE; OPAQUE | Noisy-source key recovery and password-authenticated key exchange under formal models | Whether the low-entropy structured semantic predicate can be composed without creating an offline validation or policy-leakage channel |
| Exact/fuzzy/circuit/committed PSI and private fuzzy records | Private exact/approximate matching, threshold rules, malicious security, and cross-session input consistency | Minimal one-bit evaluation of this graph policy, persistence/compromise behavior, policy privacy, and domain-separated records |
| Private graph operations; private/FHE biometric matching | Private graph intersection/union and encrypted threshold vector/biometric matching | Typed mandatory/tolerant semantic predicate and low-entropy semantic guessing under authentication-specific stored/transcript views |
| Cancelable/protected templates | Irreversibility, renewability, and unlinkability definitions and attacks | Construction-specific evidence for semantic graphs and accepted equivalents |
| PassGPT; biometric hill climbing | Model-assisted candidate ordering and adaptive score-oracle search | Frozen finite-budget attack curves for this semantic acceptance region, including one-bit feedback |

## Search coverage and limits

The refresh checked primary or authoritative records for graphical/image authentication, SemanticLock, VSA, generative-AI authentication, fuzzy extractors and secure sketches, fuzzy PAKE/aPAKE, OPAQUE, OPRF/VOPRF, exact/fuzzy/circuit/committed PSI, private fuzzy records, private biometric/vector/graph matching, protected templates, inversion/linkage, adaptive verifier attacks, and AI-assisted guessing. Traceable entries are in `docs/related_work.csv` and `paper/references.bib`.

The search was deliberately focused. It did not prove an exhaustive absence result, and the project must repeat the claim audit before submission. Any newly found work that combines the remaining properties can narrow or defeat Gate V2-N without invalidating this record.

## Gate consequence

P9 is authorised under `experiments/v2/config/preregistration_v2.json`. P10 remains blocked on Gate V2-A; P11 remains blocked on Gate V2-B; cryptographic design remains blocked on Gate V2-C. A later technical failure cannot be rescued by this novelty gate.
