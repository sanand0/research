#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx", "h2"]
# ///
"""Benchmark Cloudflare Clef over a reused REST connection without exposing auth tokens."""

import csv
import json
import statistics
import subprocess
import time
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
AUTH = Path.home() / ".config/cloudflare/config/default.json"
MODELS = ("clef-flash", "clef")
RUNS = 12

payload = json.loads((HERE / "payload.json").read_text())
token = json.loads(AUTH.read_text())["oauth_token"]
whoami = json.loads(subprocess.check_output(["cf", "auth", "whoami"], text=True))
account_id = whoami["accounts"][0]["id"]

rows = []
with httpx.Client(
    base_url=f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run",
    headers={"Authorization": f"Bearer {token}"},
    timeout=30,
    http2=True,
) as client:
    for run in range(RUNS):
        for model in MODELS:
            body = payload | {"model": model}
            t0 = time.perf_counter()
            response = client.post(f"/@cf/cloudflare/{model}", json=body)
            elapsed_ms = (time.perf_counter() - t0) * 1000
            response.raise_for_status()
            data = response.json()
            result = data.get("result", data)
            usage = result.get("usage", {})
            rows.append(
                {
                    "run": run + 1,
                    "warmup": run == 0,
                    "model": model,
                    "latency_ms": round(elapsed_ms, 1),
                    "input_tokens": usage.get("input_tokens"),
                    "cf_ray": response.headers.get("cf-ray", ""),
                    "server_timing": response.headers.get("server-timing", ""),
                }
            )
            print(f"{model:10} run {run + 1:2}: {elapsed_ms:7.1f} ms")

with (HERE / "bench.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0])
    writer.writeheader()
    writer.writerows(rows)

summary = {}
for model in MODELS:
    values = [r["latency_ms"] for r in rows if r["model"] == model and not r["warmup"]]
    ordered = sorted(values)
    summary[model] = {
        "n": len(values),
        "median_ms": round(statistics.median(values), 1),
        "mean_ms": round(statistics.mean(values), 1),
        "min_ms": round(min(values), 1),
        "p95_ms": round(ordered[max(0, int(0.95 * len(ordered) + 0.999999) - 1)], 1),
        "max_ms": round(max(values), 1),
    }

print(json.dumps(summary, indent=2))
