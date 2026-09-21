# Research notes

## 2026-09-10 — framing

Question: under strict finite objective-evaluation budgets, can a compact DE strategy improve useful target-hitting efficiency on bounded continuous problems (roughly 5–20D), while remaining usable through `scipy.optimize.differential_evolution(strategy=...)` or a small public-API wrapper?

False victories to avoid: (1) beating only SciPy defaults instead of tuned DE; (2) tuning on all BBOB functions/instances then calling transfer "confirmation"; (3) improving final error while silently using more objective calls, initialization, polish, or restarts.

Development scope for the pilot: noiseless BBOB, dimensions 5 and 10, strict budget 200D, with trace points at 20D/50D/100D/200D. Pilot functions are 1,3,6,8,10,12,15,17,20,23 (two from each broad BBOB group), instances 1–2. Hold out functions 2,7,11,16,21 plus instances 11–15 and 20D for confirmation. Public knowledge of BBOB is not blinding; the holdout is only protection against direct adaptive search on those cases.

Metrics: best error `f_best - f_opt` at fixed budgets; evaluations to target errors 1e-2 and 1e-5; success by 200D; wall time and objective-call time separately; strict objective-call count from the evaluator itself.

Literature anchors checked before coding:
- SciPy 1.18 docs: callable DE strategy has access to candidate index, population, and RNG; no fitness array. Built-ins include best/rand/current-to-best families. No-polish nominal evaluation count is `(maxiter+1)*popsize*(N-N_equal)`.
- COCO/BBOB: 24 noiseless scalable functions, standard fixed-target runtime is objective evaluations; expensive-optimization analyses use runlength-style budgets.
- JADE/SHADE/L-SHADE: current-to-pbest, archive, success-history adaptation; L-SHADE adds deterministic linear population reduction, explicitly trading exploration for faster convergence.
- CMA-ES: adapts full covariance and step size; a strong contrasting baseline where rotational invariance/geometry learning matter.
- LLaMEA: algorithm-generation loop demonstrated BBOB gains in 5D and transfer to 10D/20D, but algorithm search on a benchmark does not itself establish novelty or unbiased generalization.

Novelty standard: a new trigger/operator/sampling mechanism is structural; recombining known pieces is a useful combination; changing constants/schedules is tuning; independently arriving at an existing operator is rediscovery.

Initial structurally different ideas (pre-results):
1. **Balanced-antithetic donor scheduling.** Standard DE samples donor differences independently. Under small populations/few generations this can repeatedly use some directions while missing their opposites. Schedule donor pairs so usage is balanced and pair directions with their negatives across candidates. Prediction: lower run-to-run variance and better finite-budget progress; advantage should shrink with large budgets. Risk: correlations reduce useful randomness.
2. **Effective-rank thermostat.** Estimate population covariance effective rank. When rank collapses, reduce attraction to the best and enlarge differential steps; when rank is healthy, exploit more. Prediction: helps premature-collapse failures without global restarts. Risk: geometry-only rank is not evidence that the population is in the wrong basin; diversity rescue can waste evaluations on easy unimodal cases.
3. **Stagnation-triggered micro-rejuvenation.** Detect no movement of SciPy's best member plus population contraction; replace only occasional proposals with bounded reflected or low-discrepancy probes. Prediction: improves weak-global-structure multimodal cases at low evaluation cost. Risk: late useful contraction can be mistaken for stagnation.

A fourth diagnostic candidate is PCA-basis crossover, but eigenvector crossover is already established in DE literature/software and therefore would be a rediscovery/benchmark probe, not a novelty claim.

## Engineering evidence

`modde==0.0.4` requires Python 3.12 here; its dynamic parameter machinery fails under Python 3.14. More importantly, a nominal `budget=500` L-SHADE-style run executed 515 IOH evaluations because the implementation checks the budget only after a whole generation. The benchmark harness must therefore enforce the budget at the objective boundary and treat optimizer-internal counters as advisory only.

A source audit of modDE found benchmark metadata used only for dimensionality and `state.optimum_found`; no problem ID/name or hidden optimum is used to select behavior.

## 2026-09-10 — batch 1 results

### Scientific progress

Baseline tuning used BBOB functions 1,6,10,15,20, instance 1, dimensions 5/10, seeds 1/2, strict 200D budget. The selection criterion was performance across 50D/100D/200D rather than final error alone. The low-budget regime strongly favored small populations: SciPy popsize=5 beat popsize=10; modDE's L-SHADE modules with initial population 6D beat 10D and canonical 18D. This is parameter tuning, not an algorithm contribution.

Selected development baselines after tuning:
- SciPy `best1bin`, popsize 5, Halton init, immediate updating.
- pycma CMA-ES, initial sigma 0.30 of box width, default population.
- modDE L-SHADE modules with initial population 6D, otherwise the published modular recreation settings (target-to-pbest, SHADE F/CR adaptation, archive, LPSR; default saturation boundary handling). This is a tuned L-SHADE configuration, not canonical L-SHADE because the initial population was changed from 18D to 6D for the 200D regime.

On the broader development pilot (10 functions x 2 instances x 2 dimensions x 2 seeds = 80 runs/algorithm), median log10 final errors at 200D were 0.566 for tuned SciPy, 0.187 for CMA-ES, and 0.425 for tuned modDE L-SHADE. Successes to error <=1e-2 were 7/80, 18/80, and 9/80 respectively. The largest qualitative gap is on the ill-conditioned group: median log10 final error was 3.571 (SciPy), 0.709 (CMA-ES), and 2.121 for tuned adaptive DE; covariance/geometry learning is therefore a real baseline opportunity, but generic covariance adaptation is already established work.

Candidate 1, `BalancedAntitheticBest1` (PairDE), changes only donor scheduling relative to matched deferred SciPy best/1/bin: adjacent target pairs receive the same donor difference with opposite sign, and for even populations every member is used exactly twice as a difference donor per generation. F dithering, CR, population size, initialization, crossover, and bounds are otherwise matched. This cleanly tests whether finite-budget donor-direction sampling variance is the missing mechanism.

Result: reject Candidate 1. On 40 development problem units (function x instance x dimension, first taking the median over two seeds), PairDE's mean log10 advantage over matched deferred SciPy at 200D was -0.0745 decades; 95% problem-bootstrap CI [-0.1576, 0.0001], 19 wins / 21 losses. At 50D it was also negative (-0.0935 mean decades). The mild tuning-slice hints on f10/f15 did not transfer robustly. PairDE also had 4/80 successes to 1e-2 versus 4/80 for the matched deferred baseline and 7/80 for immediate SciPy. No practical improvement threshold was met, so no confirmation data were touched.

Mechanism/novelty assessment: mirrored (antithetic) sampling and pairwise selection are established in evolution strategies, including CMA-ES, and orthogonal/mirrored variants have BBOB evidence. A targeted search did not reveal this exact balanced DE donor schedule, but even if exact scheduling were unpublished it is best classified as a transfer/useful combination of a known derandomization principle, not yet a strong new algorithmic mechanism. Its negative development result makes novelty pursuit low value.

The initial alternatives also face novelty pressure: covariance/eigen-space crossover and covariance learned from successful DE steps are established; diversity-triggered adaptive DE and restart/rejuvenation are crowded. Next exploration should therefore not be "add covariance" or "add a restart". A sharper opening is whether objective information that DE normally discards (especially evaluated rejected trials) can cheaply estimate *actionable local geometry* early enough to matter inside 50–200D. This needs a literature search before implementation, especially against active CMA and surrogate/preconditioned DE.

### Engineering progress

The evaluator owns the objective-call budget and raises before any call beyond it. Unit tests validate a known BBOB solution and exact accounting for SciPy, modDE, PairDE, and CMA-ES. Across the current ledger there were zero budget overshoots. A raw modDE run was observed to overshoot a nominal 500-call budget to 515 because its stop check happens after a generation; the wrapper prevents this.

The first modDE development rows used `expc_center` boundary correction. A later primary-implementation audit showed the published modular L-SHADE recreation leaves boundary handling at the framework default, so these rows are retained in the ledger but superseded. Correctly configured rows are named `modde-lshade-p*`; only those are used in the checkpoint comparison.

Dependencies are pinned through `pyproject.toml`/`uv.lock` and Python 3.12 because modDE 0.0.4's dynamic parameter machinery fails under Python 3.14 in this environment. The experimental ledger is append-only/resumable and each row records config, NFE, target hits, milestones, objective time, wall time, and optimizer overhead.

Total so far: 820 ledger rows after the corrected adaptive-DE reruns, 1.23M objective evaluations. Recorded optimizer wall time is well below the 30 CPU-minute first-batch ceiling; no separately billed model API was used.

## Batch 2 — rejected-trial geometry / RejDE

### Scientific progress

- Novelty screen found that generic failure information, negative covariance updates, direct Hessian estimation, covariance/eigen-coordinate DE, directional mutation, and per-dimension crossover adaptation are all prior art. Narrowed Candidate 2 to a transfer hypothesis rather than a novelty claim: remove DE's existing proposal anisotropy, then use rejection overrepresentation in whitened coordinates to contract directions for the next generation.
- Mechanism probe on fresh quadratics (d=5,10; conditions 1,100,1e4; rotated/unrotated; 20 seeds; 100D) found an unexpected result: raw rejected-step covariance is anti-correlated with Hessian curvature because DE proposals already contour-fit soft directions.
- Proposal covariance is highly informative: inverse proposal covariance vs true Hessian has median directional Spearman ~0.78/0.94 at condition 100 rotated/axis-aligned and ~0.74/0.94 at condition 1e4. This suggests DE already learns much of the relevant shape before any explicit covariance model.
- After proposal whitening, rejection-vs-proposal contrast has incremental Hessian signal only on rotated conditioned quadratics (median Spearman ~+0.45 at condition 100 and +0.54 at 1e4); it is misleading on axis-aligned conditioned cases (~-0.39).
- Implemented RejDE: one-generation rejection whitening/correction, determinant-normalized, identity-prior regularized, zero extra objective calls, via SciPy public custom-strategy + vectorized-objective APIs.
- Small tuning slice: RejDE vs built-in matched-deferred SciPy median advantage -0.067 decades, 6/20 wins. No tuning performed.
- Broader development: RejDE vs built-in deferred SciPy at 200D: mean -0.043 decades, median -0.051, 17/40 problem-unit wins; mean bootstrap 95% CI [-0.125,+0.035].
- Added exact mechanism-off control through the identical custom strategy/vectorized path. RejDE vs this control: mean -0.063 decades, median -0.059, 15/40 wins; mean bootstrap 95% CI [-0.141,+0.012]. This rejects the active correction itself, not merely wrapper/RNG differences.
- Synthetic matched on/off test (fresh quadratics, 200D, 10 problem units per condition/rotation): only condition 100 rotated was mildly positive (+0.092 mean decades, 7/10 wins; uncertainty crosses zero). Condition 1e4 rotated was essentially null (-0.046 mean, +0.006 median), and sphere/axis-aligned cases frequently regressed.
- Decision: reject RejDE; do not tune or touch confirmation reserve. Main lesson: the useful headroom is unlikely to be obtained by another generic covariance learner. Diagnose why DE fails to exploit geometry it already has.

### Engineering progress

- Added `geometry_probe.py`, `synthetic_compare.py`, `RejectionWhitenedBest1`, an exact transform-off control, and tests for transform directionality and strict objective budget.
- Fixed two non-scientific command issues without rerunning completed optimizer work: `/usr/bin/time` absent; a post-run CSV summary mixed string/int keys.

## Batch 3 — geometry loss, population budget, and headroom assessment

### Scientific progress

- The strongest Batch-2 hypothesis was confirmed mechanistically: on conditioned quadratics the DE donor vectors contain strong inverse-Hessian geometry, and binomial crossover can destroy much of it. On rotated condition-1e4 quadratics, median inverse-covariance/Hessian directional Spearman was ~0.88 before crossover, ~0.49 after CR=0.7 crossover, and ~0.70 with CR=1. Greedy selection reduced geometry further but less than crossover. Median final synthetic error for CR=1 was ~427 versus ~1064 for CR=0.7 in this diagnostic setting.
- BBOB transfer of CR=1 was highly heterogeneous. Relative to CR=0.7 at popsize=5D, CR=1 improved f10 by ~0.90 log10 decades median and f12 by ~1.24, but regressed f1 by ~1.66 and f3 by ~0.22. Aggregate 200D mean advantage was +0.076 decades with wide problem-level uncertainty. Therefore full-vector mutation is a useful regime diagnostic, not a robust candidate.
- Targeted literature search found covariance/eigen-coordinate crossover, crossover matrices, success-history CR adaptation, population resizing, and restart mechanisms already well established. Treating CR=1, eigen-crossover, or adaptive population size as the algorithmic contribution would be rediscovery/tuning rather than invention.
- A more important baseline error was found: the initial 5D SciPy population was still too large for a strict 200D budget. On the tuning slice, popsize=2D achieved median log10 error +0.051 versus +0.681 for 5D. Broader development confirmed the effect: 2D beat 5D on 34/40 problem units, with median advantage +0.557 decades.
- Symmetric tuning changed the adaptive-DE baseline too: modDE L-SHADE with initial population 4D beat the previous 6D setting on the tuning slice and broader pilot (median 200D log-error +0.289 versus +0.425). CMA sigma=0.30 remained best among 0.10/0.20/0.30/0.50.
- Final development baselines after bounded tuning: SciPy best1bin popsize=2D Halton; CMA-ES sigma0=0.30 box width; modDE L-SHADE modules initial population=4D. Broader 80-run medians at 200D: +0.238, +0.187, +0.289 respectively; successes to 1e-2: 11/80, 18/80, 10/80; to 1e-5: 8/80, 8/80, 4/80.
- The CMA advantage over tuned 2D SciPy is now much smaller by the robust problem-unit median (~0.134 decades) but remains material in mean because CMA converges much deeper on easy/separable cases. At 5D the algorithms are essentially tied by 200D; at 10D CMA retains a clearer edge. The main remaining structured gap is moderately/strongly conditioned functions.
- Population size explains a material part of the apparent geometry gap: 2D population buys roughly 2.5x as many generations as 5D at equal budget. Therefore Batch 1's claim that the principal gap was covariance learning was too strong; both geometry preservation and generation count matter.

### Headroom decision after three batches

There is useful headroom, but the obvious mechanism space is crowded. Another covariance learner, eigen-coordinate crossover, generic CR adaptation, restart, or population resizing is unlikely to produce a defensible new contribution. Do not force Candidate 3 from these ingredients.

A narrower evaluation-efficiency mechanism remains plausible: SciPy-style dithering commits a sampled F to an entire generation. With expensive objectives, a poor generation-level parameter draw may consume NP evaluations before feedback can change it. Batch 4 should test whether outcomes from the first few trials of a generation predict the remaining trials strongly enough to justify **sequential generation truncation / early parameter resampling**. If predictive value is weak, abandon this branch. If strong, novelty-screen asynchronous/per-evaluation DE and implement a minimal candidate that aborts only demonstrably bad parameter batches without extra objective calls.

### Engineering progress

- Added `geometry_loss.py`; its first run exposed an empty-accepted-generation diagnostic edge case, which was fixed before evidence collection.
- Restored the project to Python 3.12 after a stale `.venv` caused uv to recreate under 3.13 and start rebuilding IOH.
- Added bounded tuning configurations to `bench.py`; all experimental rows remain append-only.

## Batch 4 — within-generation prediction and PrefixResample DE

### Scientific progress

- Predeclared a simple diagnostic before looking at traces: with the 2D population baseline, inspect the first quarter of a generation; zero accepted trials means the generation-level F draw is provisionally “bad.”
- Added generation_trace.py and a disjoint development split. The signal transfers: validation BBOB generation-level early-vs-late acceptance Spearman ~0.57 and AUROC ~0.75 for any later acceptance. Early and late normalized improvement are also correlated (~0.52).
- Corrected the evidence unit before interpreting the result. Across 10 BBOB validation problem units, the fixed rule would nominally save ~30% evaluations on average but discard ~21% of normalized remaining gain and ~31% of remaining accepted trials. On f23 it discards nearly as much useful gain as it saves evaluations. Therefore the signal is predictive but not cleanly actionable.
- Novelty search found dense adjacent prior art: asynchronous or steady-state DE, per-individual and success-history F/CR adaptation, strategy adaptation, and extensive expensive-optimization DE. No exact fixed-prefix revocation rule surfaced, so classify it only as a small scheduling mechanism unless stronger evidence emerges.
- Candidate 3a, abort/restart pass, failed on the tuning slice: 5/20 wins versus exact control, paired median 200D advantage -0.453 decades. No broad run.
- Candidate 3b, PrefixResampleBest1 / SwitchF, isolates the mechanism through SciPy's public callable strategy API: after a zero-success first quarter, resample F only for remaining targets. Broader development is effectively null: at 100D mean advantage +0.073 decades (21/40 wins, CI crosses zero); at 200D +0.045 mean, -0.006 median, 19/40 wins. Reject without tuning or confirmation.
- New lesson: optimizing expected immediate acceptance or yield is not enough. Low-yield trial blocks still contribute search value, so predictable waste is not necessarily reallocatable waste.
- A targeted next-idea search also found that scale-factor local search in DE is established prior art from 2009, making simple rejected-step backtracking a likely rediscovery. Batch 5 should instead novelty-screen a budget-aware DE-to-CMA handoff motivated by the observed early-DE / late-CMA complementarity.

### Engineering progress

- Added trial-level machine-readable traces and analyze_generation_trace.py.
- Added strict-budget tests for sequential abort/resample and the public-strategy SwitchF implementation.
- The environment currently runs successfully on Python 3.13; the earlier incompatibility is specifically with Python 3.14, so “Python 3.12 required” was too strong.

## Batch 5 — DE/CMA prior art, micro-population limit, CondInitDE

### Scientific progress

- Novelty-screened the proposed DE→CMA handoff before coding. Sequential DE/CMA hybrids, algorithm portfolios, learned switching times, and practical DE→CMA chaining already exist. Stopped this branch as prior-art-heavy.
- Tested the missing 1D-population baseline. SciPy p=1D collapses (+0.996 median log-error at 200D tuning) versus p=2D (+0.051), proving the finite-budget effect is a diversity/generation trade-off rather than “use the smallest population.”
- Gave adaptive DE the same opportunity. L-SHADE p0=2D transfers better than p0=4D on the broader development set (+0.197 vs +0.289 median at 200D), so the trusted adaptive-DE baseline is now p0=2D.
- Oracle analysis over SciPy-2D/L-SHADE-2D/CMA shows substantial early complementarity but little late median headroom beyond CMA: CMA is only 0.039 decades from the virtual-best median at 200D. This makes portfolio selection more obvious than a missing mutation operator, but portfolios are established work.
- The p=1D failure led to an objective-free geometry diagnostic: D points are affine-rank deficient; D+1 Halton is full-rank but badly conditioned; around 1.8–2D points are needed for reasonably conditioned initial covariance in 5–20D.
- Candidate 4 CondInitDE used the shortest Halton prefix with covariance condition <=20. Against an exact custom-Halton 2D control it wins only 7/20 pairs at 200D and is worse on average (-0.113 decades). Rejected without threshold tuning or broad pilot.
- The SciPy DIRECT exploratory command timed out after appending 30 probe rows (16 unique keys; 14 duplicate keys from the interrupted/replayed command). Median optimizer overhead was ~49 ms/evaluation, with ~993 s total wall time. These rows are excluded from scientific conclusions and preserved only for provenance; `results/ledger-audit.json` records the separation.

### Engineering progress

- Added explicit D+1/custom-2D/condition-aware SciPy initial populations via the public array-valued init API.
- Added strict-budget test for the condition-aware initializer.
- Added a DIRECT runner/test; the interrupted exploratory benchmark left 30 provenance-only rows, which are excluded from scientific analyses.

## Batch 6 — independent PK inverse-problem transfer

### Scientific progress

- Froze an oral two-compartment PK inverse problem before optimizer runs: 5 parameters (ka, CL, Vc, Q, Vp), 8 Sobol-designed synthetic subjects, 15 concentration-time observations, log-scaled parameter box, noiseless observations, 50D/100D/200D budgets, optimizer seeds 1–3.
- Fast matrix-exponential simulator independently matches solve_ivp to 1.1e-11 relative concentration error. All 144 final primary+ablation fits were re-evaluated through solve_ivp; maximum objective discrepancy was 2.7e-13 absolute.
- Primary transfer strongly confirms the tiny-population regime. SciPy p2 beats default p15 on all 8 subjects at all three budgets, by +1.32, +2.45, +3.13 mean log10 objective decades at 50D/100D/200D.
- Early-budget complementarity reproduces cleanly: SciPy p2 beats CMA at 50D by +0.624 mean decades (6/8 subjects, bootstrap CI excludes zero), is roughly tied at 100D, then loses to CMA on all 8 subjects at 200D by ~4 decades mean.
- Target hitting makes the result practical: SciPy p2 reaches objective 1e-4 in 22/24 runs at median 70.7D evaluations; CMA 21/24 at 84.8D; L-SHADE 24/24 at 101D; default p15 only 1/24.
- A 2x2 population/init ablation isolates the cause. p2 beats p15 on all subjects with either Latin hypercube or Halton, with ~1.3-3.1 decade mean advantages; Halton-vs-LHS differences are much smaller and inconsistent.
- Local PK sensitivity geometry is highly sloppy (Gauss-Newton condition ~55 to 3.9e6), but this does not explain CMA's late objective advantage. The most ill-conditioned subject demonstrates objective/parameter-identifiability divergence: ~1e-6 fit errors coexist with ~4-5% parameter error.
- Decision: the operating-regime result, not any rejected candidate, now merits frozen BBOB confirmation.

### Engineering progress

- Added pk_transfer.py, test_pk_transfer.py, pk_ablation.py, analyze_pk_transfer.py, pk_sensitivity.py.
- Added machine-readable frozen protocol, primary ledger, ablation ledger, independent simulator check, summary, problem-level analysis, and sensitivity analysis.
- Zero PK budget overshoots.

## Batch 7 — frozen BBOB confirmation

- Frozen confirmation ran 200 held-out runs: 5 functions × 5 instances × 20D × 2 seeds × 4 algorithms, all at strict 200D with 50D/100D/200D milestones.
- Preregistered primary criterion failed narrowly. p2 vs p15 at 50D: +0.349 median log10 advantage, 23/25 wins; required median was >=+0.500. At 100D it passes: +0.537 median, 23/25 wins. No threshold adjustment or retuning.
- Direction is broad but magnitude heterogeneous: f2 and f21 benefit strongly; f11 is modest; f16 is almost neutral.
- Secondary crossover did not reproduce: p2 and CMA are essentially tied at 50D/100D/200D on the held-out 20D set.
- L-SHADE p2 is comparable to p2 early and stronger at 100D/200D, supporting "tiny population matters" more than "plain SciPy p2 is best."
- Procedural caveat: the strict-budget confirmation-config smoke test executed f2/instance11/20D before the confirmation ledger run. It inspected only evaluation accounting, not performance, and settings/criterion were already frozen in checkpoint 006; nevertheless the reserve was technically touched. Test moved to f1/instance1/5D for future runs.
- Talk direction changes: center the falsification/preregistration story and the budget/population trade-off, not a universal p2 recommendation.

## Batch 8 — article, talk story, and prediction-first live experiment

- Stopped optimizer tuning completely.
- Rewrote README.md as the primary research article. The narrative keeps the four failed mechanisms, the population-size baseline correction, PK transfer, identifiability caveat, and failed preregistered confirmation in the main flow.
- Wrote talk-outline.md around the thesis: "Budget is part of the algorithm. AI can accelerate the scientific loop, but the valuable result may be the experiment that kills the clever story."
- Rebuilt live.py around the four frozen methods (SciPy p15, SciPy p2, L-SHADE p2, CMA) rather than rejected candidates.
- live.py now durably logs the spoken prediction/problem before the first objective call, fsyncs it, prints a SHA-256 commitment, and rejects exact problem reuse unless allow-repeat is explicitly supplied for rehearsal.
- Live reveal reports equal-budget errors at 50D/100D/200D. A rehearsal on a fresh 5D rotated condition-100 problem had CMA beating p2 at 50D, confirming that the demo can contradict the simplest story.
- Added test_live.py. Full suite passes 21/21.
- Audited README local links; no broken local references.
- Regenerated PK and confirmation analyses; key values are unchanged.
- Project is ready for a clean monorepo commit. No further optimization experiments are planned.

## Batch 9 planning — robustness map, before any new outcomes

- Reopened the project with a new question: not "does p2 win again?" but "how general is the population-size effect, and where does it fail?"
- Split the claim explicitly:
  - Claim A: population size is a first-order variable under tight budgets.
  - Claim B: around 2D is a robust low-budget operating point.
  Claim A may survive even if Claim B fails.
- Froze the primary population grid {1D,2D,4D,8D,15D}, budget grid {20D,50D,100D,200D,500D,1000D}, and descriptive robustness thresholds before new runs.
- Predefined generalization/failure axes: budget, dimension, BBOB landscape class, rotation/conditioning, noise, optimum near boundaries, DE strategy, parallelism/one-shot evaluation, and new scientific inverse-problem families.
- Batch 9 is frozen as a 5,760-run noiseless response surface on all 24 BBOB functions, fresh instances 21–22, D={5,20}, best1bin, LHS init, F~U(0.5,1), CR=0.7, immediate updating, two seeds.
- Later phases deliberately target likely failures: noise, weak-global-structure multimodality, high dimension, abundant budget, boundaries, strategy dependence, and massive parallelism.
- Scientific transfer families are preselected as Lotka–Volterra, SEIR, and 1D heat/diffusion. FitzHugh–Nagumo is preselected now as the untouched scientific confirmation family.
- Final confirmation criteria are frozen separately for "population matters" and "p2 is robust"; p2 is allowed to fail while the broader population-size insight survives.
- Repository hygiene changed at the same checkpoint: keep source/docs/tests plus primary append-only evidence ledgers and frozen protocols; ignore regenerated summaries, diagnostic CSVs, caches, and temporary outputs.
