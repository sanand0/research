# Analysis plan 005-E — exploratory recovery after H005 outcome-availability failure

## Why this exists

Frozen H005 at commit `b6245d6158252c74fbd12a02ca290951993d0d08` required an observed success label for all 268 frozen seasons. On first execution, before any coefficient or success/failure count was produced, the script encountered an empty outcome label. An availability-only diagnostic then found 245 known and 23 missing/blank success labels.

Therefore **H005 is not executable as preregistered**. This H005-E plan is a transparently post-unseal-but-pre-value exploratory salvage. At the time of this freeze, no yes/no success counts or association coefficients have been viewed.

## Primary exploratory cohort/model

Complete cases among the frozen 268 H005 seasons: rows whose source `success` field is one of `yes`, `no`, 1, or 0.

Use the same primary GEE specification as H005:

`success ~ z_contraction95 + z_log_mcp95_incu1 + C(sex) + z_age + C(year)`

- binomial family;
- exchangeable working correlation;
- cluster by `bird_id`;
- robust covariance.

## Prespecified sensitivities

1. Replace MCP95 contraction/current range with MCP99 equivalents.
2. Missing-outcome IPW sensitivity for MCP95:
   - on all 268 frozen rows, fit logistic `known_outcome ~ z_contraction95 + z_log_mcp95_incu1 + C(sex) + z_age + C(year)`;
   - for the 245-ish known rows, use stabilized weight `P(known)/P(known|X)` in the same GEE;
   - fail rather than tune if any stabilized weight exceeds 10.

IPW can only address outcome availability related to observed predictors; missingness depending on unobserved success remains a limitation.

## Interpretation

This is exploratory because the complete-case rule was introduced after learning that outcome availability was incomplete. Report effect size/CI and stability, but do not call it a preregistered discovery. Any signal requires independent German validation.
