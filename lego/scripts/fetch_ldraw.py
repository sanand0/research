#!/usr/bin/env -S uv run --script
"""Fetch a minimal recursive LDraw library for one model."""

from __future__ import annotations

import argparse
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE_URL = "https://library.ldraw.org/library/official/"


def download(path: str, root: Path) -> str:
    """Return an official LDraw file, caching it under root."""
    target = root / path
    if target.exists():
        return target.read_text(errors="replace")

    url = BASE_URL + urllib.parse.quote(path, safe="/")
    request = urllib.request.Request(url, headers={"User-Agent": "lego-repro-build/1"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read()
    except urllib.error.HTTPError as exc:
        raise FileNotFoundError(path) from exc

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    print(f"downloaded {path}", flush=True)
    return data.decode(errors="replace")


def dependency_candidates(reference: str) -> list[str]:
    """Map an LDraw type-1 reference to likely official-library paths."""
    ref = reference.replace("\\", "/").lstrip("./")
    lower = ref.lower()
    if lower.startswith(("parts/", "p/")):
        return [ref]
    if lower.startswith("s/"):
        return [f"parts/{ref}"]
    return [f"p/{ref}", f"parts/{ref}"]


def fetch_dependency(reference: str, root: Path) -> tuple[str, str]:
    for candidate in dependency_candidates(reference):
        try:
            return candidate, download(candidate, root)
        except FileNotFoundError:
            continue
    raise SystemExit(f"Could not resolve LDraw dependency: {reference}")


def type1_references(text: str) -> list[str]:
    refs = []
    for line in text.splitlines():
        fields = line.strip().split(maxsplit=14)
        if len(fields) == 15 and fields[0] == "1":
            refs.append(fields[14])
    return refs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parts", type=Path, required=True, help="Text file of top-level *.dat part IDs")
    parser.add_argument("--output", type=Path, required=True, help="Minimal LDraw library directory")
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    download("LDConfig.ldr", args.output)

    top_level = [
        line.strip()
        for line in args.parts.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    queue: list[tuple[str, str | None]] = [(part, None) for part in top_level]
    seen: set[str] = set()
    descriptions: list[tuple[str, str]] = []

    while queue:
        reference, parent = queue.pop()
        if parent is None:
            path = f"parts/{reference}"
            try:
                contents = download(path, args.output)
            except FileNotFoundError as exc:
                raise SystemExit(f"Top-level LDraw part not found: {reference}") from exc
            descriptions.append((reference, contents.splitlines()[0].removeprefix("0 ").strip()))
        else:
            path, contents = fetch_dependency(reference, args.output)

        key = path.casefold()
        if key in seen:
            continue
        seen.add(key)
        queue.extend((child, path) for child in type1_references(contents))

    (args.output / "parts.lst").write_text(
        "".join(f"{part} {description}\n" for part, description in descriptions)
    )
    print(f"LDraw library ready: {len(seen)} geometry files + LDConfig.ldr", flush=True)


if __name__ == "__main__":
    main()
