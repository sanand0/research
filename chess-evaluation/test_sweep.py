"""Tests for adaptive sweep boundary selection."""

from collections import Counter

from sweep import next_elo


def test_sweep_starts_lowest_and_stops_after_lowest_loss() -> None:
    assert next_elo({}) == 1320
    assert next_elo({1320: Counter(stockfish=3)}) is None


def test_sweep_jumps_high_after_lowest_win() -> None:
    assert next_elo({1320: Counter(model=3)}) == 2000


def test_sweep_finds_boundary_between_win_and_loss() -> None:
    assert next_elo({1320: Counter(model=3), 2000: Counter(stockfish=3)}) == 1700
