# Results 002 — Behavioral predictability and annual survival

## Decision

**H002 is not supported.**

The preregistered primary analysis finds no clear association between residual behavioral unpredictability and subsequent annual survival after controlling mean latency-to-resume-feeding and sex.

Primary (birds with >=4 latency observations):

- N = 74 birds: 43 redetected/surviving, 31 not redetected;
- beta for 1 SD greater unpredictability = -0.185;
- OR = **0.831**;
- 95% CI = **0.439–1.573**;
- two-sided p = **0.570**.

The interval spans effects in both directions. This is a stable but imprecise null, not evidence that behavioral predictability has exactly zero fitness association.

## Stability

The support decision is **STABLE** across all preregistered eligibility/adjustment forks:

| Specification | N | OR | 95% CI | p |
|---|---:|---:|---:|---:|
| Primary: >=4 obs + mean latency + sex | 74 | 0.831 | 0.439–1.573 | .570 |
| >=6 obs | 68 | 0.824 | 0.426–1.594 | .565 |
| >=8 obs | 62 | 0.812 | 0.397–1.659 | .567 |
| >=4 obs, no mean-latency adjustment | 74 | 0.865 | 0.485–1.545 | .625 |

The point estimate consistently suggests lower survival with greater unpredictability, but it is small relative to the uncertainty and was not directionally preregistered.

## Predictor uncertainty mattered

The primary analysis propagates posterior uncertainty in bird-specific residual scale and mean latency through 1,000 binomial GLMs. The between-imputation SD of the unpredictability coefficient is 0.195.

An independent point-estimate logistic re-derivation that ignores phenotype uncertainty gives OR = 0.754 (95% CI 0.437–1.301). Thus uncertainty propagation widens the primary interval substantially but does not change its conclusion.

## Source-outcome verification

The source CSV stores annual survival only on one row per bird and leaves later repeated behavioral rows missing. The author R code first creates `survival2 = ifelse(survival > 0, 1, 0)` and then keeps the first row per ID. Reproducing that exact storage convention yields 79 outcomes: 44 positive and 35 zero, matching the published paper.

An earlier pandas check incorrectly treated `NaN > 0` as False, creating artificial within-bird 0s. That was detected before H002 execution and did not alter the extracted first-row outcomes.

## Computational verification

- The outcome script committed before unsealing is unchanged from preregistration commit `63d7838337926959e1b147b6fcf06783b2132b9d`.
- `analysis/h002_survival_results.json` has SHA256 `1ef225411a6745cd5ef2eccad61a9aa968068733b627c50f059a56071f22a12a` on two independent reruns.
- All 1,000 multiple-imputation GLMs succeeded in each primary/sensitivity analysis.
- A separate scipy maximum-likelihood implementation recovered the same negative/null association.

## Scientific interpretation

The source paper already reports no support that a bird's **mean** feeding rate or mean risk-taking latency predicts annual survival. H002 asked whether the discarded second moment — persistent behavioral predictability — did better. It does not, at least in this 79-bird winter cohort.

This weakens a tempting story that fitness is hidden in behavioral consistency after average boldness proves null. However, H002's split-half predictability reliability is only moderate (~0.37–0.44); attenuation remains plausible. The data are not precise enough to distinguish a modest effect from zero.

## What was learned even from the null

The outcome-blind process rejected two more exciting but unstable candidate traits before survival access:

1. visual-predator-cue plasticity: fitted random-slope variance existed, but split-half slopes correlated negatively;
2. temperature plasticity: random-slope variance was near the boundary and unstable.

Only residual predictability survived reproducibility, robust-likelihood and split-half gates. It then failed the survival test. This is useful evidence that the gates are preventing the agent from converting every flexible repeated-measures dataset into a convenient discovery.

## Do not do next

Do not mine another trait against the same p3hz4 survival outcome. The outcome is now unsealed and additional phenotype selection would be post-hoc. Per protocol, the next substantive experiment should use a fresh sealed outcome, independent cohort, or different scientific dataset.
