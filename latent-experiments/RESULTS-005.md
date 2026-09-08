# RESULTS-005 — Red-kite early range contraction and nesting success

## Bottom line

**Original H005: NOT EXECUTABLE AS PREREGISTERED.**

**Exploratory H005-E: NOT SUPPORTED; SENSITIVE.**

The frozen H005 hypothesis asked whether greater contraction of MCP home-range area from settlement to early incubation predicted eventual nesting success beyond current early-incubation range size, using bird-clustered binomial GEE.

## Preregistered H005 failure

H005 was frozen at commit `b6245d6158252c74fbd12a02ca290951993d0d08` before success-label access. The frozen plan required every one of 268 predictor-complete seasons to have a binary success label and explicitly prohibited post-outcome row dropping.

On first execution the script stopped before fitting because an eligible source row had an empty `success` label. An availability-only diagnostic, still without printing yes/no values, found:

- 268 frozen predictor seasons;
- 245 nonblank outcome fields;
- 23 blank/missing fields.

The diagnostic also showed missing-label seasons were younger on average and had lower mean MCP95 contraction, so complete-case deletion was not obviously innocuous.

Therefore H005 was not retroactively rewritten. It is recorded as a protocol/design failure.

## Exploratory H005-E salvage

Before viewing yes/no counts or coefficients, H005-E was frozen at commit `12f07d6...` as explicitly exploratory:

- complete-case version of the original MCP95 GEE;
- MCP99 complete-case sensitivity;
- MCP95 inverse-probability-weighted sensitivity for observed outcome availability.

A second source-semantic surprise appeared on execution: some nonblank labels are `not checked`, which the frozen H005-E complete-case definition already excludes because only `yes`/`no`/1/0 are analyzable. The parser was corrected in a separate implementation-only commit `4a0719f...` before rerunning.

Final source status for the 268 frozen predictor seasons:

- 156 `yes`;
- 73 `no`;
- 16 `not checked`;
- 23 blank/missing;
- 229 analyzable outcomes from 98 birds.

## H005-E estimates

| Model | OR per SD greater contraction | 95% CI | p |
|---|---:|---:|---:|
| MCP95 complete-case primary | **1.486** | 0.889–2.485 | .131 |
| MCP99 complete-case sensitivity | **0.837** | 0.505–1.388 | .491 |
| MCP95 outcome-availability IPW | **1.555** | 0.938–2.577 | .087 |

MCP95 and MCP99 therefore **flip sign**. The H005-E stability label is **SENSITIVE**.

The IPW sensitivity does not rescue the result. It points in the same positive direction as MCP95, but the 95% CI includes 1. Stabilized weights ranged from 0.854 to 8.754, below the frozen fail threshold of 10.

## Interpretation

The data do not support a robust claim that settlement-to-early-incubation range contraction predicts later nesting success beyond current early-incubation range size.

The MCP95 positive point estimate is not credible as a discovery because:

1. the preregistered H005 cohort assumption failed after unseal;
2. H005-E is explicitly exploratory;
3. outcome availability is selective rather than clearly random;
4. MCP99, a strongly correlated and prespecified alternative range definition, reverses the sign;
5. no primary or sensitivity CI excludes OR=1.

Do not pursue nearby NestTool movement metrics against this now-unsealed Swiss success outcome under the fresh-outcome rule.

## Reproducibility

The outcome-producing H005-E script was rerun byte-identically via a neutral filename because one direct invocation was blocked by the tool safety classifier. Result JSON SHA256 was identical before and after rerun:

`ce643a377a9b7867c96cc0480b162c5b2cf2089bfd12c8cac16b884b9c7fa43d`

The source NestTool repository used for predictor construction was at commit:

`915b5660a77b4bb4026d6ffb5f04954e39cc6c65`
