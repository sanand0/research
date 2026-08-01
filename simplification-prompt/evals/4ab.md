### Component table

| Explicitly requested component        | Response A                                                                                                                                                                                     | Response B                                                                                                                                                                                                 |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Smallest reliable experimental design | **Partial** — efficient within-person crossover with 24–30 employees and 300–400 decisions, but no power analysis or variance-based justification establishes that this is sufficient.         | **Partial** — within-person crossover is efficient, but 40 employees × 20 cases is an unsupported fixed choice and is substantially larger without showing why it is necessary.                            |
| Control condition                     | **Present** — identical tasks, data, interface, references, and time allowance; no AI suggestion; neutral screen element controls attention effects.                                           | **Present** — same interface, normal tools, and data, with no AI suggestion; explicitly prevents other AI use.                                                                                             |
| Quality metrics distinct from speed   | **Present** — blinded rubric, paired quality effect, harmful errors, calibration, escalation, automation bias, and decision time kept secondary.                                               | **Present** — blinded rubric, paired quality effect, serious errors, answer changes, confidence, and time kept secondary.                                                                                  |
| Confounds and controls                | **Present** — addresses skill, case difficulty, order, learning, fatigue, evaluator bias, novelty, leakage, selective adoption, outages, and outcome selection.                                | **Present** — addresses skill, difficulty, learning, order, evaluator bias, output variation, contamination, novelty, and unequal effort.                                                                  |
| Stopping rule                         | **Partial** — correctly bases success and futility on a smallest worthwhile effect, but the interim analysis needs a specified group-sequential or multiplicity-adjusted confidence procedure. | **Partial** — avoids optional stopping, but its success rule does not demonstrate that the true effect meets the 0.20-SD usefulness threshold; it only requires the lower confidence bound to exceed zero. |

### A-only

* Deliberately makes about 20% of AI suggestions plausible but wrong.
* Separately estimates performance when the AI is correct, wrong, or when escalation is appropriate.
* Requires that performance on wrong AI suggestions not materially deteriorate before deployment.
* Uses a neutral panel in the control interface to reduce attention and layout effects.
* Includes appropriate uncertainty or escalation directly in the quality rubric.
* Requires partial duplicate scoring and an inter-rater-reliability check before analysis.
* Logs whether suggestions were viewed, accepted, modified, or rejected.
* Uses intention-to-treat analysis when AI suggestions fail or are delayed.
* Controls for benchmark familiarity, collaboration or answer leakage, and outcome cherry-picking.
* Defines success as the confidence interval’s lower bound exceeding the smallest worthwhile improvement.

### B-only

* Records both the first and final answer, directly showing which decisions the AI changed.
* Measures confidence both before and after seeing the suggestion.
* Explicitly prohibits use of other AI tools during control cases.
* Stores and audits all generated AI suggestions.
* Includes case difficulty and order as fixed effects in the model.
* Reports results separately by case difficulty.
* Records clicks and missing answers as indicators of unequal effort.
* Uses a fixed-sample design with no inspection of condition results before collection ends.
* Requires improvement in more than one difficulty level for success.

### Per-criterion winners

1. **Correctness — A.** A’s stopping criterion tests whether the effect exceeds the practical threshold. B could declare success with an estimate of 0.20 SD and a confidence interval such as 0.01–0.39 SD, which does not establish that the true improvement is at least 0.20 SD. A still needs a sequentially adjusted interval for its interim look.

2. **Key drivers — A.** The decisive risk in AI-assisted decisions is whether employees benefit when the AI is right without becoming worse when it is wrong; A tests this directly with controlled wrong suggestions. B merely measures incorrect changes that happen to occur.

3. **Mechanism — A.** By separating AI-correct, AI-wrong, and escalation cases, A can distinguish genuine decision support from automation bias. B’s first-versus-final answer measurement helps trace influence but does not ensure enough diagnostic AI failures occur.

4. **Caveats — A.** A covers the major additional failure modes: harmful decisions, selective adoption, AI outages, answer leakage, benchmark familiarity, evaluator reliability, and outcome cherry-picking. B covers many standard confounds but fewer deployment-critical exceptions.

5. **Calibration — A.** A treats the proposed effect threshold as an example and requires evidence above that threshold, whereas B hardcodes an unsupported sample size and labels an effect useful without requiring the confidence interval to clear the usefulness threshold. Both are insufficiently calibrated about statistical power.

6. **Actionability — A.** A provides a clearer operational deployment rule combining minimum quality improvement, non-inferior harmful-error rates, and resilience to incorrect AI advice. B is executable, but its success rule could approve an effect whose practical magnitude remains uncertain.

**Overall: A**

**Confidence: high**
