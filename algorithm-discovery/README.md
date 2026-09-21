# Budget is part of the algorithm

I started this project with a fairly conventional research goal: invent a small derivative-free optimization trick that would help when every objective evaluation is expensive.

I did not find one.

Instead, four plausible mechanisms failed, a boring parameter turned out to matter more than the clever ideas, that result transferred strongly to a scientific inverse problem, and then my own preregistered held-out test refused to let me make the strongest version of the claim.

That is now the point of the project.

When an optimizer gets only **50–200 objective evaluations per dimension**, its usual operating regime can change. For differential evolution (DE), population size is not just housekeeping: it decides how much of the evaluation budget is spent creating population breadth versus how many rounds of learning the population gets to perform.

Across these experiments, a population around **2D** was often much more evaluation-efficient than a default-like **15D** population. But the size of that advantage depends strongly on the landscape. On the final held-out benchmark, 2D beat 15D on 23 of 25 problems at 50D, yet still missed the effect-size threshold I had preregistered.

So this is **not** a recommendation to make popsize=2 the new SciPy default.

The more useful principle is:

> **The evaluation budget is part of the algorithm. Tune and evaluate an optimizer in the regime in which you will actually use it.**

The project was built for a possible [SciPy India 2026](https://scipy.in/) talk and is deliberately organized as a falsification-first experimental loop rather than a polished winner-only benchmark.

## The practical problem

Suppose each objective call is a simulation that takes minutes or hours. You need to fit perhaps 5–20 continuous parameters, but you can afford only a few hundred or a few thousand simulation calls.

SciPy's [differential_evolution](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.differential_evolution.html) is attractive because it is bounded, derivative-free, robust, and easy to use. But its default population multiplier is 15. In a D-dimensional problem, that means roughly 15D population members.

Under a budget of only 50D calls, that is expensive.

For example, in 5 dimensions:

- popsize=15 evaluates 75 initial points. A 250-call budget leaves only about 175 calls, or 2.3 more population passes.
- popsize=2 evaluates 10 initial points. The same budget leaves about 240 calls, or 24 more passes.

The small population gets dramatically more opportunities to react to what it has learned. But making the population too small destroys donor diversity. One of the sharpest development results was that **D members were too few while 2D worked well**.

That suggested a finite-budget diversity-versus-generations trade-off rather than a universal "smaller is better" rule.

## Experimental rules

I wanted the work to behave more like a scientific investigation than an optimizer leaderboard.

1. **The evaluator owns the budget.** An optimizer is never trusted to count its own calls. The objective raises before any call beyond the strict budget.
2. **Use fixed-budget trajectories, not just final answers.** The main milestones are 50D, 100D and 200D evaluations.
3. **Compare against strong baselines.** These include tuned SciPy DE, [CMA-ES](https://arxiv.org/abs/1604.00772), and L-SHADE through [Modular DE](https://github.com/Dvermetten/ModDE).
4. **Separate development and confirmation.** BBOB functions and instances used for final confirmation were reserved before the later development batches.
5. **When a mechanism fails, stop tuning it.** Do not rescue it by searching thresholds until it wins.
6. **Check mechanism claims directly.** Synthetic quadratics expose true curvature; the PK problem has independently known parameters; final PK fits are re-evaluated through an independent ODE solver.
7. **Aggregate at the problem level.** Repeated generations or stochastic runs are not treated as independent scientific evidence.

The complete chronological record is in [notes.md](notes.md), with bounded checkpoints in [checkpoints](checkpoints/).

## I tried to invent a better DE operator

Four candidate mechanisms made it far enough to be implemented and tested.

| Candidate | Idea | Why it looked plausible | What happened |
|---|---|---|---|
| **PairDE** | Balance and antithetically pair DE difference donors | Reduce donor-sampling noise without extra objective calls | Rejected: no reliable improvement; 19/40 broad-development wins at 200D |
| **RejDE** | Learn geometry from rejected trial directions | Failed evaluations might reveal expensive curvature information | Rejected: the signal was real, but acting on it hurt; exact-control comparison favored the control |
| **SwitchF** | If the first quarter of a generation gets no acceptances, resample its generation-level F | Avoid spending a whole expensive generation on a bad dither draw | Rejected: early outcomes were predictive, but "predictably low yield" was not safely reallocatable |
| **CondInitDE** | Choose the smallest Halton initial population whose covariance is numerically well-conditioned | Explain and exploit the sharp failure of a D-sized population | Rejected: improved geometry did not beat fixed 2D reliably |

The mechanism failures are documented in [checkpoint 001](checkpoints/001-baseline-pairde.md), [002](checkpoints/002-rejde.md), [004](checkpoints/004-prefix-resampling.md), and [005](checkpoints/005-saturation.md).

Several other tempting directions were stopped **before** implementation because they were established prior art: covariance/eigenvector crossover, success-history parameter adaptation, population resizing, archive-backed micro-DE, DE-to-CMA hybrids, learned algorithm switching, and scale-factor local search. [references.md](references.md) contains the literature audit.

Without that novelty screen, it would have been easy to "discover" something already known.

## The useful result was hiding in the baseline

While those candidates were failing, the baseline moved.

The first SciPy DE comparison used population sizes like 5D and 10D. Under a strict 200D budget, 5D was already much better than 10D.

Then I tested smaller populations.

On the development tuning slice at 200D:

| Configuration | Median log10 error |
|---|---:|
| SciPy DE, population D | +0.996 |
| **SciPy DE, population 2D** | **+0.051** |
| CMA-ES | +0.187 |
| L-SHADE, initial population 2D | +0.093 |
| L-SHADE, initial population 4D | +0.064 |

So D was clearly too small, but 2D was unexpectedly strong.

On the broader development set, moving SciPy from the earlier 5D population to 2D beat the old setting on **34/40 problem units**. L-SHADE also preferred a much smaller initial population in this low-budget regime.

This was not a new algorithm. It was a correction to the operating assumptions under which the algorithms were being compared.

[Checkpoint 003](checkpoints/003-geometry-budget.md) and [005](checkpoints/005-saturation.md) contain the full development evidence.

## Why 2D is plausible — but not magic

A DE population has to do two jobs:

- provide enough diverse points to create useful difference vectors;
- leave enough budget for repeated selection and adaptation.

A D-point population is especially fragile. After centering, D points in D dimensions have affine rank at most D−1. D+1 points restore full rank, but the initial design can still be badly conditioned.

For 10-dimensional scrambled Halton designs, the median condition number of the centered sample covariance was roughly:

| Points | Population | Median condition number |
|---|---:|---:|
| 11 | 1.1D | ~610 |
| 15 | 1.5D | ~40 |
| 18 | 1.8D | ~20 |
| 20 | 2D | ~15 |

That explains part of the cliff between D and 2D.

But the failed CondInitDE experiment showed why this is not the whole story: choosing population size from initial design conditioning alone did not produce a better optimizer.

The correct conclusion is weaker and more useful: **the budget creates a real diversity-versus-generations trade-off, and conventional population sizes can sit on the wrong side of it.**

## Independent transfer: fitting a pharmacokinetic model

BBOB alone was not enough. A benchmark-specific population trick would not make a good scientific result.

So I froze an independent inverse problem: fit five parameters of a standard oral two-compartment pharmacokinetic model:

- absorption rate ka
- clearance CL
- central volume Vc
- intercompartmental clearance Q
- peripheral volume Vp

A 100 mg oral dose is observed at 15 time points from 0.25 to 48 hours. Eight synthetic subjects were generated before optimizer comparison, with known true parameters inside bounded log-scaled search ranges.

The protocol is machine-readable in [results/pk-protocol.json](results/pk-protocol.json).

The fast objective uses the exact matrix exponential of the linear ODE system. Before optimization it was independently checked against SciPy [solve_ivp](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html): the worst relative concentration disagreement across 16 parameter settings was about **1.1×10⁻¹¹**.

After optimization, all **144** final primary and ablation fits were independently re-evaluated through solve_ivp. The largest objective difference was only **2.7×10⁻¹³** absolute.

### The population effect transferred strongly

Median log10 fitting objective across 24 runs per algorithm:

| Algorithm | 50D | 100D | 200D |
|---|---:|---:|---:|
| SciPy DE, p15 | -1.912 | -2.267 | -3.058 |
| **SciPy DE, p2** | **-3.261** | -4.713 | -6.052 |
| L-SHADE, p2 | -2.749 | -3.928 | -6.093 |
| CMA-ES | -2.604 | **-4.786** | **-10.618** |

At the subject level, SciPy p2 beat p15 on **8/8 subjects at all three budgets**.

Its mean log10 advantage was:

- **+1.32 decades at 50D**
- **+2.45 at 100D**
- **+3.13 at 200D**

A frozen 2×2 ablation separated population size from initialization. With **Latin hypercube held fixed**, p2 beat p15 on all 8 subjects by +1.32, +1.98 and +3.07 mean decades at 50D/100D/200D. With **Halton held fixed**, the result was similarly large. Halton-versus-LHS differences were small and inconsistent.

So the transfer was fundamentally a population-size / number-of-generations result, not a low-discrepancy-initialization trick.

### Budget changed which optimizer looked best

On the PK problem, SciPy p2 was especially strong early:

- versus CMA at 50D: **+0.62 mean decades**, 6/8 subject wins;
- at 100D: roughly tied;
- at 200D: CMA won all 8 subjects by about **4 mean decades**.

The target-hitting view says the same thing. To reach objective ≤1e−4:

| Algorithm | Successes | Median evaluations/D among successes |
|---|---:|---:|
| **SciPy p2** | 22/24 | **70.7D** |
| CMA-ES | 21/24 | 84.8D |
| L-SHADE p2 | 24/24 | 101.0D |
| SciPy p15 | 1/24 | 188.4D |

But for much deeper convergence, CMA became dominant.

The full transfer analysis is in [checkpoint 006](checkpoints/006-pk-transfer.md); running analyze_pk_transfer.py regenerates the ignored derived JSON summary from the tracked primary ledgers.

## A scientific trap: fit quality is not parameter recovery

The PK experiment also exposed a second issue.

The local Gauss–Newton condition number of the eight synthetic inverse problems ranged from about **55 to 3.9 million**. Some subjects were extremely sloppy: many different parameter vectors produced nearly indistinguishable concentration curves.

On the most ill-conditioned subject, the strong optimizers reached roughly 1e−6 objective errors while still having around 4–5% parameter error.

A deeper scalar objective is therefore not automatically a better scientific answer.

When synthetic truth exists, report parameter recovery as well as fit error.

The sensitivity analysis is in [pk_sensitivity.py](pk_sensitivity.py); its JSON output is generated locally and ignored.

## Then the held-out confirmation said "not so fast"

After the PK transfer, I froze a stronger claim for untouched 20D BBOB problems.

Before looking at their performance, I committed this pass criterion:

> At both 50D and 100D, SciPy p2 must beat p15 by at least **0.5 log10 decades median**, and must win at least **70%** of the 25 function×instance problem units.

The frozen protocol is [results/confirmation-protocol.json](results/confirmation-protocol.json).

The result:

| Budget | Median p2 advantage | Wins | Preregistered result |
|---|---:|---:|---|
| 50D | **+0.349 decades** | 23/25 | **FAIL** — required +0.500 |
| 100D | +0.537 | 23/25 | PASS |
| 200D | +0.904 | 23/25 | descriptive only |

So the confirmation **failed**.

That is not because the direction disappeared. p2 won 92% of the held-out problem units. It failed because the typical effect at 50D was smaller than the effect size I had committed to.

The landscape breakdown explains why:

| BBOB function | Median p2 advantage at 50D |
|---|---:|
| f2 | +1.59 |
| f7 | +0.40 |
| f11 | +0.21 |
| f16 | +0.04 |
| f21 | +0.56 |

The population-size effect is broad, but not uniformly dramatic.

[Checkpoint 007](checkpoints/007-confirmation.md) records the exact frozen outcome, including a procedural caveat: one reserved case was used for a budget-accounting smoke test before the confirmation run. No performance value was saved or inspected, and the criterion/configuration had already been frozen, but the reserve was technically executed. I therefore describe the confirmation as **performance-unseen, not perfectly pristine**.

### The CMA crossover also failed to generalize

The PK result suggested a neat story: tiny DE early, CMA late.

The held-out 20D BBOB set did not support that as a universal pattern.

SciPy p2 versus CMA had median advantages of approximately:

- −0.002 decades at 50D
- −0.009 at 100D
- +0.054 at 200D

Essentially tied.

L-SHADE p2 was also competitive and became stronger than plain SciPy p2 at later budgets.

So the data do not support a single universally best method or a single universal switch point.

## What I would actually claim

I would **not** claim:

- popsize=2 should replace SciPy's default;
- tiny DE always beats CMA early;
- the held-out confirmation succeeded;
- a new DE algorithm was invented.

I would claim:

> **Under very tight objective-evaluation budgets, DE population size is a first-order design variable. Conventional large populations can spend too much of the budget on breadth and too little on iterative learning. Around 2D members was broadly effective in these experiments, but the effect size is landscape-dependent and adaptive DE/CMA remain essential baselines.**

That statement survived much more scrutiny than any of the clever mechanisms did.

## The SciPy India talk

The talk is now less about an optimizer and more about **doing computational research live**.

A useful narrative is:

1. **Start with an invention goal.** Can an AI-assisted research loop invent a better compact optimizer for expensive scientific fitting?
2. **Show attractive wrong ideas.** Four mechanisms had plausible stories and measurable intermediate signals. All four failed.
3. **Let the baseline embarrass the inventions.** Population size mattered more than the clever operators.
4. **Transfer outside the benchmark.** The effect became much larger on a pharmacokinetic inverse problem.
5. **Preregister a hard confirmation.** Do not move the threshold after seeing the answer.
6. **Fail the confirmation honestly.** 23/25 wins still did not meet the promised 50D effect size.
7. **End live on a fresh problem.** Make a prediction, commit it before computation, and let the result disagree with the story if it wants to.

The thesis is not "AI invented a new optimizer."

It is:

> **AI can help run a fast scientific loop, but the useful discovery often comes from the experiment that kills the attractive story.**

A compact speaker outline is in [talk-outline.md](talk-outline.md).

## Live experiment: commit before you compute

[live.py](live.py) generates a fresh shifted quadratic from audience-selected properties:

- dimension: 5, 10 or 20;
- condition number;
- rotated or axis-aligned;
- a fresh audience-selected seed.

It compares the four frozen methods:

- SciPy DE p15;
- SciPy DE p2;
- L-SHADE p2;
- CMA-ES.

Before the **first objective call**, the script writes the problem settings, algorithms, budget and spoken prediction to an append-only JSONL log, flushes it to disk, and prints a SHA-256 commitment.

It refuses to reuse an already logged problem unless --allow-repeat is explicitly passed for rehearsal.

Then it reveals equal-budget errors at 50D, 100D and 200D. No method is encoded as the expected winner.

Example:

    uv run python live.py \
      --dimension 10 \
      --condition 10000 \
      --rotated \
      --seed 314159 \
      --budget-d 200 \
      --prediction "I expect the large population to waste too much budget, but I do not know whether p2, L-SHADE, or CMA will win."

The default live log is outside Git at:

    ~/.cache/algorithm-discovery/live-runs.jsonl

A rehearsal already produced a useful warning against overconfidence: on one fresh 5D rotated condition-100 problem, **CMA beat p2 at 50D**.

That is exactly what the live experiment should be capable of doing.

## Reproduce the research

Set up and run all tests:

    cd ~/code/research/algorithm-discovery
    uv sync
    uv run python -m unittest -v

Recompute the development summary:

    uv run python analyze.py

Recompute the PK analyses from their append-only ledgers:

    uv run python analyze_pk_transfer.py
    uv run python pk_sensitivity.py

Recompute the frozen confirmation analysis:

    uv run python analyze_confirmation.py

The confirmation runner is intentionally separate:

    uv run python confirm_bbob.py

Do **not** use confirmation results for further parameter tuning.

## Where the evidence lives

The most useful entry points are:

- [STATE.md](STATE.md) — current scientific state and guardrails.
- [notes.md](notes.md) — chronological research log.
- [references.md](references.md) — literature and novelty audit.
- [checkpoints/007-confirmation.md](checkpoints/007-confirmation.md) — final held-out result and exact failed criterion.
- [results/runs.csv](results/runs.csv) — primary append-only development ledger.
- [results/pk-protocol.json](results/pk-protocol.json) — frozen scientific-transfer protocol.
- [results/pk-runs.csv](results/pk-runs.csv) and [results/pk-ablation.csv](results/pk-ablation.csv) — primary PK evidence ledgers.
- [results/confirmation-protocol.json](results/confirmation-protocol.json) — frozen held-out criterion.
- [results/confirmation-runs.csv](results/confirmation-runs.csv) — primary held-out evidence ledger.
- Derived JSON summaries and diagnostic CSVs are intentionally ignored and can be regenerated by the analysis scripts.

The code is deliberately small enough to read:

- [bench.py](bench.py) — strict-budget BBOB harness and baseline wrappers.
- [candidate.py](candidate.py) — the rejected candidate mechanisms.
- [pk_transfer.py](pk_transfer.py) — pharmacokinetic inverse problem.
- [live.py](live.py) — fresh audience-selected, prediction-first live experiment.

## Final lesson

The original question was:

> Can we invent a better DE mechanism for expensive optimization?

The useful answer was:

> Not yet. But we found a regime where a parameter people often treat as secondary changes the result by orders of magnitude, we showed that it transfers to a scientific fitting problem, and then a held-out test stopped us from turning that into an overly simple rule.

That is a better scientific result than a benchmark win I had to tune until it appeared.
