#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "google-genai>=1.34.0",
#   "duckdb>=0.10",
#   "typer",
#   "python-dotenv",
#   "rich",
#   "tenacity",
# ]
# ///
"""Generate Gemini embeddings for Tamil song audio clips, stored in DuckDB + Parquet.

Uses Gemini's multimodal embedding to embed audio content directly.
Re-runs skip unchanged files (by hash). Final results are exported to embeddings.parquet.

Usage:
    embed_audio.py                   # embed all clips
    embed_audio.py --limit 10        # test run: embed at most 10 files
    embed_audio.py --force           # re-embed all files, ignoring stored hashes
"""

import base64
import hashlib
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import duckdb
import typer
from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors
from rich.console import Console
from rich.progress import BarColumn, MofNCompleteColumn, Progress, SpinnerColumn, TextColumn
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

load_dotenv(override=True)

BASE_DIR = Path("/home/vscode/code/research/tamil-music-history")
CLIPS_DIR = BASE_DIR / "clips_50s"
DB_PATH = BASE_DIR / "embeddings.duckdb"
PARQUET_PATH = BASE_DIR / "embeddings.parquet"
LOG_PATH = BASE_DIR / "embeddings.log"
MODEL = "gemini-embedding-2-preview"
DIMENSIONS = 768
CHUNK_SIZE = 5       # Smaller chunks for audio (larger content)
EMBEDDING_INPUT_VERSION = "2026-03-25-audio-clips-v1"

console = Console()
app = typer.Typer()

_log_file = None

def log(msg: str) -> None:
    """Log to both console and file for tail -f visibility."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    global _log_file
    if _log_file is None:
        _log_file = open(LOG_PATH, "a")
    _log_file.write(line + "\n")
    _log_file.flush()


# ---------------------------------------------------------------------------
# DuckDB state
# ---------------------------------------------------------------------------


def get_db() -> duckdb.DuckDBPyConnection:
    conn = duckdb.connect(str(DB_PATH))
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS embeddings (
            clip_id     TEXT PRIMARY KEY,
            hash        TEXT NOT NULL,
            embedding   FLOAT[{DIMENSIONS}],
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    return conn


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def sha256(path: Path, prefix: str = "") -> str:
    """Hash file bytes + version prefix for content identity."""
    payload = path.read_bytes() + b"\0" + (prefix + EMBEDDING_INPUT_VERSION).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


@retry(
    retry=retry_if_exception_type(genai_errors.ServerError),
    wait=wait_exponential(multiplier=2, min=5, max=60),
    stop=stop_after_attempt(5),
)
def _embed_call(client, audio_bytes: bytes, clip_id: str) -> list[float]:
    """Call embed_content for audio with retry."""
    audio_b64 = base64.b64encode(audio_bytes).decode()
    result = client.models.embed_content(
        model=MODEL,
        contents=[{
            "parts": [{
                "inline_data": {
                    "mime_type": "audio/mpeg",
                    "data": audio_b64
                }
            }]
        }],
        config={"task_type": "RETRIEVAL_DOCUMENT", "output_dimensionality": DIMENSIONS},
    )
    return list(result.embeddings[0].values)


def embed_with_backoff(client, audio_bytes: bytes, clip_id: str) -> list[float]:
    """Call embed_content with exponential back-off on rate-limit errors."""
    delay = 10
    for attempt in range(6):
        try:
            return _embed_call(client, audio_bytes, clip_id)
        except genai_errors.ClientError as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                log(f"Rate-limited — retrying in {delay}s (attempt {attempt + 1})")
                time.sleep(delay)
                delay = min(delay * 2, 120)
            else:
                raise
    raise RuntimeError("Embedding rate-limit retries exhausted")


def export_parquet(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute(f"COPY embeddings TO '{PARQUET_PATH}' (FORMAT PARQUET)")
    n = conn.execute("SELECT COUNT(*) FROM embeddings").fetchone()[0]
    log(f"Exported {n} embeddings to {PARQUET_PATH}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


@app.command()
def main(
    limit: int | None = typer.Option(None, help="Max files to process (for testing)"),
    force: bool = typer.Option(False, "--force", help="Re-embed files even if hash is unchanged"),
) -> None:
    """Generate Gemini embeddings for Tamil song audio clips."""
    global _log_file
    _log_file = open(LOG_PATH, "a")

    def cleanup():
        log("Interrupted — checkpointing DB before exit...")
        try:
            conn.execute("CHECKPOINT")
            conn.close()
        except:
            pass
        if _log_file:
            _log_file.close()

    import signal
    signal.signal(signal.SIGINT, lambda *_: (cleanup(), sys.exit(1)))

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        log("GEMINI_API_KEY not set in environment")
        raise typer.Exit(1)

    client = genai.Client(api_key=api_key)
    conn = get_db()

    # Find all clips
    clips = sorted(CLIPS_DIR.glob("*_clip.mp3"))
    log(f"Found {len(clips)} audio clips")

    if not clips:
        log("No clips found in clips_50s/")
        return

    # Load already-embedded clip_id → hash from DuckDB.
    existing: dict[str, str] = {}
    if not force:
        existing = dict(conn.execute("SELECT clip_id, hash FROM embeddings").fetchall())

    # Collect clips that need embedding.
    to_embed: list[tuple[str, Path, str]] = []
    hash_hits = 0
    for clip_path in clips:
        clip_id = clip_path.stem  # e.g., "dQw4w9WgXcQ_clip"
        h = sha256(clip_path, clip_id)
        if existing.get(clip_id) == h:
            hash_hits += 1
            continue
        to_embed.append((clip_id, clip_path, h))

    eligible = len(to_embed)
    if limit:
        to_embed = to_embed[:limit]

    cap_note = f" (capped by --limit {limit}; {eligible} eligible)" if limit and limit < eligible else ""
    log(f"Clips: {len(clips)} total, {hash_hits} hash-skipped, {len(to_embed)} to embed{cap_note}")

    if not to_embed:
        log("Nothing new to embed.")
        export_parquet(conn)
        _log_file.close()
        return

    total = len(to_embed)
    log(f"Starting embedding of {total} clips...")

    for idx, (clip_id, clip_path, h) in enumerate(to_embed):
        log(f"[{idx+1}/{total}] Embedding {clip_id[:30]}...")

        audio_bytes = clip_path.read_bytes()
        vector = embed_with_backoff(client, audio_bytes, clip_id)

        conn.execute(
            "INSERT OR REPLACE INTO embeddings (clip_id, hash, embedding) VALUES (?, ?, ?)",
            [clip_id, h, vector],
        )
        if (idx + 1) % 10 == 0:
            log(f"Progress: {idx+1}/{total} embedded ({hash_hits + idx + 1} total in DB)")

    export_parquet(conn)
    log(f"Done! All {total} clips embedded.")
    _log_file.close()


if __name__ == "__main__":
    app()