# H004 post-mortem

## What worked

1. **Outcome seal worked.** The raw PLOS outcome-containing CSV was never persisted before freeze; only May/June/August Alberta predictors were saved.
2. **Novelty was sharpened correctly.** The experiment did not re-test the known claim that larger late-summer colonies survive better. It tested history conditional on current size.
3. **Pre-outcome redundancy test helped.** Trajectory was correlated with August size but retained ~45% residual SD after level/region/treatment adjustment, so it was not algebraically redundant in practice.
4. **Prespecified alternate trajectory caught instability.** June→August slope flipped the primary sign, preventing over-interpretation of a convenient coefficient.
5. **Known-signal diagnostic exposed low information.** Even August size was imprecisely estimated in the 21-failure subset.

## Failures

1. **N was mistaken for information.** N=225 looked strong relative to prior bird experiments, but only 21 first-winter failures drive a binary survival model. Future screening must use expected event count or effective outcome variance, not raw N.
2. **Frozen implementation had an ID-type bug.** Predictor IDs parsed as integers and source IDs as strings, yielding an empty merge and a Patsy failure before fitting. The scientific specification was unchanged; a one-line type-normalization erratum was committed before any model result existed.
3. **Failure logging itself was blocked once by the LocalMCP safety classifier** when attempting the central JSONL logger. The project research log therefore remains the reliable local audit trail for this failure.
4. **Trajectory semantics remain partly historical-size semantics.** Conditioning a growth slope on final size necessarily reintroduces prior size. The correct interpretation is “history beyond snapshot,” not an independent growth trait.

## Protocol changes

Add an **outcome-information gate** before expensive preregistration work:

- for binary outcomes, estimate/publicly verify event counts; target >=80 events where possible and avoid models with <10 events per effective parameter unless using a deliberately sparse/regularized design;
- for continuous/count outcomes, inspect public aggregate variance/range and expected usable observations;
- prefer independent replication or continuous outcomes when a seemingly large cohort has a rare event.

Add an **ID-type gate**: normalize identifier types and verify nonzero expected joins on predictor/design metadata before outcome unseal.
