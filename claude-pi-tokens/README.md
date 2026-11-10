# Claude Code vs Pi: tokens, cache costs, and budget limits

**10 November 2026 · Claude Pro subscription · Haiku 5.5 · 9 completed trials**

**Finding:** Pi with [`pi-claude-subscription`](https://github.com/jkeskikangas/pi-claude-subscription) used **37% fewer tokens** and cost **19% less at API-equivalent prices** than Claude Code with caching enabled on our small animation task. Both harnesses completed all three trials. Disabling Claude Code's cache did not give a clear saving. All nine attempts cost less than **$0.01 each**, within the proposed **$0.03** task budget.

These are **three runs per option, for one task**. The results show that this setup works. They do not prove that Pi will save 19% on other tasks, or that its images look better. They also do not tell us how much of the Claude Pro five-hour limit each option consumes.

## The question

Can we run one-off student prompts, such as “Create an impressive HTML animation,” with a small budget? We compared three ways to run the **same prompt**, on the **same computer**, with the **same model**:

1. Claude Code with normal prompt caching.
2. Claude Code with caching disabled by `DISABLE_PROMPT_CACHING=1`.
3. Pi, with the `pi-claude-subscription` extension. This uses Claude Code's login as a model connection, but uses Pi's smaller tool and prompt setup.

A *token* is a unit of text processed by the model. A *cache write* stores a prompt prefix for reuse. A *cache read* reuses that stored prefix at a lower API price. A *turn* is one model response. One user prompt can need several model turns because the model must write a file and then respond.

*API-equivalent cost* means the estimated amount for the same token usage at Anthropic's API rates. We did **not** pay this amount separately in these tests. These requests used the local Claude Pro login. A dollar value is **not** a fixed amount of subscription usage.

## Results

We asked each agent to create one self-contained page, `index.html`, called **Aurora Garden**. It needed moving aurora ribbons, particles, pointer or touch input, a burst on tap, a pause control, and support for reduced motion. The exact prompt is in [`task.txt`](task.txt).

| Average per run | Claude, cache ON | Claude, cache OFF | Pi subscription |
|---|---:|---:|---:|
| Completed tasks | 3 of 3 | 3 of 3 | 3 of 3 |
| Total tokens processed | 37,213 | 35,652 | **23,382** |
| Input and cached tokens | 27,420 | 26,523 | **15,055** |
| Output tokens | 9,793 | 9,129 | **8,327** |
| Model turns | 2.67 | 2.67 | **2.33** |
| Estimated API cost | $0.00762 | $0.00722 | **$0.00615** |
| Cost range (three trials) | $0.00506–$0.00942 | $0.00454–$0.00883 | $0.00463–$0.00846 |

**What this means:**

- Pi used **45% fewer input/context tokens** than cache-on Claude Code. It used **37% fewer total tokens**. Its estimated cost was **19% lower**.
- Cache-off Claude Code used **about 5% less money** than cache-on Claude Code *on average here*. That is not a strong result. In the first trial, cache-on was cheaper. In the second, cache-off was cheaper. The model produced different amounts of code each time.
- All nine outputs passed a basic browser test. Each HTML file opened offline. The canvas image changed over time. The Pause button changed state. The browser reported no JavaScript errors. We did **not** run a blind visual-quality study or a full mobile and accessibility audit.

To inspect the pages, open the `index.html` files in the run folders. Here are three first-trial previews:

| Cache ON | Cache OFF | Pi subscription |
|---|---|---|
| [Image](claude-cache-on/preview.webp) · [HTML](claude-cache-on/index.html) | [Image](claude-cache-off/preview.webp) · [HTML](claude-cache-off/index.html) | [Image](pi-sdk/preview.webp) · [HTML](pi-sdk/index.html) |

See [`results.tsv`](results.tsv) for all nine runs, [`results.json`](results.json) for a structured table, and [`usage-evidence.json`](usage-evidence.json) for the source token and cost counters, including checksums of the generated HTML files.

## How we ran the tests

All trials ran on **10 November 2026**, on one Linux workstation. Graphene was not used. We checked the versions: **Claude Code 2.1.321**, **Pi 1.4.0**, and **pi-claude-subscription 0.2.4**. The Claude login reported a **Pro** plan.

- Each run started in a separate empty directory. Each run received the same text from [`task.txt`](task.txt). Each could use tools to read and write the page. We disabled other extensions and project context where the CLIs allowed it.
- Claude Code used `claude -p --model haiku --effort low --tools 'Read,Write' --permission-mode acceptEdits --max-turns 6 --max-budget-usd 0.03 --no-session-persistence --output-format stream-json --verbose` with `--setting-sources ''`, `--strict-mcp-config`, and `--disable-slash-commands`. Cache-off runs added `DISABLE_PROMPT_CACHING=1`.
- Pi used `pi -p --model claude-sdk/claude-haiku-5-5 --thinking off --tools read,write --no-session --mode json` with only the subscription extension loaded; it also used `--no-mcp`, `--no-skills`, and `--no-context-files`. Two of three Pi runs used our patched SDK budget. The first used the installed extension without the patch.
- We removed inherited `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, and `ANTHROPIC_OAUTH_TOKEN` from all runs. The subscription extension also removes inherited API credentials from the process it starts. This reduces the chance of accidental API billing. We did not independently audit the account's paid extra-usage transactions.
- Claude's `result.usage` records the token totals for the complete run. Pi reports usage per assistant response in `message_end`; we **sum** these fields over all responses. We add uncached input, cache reads, cache writes, and output tokens to get *total tokens processed*. This counts repeated context again on each model call, as it should for a usage comparison. We sum Pi's reported `cost.total` over turns. We use Claude's final `total_cost_usd` for Claude Code.
- We opened each result in Chromium and checked animation, Pause, and browser errors. We saved a screenshot in each run directory.

**Comparison limits:** Claude used *low effort* and Pi used *thinking off*, which are not identical settings. Each harness also uses its own instructions and tools. This is intentional for a harness comparison, but it is a confounding factor. We did not use fixed seeds or hold generated HTML size constant. Costs can change with model prices, model updates, cache state, and task complexity.

## What did it cost in subscription quota?

Claude reported the **account-wide** five-hour meter at **27%**, then **29%** during the broader test. The seven-day meter moved from **48%** to **49%**. The broader test also included a Pi pilot, Sonnet budget failures, and budget checks. The counters report whole percentages. Other account activity can affect them.

**We cannot assign a reliable five-hour percentage to any of the three options.** In particular, do not convert the dollar cost above into an exact share of your Claude Pro subscription. Measuring that would require more repeats, a quiet account, and finer quota readings.

## Does a $0.03 cap work?

**Claude Code:** `--max-budget-usd 0.03` works in print mode. **Pi:** version 0.2.4 of the installed subscription extension did **not** expose a command-line dollar cap. The Agent SDK supports `maxBudgetUsd`, so we added it with a [two-file patch](pi-budget.patch). We also added an option to limit the maximum output-token setting.

These caps are **soft**. One model call can use more than the set amount before the SDK returns a budget error. For example, we set a **$0.00001** cap in a small Pi pilot; a model response arrived, and the SDK then returned `Reached maximum budget` with **$0.0002406** of estimated usage. A cap can also stop a request early, before it produces useful output.

For **Sonnet 5.5**, the `$0.03` gate stopped all four attempts we tested (two Claude, two Pi). The Claude gate reported a preflight estimate of about $0.047–$0.048 but **zero actual model tokens**. The Pi gate reported partial costs of $0.00685 or $0.00964, then stopped, without creating HTML. We also tried a lower maximum-output setting. It did not solve the problem. **This does not prove that Sonnet cannot complete the task for three cents.** It only shows that these budget gates stopped it.

See [`budget-probes.json`](budget-probes.json) for the recorded evidence. For this task, **Haiku completed all nine runs well below three cents**. More tests are necessary before setting a student competition budget.

## Run a new budgeted Pi task

First install and sign in to Claude Code. Install Pi and its subscription extension:

```bash
pi install npm:pi-claude-subscription
claude auth status
```

This project does **not** include a full copy of the extension. The launcher copies the *installed* extension to a temporary directory, applies [`pi-budget.patch`](pi-budget.patch), runs the task, and deletes the temporary copy. The patch was made against **pi-claude-subscription 0.2.4**. If the extension changes, the patch can fail; this is safer than silently changing its behavior. The launcher also needs Node.js, `patch`, `timeout`, and the `pi` command.

```bash
cd ~/code/research/claude-pi-tokens
./run-pi-budgeted.sh /tmp/aurora-test "$(cat task.txt)"
```

The default settings are **Haiku 5.5**, **$0.03** estimated maximum cost, **8,192** output tokens per model request, and a **120-second** time limit. Change them with environment variables:

```bash
PI_BUDGET_USD=0.02 PI_MAX_OUTPUT_TOKENS=4096 PI_TIMEOUT_SECONDS=90 \
  ./run-pi-budgeted.sh /tmp/aurora-test-2 "$(cat task.txt)"
```

The generated file is `/tmp/aurora-test/index.html`. The full CLI event log is `/tmp/aurora-test/pi-events.jsonl`. The launcher prints a short JSON usage report. It exits with an error if the final model turn did not finish normally. It cannot prevent a single model call from exceeding the dollar cap.

**Security:** This launcher is for **trusted prompts**, not untrusted student code. Pi's SDK integration grants its tools broad permissions. The CLI options do not sandbox the file system. Before you process student submissions, put each run in a disposable container or virtual machine. Keep secrets out. Restrict its files, CPU time, memory, and network access. Review Anthropic's current terms before using a personal subscription to serve others; use API-key billing for a production student service.

## Recheck the evidence

The Git commit contains the **nine HTML outputs**, their **lossy WebP preview images**, the exact prompt, sanitized usage evidence, the summarizer, and the two-file budget patch. The original verbose JSONL streams stay in this working directory but are **ignored by Git**. They contain local paths and session/request IDs. A reader who clones the repository can still recompute the table from the sanitized evidence:

```bash
node summarize.mjs
cat results.tsv
```

If the original JSONL streams are present locally, regenerate the evidence from them:

```bash
node summarize.mjs --from-raw
```

The summarizer checks the SHA-256 checksum and byte size of every committed HTML output. The unredacted logs are not required to calculate the reported table, but they would be needed to re-audit each API event independently. See [`notes.md`](notes.md) for a dated account of the pilots, failed attempts, and limitations.

**Decision:** For small, one-off HTML-generation tasks, start with **Pi + Haiku + caching enabled**. It was the cheapest option in our small sample. Test more tasks and score the resulting pages before you use this result to select a production harness or a strict budget.
