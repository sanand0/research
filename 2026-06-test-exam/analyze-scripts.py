#!/usr/bin/env -S uv run --script
"""Inventory call expressions in the hallucination-trap archive."""

import ast
import collections
import pathlib


def calls(path: pathlib.Path) -> tuple[str, ...]:
    tree = ast.parse(path.read_text())
    return tuple(sorted(ast.unparse(node.func) for node in ast.walk(tree) if isinstance(node, ast.Call)))


root = pathlib.Path("/tmp/2026-06-test-scripts/scripts")
files = sorted(root.glob("*.py"))
by_function: dict[str, list[tuple[pathlib.Path, tuple[str, ...]]]] = collections.defaultdict(list)

for path in files:
    tree = ast.parse(path.read_text())
    function = next(node.name for node in tree.body if isinstance(node, ast.FunctionDef))
    by_function[function].append((path, calls(path)))

for function, entries in sorted(by_function.items()):
    frequencies = collections.Counter(call for _, file_calls in entries for call in file_calls)
    print(f"\n## {function}: {len(entries)} files")
    for call, count in frequencies.most_common():
        print(f"{count:3} {call}")
