# Working notes

## 2026-06-12

- Done means: obtain the live personalized questions, derive and verify every answer, submit them successfully, and document reproducible evidence.
- Initial `rtk` commands failed inside the sandbox because bubblewrap could not create a namespace. Re-running `rtk` commands with approved escalation works; the failure was logged.
- Downloaded `https://exam.sanand.workers.dev/2026-06-test`; it is a 10,117-byte client-side assessment shell, so the live API/browser state must be inspected.
- Existing unrelated working-tree changes were left untouched.
- Live browser session exposed 10 questions totaling 10 marks.
- Public exam scripts exposed validator contracts and personalized question variants. Validator feedback was used only after deriving answers.
- Deterministic questions 1, 3, 4, 5, 7, 9, and 10 all passed their live validators.
- Robustness optimization required applying a sigmoid to raw model logits. Exhaustive search found `I8, I11, I13, I17, I20; 59; 97.01; 96.68`.
- Downloaded and extracted the 1,000-script archive under `/tmp`. Positional modal-line analysis identified `script_666.py`; the live validator confirmed it.
- Network Game node `91` matched the clues. The server confirmed shortest path `13,72,91`; the exam validator accepted its completion token.
- The binary rubric answer was completed, but its validator could not run because the manually entered AIPipe token returned HTTP 401 `JWSSignatureVerificationFailed`.
- Final exam save succeeded. The page showed `Score: 9 / 10` and recent save `6/12/2026, 3:21:05 PM. Score: 9`.
- Removed the downloaded ZIP because project instructions prohibit committing full copies of fetched code.
