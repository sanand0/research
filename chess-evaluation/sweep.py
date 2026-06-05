#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx>=0.28",
#   "python-dotenv>=1.1",
#   "python-chess>=1.999",
#   "typer>=0.15",
# ]
# ///
"""Adaptively scan model, reasoning-effort, and Stockfish Elo combinations."""

from __future__ import annotations

import os
import shutil
from collections import Counter
from pathlib import Path

import chess.pgn
import typer

from chess_eval import Config, play_game, slug

app = typer.Typer(add_completion=False, no_args_is_help=True)

MODELS = ["gpt-5.4-nano", "gpt-5.4-mini", "gpt-5.5"]
EFFORTS = ["none", "low", "medium", "high", "xhigh"]
ELOS = [1320, 1500, 1700, 1900, 2000]


def outcomes(root: Path, model: str, effort: str, elo: int) -> Counter[str]:
    """Read completed outcomes for one exact combination."""
    result: Counter[str] = Counter()
    for path in sorted((root / f"{slug(model)}_elo{elo}").glob("*.pgn")):
        with path.open(encoding="utf-8") as handle:
            game = chess.pgn.read_game(handle)
        if not game or game.headers.get("Model") != model:
            continue
        if game.headers.get("ReasoningEffort", "unknown") != effort:
            continue
        winner = game.headers.get("Winner")
        if winner in {"model", "stockfish", "draw"}:
            result[winner] += 1
    return result


def next_elo(samples: dict[int, Counter[str]]) -> int | None:
    """Choose the next non-dominated Elo, prioritizing boundary discovery."""
    all_wins = [elo for elo, counts in samples.items() if counts["model"] == 3]
    all_losses = [elo for elo, counts in samples.items() if counts["stockfish"] == 3]
    candidates = [
        elo
        for elo in ELOS
        if elo not in samples
        and not any(win >= elo for win in all_wins)
        and not any(loss <= elo for loss in all_losses)
    ]
    if not candidates:
        return None
    if not samples:
        return ELOS[0]
    if all_wins and not all_losses:
        return candidates[-1]
    if all_losses and not all_wins:
        return candidates[0]
    if all_wins and all_losses:
        midpoint = (max(all_wins) + min(all_losses)) / 2
        return min(candidates, key=lambda elo: abs(elo - midpoint))
    return candidates[0]


@app.command()
def main(
    output_dir: Path = typer.Option(Path("games"), help="Game artifact root."),
    stockfish_path: str = typer.Option(
        os.getenv("STOCKFISH_PATH", "bin/stockfish"), help="Stockfish executable."
    ),
    stockfish_time: float = typer.Option(
        0.1, min=0.001, help="Seconds per Stockfish move."
    ),
    max_plies: int = typer.Option(200, min=1, help="Draw cap in half-moves."),
) -> None:
    """Run the adaptive three-game evaluation landscape."""
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise typer.BadParameter("OPENAI_API_KEY is empty")
    resolved_stockfish = shutil.which(stockfish_path) or stockfish_path
    if not Path(resolved_stockfish).is_file():
        raise typer.BadParameter(f"Stockfish executable not found: {stockfish_path}")

    for model in MODELS:
        for effort in EFFORTS:
            typer.echo(f"\n=== {model} effort={effort} ===")
            while True:
                samples = {
                    elo: outcomes(output_dir, model, effort, elo) for elo in ELOS
                }
                samples = {
                    elo: counts
                    for elo, counts in samples.items()
                    if sum(counts.values()) >= 3
                }
                elo = next_elo(samples)
                if elo is None:
                    typer.echo(f"covered: {dict(samples)}")
                    break
                counts = outcomes(output_dir, model, effort, elo)
                needed = max(0, 3 - sum(counts.values()))
                typer.echo(f"elo={elo}: existing={dict(counts)} playing={needed}")
                config = Config(
                    model=model,
                    color="white",
                    stockfish_path=resolved_stockfish,
                    stockfish_elo=elo,
                    stockfish_time=stockfish_time,
                    base_url=os.getenv("OPENAI_BASE_URL")
                    or os.getenv("OPENAI_API_BASE")
                    or "https://api.openai.com/v1",
                    reasoning_effort=effort,
                    max_retries=3,
                    max_plies=max_plies,
                    output_dir=output_dir / f"{slug(model)}_elo{elo}",
                    structured_output=True,
                )
                for game_number in range(needed):
                    typer.echo(f"sample {game_number + 1}/{needed}")
                    play_game(config, api_key)


if __name__ == "__main__":
    app()
