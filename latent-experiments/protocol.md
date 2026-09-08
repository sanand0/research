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
