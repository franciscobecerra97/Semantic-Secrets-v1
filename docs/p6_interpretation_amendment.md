# P6-R interpretation amendment

**Date:** 2026-08-25

**Status:** Frozen interpretive amendment; P6 data, code, configuration, thresholds, hashes, and results are unchanged.

## What P6 measured

P6 measured reliability and **conditional acceptance after a candidate had already been constructed** from controlled pair classes. In particular, its targeted-neighbour FAR estimates

```text
P(accept | the submitted candidate is already a frozen one-atom near neighbour).
```

This is a useful stress test of the acceptance boundary. It is not the operational probability that an attacker can discover such a candidate within a realistic number of guesses.

The missing operational quantity is

```text
P(success within B attempts | K_i),
```

where `B` is a fixed guess budget and `K_i` is an attacker-knowledge condition. A high conditional near-neighbour acceptance rate can coexist with either high or low practical attack success, depending on how common, discoverable, and rankable accepted neighbours are. P6 did not measure those factors.

## Gate A interpretation

The original P6 observations and frozen checks still fail: same-concept reliability was incomplete, targeted near-neighbour samples overlapped positives, and the uncertainty bounds did not establish a useful operating region. P6 therefore does not pass Gate A.

Gate A is amended from a conclusive `stop-or-reframe` security disposition to **conditional failure / unresolved security viability**:

- **conditional failure:** the frozen matcher/representation failed the declared conditional separation and reliability criteria;
- **unresolved security viability:** P6 alone cannot establish practical attack success within a budget;
- **not a pass:** no standalone or second-factor authentication claim is authorised;
- **not impossibility evidence:** the result does not prove that semantic authentication, or even this broad design family, cannot work.

P9/P10 remain blocked. P7 may answer only the bounded image-stage question. P8 must measure budgeted attacker success, after which Gate A2 integrates quality and attacker-budget evidence.

## Attacker knowledge K0–K3

| Level | Knowledge available before guessing | P6 relation |
|---|---|---|
| K0 | Generic/random guessing with public algorithms and configuration, but no target-specific information. | P6 random negatives are closest to K0, but are not a complete K0 attack distribution or ordered budgeted strategy. |
| K1 | Population or source-distribution knowledge that improves guess ordering, without target-specific facts. | Not measured by P6. |
| K2 | Partial target information, such as known semantic atoms, context, or attributes. | P6 partial-information diagnostics are conditional finite-dictionary probes, not budgeted K2 success. |
| K3 | Strong near-secret knowledge sufficient to construct candidates very close to the enrolled concept. | P6 frozen one-atom near negatives approximate a K3-style conditional stress test. They do not estimate the probability or cost of reaching that state. |

The levels describe knowledge conditions, not mutually exclusive attack algorithms. All public algorithms, models, canonicalisation rules, thresholds, and protocol code remain known to the attacker.

## Required P8 and Gate A2 evidence

P8 must report success@1, success@5, success@10, success@B, and guesses-to-success for supported K0–K3 strategies. Online and offline views must be separate. Online rate limits are measured assumptions; they cannot excuse an otherwise trivially enumerable semantic space.

Gate A2 will combine:

1. P6 conditional reliability and acceptance-boundary evidence;
2. P7's image-stage disposition;
3. P8's `P(success within B attempts | K_i)` evidence and uncertainty;
4. deployment assumptions, including rate limits and any non-colluding or key-holding service.

Gate A2 must select one position: standalone authentication, second factor, policy-constrained credential, negative/measurement contribution, or stop. A trusted third party can help only through explicit keys, protocol enforcement, rate-limit enforcement, and non-collusion assumptions. It does not create semantic entropy, and its benefit cannot be attributed to model secrecy.

## Semantic-tolerance boundary

This amendment does not redesign the credential as exact prompt equality or exact set equality. Semantic tolerance remains part of the research question. A future mandatory-anchor plus tolerant-attribute policy may be scientifically motivated, but it requires a new scheme/version, independent rationale, new data, preregistration, and its own gate. It may not be implemented or tuned against P6 or P7 observations.
