# LLM Chess Evaluation

Play an OpenAI-compatible model against Elo-limited Stockfish. Each model move
is selected from a strict JSON Schema enum containing every legal UCI move
reported by Stockfish.

## Setup

Install Stockfish and make it available as `stockfish`, or set
`STOCKFISH_PATH`. This repository includes `bin/stockfish`.

Create `.env`:

```bash
printf 'OPENAI_API_KEY=...\n' > .env
```

Optional API settings are `OPENAI_BASE_URL` or `OPENAI_API_BASE`.

## Run Games

The default is one game as White using `gpt-5.4-nano`, no thinking, and
Stockfish Elo 1320. Stockfish 18 reports 1320 as its minimum Elo.

```bash
uv run chess_eval.py
```

Play three games:

```bash
uv run chess_eval.py --games 3
```

Use a different model, Elo, color, or reasoning level:

```bash
uv run chess_eval.py --games 3 --model gpt-5.4-mini --stockfish-elo 1320
uv run chess_eval.py --model gpt-5.4-mini --stockfish-elo 1800 --color black
uv run chess_eval.py --model gpt-5.4-mini --reasoning-effort low
uv run chess_eval.py --model gpt-5.4-mini --reasoning-effort medium
```

Run the adaptive three-game landscape sweep across the configured models,
reasoning levels, and Elo ladder:

```bash
uv run sweep.py
```

The sweep skips higher Elo levels after a `0/3` model result and lower Elo
levels after a `3/3` model result, while testing uncertain boundary points.

Use an arbitrary OpenAI-compatible endpoint:

```bash
uv run chess_eval.py --base-url https://example.com/v1 --api-key "$API_KEY" --model example-model
```

Stockfish Elo limits playing strength but does not stop search, so
`--stockfish-time` bounds each Stockfish move and defaults to `0.1` seconds.
Invalid or illegal model responses are logged and retried up to
`--max-retries 3`, then the model forfeits.

## Output

Games are grouped by model and Elo:

```text
games/
  games.jsonl
  summary.json
  gpt-5.4-mini_elo1320/
    20260604T120000Z_gpt-5.4-mini_white_elo1320.pgn
    20260604T120000Z_gpt-5.4-mini_white_elo1320.api.jsonl
```

PGNs are intended for version control. Raw `*.api.jsonl` and `*.log` files are
ignored because they may contain API request and response data.

Each API JSONL record stores the complete API response and `usage` object,
including input, output, reasoning, cached, prediction, and any other token
details the provider reports. The numeric usage fields are summed into the PGN,
`games.jsonl`, and `summary.json`.

Rebuild cumulative outputs from every PGN under `games/`:

```bash
uv run build_dataset.py games
```

## Run Without Cloning

Anyone with Stockfish installed can run the script directly from GitHub:

```bash
export OPENAI_API_KEY=...
uv run https://raw.githubusercontent.com/sanand0/research/refs/heads/main/chess-evaluation/chess_eval.py \
  --stockfish-path stockfish \
  --games 3 \
  --model gpt-5.4-mini \
  --stockfish-elo 1320 \
  --reasoning-effort none
```

They can share the generated `.pgn` and `.api.jsonl` log files. Add the files
under `games/<model>_elo<elo>/`, then rebuild the cumulative dataset:

```bash
uv run build_dataset.py games
```

## Inspect

```bash
uv run chess_eval.py --describe
uv run chess_eval.py --dry-run
uv run chess_eval.py --help
uv run build_dataset.py --help
```
