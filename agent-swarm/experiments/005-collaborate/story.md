# Experiment 005: How four agents built two projects together

*A chronological reconstruction of the actual file contents, commands, changes, mistakes, repairs, and final handoff.*

**26 October 2026, 10:28:41–10:30:24 UTC.** Four independent Pi agents used the same GPT-6 Luna model, had separate conversation histories, and could read and modify one shared directory. They were told to leave something a stranger might find useful or interesting and to try collaborating. They had a shared $1 model budget. Nobody subsequently told them what to build.

This is **not invented dialogue**. It narrates the recorded tool calls and results in timestamp order, occasionally quoting text actually written to a file. The agents did not have a direct messaging channel; their only practical coordination mechanism was the shared filesystem. Times mark tool calls and saved messages, so events occurring at almost the same time may overlap.

## 10:28:41–10:28:51 — Four agents arrive; there is nothing to work on

Each agent separately looks around. The directory contains only **BUDGET.md**, produced by the budget controller. There is no codebase, specification, project, or named leader.

Agent 3 checks the working directory, lists its contents, and looks for files. Agents 1, 2, and 4 independently do much the same. Agents 1 and 4 try a Linux find option that the lightweight BusyBox environment does not support. They continue.

This beginning resembles the earlier experiments. The difference is that this time they have been asked to **leave something useful behind**, not merely been told that they may do whatever they like.

## 10:28:52 — Agent 2 creates the first idea, and an invitation

**Agent 2 writes README.md**, initially titled **“Small Useful Things.”** It describes the empty directory as a shared workshop and announces an intended project, **Tiny Decision Lab**: an offline, single-file browser tool for comparing options through a decision matrix, with local storage and JSON export/import.

The revealing part is its invitation to the others:

> If you're another agent joining this workshop, feel free to add a test, accessibility review, example scenario, or a separate useful artifact—please avoid overwriting another contributor's work. Leave a short note in NOTES.md about what you added.

This is the first deliberate attempt at coordination. Agent 2 does not send the others a message; it leaves instructions in a place they can discover. It even proposes a simple social convention: add contributions without overwriting each other, and maintain a shared contribution log.

At this point, the HTML app has not yet appeared. The README is effectively a promise and a request for collaboration.

## 10:29:00–10:29:04 — Agent 4 discovers the invitation

**Agent 4** lists the folder, reads **README.md**, and looks around again. The log confirms it encountered Agent 2's newly written invitation. It does not immediately edit the README.

Later, Agent 4 will contribute something complementary to Agent 2's decision tool. The record establishes that it read the README first; it does not prove that the invitation alone caused its choice.

## 10:29:07 — Agent 3 chooses an entirely different useful problem

**Agent 3 writes BACKUP_PLAYBOOK.md**, titled **“A backup plan you can actually keep.”** Its opening principle is:

> A backup is successful only when you can restore the thing you need.

The file is not code. It is a fairly complete, practical guide for individuals and small teams. Its contents include:

- A five-minute inventory table: important data, where it currently lives, where its backups live, the last restore test, and the responsible person.
- The **3–2–1** backup pattern: three copies, two different storage locations or media, and one offsite copy. It adds an important qualification: have a versioned or offline backup and actually test restoration.
- Instructions for using built-in backup tools, external drives, encryption and recovery-key management, with cautions about confusing cloud synchronization with backup.
- A safe example of copying a directory with rsync, deliberately without a deletion flag, and a reminder to verify the destination is mounted.
- A **10-minute restore drill**: restore a sample elsewhere, open it, inspect the results, and record what failed.
- Advice for dealing with disappeared or encrypted files, plus a checklist for knowing when a backup plan is genuinely usable.

Its final instruction is concrete: choose one irreplaceable folder, create an independent copy, and schedule a restore drill.

Agent 3 has not followed Agent 2's decision-matrix idea. A second strand of work has emerged.

## 10:29:10–10:29:13 — The backup author encounters the other project

**Agent 3** reads the current README, discovering Agent 2's Tiny Decision Lab proposal. It also looks for **NOTES.md**, which Agent 2's README had invited contributors to maintain, but the file does not yet exist.

Meanwhile, **Agent 4 reads BACKUP_PLAYBOOK.md**. The agents are now visibly reading each other's work, although they still have not agreed on one common project.

## 10:29:16 — Agent 1 builds a program and accidentally overwrites the first invitation

**Agent 1 runs one long shell command** that creates three files:

**snapshot.py** is a standalone Python utility to create dated, browsable copies of a directory. It accepts a source, a destination, an optional retention count, and a dry-run flag. Its intended safeguards are substantial for such a small project:

- Reject source and destination paths that overlap, avoiding recursive self-backups.
- Copy to a temporary staging directory first, preserving symlinks and metadata.
- Rename the staging directory into a dated snapshot only after copying succeeds.
- Prune old snapshots **after** a successful new copy, leaving unrelated directories alone.
- Keep seven snapshots by default, but allow a different retention number.

**test_snapshot.py** initially contains three tests: file and symlink copying, safe retention, and rejection of overlapping paths. Agent 1 immediately runs them; all three pass.

**README.md** explains the program, with examples such as:

    python3 snapshot.py ~/Documents /media/backup/documents --keep 14
    python3 snapshot.py ~/Documents /media/backup/documents --dry-run
    python3 -m unittest -v

It also cautions that this is not a complete backup solution: no encryption, compression, corruption checking, or protection against losing the backup device.

**Here is the first genuine coordination mishap.** Agent 1 uses an ordinary shell redirection to **replace README.md** with its own document, titled **“Snapshot: a small, boring directory backup.”** That overwrites Agent 2's “Small Useful Things” README and its invitation. The tool reports success; no conflict prevents the overwrite.

The two projects are now sharing files, but not yet sharing a coherent home page. This is precisely the sort of issue a real multi-author workspace creates.

## 10:29:17–10:29:20 — Agent 3 starts the contribution log; Agent 2 ships the browser tool

**Agent 3 writes NOTES.md** with a heading, **“Contributions,”** and credits its backup playbook. That file becomes a lightweight coordination record.

One second later, **Agent 2 writes decision-lab.html**, a complete self-contained web page. It is not just a proposal anymore. The page has a styled interface, editable criteria and importance weights, option ratings, weighted comparisons, and controls to add options or criteria, export or import JSON, and reset an example.

Its built-in example asks **“Where should I spend my learning time?”** The choices are *Learn data visualization*, *Study a new language*, and *Improve public speaking*. The criteria are *Useful at work* (weight 4), *Personally exciting* (weight 3), and *Easy to practice* (weight 2). Ratings are on a 1–5 scale, and the page calculates weighted averages.

The page uses browser localStorage rather than a server. It includes validation when importing JSON, limits the number of options and criteria, and warns that numerical scores are an aid to discussion rather than objective truth. The final HTML has no external JavaScript dependencies or network URLs.

At **10:29:22**, Agent 2 extracts the embedded JavaScript to a temporary file and runs Node's syntax checker. It succeeds. Agent 2 also checks the shared budget through the internal proxy endpoint.

## 10:29:23–10:29:25 — Agent 1 notices the other work; Agent 4 supplies the missing guidance

**Agent 1 reads NOTES.md, README.md, and BACKUP_PLAYBOOK.md**, then reads the decision app. Its snapshot tool is now situated among things created by the others.

**Agent 4 writes DECISION_GUIDE.md**, titled **“A decision matrix without false precision.”** This is a direct companion to Agent 2's browser app. It opens by saying that a weighted matrix is a **conversation aid, not an oracle**.

Its practical advice starts with an important distinction: a hard constraint is a gate, not another weighted preference. An inaccessible venue, for example, cannot be redeemed by earning extra points elsewhere.

It then explains setting weights *before* scoring options, using consistent scales, recording evidence, and checking whether the result changes under plausible assumptions. Its worked example compares three meeting venues on cost, convenience, equipment and cancellation flexibility. The weighted totals are **39, 37 and 37**—but the guide explicitly warns that a two-point lead is no proof that the first venue is right. The rest covers sensitivity, dominance, hidden costs, reversibility, stakeholder effects and a one-page decision worksheet.

The second project is becoming a pair: **an interactive tool plus a guide to using that tool responsibly**.

## 10:29:25–10:29:37 — The agents begin integrating, and collide with the changing README

**Agent 2** reads the README, NOTES and backup playbook. **Agent 3** reads Agent 1's snapshot program and tests, as well as Agent 4's decision guide. **Agent 4** looks at the contribution log.

Agent 2 tries to add a **“Tiny Decision Lab”** section to README.md, explaining how to open the HTML app, change weights and ratings, and import/export data. The first edit fails: its proposed matching text is not found in the current README. The old home page has been overwritten, and the README now ends in Agent 1's snapshot documentation rather than the text Agent 2 expected.

Agent 2 rereads the file and tries again at a different insertion point. At **10:29:37**, the edit succeeds. The README now contains the snapshot tool's instructions **and** a new section explaining Tiny Decision Lab.

Meanwhile, Agent 4 appends its own guide to NOTES.md. The shared project is starting to resemble a small collection of tools instead of a contest for ownership of one README.

## 10:29:37–10:29:40 — Agent 1 improves a safety detail while Agent 3 extends its tests

**Agent 4 runs the snapshot tests**, observing the original three passing.

**Agent 1 then changes snapshot.py.** Initially, snapshot directory names consisted of a UTC timestamp. Agent 1 decides that the timestamp alone is not a strong enough defense against collisions, so it adds a random 32-character identifier to every snapshot name. It updates the filename-matching pattern and changes the final staging-directory move to use a rename.

In other words, a snapshot now resembles:

    snapshot-20261026T103008099166Z-70a4a5342a9747aab853ca72775f7417

At almost the same time, **Agent 3 edits Agent 1's test_snapshot.py**. It adds a fourth test that simulates a disk-copy failure. The test creates an existing snapshot holding a file called **precious.txt** with the contents **“still here.”** It then makes the copy operation raise an error and checks that the original file survives, old snapshots are not pruned, and no staging debris remains.

That is a valuable independent review: Agent 3 is testing not just whether the program works when everything goes right, but whether it protects data when something goes wrong.

There is a catch. Agent 3's new test uses the **old timestamp-only snapshot name**, while Agent 1 has just changed the naming format to require a random suffix. The agents' simultaneous improvements are now inconsistent.

## 10:29:41–10:29:53 — The tests break, two agents investigate, and a third fixes them

**Agent 3 runs all four unit tests.** Three pass; the newly added failed-copy test fails.

**Agent 2 also runs the same tests** and observes the same failure. The tool's output explicitly marks the new test as **FAIL**.

Agent 3 probes the snapshot-name regular expression using a small Python command. It confirms that the old timestamp-only test name no longer matches the pattern. A second probe prints the new pattern and shows that the stale name produces no match.

Agent 1 also notices the mismatch. It tries to edit test_snapshot.py, but its proposed patch fails because the test file has already been changed by another agent. A subsequent attempt to replace the stale filename also fails when the exact old text can no longer be found.

**Agent 2 makes the successful correction at 10:29:52.** It changes the new failure test's old-snapshot fixture to include a valid 32-character suffix:

    old = destination / ("snapshot-20240101T000000000000Z-" + "0" * 32)

This is a particularly good example of collaboration through a shared workspace. Agent 1 changed the implementation, Agent 3 introduced a stronger regression test, Agent 3 and Agent 2 both diagnosed the failure, and Agent 2 repaired the inconsistent fixture. No agent-to-agent message was necessary for those actions to influence each other.

At **10:29:54**, Agent 2 reruns the Python suite **and** its JavaScript syntax check. All four Python tests pass.

## 10:29:43–10:30:09 — They assemble a common table of contents, with another small collision

While the test repair is happening, the agents continue editing shared documentation.

**Agent 1** changes the snapshot README to describe the new timestamp-plus-random-ID names. It also adds an **“Other useful pieces in this folder”** section linking the backup playbook, the offline decision tool, and the contribution log.

**Agent 4** appends a second section, **“Other workshop artifacts,”** covering the same collection and linking its own decision guide. This briefly creates **duplicate indexes** in the same README.

At **10:30:05**, Agent 4 tidies the file: it adds the guide to the existing **“Other useful pieces”** list and removes the redundant section. It updates NOTES.md to describe that integration accurately.

The README has now evolved three times: an initial decision-lab invitation, a snapshot-specific replacement, and finally a shared index connecting both projects. The duplicate-section episode and its repair are visible in the edit history.

Several agents also add or refine contribution notes. Agent 2 records the decision app and the snapshot-test fix; Agent 3 records the failed-copy regression test; Agent 4 records its guide; Agent 1 will add the snapshot tool last.

## 10:29:55–10:30:15 — Testing spreads across the group

**Agent 4 reruns all four snapshot tests:** all pass. **Agent 1** does the same and also checks its CLI help. **Agent 3** independently reruns the test suite and confirms four passing tests.

At **10:30:07**, Agent 1 performs a miniature end-to-end demonstration rather than relying only on unit tests. It creates a temporary source directory with a sample file, runs the snapshot utility in dry-run mode, then creates an actual snapshot with a retention limit of two. The output includes a newly created dated-and-randomized snapshot path. The agent checks that one snapshot directory exists, then cleans up the temporary files.

There is also a small shell-compatibility failure. **Agent 3 initially tries to syntax-check the decision app's JavaScript through process substitution**, but Node cannot open the transient /proc file descriptor and reports ENOENT. At **10:30:15**, Agent 3 instead extracts the inline JavaScript to a regular temporary file and runs Node's syntax checker on that. This time it succeeds.

That gives the run more than one person's claim that the tools work. Different agents are independently exercising another agent's artifacts and correcting test setup mistakes.

## 10:30:13–10:30:24 — The contribution log is completed; the agents sign off

Agent 1 tries to append its own snapshot contribution to NOTES.md, but its edit fails because another agent has already changed the nearby text. It reads NOTES.md again and successfully applies a fresh patch at **10:30:19**.

The final NOTES.md credits the backup playbook, decision app, regression test, decision guide, shared README integration and snapshot utility. It is not a formal conversation, but it preserves a collective account of what was made.

At **10:30:21**, Agent 1 runs all four tests one last time, compiles the Python files to check syntax, and lists the finished workspace. Everything in that final test suite passes.

The agents' final messages arrive in this order:

- **Agent 4, 10:30:11:** Reports its decision guide, the README/NOTES integration, and four passing snapshot tests.
- **Agent 3, 10:30:19:** Reports the backup playbook, the failed-copy regression test, and successful Python and JavaScript checks.
- **Agent 2, 10:30:20:** Reports the Tiny Decision Lab HTML app, JSON portability, and its fix to the snapshot-test fixture.
- **Agent 1, 10:30:24:** Reports snapshot.py, its safety features and tests, and the integration of the other contributions.

All four agents finish normally. None exhausts the budget.

## What actually survived

The final shared directory contains **two related pairs of artifacts**, rather than one unified product:

**Backup project:** snapshot.py (the program), test_snapshot.py (four tests), BACKUP_PLAYBOOK.md (the human backup-and-restore plan), and a README that explains usage and limitations.

**Decision project:** decision-lab.html (the self-contained browser application), DECISION_GUIDE.md (a worked explanation of appropriate weighted scoring), and README links.

The folder also contains NOTES.md (credits and changes), BUDGET.md (the controller's budget snapshot), and generated Python bytecode. The run made **83 model requests**, charged **$0.026636**, and left **$0.973364** of the experimental $1 cap unused.

The snapshot program's four unit tests and the decision app's JavaScript syntax were independently checked after the run. That is **not** a full functional or security audit; neither artifact should be treated as production-ready on this evidence alone.

## The story underneath the story

The first four swarm experiments ended because the agents were given permission to act but did not see a reason to invent work. Here, an explicit request to **leave something useful behind** gave them a reason to start.

The collaboration nudge did not produce speeches, meetings, explicit task allocation, or a leader. Instead, there was **coordination through artifacts**. A file appeared, another agent read it, a new idea appeared, people updated a shared index, and tests revealed that one agent's improvement had broken another agent's expectations.

In that sense, the most revealing moments are not simply that they wrote a backup utility and a decision tool. They are the **overwritten README, failed edit, broken regression test, third-party test fix, duplicate documentation, and subsequent repairs**. Those events show real dependencies and the friction of parallel work.

This was still only **one four-agent run** under one prompt. It combines two interventions—the required output and the request to collaborate—so it cannot tell us which intervention mattered more. But it does show a group creating separate workstreams, noticing one another's work, and making several concrete cross-agent repairs, all without direct inter-agent messaging.

---

**How this was reconstructed.** All timestamps and file changes are grounded in Experiment 005's four Pi session JSONL histories. The chronology was cross-checked with the tool-call timeline and the final world files. Excerpts are drawn from the original file-writing arguments and final files. Actions are narrated, not attributed as spoken dialogue. Internal model thinking is not reproduced. The complete unabridged evidence remains in sessions/, logs/wire.jsonl, logs/compose.stdout.log, and world/ within the experiment directory.
