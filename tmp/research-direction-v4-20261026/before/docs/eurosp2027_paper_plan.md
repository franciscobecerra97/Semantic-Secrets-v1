# EuroS&P 2027 paper narrative and structure

Venue migration approved by the project author on 26 October 2026. This is manuscript preparation, not a completed P18 phase or permission to execute a blocked experiment.

## Narrative

Working title: **Semantic Secrets: Security and Privacy of Reconstructable Visual Authentication**.

Start from a security problem: tolerating independently reconstructed semantics changes which attacker inputs authenticate. Study the complete acceptance region and the trade-off between legitimate reconstruction and reachable alternatives. Explain the attacker, public algorithms, compromised view, query budget and success event early. Then ask whether private verification preserves the exact predicate while reducing template, policy and linkage leakage.

Keep C1 reconstructability and C2 system-derived policy as enabling hypotheses. C3 acceptance-region attacks and C4 construction-specific private verification remain the potential principal contributions. A detector, graph, prompt, standard primitive or notation is not independently novel. Explicitly distinguish the two VSA baselines. No human-memory, password-replacement or unmeasured deployment claims are introduced.

EuroS&P's security-or-privacy scope removes the old venue-specific requirement to make every finding a privacy-enhancing-technology contribution. It does **not** remove the project's C4 research question or authorize omitting it from a claimed complete C1–C4 system. A security-only measurement paper would require a separate evidence-backed scope decision and prospective evaluation plan; it cannot relabel a failed gate as passed or use old held-out data for tuning.

## Eventual 13-page allocation

These are planning budgets, not promised results or formatting tricks. The current source is an honestly labelled planning draft; empty result sections are not presented as completed research.

| Main-body material | Budget, pages | Evidence required |
|---|---:|---|
| Introduction and contribution boundary | 1.0 | Actual contributions and threat, no speculative achievement |
| Background and closest work | 0.75 | Verified literature and both VSA comparators |
| System and threat model | 1.0 | Parties, assets, K0–K3, compromise/leakage views |
| Reconstruction, compiler and policy design | 1.5 | Frozen versions, algorithm, failure behaviour |
| Evaluation design and reproducibility | 1.25 | Separate capability/reconstruction data, split isolation, baselines, uncertainty |
| Reconstruction and policy results | 1.5 | Constructive V3-A1, V3-A2 and V2-B evidence |
| Acceptance-region attacks | 1.5 | V2-C budget curves, costs and failure strata |
| Private verification and analysis | 1.5 | V2-D/V2-E construction, equivalence, leakage and compromise evidence |
| Practicality | 0.75 | Measured trusted-client and protocol costs |
| Limitations and proactive prevention of harm | 0.75 | Synthetic-data limits, attacks, retention and dual-use risks |
| Conclusion and Data Availability | 0.5 | Bounded conclusions and release/restriction statement |
| Layout and revision reserve | 1.0 | Keep essential evidence in the body |
| **Total** | **13.0** | References/appendices and submission acknowledgments additional |

Keep long compiler vectors, detailed run inventories and supporting proofs in appendices/artifacts. Main threat definitions, principal numbers, privacy assumptions and negative results must remain readable without them.

## Immediate source changes and evidence limits

`paper/draft.tex` uses the supplied IEEE class/options, leads with acceptance-region security, and groups material into introduction, related work, model, design, evaluation, available evidence, security/privacy analysis, limitations, harm, availability and conclusion. It includes anonymous AI-use acknowledgments. `paper/main.tex` is the canonical build entry and inputs that source. The old source/PDF and sample are retained under `paper/templates/popets-2027/`.

The current dataset contains 240 images and 120 controlled references; naturalistic references and the ground-truth freeze remain incomplete. The compiler's 320 locally passing cases are engineering evidence. The evaluator's one-to-one entity-scoring defect and moved manual paths are unresolved implementation blockers from the 26 October audit; this migration does not claim to fix them. GPU execution, v3 capability accuracy, independent reconstruction, policy advantage, budgeted security and private verification remain unmeasured.

The public API dataset has unattested actual weights/settings. Report that limitation; never describe it as pinned local-generator reproduction. VLM prompt/graph experiments under `manual_validation/` remain separate exploratory work.

## Deadline decision

There are 30 calendar days to registration and 37 to the paper date from 26 October. A complete constructive C1–C4 result is a high-risk target given the remaining gates. On **13 November**, inspect completed evidence and decide whether a defensible submission is realistically achievable. If not, record a missed-cycle outcome and continue research; do not create findings, silently drop required experiments, or submit a blueprint as a completed system. Drafting can proceed in parallel with permitted work, but phase completion and submission readiness still require their evidence.
