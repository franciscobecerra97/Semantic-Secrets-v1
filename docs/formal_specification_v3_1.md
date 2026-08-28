# Formal specification v3.1 addendum: pre-execution suitability amendment

Status: prospective P9-v3A.1 freeze. It amends, but does not overwrite, `formal_specification_v3.md` v3.0.0. No v3 experimental output existed when this addendum was frozen.

Historical-method note (2026-08-28): Section 5 records the v3.1 decision but is superseded for execution by `formal_specification_v3_2.md`. P9-v3B has no human annotators; project-authored model-blind ground truth must instead satisfy the v3.2 freeze. All other v3.1 clauses remain active.

## 1. Binding version

The binding future capability design is `semantic-secrets-preregistration-v3.1.0` with `visual-observation-v3.1.0`. All v3.0.0 definitions remain in force except where this addendum or the v3.1 machine-readable configs explicitly supersede them. P9-v2 and v3.0.0 remain historical records.

## 2. Hardware and resource measurement

Let `CapGPU(h)` be installed device memory and `PeakVRAM(p,h)` the measured peak allocation of complete pipeline `p` under the frozen measurement protocol. There is no upper gate on `CapGPU(h)`. The resource condition remains:

`PeakVRAM(p,h) <= 24 GiB`

and `PeakRSS(p,h) <= 32 GiB`. A larger GPU does not change these bounds. The execution record must contain the full hardware/software environment. Hardware choice precedes validation and cannot depend on semantic validation outcomes.

## 3. Pipeline set

The complete set is exactly:

`P = {v3.1-gdino-siglip2, v3.1-egtr-siglip2}`.

The first pipeline retains the v3.0 Grounding DINO/SigLIP2 components. Its pair-crop action/interaction scorer is a falsifiable compositional hypothesis, not a graph-native relation detector.

The second replaces SGTR with EGTR(VG) for pre-output reproducibility reasons. EGTR emits object logits, normalized boxes, relation logits, and connectivity scores. The adapter may only threshold these tensors on development data, intersect exact normalized labels with the frozen lists, construct bounded observation records, and pass those records to the unchanged deterministic compiler. It may not generate, repair, or semantically map free-form credential text.

## 4. Support and type eligibility

For type `t` and stratum `d`, let `PosSupport(t,d)` be the number of predeclared visible reference-atom opportunities and `NegSupport(t,d)` the number of predeclared applicable false-label opportunities under the same scope. An absent label outside a predeclared opportunity is not counted.

`GateEvaluable(t,d) = [PosSupport(t,d) >= 60 and NegSupport(t,d) >= 60]`.

`Eligible(p,t)` now additionally requires `GateEvaluable(t,A)` and `GateEvaluable(t,B)` before applying the unchanged v3.0 metric thresholds separately in both strata. If support is insufficient, the result is `not_gate_evaluable`, not pass or fail.

The predeclared primary gate types are entity, colour, count, binary interaction, and geometry relation. Size, material, pattern, unary action, and scene remain observable but are frozen at 30 positive/30 negative validation opportunities per stratum and therefore cannot enter `L_cred-v3.1.0`. No post-output support increase is permitted.

## 5. Historical v3.1 annotation prerequisite (superseded by v3.2)

Naturalistic labels require two independent human annotators who have not seen perception outputs. One may be an independent external annotator. The annotator identities/roles, availability, rubric version, independence statement, and adjudication procedure must be recorded before any capability image is created. Model-assisted ground truth and fabricated or same-person duplicate annotation are forbidden. Until this record exists, P9-v3B is blocked.

## 6. Gate V3-A1

The v3.0 compiler, failure, repeatability, metric, latency, RSS, and numeric peak-VRAM thresholds remain unchanged: pipeline failure point/upper-Wilson bounds are 0.05/0.10; observation and graph repeat point/lower-Wilson bounds are 0.95/0.90; measured VRAM/RSS limits are 24/32 GiB; median/p95 latency limits are 30/60 seconds per image; and each supported type separately requires precision point/lower-bootstrap 0.90/0.85, recall 0.70/0.60, F1 0.80/0.70, and coverage point/lower-Wilson 0.75/0.65 in both strata. Installed GPU capacity is removed from the gate. Type eligibility additionally requires the v3.1 support predicate. Gate V3-A1 still requires one whole pipeline with eligible entity, two additional types, and at least one structural type; cross-pipeline union remains forbidden.
