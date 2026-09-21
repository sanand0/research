# STATE

Checkpoint: checkpoints/009-robustness-plan.md
Previous optimization discovery loop: closed after Batch 8.
New research phase: population-size robustness study.
Robustness outcomes run so far: none.

## Research question

How general is the low-budget DE population-size effect, and where does it fail?

Keep two claims separate:

- **Claim A — importance:** under tight objective-evaluation budgets, population size is a first-order performance variable.
- **Claim B — p2 robustness:** a population around 2D is a broadly useful low-budget operating point.

Claim A may survive even if Claim B fails.

The full frozen plan is in checkpoints/009-robustness-plan.md.

## Guardrails from the completed study

Do not tune against the old Batch-7 confirmation data.

Do not assume p2 is the winner.

The new robustness study must actively search for failure segments:
- multimodality / weak global structure;
- noise;
- higher dimension;
- large budgets;
- boundary optima;
- DE strategy dependence;
- massive parallelism / one-shot evaluation;
- new scientific inverse-problem families.

Primary population grid is frozen at:

    {1D, 2D, 4D, 8D, 15D}

Primary budget grid is frozen at:

    {20D, 50D, 100D, 200D, 500D, 1000D}

Robustness metrics and thresholds are frozen in checkpoint 009.

## Next action on "Continue" — Batch 9

Run the first **noiseless population response surface**, without adding or tuning population values.

Before running:
1. Read this file and checkpoint 009.
2. Implement a separate robustness harness/ledger; do not mix new runs into the historical development or confirmation ledgers.
3. Store exploratory raw output outside Git by default, under ~/.cache/algorithm-discovery/robustness/.
4. Freeze a machine-readable Batch-9 protocol in the repo before the first objective call.
5. Use all 24 BBOB functions, fresh instances 21–22, dimensions 5 and 20, budgets 20D/50D/100D/200D/500D/1000D, populations 1D/2D/4D/8D/15D, best1bin, Latin-hypercube init, F~U(0.5,1), CR=0.7, immediate updating, and two optimizer seeds.
6. Keep F/CR/init policy fixed across population sizes.
7. Verify budget accounting and duplicate-key safety before the full run.
8. Report:
   - population importance;
   - p2 regret to cell-best;
   - p2 vs p15 advantage/win rate;
   - population response by budget and official BBOB class;
   - counterexamples where p2 meaningfully loses.
9. Do not add new populations or modify thresholds after seeing Batch 9.
10. Checkpoint the evidence and decide whether Batch 10 should proceed unchanged.

## Long-run sequence

- Batch 9: broad noiseless response surface.
- Batch 10: dimension, geometry, strategy interactions.
- Batch 11: explicit failure modes — noise, multimodality, boundaries, large budgets, parallelism.
- Batch 12: interpretable segment discovery; freeze at most three failure rules.
- Batch 13: three new scientific inverse-problem families.
- Batch 14: fresh-instance/fresh-family confirmation.

No separately billed model APIs should be required.
