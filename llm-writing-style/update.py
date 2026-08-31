#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["click>=8.1"]
# ///
"""Fill missing task × style × model outputs in results.json using llm via openrouter."""

from __future__ import annotations

import json
import subprocess
import sys
from itertools import product
from pathlib import Path
from typing import Any

import click

DEFAULT_FILE = Path(__file__).with_name("results.json")


def keyed(items: list[dict[str, Any]], field: str, label: str) -> dict[str, dict[str, Any]]:
    """Index records by a required unique string field."""
    values = {item.get(field) for item in items}
    if None in values or "" in values or len(values) != len(items):
        raise click.ClickException(f"{label} must have unique non-empty {field!r} values")
    return {item[field]: item for item in items}


def load(path: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    """Load and validate the configuration and existing result keys."""
    data = json.loads(path.read_text())
    tasks = keyed(data["tasks"], "id", "tasks")
    styles = keyed(data["styles"], "id", "styles")
    models = data["models"]
    if not models or any(not isinstance(model, str) or not model for model in models) or len(set(models)) != len(models):
        raise click.ClickException("models must be unique non-empty strings")
    for task in tasks.values():
        if not isinstance(task.get("text"), str) or not task["text"]:
            raise click.ClickException(f"task {task['id']!r} needs non-empty text")
    for style in styles.values():
        if not isinstance(style.get("prompt"), str) or not style["prompt"]:
            raise click.ClickException(f"style {style['id']!r} needs a non-empty prompt")
    seen: set[tuple[str, str, str]] = set()
    for result in data.setdefault("results", []):
        key = result.get("task"), result.get("style"), result.get("model")
        if any(not isinstance(value, str) or not value for value in key):
            raise click.ClickException(f"invalid result key: {key}")
        if not isinstance(result.get("output", ""), str):
            raise click.ClickException(f"result output must be a string: {key}")
        if key in seen:
            raise click.ClickException(f"duplicate result: {key}")
        seen.add(key)
    return data, tasks, styles


def save(path: Path, data: dict[str, Any]) -> None:
    """Atomically persist progress so interrupted runs are restartable."""
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    temp.replace(path)


@click.command()
@click.option("--file", "path", type=click.Path(path_type=Path, exists=True, dir_okay=False), default=DEFAULT_FILE, show_default=True)
@click.option("--dry-run", is_flag=True, help="List missing combinations without calling llm.")
@click.option("--describe", is_flag=True, help="Print a machine-readable command description and exit.")
def main(path: Path, dry_run: bool, describe: bool) -> None:
    """Generate every missing task × style × model result."""
    if describe:
        click.echo(json.dumps({
            "file": "JSON file containing tasks[], styles[], models[], results[]",
            "dry_run": "Report missing combinations without writes or model calls",
            "result": {"task": "task id", "style": "style id", "model": "model id", "output": "llm response"},
        }))
        return

    data, tasks, styles = load(path)
    existing = {(row["task"], row["style"], row["model"]): row for row in data["results"]}
    missing = [
        (task, style, model)
        for task, style, model in product(tasks, styles, data["models"])
        if not existing.get((task, style, model), {}).get("output", "").strip()
    ]
    if dry_run:
        click.echo(json.dumps({"file": str(path), "missing": missing, "count": len(missing)}))
        return

    for index, (task_id, style_id, model) in enumerate(missing, 1):
        print(f"[{index}/{len(missing)}] {task_id} × {style_id} × {model}", file=sys.stderr, flush=True)
        prompt = f"{tasks[task_id]['text']}\n\n{styles[style_id]['prompt']}"
        process = subprocess.run(
            ["llm", "--no-stream", "--model", model, prompt],
            capture_output=True,
            text=True,
        )
        if process.returncode:
            raise click.ClickException(f"llm failed for {task_id} × {style_id} × {model}: {process.stderr.strip()}")
        output = process.stdout.strip()
        if not output:
            raise click.ClickException(f"llm returned empty output for {task_id} × {style_id} × {model}")
        row = existing.get((task_id, style_id, model))
        if row is None:
            row = {"task": task_id, "style": style_id, "model": model, "output": output}
            data["results"].append(row)
        else:
            row["output"] = output
        save(path, data)

    click.echo(json.dumps({"file": str(path), "generated": len(missing), "total": len(data["results"])}))


if __name__ == "__main__":
    main()
