# Checkpoint 001 — baseline pilot + PairDE

Date: 2026-09-10
Status: development only; confirmation reserve untouched.

## Claim tested

Under a strict 200D objective budget, balancing DE donor usage and antithetically pairing difference directions might reduce finite-population sampling variance enough to improve best/1/bin.

Prediction before testing: lower run-to-run variance and better late-budget progress, especially when few generations are available; advantage should shrink with larger budgets. Main falsifier: no consistent problem-level advantage against an otherwise matched deferred best/1/bin baseline.

## Evidence

Development pilot: BBOB f={1,3,6,8,10,12,15,17,20,23}; instances {1,2}; d={5,10}; seeds {1,2}; strict budget 200D. Confirmation reserve remains f={2,7,11,16,21}, instances 11–15, and d=20.

Selected baseline results (80 runs each):

| Algorithm | Median log10 error @200D | <=1e-2 | <=1e-5 | Median overhead us/eval |
|---|---:|---:|---:|---:|
| SciPy best1bin, p=5D, Halton | 0.566 | 7/80 | 2/80 | 33.2 |
| CMA-ES, sigma=0.30 box width | 0.187 | 18/80 | 8/80 | 99.2 |
| modDE L-SHADE modules, p0=6D | 0.425 | 9/80 | 1/80 | 28.3 |
| PairDE p=5D, Halton, deferred | 0.636 | 4/80 | 0/80 | 23.4 |
| Matched SciPy deferred | 0.577 | 4/80 | 0/80 | 13.9 |

PairDE vs matched deferred SciPy, problem as uncertainty unit after median over seeds:
- 50D: mean log10 advantage -0.0935, bootstrap 95% CI [-0.2086, 0.0109], 15/40 wins.
- 100D: -0.0437 [-0.1117, 0.0234], 14/40 wins.
- 200D: -0.0745 [-0.1576, 0.0001], 19/40 wins.

Decision: **reject PairDE; do not confirm or tune it.** The effect is not meaningfully positive and early-budget behavior is worse.

## Baseline opportunity

The strongest headroom is landscape geometry rather than donor balance. CMA-ES is dramatically ahead on ill-conditioned problems, while the three methods are much closer on weak-global-structure multimodal problems. But covariance learning, successful-step correlation matrices, eigen-space crossover, mirrored sampling, and generic diversity/restart mechanisms are already prior art. The next candidate needs a more specific information-efficiency mechanism.

## Next bounded batch

Before writing Candidate 2, search specifically for algorithms that exploit *rejected evaluated trials* or pairwise objective differences to estimate curvature/preconditioning in DE/direct search. If this is already crowded, redirect instead of implementing. If there is room, test one minimal mechanism against the same frozen development baselines at 50D/100D/200D, with no confirmation access.

## Reproduce

```bash
cd ~/code/research/algorithm-discovery
uv sync --python 3.12
uv run python -m unittest -v
uv run python bench.py --phase tune --budget-d 200 --ledger results/runs.csv --algorithms \
  scipy-best-p5-immediate scipy-best-p5-deferred scipy-currentbest-p5 scipy-rand-p5 \
  scipy-best-p10 scipy-best-p5-halton scipy-best-p5-halton-deferred \
  cma-s20 cma-s30 cma-s20-p2 modde-lshade-p6 modde-lshade-p10 modde-lshade-p18 \
  pairde-p5-halton
uv run python bench.py --phase pilot --budget-d 200 --ledger results/runs.csv \
  --algorithms scipy-best-p5-halton scipy-best-p5-halton-deferred \
  pairde-p5-halton cma-s30 modde-lshade-p6
uv run python analyze.py
```
