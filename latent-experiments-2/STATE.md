# STATE

Updated: 2026-09-09 SGT

## Phase

`C001 STOPPED -> C002 STOPPED -> C003 FAILED CONFIRMATION -> SCOUTS 001–004 NO SURVIVOR -> PROJECT REASSESSMENT -> PROTOCOL/TALK/BENCHMARK EXTRACTED -> OFFLINE REHEARSAL`.

## Durable scientific state

- **C001:** stopped before confirmation; empirical same-condition replicate structure invalidated a tempting permutation-null residual. Jacquier/Deng remain unopened. Commit `2d5a21e`.
- **C002:** stopped after one discovery mouse; estimator applicability failed on real VISp data despite branching-family calibration. Eleven discovery mice and all 12 confirmation mice remain unopened. Commit `eb02a4b`.
- **C003:** positive discovery in 2/3 German steppe plots failed frozen independent confirmation in 0/5 Danish heath plots. Constraint null itself usually had `b<2`. Commit `5afac40`.
- **Scout 001:** no survivor; exact-discriminator prior art killed C004 and C005/C006 failed confirmation/causal gates. Commit `3b47bc6`.
- **Scout 002:** no survivor; C007 lacked decisive pathology, C008 discriminator already published, C009 lacked independent same-setting gap observable. Commit `4fe1dd2`.
- **Scout 003:** no survivor; C010 confirmation destroyed same-unit LAI pairing, C011 was mature multivariable prior art. Commit `57bad75`.
- **Scout 004:** no survivor. C012 stopped before hue-effect calculation because discovery labs did not share anatomically comparable skin-temperature measurements or a common adequately observed HR variable. Confirmation labs 2/4/6/8 remain unopened. C013/C014 rejected at scout gates. See `scouts/FRESH-SCOUT-004.md`.

## C012 calibration result worth preserving

Before real outcomes, synthetic calibration rejected participant-dominated inverse-variance pooling for a multi-lab replication claim. Final analysis treats laboratory as the replication unit: equal-weight lab-level one-sample t test + >=3/4 positive + leave-one-lab-out positivity. In 1,000 simulations:

- true 0.00 °C: 3.0% pass rate;
- +0.05 °C: 47.6% power;
- +0.10 °C: 93.9% power;
- +0.15 °C: 99.9% power.

Result SHA-256 `8e72ae7abf9bd0f8c1440a5ccd3f06a409c1b0efb4e2d5c38e68c3fcc5576c83`, reproduced byte-identically.

## Extracted reusable artifacts

- `SCIENTIFIC-LOOP.md`: minimal falsification-first protocol, claim spec, access ledger, calibration checklist, confirmation rule and stop conditions, with C001/C003/C012 examples.
- `TALK-NARRATIVE.md`: 24-minute narrative + 6-minute Q&A, with C012 as a safe live gate and C003 as the full positive-discovery/failed-confirmation loop.
- `AGENT-BENCHMARK.md`: prospective paired-packet experiment that freezes a common candidate pool, compares protocol-agent/rule/random/(optional human) selectors, and uses one neutral executor so question selection is not confounded with analysis skill.
- `analysis/c012_semantic_gate.py`: discovery-only schema/missingness gate that computes no hue effect.
- `results/c012_semantic_gate.json`: semantic-stop result SHA-256 `42febae1469e3159bdddec5402fbe19498bcba57ebd558f9ca12165baadbcf49`, reproduced byte-identically. Lab 1 has back/shin skin sites, lab 7 hand only; no skin site is common to all discovery labs. `HRinst` has no usable terminal round in lab 1 and `HRave` none in lab 7. Confirmation labs 2/4/6/8 remain unopened.

## Project-level assessment

There is **no independently confirmed new domain-science claim**. Do not convert this adaptive C001–C014 case series into a population estimate of AI discovery success/failure.

The well-supported contribution is methodological: treating the research agent as an **uncalibrated scientific instrument** and using explicit gates that repeatedly changed whether results deserved belief:

1. empirical known-null calibration;
2. known-positive/power calibration;
3. model/applicability checks distinct from estimator output;
4. exact-discriminator prior-art search;
5. decisive-observable and measurement-semantic checks;
6. source-level discovery/confirmation access guards;
7. replication at the true independent unit;
8. deterministic reruns and independent verification;
9. explicit stop rules that preserve nulls/failures.

See `PROJECT-REASSESSMENT.md`.

## SciPy direction

Recommended proposition: **How do you calibrate an AI scientist?**

Use C001, C002 and C003 as three scientific failure modes and C012 as a compact live semantic/calibration gate. This is a scientific-computing/open-science talk, not a claim that AI cannot discover science.

True domain novelty remains a separate unresolved goal. Pursue it only via a targeted collaborator's under-analysed replicated dataset or a prospective experiment in which the decisive observable is collected by design. Do **not** resume broad public-archive scouting in this repo.

## Three-step assessment

1. **Does continued broad scouting have positive expected value? No.** Four increasingly strict scouts produced no survivor, and the frozen rule required a strategy reassessment.
2. **Can the current evidence support a strong SciPy contribution? Yes.** It contains reproducible examples where calibration/gating changed conclusions, including a complete discovery-to-failed-confirmation loop.
3. **Is true new domain science solved? No.** Existing public archives repeatedly lacked the decisive observable/alignment or had already published the implied discriminator. Change evidence source, not standards.

## Exact next action

Run a **clean offline talk rehearsal**; do not search for a new scientific candidate.

1. From a clean checkout/worktree, warm only declared FOSS dependencies, then disable network for the actual rehearsal.
2. Verify the C012 live sequence end-to-end and time it:
   - inspect frozen evidence roles;
   - run `analysis/c012_calibrate.py`;
   - run `analysis/c012_semantic_gate.py` on discovery labs only;
   - show the STOP state and audit that confirmation labs 2/4/6/8 were never materialized.
3. Verify precomputed offline fallbacks (`results/c012_calibration.json`, `results/c012_semantic_gate.json`) and all result hashes.
4. Draft `CFP-DRAFT.md` from `TALK-NARRATIVE.md`: title, concise abstract, audience, three takeaways, FOSS/open-science fit, and explicit claims-not-made. Do not inflate the adaptive C001–C014 case series into a benchmark.
5. If the rehearsal exposes a demo failure, fix only the minimum talk artifact/script required. Do not build a framework.

## Ranked next actions

1. Offline rehearsal + demo timing/confirmation-access audit.
2. CFP-ready submission draft.
3. If true domain novelty is still desired, seek collaborator/prospective evidence outside this repo; no scout 005.
4. Implement `AGENT-BENCHMARK.md` only when genuinely unseen collaborator/prospective packets exist.
