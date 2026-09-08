# Latent Experiments candidate scorecard

Use this before substantive predictor modeling. **Hard-gate failures reject/defer the candidate.** Scores rank only candidates that pass every hard gate.

## Hard gates

| Gate | Pass criterion | Why |
|---|---|---|
| Open access | Predictor-side raw/minimally processed data + code can be normally retrieved and parsed | H001/Amherst and early red-kite scouting lost time to blocked blobs |
| Original-analysis gap | Source paper/code demonstrably did **not** test the proposed relationship/estimand | First chickadee timing idea and killifish lifespan forecasting failed here |
| Outcome vocabulary | Possible source statuses are known before freeze; valid labels explicitly defined | H005 `not checked` showed non-null != usable outcome |
| Outcome information | Binary/event outcome preferably >=80 usable events; continuous/count outcome has adequate spread/N | H004 N=225 hid only 21 deaths |
| Temporal provenance | Every ingredient of predictor was knowable by claimed prediction time | NestTool early nest-relative features leaked future nest-location inference |
| Predictor measurability | Derived trait/trajectory passes repeatability/reliability/quality checks before outcome | H002 killed visual slopes; H003 killed blue-tit predictability |
| Join/schema integrity | Predictor/outcome/design IDs and types verified before unseal | H004 string/int IDs caused empty join |
| Fresh outcome | Outcome has not already been used to select/tune predictors in this project | Prevents post-null phenotype mining |
| Replication path | Independent dataset/population/season is visible before outcome unseal, or candidate is explicitly exploratory | Makes a positive result worth pursuing |

## Ranking among gate-passers (0–2 each)

1. **Scientific need** — real recurring domain decision/problem.
2. **Novelty** — plausible paper-worthy residual question, not a trivial reanalysis.
3. **Information** — comfortable N/events/continuous range beyond minimum gate.
4. **Interpretability** — one-sentence estimand and low-dimensional primary model.
5. **Live-demo value** — outcome seal/reveal is understandable on stage.
6. **Reusable asset** — methods/general transform applies beyond one dataset.
7. **Replication ease** — independent data already public and structurally comparable.

Prefer >=10/14; treat <=7/14 as scout-only.

## High-value latent transforms discovered so far

- **projection join:** one paper studies *when*, another *where/outcome*;
- **mean -> residual variance:** does consistency matter beyond average behavior?;
- **snapshot -> trajectory:** does history add information beyond current state?;
- **state -> derivative/change point:** does acceleration/deceleration add warning?;
- **published null -> omitted component:** if average/plasticity is null, what variation did the abstraction discard?;
- **early-label audit:** is a feature actually knowable early, or merely named after an early phase?;
- **status -> estimand:** distinguish a true negative outcome from unknown/not-checked/censored.

## Outcome seal checklist

Before commit:

- persist no outcome values;
- inspect source code/schema for outcome status **vocabulary**, but not positive/negative counts;
- freeze usable-outcome rule and expected usable row count if it can be determined without revealing outcome values;
- freeze unit, time window, predictor, covariates, forks, support rule;
- verify predictor file contains no outcome-like columns;
- hash freeze artifacts and git commit;
- only then reveal outcome values.
