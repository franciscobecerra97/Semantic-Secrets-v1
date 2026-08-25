# Security and privacy model v1

Status: frozen for P3–P8 pilot design on 2026-08-24; interpretively clarified by P6-R on 2026-08-25; protocol and deployment architecture remain unselected until a constructive Gate A2 and D6/D7.

This document makes the project hypotheses falsifiable. It does not claim that a future construction satisfies any goal below. A claim becomes valid only for a named construction, adversary, compromise state, and evidence method.

## 1. Scope and trust boundary

### Actors

- **User (`U`)** chooses and later attempts to recreate a concept. Human choice, memory, and usability are outside this paper's evidence.
- **Client (`C`)** is trusted for the target design. It receives the prompt, generates or receives the local image, extracts/canonicalises semantics, and performs client protocol steps.
- **Authentication service (`AS`)** manages accounts, sessions, rate limits, stored records, and the final authentication policy.
- **Privacy service (`PS`)** is an optional, administratively independent party used by two-server or threshold candidates.
- **Isolated key service (`IKS`)** is an optional HSM/TEE/process-isolated key and policy boundary. Isolation is an operational assumption, not a cryptographic substitute.
- **Adversary (`Adv`)** may control an authenticating client, observe protocol-defined outputs, steal named state, use public data and AI models, or make services deviate as specified by A1–A8.

### Target data flow

```text
concept c / prompt p
  -> trusted local generation G_v (optional path under Gate B)
  -> local observation x (normally an image)
  -> trusted local extraction and canonicalisation F_v
  -> semantic credential s
  -> registration/authentication protocol Pi
  -> protected record r and Accept/Reject
```

In the strongest target, plaintext prompts, images, semantic atoms, raw embeddings, and exact similarity scores remain on `C`. Account identifiers, public version identifiers, protocol messages, record metadata, and a final decision may be visible to `AS`. Any weaker flow must enumerate the additional fields and the goal it forfeits.

### Baseline trust and channel assumptions

- The legitimate user's client and pinned local models are trusted while the credential is entered. Client compromise, keylogging, malicious model weights, and endpoint exfiltration defeat credential confidentiality and are outside v1 guarantees.
- Authenticated, confidential, replay-resistant transport (for example, correctly configured TLS) is assumed. The application protocol must still bind messages to the service domain, account, phase, session, and fresh challenge where applicable.
- `AS`, `PS`, and `IKS` may be honest-but-curious or malicious only as stated for a concrete candidate. A passive-only proof cannot support an active-security claim.
- Public algorithms, schemas, model identifiers, canonicalisation rules, thresholds, and protocol code are known to the adversary. Security may not rely on their secrecy.
- The semantic source is non-uniform and potentially low entropy. No goal assumes image-pixel entropy or an ideal uniform secret.

### Explicit v1 exclusions

- denial of service and guaranteed service availability;
- compromise of the legitimate client during enrolment or authentication;
- coercion, shoulder surfing, phishing, account recovery, and device theft outside protocol state;
- model supply-chain compromise or a malicious local generator/extractor;
- claims about memorability, usability, natural credential selection, or human behaviour;
- attacks on real third-party systems or identification of public-dataset contributors.

Exclusion means “not evaluated,” not “safe.” Service unavailability, privacy-service failure, key loss, and recovery must still be described as deployment limitations in P9–P12.

## 2. Formal objects and notation

### Versions and spaces

Let the public scheme version be

```text
v = (v_G, v_E, v_C, v_M, v_P)
```

for generator, extractor, canonicaliser, matcher, and protocol versions. A text-only path uses `v_G = none`. Version mismatch is rejected unless an explicit, tested migration rule exists.

- `C` is the conceptual-intent space used only as controlled experimental ground truth; the system never observes intent directly.
- `X_v` is the local observation space for version `v` (for example, generated images or text-only inputs).
- `S_v` is the canonical semantic credential space.
- `F_v : X_v -> S_v union {failure}` is the deterministic, versioned local extractor/canonicaliser after fixing model decoding and preprocessing randomness.
- `Gen_v(c; rho)` is the controlled generation/reproduction process for concept `c` and randomness `rho`. It models technical trials, not human recall.
- `s = F_v(Gen_v(c; rho))` is one enrolled credential, when neither stage fails.

For a structured representation, `s` may be a set or weighted set of typed atoms. For an embedding baseline, `s` is a versioned vector. These are alternative representations, not assumed equivalents.

### Similarity, decision, and acceptance regions

Let `sim_v : S_v x S_v -> R` be a public plaintext reference similarity, with larger values meaning closer credentials, and let `tau` be a public or explicitly protected threshold. The reference decision is

```text
Match_{v,tau}(s, s') = 1[sim_v(s, s') >= tau].
```

Distance-based matchers use the equivalent convention `d_v(s,s') <= tau_d`. A private protocol must be checked against this reference functionality, including equality at the boundary.

The credential-space acceptance region is

```text
A_{v,tau}(s) = {s' in S_v : Match_{v,tau}(s,s') = 1}.
```

The observation-space preimage is

```text
B_{v,tau}(s) = {x in X_v : F_v(x) != failure and F_v(x) in A_{v,tau}(s)}.
```

For a concept `c'`, its technical acceptance probability against enrolled `s` is

```text
alpha_v(c' -> s) = Pr_rho[Gen_v(c';rho) succeeds and
                           F_v(Gen_v(c';rho)) in A_{v,tau}(s)].
```

This distinction prevents the paper from treating a single semantic set, prompt, or image as the whole secret. An attacker wins with any accepted credential or observation.

### Reproduction, correctness, and technical stability

For a declared same-concept trial distribution `D_same` and negative distribution `D_neg`:

```text
Completeness_v(tau) = Pr[Match(s,s') = 1 | (s,s') sampled from D_same]
Soundness_{v,D_neg}(tau) = Pr[Match(s,s') = 0 | (s,s') sampled from D_neg].
```

The corresponding empirical error rates are `FRR = 1 - Completeness` and `FAR = 1 - Soundness`. Soundness is always distribution-qualified; it is not a universal guarantee against targeted attackers.

**Technical stability** is the distribution of extraction success, representation agreement, and similarity scores across controlled same-concept variations in seed, paraphrase, style, and model version. It is not memorability, recall, or usability. Report strata and uncertainty rather than collapsing stability to an unsupported adjective.

A protocol has **functional correctness** for an input domain if its output equals `Match_{v,tau}(s,s')`, except with a stated failure probability, for valid inputs and explicitly defined duplicate, malformed, and version-mismatch behaviour.

### Attacker distributions and budgets

An attacker strategy `Q` maps public information, side information `K`, prior observations, and its internal randomness to an adaptive ordered sequence of guesses `g_1,...,g_q`. A guess may be a concept, prompt, image, or credential according to the attack interface. Every result must name the interface.

For online budget `q`, success is

```text
Succ_online(Q,q) = Pr[there exists i <= q such that the target accepts g_i].
```

Report success-versus-budget curves, per-account and aggregate outcomes, duplicate handling, rate-limit assumptions, and whether feedback is only `Accept/Reject` or richer. Expected guesses and median rank may supplement, but not replace, budgeted success.

P6-R fixes four attacker-knowledge conditions for later budgeted evaluation:

- **K0 — generic/random:** public system knowledge, but no target-specific or population-ordering advantage;
- **K1 — population/distribution:** source, frequency, or population knowledge that improves ordering without target-specific facts;
- **K2 — partial target:** some target-specific atoms, attributes, context, or equivalent side information;
- **K3 — strong near-secret:** enough target-specific knowledge to construct candidates already close to the enrolled credential.

P6 random negatives are only a limited K0-like diagnostic, and its frozen one-atom near negatives are a K3-like conditional stress test. Neither estimates `P(success within B attempts | K_i)`. P8 must report success@1, success@5, success@10, success@B, and guesses-to-success for each supported level, keeping online and offline views separate. A K3 FAR of zero is not required; the question is whether the accepted region creates material budgeted advantage under the named knowledge condition.

Rate limits are explicit online assumptions, not substitutes for a nontrivial credential space. All algorithms, models, schemas, canonicalisation rules, thresholds, and protocol code remain public. If an optional `PS` or `IKS` improves an outcome, the benefit must be traced to key possession, protocol or rate-limit enforcement, and a stated non-collusion/isolation assumption—not to model secrecy or to the existence of a third party by itself.

For an offline view `V`, an **offline validation procedure** is an algorithm that uses `V` to test or rank candidate guesses without interacting with an uncompromised rate-limiting service. Measure candidate throughput/cost, success by budget, and ranking or distinguishing advantage relative to the same attacker without `V`. “No offline oracle” may be claimed only if the construction's proof and implementation support that statement for the exact compromise state.

### Leakage classes

Protocol outputs are classified, from narrower to richer:

1. `L0`: public configuration and coarse message lengths/timing buckets;
2. `L1`: one final `Accept/Reject` bit for an authorised, rate-limited session;
3. `L2`: threshold/intersection predicate(s), failure reason, or repeated intermediate decisions;
4. `L3`: intersection cardinality, similarity score, matching atom positions, or other graded feedback;
5. `L4`: deterministic/linkable protected values, helper data, embeddings, or plaintext semantic content.

This is a descriptive taxonomy, not a theorem: timing and message sizes can themselves be sensitive. Every protocol candidate must state its ideal output and measured/structural deviations. An exact score or cardinality is never described as “Accept/Reject-only.”

## 3. Protected assets and security/privacy goals

| ID | Goal and success condition | Required evidence before using the claim |
|---|---|---|
| G1 | **Online guessing resistance:** under named rate limits and attacker distribution, budgeted acceptance success remains below a preregistered bound. | A1/A4/A5/A8 experiments; bound and operational assumptions. |
| G2 | **Database-only offline-validation resistance:** possession of database records alone does not materially improve candidate validation/ranking over the prior-only attacker, under a named construction. | Formal argument or reduction plus E9 implementation attack and throughput; A2 view precisely enumerated. |
| G3 | **Compromise containment:** compromise of fewer than the declared services/shares/isolation boundary does not expose plaintext semantics or create the excluded offline oracle; total compromise outcome is explicit. | Construction-specific proof/analysis and A3 failure/collusion tests. |
| G4 | **Representation confidentiality/inversion resistance:** an attacker cannot recover declared semantic attributes or an accepted equivalent above baselines from its named view. | A6 task, dataset, baseline, metric, uncertainty, and attack strength; no absolute “non-invertible” wording from a failed attack alone. |
| G5 | **Transcript privacy:** transcripts reveal no more than the declared leakage class under the named passive or active model. | Simulation/reduction where applicable; message audit and active/selective-failure tests. |
| G6 | **Cross-service unlinkability:** given two service-scoped records/transcripts, the attacker cannot distinguish same-secret from different-secret pairs materially above the preregistered baseline. | A7 game, balanced/challenging negative pairs, ROC/AUC or advantage with uncertainty, and domain-separation analysis. |
| G7 | **Decision minimisation:** the normal authentication path exposes no more than declared metadata and `L1`, unless richer output is justified and measured. | Interface/message trace audit; tests proving scores/cardinalities/failure detail are not exposed. |
| G8 | **Replay/session integrity:** a captured successful transcript cannot authenticate in a fresh session or different account/service/version. | Protocol binding specification, nonce/challenge tests, replay and cross-context tests; active-security analysis. |
| G9 | **Semantic-collision resistance (empirical):** within a named attack budget, A8 does not find substantially different concepts accepted above a preregistered rate. | Targeted/adversarial search with semantic-difference rules fixed before the full test. This is not a cryptographic collision-resistance claim. |

Availability is not a privacy guarantee in v1. If `PS`, a threshold share, or `IKS` is unavailable, authentication may fail closed; fallback to a weaker path must never occur silently.

## 4. Architecture hypotheses and compromise matrix

No architecture is selected in P2. The following labels are hypotheses for D6/D7 comparison.

- **H1 — Single service:** `AS` stores the record and holds all online server secret material.
- **H2 — Separate privacy service:** `AS` and `PS` are independently administered and assumed not to collude for the conditional goal.
- **H3 — Threshold services:** key capability is split across `n` services with threshold `t`; fewer than `t` shares are insufficient under the selected primitive.
- **H4 — Isolated key:** `AS` calls `IKS`, which protects a key and enforces an explicitly defined policy/rate limit.

| Compromise event | H1 single service | H2 separate service | H3 threshold | H4 isolated key |
|---|---|---|---|---|
| Database snapshot only | Candidate may protect only if records are not efficient verifiers; must be attacked. | Same, with `PS` state absent. | Same, with shares absent. | Same, with isolated key absent. |
| `AS` process/state but no independent component | All `AS`-held keys are lost; no stronger containment is presumed. | Conditional protection may remain if `PS` is uncompromised and protocol resists malicious `AS`. | Conditional protection may remain if fewer than `t` shares are obtained. | Conditional protection may remain only if `IKS` resists extraction and gates adversarial queries. |
| One auxiliary service/share | Not applicable. | If `PS` alone is compromised, protection depends on what it stores/sees and protocol security against malicious `PS`. | Fewer than `t` shares should not reconstruct the key; metadata/transcript leakage remains candidate-specific. | `IKS` compromise loses the isolated key; database/record may still be needed, depending on construction. |
| Required collusion / threshold reached | Equivalent to full server/key compromise. | `AS + PS` collusion is treated as total service compromise. | At least `t` relevant shares plus required records is treated as total key capability. | `AS + IKS`, or extraction plus required records, is treated as total service/key compromise. |
| Total service/key compromise | Semantic guessing may be performed offline whenever the resulting state validates candidates; no blanket protection claim. Low/nonuniform semantic entropy remains a limit. | Same after collusion. | Same after threshold compromise. | Same after isolation failure. |
| Component unavailable | Authentication unavailable. | May be unavailable; no silent H1 fallback. | Available only if enough healthy shares remain. | May be unavailable; no export/fallback of the key. |

Passwords and semantic credentials cannot be promised safe after an attacker obtains every component needed to evaluate the verifier. P9–P11 must state whether a construction offers only database-snapshot protection, conditional compromise containment, or another precisely justified property.

## 5. A1–A8 architecture walkthrough

| Threat | H1 | H2 | H3 | H4 | Mandatory evaluation or proof |
|---|---|---|---|---|---|
| A1 online guesser | Rate-limited `L1` oracle at `AS`. | Same externally; `PS` must not become a bypass oracle. | Same; shares must bind authorised sessions. | Same; `IKS` policy must not add a bypass oracle. | Success by budget with and without stated rate limits; replay/session tests. |
| A2 database attacker | Test whether `r` is an offline verifier or inversion/linking surface. | Test `AS` and `PS` snapshots separately. | Test records and every sub-threshold share set in scope. | Test record without `IKS` key; do not equate isolation with proof. | E9/E10/E11 plus construction analysis. |
| A3 server/key compromise | Full H1 state is total compromise; quantify residual attack cost, do not claim prevention by default. | Test `AS`-only, `PS`-only, and collusion; active deviations matter. | Test each sub-threshold compromise and threshold reached. | Test `AS`-only, key-query abuse, `IKS` extraction, and combined compromise. | Data/key inventory, malicious behaviour analysis, collusion/failure tests. |
| A4 AI-assisted | Improves guess ordering against online or stolen-view oracle. | Same; architecture changes validation access, not prior quality. | Same. | Same. | Fixed random/frequency/LLM/generator-assisted strategies, success by budget. |
| A5 partial information | Conditions `Q` on `k` known atoms/context. | Same. | Same. | Same. | Stratified `k`, atom-selection rule, and uncertainty. |
| A6 inversion | Attack record, helper data, transcripts, embeddings, or scores actually exposed by H1. | Attack each party's separate and colluding views. | Attack sub-threshold and threshold views. | Attack record, permitted query outputs, then extracted-key view. | Attribute/concept recovery versus prior and representation baselines. |
| A7 linking | Compare records/transcripts across service domains; deterministic tokens are suspect. | Include either party and colluding views. | Include share/service identifiers and combined views. | Include domain binding and isolated service outputs. | Same-secret/different-service game with hard negatives and domain separation. |
| A8 adversarial collision | Crafted client inputs can target local extractor/matcher; protocol privacy does not remove semantic collisions. | Same. | Same. | Same. | Budgeted targeted search, reference-function agreement, malformed-input checks. |

The canonical machine-readable mapping is `docs/threat_claim_matrix.csv`. Later phases may add versioned rows but must not silently change v1 meanings.

## 6. Behaviour models and observable views

### Honest-but-curious service

Follows the protocol but retains and analyses everything legitimately visible: stored state, messages, lengths, timing available to the implementation, outcomes, and authorised query history. A claim in this model does not imply protection against malicious deviations.

### Malicious service

May choose malformed messages, keys, inputs, challenges, service identifiers, or abort behaviour; replay/interleave sessions; and mount selective-failure or chosen-input attacks. It cannot break the assumed secure transport to impersonate another uncompromised endpoint or compromise the trusted client unless that is explicitly added. P9 must identify whether each candidate offers active security, detection, or only honest-but-curious privacy.

### Malicious authenticating client

May submit arbitrary syntactically permitted prompts, images, semantic credentials, and protocol messages to its own sessions, adapt based on observable outputs, and use automation/AI. It does not receive the victim's trusted-client state. This behaviour covers A1, A4, A5, and A8.

### Network observer and replay attacker

Sees transport metadata and any deliberately public protocol fields; ciphertext contents are protected by the channel assumption. It may replay captured application messages. G8 requires fresh, context-bound sessions even when transport-level replay protection exists.

## 7. Research questions and provisional hypotheses

The RQ wording in `AGENT.md` remains compatible with verified P1 evidence and is not amended. P2 narrows how it is answered:

- **RQ1/RQ2:** technical distributions under controlled concepts only; never human reproducibility or usability.
- **RQ3:** success is budgeted acceptance-region success under named `Q`, not exact-prompt recovery.
- **RQ4:** every result is indexed by architecture, compromise row, behaviour model, and leakage class.
- **RQ5:** includes trust/deployment burden and separate setup/offline/online costs, not latency alone.
- **RQ6:** the image path survives Gate B only through measured technical/privacy benefit over paired text-only processing.

Provisional, falsifiable hypotheses—not results—are:

- **H-R:** at some preregistered operating range, same-concept technical completeness and targeted-negative soundness may be jointly useful.
- **H-A:** acceptance-region mass under realistic and AI-assisted `Q` may be materially larger than exact-secret probability and must determine positioning.
- **H-P:** at least one private-matching architecture may reduce database-only validation, inversion, or cross-service linkage relative to plaintext/hash-bound baselines under a realistic partial-compromise boundary.
- **H-I:** the image stage may or may not add measurable technical value; no direction is presumed.

Gate failures can reject all four without violating the research plan.

## 8. Ethical and inference boundaries

- No participant recruitment, interaction, observation, or claim about human secret choice is authorised.
- Controlled researcher-generated concepts establish technical ground truth only.
- Public prompts may estimate properties of that corpus and construct attacker orderings; they are not authentication credentials and do not represent authentication-secret selection without evidence.
- Retain only fields required by the stated analysis. Do not deanonymise, link contributors, contact users, or publish unnecessary identifiers or sensitive examples.
- Record dataset licence, provenance, access date, filtering, deduplication, harmful/NSFW handling, and exclusions before acquisition.
- Run attacks only against synthetic/local research accounts and authorised components. Do not probe third-party authentication services.
- AI attack generation must use frozen prompts/configurations, record model/version/provenance, filter harmful outputs where needed, and preserve negative results.

## 9. Claim discipline and phase handoff

The unqualified words “secure,” “privacy-preserving,” “non-invertible,” “unlinkable,” “offline-attack resistant,” and “Accept/Reject-only” are forbidden in result claims. Replace each with a construction- and model-specific statement tied to G1–G9 and an evidence row.

P3–P8 may rely on v1 definitions for pilot methodology. P9 must instantiate all data, messages, keys, leakage, service behaviour, and compromise outcomes for each protocol candidate. P10/P11 must test the reference-function boundary and the attacks in the machine-readable matrix. Any semantic change to v1 requires a new version and a decision-log entry; editorial clarification may retain v1 with a dated changelog.

No `AGENT.md` amendment is proposed in P2 because its RQs, A1–A8, no-human-study rule, and architecture non-selection are consistent with this formalisation.
