# AGENT.md — Semantic Secrets / PETS 2027 Research Project

## 1. Purpose of this file

This file is the persistent scientific and engineering guide for any AI coding/research agent working on this repository, especially Codex.

The project goal is to produce a **scientifically defensible, reproducible research publication for PoPETs/PETS 2027** together with a working prototype and evaluation artifact.

This file is **not a one-time task list**. It defines the project's research contract: scope, research questions, threat model, architecture, methodological rules, expected evidence, non-goals, and standards for paper/artifact preparation. A separate step-by-step `PLAN.md` should be created from this file and updated as the project progresses.

An agent must read this file before proposing or implementing work that affects the research design, prototype, experiments, paper, or artifact.

---

## 2. Working title and core idea

**Working title:**

> **Semantic Secrets: Privacy-Preserving Authentication from AI-Generated Images**

The title is provisional and may change after the contribution is validated.

### Core idea

A user defines a visual concept. A locally deployed text-to-image model generates an image representing that concept. A local semantic extractor converts the generated image into a canonical semantic credential containing objects, attributes, counts, actions, and/or relations.

At a later login, the user recreates the concept. A new image is generated independently, its semantics are extracted, and a privacy-preserving matching protocol determines whether the new semantic credential is sufficiently similar to the enrolled credential.

The server should learn as little as possible about the underlying secret.

Conceptually:

```text
ENROLMENT

user concept
    ↓
local image generation
    ↓
local semantic extraction
    ↓
canonical semantic credential S
    ↓
privacy-preserving registration
    ↓
protected server record R_u
```

```text
AUTHENTICATION

recreated concept
    ↓
local image generation
    ↓
local semantic extraction
    ↓
canonical semantic credential S'
    ↓
private approximate/threshold matching against R_u
    ↓
accept / reject
```

The research is **not** simply “AI-generated graphical passwords.” The scientific focus is privacy-preserving authentication of **noisy semantic secrets**.

---

## 3. Main research question

The central research question is:

> **Can noisy semantic concepts reproduced through independently generated images be used for authentication while preventing the authentication service, a database attacker, or an AI-assisted guesser from learning or efficiently validating the underlying semantic secret?**

All major engineering and experimental tasks must contribute evidence toward this question.

---

## 4. Intended PoPETs/PETS 2027 positioning

This project is intended for PoPETs/PETS 2027, so privacy must be a **core contribution**, not a superficial application label.

The project should be framed as a privacy-enhancing authentication system with a real application: protecting user-chosen semantic credentials during storage and approximate verification.

The final first page of the PoPETs manuscript must clearly explain the real-world privacy relevance.

The intended contribution is the combination of:

1. formalising semantic visual credentials as noisy, user-chosen knowledge secrets;
2. modelling the security cost of the credential's acceptance region;
3. designing a privacy-preserving approximate/threshold matching protocol;
4. studying database/server compromise, offline verification, representation leakage, and cross-service linkability;
5. evaluating AI-assisted semantic guessing using realistic prompt distributions; and
6. implementing and reproducibly evaluating an end-to-end system.

Do **not** frame novelty as “the first semantic image password.” Closely related visual-semantic authentication work already exists, including a 2026 Image-Agnostic Visual Semantic Authentication (VSA) framework using Grounding DINO + CLIP, semantic policies, approximate matching, and hash-based secret binding.

The project must differentiate itself through the **privacy-preserving protocol, threat model, attack analysis, acceptance-region model, and generative re-creation pipeline**.

---

## 5. Absolute scope constraint: no human-subject study

This project cannot include participant recruitment or a user study.

Therefore the paper MUST NOT claim to have demonstrated:

- human memorability;
- usability;
- user preference;
- long-term recall;
- human prompt reproduction behaviour;
- human authentication speed;
- accessibility benefits;
- that users naturally select high-entropy visual secrets; or
- superiority to passwords/passkeys/password managers from a human-factors perspective.

The system may be described as *intended* to reduce exact-string reproduction requirements, but any claimed human benefit must be explicitly marked as unvalidated.

Use the term **technical reproducibility** or **representation stability** for machine-evaluated experiments. Never substitute those metrics for human memorability.

A future human study may be proposed in the paper's future-work section, subject to ethics review.

---

## 6. Key security principle

### Visual complexity is not secret entropy

Do not claim that a detailed AI-generated image automatically creates a high-entropy credential.

If the persistent user secret is a concept such as:

```text
cat wearing a hat
```

then the attacker targets that concept or an accepted semantic neighbour, not all possible image pixels.

Let the enrolled semantic credential be `S`, semantic distance be `d`, and threshold be `tau`.

```text
A_tau(S) = { S' : d(S, S') <= tau }
```

The attacker wins by generating **any** element in this acceptance region.

The project's security analysis should therefore estimate or bound the probability mass of the acceptance region under realistic attacker distributions.

This creates an explicit trade-off:

```text
larger tolerance
    → potentially lower false rejection
    → larger accepted semantic region
    → potentially easier guessing
```

This trade-off is a central research contribution and must be measured.

---

## 7. Research questions

Unless later evidence justifies a revision, the project should answer the following RQs.

### RQ1 — Semantic stability

How consistently can independently generated images representing the same concept be mapped to equivalent authentication representations across:

- random seeds;
- prompt paraphrases;
- image styles;
- generator versions;
- extractor versions; and
- controlled semantic perturbations?

### RQ2 — Authentication separability

How accurately can the system distinguish intended same-concept trials from:

- random impostor concepts;
- semantically similar impostors; and
- deliberately targeted semantic neighbours?

Measure FAR, FRR, EER, ROC/AUC, and threshold effects.

### RQ3 — AI-assisted guessability

How susceptible are semantic credentials to:

- frequency-based dictionaries;
- public prompt distributions;
- LLM-generated guesses;
- VLM/generator-assisted semantic variations; and
- partial-information attacks?

### RQ4 — Template and protocol privacy

What information can an attacker learn or validate from:

- a compromised database;
- a stored embedding;
- helper data;
- protected tokens;
- protocol transcripts; or
- server-side keys?

Can the proposed protocol reduce offline verification, representation inversion, and cross-service linkability?

### RQ5 — Practicality

What latency, bandwidth, storage, CPU/GPU, and memory overhead is introduced by private semantic matching relative to plaintext baselines?

### RQ6 — Is the generated image technically necessary?

Does this path:

```text
prompt → image → semantics
```

provide a measurable technical advantage over:

```text
prompt → semantics
```

under this paper's non-human evaluation?

If it does not, the scientific design must acknowledge this and may need to simplify or reposition the system.

---

## 8. System actors

### 8.1 Client

Trusted for local generation/extraction in the target privacy design.

Responsibilities:

- accept the user's concept/prompt;
- generate image locally;
- extract semantic representation locally;
- canonicalise the representation;
- execute client-side cryptographic protocol steps; and
- avoid transmitting plaintext prompt/image/semantics unless a specific experiment intentionally evaluates that baseline.

### 8.2 Authentication server

Responsibilities:

- account/session management;
- store protected authentication records;
- execute server-side matching protocol;
- enforce rate limits and replay protection; and
- return authentication decision.

### 8.3 Optional privacy/OPRF service

A separate service may be introduced for a two-server or threshold construction.

Potential use:

- OPRF/threshold OPRF;
- distributed tokenisation;
- PSI helper role; or
- protection against a single compromised database/authentication server becoming an offline semantic dictionary oracle.

If a non-collusion assumption is used, the paper and code documentation must state it explicitly.

---

## 9. Data that should ideally remain client-side

The strongest architecture should not send these plaintext values to the authentication server:

```text
natural-language secret prompt
original/generated image
plaintext semantic atoms
raw semantic embedding
exact similarity score (unless needed by the selected protocol)
```

The target server-visible result should be as close as practical to:

```text
account/protocol metadata
accept or reject
```

A weaker construction may reveal more. If so, document exactly what is leaked and why.

---

## 10. Semantic credential design

### 10.1 Primary representation: structured semantic credential

Preferred representation:

```text
objects
attributes
counts
actions
spatial relations
scene concepts
```

Example:

```json
{
  "objects": ["cat", "helmet", "bicycle", "moon"],
  "attributes": [
    ["cat", "black"],
    ["helmet", "yellow"]
  ],
  "relations": [
    ["cat", "riding", "bicycle"]
  ],
  "scene": ["lunar"]
}
```

Then canonicalise to stable atoms such as:

```text
cat
black(cat)
yellow(helmet)
bicycle
moon
riding(cat,bicycle)
lunar-scene
```

### 10.2 Canonicalisation requirements

The canonicaliser must be deterministic and versioned.

It should define rules for:

- Unicode/case normalisation;
- singular/plural handling;
- synonyms;
- object aliases;
- colour/attribute vocabulary;
- relation direction;
- count representation;
- low-confidence filtering;
- duplicate atoms;
- ordering; and
- unsupported model output.

Do not silently change canonicalisation between experiments. Any change increments a scheme version.

### 10.3 Weighted semantic atoms

Evaluate whether different atoms should receive different weights based on measured:

- corpus frequency;
- stability;
- discriminative value; and
- attackability.

Do not invent weights based only on intuition.

### 10.4 Embedding baseline

Keep an embedding path such as CLIP/SigLIP-style cosine similarity as a baseline.

Raw embeddings are **not automatically private**. Treat inversion and linkability as attacks to test.

### 10.5 Text-only baseline

Implement direct prompt semantic extraction as a mandatory baseline to answer RQ6.

---

## 11. AI model strategy

Model choice is not the contribution. Models are experimental dependencies.

### 11.1 Image generator

Initial candidate:

- locally deployable Stable Diffusion XL (SDXL), or another reproducible open-weight model selected after environment validation.

Record exact:

- model ID;
- model hash/version;
- library versions;
- scheduler/sampler;
- steps;
- guidance;
- resolution;
- random seed; and
- hardware.

The code must support swapping generator backends.

### 11.2 Structured semantic extraction

Compare at least these families if feasible:

1. **Open-vocabulary detector + VLM encoder**
   - Grounding-DINO-style detector;
   - CLIP/SigLIP-style feature/attribute support;
   - deterministic relation extraction from boxes where possible.

2. **Constrained multimodal VLM**
   - locally deployable VLM;
   - fixed prompt;
   - fixed JSON schema;
   - deterministic/tightly controlled decoding;
   - strict schema validation.

3. **Dense embedding baseline**
   - CLIP/SigLIP-style embedding;
   - cosine/dot-product similarity.

The final primary extractor must be selected through evidence, not preference.

### 11.3 Model drift

The evaluation must include cross-version tests.

Example matrix:

```text
Enroll G1/E1 → Auth G1/E1
Enroll G1/E1 → Auth G2/E1
Enroll G1/E1 → Auth G1/E2
Enroll G1/E1 → Auth G2/E2
```

Report both reliability and security changes.

---

## 12. Matching functions

Candidate plaintext functions include:

### Set cardinality threshold

```text
|S ∩ S'| >= t
```

### Jaccard similarity

```text
J(S,S') = |S ∩ S'| / |S ∪ S'|
```

### Weighted overlap

```text
W(S,S') = matching enrolled semantic weight / total enrolled semantic weight
```

### Embedding baseline

```text
cos(z,z') >= tau
```

The final matching function should be chosen jointly with the privacy protocol. Do not choose a metric that cannot be evaluated privately within realistic overhead unless it is only a baseline.

---

## 13. Cryptographic/protocol research directions

### 13.1 Important prohibition

Do **not** implement or describe this as the secure solution:

```text
encrypt semantics
→ encrypt new semantics
→ compare ciphertexts directly
```

Ordinary semantically secure encryption does not preserve approximate similarity.

A dedicated private-comparison protocol is required.

### 13.2 Primary candidate: OPRF/PSI-style private semantic set matching

Primary direction:

```text
canonical semantic atoms
→ privacy-preserving tokenisation / set protocol
→ private intersection/threshold result
```

Candidate primitives:

- OPRF;
- threshold OPRF;
- PSI;
- PSI-cardinality;
- private threshold set intersection;
- secure two-party computation.

Security question:

> Does compromise of the stored record permit efficient offline semantic dictionary testing?

A single server that holds both protected records and the complete OPRF key may still enable an offline attack after full compromise.

Investigate stronger options:

- separate key service;
- two non-colluding servers;
- threshold OPRF;
- hardware-isolated key as an explicitly weaker operational assumption.

Do not claim “no offline oracle” unless the exact threat model and construction justify it.

### 13.3 Alternative: fuzzy extractor / secure sketch + PAKE

Research baseline/candidate:

```text
noisy semantic credential
→ fuzzy recovery
→ stable secret K
→ PAKE (e.g. OPAQUE)
```

Evaluate:

- whether semantic source min-entropy is adequate;
- helper-data leakage;
- offline dictionary capability;
- recovery reliability; and
- protocol overhead.

OPAQUE is relevant because it hides the password from the server during registration and login, but it does **not** automatically solve fuzzy semantic matching or low secret entropy.

### 13.4 Alternative: private encrypted embedding similarity

For embedding baselines, evaluate:

- homomorphic encryption;
- secure computation; or
- another validated private vector-comparison construction.

This baseline may protect similarity computation but does not by itself solve semantic guessability.

### 13.5 Protocol-selection rule

Do not lock the paper to a primitive before benchmark/security evidence exists.

The `PLAN.md` should contain an explicit protocol-selection phase with measurable criteria:

- privacy leakage;
- compromise resistance;
- offline attack cost;
- correctness;
- communication cost;
- latency;
- implementation complexity; and
- suitability for a 12-page PoPETs main-body story.

---

## 14. Threat model

Experiments and claims must distinguish these adversaries.

### A1 — Online guesser

Can submit login guesses and observe accept/reject.

Model realistic rate limits separately from unbounded theoretical attempts.

### A2 — Database attacker

Obtains stored authentication records.

Question: can the attacker validate guesses offline or infer semantic content?

### A3 — Server/key compromise attacker

Obtains authentication-server state and some cryptographic keys.

Explicitly define what remains protected for each protocol variant.

### A4 — AI-assisted attacker

Can use:

- LLMs;
- VLMs;
- text-to-image generators;
- prompt corpora;
- semantic frequency models.

### A5 — Partial-information attacker

Knows `k` semantic atoms or contextual information about the target.

Measure attack success as `k` increases.

### A6 — Representation inversion attacker

Attempts to recover:

- objects;
- attributes;
- relations;
- approximate prompt/concept;
- nearest semantic neighbour.

### A7 — Cross-service linking attacker

Attempts to determine whether two protected records correspond to the same reused semantic secret.

### A8 — Adversarial semantic collision attacker

Searches for an input that the extractor/matcher accepts despite a substantially different intended concept.

---

## 15. Datasets and experimental inputs

### 15.1 Controlled researcher-generated concept set

Create a controlled semantic corpus with explicit ground-truth concept structure.

Vary:

- number of objects;
- common vs rare objects;
- colours/attributes;
- counts;
- spatial relations;
- actions;
- concept complexity;
- semantic near-neighbours.

Important limitation:

> This corpus measures technical behaviour, not real user secret choice.

### 15.2 Public prompt corpus for attacker modelling

DiffusionDB is a useful candidate because it contains approximately 14 million Stable Diffusion images and 1.8 million unique prompts specified by real users.

Permitted intended use:

- empirical prompt/semantic frequency;
- dictionary construction;
- semantic co-occurrence estimates;
- AI-assisted attacker ordering.

Do **not** claim DiffusionDB represents authentication-password selection. Its prompts were not collected as credentials.

### 15.3 Dataset ethics

- obey licences and terms;
- do not deanonymise contributors;
- do not expose unnecessary identifiers;
- document filters;
- document harmful/NSFW handling;
- use public data only for the stated research purpose.

---

## 16. Required experiment families

### E1 — Same-concept seed stability

Same canonical concept, different generator seeds.

### E2 — Prompt paraphrase stability

Same intended concept, controlled paraphrases.

### E3 — Style variation

Same semantics, different style descriptors.

### E4 — Semantic perturbation

Remove/change one object, attribute, count, action, or relation at a time.

### E5 — Random impostor trials

Compare unrelated concepts.

### E6 — Near-neighbour impostor trials

Compare concepts sharing several atoms but differing in one important component.

### E7 — Threshold sweep

Measure FAR/FRR/EER/ROC/AUC over all relevant thresholds.

### E8 — Acceptance-region security

Estimate accepted-neighbour probability under empirical and AI-assisted attacker distributions.

### E9 — Offline dictionary attack

For each stored-record design, test whether a database attacker can validate candidate semantic guesses and at what cost.

### E10 — Representation inversion

Attempt to recover semantic atoms/concepts from stored representations.

### E11 — Cross-service linkability

Measure whether same-secret protected records can be linked across service domains.

### E12 — Partial-information attack

Reveal increasing numbers of atoms to the attacker.

### E13 — AI-assisted guessing

Compare random, frequency-ordered, LLM-assisted, and generator-assisted strategies.

### E14 — Model drift

Cross generator/extractor versions.

### E15 — Protocol performance

Measure client/server computation, latency, memory, bandwidth, and storage.

### E16 — Text-only baseline

Remove the image-generation stage and repeat applicable stability/security tests.

---

## 17. Required metrics

### Authentication/reliability

- FAR;
- FRR;
- EER;
- ROC/AUC;
- representation stability;
- threshold curves.

### Guessing security

- success@10;
- success@100;
- success@1,000;
- larger feasible budgets;
- guesses-to-success distribution;
- accounts compromised under a fixed dictionary;
- effect of partial knowledge;
- acceptance-region probability estimate.

### Privacy

- offline guess-validation capability;
- semantic recovery accuracy;
- inversion accuracy;
- cross-service linkability AUC/accuracy;
- protocol leakage classification;
- compromise sensitivity.

### Performance

- generation latency;
- extraction latency;
- crypto latency;
- end-to-end latency;
- bandwidth;
- stored bytes/account;
- CPU/GPU usage;
- peak memory;
- scalability vs semantic set size.

---

## 18. Mandatory baselines

Unless technically impossible, include:

1. **Plain embedding similarity** — no privacy protection.
2. **Plain structured semantic matching** — no privacy protection.
3. **Closest prior visual-semantic authentication approach** — reproduce documented policy where feasible.
4. **Fuzzy recovery/fuzzy extractor baseline** — if representation can support it.
5. **Main privacy-preserving protocol** — selected through evidence.
6. **Text-only semantic authentication baseline**.

If a baseline cannot be implemented, document the exact reason in the paper/appendix; do not silently omit it.

---

## 19. Prototype requirements

The prototype should be modular and usable independently of the research web UI.

Recommended logical structure:

```text
project-root/
├── AGENT.md
├── PLAN.md
├── README.md
├── paper/
│   ├── draft.tex
│   ├── references.bib
│   └── figures/
├── prototype/
│   ├── client/
│   ├── server/
│   ├── privacy_service/       # if required by selected protocol
│   ├── semantic/
│   ├── generation/
│   └── crypto/
├── experiments/
│   ├── configs/
│   ├── datasets/
│   ├── runners/
│   ├── attacks/
│   └── analysis/
├── tests/
├── artifacts/
│   ├── scripts/
│   └── README.md
└── results/                    # generated; large data should not be blindly committed
```

This is a recommendation, not an instruction to reorganise an existing repository destructively. Inspect the current repository first and adapt incrementally.

### Engineering rule

The scientific pipeline must be runnable without clicking through the web UI.

Example future interface:

```bash
python -m experiments.run --config experiments/configs/e1_seed_stability.yaml
python -m experiments.run --config experiments/configs/e9_offline_attack.yaml
python -m experiments.analyze --run <run-id>
```

Exact commands should be defined in the later `PLAN.md` and implementation.

---

## 20. Reproducibility requirements

Every experiment run should record, at minimum:

```text
run ID
git commit
UTC timestamp
experiment config hash
random seeds
model IDs and hashes
model inference parameters
Python version
dependency lock hash
OS/container information
CPU/GPU information
dataset version/split
protocol configuration
thresholds
raw metrics
```

Do not overwrite experimental results in place.

Prefer immutable run directories and machine-readable metadata.

Any figure/table in the paper should be generated by a script from saved result data.

---

## 21. Testing requirements

### Unit tests

Test:

- semantic schema validation;
- canonicalisation;
- synonym rules;
- relation normalisation;
- matching functions;
- protocol serialization;
- crypto primitive wrappers;
- error handling;
- deterministic configuration loading.

### Integration tests

Test:

- enrolment end to end;
- authentication end to end;
- incorrect credential rejection;
- server restart with persisted record;
- model-version mismatch handling;
- privacy-service unavailability;
- malformed protocol messages;
- replay/session handling.

### Security regression tests

Once an attack/failure is discovered, add a regression test where appropriate.

### Experiment smoke tests

Each expensive experiment needs a tiny deterministic smoke-test configuration for CI/local validation.

---

## 22. Scientific integrity rules for agents

These rules are mandatory.

### 22.1 Never fabricate experimental results

Do not write numerical results into the paper unless they come from a recorded experiment or a properly cited source.

Use placeholders such as:

```text
TODO_RESULT
```

until evidence exists.

### 22.2 Never invent references

All references must be verified against a primary source, DOI/RFC, publisher page, or trusted bibliographic index.

Do not generate plausible-looking BibTeX and treat it as verified.

PoPETs 2027 explicitly holds authors responsible for AI-generated citation errors.

### 22.3 Separate hypothesis from result

Before experiment:

```text
Hypothesis: structured semantics may reduce model-specific embedding drift.
```

After evidence:

```text
Observed result: ...
```

Never convert a hypothesis into a factual claim without evidence.

### 22.4 Preserve negative results

Do not discard results merely because they weaken the proposed system.

If the system is too guessable, unstable, leaky, or slow, that is scientifically relevant.

### 22.5 Avoid “security by adjective”

Do not use words such as:

```text
secure
privacy-preserving
high-entropy
robust
unlinkable
verifier-free
```

as unqualified claims unless the property is formally defined and supported by proof or experiment under a stated threat model.

---

## 23. Paper-writing rules

### 23.1 Page budget

PoPETs 2027 submissions allow at most **12 main-body pages** before revision, excluding the three mandatory template sections, acknowledgements, bibliography, and clearly marked appendices.

Write compactly from the start.

### 23.2 Mandatory PoPETs 2027 requirements

Before submission:

- use the official PoPETs 2027 LaTeX template;
- make real-world privacy relevance explicit on page 1;
- include the mandatory Ethical Considerations section;
- include the mandatory Open Science section;
- include the mandatory AI Use section;
- comply with anonymisation requirements;
- verify every reference;
- ensure the paper builds with the venue-supported TeX environment;
- keep appendices supplementary rather than essential to understanding the claimed contribution.

### 23.3 Suggested main-body structure

Working structure:

1. Introduction
2. Background and Related Work
3. System and Threat Model
4. Semantic Credential Construction
5. Privacy-Preserving Authentication Protocol
6. Security and Privacy Analysis
7. Implementation
8. Experimental Evaluation
9. Limitations
10. Conclusion

Security proofs may move to an appendix if long, but the body must clearly state assumptions and theorem claims.

### 23.4 Claims the introduction should eventually support

Do not write final contribution bullets until validated.

Target contribution families are:

- formal model of semantic credential acceptance regions;
- private matching protocol;
- AI-assisted guessing/privacy attack evaluation;
- open implementation and reproducible experiments.

---

## 24. Artifact requirements

The artifact should reproduce the core scientific evidence rather than only launch the demo.

Target contents:

- source code;
- dependency lock/environment;
- model/download scripts;
- dataset acquisition/preprocessing scripts;
- experiment configs;
- attack scripts;
- analysis scripts;
- result files needed for figures/tables;
- artifact README;
- minimal/full experiment modes;
- expected resource requirements.

Do not redistribute model weights or datasets if their licences do not permit it. Provide validated acquisition scripts instead.

---

## 25. Ethics and privacy rules

The current paper intentionally avoids new participant research.

For public prompt datasets:

- do not attempt identity linkage/deanonymisation;
- remove/ignore unnecessary user identifiers;
- do not publish sensitive examples without a research need;
- document filtering decisions;
- follow licences and dataset documentation.

For attack experiments:

- use synthetic/local research accounts;
- do not attack real third-party authentication systems;
- do not probe external services for vulnerabilities without authorisation;
- follow responsible disclosure if an unexpected third-party vulnerability is found.

---

## 26. Related-work anchors that must be checked

The literature review should include and verify work in these categories:

### Semantic/graphical authentication

- graphical passwords;
- image-independent/semantic authentication;
- 2026 Image-Agnostic Visual Semantic Authentication (VSA).

### Noisy-secret cryptography

- secure sketches;
- fuzzy extractors;
- neural fuzzy extractors.

### Password authentication

- PAKE/aPAKE;
- OPAQUE (RFC 9807);
- OPRF/VOPRF specifications, including RFC 9497 where applicable.

### Private matching

- PSI/PSI-cardinality;
- secure two-party computation;
- private threshold matching;
- homomorphic encrypted similarity, including relevant PoPETs image/biometric matching work such as HyDia.

### Privacy attacks

- biometric/template inversion;
- embedding leakage;
- linkability;
- offline guessing.

### Prompt data / AI attacks

- DiffusionDB;
- password guessing with generative models/LLMs where relevant;
- adversarial VLM/image-representation attacks.

Do not cite a source merely because an AI agent says it exists. Verify it.

---

## 27. Decision gates

The later `PLAN.md` should include explicit decision gates. At minimum:

### Gate A — Semantic representation viability

Proceed only if intended concepts demonstrate usable technical separation from negative/near-neighbour concepts.

### Gate B — Image-stage justification

Decide whether image generation adds sufficient technical value compared with the text-only baseline.

### Gate C — Protocol selection

Choose the main privacy protocol only after correctness, leakage, compromise model, and performance comparisons.

### Gate D — Privacy contribution viability

Proceed with PETS framing only if the selected construction demonstrates a concrete privacy advantage over prior/plain baselines.

### Gate E — Attack resistance / honest limitations

If semantic guessing is too effective for standalone authentication, consider whether the contribution should be reframed as:

- a second factor;
- a warning/measurement paper;
- a protocol showing conditions under which semantic authentication can or cannot be secure.

Do not force a positive conclusion.

### Gate F — Paper story

Before final manuscript polishing, ensure all claimed contributions have direct evidence in figures, tables, proofs, or clearly defined analysis.

---

## 28. Recommended working outputs

The project should eventually produce:

```text
AGENT.md
PLAN.md
README.md
paper/draft.tex
paper/references.bib
paper/figures/*
prototype/*
experiments/*
tests/*
artifacts/README.md
results/*
```

The exact repository layout may differ if an existing project already has established conventions.

---

## 29. How Codex should work on this project

For every substantial task:

1. Read `AGENT.md`.
2. Read the current `PLAN.md` when it exists.
3. Inspect repository status and relevant files before changing them.
4. Identify which RQ, experiment, protocol component, or paper claim the task supports.
5. Do not silently broaden scope.
6. Implement the smallest coherent change.
7. Add/update tests.
8. Run relevant tests/linters/experiment smoke tests.
9. Update documentation when interfaces or scientific assumptions change.
10. Record unresolved scientific questions explicitly.
11. Do not write invented results into the manuscript.
12. Do not create unverified references.
13. Keep research code reproducible and configurable.
14. Summarise exactly what changed, what was validated, and what remains unresolved.

When a requested implementation conflicts with the scientific rules in this file, stop that implementation path and explain the conflict rather than silently weakening the research design.

---

## 30. Branch and change discipline

Unless the user explicitly instructs otherwise:

- do not rewrite Git history;
- do not force-push;
- do not delete branches;
- do not merge unrelated branches automatically;
- keep experimental changes reviewable;
- avoid committing generated model weights, massive datasets, secrets, tokens, or large experiment caches;
- use `.gitignore`/data instructions appropriately;
- preserve exact configuration for results that appear in the paper.

Before any destructive repository operation, obtain explicit user authorisation.

---

## 31. Secrets and sensitive data

Never commit:

- API keys;
- access tokens;
- passwords;
- private cryptographic keys used outside synthetic experiments;
- personal dataset identifiers;
- confidential data.

Use environment variables, `.env.example`, or secret-management mechanisms.

Research cryptographic keys used in reproducible synthetic experiments may be deterministically generated only when the experiment explicitly requires reproducibility and the documentation makes clear that they are non-production keys.

---

## 32. Current paper-level hypothesis

The working hypothesis is:

> A structured semantic credential combined with a private threshold matching protocol can provide a useful technical acceptance region for independently generated visual concepts while revealing less credential information and offering better compromise properties than plaintext or hash-bound semantic authentication baselines.

This is a **hypothesis**, not a result.

The project must be willing to reject or narrow it based on evidence.

---

## 33. Current preferred research direction

At project start, prioritise this path:

```text
local image generator
    ↓
structured semantic extraction
    ↓
versioned deterministic canonicalisation
    ↓
set/weighted-set matching
    ↓
OPRF/PSI-style private threshold protocol
    ↓
AI-assisted guessing + database-compromise evaluation
```

Maintain these alternatives as baselines/candidates:

```text
embedding + cosine
embedding + private encrypted similarity
fuzzy recovery + OPAQUE/PAKE
text-only semantic credential
```

Do not prematurely delete an alternative before the planned comparison/decision gate.

---

## 34. Future studies after this paper

Possible future human-subject work, outside this project scope:

- memorability over time;
- natural secret selection;
- authentication task completion;
- user preference;
- secure concept-creation guidance;
- accessibility;
- comparisons with passphrases/passkeys/password managers;
- recovery/reset workflows.

Do not implement a participant study as part of the current PETS project unless the project scope is explicitly changed by the user and all ethics requirements are addressed.

---

## 35. Definition of project success

The project is successful if it produces a publication-quality, evidence-backed answer to the research question, even if the answer reveals important limitations.

A strong positive result would show:

- stable enough technical semantic reproduction;
- measurable separation from realistic attackers;
- a concrete privacy benefit from the selected matching protocol;
- clear compromise/security assumptions;
- practical enough performance for the intended use case;
- reproducible experiments; and
- novelty clearly distinguished from prior visual-semantic authentication work.

A scientifically valuable negative result could show, for example:

- semantic acceptance regions are inherently too guessable at usable thresholds;
- model drift makes long-lived authentication impractical;
- protected templates remain effective offline verifiers;
- privacy-preserving comparison overhead is prohibitive; or
- image generation adds no technical value over text-only semantics.

Do not hide such results. They may require changing the paper's thesis, but they are part of correct research.

---

## 36. Next project action

After this `AGENT.md` is accepted, create a **step-by-step `PLAN.md`** that converts the research contract into implementation phases.

The plan should cover, in order:

1. literature/novelty validation;
2. repository and reproducible environment setup;
3. controlled semantic dataset design;
4. baseline AI pipelines;
5. canonical semantic representation;
6. plaintext matcher evaluation;
7. threat-model-driven attack framework;
8. privacy protocol candidates;
9. protocol comparison and selection gate;
10. end-to-end prototype;
11. full experiment matrix;
12. statistical analysis and figures;
13. manuscript drafting in the official PoPETs 2027 template;
14. artifact packaging and reproducibility checks; and
15. submission-readiness audit.

The detailed plan must contain acceptance criteria for every phase and must not assume positive experimental outcomes.
