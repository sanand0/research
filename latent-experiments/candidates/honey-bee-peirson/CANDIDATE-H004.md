# H004 candidate — does colony history add information beyond current hive size?

Source: Peirson et al. (2024), 362 commercial honey-bee colonies across three Canadian regions, 11 assessments over two years. Main CSV and author R code are public PLOS supplements.

## Latent omission

The source paper models adult bee population longitudinally as an outcome and survival separately as a treatment/region outcome. It does not test whether pre-winter population *history* predicts subsequent survival conditional on current colony size.

Known prior: late-summer/fall colony size predicts overwinter survival. Therefore H004 is **not** “large colonies survive.” It asks whether history adds information after current August size is held fixed.

## Outcome seal

Only May/June/August 2014 Alberta predictor fields have been persisted. No `Viable`, `Colony Death`, `Last Viable`, November 2014, April/May 2015, or later values have been saved or summarized before freeze.

Alberta only is primary because PEI colonies were split and managed differently during summer 2014, creating a changing unit/management structure.

## Predictor-side feasibility

- 240 Alberta colonies; 225 have complete adult-population measurements in May, June and August 2014.
- all three measurements use the same visual population-estimation method in the source study.
- primary trajectory: OLS slope of `log1p(Adults)` vs actual inspection date across May/June/August, expressed per 30 days.
- trajectory vs recent June→August slope: Spearman rho ~0.759.
- trajectory vs August log size: rho ~0.781; therefore size adjustment is mandatory.
- after conditioning on August size, region and randomized treatments, residual trajectory SD is ~45% of its marginal SD: not fully redundant.

Decision: **passes pre-outcome feasibility**.
