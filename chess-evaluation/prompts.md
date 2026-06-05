# Prompts

## Initial draft, 04 Jun 2026

<!--
cd /home/sanand/code/research/chess-evaluation
dev.sh
codex --yolo --model gpt-5.5 --config model_reasoning_effort=medium
-->

Write a minimal agent-friendly Python CLI that I can run using uv that will play chess and use an LLM API to identify the next set of moves and log the results as a PGN file as well as the LLM API requests and response along with the final cost. The way it should work is that the user should be able to specify an OpenAI compatible API endpoint and an API key, both of which should be picked up from the default environment variables. It should then send a minimal prompt to the LLM model, which the user should be able to specify from the command prompt using the configurations that again can be specified from the command prompt, but default to sensible options. The prompt itself should simply ask for the next moves, providing it the absolute minimum context, saying that it's playing a game of chess against Stockfish. The path to Stockfish should also be a configurable parameter as well as the target Elo level that we want to play it against. In the next iteration, it should take the LLM response, pass it to Stockfish, capture Stockfish's response, and send a new prompt to the same model, giving it the game's history. Provide the game's history and context in the same minimal incremental template possible. Use structured responses where possible to ensure that the output is merely the valid move. There is no need to provide the list of valid moves unless Stockfish explicitly provides that, in which case it can be an enumerated list of possible responses. Log progress as we move by showing on the terminal the move number, who's making what move, and what the move is in chess notation. The aim is to be able to build an incremental database out of this that can be synchronized to a central location. So name the PGN files sensibly, making sure that we capture the timestamp, the model, and other important parameters, not necessarily exhaustively. And accumulate the results in a JSONL file with a standalone script that can parse the PGN files and build the JSONL as well as a JSON summary that captures how often Stockfish won versus the model won for different models at different ELO levels.

Download stockfish and install it.

Interview me for the most important questions that are unclear to you. Plan. Then build.
Run and test. Use the OPENAI_API_KEY in the environment. Test with gpt-5.4-nano with no thinking as a base case.

---

1. The model should play White or Black - via a CLI options
2. If the model returns an invalid or illegal move, the CLI should retry with an error prompt
3. Don't limit Stockfish moves by time or search depth. I think if it you set an ELO target level it handles the rest. See https://github.com/PythonicVarun/llm-chess-evaluation-harness - the way it does it is what I'm thinking of.
4. Just use whatever API pricing the provider reports. No need to calculate it ourselves.

---

Modify the script to use the OPENAI_API_KEY from .env.
Run, and let me know the time and cost to run it with gpt-5.4-nano across 3 games at ELO 1320 (which I believe is the lowest, and should be the default ELO level).

---

Write minimal code to use stockfish to list legal moves and ensure that the LLM response is one of those, using an enum JSON schema. I expect to see no failures due to illegal moves, but if they do happen, log and retry up to 3 times before forfeiting.

Log the token usage (input, output, thinking, cached, ... everything OpenAI API reports).

Restructure `games/` so that:
- folder names are like `gpt-5.4-nano_elo1320`
- file names are as they are
- summary.json and games.jsonl are directly under `games/` and capture all games, cumulatively
- The *.api.jsonl and *.log files are not committed

Rename / modify existing files as needed to fit this structure.

Run and test with 3 games with gpt-5.4-mini at ELO 1320, no thinking.

Document README.md with usage instructions.
- Document how anyone could just run `uv run https://raw.githubusercontent.com/sanand0/research/refs/heads/main/chess-evaluation/chess_eval.py ...` and share the .pgn and log files for me to add to the cumulative summary.
- Document different scenarios - more games, different models, different ELO levels, different thinking levels, etc.

---

FYI: I have `.gitignore`d all `games/*/` and erased the previous gpt-5.4-nano games in the folder `gpt-5.4-nano_elo1320`.

Replay with gpt-5.4-nano and with gpt-5.5.

Run 3 games each with all combinations of:

- Models: gpt-5.4-nano, gpt-5.4-mini, gpt-5.5
- ELO levels: 1320, 1500, 1700, 1900, 2000
- Reasoning effort: minimal/none (check the docs), low, medium, high / xhigh

Don't scan redundant combinations, beyond what's necessary. For example:

- If a model + reasoning effort combination wins all games at a specific ELO level, there's no point testing it at lower ELO levels - it will likely win them all too
- If a model + reasoning effort combination loses all games at a specific ELO level, there's no point testing it at higher ELO levels - it will likely lose them all too

Progressively scan the combinations until you have covered the performance landscape.

--- <!-- steering -->

Run in parallel for speed. No need to modify the script - just run in the background.

--- <!-- steering -->

Sop the processes for now. I will resume later.

<!-- codex resume 019e917a-08a3-7162-9102-d9a860da94bc --yolo -->
