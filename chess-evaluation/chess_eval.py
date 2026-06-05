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
"""Play an LLM against Elo-limited Stockfish and persist evaluation artifacts."""

from __future__ import annotations

import base64
import json
import os
import re
import shutil
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import chess
import chess.engine
import chess.pgn
import httpx
import typer
from dotenv import load_dotenv

load_dotenv(override=True)

app = typer.Typer(add_completion=False, no_args_is_help=True)


@dataclass(frozen=True)
class Config:
    model: str
    color: Literal["white", "black"]
    stockfish_path: str
    stockfish_elo: int
    stockfish_time: float
    base_url: str
    reasoning_effort: str | None
    max_retries: int
    max_plies: int
    output_dir: Path
    structured_output: bool


class APIError(RuntimeError):
    """Raised after an API error response has been persisted."""


def slug(value: str) -> str:
    """Return a filesystem-safe identifier."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-") or "unknown"


def prompt_for(board: chess.Board, color: str, error: str | None = None) -> str:
    """Build the smallest prompt that still fully identifies the current game."""
    history = board.root().variation_san(list(board.move_stack)) or "(start)"
    prompt = f"Play {color} against Stockfish. Moves: {history}"
    return (
        f"{prompt}\nPrevious response was invalid or illegal: {error}"
        if error
        else prompt
    )


def parse_move(response: dict[str, Any]) -> str:
    """Extract a move string from a Chat Completions response."""
    content = response["choices"][0]["message"]["content"]
    if isinstance(content, list):
        content = "".join(
            part.get("text", "") for part in content if isinstance(part, dict)
        )
    payload = json.loads(content)
    move = payload["move"]
    if not isinstance(move, str):
        raise ValueError("move must be a string")
    return move.strip()


def move_schema(legal_moves: list[str]) -> dict[str, Any]:
    """Return a strict schema whose only values are Stockfish legal moves."""
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "chess_move",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {"move": {"type": "string", "enum": legal_moves}},
                "required": ["move"],
                "additionalProperties": False,
            },
        },
    }


def stockfish_legal_moves(
    engine: chess.engine.SimpleEngine, board: chess.Board
) -> list[str]:
    """Ask Stockfish for every legal root move."""
    count = board.legal_moves.count()
    infos = engine.analyse(board, chess.engine.Limit(depth=1), multipv=count)
    moves = sorted({info["pv"][0].uci() for info in infos if info.get("pv")})
    if len(moves) != count:
        raise RuntimeError(f"Stockfish returned {len(moves)} of {count} legal moves")
    return moves


def reported_cost(response: dict[str, Any]) -> float | None:
    """Read cost only when the API provider includes it in the response."""
    for value in (response.get("cost"), response.get("usage", {}).get("cost")):
        if isinstance(value, int | float):
            return float(value)
    return None


def sum_numeric_tree(total: dict[str, Any], value: dict[str, Any]) -> None:
    """Add every numeric leaf from an API usage object."""
    for key, item in value.items():
        if isinstance(item, dict):
            target = total.setdefault(key, {})
            if isinstance(target, dict):
                sum_numeric_tree(target, item)
        elif isinstance(item, int | float):
            total[key] = total.get(key, 0) + item


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    """Append one durable JSON record."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(record, ensure_ascii=True, separators=(",", ":"), default=str)
            + "\n"
        )


def api_request(
    client: httpx.Client,
    config: Config,
    api_key: str,
    prompt: str,
    legal_moves: list[str],
) -> tuple[dict[str, Any], dict[str, Any], int]:
    """Send one OpenAI-compatible Chat Completions request."""
    body: dict[str, Any] = {
        "model": config.model,
        "messages": [{"role": "user", "content": prompt}],
    }
    if config.reasoning_effort:
        body["reasoning_effort"] = config.reasoning_effort
    if config.structured_output:
        body["response_format"] = move_schema(legal_moves)

    response = client.post(
        f"{config.base_url.rstrip('/')}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json=body,
    )
    try:
        payload = response.json()
    except json.JSONDecodeError:
        payload = {"raw_text": response.text}
    return body, payload, response.status_code


def model_move(
    board: chess.Board,
    client: httpx.Client,
    config: Config,
    api_key: str,
    log_path: Path,
    legal_moves: list[str],
) -> chess.Move:
    """Ask until the model returns a legal move or exhausts retries."""
    error: str | None = None
    for attempt in range(1, config.max_retries + 1):
        prompt = prompt_for(board, config.color, error)
        request, response, status_code = api_request(
            client, config, api_key, prompt, legal_moves
        )
        usage = response.get("usage") if isinstance(response.get("usage"), dict) else {}
        append_jsonl(
            log_path,
            {
                "type": "api",
                "timestamp": datetime.now(UTC).isoformat(),
                "ply": board.ply() + 1,
                "attempt": attempt,
                "request": request,
                "response": response,
                "status_code": status_code,
                "usage": usage,
                "reported_cost": reported_cost(response),
            },
        )
        if status_code >= 400:
            raise APIError(f"API returned HTTP {status_code}: {response}")
        try:
            move_text = parse_move(response)
            if move_text not in legal_moves:
                raise ValueError(move_text)
            return chess.Move.from_uci(move_text)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            error = str(exc)
        typer.echo(f"retry {attempt}/{config.max_retries}: {error}", err=True)
    raise RuntimeError(
        f"model failed to provide a legal move after {config.max_retries} attempts"
    )


def configure_engine(engine: chess.engine.SimpleEngine, elo: int) -> None:
    """Configure Stockfish's built-in strength limiter."""
    option = engine.options.get("UCI_Elo")
    if option and option.min is not None and option.max is not None:
        if not option.min <= elo <= option.max:
            raise typer.BadParameter(
                f"Stockfish Elo must be between {option.min} and {option.max}"
            )
    engine.configure({"UCI_LimitStrength": True, "UCI_Elo": elo})


def result_owner(result: str, color: str) -> str:
    """Map a PGN result to model, Stockfish, or draw."""
    if result == "1/2-1/2":
        return "draw"
    model_won = (result == "1-0" and color == "white") or (
        result == "0-1" and color == "black"
    )
    return "model" if model_won else "stockfish"


def write_pgn(
    game: chess.pgn.Game,
    path: Path,
    config: Config,
    started: datetime,
    termination: str,
    log_path: Path,
    total_cost: float | None,
    usage: dict[str, Any],
) -> None:
    """Write a complete PGN with aggregation metadata."""
    result = game.headers.get("Result", "*")
    game.headers.update(
        {
            "Event": "LLM vs Stockfish Evaluation",
            "Site": "local",
            "Date": started.strftime("%Y.%m.%d"),
            "UTCDate": started.strftime("%Y.%m.%d"),
            "UTCTime": started.strftime("%H:%M:%S"),
            "White": config.model
            if config.color == "white"
            else f"Stockfish Elo {config.stockfish_elo}",
            "Black": f"Stockfish Elo {config.stockfish_elo}"
            if config.color == "white"
            else config.model,
            "Result": result,
            "Termination": termination,
            "Model": config.model,
            "ModelColor": config.color,
            "ReasoningEffort": config.reasoning_effort or "omitted",
            "StockfishElo": str(config.stockfish_elo),
            "StockfishTime": str(config.stockfish_time),
            "APIBaseURL": config.base_url,
            "APILog": log_path.name,
            "ReportedCost": "" if total_cost is None else str(total_cost),
            "APIUsageB64": base64.urlsafe_b64encode(
                json.dumps(usage, separators=(",", ":")).encode()
            ).decode(),
            "Winner": result_owner(result, config.color) if result != "*" else "none",
        }
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(game), encoding="utf-8")


def play_game(config: Config, api_key: str) -> Path:
    """Play and persist one game."""
    started = datetime.now(UTC)
    stem = (
        f"{started.strftime('%Y%m%dT%H%M%SZ')}_{slug(config.model)}_"
        f"{config.color}_elo{config.stockfish_elo}_{slug(config.reasoning_effort or 'omitted')}"
    )
    pgn_path = config.output_dir / f"{stem}.pgn"
    log_path = config.output_dir / f"{stem}.api.jsonl"
    board = chess.Board()
    game = chess.pgn.Game()
    node = game
    termination = "normal"

    append_jsonl(
        log_path, {"type": "config", "timestamp": started.isoformat(), **asdict(config)}
    )
    with (
        httpx.Client(timeout=600) as client,
        chess.engine.SimpleEngine.popen_uci(config.stockfish_path) as engine,
    ):
        configure_engine(engine, config.stockfish_elo)
        try:
            while (
                not board.is_game_over(claim_draw=True)
                and board.ply() < config.max_plies
            ):
                model_turn = board.turn == (config.color == "white")
                if model_turn:
                    legal_moves = stockfish_legal_moves(engine, board)
                    move = model_move(
                        board, client, config, api_key, log_path, legal_moves
                    )
                    player = config.model
                else:
                    result = engine.play(
                        board, chess.engine.Limit(time=config.stockfish_time)
                    )
                    move = result.move
                    player = "Stockfish"
                san = board.san(move)
                move_number = f"{board.fullmove_number}{'.' if board.turn else '...'}"
                typer.echo(f"{move_number} {player}: {san}")
                board.push(move)
                node = node.add_variation(move)
        except APIError as exc:
            termination = "model API error"
            game.headers["Result"] = "*"
            typer.echo(str(exc), err=True)
        except RuntimeError as exc:
            termination = "model illegal move forfeit"
            game.headers["Result"] = "0-1" if config.color == "white" else "1-0"
            typer.echo(str(exc), err=True)

    if board.is_game_over(claim_draw=True):
        game.headers["Result"] = board.result(claim_draw=True)
        termination = (
            board.outcome(claim_draw=True).termination.name.lower().replace("_", " ")
        )
    elif board.ply() >= config.max_plies:
        game.headers["Result"] = "1/2-1/2"
        termination = "max plies draw"

    records = [
        json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()
    ]
    costs = [
        record.get("reported_cost") for record in records if record.get("type") == "api"
    ]
    usage: dict[str, Any] = {}
    for record in records:
        if record.get("type") == "api":
            sum_numeric_tree(usage, record.get("usage", {}))
    total_cost = (
        sum(cost for cost in costs if cost is not None)
        if any(cost is not None for cost in costs)
        else None
    )
    append_jsonl(
        log_path,
        {
            "type": "final",
            "timestamp": datetime.now(UTC).isoformat(),
            "result": game.headers["Result"],
            "winner": result_owner(game.headers["Result"], config.color)
            if game.headers["Result"] != "*"
            else "none",
            "termination": termination,
            "reported_cost": total_cost,
            "usage": usage,
        },
    )
    write_pgn(game, pgn_path, config, started, termination, log_path, total_cost, usage)
    typer.echo(f"result: {game.headers['Result']} ({termination})")
    typer.echo(
        f"provider-reported cost: {total_cost if total_cost is not None else 'not reported'}"
    )
    typer.echo(f"usage: {json.dumps(usage, separators=(',', ':'))}")
    typer.echo(f"pgn: {pgn_path}")
    typer.echo(f"api log: {log_path}")
    return pgn_path


def describe() -> None:
    """Print a compact machine-readable CLI description."""
    typer.echo(
        json.dumps(
            {
                "command": "uv run chess_eval.py",
                "writes": [
                    "OUTPUT_DIR/MODEL_eloELO/*.pgn",
                    "OUTPUT_DIR/MODEL_eloELO/*.api.jsonl",
                ],
                "env": [
                    "OPENAI_API_KEY",
                    "OPENAI_BASE_URL",
                    "OPENAI_API_BASE",
                    "STOCKFISH_PATH",
                ],
                "notes": [
                    "Stockfish Elo limits quality, while --stockfish-time bounds each search.",
                    "Cost is null unless the API provider reports a numeric cost.",
                ],
            }
        )
    )


@app.command()
def main(
    model: str = typer.Option("gpt-5.4-nano", help="OpenAI-compatible model ID."),
    color: Literal["white", "black"] = typer.Option("white", help="Model side."),
    stockfish_path: str = typer.Option(
        os.getenv("STOCKFISH_PATH", "bin/stockfish"), help="Stockfish executable."
    ),
    stockfish_elo: int = typer.Option(1320, min=1, help="Target Stockfish UCI Elo."),
    stockfish_time: float = typer.Option(
        0.1, min=0.001, help="Seconds per Stockfish move."
    ),
    base_url: str = typer.Option(
        os.getenv("OPENAI_BASE_URL")
        or os.getenv("OPENAI_API_BASE")
        or "https://api.openai.com/v1",
        help="OpenAI-compatible API base URL.",
    ),
    api_key: str = typer.Option(
        os.getenv("OPENAI_API_KEY", ""), envvar="OPENAI_API_KEY", help="API key."
    ),
    reasoning_effort: str | None = typer.Option(
        "none", help="Reasoning effort, or empty to omit."
    ),
    max_retries: int = typer.Option(3, min=1, help="Model attempts per move."),
    max_plies: int = typer.Option(200, min=1, help="Draw cap in half-moves."),
    games: int = typer.Option(1, min=1, help="Number of games to play."),
    output_dir: Path = typer.Option(Path("games"), help="Artifact root directory."),
    structured_output: bool = typer.Option(
        True, help="Request strict JSON Schema output."
    ),
    dry_run: bool = typer.Option(
        False, help="Validate and print configuration without playing."
    ),
    show_description: bool = typer.Option(
        False, "--describe", help="Print machine-readable usage."
    ),
) -> None:
    """Play one LLM-versus-Stockfish game."""
    if show_description:
        describe()
        raise typer.Exit()
    if not api_key:
        raise typer.BadParameter(
            "API key is empty; set OPENAI_API_KEY or pass --api-key"
        )
    resolved_stockfish = shutil.which(stockfish_path) or stockfish_path
    if not Path(resolved_stockfish).is_file():
        raise typer.BadParameter(f"Stockfish executable not found: {stockfish_path}")
    config = Config(
        model=model,
        color=color,
        stockfish_path=resolved_stockfish,
        stockfish_elo=stockfish_elo,
        stockfish_time=stockfish_time,
        base_url=base_url,
        reasoning_effort=reasoning_effort or None,
        max_retries=max_retries,
        max_plies=max_plies,
        output_dir=output_dir / f"{slug(model)}_elo{stockfish_elo}",
        structured_output=structured_output,
    )
    if dry_run:
        typer.echo(json.dumps(asdict(config), default=str))
        raise typer.Exit()
    for game_number in range(1, games + 1):
        if games > 1:
            typer.echo(f"game {game_number}/{games}")
        play_game(config, api_key)


if __name__ == "__main__":
    app()
