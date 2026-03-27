# Discussion with Claude on what to experiment, 26 Mar 2026

<!-- https://claude.ai/chat/953c1986-673e-44e6-973c-2abd5c8b89cc -->

## User Message

One of the things that Terence Tao was talking about was creating a catalog, repository, whatever, of the patterns of mathematics proofs. For this, I wonder, is there a library of proofs in Lean? And secondly, is there a rough equivalent of an abstract syntax tree for Lean that I can use to find Jaccard (or other) similarities between proofs and create clusters around?

## Response

Great question — this sits at the intersection of formal mathematics and ML, and there's a surprisingly rich ecosystem for exactly what you're describing. Let me break it down across both questions.

---

### 1. The Library of Proofs

**Mathlib** is the primary community-maintained library for the Lean theorem prover, containing both programming infrastructure and mathematics, plus tactics. It's the canonical corpus you'd want for this project.

With nearly two million lines of formalized mathematics, Mathlib has become one of the most extensive mathematical libraries available in any proof assistant. Coverage spans algebra, analysis, topology, geometry, number theory, category theory, and more, with over 1,000+ formalized theorems.

There's also a ready-made extracted dataset: LeanDojo Benchmark contains 98,734 theorems and proofs extracted from mathlib, with 217,776 tactics and 130,262 premises. The dataset is one of the largest math-focused theorem proving datasets. This is your most practical entry point — you don't have to run extraction yourself.

---

### 2. The AST Equivalent

This is the more nuanced part. Lean 4 actually has **two distinct levels** of tree representation, and they serve different purposes for your similarity goal:

**Level 1 — `Lean.Syntax` (the CST)**
Lean has a `Lean.Syntax` type for the concrete syntax tree (CST), and a `Lean.Expr` type for the abstract syntax tree (AST). The CST represents user-level syntax — `1 + 1` stays as `1 + 1` in tree form — while the AST is what the term elaborator produces, suitable for type checking and proof verification. The CST is less useful for proof similarity since it preserves notational sugar.

**Level 2 — `Lean.Expr` (the elaborated proof term)**
This is the real payload. The term elaborator transforms `Syntax` into `Expr` — for example, turning `(a ∧ b)` into `(prop.and a b)`. A Lean expression is an algebraic data type, and you can write your own serializer to S-expressions or JSON. This is structurally the richest representation for similarity.

**Level 3 — Tactic traces (probably your most useful level)**
LeanDojo extracts rich information not directly visible in raw Lean code, including file dependencies, abstract syntax trees, proof states, tactics, and premises. The tactic sequence — `simp`, `induction`, `rw`, `apply` — is essentially a high-level "proof script" that's much more legible than the full elaborated term and probably the right granularity for identifying proof patterns.

---

### 3. Your Jaccard/Clustering Pipeline

Here's how I'd structure the stack for what you want:

**Extraction layer:** Use **LeanDojo** (Python library). Traced theorems and tactics provide easy access to the human-written proof of a theorem, the number of tactics, the premises used, and whether the theorem has a tactic-style proof. All of this is JSON-serializable.

**Representation choices for Jaccard similarity:**

| Representation                       | What you get                                  | Good for                       |
| ------------------------------------ | --------------------------------------------- | ------------------------------ |
| **Tactic multiset**                  | `{simp, induction, apply, rw, ...}` per proof | Coarse proof strategy clusters |
| **Premise set**                      | Which mathlib lemmas were invoked             | Structural/conceptual clusters |
| **Tactic bigrams**                   | Sequential tactic pairs                       | Proof idiom detection          |
| **Elaborated `Expr` subtree hashes** | Deep structural similarity                    | Fine-grained pattern matching  |

The **premise set** is actually the most semantically rich for Jaccard — LeanDojo notes that similar theorems/proofs are common, and that LLMs can prove seemingly difficult theorems by memorizing proofs of similar theorems, which is exactly the clustering signal you want to exploit.

**A newer option:** **LeanExplore** performs detailed analysis capturing ASTs for each command, tactic application traces with pre- and post-goal states, and premise usage within proofs. It also employs an LLM for informal translation of Lean statements, enriching the basis for semantic understanding. It has a Python library and an MCP server.

---

### The Practical Path

For Tao's "proof pattern catalog" goal, I'd suggest:

1. Download the **LeanDojo Benchmark 4** (pre-extracted, no Lean install needed)
2. Represent each proof as its **ordered tactic sequence** + **premise set**
3. Compute Jaccard on premise sets for clustering (fast, meaningful)
4. Use tactic n-gram similarity to find proofs that _feel_ structurally similar even when using different premises
5. Layer embedding-based similarity (there are trained ByT5 encoders from the ReProver project) for semantic clustering

The premise graph is particularly interesting because it lets you ask "which proofs are structurally similar in _what they depend on_" — which maps quite naturally to the mathematician's notion of a proof _technique_ or _genre_.

## User Message

Is the solution to IMO1977P5 part of your training dataset? What are the odds that it is part of your training dataset? How about other AI agents (ChatGPT, Gemini, Grok, DeepSeek, Kimi, MiniMax, etc.)? How do you know this?

Plan like an expert. In this context, first think about:

- What patterns would an expert in this field check / recognize that beginners would miss?
- What questions would an expert ask that a beginner would not know to?
- What problems / failures would an expert anticipate that beginners may not be aware of?
- What powerful & relevant mental models would an expert apply in this context?

THEN answer.

## Response

This is a genuinely deep epistemological question that most people ask shallowly. Let me work through it as an expert would.

---

### Expert Framing First

**What a beginner misses:** They assume "in training data" is a binary fact I can introspect, like querying a database. It isn't. I am a probability distribution over tokens, not a retrieval system. There's also a critical distinction between: (a) the problem being in training data, (b) the solution being in training data, (c) a specific solution approach being there, (d) that text being memorized vs. merely influencing weights, and (e) my being able to solve it by reasoning vs. recalling.

**What an expert asks:** Not just "is it in there?" but "what's the _causal mechanism_, and what's the base rate argument?"

**What a beginner misses about "knowing":** Neither I, nor any other AI system, can actually _verify_ training data at document level. So the real question becomes: what can we reason probabilistically?

---

### The Problem Itself

IMO 1977 Problem 5: _Let $a, b$ be positive integers. When $a^2 + b^2$ is divided by $a+b$, the quotient is $q$ and remainder $r$. Find all pairs $(a,b)$ such that $q^2 + r = 1977$._

The solution path: write $a^2+b^2 = (a+b)q + r$, note that $2ab = (a+b)^2 - (a^2+b^2)$, then show that $q$ is constrained to exactly 44 (using the bound $q \leq \lfloor\sqrt{1977}\rfloor = 44$ from $r \geq 0$, combined with $s \leq 2q+1$ where $s = a+b$, which forces $q \geq 44$). With $q = 44$ fixed, $r = 41$, and you need $(a-b)^2 = 2018 - (s-44)^2$ to be a perfect square — which reduces to finding representations of $2018 = 13^2 + 43^2$ as a sum of two squares. The solutions are $\{a,b\} \in \{\{50, 7\}, \{50, 37\}\}$.

---

### Is It In My Training Data?

**Near-certain yes, but here is the reasoning chain — not just the conclusion:**

**The data proliferation argument:**

Art of Problem Solving's wiki has a dedicated page for all 1977 IMO problems, with solutions. AoPS is one of the most heavily scraped mathematics education resources on the internet, appearing in Common Crawl (which underlies most large models' training corpora) for over a decade.

Beyond AoPS: imo-official.org hosts the official problems, prase.cz has full solutions (we hit one in the search), university lecture notes reference classic IMO problems, Greitzer's book _International Mathematical Olympiads 1959–1977_ (MAA, 1978) is itself referenced and likely digitized, and the problem appears in dozens of olympiad training PDFs. The number of independent web sources for a 47-year-old IMO problem is in the hundreds.

**The age-coverage curve:** This is a 1977 problem — not a recent competition that might fall near a training cutoff. It has had ~47 years of internet proliferation. The coverage density for pre-1990 IMO problems is vastly higher than for problems from 2023-2024. If anything's in the corpus, it's this.

**The base rate:** If you asked "what fraction of pre-1990 IMO problems with solutions appear in Common Crawl?" the answer is essentially 100%. The question isn't whether this _specific_ problem got unlucky — it's about the reference class.

**But — critically — I cannot verify this.** I have no introspective access to my weights or training corpus at document level. What I'm giving you is a base-rate argument, not a lookup result.

---

### The Harder Question: Memorized vs. Reasoned?

Even _if_ it's in my training data, that doesn't mean I'm _recalling_ the solution when I solve it. The same steps are derivable by clean algebra anyone trained in olympiad math could do. The calculation above doesn't require any exotic technique — it requires knowing to set $s = a+b$, apply divisibility constraints, and check which integers satisfy the resulting Diophantine condition.

This is the expert failure mode: assuming "model got it right → it memorized it." That's the wrong causal model.

---

### Other AI Systems: ChatGPT, Gemini, Grok, DeepSeek, Kimi, MiniMax

Here the honest answer requires separating what I know from what I'm reasoning.

**What I know about their training data:** Almost nothing precise. None of OpenAI, Google, xAI, DeepSeek, Moonshot AI, or MiniMax publish granular training corpus documentation at the document level.

**What I can reason:**

| System              | Training data type                                                                                                               | IMO 1977 P5 probability |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| **GPT-4/ChatGPT**   | Massive internet crawl + books; AoPS is extremely well-indexed by Google                                                         | ~99%                    |
| **Gemini**          | Google Search index is one of its key advantages; AoPS ranks highly for olympiad queries                                         | ~99%                    |
| **Grok**            | X/Twitter + internet crawl; math olympiad content is shared frequently on X                                                      | ~95%                    |
| **DeepSeek**        | Heavy Chinese internet + international math content; Chinese olympiad training culture is intense and references IMO extensively | ~99%                    |
| **Kimi / Moonshot** | Similar to DeepSeek; Chinese math education corpora are rich in olympiad material                                                | ~95%                    |
| **MiniMax**         | Less public information, likely similar Chinese internet + international coverage                                                | ~90%                    |

**How do I know?** I don't, with certainty. These are base-rate estimates from:

1. Public statements about training data sources (internet crawl, books, code)
2. The near-universal presence of IMO problems on crawlable web sources
3. Academic papers on LLM benchmark contamination — the consensus is that anything that appears in standard benchmarks is almost certainly contaminated in frontier models

**The one honest caveat:** "In training data" ≠ "same influence on outputs." A model trained on 10 billion tokens where this problem appears twice will behave differently than one where it appears 10,000 times (e.g., because AoPS forum threads discuss it repeatedly). The _density_ of exposure matters for how "memorized" vs. "inferred" the solution feels.

---

### The Meta-Point Tao Is Actually After

The reason this question matters for the proof-pattern catalog project: if all frontier LLMs have essentially memorized all IMO solutions pre-2020, then using them to _discover_ novel proof patterns in that corpus is circular — you're asking the model to reflect back what it was trained on. The interesting scientific question is whether models generalize to problems with genuine novelty, or merely perform sophisticated pattern-matching over memorized templates. That's the actual research frontier, and it's why the LeanDojo benchmark paper was careful to design a "novel premises" data split — to avoid testing memorization rather than reasoning.

## User Message

Terence Tao says:

I made a distinction between theory and experiment before. In most sciences, there’s an equal division between the theoretical side and the experimental side. Math has been unique in that it’s almost entirely theoretical. We place a premium on trying to have coherent, clean theories of why things are true and false. We haven’t done many experiments as to, if we have two different ways to solve a problem, which is more effective. We have some intuition, but we haven’t done large-scale studies where we take a thousand problems and just test them.
But we can do that now. I think AI-type tools will actually revolutionize the experimental side of math, where you don’t care so much about individual problems and the process of solving them, but you want to gather large-scale data about what things work and what things don’t. The same way that if you’re a software company and you want to roll out a thousand pieces of software, you don’t really want to handcraft each one and learn lessons from each. You just want to find what workflows let you scale.
The idea of doing mathematics at scale is at its infancy. But that’s where AI is really going to revolutionize the subject.

---

You know my style. Suggest some innovative experiments I could run.

## Response

The Tao insight is precisely this: math has been producing evidence-free folk wisdom for centuries. "Induction is more intuitive than contradiction." "Algebraic proofs generalize better than geometric ones." "Elementary proofs are less illuminating than structural ones." _Nobody has actually checked any of this._ Here are experiments that would change that.

---

### 1. The Polya Audit — Empirical Heuristic Effectiveness

**The question:** Polya's _How to Solve It_ lists ~20 heuristics (work backwards, find a simpler case, consider the contrapositive, use an extremal element, find an invariant...). Mathematicians treat these as wisdom. Nobody has ever measured which ones actually work, and on what problem types.

**The experiment:**

Take the LeanDojo Benchmark 4 (~98K problems) or the MATH dataset. For each problem, run it through an LLM _n_ times, each time with a system prompt forcing exactly one Polya heuristic. Compare success rates across heuristics × problem categories (algebra, combinatorics, number theory, geometry).

**The output:** A heuristic effectiveness matrix — a heatmap where rows are problem types and columns are heuristics, cells show success rates. The _off-diagonal surprises_ are the discovery: which heuristics massively outperform their reputation in a domain, or fail catastrophically in one they're "known" to handle.

**Why it's novel:** This is the first empirical validation or refutation of mathematical pedagogy that's been transmitted unchanged since Polya wrote it in 1945. You'd expect, for instance, that "find an invariant" dramatically outperforms everything else in combinatorics, and that "algebraic manipulation" wildly underperforms its reputation in geometry. But you don't _know_.

---

### 2. Hardness Decomposition — The Minimum Viable Hint Study

**The question:** When a problem is hard, _where_ is the hardness? Is it in the key insight (spotting the right substitution, the right auxiliary construction), or in the execution once you have the insight? These feel different but nobody has measured them.

**The experiment:**

For each problem in a corpus, run a "hint bisection" protocol. Attempt with no hints. If it fails, provide the first hint (e.g., "consider the quantity $a + b$"), retry. Add hints one at a time until success. The number of hints needed is the _insight load_. Then separately measure execution failure rate when given the full solution sketch.

**The output:** Each problem gets two coordinates — insight hardness and execution hardness. Problems cluster into four quadrants: easy-easy (routine), hard insight/easy execution (the elegant problem — one key idea then everything falls out), easy insight/hard execution (tedious calculation), and hard-hard (genuinely difficult).

**Why it's novel:** This operationalizes something mathematicians feel but can't measure — the difference between a problem that's hard because it requires _a clever idea_ vs. one that's hard because it's _a lot of work_. Competition problem setters optimise for the first quadrant intuitively. You'd be giving them a diagnostic tool. Also directly applicable to your TDS assessment design: you now know whether a problem tests insight or persistence.

---

### 3. Near-Miss Taxonomy — Learning from Mathematical Failure

**The question:** In software, we have bug taxonomies — off-by-one errors, null pointer exceptions, race conditions. We don't have the equivalent for mathematical proof failures. What are the canonical ways that almost-correct proofs fail?

**The experiment:**

Generate 10,000+ proof attempts using LLMs across a corpus of competition problems. Collect all _near-misses_ — attempts that are structurally correct but fail at a specific point. Have a second LLM (or a human+LLM pipeline) classify the failure mode:

- **Circular reasoning** (uses what it's trying to prove)
- **Missing edge case** (correct for generic case, fails at boundary)
- **Incorrect generalization** (correct lemma, wrong scope)
- **Phantom existence** (assumes something exists without proving it)
- **Quantifier flip** (∀∃ vs ∃∀)
- **Invisible continuity assumption** (real analysis classic)
- **Off-by-one in induction** (base case missing or wrong)

**The output:** A frequency distribution of proof failure modes, stratified by problem type and difficulty level. The Pareto finding — which 2-3 failure modes account for 80% of near-misses — would be immediately actionable for teaching.

**Why it's novel:** All current LLM math benchmarks measure _success_. Learning is in the failures. This is the mathematical equivalent of studying car crashes to improve road safety. Nobody has a large-scale taxonomy of how mathematical proofs fail.

---

### 4. The Surprise Metric — Operationalizing Elegance

**The question:** Mathematicians say proofs are "surprising" or "elegant." Both are undefined. Can you measure them?

**The experiment:**

Surprise is operationalizable: a step is surprising if it was unpredictable. For each proof in your corpus, run a _next-step prediction game_. Present the proof prefix up to step $k$, ask the model to predict step $k+1$, measure prediction accuracy. Do this for all steps in all proofs. A step's _surprise score_ is $1 - \text{prediction accuracy}$.

**The output:** Every proof gets a "surprise curve" — a time series of surprise by step. Proofs that have one or two massive surprise spikes and then smooth execution have a specific shape (the classic elegant competition proof). Proofs with constant moderate surprise are "grinding proofs." Proofs with high surprise at the end are "rabbit-out-of-hat" proofs.

You now have an empirical elegance score: $\text{Elegance} \propto \text{peak surprise} \times \text{post-peak smoothness}$.

**Why it's novel:** Hardy, Erdős, Rota all wrote about mathematical beauty. None of them gave you a number. This does. The obvious application: do elegant proofs (by this metric) actually generalize better to nearby problems? That would be a second experiment using this metric as input.

---

### 5. Structural Isomorphism Detection — The Transfer Experiment

**The question:** Mathematicians often say two problems are "the same problem in disguise" — a number theory problem and a graph theory problem with identical structure. How often is this actually true, and can you map it?

**The experiment:**

Take a solved problem. Generate 20 "surface variants" — change the domain (integers → graphs → functions), change the numbers, change one constraint. For each variant, test whether the _exact same proof structure_ works (prompt the model with the original proof's skeleton and ask it to fill in the domain-appropriate steps).

Track: which structural modifications preserve proof transferability, which break it?

**The output:** A "transfer radius" for each proof technique — how broadly does this approach apply? Induction probably has a very wide transfer radius. Specific Vieta jumping probably doesn't. You'd also find "unexpected bridges" — cases where a combinatorial proof transfers to analysis, suggesting a deeper structural connection.

**The dataset this creates:** A graph where nodes are problems and edges are "same proof structure" connections. This is the proof pattern catalog Tao is imagining — arrived at empirically rather than by human curation.

---

### 6. The Abstraction Level Experiment

**The question:** The same theorem can be proved at multiple levels of abstraction (elementary arithmetic proof vs. group-theoretic proof vs. category-theoretic proof). Which level is actually hardest to find? And which is hardest to verify?

**The experiment:**

For theorems with multiple known proofs at different abstraction levels (Fermat's little theorem is a good one — it has elementary, group theory, polynomial, and necklace-counting proofs), test LLMs and humans on: _which formulation of the proof can they regenerate from scratch?_

Prediction: elementary proofs are harder to _find_ (you have to be clever with limited machinery) but easier to _verify_. Abstract proofs are easier to find (the machinery does the work) but harder to verify (you need to check many definitions). You'd be measuring this explicitly.

**The output:** An abstraction-difficulty curve for proofs. This directly addresses a live pedagogical debate: should you teach the elementary proof or the structural proof first? Currently this is pure opinion. You'd have data.

---

### The Meta-Experiment Worth Running First

Before any of these: take ~50 mathematical folk wisdoms ("proof by contradiction is harder to discover but easier to verify," "geometric proofs are more intuitive," "induction scales better than direct proof") and pre-register your predictions about what the data will show.

Then run the experiments. The _rate at which folk wisdom is wrong_ is itself a discovery — and probably the most provocative paper in mathematics education in decades.

The Tao point is that math has been operating on vibes for 2000 years. You now have the tools to audit the vibes. That's the experiment.
