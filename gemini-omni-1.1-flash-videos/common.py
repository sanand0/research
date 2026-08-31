"""Small shared helpers for resumable Gemini Omni video experiments."""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from google import genai

MODEL = "gemini-omni-1.1-flash"
INPUT_USD_PER_M = 1.50
TEXT_OUTPUT_USD_PER_M = 9.00
VIDEO_OUTPUT_USD_PER_M = 17.50
ROOT = Path(__file__).resolve().parent


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_env() -> None:
    path = ROOT / ".env"
    if path.exists():
        for line in path.read_text().splitlines():
            if line and not line.lstrip().startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                key, value = key.strip(), value.strip().strip("'\"")
                if not os.environ.get(key):
                    os.environ[key] = value
    if not os.environ.get("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY is missing; add it to .env or the environment")


def client() -> genai.Client:
    load_env()
    return genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)


def read_json(path: Path, default: Any) -> Any:
    return json.loads(path.read_text()) if path.exists() else default


def sanitize(message: str) -> str:
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        message = message.replace(key, "<redacted>")
    return re.sub(r"([?&]key=)[^&\s]+", r"\1<redacted>", message)


class Log:
    def __init__(self, output_dir: Path):
        self.path = output_dir / "events.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event: str, **data: Any) -> None:
        record = {"time": now(), "event": event, **data}
        with self.path.open("a") as f:
            f.write(json.dumps(record, sort_keys=True) + "\n")
            f.flush()
        detail = " ".join(f"{k}={v}" for k, v in data.items() if k in {"step", "resolution", "output", "error"})
        try:
            print(f"[{event}] {detail}".rstrip(), flush=True)
        except BrokenPipeError:
            # Logging transport failure must never mark a completed, billed API call as failed.
            # Redirect stdout so interpreter shutdown does not fail while flushing the dead pipe.
            sys.stdout = open(os.devnull, "w")


def usage_dict(usage: Any) -> dict[str, Any]:
    if not usage:
        return {"input_tokens": 0, "output_tokens": 0, "video_tokens": 0, "thought_tokens": 0, "estimated_cost_usd": 0.0}
    input_tokens = usage.total_input_tokens or 0
    output_tokens = usage.total_output_tokens or 0
    video_tokens = sum(x.tokens for x in usage.output_tokens_by_modality or [] if str(x.modality).lower().endswith("video"))
    other_output_tokens = max(0, output_tokens - video_tokens)
    cost = (input_tokens * INPUT_USD_PER_M + video_tokens * VIDEO_OUTPUT_USD_PER_M + other_output_tokens * TEXT_OUTPUT_USD_PER_M) / 1_000_000
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "video_tokens": video_tokens,
        "thought_tokens": usage.total_thought_tokens or 0,
        "estimated_cost_usd": round(cost, 6),
    }


def state_for(output_dir: Path, experiment: str) -> dict[str, Any]:
    return read_json(output_dir / "state.json", {"experiment": experiment, "created_at": now(), "steps": {}})


def total_cost(state: dict[str, Any]) -> float:
    return round(sum(step.get("usage", {}).get("estimated_cost_usd", 0) for step in state.get("steps", {}).values()), 6)


def _download_video(c: genai.Client, output_video: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if getattr(output_video, "data", None):
        path.write_bytes(base64.b64decode(output_video.data))
        return
    uri = getattr(output_video, "uri", None)
    if not uri:
        raise RuntimeError("No video data or URI returned")
    # URI delivery may briefly need processing before it can be downloaded.
    for attempt in range(30):
        try:
            data = c.files.download(file=uri)
            path.write_bytes(data)
            return
        except Exception:
            if attempt == 29:
                raise
            time.sleep(2)


def generate_step(
    c: genai.Client,
    output_dir: Path,
    state: dict[str, Any],
    log: Log,
    *,
    step: str,
    prompt: str,
    output_rel: str,
    resolution: str,
    duration: int,
    aspect_ratio: str = "16:9",
    previous_interaction_id: str | None = None,
    input_parts: list[dict[str, Any]] | None = None,
    task: str | None = None,
) -> dict[str, Any]:
    video = output_dir / output_rel
    metadata = video.with_suffix(".json")
    saved = state.get("steps", {}).get(step)
    if saved and saved.get("status") == "completed" and video.exists() and metadata.exists():
        log.emit("resume.skip", step=step, output=str(video))
        return saved

    log.emit("api.start", step=step, resolution=resolution, output=str(video))
    response_format: dict[str, Any] = {
        "type": "video",
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "duration": f"{duration}s",
        "delivery": "uri",
    }
    kwargs: dict[str, Any] = {
        "model": MODEL,
        "input": input_parts if input_parts is not None else prompt,
        "response_format": response_format,
    }
    if previous_interaction_id:
        kwargs["previous_interaction_id"] = previous_interaction_id
    if task:
        kwargs["generation_config"] = {"video_config": {"task": task}}
    try:
        interaction = c.interactions.create(**kwargs)
        if not interaction.output_video:
            raise RuntimeError(f"No video returned: status={interaction.status}")
        _download_video(c, interaction.output_video, video)
        usage = usage_dict(interaction.usage)
        record = {
            "status": "completed",
            "interaction_id": interaction.id,
            "model": interaction.model,
            "prompt": prompt,
            "resolution": resolution,
            "duration_seconds": duration,
            "aspect_ratio": aspect_ratio,
            "output": str(video.relative_to(ROOT)),
            "usage": usage,
            "completed_at": now(),
        }
        write_json(metadata, record)
        state.setdefault("steps", {})[step] = record
        state["updated_at"] = now()
        write_json(output_dir / "state.json", state)
        log.emit("api.done", step=step, output=str(video))
        return record
    except Exception as exc:
        error = sanitize(str(exc))
        state.setdefault("steps", {})[step] = {"status": "failed", "error": error, "failed_at": now()}
        state["updated_at"] = now()
        write_json(output_dir / "state.json", state)
        log.emit("api.error", step=step, error=error)
        raise


def upload_part(c: genai.Client, path: Path, kind: str, log: Log) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    log.emit("upload.start", step=path.name)
    uploaded = c.files.upload(file=str(path))
    name = getattr(uploaded, "name", None)
    for _ in range(60):
        state = str(getattr(uploaded, "state", "")).upper()
        if "FAILED" in state:
            raise RuntimeError(f"Upload failed for {path}")
        if "ACTIVE" in state or not name:
            break
        time.sleep(1)
        uploaded = c.files.get(name=name)
    mime = getattr(uploaded, "mime_type", None) or mimetypes.guess_type(path)[0] or ("video/mp4" if kind == "video" else "image/png")
    log.emit("upload.done", step=path.name)
    return {"type": kind, "uri": uploaded.uri, "mime_type": mime}


def assemble_side_by_side(before: Path, after: Path, output: Path, log: Log) -> None:
    if output.exists():
        log.emit("resume.skip", step="assemble", output=str(output))
        return
    log.emit("assemble.start", step="assemble", output=str(output))
    output.parent.mkdir(parents=True, exist_ok=True)
    filter_graph = (
        "[0:v]drawtext=text='BEFORE':x=30:y=30:fontsize=40:fontcolor=white:box=1:boxcolor=black@0.65[b];"
        "[1:v]drawtext=text='AFTER':x=30:y=30:fontsize=40:fontcolor=white:box=1:boxcolor=black@0.65[a];"
        "[b][a]hstack=inputs=2[v0];"
        "[v0]drawtext=text='ONE PROMPT - ORANGE TERMINAL TO COBALT BLUE - EVERYTHING ELSE THE SAME':"
        "x=(w-text_w)/2:y=h-60:fontsize=30:fontcolor=white:box=1:boxcolor=black@0.75[v]"
    )
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(before), "-i", str(after), "-filter_complex", filter_graph,
         "-map", "[v]", "-map", "1:a?", "-c:v", "libx264", "-crf", "20", "-c:a", "aac", "-shortest", str(output)],
        check=True,
    )
    log.emit("assemble.done", step="assemble", output=str(output))


def print_result(output_dir: Path, state: dict[str, Any], fmt: str, **extra: Any) -> None:
    result = {
        "status": "completed",
        "experiment": state["experiment"],
        "output_dir": str(output_dir.relative_to(ROOT)),
        "estimated_cost_usd": total_cost(state),
        "steps": {k: v.get("status") for k, v in state.get("steps", {}).items()},
        **extra,
    }
    if fmt == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Completed {result['experiment']}; estimated API cost ${result['estimated_cost_usd']:.3f}")
        for key, value in extra.items():
            print(f"{key}: {value}")
