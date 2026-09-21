# Checkpoint 008 — talk-ready research package

Date: 2026-09-20
Status: research loop closed; no further optimizer tuning planned.

## Final scientific position

The project did not produce a new derivative-free optimizer.

It produced a more defensible result:

- four plausible DE mechanisms were implemented and falsified;
- strict low-budget baseline work showed population size was a first-order variable;
- around 2D population members was dramatically more efficient than default-like 15D on the independent 5-parameter PK fitting problem;
- the PK ablation showed population size, not Halton initialization, dominated the effect;
- a frozen 20D BBOB confirmation reproduced the direction broadly (23/25 wins) but failed the preregistered 50D median effect-size threshold (+0.349 versus required +0.500);
- the attractive PK story "tiny DE early, CMA late" did not generalize to the held-out 20D set;
- therefore neither p2 nor a DE-to-CMA switch is presented as a universal recommendation.

The final claim is deliberately narrower:

> Under very tight objective-evaluation budgets, DE population size is a first-order design variable. Conventional large populations can spend too much of the budget on breadth and too little on iterative learning. Around 2D members was broadly effective in these experiments, but the effect size is landscape-dependent and adaptive DE/CMA remain essential baselines.

## Article

README.md is now the main research article. It tells the story in experimental order:

1. expensive-evaluation motivation;
2. falsification rules;
3. four rejected mechanisms;
4. discovery of the population/generation trade-off;
5. independent pharmacokinetic transfer;
6. objective-versus-parameter-recovery caveat;
7. preregistered confirmation failure;
8. defensible claim;
9. live experiment and reproduction.

The failed confirmation and the reserve smoke-test caveat remain visible rather than being edited out.

## Talk thesis

The talk thesis is:

> Budget is part of the algorithm. AI can accelerate the scientific loop, but the valuable result may be the experiment that kills the clever story.

talk-outline.md gives an approximately 34–37 minute narrative before questions/live variability.

## Live experiment

live.py was rewritten around the final scientific conclusion rather than the rejected candidates.

Audience-selected inputs:
- dimension 5/10/20;
- condition number;
- rotated or axis-aligned;
- fresh seed.

Frozen methods:
- SciPy DE p15;
- SciPy DE p2;
- L-SHADE p2;
- CMA-ES.

Before the first objective evaluation, the script:
1. appends problem settings, algorithm list, budget, and spoken prediction to a JSONL log;
2. fsyncs the record;
3. prints a SHA-256 commitment.

It rejects an already logged problem by default. The allow-repeat flag exists only for rehearsal.

The reveal shows equal-budget errors at 50D/100D/200D and names each milestone winner.

A plumbing rehearsal on a fresh 5D rotated condition-100 quadratic was intentionally not used as evidence. It was still useful: CMA, not p2, won at 50D, demonstrating that the live harness is capable of contradicting an over-simple p2 story.

## Verification

Final package checks:
- README local links resolve.
- PK analyses regenerate from append-only ledgers.
- confirmation analysis regenerates the frozen failure.
- all unit tests pass.
- live prediction persistence and duplicate-problem rejection are unit tested.
- no live rehearsal record is stored in Git; default live logs live under ~/.cache/algorithm-discovery/.
- no further confirmation result is used for tuning.

## End condition

The algorithm-search loop is closed.

Further work should be talk preparation, visualization, or a genuinely new preregistered research question — not another parameter tweak against the existing development/confirmation data.
