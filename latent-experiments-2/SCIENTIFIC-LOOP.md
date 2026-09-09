# Scientific loop: make a research agent earn belief

This is a small, falsification-first protocol for agent-assisted science. It is not a framework and does not assume the agent is trustworthy.

The central rule is simple:

> Treat the research agent like an uncalibrated scientific instrument. Calibrate the analysis, verify the measurement semantics, reserve independent evidence, and stop when a gate fails.

## The loop

### 0. Start from a consequential discrepancy

Write down, before data exploration:

- the observation or disagreement;
- who cares and what decision would change;
- explanation A and explanation B;
- the cheapest observable that would distinguish them.

Reject the candidate immediately if the exact discriminating experiment is already published, or if the decisive observable is not measured directly enough to distinguish A/B.

### 1. Freeze evidence roles before outcomes

Use source-level units whenever possible: independent experiment, batch, animal, device, site, laboratory or ecosystem. Do not call an arbitrary row split “confirmation.”

Declare:

- discovery source(s);
- confirmation source(s);
- controls/negative controls;
- true independent unit;
- what may be opened at each stage.

Public data are only a **procedural holdout**. A hash proves file identity, not blinding. If secrecy matters, a trusted evaluator must hold the confirmation data.

### 2. Check measurement semantics before effect values

Inspect documentation, schema, identifiers, units, missingness and sampling structure first.

Stop if:

- the same column name means different biological/physical quantities across sources;
- the confirmation source aggregates away the required analysis unit;
- observation opportunities differ incoherently;
- independent confirmation units are too few;
- choosing among ambiguous samples would require seeing outcomes.

### 3. Calibrate the proposed analysis

Before substantive discovery outcomes, test both:

**Known null.** Generate or identify data where the claim should not fire while preserving clustering, covariance, missingness and measurement structure as far as practical.

**Known positive.** Inject a scientifically meaningful effect and verify usable power.

Also test the model's **applicability**, separately from whether its estimator returns a number.

Reject or redesign the analysis if:

- empirical false-positive rate is unacceptable;
- meaningful injected effects are undetectable;
- a real same-condition/technical null triggers the detector;
- model-fit/applicability checks fail.

Do not tune repeatedly against confirmation evidence.

### 4. Run discovery once under the frozen rule

Record every committed primary and sensitivity test, including null results.

If discovery fails, stop. Do not search nearby outcomes, thresholds or sources to rescue the same claim.

If discovery passes, freeze the confirmation rule **before** confirmation access:

- eligibility;
- estimand;
- test/model;
- effect threshold;
- multiplicity handling;
- aggregate study-level rule;
- allowed sensitivities;
- exact stop/confirm decision.

### 5. Spend confirmation evidence once

Run every committed confirmation test unchanged.

A failed confirmation stays failed. A new mechanism, null, subgroup or source is a **new investigation requiring fresh evidence**, not a continuation of the old one.

### 6. Verify independently

At minimum:

- hash every load-bearing input/result;
- rerun stochastic outputs with fixed seeds and require deterministic equality when expected;
- parse all claim/ledger records;
- reproduce the main statistic by a materially different calculation where practical;
- audit that held-out evidence was not opened early.

### 7. Preserve the stop

The durable output is not only a positive claim. Record why the path stopped and what narrower lesson survived.

A scientifically useful stop often has the form:

> “This statistic looked compelling under the nominal analysis, but the empirical null/model/measurement/confirmation gate shows it does not justify the proposed interpretation.”

## Minimal claim specification

```json
{
  "claim_id": "CXXX",
  "question": "What exact claim is being tested?",
  "competing_explanations": {
    "A": "...",
    "B": "..."
  },
  "decisive_observable": "What measurement distinguishes A from B?",
  "unit_of_independence": "animal/site/device/lab/...",
  "evidence_roles": {
    "discovery": ["source_A"],
    "confirmation": ["source_B"],
    "control": ["optional_source_C"]
  },
  "estimand": "...",
  "analysis": "...",
  "decision_rule": "...",
  "calibration": {
    "known_null": "...",
    "known_positive": "...",
    "acceptance": "..."
  },
  "access_state": {
    "discovery_outcomes": "not_accessed",
    "confirmation_outcomes": "not_accessed"
  },
  "stop_conditions": [
    "exact discriminator already published",
    "decisive observable absent or incompatible",
    "known-null calibration fails",
    "model applicability fails",
    "discovery rule fails",
    "confirmation rule fails"
  ]
}
```

The specification should stay small enough to review manually. Add domain-specific fields only when they change interpretation or access control.

## Minimal access ledger

Append-only JSONL is sufficient:

```json
{"event":"role_freeze","claim_id":"CXXX","discovery":["A"],"confirmation":["B"],"date":"YYYY-MM-DD"}
{"event":"metadata_access","claim_id":"CXXX","source":"A","outcomes_accessed":false,"sha256":"..."}
{"event":"calibration_result","claim_id":"CXXX","null_fpr":0.02,"power":0.87,"pass":true,"sha256":"..."}
{"event":"discovery_access","claim_id":"CXXX","source":"A","sha256":"..."}
{"event":"confirmation_freeze","claim_id":"CXXX","rule":"..."}
{"event":"confirmation_access","claim_id":"CXXX","source":"B","sha256":"..."}
{"event":"candidate_stop","claim_id":"CXXX","stage":"after_failed_confirmation","reason":"..."}
```

The ledger answers a critical question that prose cannot: **what did the agent know when it made each decision?**

## Calibration checklist

Before discovery outcomes:

- [ ] exact discriminator searched in prior literature;
- [ ] decisive observable exists and is not the disputed proxy itself;
- [ ] independent unit identified;
- [ ] discovery/confirmation sources frozen;
- [ ] measurement units and missing-value semantics checked;
- [ ] known-null false-positive behavior tested;
- [ ] known-positive effect/power tested;
- [ ] clustering/covariance/missingness preserved in calibration where feasible;
- [ ] model applicability gate defined;
- [ ] primary/sensitivity/multiplicity rules frozen;
- [ ] stop condition written before confirmation access.

## Three examples from this project

### C001: empirical null beats an attractive p-value

A cross-assay TEM-1 residual statistic was highly significant under residual permutation. But five **same-condition technical replicate pairs** also triggered that null, and the cross-study position structure was no larger than replicate structure. The detector failed calibration, so reserved confirmation was never opened.

Lesson: a nominal null is not trustworthy merely because it is mathematically convenient.

### C003: discovery is allowed to fail confirmation

Two of three German steppe plots showed extra temporal organization beyond a constraint-preserving Taylor-law null. The confirmation rule was frozen, then a separate Danish heath dataset produced **0/5** passing plots. The result stayed failed.

Lesson: the workflow must make a positive discovery easy to kill with independent evidence.

### C012: statistical calibration cannot rescue incompatible measurements

A synthetic multi-lab calibration first showed that participant-dominated inverse-variance pooling was anti-conservative. Treating **laboratory as the replication unit** fixed the false-positive behavior. Then a schema/missingness audit showed the discovery laboratories did not actually share an anatomically comparable skin-temperature variable, nor a consistently observed common heart-rate variable. The candidate stopped before any hue-effect estimate.

Lesson: calibration has layers. A statistically valid test of the wrong cross-source quantity is still invalid science.

## What this protocol does not establish

It does not prove that an AI agent selects scientifically valuable questions better than humans or simple baselines. That requires a separate prospective benchmark with genuinely withheld confirmation evidence. See `AGENT-BENCHMARK.md`.
