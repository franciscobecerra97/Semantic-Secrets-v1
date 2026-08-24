# Power and uncertainty rationale v1

P3 does not choose a full sample size. It defines how P6/P7 must choose one after the pilot.

## Independent unit and clustering

The primary independent unit is the concept family. Seeds, paraphrases, styles, layouts, model versions, and near neighbours are repeated observations within a family. Treating every generated image or pair as independent would understate uncertainty.

Analyses must use family-level aggregation, cluster bootstrap/resampling by family, hierarchical/mixed models where justified, or another method that explicitly preserves this dependence. Random impostor pair counts can grow quadratically without adding the equivalent number of independent secrets.

## Smoke and pilot roles

- Smoke (`12` families) is for schema/interface/failure discovery only. It cannot pass Gate A or support paper-level estimates.
- Pilot (`60` planned families, split 36/12/12) estimates extraction failure, same/negative score variance, within-family correlation, stratum imbalance, model runtime/storage, preliminary AUC, and attack-success dispersion. It is candidate-elimination and design evidence, not confirmatory evidence.
- If pilot failures or intervals make useful discrimination implausible, stop/revise at the gate rather than increasing `n` until significance appears.

## Full-size rule

Before opening full test labels, P6/P7 must freeze:

1. primary estimands and acceptable uncertainty;
2. operating-point selection using train/validation only;
3. family/stratum allocation;
4. the pilot variance/intraclass-correlation inputs;
5. attrition/failure handling;
6. bootstrap/simulation code and seed; and
7. compute/storage feasibility using measured P4 costs.

Candidate precision requirements for planning are:

- family-level completeness/stability and targeted-negative acceptance: two-sided 95% interval half-width at most `0.05` for the aggregate, with stratum intervals reported even if wider;
- ROC AUC: cluster-bootstrap 95% interval total width at most `0.05` for the primary representation/matcher comparison;
- paired image-versus-text primary effect: 95% interval excludes effects smaller than the preregistered smallest technically meaningful difference, which P7 must define in metric units before full data;
- guessing/attack success: confidence bounds at named budgets; no claimed rate below the experiment's effective resolution.

The final family count is the maximum required across primary estimands and mandatory strata, rounded only to satisfy balanced family allocations. Use pilot-based cluster bootstrap or simulation for AUC/paired effects. For a simple family-level proportion, use Wilson/exact-binomial planning as a cross-check and inflate for repeated-measure clustering rather than counting each trial independently.

For zero observed independent successes among `n` families, the approximate one-sided 95% upper bound is `3/n`; report the exact bound in final analysis. This prevents claims of negligible FAR or attack success from a small test.

## Multiplicity and threshold selection

- One primary representation/matcher/operating rule is selected before confirmatory testing.
- Threshold sweeps are descriptive curves; a threshold chosen on test data cannot support a confirmatory point claim.
- Mandatory baselines remain reported. Secondary strata and attacks receive labelled exploratory intervals or a frozen multiplicity procedure.
- Model/canonicalisation changes create a new version and cannot reuse the old test set as untouched confirmatory evidence.

## Missingness and failures

Generator/extractor/schema failures are outcomes. Report their rate by concept stratum and pathway. Do not silently drop a failed positive trial; the primary technical-completeness analysis treats failure as non-acceptance unless a separately justified estimand says otherwise. For malformed authored concepts discovered by blind audit, amend the catalog before any model comparison and preserve the prior version.

## Stop conditions

Narrow or stop rather than scaling if:

- the ontology cannot be annotated consistently;
- the pilot shows gross technical instability or near-neighbour overlap;
- required family counts exceed available compute/storage under measured P4 costs;
- public sources cannot be used ethically/reproducibly; or
- the image pathway offers no plausible measurable benefit and Gate B should remove it.
