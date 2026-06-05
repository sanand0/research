"""Focused tests for the chess evaluation CLI."""

from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import chess
import chess.pgn

from build_dataset import record_from_pgn, summarize
from chess_eval import (
    Config,
    move_schema,
    model_move,
    parse_move,
    prompt_for,
    reported_cost,
    result_owner,
)


class FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        self.status_code = 200

    def json(self) -> dict[str, Any]:
        return self.payload


class FakeClient:
    def __init__(self, moves: list[str]) -> None:
        self.moves = iter(moves)

    def post(self, *args: Any, **kwargs: Any) -> FakeResponse:
        move = next(self.moves)
        return FakeResponse(
            {"choices": [{"message": {"content": f'{{"move":"{move}"}}'}}]}
        )


def test_prompt_is_minimal_and_incremental() -> None:
    board = chess.Board()
    board.push_uci("e2e4")
    prompt = prompt_for(board, "black")
    assert prompt == "Play black against Stockfish. Moves: 1. e4"
    assert "legal_moves" not in prompt
    assert "fen" not in prompt.lower()


def test_dotenv_dependency_is_available() -> None:
    from dotenv import load_dotenv

    assert callable(load_dotenv)


def test_dotenv_overrides_empty_environment_key(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("OPENAI_API_KEY=from-dotenv\n", encoding="utf-8")
    env = {**os.environ, "OPENAI_API_KEY": "", "PYTHONPATH": str(Path(__file__).parent)}
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import chess_eval; print(chess_eval.os.getenv('OPENAI_API_KEY'))",
        ],
        cwd=tmp_path,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "from-dotenv"


def test_parse_move_and_reported_cost() -> None:
    response = {
        "choices": [{"message": {"content": '{"move":"e2e4"}'}}],
        "usage": {"cost": 0.001},
    }
    assert parse_move(response) == "e2e4"
    assert reported_cost(response) == 0.001
    assert reported_cost({"usage": {"prompt_tokens": 5}}) is None


def test_move_schema_enumerates_legal_moves() -> None:
    schema = move_schema(["e2e4", "d2d4"])
    assert schema["json_schema"]["schema"]["properties"]["move"]["enum"] == [
        "e2e4",
        "d2d4",
    ]


def test_result_owner() -> None:
    assert result_owner("1-0", "white") == "model"
    assert result_owner("0-1", "white") == "stockfish"
    assert result_owner("1/2-1/2", "black") == "draw"


def test_model_retries_illegal_move(tmp_path: Path) -> None:
    config = Config(
        model="test-model",
        color="white",
        stockfish_path="stockfish",
        stockfish_elo=1320,
        stockfish_time=0.1,
        base_url="http://example.test/v1",
        reasoning_effort=None,
        max_retries=2,
        max_plies=2,
        output_dir=tmp_path,
        structured_output=True,
    )
    log_path = tmp_path / "api.jsonl"
    move = model_move(
        chess.Board(),
        FakeClient(["e2e5", "e2e4"]),
        config,
        "key",
        log_path,
        ["e2e4", "d2d4"],
    )  # type: ignore[arg-type]
    assert move == chess.Move.from_uci("e2e4")
    records = log_path.read_text(encoding="utf-8").splitlines()
    assert len(records) == 2
    assert "Previous response was invalid or illegal: e2e5" in records[1]


def test_record_and_summary(tmp_path: Path) -> None:
    game = chess.pgn.Game()
    game.headers.update(
        {
            "Model": "test-model",
            "ModelColor": "white",
            "ReasoningEffort": "none",
            "StockfishElo": "1320",
            "StockfishTime": "0.1",
            "Result": "1-0",
            "Winner": "model",
            "Termination": "checkmate",
            "ReportedCost": "0.25",
            "APILog": "game.api.jsonl",
            "APIUsageB64": base64.urlsafe_b64encode(
                json.dumps({"prompt_tokens": 10}).encode()
            ).decode(),
        }
    )
    path = tmp_path / "game.pgn"
    path.write_text(str(game), encoding="utf-8")
    record = record_from_pgn(path)
    assert record["reported_cost"] == 0.25
    assert record["reasoning_effort"] == "none"
    assert record["usage"]["prompt_tokens"] == 10
    summary = summarize([record])
    assert summary["groups"][0]["model_wins"] == 1
    assert summary["groups"][0]["reported_cost"] == 0.25


def test_summary_distinguishes_unreported_cost() -> None:
    summary = summarize(
        [
            {
                "model": "test-model",
                "reasoning_effort": "none",
                "stockfish_elo": 1320,
                "winner": "stockfish",
                "reported_cost": None,
                "usage": {
                    "prompt_tokens": 10,
                    "prompt_tokens_details": {"cached_tokens": 4},
                },
            }
        ]
    )
    assert summary["groups"][0]["reported_cost"] is None
    assert summary["groups"][0]["usage"]["prompt_tokens"] == 10
    assert summary["groups"][0]["usage"]["prompt_tokens_details"]["cached_tokens"] == 4
