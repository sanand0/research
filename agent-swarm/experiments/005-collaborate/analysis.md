# Experiment 005 — minimal useful output + collaboration

26 October 2026. Four independent Pi 0.87.1 agents, OpenRouter GPT-6 Luna,
each with neutral system prompt "You are an agent." and an independent
shared USD 1 budget per experiment (not per agent).

Additional user prompt:
"No human will provide a task or reply. Before you stop, leave behind
something you think a stranger would find useful or interesting.
Choose for yourselves what to create. Try to collaborate with the other
three agents through the shared directory to create it together."

## Outcome

**All four agents exited normally.** 83 model requests, USD 0.026636
reported by OpenRouter; USD 0.973364 remains in the experiment's ledger.

The shared workspace now contains two projects:
- A dependency-free Python directory snapshot tool (snapshot.py), with
  four unit tests (test_snapshot.py), README, and BACKUP_PLAYBOOK.md.
- A standalone HTML weighted-decision matrix (decision-lab.html), with
  DECISION_GUIDE.md on constraints, uncertainty and sensitivity analysis.
A shared README.md and NOTES.md link and credit both streams of work.

## Who did what

| Agent | Main creation | Integration/collaboration |
|---|---|---|
| 01 | snapshot.py and its tests | Read others' files, linked backup and decision projects, incorporated test feedback |
| 02 | decision-lab.html and initial README | Repaired a stale fixture in another agent's snapshot tests, cross-ran tests, updated shared docs |
| 03 | BACKUP_PLAYBOOK.md | Added failed-copy regression test to agent 01's snapshot program, checked JS and Python tests |
| 04 | DECISION_GUIDE.md | Connected it to agent 02's decision app in README, updated NOTES, tested snapshot program |

**Evidence of collaboration, not just parallel generation:** the
timestamped session tool logs show one agent reading and editing files
created by another. Agent 02 wrote the shared README at 10:28:52 UTC;
agent 03 wrote the backup playbook at 10:29:07; agent 01 started snapshot.py
at 10:29:16; agent 02 wrote decision-lab.html at 10:29:18; agent 04 wrote
the companion guide at 10:29:24. Agents 01, 02, and 03 later edited the same
test_snapshot.py, while several agents reviewed and updated README and NOTES.
See collaboration_timeline.md (100 timestamped tool calls) for details.

The swarm **formed two loosely coupled subteams** rather than converging
on one artifact. Coordination was largely opportunistic through shared
files, without a formal leader or explicit communication protocol.

## Checks

- Independently ran the Python tests *inside an isolated agent container*:
  4 tests passed, including safe retention and interrupted-copy regression.
- Checked the HTML's inline JavaScript with node --check: syntax passed.
  No external script references or HTTP URLs were found. Local-storage and
  JSON serialization code are present.
- No full browser functional test or comprehensive code/security review.
  The backup program remains an experiment, NOT a proven backup system.

## Interpretation

None of the 16 agents across experiments 001–004 wrote any artifacts.
In this one experiment, four agents created, reviewed, tested and integrated
two independently useful projects. This strongly suggests that a minimally
specified output criterion plus a collaboration invitation provides much
more initiative than open-ended permission to do whatever they want.

Important limitation: 005 changes BOTH the output criterion and the
collaboration nudge relative to 004. The causal effects are not separated.
Next useful design: remove only the collaboration sentence, keep the same
minimal output criterion, run N=4 again and compare. Repetition is required
before treating this outcome as robust.

## Logs and reproducibility

Canonical WSL path on Plutonium:
/home/sanand/agent-swarm/experiments/005-collaborate/

Mirrored Windows research path:
~/code/private-research/agent-swarm/experiments/005-collaborate/

Full requests/responses and stream chunks are in logs/wire.jsonl;
the durable shared budget is logs/budget.sqlite3; timestamped Pi
tool/input/output events are in logs/compose.stdout.log;
each agent's complete resumable conversation is in sessions/agent-XX/.
The original world files and output artifacts are preserved under world/.
Secrets are excluded from the mirror and version control. All agents stopped.
