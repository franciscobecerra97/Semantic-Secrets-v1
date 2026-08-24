# Semantic Secrets

Research project for a prospective PoPETs/PETS 2027 paper on privacy-preserving authentication of noisy semantic credentials derived from AI-generated images.

## Current state

The project is initialized for research planning only. No authentication implementation, model pipeline, dataset, protocol, experiment, or result has been produced yet.

Read these files before beginning work:

1. `AGENT.md` — persistent scientific and engineering contract.
2. `PLAN.md` — phased execution plan and decision gates.
3. `paper/draft.tex` — research-direction manuscript; hypotheses are not results.

`paper/main.tex` and `paper/sample-base.bib` are venue/template examples, not the research manuscript or verified project bibliography. Verified references belong in `paper/references.bib`.

## Repository areas

- `paper/` — manuscript, verified bibliography, and final figures.
- `prototype/` — future modular client/server/semantic/cryptographic implementation.
- `experiments/` — future configs, runners, datasets, attacks, and analysis.
- `tests/` — future unit, integration, security-regression, and smoke tests.
- `results/` — future immutable run outputs and compact reproducibility evidence.
- `artifacts/` — future artifact-evaluation instructions and release scripts.

Large models, raw datasets, generated images, secrets, caches, and recomputable intermediates must not be committed. Small manifests, exact configurations, analysis inputs needed for paper claims, final figures, and compact result tables should remain versioned.

## Working rule

Execute one numbered phase from `PLAN.md` at a time. Do not pass a decision gate without its recorded evidence and acceptance criteria, and do not claim human memorability or usability: this project has no human-subject study.

