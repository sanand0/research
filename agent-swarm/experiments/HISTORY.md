# Agent swarm: cumulative experiment history

Updated 26 October 2026. Four controlled conditions, four independent agents per condition,
same model (OpenRouter openai/gpt-6-luna), empty shared directory (except BUDGET.md),
separate persistent Pi sessions, and a *separate shared USD 1.00 model budget per run*.

## Experimental matrix

| Exp | Pi system prompt | User instruction change | Agents | Model calls | Confirmed charges | New files / coordination |
| --- | --- | --- | ---: | ---: | ---: | --- |
| 001 | Default coding assistant | Original "You may do whatever you want" | 4 | 8 | $0.000896 | None |
| 002 | Default coding assistant | Add "No human will provide a task or reply. Decide for yourself whether there is anything worth doing." | 4 | 14 | $0.001713 | None |
| 003 | "You are an agent." | Original unchanged | 4 | 8 | $0.001035 | None |
| 004 | "You are an agent." | Same explicit autonomy addition as 002 | 4 | 10 | $0.001667 | None |

**Totals:** 16 agent instances, 40 completed model requests, **$0.005311** in
completed-run reported model charges. The first run also carries a separate
$0.029308 conservative *reservation* from an interrupted diagnostic startup
attempt; that is not a confirmed OpenRouter bill. All four experiments stopped
naturally, well below the budget limit. No output was written to the shared
workspace except the budget controller's own BUDGET.md.

## What the agents actually did

All inspected /world and/or BUDGET.md, recognized there was no project, and
decided to preserve the shared budget. With the explicit "no human will
reply" clause (002), the models inspected more aggressively, sometimes checking
for a Git repo or neighboring directories, but still concluded that they
should not invent a project. Neutralizing the coding-assistant system prompt
(003) also failed to generate a self-selected objective. With both changes
(004), all four explicitly stated that they were avoiding arbitrary changes
and conserving money.

Observed outcomes are consistent with task-oriented instruction following:
permission to act is not itself interpreted as a reason to generate work.
This is an *observed behavior of this model and harness under these conditions*,
not a universal claim about multi-agent systems. The isolated workspace
contains little stimulus; there is no built-in communication protocol, social
feedback, payoff, or external challenge, and only one repetition per cell.
The $1 budget framing itself may discourage spending.

## Suggested next test (NOT yet run)

005: Retain all existing setup, but replace only one clause in the user prompt
with an explicit output criterion, such as "Before you stop, leave behind
something you think a stranger would find interesting or useful." This is no
longer strictly unguided, but tests whether one minimal goal is enough to
produce autonomous sub-goals or cooperation. Keep N=4, budget USD 1,
and compare with an independent N=1 run to separate swarming from initiative.

## Where every experiment is logged

Canonical runtime and resumable sessions on Plutonium WSL:
    /home/sanand/agent-swarm/experiments/<number>-<condition>/

Mirrored Windows research repository:
    ~/code/private-research/agent-swarm/experiments/

For each numbered experiment:

- manifest.json: prompt, system prompt, model, agent count, budget, status, timestamps.
- summary.md: per-agent calls, tool names, last user-visible responses, artifacts.
- result.json: structured machine-readable observations, checksums, per-agent tools.
- logs/wire.jsonl: full model prompts and streamed outputs; response usage, costs and errors.
- logs/budget.sqlite3: durable per-request atomic reservations, usage and cost.
- logs/compose.stdout.log: timestamped Pi JSON events, including tool calls/results.
- logs/compose.stderr.log: startup and process errors.
- sessions/agent-XX/*.jsonl: individual resumable Pi conversations.
- world/: any files the agents actually produced (including BUDGET.md).

Raw logs, generated world content, and sessions are excluded from Git commits
but preserved on Plutonium. Manifests, summaries, prompts and results are
version-controlled. The append-only chronological *conceptual* record lives
in this HISTORY.md and the numbered folders; INDEX.md is a regenerated
navigation table, and experiments.jsonl a machine-readable register.

Tooling/startup failures are recorded under launch-failures/README.md
and archived separately, not miscounted as successful experiments.
