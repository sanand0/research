# Prompts

## Setup

```bash
curl https://elan.lean-lang.org/elan-init.sh -sSf | sh
# Press 1

export PATH=$PATH:$HOME/.elan/bin
lake exe cache get
lake build
```

## Prove something, 26 Mar 2026 (Copilot Yolo - Sonnet 4.6 medium)

`lake` is installed. Verify - prove something simple.
Use mathlib. Think of something CREATIVE to do with it!
Save the .lean file. Document in README.md.

## The Polya Audit, 26 Mar 2026 (Copilot Yolo - Sonnet 4.6 high)

**The question:** Polya's _How to Solve It_ lists ~20 heuristics (work backwards, find a simpler case, consider the contrapositive, use an extremal element, find an invariant...). Mathematicians treat these as wisdom. Nobody has ever measured which ones actually work, and on what problem types.

**The experiment:**

Take the LeanDojo Benchmark 4 (~98K problems) or the MATH dataset. For each problem, run it through an LLM _n_ times, each time with a system prompt forcing exactly one Polya heuristic. Compare success rates across heuristics × problem categories (algebra, combinatorics, number theory, geometry).

**The output:** A heuristic effectiveness matrix — a heatmap where rows are problem types and columns are heuristics, cells show success rates. The _off-diagonal surprises_ are the discovery: which heuristics massively outperform their reputation in a domain, or fail catastrophically in one they're "known" to handle.

This is a large scale experiment. PLAN CAREFULLY. Experiment to validate your plan.

Do this EFFICIENTLY. Maximize programmatic automation. Verify with small samples, then scale. Check with me at each step before scaling.

---

Document progress and learnings so far in notes.md under `## The Polya Audit, 26 Mar 2026`.
Let's run for gpt-5.4-nano instead of the gpt-4.1-* series. Let's also run for gemini-3.1-flash-lite-preview (not the gpt-4.1 or any others). Test what the sweet-spot should be in terms of level of difficulty for these models.
We want to run enough experiments so that the total cost will be about $1 per model with that pricing. Plan accordingly.
Write the script to allow selecting subsets of problem sets, Polya heuristics, models, and number of runs per problem.
Write the script in a resumable way, i.e. if interrupted, it'll start where it left off.
Store the output in a structured way for easy analysis and visualization.
Ensure that everything (code, output, intermediate logs/results/...) are in the current directory (~/code/research/learn/).
Do a quick test, document your findings again in notes.md, and check with me.

---

Let's just run with gpt-5.4-nano for now - but write the script so that we'll be able to extend to other models soon.
Let's do L5 only (tougher, ~72% baseline), rather than L4+L5.
Go ahead and run!
Make sure that I can continuously see the progress a log file.

---

I updated the Gemini API key for `llm`. See if you can run it?
If not, let me know.
If yes, run the same analysis that you did for gpt-5.4-nano, but now for gemini-3.1-flash-lite-preview. Make sure you UPDATE the JSON (without deleting past model runs!) Document your findings in notes.md.

---

Are you able to access claude-haiku-4-5?

---

I added an ANTHROPIC_API_KEY in .env. Try now.

---

Stop the run for now. I'll resume it later.

---

Resume

<!-- copilot --resume=e742ab4b-5b1b-4906-ab9b-d3ae6f877f05 -->

## Data story

Write a single-page polya.html interactive narrative data story (using the data-story skill) written in the style of Malcolm Gladwell, visualized like The New York Times, that shares the lessons of the Polya Audit on Lean.

Context: on the [Dwarkesh Patel podcast](https://www.dwarkesh.com/p/terence-tao), [Terence Tao](https://en.wikipedia.org/wiki/Terence_Tao) said:

> I made a distinction between theory and experiment before. In most sciences, there’s an equal division between the theoretical side and the experimental side. Math has been unique in that it’s almost entirely theoretical. We place a premium on trying to have coherent, clean theories of why things are true and false. We haven’t done many experiments as to, if we have two different ways to solve a problem, which is more effective. We have some intuition, but we haven’t done large-scale studies where we take a thousand problems and just test them.
But we can do that now. I think AI-type tools will actually revolutionize the experimental side of math, where you don’t care so much about individual problems and the process of solving them, but you want to gather large-scale data about what things work and what things don’t. The same way that if you’re a software company and you want to roll out a thousand pieces of software, you don’t really want to handcraft each one and learn lessons from each. You just want to find what workflows let you scale.
The idea of doing mathematics at scale is at its infancy. But that’s where AI is really going to revolutionize the subject.

This led me to a [discussion with Claude](lean-experiments-ideas.md) where it suggested: "The Polya Audit — Empirical Heuristic Effectiveness":

- **The question:** Polya's _How to Solve It_ lists ~20 heuristics (work backwards, find a simpler case, consider the contrapositive, use an extremal element, find an invariant...). Mathematicians treat these as wisdom. Nobody has ever measured which ones actually work, and on what problem types.
- **The experiment:** Take the LeanDojo Benchmark 4 (~98K problems) or the MATH dataset. For each problem, run it through an LLM _n_ times, each time with a system prompt forcing exactly one Polya heuristic. Compare success rates across heuristics × problem categories (algebra, combinatorics, number theory, geometry).
- **The output:** A heuristic effectiveness matrix — a heatmap where rows are problem types and columns are heuristics, cells show success rates. The _off-diagonal surprises_ are the discovery: which heuristics massively outperform their reputation in a domain, or fail catastrophically in one they're "known" to handle.
- **Why it's novel:** This is the first empirical validation or refutation of mathematical pedagogy that's been transmitted unchanged since Polya wrote it in 1945. You'd expect, for instance, that "find an invariant" dramatically outperforms everything else in combinatorics, and that "algebraic manipulation" wildly underperforms its reputation in geometry. But you don't _know_.

Read prompt.md to understand what I asked Claude Sonnet 4.6 on GitHub Copilot to do. Read notes.md to understand the results.

Analyze the results based on the data-analysis skill.

Based on this, write the story of whether Polya's advice helps LLMs solve math problems, what works, what doesn't work, what we can infer conclusively and what's grounded in others' recent/proven research (think creatively!)

**Optional context** if required:

- polya_experiment.py: The main script for running the Polya Audit experiment, including functions for selecting problem subsets, heuristics, models, and handling resumable runs.
- polya_heuristics.json: List of Polya heuristics and their corresponding system prompts
- polya_results/problems.json: Problem set
- polya_results/results.db: Full results
- polya_results/logs/run_*.jsonl: Run logs
- polya_results/calibration_gemini_fixed.txt
- polya_results/{full_run,gemini_run,haiku_run}.log: Logs for GPT-5.4-nano, Gemini 3.1 Flash Lite, and Claude Haiku runs
- polya_results/calibration_log.txt: Calibration run log

You can also read what Copilot did at ~/.copilot/logs/ for the session e742ab4b-5b1b-4906-ab9b-d3ae6f877f05

Use tooltips, popups, interactions, and animations as informative and engaging aids.

**Tooltips** are for:

- Context about non-obvious terms or phrases (only if relevant and useful)
- Additional context about references (where possible)
- Metadata and context about data points, table cells, chart elements, etc. (always)

**Popups** are for:

- Citations. Search for and include references. Cite the key point from the reference and link to it.
- Files. Link liberally to files as supporting evidence. Clicking on file links should open the files in a popup, with a link to open the original in a new tab. Syntax-highlighted if code. Show sortable for tabular data, gradient-coloring important numeric / categorical columns if that will help understand the context
- Data points. Provide extensive context for data points.
  - Wherever useful, clicking on data points, table cells, chart elements, etc. should open a popup that provides full context about that element.
  - Include narratives, cards, tables, charts, or even entire dashboards that answer what the user is likely to be curious about or wants to dig in for more details. E.g. context, examples, related metrics, trends over time, breakdown by relevant dimensions, etc.
  - Standardize the format of these popups so users know what to expect. Reuse popups by archetype.

**Animated SVGs** are for explaining processes, mechanisms, workflows, etc. The aim is to make users FEEL the process. One glance should give them an intuitive understanding of how it works, even before they read the accompanying text. Show how things are connected, what data flows from where to where, how elements, interact, etc.

Plan the design and layout carefully before coding. Sketch the information architecture, interaction inventory, design tokens, performance sensitive paths, responsive breakpoints, etc.

---

Use `uvx rodney` to take screenshots. I see overlap issues in many chart titles, e.g. Finding #1, #3, #4.
Spacing can be improved as well - within as well as around charts.
Labels (e.g. model names) get cut off in "Heuristic Effect on Each Model".

Include an interactive table showing what the impact of each Polya heuristics (as rows) is across models (on average) OR across problem types (on average).
Which of these is a better split, i.e. are models consistent in how they respond to heuristics? Or are problem types more consistent in how they respond to heuristics? Or does it depend? Analyze and share insights.
This is a powerful summary of whether some heuristics are clearly more effective than others - so factor in the statistical significance and make it visibly clear in the table.
You don't need to include BOTH tables (heuristics × models AND heuristics × problem types) if one is more insightful than the other.

This current directory will be deployed at https://github.com/sanand0/research/ under the `lean` directory. (You can't see the git repo because you're running a container in a sub-folder. That's OK.)
Update .gitignore to ignore files that needn't be committed (e.g. log files, results.db) but if there ARE results that we should be publishing (e.g. a concise summary of results), modify the code to generate that and run it.
Include links to GitHub (e.g. https://github.com/sanand0/research/blob/main/lean/prompts.md for the prompts - it doesn't exist now but I will push it later) where it will enhance the story and provide access to the code and data for readers who want to dig in.

---


Introduce richer tooltips on the "Which Heuristics Win — And Where?" table. Clicking on the heuristic can reveal the full system prompt and a concise summary of the statistics for that heuristic.
Clicking on the cells can, similarly, reveal a next level of detail. Currently it shows Uncaught TypeError: Cannot read properties of undefined (reading 'name') at openCellPopup (polya.html:1722:77) at HTMLTableCellElement.onclick (polya.html:2070:2).
The contrast for the column headers of the "Heuristic Effect on Each Model" chart is low. Can you increase it?

---

The column headers have color: #444 inline style which overrides the color: #ccc on #htable th.
Provide rich popups for the row and column headers of the "Every Heuristic, Every Category, Every Model" table as well.
In the "Heuristic Effect on Each Model (Δ from baseline accuracy)" chart, the text descriptions get chopped off. Shorten them.

Explore the theory that some types of questions consistently benefit from some types of heuristics.
If this is numerically and statistically significant, detail it out.
If not, mention that there is no such pattern.

---

Let's make all chart elements in the "Findings" charts clickable, too.

IMPORTANT: In the light of finding #5: "The single biggest predictor of whether Pólya advice will help is what kind of problem you're facing" would you want to rewrite any parts of the narrative?

---

For tables like "Which Heuristics Win — And Where?" which can be wide, allow it to take up a wider width of the page, centered - even the full viewport. We do this for "Every Heuristic, Every Category, Every Model" already. Same for the stat-cards in "The Main Finding" - let them take up the full width, centered.

<!-- claude --resume 2826c3ba-13db-48ea-870c-5b41fa64d2e8 -->
