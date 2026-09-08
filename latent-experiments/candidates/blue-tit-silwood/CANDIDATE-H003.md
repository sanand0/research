# Candidate H003 — female laying-date predictability and later reproductive fitness

## Source

Chik et al. (2022), Silwood Park blue tits, 2002–2019. Public Figshare record 11856108.
The source analysis tests selection on female mean laying date and laying-date plasticity to oak budburst via lifetime breeding success (LBS). The paper explicitly notes that heterogeneity in individual variance could be biologically interesting but was not modelled to avoid overfitting.

## Outcome seal

The source `btoak.csv` also contains clutch-size and hatchling outcomes. It is never saved locally. `analysis/extract_blue_tit_predictors.py` streams the source and persists only:

`year,nest.box,female,f.age,LD,BD,mc.LD,mc.BD`

No clutch-size or hatchling field is persisted or summarized before a preregistration freeze.

## Latent question

Do repeat-breeding females differ reproducibly in **laying-date predictability** — residual within-female variation in laying date after accounting for population year and age effects — and, if so, does that predict later/lifetime reproductive fitness independently of mean laying timing?

This is not yet H003. It must first pass predictor-only trait gates.

## Predictor-only primary phenotype

Hierarchical location-scale model on laying date:

- mean: year fixed effects + age category + female random intercept;
- residual scale: partially pooled female-specific log-SD;
- primary eligible phenotype population: females with >=3 laying-date observations and whose last observed breeding year is before 2019 (mirrors the source paper's right-censoring exclusion for LBS);
- >=4-observation females are used for split-half reliability.

## Pre-outcome acceptance gates

1. Convergence: max R-hat <=1.01, zero divergences, adequate ESS.
2. Nontrivial among-female residual-scale heterogeneity.
3. Independent odd/even breeding-attempt predictability ranking is positive; target rho >0.2, with uncertainty reported.
4. Primary ranking is stable to Student-t residual likelihood (rho >=0.80).
5. Primary ranking is not mainly an observation-count artifact (|rho| <0.30 with n observations).
6. Mean-model/source check: strong year structure and sensible age effect; no obvious residual pathology.
7. Correlation of predictability with mean laying date is quantified; if material, mean laying date becomes a mandatory fitness covariate.

If gates 1–3 fail, reject before outcome access. Passing is permission to design/freeze an outcome test, not evidence for a fitness relationship.

## Important design question still unresolved

The source paper's LBS is `sum(no.hatchlings)` and therefore combines longevity/exposure with annual productivity. Before freezing an outcome test, choose between:

- evolutionary-fitness estimand: lifetime hatchlings, closely matching authors;
- productivity estimand: annual/future reproductive output with exposure handled explicitly.

The choice must be made before unsealing hatchling values.

## Predictor-only gate result — REJECTED

The cheap residual-SD screen was weak (odd/even Spearman rho 0.083; early/late rho 0.148). A four-chain hierarchical location-scale model was then fitted exactly because partial pooling could, in principle, rescue noisy raw SDs.

Full-fit result:
- 193 females with >=3 observations, 677 observations;
- among-female residual-scale heterogeneity is clearly nonzero: `sigma_log_sigma` median 0.533, 3–97% quantiles 0.446–0.636;
- full model max R-hat 1.008, zero divergences.

But the preregistered trait-reproducibility gate fails:
- 69 females with >=4 observations available for independent odd/even splits;
- posterior predictability odd/even Spearman rho = **0.166**, below the predeclared 0.20 target;
- odd split has 6 divergences and max R-hat 1.011;
- even split has 31 divergences;
- score-vs-observation-count rho = 0.059 (good but insufficient to rescue reliability);
- score-vs-mean-laying-date rho = 0.312.

Decision: **reject H003 candidate before any clutch-size/hatchling outcome access.** Do not tune target_accept, priors, thresholds, or residual definitions to make the split ranking cross the gate. The scientifically interesting fact is that females differ in apparent residual variance, but with only 3–7 breeding records per repeat female that variance is not reproducible enough at the individual level for a fitness test.
