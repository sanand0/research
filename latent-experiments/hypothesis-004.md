# H004 — summer colony history and first-winter survival

Frozen before accessing individual post-August-2014 viability/death outcomes.

## Question

Among commercial honey-bee colonies of the same late-summer size, does how they arrived at that size predict whether they survive the following winter?

## Primary hypothesis

More positive May→August 2014 adult-population trajectory is associated with higher odds of being viable at the April 2015 post-winter assessment, conditional on August adult population, region, protein-supplement assignment and fumagillin assignment.

The test is two-sided; the mechanistic expectation is positive, but a negative effect is scientifically plausible because healthy strong colonies can naturally decline while transitioning from summer to winter bees.

## Population

Northern and Southern Alberta colonies with non-missing adult-population measurements at May, June and August 2014. Prince Edward Island is excluded because summer splitting and different management complicate a fixed-colony trajectory estimand.

## Primary predictor

OLS slope of `log1p(Adults)` against actual inspection date across May, June and August 2014, per 30 days.

Mandatory covariate: log August adult population. This makes the estimand explicitly “history beyond snapshot.”

Other covariates: region, protein supplementation assignment, fumagillin assignment.

## Outcome

Binary first-winter survival: viable at the April 2015 assessment. If an eligible colony lacks an April status, it is coded dead only if the source explicitly records `Colony Death==1` by the April assessment; otherwise it is excluded as outcome-unknown.

## Primary model

`survived_first_winter ~ August_log_adults + three_point_slope + Region + Patties + Fumagillin`

Continuous predictors are standardized over the analyzed cohort. Report OR per 1 SD more positive trajectory, 95% CI and two-sided p-value.

## Prespecified stability checks

1. June→August log-population slope instead of the three-point slope.
2. Apiary fixed effects instead of region fixed effects.

Conclusion labels:
- SUPPORTED: primary 95% CI excludes OR=1.
- NOT SUPPORTED: primary CI includes 1.
- STABLE only if both sensitivity estimates retain the primary sign and neither produces a substantively contradictory large effect.

No alternative trajectory, threshold, outcome date, region subset, or colony-health variable will be selected after outcome access.
