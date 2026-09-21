# What we learned about optimization when every experiment is expensive

## The question

Suppose you have a model with a handful of unknown parameters.

Maybe it is a scientific simulation. You give it five numbers, it runs for a while, and it tells you how well those numbers match the data.

In code, the problem looks roughly like this:

    def loss(params):
        prediction = expensive_simulation(params)
        return error(prediction, observed_data)

Now you want to find the parameters that make loss() as small as possible.

The catch is that expensive_simulation() may take seconds, minutes, or hours. You cannot afford millions of guesses. You may only get a few hundred.

I set out to see whether I could invent a small improvement to a popular optimization method called **differential evolution**, especially for this "every evaluation is precious" setting.

I did not end up inventing a better algorithm.

I found something simpler and, in practice, probably more useful:

> **When the number of evaluations is tightly limited, the size of the optimizer's population can matter more than clever changes to the optimizer itself.**

And then a held-out test stopped me from making that statement too strong.

## First: what is differential evolution?

Differential evolution, or DE, is a derivative-free optimizer.

That means you do not need to tell it the gradient or the equations behind the model. You only need to be able to say:

> "Try these parameters and I will tell you how good they are."

DE keeps a **population** of candidate answers.

Imagine trying to find the best recipe for coffee with five knobs:

- coffee dose
- water temperature
- grind size
- brew time
- water quantity

A DE-like process is roughly:

1. Start with several different recipes.
2. Taste them.
3. Mix ideas from the better and different recipes to create new ones.
4. Taste the new recipes.
5. Keep the better ones.
6. Repeat.

The important point is that **every member of the population costs an experiment**.

In SciPy, the code can be as simple as:

    from scipy.optimize import differential_evolution

    result = differential_evolution(
        loss,
        bounds,
        popsize=15,   # SciPy's default multiplier
    )

For a problem with D parameters, SciPy's popsize=15 means roughly **15 × D candidate solutions**.

So for five parameters, the initial population is about 75 candidates.

That is perfectly reasonable when evaluations are cheap.

It can be surprisingly expensive when you only have 250 evaluations total.

## The simple arithmetic that changed the project

Take a five-parameter problem and allow only **50 evaluations per parameter**, or 250 evaluations total.

With popsize=15:

- initial population: 75 evaluations
- budget remaining: 175
- that is only about **2.3 more full population rounds**

With popsize=2:

- initial population: 10 evaluations
- budget remaining: 240
- that allows about **24 more rounds**

Same optimizer. Same objective function. Same total budget.

But one version spends much of the budget creating a wide initial population, while the other gets many more chances to **learn from what happened and try again**.

That led to the most useful idea in the project:

> With a tight budget, there is a trade-off between **breadth** and **number of learning rounds**.

Too large a population: you explore widely but barely get to iterate.

Too small a population: you get many rounds, but the candidates become too similar and DE loses the diversity it needs to create useful new directions.

In my experiments, a population around **2 × D** often landed in a good middle ground.

Going all the way down to about D candidates was clearly too small.

## What I actually tested

I did not start with population size.

I first tried several more sophisticated ideas for improving DE: balancing how candidate differences are chosen, learning from rejected trials, abandoning apparently bad generations early, and choosing the initial population from its geometry.

Each idea had a plausible explanation.

None produced a reliable improvement.

That was useful because it forced me to improve the baselines instead of congratulating myself on a clever mechanism.

Once I tested much smaller populations, the baseline itself improved dramatically.

For example, in one development comparison at a 200D evaluation budget:

| Method | Median log10 error |
|---|---:|
| SciPy DE, population D | +0.996 |
| **SciPy DE, population 2D** | **+0.051** |
| CMA-ES | +0.187 |

The exact values matter less than the pattern:

- D candidates: too little diversity
- 2D: dramatically better
- much larger populations: often wasteful under the same evaluation budget

This was not a new optimization algorithm.

It was a change in the **operating regime**.

## Would this survive outside an artificial benchmark?

That was the important question.

So I built a separate scientific fitting problem based on pharmacokinetics: a simple model of how a drug is absorbed and distributed through the body.

The model had five unknown parameters:

- absorption rate
- clearance
- central volume
- transfer rate between compartments
- peripheral volume

Think of the task as:

    def loss(params):
        predicted = simulate_drug_model(params)
        return difference(predicted, measured_concentrations)

I generated synthetic patients whose true parameters were known, then asked the optimizers to recover them from concentration measurements.

This let me check two things independently:

1. **Does the fitted curve look right?**
2. **Did we actually recover the right scientific parameters?**

I also implemented the simulation in two independent ways and checked that they agreed, so the result was not caused by a bug in the simulator.

### The small population effect transferred strongly

On eight synthetic patients, the small-population SciPy DE beat the default-like large population on **all eight patients** at every tested budget.

At 50 evaluations per dimension, the improvement in fitting error was about **1.3 orders of magnitude on average**.

At 100D, about **2.4 orders of magnitude**.

At 200D, about **3.1 orders of magnitude**.

I also changed the initialization method while holding population size fixed.

The result stayed.

So the main effect really was **population size / number of learning rounds**, not a lucky initialization trick.

## But another optimizer eventually caught up

I also compared against **CMA-ES**, another strong derivative-free optimizer.

On the pharmacokinetic problem:

- at a very small budget, the small-population DE was often better;
- around 100D, they were roughly comparable;
- by 200D, CMA-ES was much better at very deep convergence.

This was a useful reminder that asking:

> "Which optimizer is best?"

is often the wrong question.

A better question is:

> "Which optimizer is best **at the budget I actually have**?"

The answer can change as the budget changes.

## A second lesson: a better fit is not always a better scientific answer

Because the synthetic patients had known true parameters, I could compare fitted parameters against the truth.

On some patients, several very different parameter combinations produced almost the same concentration curve.

So an optimizer could get an extremely small fitting error while still recovering the parameters only approximately.

That is common in scientific inverse problems: the data may not contain enough information to identify every parameter precisely.

So another practical lesson is:

> **If you know the ground truth in a simulation study, measure parameter recovery as well as objective value.**

Otherwise you can mistake "I fit the observations beautifully" for "I recovered the underlying science."

## Then I tried to prove the stronger claim — and failed

After the development work and the drug-model experiment, the tempting conclusion was:

> "A 2D population is dramatically better than the usual 15D population under tiny budgets."

Instead of simply reporting that, I reserved a set of benchmark problems that had not been used for tuning.

Before looking at the results, I wrote down a success criterion.

At both 50D and 100D evaluations, the small population had to:

- beat the large population on at least 70% of the held-out problems; and
- improve the typical error by at least **0.5 log10 units**.

Then I ran the held-out test.

At 50D:

- small population won **23 of 25** problems;
- but the median improvement was only **0.349**, below the promised **0.500** threshold.

So by my own rule, the confirmation **failed**.

At 100D it passed.

That changes how I would describe the result.

I would **not** say:

> "Use popsize=2; it is the new best default."

I would say:

> **Under very tight evaluation budgets, population size is a first-order design choice. A much smaller population can be dramatically better than a default-like large population, but the size of the benefit depends on the problem.**

That is less catchy, but better supported.

## The most useful mental model

Picture a classroom with a fixed number of questions the teacher will answer.

You can bring:

- **75 students**, each of whom gets to ask a few questions; or
- **10 students**, who can ask questions, hear the answers, revise their thinking, and ask again many times.

The large class has more diversity.

The small class gets more feedback cycles.

If the class becomes *too* small, everyone starts thinking alike and useful diversity disappears.

That is roughly the trade-off DE faces under a fixed evaluation budget.

The best balance depends on the problem.

## What this means in practice

If you are using SciPy's differential evolution for an expensive objective, I would not blindly accept the default population size.

For example, instead of only trying:

    result = differential_evolution(
        loss,
        bounds,
        popsize=15,
        polish=False,
    )

it is worth comparing, under the **same strict evaluation budget**:

    result = differential_evolution(
        loss,
        bounds,
        popsize=2,
        polish=False,
    )

But do not treat 2 as a magic constant.

A sensible experiment is:

1. Pick the budget you actually expect to have.
2. Compare a few population sizes under exactly that budget.
3. Include a strong alternative such as CMA-ES or an adaptive DE method.
4. Measure progress at intermediate budgets, not only the final result.
5. Test the choice on problems that were not used to tune it.
6. For scientific fitting, measure whether the recovered parameters are correct, not only whether the simulated curve fits.

## What I set out to do versus what I learned

I set out to invent a new optimizer.

I did not.

Instead I learned that, in this regime:

- the **evaluation budget changes what good optimizer settings look like**;
- population size can matter more than several clever algorithmic modifications;
- roughly 2D candidates was a strong low-budget setting in these experiments, but not a universal optimum;
- stronger adaptive methods such as L-SHADE and CMA-ES remain important comparisons;
- results on a benchmark should be transferred to a real scientific problem;
- a beautiful objective value can hide poor parameter identification;
- and a preregistered failure can be more informative than another tuned benchmark win.

The shortest version is:

> **When experiments are expensive, do not ask only "Which algorithm?" Ask "Which algorithm, configured for this exact evaluation budget?"**

That was the useful discovery.
