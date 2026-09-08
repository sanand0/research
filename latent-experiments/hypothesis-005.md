# H005 — Early range contraction and later nesting success in red kites

## Frozen question

Among field-observed red-kite nesting attempts, does contraction of the bird's home range from the settlement phase into early incubation predict eventual fledging success **beyond the bird's current early-incubation home-range size**?

The latent quantity is movement **history**, not current range size: two birds can have the same early-incubation range but have arrived there from very different settlement ranges.

## Outcome seal

Before this freeze, persisted H005 data contain no `success` values. Source code/metadata establish only that `success` is encoded as `yes`/`no` or 1/0 and is available for the eligible nesting seasons. Individual success labels, success counts for the H005 cohort, and any H005 model coefficient have not been inspected.

## Population and quality gate

- Swiss NestTool seasons with field-observed `nest == "nest"`.
- Valid settlement and early-incubation MCP95 and MCP99 areas.
- Exclude the exact MCP value `1`, which NestTool source code can use as a synthetic fill for a missing phase; values below 1 are valid areas.
- At least 100 GPS fixes in both settlement (DOY 70–96) and early incubation (DOY 97–112).
- Current outcome-blind eligible cohort: 268 seasons from 115 birds across 2017–2022.

## Primary predictor

`contraction95 = log(MCP95Settle) - log(MCP95Incu1)`

Positive values mean the range contracted between settlement and early incubation. Continuous predictors are standardized within the frozen eligible cohort.

## Mandatory current-state adjustment

`log_mcp95_incu1 = log(MCP95Incu1)`

This is load-bearing because contraction95 and current early-incubation range are strongly related outcome-blind (Spearman rho about -0.69). The estimand is therefore the association of *history beyond current state* with success.

## Primary model

Binomial GEE with exchangeable within-bird working correlation and robust sandwich covariance:

`success ~ z_contraction95 + z_log_mcp95_incu1 + C(sex) + z_age + C(year)`

Cluster: `bird_id`.

Primary estimand: odds ratio for success per 1 SD greater MCP95 contraction, two-sided 95% CI.

## Prespecified sensitivity

Replace MCP95 with MCP99:

`success ~ z_contraction99 + z_log_mcp99_incu1 + C(sex) + z_age + C(year)`

MCP95 and MCP99 contraction rankings agree strongly outcome-blind (rho about 0.83).

## Decision rule

- **SUPPORTED**: primary 95% CI excludes OR=1.
- **NOT SUPPORTED**: primary 95% CI includes OR=1.
- **STABLE**: MCP99 has the same coefficient sign and the same support/not-support classification.
- **SENSITIVE**: MCP99 changes sign or support classification.

A null is a valid result. No other NestTool movement feature will be tested against this success outcome after unseal as part of H005.

## Temporal-provenance exclusion

Do **not** use settlement/incubation `revisits`, `time`, `Dist*`, or other features measured relative to NestTool's inferred nest location. `data_prep()` identifies that reference location using season-wide tracking information, so those apparently early variables leak future information. MCP phase areas are computed from within-phase locations and pass the strict temporal-provenance gate.

## Source provenance

NestTool repository source commit used for predictor reconstruction: `915b5660a77b4bb4026d6ffb5f04954e39cc6c65`.
