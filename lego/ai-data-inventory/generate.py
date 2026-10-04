#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2",
#   "scipy>=1.15",
# ]
# ///
"""Generate the inventory-constrained 7-high AI↔DATA LEGO sculpture."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csr_matrix, lil_matrix, vstack

HEIGHT = 7

A = ["010", "101", "101", "111", "101", "101", "101"]
I = ["111", "010", "010", "010", "010", "010", "111"]
D = ["110", "101", "101", "101", "101", "101", "110"]
T = ["111", "010", "010", "010", "010", "010", "010"]

LDRAW_COLORS = {
    "white": 15,
    "grey": 72,
    "pink3": 5,
    "green": 2,
    "brown": 70,
    "light_green": 27,
    "red": 4,
    "yellow": 14,
    "black": 0,
    "maroon": 320,
    "blue": 1,
    "orange": 25,
    "pink5": 13,
    "cream": 19,
    "light_blue": 212,
}

SIGNAL_COLOR_BY_COLUMN = {
    # Bright signal palette; dark colors are reserved for supports.
    (4, 0): "light_green",  # 1
    (5, 0): "white",        # 7
    (6, 1): "pink5",        # 2
    (2, 2): "green",        # 5
    (0, 4): "yellow",       # 6
    (1, 5): "pink3",        # 2
    (2, 6): "red",          # 6
    (4, 8): "cream",        # 1
    (5, 9): "light_blue",   # 7
    (4, 10): "white",       # 1
    (2, 12): "orange",      # 6
    (1, 13): "light_blue",  # 2
    (2, 14): "cream",       # 6
}


SUPPORT_PALETTE = [
    ("maroon", 13),
    ("grey", 7),
    ("black", 5),
    ("brown", 3),
]


EXPECTED_COLUMNS = {
    (4, 0), (5, 0), (6, 1), (2, 2), (0, 4), (1, 5), (2, 6),
    (4, 8), (5, 9), (4, 10), (2, 12), (1, 13), (2, 14),
}


def join_letters(letters: list[list[str]]) -> list[str]:
    return ["0".join(letter[row] for letter in letters) for row in range(HEIGHT)]


def solve() -> tuple[np.ndarray, np.ndarray, list[str], list[str]]:
    front_top = join_letters([A, I])
    side_top = join_letters([D, A, T, A])
    width, depth = len(front_top[0]), len(side_top[0])
    assert (width, depth) == (7, 15)

    front = np.array(
        [[int(front_top[HEIGHT - 1 - level][x]) for x in range(width)]
         for level in range(HEIGHT)]
    )
    side = np.array(
        [[int(side_top[HEIGHT - 1 - level][z]) for z in range(depth)]
         for level in range(HEIGHT)]
    )

    index = {
        (x, z, level): (level * width + x) * depth + z
        for level in range(HEIGHT)
        for x in range(width)
        for z in range(depth)
    }
    reverse = [None] * len(index)
    for position, item in index.items():
        reverse[item] = position

    count = len(reverse)
    rows: list[list[tuple[int, int]]] = []
    lower: list[float] = []
    upper: list[float] = []

    for level in range(1, HEIGHT):
        for x in range(width):
            for z in range(depth):
                rows.append([
                    (index[x, z, level], 1),
                    (index[x, z, level - 1], -1),
                ])
                lower.append(-np.inf)
                upper.append(0)

    for level in range(HEIGHT):
        for x in range(width):
            if front[level, x]:
                ids = [
                    index[x, z, level]
                    for z in range(depth)
                    if side[level, z]
                ]
                rows.append([(item, 1) for item in ids])
                lower.append(1)
                upper.append(np.inf)
        for z in range(depth):
            if side[level, z]:
                ids = [
                    index[x, z, level]
                    for x in range(width)
                    if front[level, x]
                ]
                rows.append([(item, 1) for item in ids])
                lower.append(1)
                upper.append(np.inf)

    matrix = lil_matrix((len(rows), count), dtype=float)
    for row, items in enumerate(rows):
        for item, value in items:
            matrix[row, item] = value
    matrix = matrix.tocsr()

    bounds = Bounds(np.zeros(count), np.ones(count))
    integrality = np.ones(count)
    constraint = LinearConstraint(matrix, np.array(lower), np.array(upper))

    first = milp(
        c=np.ones(count),
        integrality=integrality,
        bounds=bounds,
        constraints=constraint,
        options={"time_limit": 30.0, "mip_rel_gap": 0.0},
    )
    if not first.success:
        raise SystemExit(f"Minimum-piece MILP failed: {first.message}")
    minimum = round(first.x.sum())
    assert minimum == 80

    matrix2 = vstack([matrix, csr_matrix(np.ones((1, count)))])
    lower2 = np.r_[lower, minimum]
    upper2 = np.r_[upper, minimum]
    objective = np.array(
        [((x - 3) ** 2) * 1_000_000 + item
         for item, (x, _z, _level) in enumerate(reverse)],
        dtype=float,
    )
    second = milp(
        c=objective,
        integrality=integrality,
        bounds=bounds,
        constraints=LinearConstraint(matrix2, lower2, upper2),
        options={"time_limit": 30.0, "mip_rel_gap": 0.0},
    )
    if not second.success:
        raise SystemExit(f"Aesthetic MILP failed: {second.message}")

    occupied = (second.x > 0.5).reshape(HEIGHT, width, depth)
    signal = np.zeros_like(occupied)
    for level in range(HEIGHT):
        for x in range(width):
            for z in range(depth):
                signal[level, x, z] = (
                    occupied[level, x, z]
                    and front[level, x]
                    and side[level, z]
                )

    actual_columns = {
        (x, z)
        for x in range(width)
        for z in range(depth)
        if occupied[:, x, z].any()
    }
    assert actual_columns == EXPECTED_COLUMNS
    assert int(occupied.sum()) == 80
    assert int(signal.sum()) == 52
    assert int(occupied.sum() - signal.sum()) == 28

    assert all(
        signal[level, x, :].any() == bool(front[level, x])
        for level in range(HEIGHT)
        for x in range(width)
    )
    assert all(
        signal[level, :, z].any() == bool(side[level, z])
        for level in range(HEIGHT)
        for z in range(depth)
    )

    return occupied, signal, front_top, side_top


def write_outputs(output: Path, inventory_path: Path) -> None:
    inventory = Counter(json.loads(inventory_path.read_text()))
    occupied, signal, front_top, side_top = solve()
    height, width, depth = occupied.shape
    output.mkdir(parents=True, exist_ok=True)

    placements: list[dict[str, object]] = []
    for level in range(height):
        for x in range(width):
            for z in range(depth):
                if not occupied[level, x, z]:
                    continue
                placements.append({
                    "x": x + 1,
                    "z": z + 1,
                    "level": level + 1,
                    "color": SIGNAL_COLOR_BY_COLUMN[x, z] if signal[level, x, z] else None,
                    "signal": bool(signal[level, x, z]),
                })

    support_slots = [placement for placement in placements if not placement["signal"]]
    support_slots.sort(key=lambda placement: (placement["z"], placement["x"], placement["level"]))
    support_colors = [
        color
        for color, quantity in SUPPORT_PALETTE
        for _ in range(quantity)
    ]
    assert len(support_slots) == len(support_colors) == 28
    for placement, color in zip(support_slots, support_colors, strict=True):
        placement["color"] = color

    usage = Counter(str(placement["color"]) for placement in placements)
    for color, needed in usage.items():
        available = inventory[color]
        assert needed <= available, f"{color}: need {needed}, have {available}"
    assert sum(usage[color] for color, _quantity in SUPPORT_PALETTE) == 28
    support_total = sum(usage[color] for color, _quantity in SUPPORT_PALETTE)
    assert support_total == 28
    assert sum(usage.values()) - support_total == 52

    (output / "front-ai.txt").write_text(
        "\n".join(row.replace("1", "#").replace("0", ".") for row in front_top) + "\n"
    )
    (output / "side-data.txt").write_text(
        "\n".join(row.replace("1", "#").replace("0", ".") for row in side_top) + "\n"
    )
    (output / "placements.json").write_text(json.dumps(placements, indent=2))

    lines = [
        "0 Inventory-constrained AI / DATA dual-perspective sculpture",
        "0 Name: ai-data.ldr",
        "0 Author: generated with ChatGPT",
        "0 // Front projection: AI; right projection: DATA",
        "0 // Pale bricks = signal; dark bricks = support",
        "1 2 0 0 0 0 0 1 0 1 0 -1 0 0 3857.dat",
        "0 STEP",
    ]

    for level in range(height):
        y = -24 * (level + 1)
        for x in range(width):
            xx = (x - (width - 1) / 2) * 20 + 10
            for z in range(depth):
                if not occupied[level, x, z]:
                    continue
                zz = (z - (depth - 1) / 2) * 20 + 10
                assert (xx + 150) % 20 == 0 and (zz + 310) % 20 == 0
                assert -150 <= xx <= 150 and -310 <= zz <= 310
                placement = next(
                    item
                    for item in placements
                    if item["x"] == x + 1
                    and item["z"] == z + 1
                    and item["level"] == level + 1
                )
                color_name = str(placement["color"])
                color_id = LDRAW_COLORS[color_name]
                lines.append(
                    f"1 {color_id} {xx:g} {y:g} {zz:g} "
                    "1 0 0 0 1 0 0 0 1 3005.dat"
                )
        if level != height - 1:
            lines.append("0 STEP")
    (output / "ai-data.ldr").write_text("\n".join(lines) + "\n")

    with (output / "bom.csv").open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["part", "description", "color", "quantity", "available"])
        for color in sorted(usage):
            writer.writerow(["3005", "Brick 1 x 1", color, usage[color], inventory[color]])
        writer.writerow(["3857", "Baseplate 16 x 32", "green", 1, "existing baseplate"])

    with (output / "inventory-usage.csv").open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["piece", "used", "available", "remaining"])
        for color in inventory:
            used = usage[color]
            writer.writerow([color, used, inventory[color], inventory[color] - used])

    with (output / "columns.csv").open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["x", "z", "height", "bottom_to_top", "signal_pattern"])
        for z in range(depth):
            for x in range(width):
                levels = np.where(occupied[:, x, z])[0]
                if len(levels) == 0:
                    continue
                colors = []
                pattern = []
                for level in levels:
                    is_signal = bool(signal[level, x, z])
                    placement = next(
                        item
                        for item in placements
                        if item["x"] == x + 1
                        and item["z"] == z + 1
                        and item["level"] == level + 1
                    )
                    colors.append(str(placement["color"]))
                    pattern.append("S" if is_signal else "s")
                writer.writerow([
                    x + 1,
                    z + 1,
                    len(levels),
                    " ".join(colors),
                    "".join(pattern),
                ])

    print(
        f"built {output}: 80 1x1 bricks = 52 bright signal + 28 dark support; "
        f"{len(EXPECTED_COLUMNS)} columns",
        flush=True,
    )
    print("usage:", ", ".join(f"{k}={v}" for k, v in sorted(usage.items())))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent / "build",
    )
    args = parser.parse_args()
    write_outputs(args.output, Path(__file__).with_name("inventory.json"))


if __name__ == "__main__":
    main()
