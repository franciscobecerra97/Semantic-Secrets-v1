# Semantic Secrets

Research project for a prospective PoPETs/PETS 2027 paper on privacy-preserving authentication of noisy semantic credentials derived from AI-generated images.

## Current state

P0–P5 are complete. The repository now contains a frozen semantic canonicaliser, structured/weighted/dense representations, and a bounded 27-row train/validation smoke comparison. Controlled weighted direct-text semantics is the primary P6 hypothesis; SigLIP, MiniLM, and unweighted structured text remain baselines. Florence structured fusion was rejected, and no real representation has uncertainty-supported near-neighbour separation, so Gate A remains closed. No authentication implementation, downloaded public dataset, held-out test evaluation, protocol implementation, publication experiment result, or human-subject evidence has been produced.

Read these files before beginning work:

1. `AGENT.md` — persistent scientific and engineering contract.
2. `PLAN.md` — phased execution plan and decision gates.
3. `paper/draft.tex` — research-direction manuscript; hypotheses are not results.
4. `docs/security_model.md` — frozen P2 definitions, compromise states, and claim boundaries.
5. `experiments/datasets/README.md` — approved P3 smoke/pilot methodology and data restrictions.
6. `docs/model_screening.md` — P4 hardware, model/licence screen, smoke observations, and D1/D2 handoff.
7. `docs/representation_screening.md` — P5 canonicalisation, representation comparison, negative uncertainty result, and P6 boundary.

`paper/main.tex` and `paper/sample-base.bib` are venue/template examples, not the research manuscript or verified project bibliography. Verified references belong in `paper/references.bib`.

## Repository areas

- `paper/` — manuscript, verified bibliography, and final figures.
- `prototype/` — future modular client/server/semantic/cryptographic implementation.
- `experiments/` — controlled dataset specifications/manifests plus future runners, attacks, and analysis.
- `tests/` — future unit, integration, security-regression, and smoke tests.
- `results/` — future immutable run outputs and compact reproducibility evidence.
- `artifacts/` — future artifact-evaluation instructions and release scripts.

Large models, raw datasets, generated images, secrets, caches, and recomputable intermediates must not be committed. Small manifests, exact configurations, analysis inputs needed for paper claims, final figures, and compact result tables should remain versioned.

## Working rule

Execute one numbered phase from `PLAN.md` at a time. Do not pass a decision gate without its recorded evidence and acceptance criteria, and do not claim human memorability or usability: this project has no human-subject study.
