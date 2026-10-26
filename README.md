# Semantic Secrets

Research toward EuroS&P 2027 on **reconstruction and security-relevant semantic distinctions in visual authentication**.

## Active question

Can an intended semantic credential be reconstructed reliably while related unauthorized alternatives remain distinguishable, and how do perception and normalization affect that balance?

The immediate study connects perception and normalization errors to authentication outcomes. It compares one feasible generative VLM pipeline and one feasible specialized perception pipeline through a common deterministic graph compiler and evaluation method. Generated naturalistic images test the reconstruction workflow; controlled drawings isolate errors; photographs test external visual generalization. Exact models, data and metrics still require a detailed protocol.

The author manually labels actual image content. Intended concepts are recorded separately to distinguish generation errors from extraction errors. Deterministic reviewed normalization is primary; live LLM normalization is an optional ablation. Initial experiments use approved APIs on non-secret fixtures. Local model execution and private verification are later, separate goals.

## Approval and failure handling

**Before every phase:** explain what will be done, how, why, dependencies, costs, success/failure interpretation and alternatives; then wait for the author's explicit authorization. Direction approval does not authorize execution.

**If something fails:** preserve the result, diagnose the issue, explain what it establishes, offer alternatives and recommend the next step. Do not automatically reject the hypothesis or terminate the project. Frozen results are never repaired by post-hoc tuning.

See [phase workflow](docs/phase_workflow.md). The present authorization covers this documentation amendment only.

## Current status - 26 October 2026

- The v4 direction is approved. **No P9-v4 phase has started.** The next step is a detailed P9-v4A design proposal.
- P0-P7 remain historical v1 evidence. P6's targeted-neighbor failure and P7's image-stage finding remain unchanged; the twelve sealed v1 families stay sealed.
- P8 passed its earlier scoped novelty gate; v4 requires a focused novelty review.
- P9-v2 failed its direct complete-JSON schema requirement. This is bounded negative evidence, not a fair completed comparison against v3/v4 or proof that VLM extraction is impossible.
- P9-v3's methodology and compiler/runtime preparation remain available; its empirical branch is paused. The prior audit reported 421 passing core tests including 320 compiler cases, not model accuracy.
- The v3 dataset contains 240 images and 120 controlled references. Naturalistic final references, manifest/support audit and ground-truth freeze remain incomplete. Actual remote generator weights/settings are unattested.
- The audited one-to-one entity-scoring bug and moved manual-script root-path errors remain unresolved. Repairs belong to a separately authorized implementation phase.
- No v4 capability, independent reconstruction, attacker-resistance, local-performance or private-verification result is established.

## Read first

1. [AGENT.md](AGENT.md): active contract and claim boundaries.
2. [PLAN.md](PLAN.md): active phases, deadline targets and historical programme reference.
3. [Research direction v4](docs/research_direction_v4.md): question, proposed contributions and scope.
4. [P9-v4 study design](docs/p9_v4_study_design.md): shared comparison and open protocol decisions.
5. [Phase workflow](docs/phase_workflow.md): approval, diagnosis and continuation rules.
6. [Security model v4](docs/security_model_v4.md) and [claim matrix](docs/threat_claim_matrix_v4.csv): current threat/evidence boundary.
7. [DECISIONS.md](DECISIONS.md): append-only decision history, including DIRECTION-V4-01.
8. [VSA comparison](docs/vsa_2026_comparison.md): mandatory closest-work boundary.
9. [Paper plan](docs/eurosp2027_paper_plan.md) and [build guide](paper/README.md): anonymous planning manuscript.

The v2/v3 specifications, experiment configurations and results retain their original meanings. Their old execution sequences do not authorize v4. The prior direction is preserved in docs/research_direction_v2.md.

## Target venue

**12th IEEE European Symposium on Security and Privacy, Madrid, 5-9 July 2027.** Mandatory registration: **25 November 2026 AoE**. Full paper: **2 December 2026 AoE**. Supplied IEEE template, A4, 13 body pages. See [requirements](docs/eurosp2027_requirements.md) and [submission metadata](docs/eurosp2027_submission.json).

The source builds an anonymous planning draft, not a finished submission. Submission requires separate authorization and completed evidence.

## Scientific boundaries

No human-subject study or memorability/usability/password-superiority claim. Pixels supply no credential entropy. Algorithms and thresholds are public; an attacker wins with any accepted alternative. Random FAR does not establish guessing resistance. API feasibility does not establish provider privacy or local performance. Private verification needs independent construction-specific evidence. Negative results remain evidence; continuation decisions require diagnosis and author involvement.

Large models, raw images/data, credentials, secrets and caches stay out of Git. Version compact configurations, manifests, tests and provenance. Preserve unrelated work and historical evidence.
