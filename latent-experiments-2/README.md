# Latent Experiments 2

## Objective

Build and demonstrate an agent-driven scientific loop that starts from a consequential unexplained observation or disagreement, commits a discriminating prediction before confirmation access, tests it against independent evidence, preserves failures, and leaves reusable FOSS tooling.

This project is separate from `latent-experiments/`. The pilot is evidence about failure modes, not the operating protocol. See `PILOT-LESSONS.md`.

## Current status

**C001 and C002 stopped before confirmation; C003 completed a positive discovery but failed frozen independent confirmation; fresh scout 001 produced no survivor after C004 was killed by prior art and C005/C006 failed the clean-confirmation gate. No independently confirmed new scientific claim yet. Next: intervention-focused fresh scout 002.**

### C001 — repeated TEM-1 DMS maps: stopped

Firnberg 2014 + Stiffler 2015 were discovery evidence; Jacquier 2013 was reserved confirmation and Deng 2012 a method-contrast control. **Jacquier and Deng scores remain unopened.**

What survived:

- 4,782 common missense mutations; rank correlation ~.937 despite incompatible raw scales.
- ProteinGym preserves the chosen source scores numerically.
- Primary literature already establishes selection-strength-dependent TEM-1 effects.
- A tempting structured-residual statistic fails its empirical null: Firnberg→Stiffler position eta²=.215, while five actual same-condition Stiffler replicate pairs span .186-.454 and all reject the naive permutation null.
- Independent percentile-rank residuals make the stop stronger: cross-study eta²=.246 versus replicate range .298-.470.

Reusable lesson: **a cross-assay residual null must accept real same-condition replicates before structured residuals are called biology.** See `results/c001_calibration.json` and commit `2d5a21e`.

### C002 — neuronal criticality / subsampling: stopped

Allen Visual Coding Neuropixels supplied a strong operational testbed. Design metadata were used before spike access to freeze `functional_connectivity` sessions with a continuous ~30-minute spontaneous period. A VISp eligibility rule produced 12 discovery + 12 confirmation mice.

Only discovery mouse `767871931` was opened. **Eleven other eligible discovery mice and all 12 confirmation mice remain unopened.**

A FOSS multistep-regression (MR) estimator was calibrated at 4-ms bins with a frozen exponential-fit applicability gate R²>=.90:

- aggregate branching simulations at true m=.8/.98/.99 remain essentially unbiased under 100%/50%/25% event sampling;
- independent Poisson/null data fail applicability despite occasionally returning raw m near 1;
- the real mouse's primary 32/16/8-unit subsets all fail applicability; across ten alternative 32-unit subsets only 7/10 pass;
- fixed-neuron simulations with strong rate heterogeneity and static mixed timescales give 60/60 valid fits;
- simple global/asynchronous state-switch stress tests give 60/60 valid full-session fits.

Thus the real subset-dependent low-R² behavior is not reproduced by the bounded branching-family calibrations. Continuing would require progressively richer post-outcome model invention in a mature criticality debate, so C002 is stopped rather than rescued. See `RESULTS-C002.md`.

Reusable lesson: **“subsampling-invariant” estimation is conditional on model applicability. Gate the correlation/dynamical form itself before interpreting a near-one parameter.**

All four stochastic C002 result files reproduced byte-identically across two runs.

## Candidate ranking

1. **Fresh discrepancy scout.** Search current 2025–2026 primary literature for consequential observations with two credible explanations and clean, source-level independent confirmation.
2. **Prefer direct measurements + cheap perturbations.** Penalize mature debates, ambiguous aggregation, derived traits, and confirmation that can only be made by arbitrary row splits.
3. **Do not reopen C001/C002/C003.** C001/C002 methods failed before confirmation; C003 failed independent confirmation. Any follow-on requires a new claim and fresh evidence.

### C003 — Taylor-law dominance interpretation: failed confirmation

A constraint-preserving null fixed every species total, census total, and occurrence mask. Discovery in three German steppe cover plots found extra dominance-like temporal organization in 2/3 plots. Frozen confirmation in five independent Danish heath plots found 0/5 passes despite every raw Taylor slope being below 2; study-level p=1.0 under both null generators.

Reusable lesson: **`b<2` alone is mechanistically non-diagnostic.** In all eight analyzed plots the constraint null itself typically produced `b<2` (median roughly 1.4–1.8). Some communities showed extra organization beyond those constraints, but it did not generalize. See `RESULTS-C003.md`.

### Fresh scout 001 — no survivor

C004 used newly released ABCFlux v2 to ask whether CH4 observation-network representativeness is a between-ecosystem/time problem or a within-stratum sparse-measurement problem. Synthetic calibration showed ecosystem×month weighting can remove class oversampling but not preferential high-flux-day sampling. The exact needed empirical chamber-vs-eddy-covariance comparison, however, was already published across ten sites and multiple timescales in July 2026, so C004 was rejected before real flux outcomes. C005 (unperceived LO decoding) and C006 (data-availability statements) were demoted for weak clean confirmation / mature prior art. See `scouts/FRESH-SCOUT-001.md`.

Reusable lesson: **search for the implied discriminating experiment before investing in a newly enabled dataset analysis.**

## Minimal execution layer

- `claims/` — claim/evidence-role/access state.
- `ledger.jsonl` — machine-readable input versions, access, calibration/results, decisions and resource events.
- `analysis/` — only analysis needed by an active investigation.
- `results/` — small reproducible outputs.
- `STATE.md` — exact resumable action.
- Raw data and third-party archives remain ignored.

## Resource budget

- FOSS/local computation only; no paid APIs or cloud compute without an explicit new budget.
- <=2 GB downloaded source data before a scientific checkpoint and <=10 GB transient cache.
- <=30 CPU-minutes for any single bounded analysis; no persistent/background jobs.
- Commit only code, metadata, small results, and documentation.
- Stop a path when the next test cannot change the scientific conclusion.

## SciPy India fit

Current conference requirements checked 2026-09-09: 30-minute in-person talk including Q&A; FOSS/OSI-licensed focus; CFP closes 19 Oct 2026 23:59 IST. AI/data-driven discovery and reproducibility are plausible tracks. The live loop should make **failed calibration and stopping** first-class outcomes, not only successful discoveries.
