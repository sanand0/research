# Experiment startup failures — 26 October 2026

Failures are kept distinct from experimental outcomes.

- During Experiment 001 setup, the first attempt failed before any model requests because Pi 0.87.1 rejected `--no-mcp`. A second attempt hit unreliable SQLite access on the Windows Docker bind mount after four model streams began. These incomplete streams are represented by a $0.029308 pessimistic reservation in the 001 ledger. The final complete run was performed on native WSL storage.
- Before Experiment 002, a launcher attempt failed because Docker Compose returned a JSON array instead of individual JSON objects. **Zero model requests**. Raw diagnostic: WSL `experiments/launch-failures/002-autonomy-parser-failure/`.
- A subsequent Experiment 002 launcher attempt omitted `--profile run`, starting only the proxy. **Zero model requests**. Raw diagnostic: WSL `experiments/launch-failures/002-autonomy-missing-profile/`.
- Corrected launcher, fresh sessions and budget, then ran 002, 003, and 004 successfully.

All experimental summaries and budgets exclude these failed 002 attempts. See `../HISTORY.md`.
