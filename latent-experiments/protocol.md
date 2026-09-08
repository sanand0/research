# Latent Experiments protocol

Started: 2026-09-08 (SGT)

## Goal

Test whether an AI research workflow can find a scientifically plausible relationship in an already-published open dataset that the original paper did not test, while avoiding outcome-peeking before the hypothesis is frozen.

This phase implements only steps 1-5:

1. Search papers with rich open datasets.
2. Read paper, supplementary material, and data documentation/structure.
3. Enumerate what the authors actually tested.
4. Generate plausible relationships they did not test.
5. Freeze a candidate hypothesis before inspecting its relevant outcomes.

Outcome analysis, replication, and novelty claims are deliberately out of scope until after the freeze.

## Inclusion criteria

A candidate should have:

- an openly downloadable dataset and enough documentation to interpret it;
- multiple measured variables beyond the paper's narrow headline hypothesis;
- raw or minimally processed observations, not only published aggregate results;
- a scientifically interpretable candidate relationship with a plausible mechanism;
- enough observations / repeated measures to make a later test meaningful;
- preferably a path to independent replication in another dataset;
- no need for new sensitive/private data or risky intervention;
- a relationship that can be stated before looking at the relevant outcome values.

## Anti-HARKing / anti-leakage rules

Before hypothesis freeze, allowed:

- paper text, methods, stated analyses and reported results;
- supplementary methods and code, to identify what was already tested;
- dataset README / dictionary;
- file names, dimensions, column names, types, missingness counts and identifier cardinalities;
- study design, sampling dates/locations, and sample size;
- literature search about mechanisms and prior work.

Before hypothesis freeze, prohibited for a candidate relationship:

- correlations, regressions, group means, plots, contingency tables, or outcome distributions involving the candidate predictor and outcome;
- sorting/filtering rows in a way that reveals their joint relationship;
- reading analysis output that already reports the candidate relationship;
- choosing direction/effect after seeing outcome data.

If a source accidentally reveals the candidate relationship, that relationship is contaminated and cannot count as a latent experiment.

## Freeze requirements

A frozen hypothesis must record:

- exact predictor(s), outcome(s), population/unit of analysis;
- expected direction or shape (or explicitly two-sided if theory cannot justify direction);
- proposed mechanism;
- primary statistical test/model and key controls known in advance;
- falsification / failure criterion;
- known prior art found before freeze;
- file hashes / source versions where practical;
- timestamp in git history.

## Ranking criteria

Prioritize: scientific legitimacy, novelty plausibility, outcome-blind testability, replication path, interpretability, SciPy demo value, and reusable-asset potential.


## Phase-2 validation gates learned from Experiment 001

These gates apply once a frozen hypothesis advances to outcome analysis or replication.

### Derived-phenotype known-signal gate

Before a reconstructed or approximated phenotype is trusted for a novel relationship, reproduce at least one source-paper quantity or known relationship when possible: sample structure, fixed effect, variance/repeatability, cross-trait correlation, or published downstream association. A plausible feature is not enough.

If a phenotype fails this gate, it may not be used to rescue or overturn the primary result without being labelled post-hoc.

### Computational reproducibility gate

Every stochastic analysis component must be executed at least twice from the same inputs and explicit RNG state. Compare output hashes or key numeric outputs. A global seed is not sufficient if the underlying library accepts or uses its own RNG.

### Stability gate

Predeclare the few defensible analytical forks most likely to matter. Report whether the conclusion is STABLE, SENSITIVE, or FLIPS. A null must not trigger substitution of an unregistered outcome, subgroup, window, or phenotype.

### Replication before re-mining

After the primary test, prefer an independent population or season to additional relationship mining in the same outcome data. Replication protocols should be frozen before external outcome membership or labels are viewed.

### Staged outcome unseal

When outcome files also contain design metadata needed to define observation opportunity, separate them programmatically: first extract design-only information with individual membership suppressed; freeze the eligible cohort and observation model; only then expose individual outcome membership.

The observable endpoint must match the sampling design. Do not call non-detection `death` or `survival` when dispersal or changed detector coverage are plausible.

## Phase-3 gates learned from H002

### Individual-trait reproducibility gate

A nonzero random-effect or random-slope variance does **not** establish a persistent individual trait. Before relating a derived individual phenotype to an outcome, require outcome-blind stability across independent repeat blocks/splits when the study design permits it. Reject traits whose individual ranking reverses or collapses even if the full mixed model converges.

### Archive-semantics gate

Before treating a large archive as a data source, inspect its manifest/README/central directory. Filenames and size are not evidence of scientific content.

### Cross-language missing-value gate

When reproducing an author pipeline in a different language, explicitly test missing-value and categorical transformation semantics. R `NA`, pandas `NaN`, SQL `NULL`, and boolean casts do not necessarily behave equivalently.

### Full latent diagnostic gate

For hierarchical Bayesian phenotypes, convergence checks include all sampled latent/random-effect parameters, not just population-level coefficients. Record max R-hat, minimum bulk ESS and divergences.

### Fresh-outcome rule

Once a sealed outcome has been unsealed, do not select or tune additional latent predictors against that outcome. New scientific questions must use a fresh sealed outcome, independent replication cohort, or be labeled explicitly exploratory/post-hoc.

### Outcome-information gate

Raw sample size is not enough. Before investing in a fresh experiment, use public aggregate information (not sealed individual outcomes) to estimate how much outcome information exists.

- Binary/time-to-event: record expected event count, not only N. Prefer >=80 events for modest multivariable tests; if far lower, simplify the estimand/model or reject the candidate before outcome access.
- Continuous/count: record usable N plus aggregate variability/range when publicly reported.
- Flag designs with <10 outcome events per effective parameter as high-risk for imprecision unless a prespecified regularized/sparse model justifies them.

### Identifier-type gate

Before outcome unseal, normalize join-key types and verify that predictor/design-only namespaces produce the expected nonzero overlap. String-vs-integer parsing errors must not be discovered only after outcome access.

## Phase-4 gates learned from H005

### Temporal-provenance gate

A predictor labelled with an early phase/date is not automatically an early predictor. Before freeze, trace when **every ingredient** used to construct it became knowable. If an early feature depends on a reference point, segmentation, calibration, label, or location inferred from future observations, treat it as future-leaking and exclude it from prospective/early-warning claims.

### Outcome-status vocabulary gate

Before freezing an outcome model, establish the complete **set of source outcome statuses** without inspecting their positive/negative distribution or predictor associations. Define usable outcomes by explicit membership in valid labels, not by non-null/nonblank checks. Distinguish values such as `yes`, `no`, `not checked`, `unknown`, `censored`, blanks, and true missingness.

Freeze the expected `usable_outcome` row count before unseal. If that count fails after unseal, the preregistered analysis is non-executable unless the frozen plan already specifies the missing-status handling.

### Confirmatory-to-exploratory demotion rule

If a frozen cohort/outcome assumption fails after unseal and fixing it changes the analysis population, do not silently call the corrected analysis preregistered. Close the original as non-executable and, only if outcome values remain unseen, freeze a separately named exploratory salvage with explicit missingness assumptions. Any signal from that salvage requires independent replication.
