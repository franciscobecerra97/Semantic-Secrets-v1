# Phase authorization and failure handling

Effective: 26 October 2026. Authority: the project author's explicit instruction and decision DIRECTION-V4-01. This rule applies to every project phase and subphase, including design, implementation, data work, experiments, analysis, manuscript, artifact and submission work.

## Explain, then wait

Before executing a phase, provide the author a detailed, readable proposal containing:

1. **What and why:** the research question, expected outputs, intended contribution and decisions the work will inform.
2. **Current evidence:** inputs, dependencies, unresolved defects and applicable scientific restrictions.
3. **How:** ordered steps, files/components affected, models/services, data/split roles, prompts and normalization, reference authoring, metrics and analysis.
4. **Limits:** exact scope, estimated calls/cost/time/storage where relevant, retry bounds, information sent to providers, and exclusions. Unknown estimates must be identified.
5. **Success and failure interpretation:** checks, criteria, what each possible outcome establishes, and what it cannot establish.
6. **Alternatives:** credible alternatives and why the proposed option is preferred.
7. **Authorization request:** name the phase/subphase and the specific work requiring approval.

Then wait for explicit authorization. Approval of the overall direction, the existence of a plan, elapsed time, or completion of a previous phase does not authorize execution of the next phase. If the user requests a phase without having received its detailed proposal, explain it first and wait. If the user approves the already explained phase, proceed within that scope without asking repeatedly.

Read-only inspection needed to prepare the proposal is permitted; it must not invoke models, acquire datasets, expose held-out inputs, incur charges, or turn into phase execution.

An authorized phase may include its described implementation and validation. Record the approving user instruction, date, phase ID, scope, limits, artifacts and any changed assumptions. Substantive scope changes require a revised explanation and authorization.

The current authorization covers documenting the approved direction, updating manuscript/research-description sources and PDFs, and checking those edits. It does not authorize P9-v4A or any experiment, repair of the evaluator, API invocation, dataset acquisition/generation, GPU rental or submission.

## When something fails

Preserve logs, inputs, raw outputs, configuration hashes and the failed result. Stop only the affected action when continuing would corrupt evidence, violate a frozen protocol, exceed the approved budget, or repeat an unresolved failure.

Explain to the author:

- what happened and which outputs are affected;
- whether the cause is known or suspected, with supporting evidence;
- whether it is an infrastructure/API, implementation/evaluation, annotation/data, output-format, semantic capability, statistical-support, or hypothesis-level issue;
- what conclusions the failure supports and what conclusions it does not support;
- alternative repairs, model/adapter choices, data improvements or prospective redesigns, their costs and scientific consequences;
- the recommended next step and the authorization needed.

An operational error is not a rejected research hypothesis. A valid negative experiment is evidence about its stated conditions, not automatic termination of the project. Do not discard an approach, declare the research impossible, change the project goal or terminate the programme without explaining the evidence and alternatives and obtaining the author's decision.

This does not require endless retries or force a positive result. Existing failures stay failures. Never lower a frozen threshold, repair held-out outputs, omit inconvenient cases, or rename a failed run as successful. A substantive change after output creates a new version and, where necessary, fresh evaluation data. Negative or restricted findings can remain scientifically useful.

A retry with identical scientific settings is permitted only within an explicitly approved bounded retry policy. Unexpected failures outside that policy are reported before additional execution. Pre-authorized deterministic debugging/tests may diagnose an issue; they do not authorize new model runs or methodology changes.

## Close one phase before proposing the next

Report outputs, validation, deviations, failures, uncertainties, scientific interpretation and the recommended next phase. Distinguish engineering completion, valid measurement, constructive viability and publication readiness.

Statuses: awaiting proposal; awaiting authorization; authorized; in progress; blocked pending diagnosis/decision; complete; superseded by an approved version. Gate outcomes and experimental results are separate fields; a failed experiment can yield a complete, valid report.

Existing phase checkpoint instructions in PLAN.md apply only to completed, authorized phases and their own changes. This documentation amendment is not completion of an experimental phase. Never include unrelated user changes in a checkpoint.
