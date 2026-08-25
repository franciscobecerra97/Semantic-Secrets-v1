# Security and privacy model v2

Status: planning contract. No candidate construction has been selected or proved.

`docs/security_model.md` remains the frozen v1 model. This document governs only the new reconstructable private visual-semantics direction.

## 1. Functional objects

For a controlled concept `C`, free reconstruction prompt `P`, local generator `G`, randomness `r`, and local extractor `E`:

```text
I = G(P,r)
S = E(I) = (V,E_S,A,C_S)
(M,T) = Π(S)
R = Protect(S,M,T,account,service,version)
```

`M` is the mandatory anchor set and `T` the tolerant secondary set. `Π` is system-derived, deterministic, versioned, and frozen before held-out evaluation. An authentication trial independently forms `I'`, `S'`, and `(M',T')`.

The plaintext reference decision is:

```text
Accept_ref(S,M,T,S',M',T'; θ) ∈ {0,1}.
```

Its complete semantics—including missing anchors, duplicates, graph isomorphism/canonical order, count operators, tolerance, malformed inputs, version mismatch, and boundary equality—must be fixed in P8. A private construction is functionally correct only if it returns the same decision except with a stated failure probability.

The semantic acceptance region is:

```text
A(S,M,T) = { (S',M',T') : Accept_ref(...) = 1 }.
```

Security is about finding any member of this region, not recovering the enrolled prompt or pixels.

## 2. Trust and data boundary

- The **trusted client** receives `P`, runs `G`, obtains transient `I`, runs `E` and `Π`, and performs client protocol steps.
- The **authentication service (AS)** stores account state, starts sessions, enforces authorised online policy, and produces or receives the final decision according to the selected construction.
- An optional **privacy/key service (PS)** may hold independent key material or shares. Any non-collusion or isolation assumption must be explicit.
- `P`, `I`, plaintext `S`, and raw embeddings remain local and are deleted when no longer needed under the data-retention contract.
- Public algorithms, model identities, schemas, policy algorithms, and thresholds are not secrets.

## 3. Adversaries and knowledge

- **A1 online guesser:** submits authorised guesses and sees the externally observable response under rate limits.
- **A2 database attacker:** obtains a database snapshot without live server/key-service secrets unless the tested view says otherwise.
- **A3 service/key compromise:** obtains named process state, long-term keys, service shares, logs, or combinations thereof.
- **A4 AI-assisted guesser:** improves proposal/ranking with language, vision, or generation models.
- **A5 partial-information attacker:** knows target attributes/context according to K2 or K3.
- **A6 inversion/reconstruction attacker:** attempts to recover semantic facts, an equivalent accepted graph, or distinguishing attributes from protected state/transcripts.
- **A7 linker:** distinguishes same-secret from different-secret records or sessions across accounts/services.
- **A8 adaptive collision/oracle attacker:** chooses queries based on prior outcomes to locate an accepted region, infer policy, or exploit malformed/graded responses.

Knowledge levels:

- `K0`: generic/public information only;
- `K1`: population/source/frequency information;
- `K2`: partial target facts;
- `K3`: strong near-secret information.

For a strategy `Q`, budget `B`, public context, auxiliary knowledge `K_i`, and view `V`:

```text
Succ(Q,B,K_i,V) = Pr[∃ j ≤ B : candidate_j ∈ A(S,M,T)].
```

Report online and offline success separately. Offline evaluation must measure whether stolen state validates or materially improves ranking of candidate graphs without an uncompromised rate-limiting service.

## 4. Protected assets and required goals

| ID | Goal | Minimum evidence before claim |
|---|---|---|
| V2-G1 | Technical reconstruction correctness | Independent generation/re-extraction trials; preregistered FRR, targeted FAR, uncertainty, failure strata |
| V2-G2 | Acceptance-region guessing resistance | K0–K3 and AI/adaptive success@budgets; distribution and oracle named |
| V2-G3 | Template confidentiality | Construction analysis plus semantic recovery/inversion attacks against each stored view |
| V2-G4 | Database offline-validation resistance | Exact database view; candidate-testing implementation/throughput; formal argument where applicable |
| V2-G5 | Policy privacy | Leakage/attack analysis for M/T identities, types, counts, operators, weights, threshold, graph size |
| V2-G6 | Transcript and decision minimisation | Message trace; ideal leakage; passive/active analysis; no hidden score/cardinality assumption |
| V2-G7 | Cross-service/account unlinkability | Domain-separated records; same/different game with hard negatives and uncertainty |
| V2-G8 | Compromise containment | Separate database, AS, PS/share, sub-threshold, colluding, and total-compromise outcomes |
| V2-G9 | Replay/session/context integrity | Nonce and account/service/version binding; replay, cross-context, downgrade tests |
| V2-G10 | Reference-function preservation | Boundary, malformed, duplicate, and version differential tests against `Accept_ref` |

No row is a present achievement.

## 5. Observable views and leakage

Each construction must enumerate the exact contents of:

1. client state before/after deletion;
2. stored database record;
3. AS long-term and ephemeral state;
4. PS/share state, if any;
5. network/application transcript;
6. logs, errors, timing and message sizes;
7. output received by every party;
8. combined views after named compromises.

Desired normal-session leakage is public configuration, coarse unavoidable transport metadata, and one authorised context-bound `Accept/Reject` bit. The following are additional leakage unless explicitly justified: score, intersection size, matching anchors, policy shape, failure reason, stable tag, raw/derived embedding, deterministic token, or distinguishable early-abort timing.

Policy privacy cannot be inferred from hiding token strings while exposing operator/quantity metadata. Unlinkability cannot be inferred from per-user salts unless the complete record and transcript distributions support the claim.

## 6. Compromise requirements

At minimum compare:

- database snapshot only;
- AS state without an independent PS/key share;
- each individual PS/share view;
- all in-scope sub-threshold share combinations;
- AS plus PS or threshold key capability;
- total service/key compromise;
- client compromise, separately, if placed in scope.

For total compromise, semantic guessing is expected to be feasible whenever the combined state evaluates candidates. Do not promise otherwise by default. If conditional protection depends on non-collusion, HSM/TEE isolation, threshold availability, or an online service, state the assumption and failure mode. No silent fallback to a weaker verifier is allowed.

## 7. Semantic correctness is not cryptographic privacy

FAR/FRR describe the empirical semantic decision under declared trial distributions. They do not show secrecy, offline resistance, or unlinkability. Conversely, secure computation can hide inputs to a weak predicate while leaving a large or easily guessed acceptance region.

The phase order is therefore binding:

1. freeze and test independent reconstruction (`V2-A`);
2. establish policy value (`V2-B`);
3. measure acceptance-region attacks (`V2-C`);
4. select/prove/implement private evaluation (`V2-D`);
5. attack its privacy and compromise claims (`V2-E`).

No later gate can compensate for an earlier failure.

## 8. Claim limits

Do not use unqualified “secure,” “private,” “zero knowledge,” “offline resistant,” “non-invertible,” “unlinkable,” or “Accept/Reject-only.” Every claim names a construction, adversary behaviour, knowledge level, compromise view, leakage, budget, dataset, and evidence type.

VSA's server-opaque SHA-256 binding is a comparison baseline, not evidence for V2-G3–V2-G8. Argon2id and salting can raise per-guess cost but do not create semantic entropy or private computation.
