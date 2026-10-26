# Security model v4: measurement scope and deferred deployment

Approved direction: 26 October 2026. This document defines the scope of the prospective study, not a proven protocol. Detailed experimental rules require authorized preregistration.

## Functional objects and attacker success

For intended concept C, reconstruction prompt P and generator randomness r, I = G(P,r). A versioned pipeline emits O; normalization N and deterministic compilation produce S = Compile(N(O)), or a typed failure.

A frozen policy/predicate theta defines A_theta(S) = {S' : Accept_theta(S,S') = 1}. An attacker wins by reaching any accepted alternative within budget B; recovering the exact prompt, image or graph is unnecessary. Specify whether candidates are prompts, images or graphs, the interface an attacker can actually submit, and which generation/extraction costs are counted. Direct graph attacks are a separately named abstraction unless a deployed interface permits them.

For strategy Q and knowledge K, report Pr[at least one accepted candidate in B attempts] under the declared experimental distribution. Random FAR, conditional near-neighbor acceptance and adaptive success are distinct estimands. Samples do not enumerate or prove security of the full acceptance region.

All model identities, vocabulary, mappings, compiler/policy algorithms and thresholds are public. Freeze reference correspondence, missing anchors, malformed data, duplicates, counts, thresholds and version mismatch behavior before final evaluation. Errors fail closed for acceptance; preserve separate error categories in research reporting.

## Current experimental trust boundary

Approved API studies use only public or safely authorized non-secret fixtures and simulated/local research accounts. Providers receive images/prompts/observations according to their endpoint; do not claim confidentiality from them. Author labels and intended per-image semantic answers are withheld from extraction and normalization.

The v4 study measures semantic decisions and specified attack budgets. It has no protected database construction, key service, private-verification proof, real account deployment or measured privacy guarantee. Offline plaintext laboratory testing is not evidence of database-compromise resistance.

## Knowledge and observation

- K0: public configuration and generic candidates.
- K1: declared auxiliary/source-frequency information, separated from target evaluation.
- K2: prospectively specified partial target facts.
- K3: strong near-secret knowledge sufficient for close alternatives.

For each attack name auxiliary data, known facts, candidate interface, oracle output, adaptive/nonadaptive behavior, duplicates, budget, randomness and service costs. Adaptive attacks use prior permitted responses; graded scores or diagnostic error messages are not silently available to an Accept/Reject-only attacker.

Report enrollment rejection, technical false rejection, negative acceptance and attack success with exact denominators and family/account uncertainty. No human behavior, natural-choice entropy or password/passkey superiority inference is supported.

## Deferred private-verification goal

The strongest future deployment keeps secret-bearing prompts, images, observations, graphs and embeddings on a trusted client. Local execution requires semantic-parity and performance evidence; API feasibility is insufficient.

Historical C4 and docs/security_model_v2.md retain the required questions for any future constructive private system: exact protected record, named compromise views, template/policy/transcript leakage, database-only candidate validation, cross-domain linkage, replay/version binding and total-compromise limits. Those historical definitions do not make the v4 experiment a private system.

A future protocol branch needs a separately authorized design mapping v4's frozen predicate and tested semantic scope to a construction and its leakage/correctness goals. It cannot inherit old gate passes, claim privacy from hashing/encryption alone, or use cryptography to repair semantic guessability. Cryptographic engineering remains deferred.

## Gates and claim mapping

Use docs/threat_claim_matrix_v4.csv for current claims. V4 review checkpoints distinguish measurement validity, constructive viability and publication readiness. Exact numeric criteria must be prospectively justified and approved. Historical V2/V3 outcomes stay under their original identifiers.

Failures trigger diagnosis, alternatives and an author decision under docs/phase_workflow.md. Preserve negative evidence; do not infer project-wide impossibility from an API error or one tested architecture.
