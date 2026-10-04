#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2",
#   "scipy>=1.15",
# ]
# ///
"""Generate the optimized AI↔DATA dual-perspective LEGO sculpture."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix

HEIGHT = 7

A = ["01110", "10001", "10001", "11111", "10001", "10001", "10001"]
I = ["111", "010", "010", "010", "010", "010", "111"]
D = ["11110", "10001", "10001", "10001", "10001", "10001", "11110"]
T = ["11111", "00100", "00100", "00100", "00100", "00100", "00100"]


def join_letters(letters: list[list[str]]) -> list[str]:
    return ["0".join(letter[row] for letter in letters) for row in range(HEIGHT)]


def solve() -> tuple[np.ndarray, np.ndarray, list[str], list[str]]:
    """Minimize occupied brick positions while preserving both projections and support."""
    front_top = join_letters([A, I])
    side_top = join_letters([D, A, T, A])
    width, depth = len(front_top[0]), len(side_top[0])
    assert (width, depth) == (9, 23)

    front = np.array(
        [[int(front_top[HEIGHT - 1 - level][x]) for x in range(width)] for level in range(HEIGHT)]
    )
    side = np.array(
        [[int(side_top[HEIGHT - 1 - level][z]) for z in range(depth)] for level in range(HEIGHT)]
    )

    def variable(x: int, z: int, level: int) -> int:
        return (level * width + x) * depth + z

    count = width * depth * HEIGHT
    rows: list[list[tuple[int, int]]] = []
    lower: list[float] = []
    upper: list[float] = []

    # Any elevated brick requires the brick directly beneath it.
    for level in range(1, HEIGHT):
        for x in range(width):
            for z in range(depth):
                rows.append([(variable(x, z, level), 1), (variable(x, z, level - 1), -1)])
                lower.append(-np.inf)
                upper.append(0)

    # Every requested pixel in each projection must be represented by at least one
    # occupied cell at an intersection where the other projection is also "on".
    for level in range(HEIGHT):
        for x in range(width):
            if front[level, x]:
                ids = [variable(x, z, level) for z in range(depth) if side[level, z]]
                rows.append([(item, 1) for item in ids])
                lower.append(1)
                upper.append(np.inf)
        for z in range(depth):
            if side[level, z]:
                ids = [variable(x, z, level) for x in range(width) if front[level, x]]
                rows.append([(item, 1) for item in ids])
                lower.append(1)
                upper.append(np.inf)

    constraints = lil_matrix((len(rows), count), dtype=float)
    for row, items in enumerate(rows):
        for item, value in items:
            constraints[row, item] = value

    # The tiny secondary term chooses a stable answer among equal-brick-count optima
    # without ever making one additional brick preferable.
    objective = np.ones(count) + np.arange(count) * (1e-8 / count)
    result = milp(
        c=objective,
        integrality=np.ones(count),
        bounds=Bounds(np.zeros(count), np.ones(count)),
        constraints=LinearConstraint(
            constraints.tocsr(), np.array(lower), np.array(upper)
        ),
        options={"time_limit": 30.0, "mip_rel_gap": 0.0},
    )
    if not result.success:
        raise SystemExit(f"MILP failed: {result.message}")

    occupied = (result.x > 0.5).reshape(HEIGHT, width, depth)
    red = np.zeros_like(occupied)
    for level in range(HEIGHT):
        for x in range(width):
            for z in range(depth):
                red[level, x, z] = (
                    occupied[level, x, z] and front[level, x] and side[level, z]
                )

    assert all(
        red[level, x, :].any() == bool(front[level, x])
        for level in range(HEIGHT)
        for x in range(width)
    )
    assert all(
        red[level, :, z].any() == bool(side[level, z])
        for level in range(HEIGHT)
        for z in range(depth)
    )
    assert all(
        (not occupied[level, x, z]) or occupied[level - 1, x, z]
        for level in range(1, HEIGHT)
        for x in range(width)
        for z in range(depth)
    )
    return occupied, red, front_top, side_top


def write_outputs(output: Path) -> None:
    occupied, red, front_top, side_top = solve()
    height, width, depth = occupied.shape
    output.mkdir(parents=True, exist_ok=True)

    (output / "front-ai.txt").write_text(
        "\n".join(row.replace("1", "#").replace("0", ".") for row in front_top) + "\n"
    )
    (output / "side-data.txt").write_text(
        "\n".join(row.replace("1", "#").replace("0", ".") for row in side_top) + "\n"
    )

    lines = [
        "0 AI / DATA dual-perspective sculpture",
        "0 Name: ai-data.ldr",
        "0 Author: generated with ChatGPT",
        "0 // Front projection: AI; right projection: DATA",
        "0 // 1 LDU = 0.4 mm; stud pitch = 20 LDU; brick height = 24 LDU",
        # Rotate the baseplate so X spans 16 studs and Z spans 32.
        "1 0 0 0 0 0 0 1 0 1 0 -1 0 0 3857.dat",
        "0 STEP",
    ]

    columns: dict[tuple[int, int], tuple[float, float]] = {}
    for level in range(height):
        y = -24 * (level + 1)
        for x in range(width):
            # Odd-sized sculpture on an even-sized baseplate requires a half-stud offset.
            xx = (x - (width - 1) / 2) * 20 + 10
            for z in range(depth):
                if not occupied[level, x, z]:
                    continue
                zz = (z - (depth - 1) / 2) * 20 + 10
                assert (xx + 150) % 20 == 0 and (zz + 310) % 20 == 0
                assert -150 <= xx <= 150 and -310 <= zz <= 310
                color = 4 if red[level, x, z] else 47
                lines.append(
                    f"1 {color} {xx:g} {y:g} {zz:g} 1 0 0 0 1 0 0 0 1 3005.dat"
                )
                columns[x, z] = xx, zz
        if level != height - 1:
            lines.append("0 STEP")
    (output / "ai-data.ldr").write_text("\n".join(lines) + "\n")

    red_count = int(red.sum())
    brick_count = int(occupied.sum())
    clear_count = brick_count - red_count

    with (output / "bom.csv").open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["part", "description", "color", "quantity", "bricklink_color_id"])
        writer.writerow(["3005", "Brick 1 x 1", "Red", red_count, 5])
        writer.writerow(["3005", "Brick 1 x 1", "Trans-Clear", clear_count, 12])
        writer.writerow(["3857", "Baseplate 16 x 32", "Black", 1, 11])

    with (output / "columns.csv").open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["baseplate_x", "baseplate_z", "height_bricks", "stack_bottom_to_top"])
        for x, z in sorted(columns, key=lambda position: (position[1], position[0])):
            xx, zz = columns[x, z]
            base_x = round((xx + 150) / 20) + 1
            base_z = round((zz + 310) / 20) + 1
            top = int(np.where(occupied[:, x, z])[0].max())
            stack = "".join("R" if red[level, x, z] else "C" for level in range(top + 1))
            writer.writerow([base_x, base_z, len(stack), stack])

    (output / "bricklink-wanted-list.xml").write_text(
        f"""<INVENTORY>
  <ITEM><ITEMTYPE>P</ITEMTYPE><ITEMID>3005</ITEMID><COLOR>5</COLOR><MINQTY>{red_count}</MINQTY><REMARKS>AI-DATA red pixels</REMARKS></ITEM>
  <ITEM><ITEMTYPE>P</ITEMTYPE><ITEMID>3005</ITEMID><COLOR>12</COLOR><MINQTY>{clear_count}</MINQTY><REMARKS>AI-DATA clear supports</REMARKS></ITEM>
  <ITEM><ITEMTYPE>P</ITEMTYPE><ITEMID>3857</ITEMID><COLOR>11</COLOR><MINQTY>1</MINQTY><REMARKS>AI-DATA baseplate</REMARKS></ITEM>
</INVENTORY>
"""
    )

    column_count = sum(
        occupied[:, x, z].any() for x in range(width) for z in range(depth)
    )
    print(
        f"built {output}: {brick_count + 1} pieces "
        f"({red_count} red, {clear_count} clear, 1 baseplate), {column_count} columns",
        flush=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent / "build",
        help="Generated-artifact directory",
    )
    args = parser.parse_args()
    write_outputs(args.output)


if __name__ == "__main__":
    main()
