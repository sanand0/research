#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy", "scipy"]
# ///
"""Keypoints -> joint angles -> reps -> per-rep form scores, for every pose model (+ a median ensemble).

Reads data/raw/<model>/<video>.npz (see common.py), data/vlm/<model>/<video>.json.
Writes data/site/<video>.js and data/site/summary.js (model quality, scores, adjudication) for index.html.

Geometry is 2D, side view. Angles use the side of the body nearer the camera (higher keypoint confidence).
"""

import base64
import json
import zlib

import numpy as np
from scipy.signal import find_peaks, savgol_filter

from common import KP, ROOT, VIDEOS

MODELS = ["rtmpose-x", "vitpose-h", "yolo26x", "mediapipe-heavy"]
ENSEMBLE = "ensemble"  # per-keypoint median of MODELS: cheap robustness against any single model's glitches
VLMS = ["gemini-4-argon", "gemini-3.8-flash"]
PTS = ["ear", "shoulder", "elbow", "wrist", "hip", "knee", "ankle", "heel", "toe"]  # near-side points stored for the overlay
CONF = 0.3  # keypoints below this confidence are treated as missing
W, H = 1920, 1080  # source pixels, for px-denominated metrics

# Scoring: metric value -> 0..100, linear between `bad` (0) and `good` (100). Coach-style thresholds; see README for sources.
SCORING = {
    "depth": dict(label="Depth", unit="° min elbow", good=90, bad=140, weight=0.30),  # elbows ≤90° at the bottom
    "body": dict(label="Body line", unit="° hip bend (90th pct in rep)", good=10, bad=30, weight=0.30),  # shoulder–hip–ankle straight
    "lockout": dict(label="Lockout", unit="° max elbow", good=165, bad=135, weight=0.15),  # arms straight at the top
    "neck": dict(label="Head", unit="° neck bend", good=15, bad=40, weight=0.15),  # ear in line with shoulder–hip
    "knees": dict(label="Knees", unit="° min knee", good=165, bad=140, weight=0.10),  # legs straight
}
# Rep = elbow-angle dip ≥30°, bottom <130°, ≤2.5 s each way, plank at the bottom (hip bend <40°, body <45° off the floor),
# and hip bend <60° for ≥80% of the rep. The 60° (not 40°) keeps reps with a piked top (15 Nov) so they're scored, not dropped;
# downward-dog rests bend 80-160° and are still excluded.
REP = dict(
    prominence=30, max_bottom=130, max_half=2.5, plank_bend=40, max_bend=60, min_frac=0.8, min_gap=0.7
)  # fastest real reps: ~0.85 s apart (7 Nov)


def angle(a, b, c):
    """Angle ABC in degrees for arrays of points [..., 2]."""
    v1, v2 = a - b, c - b
    cos = (v1 * v2).sum(-1) / (np.linalg.norm(v1, axis=-1) * np.linalg.norm(v2, axis=-1))
    return np.degrees(np.arccos(np.clip(cos, -1, 1)))


def side_of_line(p, a, b):
    """+1 if p is above line a→b on screen (smaller y), -1 if below. Image y grows downward."""
    t = (p[..., 0] - a[..., 0]) / (b[..., 0] - a[..., 0])
    return np.sign(a[..., 1] + t * (b[..., 1] - a[..., 1]) - p[..., 1])


def fill_gaps(x, max_gap):
    """Linearly interpolate NaN runs up to max_gap samples along axis 0; longer gaps stay NaN."""
    x = x.copy()
    for j in np.ndindex(x.shape[1:]):
        col = x[(slice(None), *j)]
        bad = np.isnan(col)
        if bad.all() or not bad.any():
            continue
        idx = np.arange(len(col))
        filled = np.interp(idx, idx[~bad], col[~bad])
        run_id = np.cumsum(~bad)  # gap length per sample = size of its NaN run
        gap = np.bincount(run_id, weights=bad)[run_id]
        col[bad & (gap <= max_gap)] = filled[bad & (gap <= max_gap)]
    return x


def score(metric, v):
    s = SCORING[metric]
    return float(np.clip(100 * (v - s["bad"]) / (s["good"] - s["bad"]), 0, 100))


def load(vid):
    """{model: (kp [S, 21, 3] with low-conf -> NaN, frames, fps, ms)} incl. the ensemble."""
    out = {}
    for m in MODELS:
        z = np.load(ROOT / "data" / "raw" / m / f"{vid}.npz")
        kp = z["kp"].copy()
        kp[kp[..., 2] < CONF, :2] = np.nan
        out[m] = (kp, z["frame"], float(z["fps"]), z["ms"])
    stack = np.stack([out[m][0] for m in MODELS])
    with np.errstate(all="ignore"):
        ens = np.nanmedian(stack, axis=0)  # NaN only where every model is missing
    out[ENSEMBLE] = (ens, out[MODELS[0]][1], out[MODELS[0]][2], sum(out[m][3] for m in MODELS))
    return out


def near_side(kp):
    """'l' or 'r': the side with higher mean limb-keypoint confidence. The far side is occluded, so models guess it with lower
    confidence. (Not "fraction present": these models emit every keypoint, so presence doesn't separate the sides.)"""
    conf = {s: np.nanmean(kp[:, [KP.index(f"{s}_{p}") for p in PTS[1:7]], 2]) for s in "lr"}
    return max("lr", key=conf.get)


def points(kp, side, fps_s):
    """{name: [S, 2] in source pixels}: near-side points, gaps ≤0.5 s filled, Savitzky–Golay smoothed (~0.33 s)."""
    names = {p: f"{side}_{p}" for p in PTS}
    names["ear"] = f"{side}_ear" if np.isfinite(kp[:, KP.index(f"{side}_ear"), 0]).mean() > 0.3 else "nose"
    raw = np.stack([kp[:, KP.index(n), :2] for n in names.values()], 1) * [W, H]
    filled = fill_gaps(raw, int(fps_s / 2))
    win = max(5, int(fps_s / 3) | 1)
    smooth = filled.copy()
    ok = np.isfinite(filled).all(axis=(1, 2))
    # smooth contiguous finite runs only (savgol can't see NaN)
    edges = np.flatnonzero(np.diff(np.r_[0, ok.astype(int), 0]))
    for a, b in zip(edges[::2], edges[1::2], strict=True):
        if b - a >= win:
            smooth[a:b] = savgol_filter(filled[a:b], win, 2, axis=0)
    return {p: smooth[:, i] for i, p in enumerate(PTS)}, {p: raw[:, i] for i, p in enumerate(PTS)}


def signals(P):
    """Per-sample form signals (degrees unless noted)."""
    toe = np.where(np.isfinite(P["toe"]), P["toe"], P["ankle"])
    sag_sign = side_of_line(P["hip"], P["shoulder"], P["ankle"])  # +1 hips above the line (pike), -1 below (sag)
    neck_sign = side_of_line(P["ear"], P["hip"], P["shoulder"])  # extend hip→shoulder: +1 ear above (craning), -1 below (dropped)
    floor = toe - P["wrist"]  # wrists and toes are both on the floor: gives the floor direction even if the camera is tilted
    floor_ang = np.degrees(np.arctan2(floor[:, 1], floor[:, 0]))
    body_ang = np.degrees(np.arctan2(*(P["ankle"] - P["shoulder"])[:, ::-1].T))
    arm = np.linalg.norm(P["shoulder"] - P["elbow"], axis=1) + np.linalg.norm(P["elbow"] - P["wrist"], axis=1)
    fn = floor / np.linalg.norm(floor, axis=1, keepdims=True)
    rel = P["shoulder"] - P["wrist"]
    height = np.abs(rel[:, 0] * fn[:, 1] - rel[:, 1] * fn[:, 0])  # shoulder's perpendicular distance from the floor line
    return {
        "elbow": angle(P["shoulder"], P["elbow"], P["wrist"]),
        "body": (180 - angle(P["shoulder"], P["hip"], P["ankle"])) * sag_sign,  # signed: + pike, - sag
        "neck": (180 - angle(P["ear"], P["shoulder"], P["hip"])) * neck_sign,  # signed: + head up, - head down
        "knees": angle(P["hip"], P["knee"], P["ankle"]),
        "incline": np.abs((body_ang - floor_ang + 180) % 360 - 180),  # body vs floor; plank ≈ 10-30°
        "height": height / np.nanmedian(arm),  # shoulder height in arm-lengths (≈1 at the top, ≈0.3-0.5 at the bottom)
    }


def find_reps(S, t):
    """Reps = elbow-angle dips (top → bottom → top) while in a plank. Returns list of (start, bottom, end) sample indices."""
    e = np.nan_to_num(S["elbow"], nan=180)
    dt = np.median(np.diff(t))
    bend = np.abs(np.nan_to_num(S["body"], nan=180))
    plank = (bend < REP["plank_bend"]) & (np.nan_to_num(S["incline"], nan=90) < 45)
    bottoms, _ = find_peaks(-e, prominence=REP["prominence"], distance=max(1, int(REP["min_gap"] / dt)))
    tops, _ = find_peaks(e, prominence=10)
    reps, half = [], int(REP["max_half"] / dt)
    for b in bottoms:
        if e[b] > REP["max_bottom"] or not plank[b]:
            continue
        before, after = tops[(tops < b) & (tops >= b - half)], tops[(tops > b) & (tops <= b + half)]
        s = before[-1] if len(before) else max(0, b - half) + int(np.argmax(e[max(0, b - half) : b]))
        f = after[0] if len(after) else b + int(np.argmax(e[b : b + half + 1]))
        if (bend[s : f + 1] < REP["max_bend"]).mean() >= REP["min_frac"]:
            reps.append((int(s), int(b), int(f)))
    # adjacent reps share a top; keep them ordered and non-overlapping
    return [r for i, r in enumerate(reps) if i == 0 or r[1] > reps[i - 1][2] - 1]


def rep_metrics(S, t, s, b, f):
    seg = slice(s, f + 1)
    body = S["body"][seg]
    p90 = np.nanpercentile(np.abs(body), 90)  # "worst sustained" bend; a raw max is driven by one-frame keypoint glitches
    worst = int(np.nanargmin(np.abs(np.abs(body) - p90)))  # the frame that shows it, for the click-to-prove link
    neck = S["neck"][seg]
    nan = lambda f, x: f(x) if np.isfinite(x).any() else np.nan
    m = {
        "depth": float(np.nanmin(S["elbow"][seg])),
        "lockout": float(min(np.nanmax(S["elbow"][s : b + 1]), np.nanmax(S["elbow"][b : f + 1]))),
        "body": float(p90),
        "neck": float(nan(lambda x: np.nanpercentile(np.abs(x), 75), neck)),
        "knees": float(nan(np.nanmin, S["knees"][seg])),
    }
    ok = {k: v for k, v in m.items() if np.isfinite(v)}  # e.g. no ear visible -> no head metric; renormalise the weights
    scores = {k: score(k, v) for k, v in ok.items()}
    weight = sum(SCORING[k]["weight"] for k in scores)
    nan_none = lambda x, d=1: round(float(x), d) if np.isfinite(x) else None
    return {
        "start": round(float(t[s]), 2),
        "bottom": round(float(t[b]), 2),
        "end": round(float(t[f]), 2),
        "worst_body_t": round(float(t[s + worst]), 2),
        "body_dir": "pike" if body[worst] > 0 else "sag",
        "neck_dir": "up" if np.nanmedian(neck) > 0 else "down" if np.isfinite(neck).any() else None,
        "down_s": round(float(t[b] - t[s]), 2),
        "up_s": round(float(t[f] - t[b]), 2),
        "height": nan_none(np.nanmin(S["height"][seg]), 2),
        "metrics": {k: nan_none(v) for k, v in m.items()},
        "scores": {k: round(scores[k]) if k in scores else None for k in SCORING},
        "score": round(sum(scores[k] * SCORING[k]["weight"] for k in scores) / weight),
    }


def pack(a) -> str:
    """Integer array -> int16 deltas along time (axis 0) -> zlib -> base64. Smooth tracks give tiny deltas that deflate ~2x.
    index.html reverses it with DecompressionStream("deflate") + a running sum. Values must fit int16."""
    a = np.asarray(a, np.int32)
    d = np.diff(a, axis=0, prepend=np.zeros_like(a[:1]))
    assert np.abs(d).max() < 32768
    return base64.b64encode(zlib.compress(d.astype("<i2").tobytes(), 9)).decode()


def quality(m, P_raw, data, t, side):
    """Ground-truth-free model-quality signals."""
    kp = data[m][0]
    idx = [KP.index(f"{side}_{p}") for p in PTS[1:7]]
    pres = np.isfinite(kp[:, idx, 0])
    # jitter: median |2nd difference| of raw positions = frame-to-frame shake (real motion is the same for every model)
    acc = np.abs(np.diff(np.stack([P_raw[p] for p in PTS[1:7]], 1), 2, axis=0))
    # agreement: distance to the median of the OTHER pose models, in torso lengths (like PCK against a consensus)
    others = np.nanmedian(np.stack([data[o][0][:, idx, :2] for o in MODELS if o != m]), 0) * [W, H]
    mine = kp[:, idx, :2] * [W, H]
    torso = np.nanmedian(np.linalg.norm(mine[:, 0] - mine[:, 3], axis=1))
    d = np.linalg.norm(mine - others, axis=2) / torso
    return {
        "coverage": round(float(pres.mean() * 100), 1),
        "jitter_px": round(float(np.nanmedian(acc)), 2),
        "consensus_err": round(float(np.nanmedian(d)), 3),
        "consensus_pck10": round(float(np.nanmean(d[np.isfinite(d)] < 0.1) * 100), 1),
        "ms": round(float(np.median(data[m][3])), 1),
    }


def camera(kp, side, fps_s, t, reps) -> dict:
    """Setup control: floor tilt, body incline and body length (% of frame width) at the top of reps. If these match across
    days, 2D angles are comparable across days."""
    P, _ = points(kp, side, fps_s)
    S = signals(P)
    tops = np.searchsorted(t, [r["start"] for r in reps] + [r["end"] for r in reps]).clip(0, len(t) - 1)
    toe = np.where(np.isfinite(P["toe"]), P["toe"], P["ankle"])
    fl = toe - P["wrist"]
    tilt = np.degrees(np.arctan2(-fl[:, 1], -fl[:, 0]))
    length = np.linalg.norm(P["shoulder"] - P["ankle"], axis=1) / W * 100
    med = lambda x: round(float(np.nanmedian(x[tops])), 1) if len(tops) else None
    return {"floor_tilt": med(tilt), "incline": med(S["incline"]), "body_length_pct": med(length)}


def cluster(found: dict[str, list[float]], tol: float = 0.6) -> list[dict]:
    """Group rep bottoms (seconds) into candidate reps: {t, by: [approaches]}. Safe because each model's bottoms are ≥ REP["min_gap"] = 0.7 s apart."""
    out = []
    for b, m in sorted((b, m) for m, bs in found.items() for b in bs):
        if out and b - out[-1]["ts"][0] <= tol and m not in out[-1]["by"]:
            out[-1]["ts"].append(b)
            out[-1]["by"].append(m)
        else:
            out.append({"ts": [b], "by": [m]})
    return [{"t": round(float(np.median(c["ts"])), 2), "by": c["by"]} for c in out]


def adjudicate(found: dict[str, list[float]], rulings: dict) -> tuple[list[dict], dict]:
    """Truth = candidates ≥3 of the 4 pose models agree on, overridden by manual rulings (visual checks) in data/truth.json.

    Pose reps are clustered (≤0.6 s). VLM timestamps drift (5 fps sampling), so each VLM's reps are matched one-to-one to
    the nearest candidate within 0.8 s instead; unmatched VLM reps become VLM-only candidates.
    rulings: {"reject": [t, ...], "add": [t, ...]}, within 0.3 s of a candidate. Returns (candidates, per-approach accuracy)."""
    cands = cluster({m: v for m, v in found.items() if m not in VLMS})
    timing = {}
    for v in [m for m in found if m in VLMS]:
        pairs = sorted((abs(b - c["t"]), i, j) for i, b in enumerate(found[v]) for j, c in enumerate(cands) if abs(b - c["t"]) <= 0.8)
        used_b, used_c, offs = set(), set(), []
        for d, i, j in pairs:
            if i not in used_b and j not in used_c:
                used_b.add(i), used_c.add(j), offs.append(d)
                cands[j]["by"].append(v)
        cands += [{"t": b, "by": [v]} for i, b in enumerate(found[v]) if i not in used_b]
        timing[v] = round(float(np.median(offs)), 2) if offs else None
    cands.sort(key=lambda c: c["t"])
    near = lambda t, ts: any(abs(t - x) <= 0.3 for x in ts)
    for c in cands:
        c["votes"] = sum(m in MODELS for m in c["by"])
        c["truth"] = (c["votes"] >= 3 or near(c["t"], rulings.get("add", []))) and not near(c["t"], rulings.get("reject", []))
        c["ruled"] = near(c["t"], rulings.get("add", []) + rulings.get("reject", []))
    n = sum(c["truth"] for c in cands)
    acc = {}
    for m in found:
        tp = sum(c["truth"] and m in c["by"] for c in cands)
        fp = sum(not c["truth"] and m in c["by"] for c in cands)
        acc[m] = {
            "truth": n,
            "found": len(found[m]),
            "tp": tp,
            "fp": fp,
            "missed": n - tp,
            "recall": round(100 * tp / n, 1) if n else None,
            "precision": round(100 * tp / (tp + fp), 1) if tp + fp else None,
            **({"timing_s": timing[m]} if m in timing else {}),
        }
    return cands, acc


def main():
    summary = {"scoring": SCORING, "rep_rules": REP, "videos": {}}
    truth = json.loads((ROOT / "data" / "truth.json").read_text()) if (ROOT / "data" / "truth.json").exists() else {}
    for vid in VIDEOS:
        data = load(vid)
        frames, fps = data[MODELS[0]][1], data[MODELS[0]][2]
        t = frames / fps
        fps_s = fps / np.median(np.diff(frames))
        side = near_side(data[ENSEMBLE][0])
        site = {
            "video": vid,
            "fps": fps,
            "t0": float(t[0]),
            "dt": float(t[1] - t[0]),
            "n": len(t),
            "side": side,
            "pts": PTS,
            "models": {},
            "vlm": {},
        }
        vsum = {"side": side, "models": {}, "vlm": {}}
        for m in [*MODELS, ENSEMBLE]:
            P, P_raw = points(data[m][0], side, fps_s)
            S = signals(P)
            reps = [rep_metrics(S, t, *r) for r in find_reps(S, t)]
            for i, r in enumerate(reps):
                r["n"] = i + 1
            q = quality(m, P_raw, data, t, side) if m in MODELS else {"ms": round(float(np.median(data[m][3])), 1)}

            def mean(k, field="metrics", d=1, reps=reps):
                xs = [r[field][k] for r in reps if r[field][k] is not None]
                return round(float(np.mean(xs)), d) if xs else None

            vsum["models"][m] = {
                "reps": len(reps),
                "score": round(float(np.mean([r["score"] for r in reps]))) if reps else None,
                "pike_pct": round(100 * float(np.mean([r["body_dir"] == "pike" for r in reps]))) if reps else None,  # rest = sag
                "metrics": {k: mean(k) for k in SCORING},
                "scores": {k: mean(k, "scores", 0) for k in SCORING},
                **q,
            }
            xy = np.stack([P[p] for p in PTS], 1) / [W, H]  # [S, 9, 2] normalised
            site["models"][m] = {
                # [S, 9, 2] in 1/5000 of the frame (~0.4 px at 1080p), -1 = missing
                "xy": pack(np.nan_to_num(xy * 5000, nan=-1).round()),
                # angles in whole degrees (labels show integers), height in 0.01 arm-lengths, -9999 = missing
                "sig": {
                    k: pack(np.nan_to_num(S[k] * (100 if k == "height" else 1), nan=-9999).round())
                    for k in ["elbow", "body", "neck", "knees", "height"]
                },
                "reps": reps,
            }
            print(f"{vid} {m:16s} side={side} reps={len(reps):3d} score={vsum['models'][m]['score']} {q}", flush=True)
        for v in VLMS:
            f = ROOT / "data" / "vlm" / v / f"{vid}.json"
            if f.exists():
                d = json.loads(f.read_text())
                site["vlm"][v] = {k: d[k] for k in ["reps", "other_movements", "summary"]}
                vsum["vlm"][v] = {
                    "reps": len(d["reps"]),
                    "score": round(float(np.mean([r["overall"] for r in d["reps"]]))) if d["reps"] else None,
                    "seconds": d.get("seconds"),
                    "tokens": (d.get("usage") or {}).get("total_token_count"),
                }
        vsum["camera"] = camera(data[ENSEMBLE][0], side, fps_s, t, site["models"][ENSEMBLE]["reps"])
        found = {m: [r["bottom"] for r in site["models"][m]["reps"]] for m in [*MODELS, ENSEMBLE]}
        found |= {v: [r["bottom"] for r in site["vlm"][v]["reps"]] for v in site["vlm"]}
        cands, acc = adjudicate(found, truth.get(vid, {}))
        vsum["truth"] = sum(c["truth"] for c in cands)
        vsum["accuracy"] = acc
        vsum["disputed"] = [c for c in cands if c["votes"] < 3 and not c["ruled"]]
        site["truth"] = vsum["truth_t"] = [c["t"] for c in cands if c["truth"]]
        print(
            f"{vid} truth={vsum['truth']} disputed={len(vsum['disputed'])} "
            + " ".join(f"{m}:{a['recall']}/{a['precision']}" for m, a in acc.items()),
            flush=True,
        )
        summary["videos"][vid] = vsum
        write_js(ROOT / "data" / "site" / f"{vid}.js", vid, site)
    summary["audits"] = [
        {"src": f"data/audit/{f.name}", "alt": f"{f.stem}: the 4 adjudicated rep bottoms where the pose models disagree most"}
        for f in sorted((ROOT / "data" / "audit").glob("*.webp"))
    ]
    write_js(ROOT / "data" / "site" / "summary.js", "summary", summary)


def write_js(path, key, obj):
    """JS (not JSON) so index.html works from file:// via <script src>, where fetch() is blocked."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"(window.PUSHUPS ||= {{}})[{json.dumps(key)}] = {json.dumps(obj, separators=(',', ':'))};\n")


if __name__ == "__main__":
    main()
