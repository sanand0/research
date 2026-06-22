# AI-Era Capability Test, June 2026

Solved and submitted [`2026-06-test`](https://exam.sanand.workers.dev/2026-06-test) for `anand@study.iitm.ac.in` on 2026-06-12.

## Result

- Saved score: **9 / 10**
- Verified correct: questions 1 and 3-10
- Blocked: question 2s external AIPipe judge returned HTTP 401 because its manually entered bearer token had an invalid signature
- Network Game: compromised node `91`; server-confirmed shortest path `13,72,91`

The exam page confirmed the save as submitted and listed the recent official save as `6/12/2026, 3:21:05 PM. Score: 9`.

## Method

1. Inspected the live authenticated exam DOM and public exam-definition scripts.
2. Derived answers locally, then used each questions Check validator for verification.
3. Exhaustively searched all `2^21` prompt-fragment subsets with [`solve-robustness.js`](solve-robustness.js).
4. Analyzed the 1,000-file archive with AST call inventories and positional modal-line comparison. This isolated `script_666.py`, which the live validator confirmed.
5. Solved the weekly graph game using clue-calibrated probes. Node `91` had volume `24,000`, count `3`, inbound/outbound ratio `0.03`, counterparties `5`, and average transaction size `9,480`.

## Artifacts

- [`answers.json`](answers.json): submitted answer text except the short-lived Network Game completion JWT
- [`solve-robustness.js`](solve-robustness.js): exhaustive prompt optimizer
- [`analyze-scripts.py`](analyze-scripts.py): AST call inventory for the downloaded archive
- [`cdp-fill.js`](cdp-fill.js): fills answers into the already-authenticated live exam tab
- [`notes.md`](notes.md): chronological investigation log

The downloaded archive was intentionally excluded because it is a full copy of fetched code.
