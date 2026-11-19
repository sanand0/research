#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.12.*"
# dependencies = ["numpy", "scipy", "skia-python"]
# ///
"""Summary video: per day, a 2 s story card then 6 s from the 2nd rep, with the same telestration as index.html (ensemble, Single).

Usage: uv run summary_video.py OUT.mp4   (needs data/raw/ — see README — and work/fonts/; then run `videocompress OUT.mp4`)
Renders RGBA frames with skia (a port of drawPose() in index.html) and pipes them to ffmpeg as high-quality H.264.
"""

import subprocess
import sys
from pathlib import Path

import numpy as np
import skia

import analyze as A
from common import ROOT, load_js

FPS, W, H, CLIP_S, CARD_S, OUTRO_S = 30, 1920, 1080, 6.0, 2.0, 3.0
SRC = Path.home() / "r2/media/2026-11-push-ups"
FONTS = ROOT / "work" / "fonts"
TF = {k: skia.Typeface.MakeFromFile(str(FONTS / f)) for k, f in {
    "mono": "JetBrainsMono-SemiBold.ttf", "cond": "BarlowCondensed-Bold.ttf", "cond6": "BarlowCondensed-SemiBold.ttf",
    "body": "Barlow-Medium.ttf"}.items()}
NEON = dict(good="#3ddc84", ok="#ffc53d", bad="#ff5470", accent="#c6ff3d")
BG, INK, MUTED = "#0d0f12", "#e8ece6", "#8f9aa6"
# The story, one beat per day. kind drives the mini body-line diagram on the card.
DAYS = {
    "07": dict(date="7 NOV", head="HIPS SAG", sub="Hips drop below the line · arms never fully straighten", word="SAG", kind="sag", tone="bad"),
    "08": dict(date="8 NOV", head="HEAD DROPS", sub="Hips better — but the neck bends ~30° down", word="HEAD DROPS", kind="head", tone="ok"),
    "11": dict(date="11 NOV", head="BEST DAY", sub="Straight line · full lockout · neutral head", word="STRAIGHT", kind="straight", tone="good"),
    "15": dict(date="15 NOV", head="HIPS PIKE", sub="Overcorrected: hips now ~36° above the line", word="PIKE", kind="pike", tone="bad"),
}


def color(c: str) -> int:
    """'#rrggbb' or '#rrggbbaa' (as in index.html) -> skia ARGB int."""
    c = c.lstrip("#")
    a = int(c[6:8], 16) if len(c) == 8 else 255
    return skia.ColorSetARGB(a, int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))


def stroke(cv, pts, c, w, dash=None):
    pts = [p for p in pts if p is not None]
    if len(pts) < 2:
        return
    path = skia.Path()
    path.moveTo(*pts[0])
    for p in pts[1:]:
        path.lineTo(*p)
    paint = skia.Paint(AntiAlias=True, Color=color(c), StrokeWidth=w, Style=skia.Paint.kStroke_Style,
                       StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join)
    if dash:
        paint.setPathEffect(skia.DashPathEffect.Make(dash, 0))
    cv.drawPath(path, paint)


def text(cv, s, x, y, size, c, tf="mono", align="left"):
    font = skia.Font(TF[tf], size)
    w = font.measureText(s)
    x = x - w if align == "right" else x - w / 2 if align == "center" else x
    cv.drawString(s, x, y, font, skia.Paint(AntiAlias=True, Color=color(c)))
    return w


def tag(cv, xy, s, c, k):
    """index.html tag(): 13px mono on a #000c rounded box, vertically centred on y."""
    x, y = xy
    font = skia.Font(TF["mono"], 13 * k)
    w, h = font.measureText(s) + 10 * k, 18 * k
    x = min(max(x, 8), W - 8 - w)  # unlike the page, keep labels inside the frame (video has no scrollable margin)
    cv.drawRoundRect(skia.Rect.MakeXYWH(x, y - h / 2, w, h), 4 * k, 4 * k, skia.Paint(AntiAlias=True, Color=color("#000000cc")))
    cv.drawString(s, x + 5 * k, y + 4.5 * k, font, skia.Paint(AntiAlias=True, Color=color(c)))


def tone(s):
    """Same bands as canvasScore() in index.html."""
    return NEON["good"] if s >= 75 else NEON["ok"] if s >= 40 else NEON["bad"]


def score_col(metric, v):
    return tone(A.score(metric, v))


def draw_pose(cv, p, sig):
    """Port of drawPose(ctx, m, t, full=true) in index.html. p: {name: (x, y) px or None}; sig: {signal: value or None}."""
    k = W / 960
    sh, el, wr, hip, knee, an, ear, toe, heel = (p[n] for n in ["shoulder", "elbow", "wrist", "hip", "knee", "ankle", "ear", "toe", "heel"])
    lw = 3.2 * k
    elbow, body, neck, knees, height = (sig[n] for n in ["elbow", "body", "neck", "knees", "height"])
    ft = toe or an
    if wr and ft:  # floor line (wrist→toe, extended) and shoulder height above it
        dx, dy = ft[0] - wr[0], ft[1] - wr[1]
        stroke(cv, [(wr[0] + dx * 0.15, wr[1] + dy * 0.15), (wr[0] - dx * 0.25, wr[1] - dy * 0.25)], "#ffffff70", 1.5 * k, [2 * k, 6 * k])
        stroke(cv, [(ft[0] + dx * 0.05, ft[1] + dy * 0.05), wr], "#ffffff70", 1.5 * k, [2 * k, 6 * k])
        if sh and height is not None:
            L = np.hypot(dx, dy)
            ux, uy = dx / L, dy / L
            d = (sh[0] - wr[0]) * ux + (sh[1] - wr[1]) * uy
            foot = (wr[0] + ux * d, wr[1] + uy * d)
            stroke(cv, [sh, foot], "#ffffffb0", 1.5 * k, [4 * k, 4 * k])
            tag(cv, (foot[0] - 120 * k, (sh[1] + foot[1]) / 2), f"height {height:.2f}", "#ffffff", k)
    if sh and an and hip and body is not None:  # straight-body reference and hip deviation
        c = score_col("body", abs(body))
        stroke(cv, [sh, an], "#ffffffc0", 2 * k, [8 * k, 6 * k])
        dx, dy = an[0] - sh[0], an[1] - sh[1]
        d = ((hip[0] - sh[0]) * dx + (hip[1] - sh[1]) * dy) / (dx * dx + dy * dy)
        stroke(cv, [hip, (sh[0] + dx * d, sh[1] + dy * d)], c, 3 * k)
        tag(cv, (hip[0] - 30 * k, hip[1] + (-26 if body > 0 else 26) * k), f"{'pike' if body > 0 else 'sag'} {abs(body):.0f}°", c, k)
    if sh and hip and ear and neck is not None:  # neutral-head guide
        c = score_col("neck", abs(neck))
        dx, dy = sh[0] - hip[0], sh[1] - hip[1]
        L, e = np.hypot(dx, dy), np.hypot(ear[0] - sh[0], ear[1] - sh[1])
        stroke(cv, [sh, (sh[0] + dx / L * e * 1.3, sh[1] + dy / L * e * 1.3)], "#ffffffa0", 1.5 * k, [3 * k, 4 * k])
        stroke(cv, [sh, ear], c, lw)
        tag(cv, (ear[0] + 10 * k, ear[1] - 22 * k), f"head {'up' if neck > 0 else 'down'} {abs(neck):.0f}°", c, k)
    stroke(cv, [sh, hip], "#ffffffe0", lw)
    kc = score_col("knees", knees) if knees is not None else "#ffffff"
    stroke(cv, [hip, knee, an], kc, lw)
    stroke(cv, [heel, an, toe], "#ffffffc0", 2 * k)
    if knee and knees is not None and knees < 170:
        tag(cv, (knee[0] - 20 * k, knee[1] + 22 * k), f"knee {knees:.0f}°", kc, k)
    ac = NEON["accent"]
    stroke(cv, [sh, el, wr], ac, lw * 1.2)
    if sh and el and wr and elbow is not None:
        a1, a2 = np.arctan2(sh[1] - el[1], sh[0] - el[0]), np.arctan2(wr[1] - el[1], wr[0] - el[0])
        d = (a2 - a1 + np.pi) % (2 * np.pi) - np.pi
        r = 28 * k
        path = skia.Path()
        path.moveTo(*el)
        path.arcTo(skia.Rect.MakeLTRB(el[0] - r, el[1] - r, el[0] + r, el[1] + r), np.degrees(a1), np.degrees(d), False)
        path.close()
        cv.drawPath(path, skia.Paint(AntiAlias=True, Color=color(ac + "40")))
        cv.drawPath(path, skia.Paint(AntiAlias=True, Color=color(ac), StrokeWidth=2 * k, Style=skia.Paint.kStroke_Style))
        tag(cv, (el[0] + 14 * k, el[1] + 30 * k), f"elbow {elbow:.0f}°", ac, k)
    for q in [ear, sh, el, wr, hip, knee, an]:
        if q:
            cv.drawCircle(*q, 4 * k, skia.Paint(AntiAlias=True, Color=color("#ffffff")))


def chip(cv, x, y, parts, size=30, right=False):
    """HUD chip: [(text, colour), ...] on a dark rounded box. y = box top."""
    font = skia.Font(TF["mono"], size)
    gap = size * 0.6
    w = sum(font.measureText(s) for s, _ in parts) + gap * (len(parts) - 1) + size
    x = x - w if right else x
    cv.drawRoundRect(skia.Rect.MakeXYWH(x, y, w, size * 1.6), size * 0.3, size * 0.3, skia.Paint(AntiAlias=True, Color=color("#000000c0")))
    cx = x + size / 2
    for s, c in parts:
        cv.drawString(s, cx, y + size * 1.12, font, skia.Paint(AntiAlias=True, Color=color(c)))
        cx += font.measureText(s) + gap


def body_diagram(cv, x, y, w, kind, c, thick=10):
    """Mini side view: ankle at (x, y), shoulder up-right; dashed straight line vs the actual body line (sag / pike / head)."""
    sh, an = np.array([x + w, y - 0.30 * w]), np.array([x, y])
    mid, n = (sh + an) / 2, np.array([0.30, 1.0]) / np.hypot(0.30, 1.0)  # unit normal pointing down-ish
    hip = mid + n * {"sag": 0.14, "pike": -0.16}.get(kind, 0.0) * w
    head_dir = (sh - an) / np.linalg.norm(sh - an)
    if kind == "head":
        head_dir = np.array([0.55, 0.84])  # dropped toward the floor
    head = sh + head_dir * 0.09 * w
    hand = np.array([x + w * 1.0, y])
    stroke(cv, [(x - 0.06 * w, y + thick), (x + 1.12 * w, y + thick)], "#ffffff40", 3)
    stroke(cv, [tuple(an), tuple(sh)], "#ffffffa0", 4, [14, 10])
    stroke(cv, [tuple(sh), tuple(hand)], "#ffffff90", thick * 0.7)
    stroke(cv, [tuple(an), tuple(hip), tuple(sh)], c, thick)
    if kind in ("sag", "pike"):  # same hip-offset marker as the video overlay
        stroke(cv, [tuple(hip), tuple(mid)], "#ffffff", thick * 0.45)
        cv.drawCircle(*hip, thick * 0.9, skia.Paint(AntiAlias=True, Color=color(c)))
    cv.drawCircle(*head, 0.045 * w, skia.Paint(AntiAlias=True, Color=color(c if kind == "head" else INK)))


def card(vid, i, n_days, summary):
    """2 s story card: big headline in the fault colour; date, score, a body-line diagram, and the story so far."""
    img = np.zeros((H, W, 4), np.uint8)
    cv = skia.Surface(img).getCanvas()
    cv.clear(color(BG))
    d, s = DAYS[vid], summary["videos"][vid]["models"]["ensemble"]
    c = NEON[d["tone"]]
    text(cv, f"PUSH-UP FORM  ·  DAY {i + 1} OF {n_days}", 140, 170, 34, MUTED)
    text(cv, d["date"], 140, 330, 140, INK, "cond6")
    head_font = 250 if len(d["head"]) <= 9 else 210
    text(cv, d["head"], 132, 560, head_font, c, "cond")
    text(cv, d["sub"], 140, 650, 50, "#c8d0d8", "body")
    # right column: diagram + score
    body_diagram(cv, 1240, 400, 520, d["kind"], c)
    sc = s["score"]
    w = text(cv, str(sc), 1780, 650, 190, tone(sc), "cond", "right")
    text(cv, "/100", 1780, 700, 40, MUTED, "body", "right")
    text(cv, "FORM SCORE", 1780 - w - 20, 650, 30, MUTED, "mono", "right")
    # story strip
    days = list(DAYS)
    x0, x1, y = 180, 1740, 900
    stroke(cv, [(x0, y), (x1, y)], "#ffffff30", 3)
    for j, v in enumerate(days):
        x = x0 + (x1 - x0) * j / (len(days) - 1)
        dj = DAYS[v]
        past = j <= i
        cj = NEON[dj["tone"]] if past else "#ffffff30"
        cv.drawCircle(x, y, 16 if j == i else 10, skia.Paint(AntiAlias=True, Color=color(cj)))
        text(cv, DAYS[v]["date"], x, y - 34, 32, INK if j == i else MUTED, "cond6", "center")
        if past:
            text(cv, dj["word"], x, y + 62, 40 if j == i else 32, cj, "cond", "center")
    return img


def outro(summary):
    img = np.zeros((H, W, 4), np.uint8)
    cv = skia.Surface(img).getCanvas()
    cv.clear(color(BG))
    text(cv, "THE STORY", W / 2, 190, 40, MUTED, "mono", "center")
    days = list(DAYS)
    for j, v in enumerate(days):
        d, c = DAYS[v], NEON[DAYS[v]["tone"]]
        cx = 240 + j * 480
        body_diagram(cv, cx - 150, 520, 300, d["kind"], c, thick=8)
        text(cv, d["date"], cx, 300, 44, INK, "cond6", "center")
        text(cv, d["word"], cx, 640, 64, c, "cond", "center")
        text(cv, f'{summary["videos"][v]["models"]["ensemble"]["score"]}/100', cx, 705, 40, MUTED, "body", "center")
        if j < len(days) - 1:  # arrow as a path: Barlow has no → glyph
            ax = cx + 240
            stroke(cv, [(ax - 22, 600), (ax + 22, 600)], MUTED, 5)
            stroke(cv, [(ax + 6, 586), (ax + 22, 600), (ax + 6, 614)], MUTED, 5)
    text(cv, "Keep the hips on the dashed line — not below it, not above it.", W / 2, 880, 56, INK, "body", "center")
    return img


def track(vid):
    """Ensemble near-side points (px) and signals per sample, as analyze.py computes them for the page."""
    data = A.load(vid)
    kp, frames, fps, _ = data[A.ENSEMBLE]
    t = frames / fps
    side = A.near_side(kp)
    P, _ = A.points(kp, side, fps / np.median(np.diff(frames)))
    return t, P, A.signals(P)


def at(t, ts, arr):
    """Linear interpolation at time t; if one neighbour is missing use the other (like poseAt in index.html)."""
    i = int(np.clip(np.searchsorted(ts, t) - 1, 0, len(ts) - 2))
    u = (t - ts[i]) / (ts[i + 1] - ts[i])
    a, b = arr[i], arr[i + 1]
    ok_a, ok_b = np.all(np.isfinite(a)), np.all(np.isfinite(b))
    v = a + (b - a) * u if ok_a and ok_b else a if ok_a else b if ok_b else None
    return None if v is None else (tuple(float(x) for x in v) if np.ndim(v) else float(v))


def frames_of(vid, start):
    """RGBA frames at FPS for CLIP_S seconds from `start` of the original 1080p video."""
    src = SRC / f"2026-11-{vid}-push-ups.webm"
    cmd = ["ffmpeg", "-v", "error", "-threads", "4", "-ss", f"{start:.3f}", "-i", str(src), "-t", str(CLIP_S),
           "-vf", f"fps={FPS},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgba", "-"]
    with subprocess.Popen(cmd, stdout=subprocess.PIPE) as p:
        while buf := p.stdout.read(W * H * 4):
            if len(buf) < W * H * 4:
                break
            yield np.frombuffer(buf, np.uint8).reshape(H, W, 4).copy()


def fade(img, a):
    return (img.astype(np.float32) * a).astype(np.uint8) if a < 1 else img


def main(out: str):
    summary = load_js(ROOT / "data" / "site" / "summary.js")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "12", "-threads", "4", "-pix_fmt", "yuv420p", out],
                           stdin=subprocess.PIPE)
    write = lambda img: enc.stdin.write(np.ascontiguousarray(img).tobytes())
    nf = int(CARD_S * FPS)
    for i, vid in enumerate(DAYS):
        print(f"{vid}: card + clip", flush=True)
        c = card(vid, i, len(DAYS), summary)
        for f in range(nf):  # quick fade in/out so cuts don't jolt
            write(fade(c, min(1, (f + 1) / 5, (nf - f) / 5)))
        reps = load_js(ROOT / "data" / "site" / f"{vid}.js")["models"]["ensemble"]["reps"]
        start = reps[1]["start"]  # from the 2nd push-up onwards
        ts, P, S = track(vid)
        d = DAYS[vid]
        for f, img in enumerate(frames_of(vid, start)):
            t = start + f / FPS
            cv = skia.Surface(img).getCanvas()
            p = {n: at(t, ts, P[n]) for n in A.PTS}
            sig = {n: at(t, ts, S[n]) for n in ["elbow", "body", "neck", "knees", "height"]}
            draw_pose(cv, p, sig)
            rep = next((r for r in reps if r["start"] <= t <= r["end"]), None)
            parts = [(d["date"], INK)] + ([(f"REP {rep['n']}", MUTED), (f"{rep['score']}/100", tone(rep["score"]))] if rep else [])
            chip(cv, 32, 28, parts)
            chip(cv, W - 32, 28, [(d["head"], NEON[d["tone"]])], right=True)
            write(img)
    o = outro(summary)
    no = int(OUTRO_S * FPS)
    for f in range(no):
        write(fade(o, min(1, (f + 1) / 5, (no - f) / 8)))
    enc.stdin.close()
    sys.exit(enc.wait())


if __name__ == "__main__":
    main(sys.argv[1])
