#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["aiohttp", "fsspec", "h5py", "mrestimator==0.2.0", "numpy>=2", "scipy>=1.10"]
# ///
"""Guarded discovery-only MR analysis for Allen functional-connectivity V1 sessions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from c002_mr_calibrate import DT_MS, estimate_m

ROOT = Path(__file__).parents[1]
CLAIM = ROOT / "claims" / "C002.json"
UNIT_IDS = ROOT / "inputs" / "c002_visp_good_units.json"


def assert_discovery(session_id: int, claim: dict) -> None:
    if session_id in claim.get("confirmation_sessions", []):
        raise ValueError(f"refusing confirmation session {session_id}")
    if session_id not in claim.get("discovery_sessions", []):
        raise ValueError(f"session {session_id} is not in frozen discovery set")


def fixed_subset(unit_ids: list[int], n: int, seed: int) -> list[int]:
    """Return deterministic nested unit subsets by taking a fixed permutation prefix."""
    ids = np.array(sorted(unit_ids), dtype=np.int64)
    if len(ids) < n:
        raise ValueError(f"need {n} units, have {len(ids)}")
    order = np.random.default_rng(seed).permutation(len(ids))
    return sorted(map(int, ids[order[:n]]))


def population_counts(session_id: int, selected_ids: list[int]) -> tuple[np.ndarray, dict]:
    """Range-read selected unit spikes and return per-unit 4-ms counts."""
    import fsspec
    import h5py

    url = (
        "https://allen-brain-observatory.s3.us-west-2.amazonaws.com/"
        f"visual-coding-neuropixels/ecephys-cache/session_{session_id}/session_{session_id}.nwb"
    )
    with fsspec.open(url, "rb", block_size=2 << 20, cache_type="readahead").open() as fo:
        with h5py.File(fo, "r") as f:
            intervals = f["intervals/spontaneous_presentations"]
            starts = intervals["start_time"][:]
            stops = intervals["stop_time"][:]
            durations = stops - starts
            j = int(np.argmax(durations))
            start = float(starts[j])
            duration = min(1800.0, float(durations[j]))
            if duration < 1790:
                raise ValueError(f"longest spontaneous interval only {duration:.1f}s")
            stop = start + duration

            ids = f["units/id"][:].astype(np.int64)
            lookup = {int(x): i for i, x in enumerate(ids)}
            missing = [x for x in selected_ids if x not in lookup]
            if missing:
                raise ValueError(f"{len(missing)} selected unit IDs absent from NWB")
            pos = np.array(sorted(lookup[x] for x in selected_ids), dtype=int)
            ends = f["units/spike_times_index"][:]
            starts_idx = np.r_[0, ends[:-1]]
            lo = int(starts_idx[pos.min()])
            hi = int(ends[pos.max()])
            block = f["units/spike_times"][lo:hi]

            dt = DT_MS / 1000
            nbins = int(round(duration / dt))
            unit_counts = np.zeros((len(pos), nbins), dtype=np.uint16)
            spike_count = 0
            for row, i in enumerate(pos):
                x = block[int(starts_idx[i] - lo) : int(ends[i] - lo)]
                x = x[(x >= start) & (x < stop)] - start
                bins = np.minimum((x / dt).astype(np.int64), nbins - 1)
                unit_counts[row] = np.bincount(bins, minlength=nbins).astype(np.uint16)
                spike_count += len(x)

    return unit_counts, {
        "url": url,
        "spontaneous_start_s": start,
        "duration_s": duration,
        "loaded_units": len(selected_ids),
        "spike_count": spike_count,
        "timestamp_payload_MB": block.nbytes / 1e6,
    }


def analyze(session_id: int) -> dict:
    claim = json.loads(CLAIM.read_text())
    assert_discovery(session_id, claim)
    units = json.loads(UNIT_IDS.read_text()).get(str(session_id), [])
    if len(units) < 32:
        raise ValueError(f"session {session_id} has only {len(units)} qualifying VISp units")

    seed = 20260909 + session_id
    selected32 = fixed_subset(units, 32, seed)
    unit_counts_all, source = population_counts(session_id, units)
    row_for_id = {unit_id: i for i, unit_id in enumerate(units)}
    rows32 = [row_for_id[x] for x in selected32]
    counts32 = unit_counts_all[rows32].sum(axis=0, dtype=np.int32)

    # Nested thinning is deterministic and uses the same 32-unit source population.
    subsets = {
        32: selected32,
        16: fixed_subset(selected32, 16, seed + 1),
        8: fixed_subset(selected32, 8, seed + 1),
    }
    estimates = {}
    for n in [32, 16, 8]:
        rows = [row_for_id[x] for x in subsets[n]]
        counts = unit_counts_all[rows].sum(axis=0, dtype=np.int32)
        estimates[str(n)] = estimate_m(counts, kmax=200)

    subset_repeats = []
    for rep in range(10):
        ids32 = fixed_subset(units, 32, seed + 1000 + rep)
        rows = [row_for_id[x] for x in ids32]
        counts = unit_counts_all[rows].sum(axis=0, dtype=np.int32)
        subset_repeats.append({"replicate": rep, **estimate_m(counts, kmax=200)})

    # Prospective discovery diagnostic for the remaining sessions: fixed six 300 s windows.
    windows = []
    bins_per_window = int(300_000 / DT_MS)
    for w in range(6):
        sl = counts32[w * bins_per_window : (w + 1) * bins_per_window]
        windows.append({"window": w, "start_s": 300 * w, **estimate_m(sl, kmax=200)})

    return {
        "claim_id": "C002",
        "session_id": session_id,
        "role": "discovery",
        "region": "VISp",
        "unit_selection": "32 good units, deterministic session-specific random subset; nested 16/8 subsets",
        "dt_ms": DT_MS,
        "kmax": 200,
        "source": source,
        "full_block": estimates,
        "random_32_unit_subsets": subset_repeats,
        "windows_300s": windows,
        "interpretation_rule": "m is uninterpretable whenever applicable=false; do not tune kmax/R2 gate on real data.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("session_id", type=int)
    args = parser.parse_args()
    result = analyze(args.session_id)
    out = ROOT / "results" / f"c002_session_{args.session_id}.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
