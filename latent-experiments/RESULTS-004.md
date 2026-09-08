# H004 result — honey-bee summer history vs first-winter survival

## Decision

**NOT SUPPORTED; SENSITIVE across prespecified trajectory definitions.**

H004 asked whether summer adult-population history predicts first-winter survival beyond August colony size in Alberta commercial honey-bee colonies.

Frozen preregistration commit: `fe4365120593c3aa15521085e4a6912b7338a488` (2026-09-08T20:08:22+08:00).
Implementation-only ID-type erratum: `870adbe18de88007eb917894b7857087ecd65b65` (2026-09-08T20:10:16+08:00). No model had fit before the erratum.

## Frozen results

225 predictor-complete Alberta colonies; 204 viable at April 2015 and 21 not viable.

- Primary three-point May/June/August log-adult trajectory: OR **0.864** per SD more positive slope, 95% CI **0.301–2.478**, p=.785.
- Prespecified June→August slope: OR **1.221**, CI **0.590–2.528**, p=.590.
- Prespecified apiary-fixed model with three-point slope: OR **0.743**, CI **0.247–2.230**, p=.596.

The primary and recent-slope specifications have opposite signs. Therefore the frozen stability criterion fails even though every interval is wide and includes 1.

## Known-signal / information diagnostic (post-hoc validation)

A simpler model using the known late-summer size signal gives August adult population OR **1.529** per SD, CI 0.958–2.440, p=.075 after region adjustment. In the full H004 model the August-size OR is 1.723, CI 0.799–3.715, p=.166.

This is qualitatively in the expected direction but imprecise. The 225-colony cohort contains only **21 failure events**. The full primary model therefore has ~3.5 failures per fitted parameter. At the observed trajectory standard error (~0.538 log-odds), a rough normal approximation implies ~80% power only for an effect around OR **4.5**. This is not a useful design for moderate incremental predictive effects.

## Interpretation

The data do not support the claim that pre-August adult-population history adds survival information beyond August size. They also cannot rule out large effects in either direction. The sign flip across reasonable slope definitions indicates that the trajectory estimand is not stable enough here to interpret.

This is primarily a **design/information failure**, not strong evidence of biological absence.
