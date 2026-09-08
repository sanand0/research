# H004 analysis plan — honey-bee level vs history

## Pre-outcome evidence

`analysis/extract_bee_predictors.py` streams the public PLOS S2 CSV and persists only safe May/June/August 2014 predictors. `analysis/prepare_bee_h004.py` produces one row per eligible colony. `analysis/bee_preoutcome_gate.py` establishes N, redundancy and specification agreement without outcome access.

## Outcome extraction

`analysis/run_bee_h004_survival.py` is written and frozen before outcomes. It fetches the source CSV into memory, retaining only `Colony Number`, `Date`, `Viable`, and `Colony Death` for endpoint construction; the raw source is never saved.

Primary endpoint is viability at April 2015. Explicit pre-April death is used only as a fallback for colonies without an April status. Ambiguous/missing outcomes are excluded rather than inferred.

## Model

Primary logistic GLM as specified in `hypothesis-004.md`. Sensitivities are recent slope and apiary fixed effects. No model selection occurs after outcome access.

## Verification

Before unseal:
- source outcome-containing CSV absent locally;
- predictor-only CSV contains no outcome fields;
- scripts compile/run predictor-side;
- freeze manifest hashes hypothesis, plan, extractor, feature builder, outcome script, and predictor gate.

After unseal:
- compare endpoint counts against public study-level information where possible;
- rerun frozen outcome script and require identical result hash;
- independently reproduce the primary coefficient with a second implementation if practical.
