#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "python-chess>=1.999",
#   "typer>=0.15",
# ]
# ///
"""Build JSONL game records and grouped JSON summaries from PGN files."""

from __future__ import annotations

import base64
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import chess.pgn
import typer

app = typer.Typer(add_completion=False, no_args_is_help=True)


def sum_numeric_tree(total: dict[str, Any], value: dict[str, Any]) -> None:
    """Add every numeric leaf from a usage object."""
    for key, item in value.items():
        if isinstance(item, dict):
            target = total.setdefault(key, {})
            if isinstance(target, dict):
                sum_numeric_tree(target, item)
        elif isinstance(item, int | float):
            total[key] = total.get(key, 0) + item


def record_from_pgn(path: Path) -> dict[str, Any]:
    """Convert one PGN into a synchronization-friendly record."""
    with path.open(encoding="utf-8") as handle:
        game = chess.pgn.read_game(handle)
    if game is None:
        raise ValueError(f"No game found in {path}")
    headers = dict(game.headers)
    usage = (
        json.loads(base64.urlsafe_b64decode(headers["APIUsageB64"]))
        if headers.get("APIUsageB64")
        else {}
    )
    return {
        "id": path.stem,
        "pgn_path": str(path),
        "api_log_path": str(path.with_name(headers["APILog"]))
        if headers.get("APILog")
        else None,
        "model": headers.get("Model"),
        "model_color": headers.get("ModelColor"),
        "reasoning_effort": headers.get("ReasoningEffort", "unknown"),
        "stockfish_elo": int(headers["StockfishElo"])
        if headers.get("StockfishElo")
        else None,
        "stockfish_time": float(headers["StockfishTime"])
        if headers.get("StockfishTime")
        else None,
        "result": headers.get("Result"),
        "winner": headers.get("Winner"),
        "termination": headers.get("Termination"),
        "reported_cost": float(headers["ReportedCost"])
        if headers.get("ReportedCost")
        else None,
        "usage": usage,
        "plies": game.end().board().ply(),
        "pgn": str(game),
    }


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Group game outcomes by model and Stockfish Elo."""
    groups: dict[tuple[str, str, int], dict[str, Any]] = defaultdict(
        lambda: {
            "games": 0,
            "model_wins": 0,
            "stockfish_wins": 0,
            "draws": 0,
            "reported_cost": 0.0,
            "games_with_reported_cost": 0,
            "usage": {},
        }
    )
    for record in records:
        key = (
            record["model"],
            record.get("reasoning_effort", "unknown"),
            record["stockfish_elo"],
        )
        group = groups[key]
        group["games"] += 1
        outcome_key = {
            "model": "model_wins",
            "stockfish": "stockfish_wins",
            "draw": "draws",
        }.get(record["winner"])
        if outcome_key:
            group[outcome_key] += 1
        if record["reported_cost"] is not None:
            group["reported_cost"] += record["reported_cost"]
            group["games_with_reported_cost"] += 1
        sum_numeric_tree(group["usage"], record.get("usage", {}))
    return {
        "total_games": len(records),
        "groups": [
            {
                "model": model,
                "reasoning_effort": effort,
                "stockfish_elo": elo,
                **values,
                "reported_cost": values["reported_cost"]
                if values["games_with_reported_cost"]
                else None,
            }
            for (model, effort, elo), values in sorted(groups.items())
        ],
    }


@app.command()
def main(
    pgn_dir: Path = typer.Argument(Path("games"), help="Game artifact root."),
    jsonl_path: Path | None = typer.Option(None, help="Output JSONL path."),
    summary_path: Path | None = typer.Option(None, help="Output summary JSON path."),
) -> None:
    """Rebuild cumulative aggregate files from all PGNs under a directory."""
    jsonl_path = jsonl_path or pgn_dir / "games.jsonl"
    summary_path = summary_path or pgn_dir / "summary.json"
    paths = sorted(pgn_dir.rglob("*.pgn"))
    records = [record_from_pgn(path) for path in paths]
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    jsonl_path.write_text(
        "".join(
            json.dumps(record, ensure_ascii=True, separators=(",", ":")) + "\n"
            for record in records
        ),
        encoding="utf-8",
    )
    summary_path.write_text(
        json.dumps(summarize(records), indent=2) + "\n", encoding="utf-8"
    )
    typer.echo(f"games: {len(records)}")
    typer.echo(f"jsonl: {jsonl_path}")
    typer.echo(f"summary: {summary_path}")


if __name__ == "__main__":
    app()
