#!/usr/bin/env python3
"""Render the Calvin & Hobbes 957 Scrabble game as a social-media video.

Edit storyboard.json (text, timings, colours, dialogue) and moves.json (the game),
then run:  python3 render.py            -> calvin-957.mp4
           python3 render.py --frames 12.5 40 81   -> PNG stills at those seconds (for checking)
Needs: Python 3 + Pillow, ffmpeg on PATH, and the fonts/ folder next to this file.
"""
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SB = json.load(open(os.path.join(HERE, 'storyboard.json')))
MOVES = json.load(open(os.path.join(HERE, 'moves.json')))
W, H, FPS = SB['video']['width'], SB['video']['height'], SB['video']['fps']
TM = SB['timing']

def rgb(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
PAL = {k: (rgb(v) if isinstance(v, str) else [rgb(x) for x in v]) for k, v in SB['palette'].items()}

_fc = {}
def F(name, size):
    key = (name, size)
    if key not in _fc:
        path = os.path.join(HERE, 'fonts', name)
        if not os.path.exists(path): path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
        _fc[key] = ImageFont.truetype(path, size)
    return _fc[key]
DISPLAY, HAND, TILEF = 'RammettoOne.woff', 'GochiHand.woff', 'ArchivoBlack.woff'
BODY, BOLD = 'Atkinson-Regular.woff', 'Atkinson-Bold.woff'

# ---------- easing ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(p): return 1 - (1 - p) ** 3
def ease_in_out(p): return 3 * p * p - 2 * p * p * p
def ease_back(p, s=1.7): p -= 1; return p * p * ((s + 1) * p + s) + 1
def mix(c1, c2, a): return tuple(int(c1[i] + (c2[i] - c1[i]) * a) for i in range(3))

# ---------- board geometry ----------
BX, BY, PITCH = 113, 160, 57
CELL = PITCH - 3
P = {}
def _sym(pts, t):
    for r, c in pts:
        for rr in (r, 14 - r):
            for cc in (c, 14 - c):
                P[(rr, cc)] = t; P[(cc, rr)] = t
_sym([(0, 0), (0, 7), (7, 0)], 'TW'); _sym([(1, 1), (2, 2), (3, 3), (4, 4), (7, 7)], 'DW')
_sym([(1, 5), (5, 5), (5, 1)], 'TL'); _sym([(0, 3), (3, 0), (2, 6), (6, 2), (3, 7), (7, 3), (6, 6)], 'DL')
VAL = dict(A=1, B=3, C=3, D=2, E=1, F=4, G=2, H=4, I=1, J=8, K=5, L=1, M=3, N=1, O=1, P=3, Q=10, R=1, S=1, T=1, U=1, V=4, W=4, X=8, Y=4, Z=10)
def cell_xy(r, c): return BX + c * PITCH + 1, BY + r * PITCH + 1

def text_c(d, xy, s, font, fill, anchor='mm'): d.text(xy, s, font=font, fill=fill, anchor=anchor)
def fit_font(name, s, maxw, start, minsize=18):
    size = start
    while size > minsize and F(name, size).getlength(s) > maxw: size -= 2
    return F(name, size)

def board_base():
    im = Image.new('RGB', (W, H), PAL['bg'])
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([BX - 12, BY - 12, BX + 15 * PITCH + 9, BY + 15 * PITCH + 9], 18, fill=PAL['frame'])
    for r in range(15):
        for c in range(15):
            x, y = cell_xy(r, c); p = P.get((r, c))
            d.rounded_rectangle([x, y, x + CELL, y + CELL], 5, fill=PAL[p] if p else PAL['sq'])
            label = '★' if (r, c) == (7, 7) else (p or '')
            if label:
                f = F('DejaVuSans-Bold.ttf', 22) if label == '★' else F(BOLD, 15)
                text_c(d, (x + CELL / 2, y + CELL / 2), label, f, PAL['premium_text'] if p else PAL['sq_text'])
    return im

_tiles = {}
def tile_img(ch, tier, size=CELL):
    key = (ch, tier, size)
    if key in _tiles: return _tiles[key]
    s = 4  # supersample for smooth edges
    im = Image.new('RGBA', (size * s, size * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, size * s - 1, size * s - 1], 7 * s, fill=PAL['tiers'][tier])
    d.rounded_rectangle([0, 0, size * s - 1, size * s - 1 - 6 * s], 7 * s, fill=PAL['tile'])
    text_c(d, (size * s / 2, size * s / 2 - 3 * s), ch, F(TILEF, int(size * 0.56) * s), PAL['ink'])
    text_c(d, (size * s - 8 * s, size * s - 13 * s), str(VAL[ch]), F(BOLD, int(size * 0.22) * s), PAL['ink'], 'rm')
    im = im.resize((size, size), Image.LANCZOS)
    _tiles[key] = im
    return im

# ---------- timeline ----------
def act_of(n):
    for i, a in enumerate(SB['acts']):
        if a['from'] <= n <= a['to']: return i, a
def say_dur(lines): return sum(TM['dialogue_base'] + TM['dialogue_per_char'] * len(l) for _, l in lines)

segs, t = [], 0.0
for i, card in enumerate(SB['intro']):
    segs.append(dict(kind='intro', i=i, start=t, dur=card['duration'])); t += card['duration']
for m in MOVES:
    n = m['n']; ai, act = act_of(n)
    ov = SB['moves'].get(str(n), {})
    say = ov.get('say', [])
    banner = TM['act_banner'] if n == act['from'] else 0.0
    drop = TM['tile_stagger'] * (len(m['tiles']) - 1) + TM['tile_drop']
    pop = TM['score_pop']
    hold = max(TM['hold_by_act'][ai], say_dur(say)) + ov.get('extra_hold', 0)
    seg = dict(kind='move', n=n, m=m, start=t, banner=banner, drop=drop, pop=pop, say=say, hold=hold)
    if n == MOVES[-1]['n']:
        fz = SB['finale']
        seg['steps'] = [fz['step_main']] + [fz['step_cross']] * (len(m['words']) - 1)
        seg['hold'] = sum(seg['steps']) + fz['stamp_hold'] + max(fz['say_hold'], say_dur(fz['say']))
        seg['say'] = fz['say']
    seg['dur'] = banner + drop + pop + seg['hold']
    segs.append(seg); t += seg['dur']
segs.append(dict(kind='outro', start=t, dur=SB['outro']['duration'])); t += SB['outro']['duration']
TOTAL = t

# running totals before each move
before = {}; tot = {'Calvin': 0, 'Hobbes': 0}
for m in MOVES:
    before[m['n']] = dict(tot); tot[m['who']] += m['score']
FINAL = dict(tot)

# boards with all tiles of earlier moves already settled
_settled = {}
def settled(n):
    if n in _settled: return _settled[n]
    im = board_base() if n == 1 else settled(n - 1).copy()
    if n > 1:
        pm = MOVES[n - 2]
        for r, c, ch in pm['tiles']:
            x, y = cell_xy(r, c); ti = tile_img(ch, pm['tier']); im.paste(ti, (x, y), ti)
    _settled[n] = im
    return im

# ---------- drawing helpers ----------
def pill(d, x, y, text, font, bg, fg, padx=14, h=40, anchor='l'):
    w = font.getlength(text) + 2 * padx
    if anchor == 'r': x -= w
    d.rounded_rectangle([x, y, x + w, y + h], h // 2, fill=bg)
    text_c(d, (x + w / 2, y + h / 2 + 1), text, font, fg)
    return x + w

def header(d, n, alpha=1.0):
    ai, act = act_of(n); m = MOVES[n - 1]
    text_c(d, (60, 58), f'MOVE {n:02d} / {len(MOVES)}', F(BOLD, 30), PAL['muted'], 'lm')
    text_c(d, (60, 112), f"{act['label']} · {act['title']}", fit_font(DISPLAY, f"{act['label']} · {act['title']}", 600, 38), PAL['fg'], 'lm')
    # cheat-o-meter
    x0, y0, sw, sh, gap = 700, 50, 36, 22, 4
    text_c(d, (x0, y0 - 16), 'CHEAT-O-METER', F(BOLD, 20), PAL['muted'], 'lm')
    for i in range(8):
        col = PAL['tiers'][i] if i <= m['tier'] else PAL['line']
        d.rounded_rectangle([x0 + i * (sw + gap), y0, x0 + i * (sw + gap) + sw, y0 + sh], 5, fill=col)
    text_c(d, (x0, y0 + 50), SB['tiers'][m['tier']], fit_font(BOLD, SB['tiers'][m['tier']], 320, 32), PAL['tiers'][m['tier']], 'lm')

def grade_line(d, m, y, a=1.0):
    main = m['words'][0]['g']
    label = {'US': '✓ IN THE US DICTIONARY', 'UK': '✓ BRITISH DICTIONARY ONLY', 'NO': '✗ NOT A WORD'}[main]
    if main == 'NO' and m['word'] in ('CALVIN', 'SUSIE', 'CALVINBALL'): label = '✗ PROPER NOUN'
    col = mix(PAL['panel'], PAL[main], a)
    xe = pill(d, 60, y, label, F('DejaVuSans-Bold.ttf', 26), col, mix(PAL['panel'], PAL['bg'], a), h=46)
    junk = sum(1 for w in m['words'][1:] if w['g'] == 'NO')
    extra = []
    if junk: extra.append(f'+ {junk} gibberish cross-word' + ('s' if junk > 1 else ''))
    if m['bingo']: extra.append('+50 for using all 7 tiles')
    if extra: text_c(d, (xe + 16, y + 24), '  ·  '.join(extra), fit_font(BOLD, '  ·  '.join(extra), 1020 - xe - 16, 28, 18), mix(PAL['bg'], PAL['muted'], a), 'lm')

def totals(d, cal, hob):
    y = 1305
    text_c(d, (60, y), 'CALVIN', F(BOLD, 28), PAL['Calvin'], 'lm')
    text_c(d, (60 + F(BOLD, 28).getlength('CALVIN ') + 4, y), f'{int(cal):,}', F(DISPLAY, 36), PAL['fg'], 'lm')
    text_c(d, (1020, y), f'{int(hob):,}', F(DISPLAY, 36), PAL['fg'], 'rm')
    text_c(d, (1020 - F(DISPLAY, 36).getlength(f'{int(hob):,}') - 12, y), 'HOBBES', F(BOLD, 28), PAL['Hobbes'], 'rm')
    # tug-of-war bar
    x0, x1 = 400, 680; tot = max(1, cal + hob); mid = x0 + (x1 - x0) * (cal / tot if cal + hob else 0.5)
    d.rounded_rectangle([x0, y - 5, x1, y + 5], 5, fill=PAL['line'])
    d.rounded_rectangle([x0, y - 5, mid, y + 5], 5, fill=PAL['Calvin'])
    d.rounded_rectangle([mid, y - 5, x1, y + 5], 5, fill=PAL['Hobbes'])

def dialogue(d, lines, shown, y0=1192, maxw=960):
    y = y0
    for (who, text), a in zip(lines[-2:], shown[-2:]):
        if a <= 0: continue
        nm = who.upper() + '  '
        f = F(BOLD, 26); fh = fit_font(HAND, f'“{text}”', maxw - f.getlength(nm), 46, 28)
        text_c(d, (60, y + 4), nm, f, mix(PAL['bg'], PAL[who], a), 'lm')
        text_c(d, (60 + f.getlength(nm), y), f'“{text}”', fh, mix(PAL['bg'], PAL['fg'], a), 'lm')
        y += 50

def word_row(d, m, score_shown, a=1.0, word=None, sc_prefix='+'):
    who = m['who']
    xe = pill(d, 60, 1052, who.upper(), F(BOLD, 28), mix(PAL['bg'], PAL[who], a), PAL['bg'], h=50)
    sc = f'{sc_prefix}{int(score_shown)}'
    fs = F(DISPLAY, 60); scw = fs.getlength(sc)
    w = word or m['word']
    fw = fit_font(TILEF, w, 1020 - scw - 40 - (xe + 18), 66, 26)
    text_c(d, (xe + 18, 1078), w, fw, mix(PAL['bg'], PAL['fg'], a), 'lm')
    text_c(d, (1020, 1080), sc, fs, mix(PAL['bg'], PAL['highlight'], a), 'rm')

def ring(d, r, c, col, width=4, a=1.0):
    x, y = cell_xy(r, c)
    d.rounded_rectangle([x - 3, y - 3, x + CELL + 3, y + CELL + 3], 8, outline=mix(PAL['bg'], col, a), width=width)

# ---------- frame renderers ----------
def wrap(text, font, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if font.getlength(t) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def render_intro(seg, tau):
    card = SB['intro'][seg['i']]
    im = Image.new('RGB', (W, H), PAL['bg']); d = ImageDraw.Draw(im)
    def A(t0, dur=0.45): return ease_out(clamp((tau - t0) / dur))
    y = card.get('top', 430)
    a = A(0.1)
    for ln in wrap(card['kicker'], F(BOLD, 44), 920):
        text_c(d, (W / 2, y), ln, F(BOLD, 44), mix(PAL['bg'], PAL['fg'], a)); y += 58
    y += 40
    if 'tiles' in card:
        ts = card['tiles']; size = 120; gap = 14; x0 = (W - (len(ts) * size + (len(ts) - 1) * gap)) / 2
        for i, ch in enumerate(ts):
            p = clamp((tau - 0.7 - i * 0.12) / 0.35)
            if p <= 0: continue
            ti = tile_img(ch, 7, size)
            sc = 1.3 - 0.3 * ease_back(p); sz = max(2, int(size * sc))
            t2 = ti.resize((sz, sz), Image.LANCZOS)
            if p < 1: t2.putalpha(t2.getchannel('A').point(lambda v: int(v * ease_out(p))))
            im.paste(t2, (int(x0 + i * (size + gap) + (size - sz) / 2), int(y + (size - sz) / 2 - 40 * (1 - ease_out(p)))), t2)
        y += size + 60
    if 'title' in card:
        a = A(0.9); text_c(d, (W / 2, y + 30), card['title'], F(DISPLAY, 84), mix(PAL['bg'], PAL['highlight'], a)); y += 140
    a = A(1.7)
    for ln in wrap(card['after'], F(BODY, 40), 900):
        text_c(d, (W / 2, y), ln, F(BODY, 40), mix(PAL['bg'], PAL['muted'], a)); y += 54
    y += 40
    if card.get('say'):
        a = A(2.5)
        for who, line in card['say']:
            text_c(d, (W / 2, y), f'{who.upper()}', F(BOLD, 26), mix(PAL['bg'], PAL[who], a)); y += 50
            text_c(d, (W / 2, y), f'“{line}”', F(HAND, 64), mix(PAL['bg'], PAL['fg'], a)); y += 80
    if card.get('meter'):
        a = A(2.4); x0, w = 140, 800; seg_w = w / 8
        for i in range(8):
            d.rounded_rectangle([x0 + i * seg_w + 3, y, x0 + (i + 1) * seg_w - 3, y + 34], 8, fill=mix(PAL['bg'], PAL['tiers'][i], a))
        text_c(d, (x0, y + 70), 'honest Scrabble', F(BOLD, 28), mix(PAL['bg'], PAL['tiers'][0], a), 'lm')
        text_c(d, (x0 + w, y + 70), 'Calvinball', F(BOLD, 28), mix(PAL['bg'], PAL['tiers'][7], a), 'rm')
    # fade to black-green at the end of the last intro card
    if seg['i'] == len(SB['intro']) - 1:
        f = clamp((tau - (seg['dur'] - TM['intro_fade'])) / TM['intro_fade'])
        if f > 0: im = Image.blend(im, Image.new('RGB', (W, H), PAL['bg']), f)
    if seg['i'] > 0 or tau > 0.0:
        f = clamp(tau / 0.3)
        if f < 1: im = Image.blend(Image.new('RGB', (W, H), PAL['bg']), im, f)
    return im

def render_move(seg, tau):
    m, n = seg['m'], seg['n']
    im = settled(n).copy(); d = ImageDraw.Draw(im)
    header(d, n)
    tb = seg['banner']; t_drop = tau - tb; t_after = t_drop - seg['drop']
    # tiles
    for i, (r, c, ch) in enumerate(m['tiles']):
        p = clamp((t_drop - i * TM['tile_stagger']) / TM['tile_drop'])
        if p <= 0: continue
        x, y = cell_xy(r, c); ti = tile_img(ch, m['tier'])
        if p >= 1:
            im.paste(ti, (x, y), ti)
        else:
            sc = 1.45 - 0.45 * ease_back(p); sz = max(2, int(CELL * sc))
            t2 = ti.resize((sz, sz), Image.LANCZOS)
            t2.putalpha(t2.getchannel('A').point(lambda v, q=ease_out(min(1, p * 1.6)): int(v * q)))
            im.paste(t2, (int(x + (CELL - sz) / 2), int(y + (CELL - sz) / 2 - 36 * (1 - ease_out(p)))), t2)
    d = ImageDraw.Draw(im)
    is_final = 'steps' in seg
    # rings on the new tiles, fading through the hold
    if t_drop > 0 and not (is_final and t_after > seg['pop']):
        ra = 1.0 if t_after < seg['pop'] else clamp(1 - (t_after - seg['pop']) / max(0.6, seg['hold']) * 0.8)
        for i, (r, c, ch) in enumerate(m['tiles']):
            if t_drop - i * TM['tile_stagger'] >= TM['tile_drop']: ring(d, r, c, PAL['highlight'], 4, ra)
    # act banner
    if tb and tau < tb + 0.25:
        a = clamp(tau / 0.3) * clamp((tb + 0.25 - tau) / 0.35)
        ai, act = act_of(n)
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.rectangle([BX - 12, BY + 310, BX + 15 * PITCH + 9, BY + 550], fill=PAL['bg'] + (int(235 * a),))
        text_c(od, (W / 2, BY + 380), act['label'], F(DISPLAY, 50), PAL['tiers'][m['tier']] + (int(255 * a),))
        text_c(od, (W / 2, BY + 465), act['title'], F(HAND, 72), PAL['fg'] + (int(255 * a),))
        im.paste(ov, (0, 0), ov); d = ImageDraw.Draw(im)
    # panel
    prev = before[n]
    if t_drop < 0:
        totals(d, prev['Calvin'], prev['Hobbes']); return im
    wa = ease_out(clamp(t_drop / 0.3))
    pp = ease_in_out(clamp(t_after / seg['pop']))
    if not is_final:
        word_row(d, m, m['score'] * pp, wa)
        if t_after > 0: grade_line(d, m, 1122, ease_out(clamp(t_after / 0.3)))
        cal = prev['Calvin'] + (m['score'] * pp if m['who'] == 'Calvin' else 0)
        hob = prev['Hobbes'] + (m['score'] * pp if m['who'] == 'Hobbes' else 0)
        totals(d, cal, hob)
        if seg['say'] and t_after > 0:
            shown, t0 = [], 0.1
            for who, l in seg['say']:
                shown.append(ease_out(clamp((t_after - t0) / 0.3))); t0 += TM['dialogue_base'] + TM['dialogue_per_char'] * len(l)
            dialogue(d, seg['say'], shown)
        return im
    return render_finale(seg, im, d, t_after, prev)

def render_finale(seg, im, d, t_after, prev):
    m = seg['m']; words = m['words']
    tb = t_after - seg['pop']
    steps = seg['steps']; ends = [sum(steps[:i + 1]) for i in range(len(steps))]
    k = max(0, min(len(words) - 1, sum(1 for i in range(len(steps)) if tb >= ends[i] - steps[i]) - 1)) if tb >= 0 else -1
    running = sum(w['s'] for w in words[:k + 1]) if k >= 0 else 0
    if 0 <= k:
        step_p = clamp((tb - (ends[k] - steps[k])) / 0.35)
        running = sum(w['s'] for w in words[:k]) + words[k]['s'] * ease_in_out(step_p)
    stamp_t = tb - ends[-1]
    # spotlight on the current word (until the stamp)
    if tb >= 0 and stamp_t < 0.2:
        cells = {tuple(x) for x in words[k]['cells']}
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        for r in range(15):
            for c in range(15):
                if (r, c) not in cells:
                    x, y = cell_xy(r, c); od.rectangle([x - 1, y - 1, x + CELL + 1, y + CELL + 1], fill=PAL['frame'] + (170,))
        im.paste(ov, (0, 0), ov); d = ImageDraw.Draw(im)
        for r, c in cells: ring(d, r, c, PAL['highlight'], 4)
    # panel
    if tb < 0:
        word_row(d, m, 0, 1.0)
    elif stamp_t < 0:
        w = words[k]
        label = w['w'] if k == 0 else f"{w['w']}"
        word_row(d, m, w['s'], 1.0, word=label)
        text_c(d, (60, 1145), ('Main word, ×2 for the double-word square' if k == 0 else f'Cross-word {k} of 6' + (', ×2 (double word)' if k == 6 else '')),
               F(BOLD, 30), PAL['muted'], 'lm')
        text_c(d, (1020, 1145), f'total {int(running)}', F(DISPLAY, 36), PAL['highlight'], 'rm')
    else:
        word_row(d, m, 957, 1.0, word='ZQFMGB', sc_prefix='+')
        grade_line(d, m, 1122, 1.0)
    cal = prev['Calvin'] + (running if stamp_t < 0 else m['score'])
    totals(d, cal, prev['Hobbes'])
    # 957 stamp
    if stamp_t >= 0:
        p = clamp(stamp_t / 0.45)
        ov = Image.new('RGBA', (900, 420), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.rounded_rectangle([60, 40, 840, 380], 40, fill=PAL['bg'] + (int(225 * ease_out(p)),), outline=PAL['highlight'] + (int(255 * ease_out(p)),), width=8)
        text_c(od, (450, 175), '957', F(DISPLAY, 210), PAL['highlight'] + (int(255 * ease_out(p)),))
        text_c(od, (450, 320), 'points. For ZQFMGB.', F(BOLD, 44), PAL['fg'] + (int(255 * ease_out(p)),))
        sc = 1.6 - 0.6 * ease_back(p)
        ov = ov.rotate(-6 * ease_out(p), resample=Image.BICUBIC, expand=False)
        ov = ov.resize((int(900 * sc), int(420 * sc)), Image.LANCZOS)
        im.paste(ov, (int(W / 2 - ov.width / 2), int(BY + 450 - ov.height / 2)), ov); d = ImageDraw.Draw(im)
        st = stamp_t - SB['finale']['stamp_hold']
        if st > 0:
            shown, t0 = [], 0.0
            for who, l in seg['say']:
                shown.append(ease_out(clamp((st - t0) / 0.3))); t0 += TM['dialogue_base'] + TM['dialogue_per_char'] * len(l)
            dialogue(d, seg['say'], shown)
    return im

def render_outro(seg, tau):
    base = settled(len(MOVES) + 1).copy()
    a = ease_out(clamp(tau / 0.6))
    dim = Image.new('RGB', (W, H), PAL['bg'])
    im = Image.blend(base, dim, 0.84 * a); d = ImageDraw.Draw(im)
    o = SB['outro']
    text_c(d, (W / 2, 470), 'Final score', F(BOLD, 36), mix(PAL['bg'], PAL['muted'], a))
    text_c(d, (W / 2, 560), o['title'], fit_font(DISPLAY, o['title'], 960, 64), mix(PAL['bg'], PAL['highlight'], a))
    y = 680
    for i, ln in enumerate(o['lines']):
        b = ease_out(clamp((tau - 0.5 - i * 0.35) / 0.4))
        for sub in wrap(ln, F(BODY, 36), 900):
            text_c(d, (W / 2, y), sub, F(BODY, 36), mix(PAL['bg'], PAL['fg'], b)); y += 50
        y += 26
    if o.get('credit'): text_c(d, (W / 2, 1240), o['credit'], F(BOLD, 30), mix(PAL['bg'], PAL['muted'], a))
    return im

def frame_at(t):
    for seg in segs:
        if seg['start'] <= t < seg['start'] + seg['dur']:
            tau = t - seg['start']
            if seg['kind'] == 'intro': return render_intro(seg, tau)
            if seg['kind'] == 'outro': return render_outro(seg, tau)
            im = render_move(seg, tau)
            if seg['n'] == 1 and tau < 0.35:   # fade in from the intro
                im = Image.blend(Image.new('RGB', (W, H), PAL['bg']), im, ease_out(tau / 0.35))
            return im
    return render_outro(segs[-1], segs[-1]['dur'] - 0.001)

def main():
    if '--frames' in sys.argv:
        for s in sys.argv[sys.argv.index('--frames') + 1:]:
            frame_at(float(s)).save(os.path.join(HERE, f'frame_{float(s):06.2f}.png')); print('wrote', s)
        return
    out = os.path.join(HERE, SB['video']['output'])
    nframes = int(math.ceil(TOTAL * FPS))
    print(f'{TOTAL:.1f}s, {nframes} frames -> {out}', flush=True)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', SB['video']['preset'], '-crf', str(SB['video']['crf']), '-tune', 'animation',
           '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(nframes):
        ff.stdin.write(frame_at(i / FPS).tobytes())
        if i % 300 == 0: print(f'  frame {i}/{nframes}', flush=True)
    ff.stdin.close(); ff.wait()
    print('done', os.path.getsize(out) // 1024, 'KB')

if __name__ == '__main__':
    main()
