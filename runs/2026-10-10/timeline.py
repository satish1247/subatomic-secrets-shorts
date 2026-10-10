"""2026-10-10 story: Google Cloud's Gemini agent, Arjun & Nimi (contract: DURATION + render_frame)."""
import json
import math
import os
import cairo
from gfx import (FONT, W, H, Track, ease_back, ease_out, seg, src, text, ellipse, rrect, lerp,
                 wrap, soft_shadow, fill_out, limb, TEAL, TEAL_D, ORANGE, WHITE, OUT)
from characters import ARJUN_BASE, draw_arjun, draw_nimi_bust
from backgrounds import draw_home_bg, draw_sunbeam
import brand
import sfx

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "lines.json"), encoding="utf8") as _f:
    DATA = json.load(_f)
DURATION = DATA["duration"]
LINES = DATA["lines"]
ENV = [sfx.envelope(os.path.join(HERE, k["wav"])) for k in LINES]
END = DURATION - 1.4
ST = [k["start"] for k in LINES]
Y_ = brand.BRAND_YELLOW
K_ = brand.BRAND_BLACK
PANEL = (0.10, 0.11, 0.14)
GREY = (0.62, 0.65, 0.70)
RED = (0.88, 0.22, 0.18)
GREEN = (0.20, 0.72, 0.42)
CAP_SIZE = 62
PX, PY, PW, PH = 80, 300, W - 160, 470          # info panel (safe area)
ARJUN_X, NIMI_X = 330, 830


# ------------------------------------------------------------------ captions
def _chunks(line):
    probe = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 8, 8))
    words, out, cur = line["text"].split(), [], []
    for w in words:
        trial = cur + [w]
        if len(wrap(probe, " ".join(trial), CAP_SIZE, W - 200)) > 2 and cur:
            out.append(" ".join(cur))
            cur = [w]
        else:
            cur = trial
    out.append(" ".join(cur))
    if len(out) > 1 and len(cur) < 3:   # avoid one-word caption tails
        prev = out[-2].split()
        out[-2:] = [" ".join(prev[:-2]), " ".join(prev[-2:] + cur)]
    total = sum(len(c) for c in out)
    t, res = line["start"], []
    for c in out:
        res.append((t, c))
        t += line["dur"] * len(c) / total
    return res


CHUNKS = [_chunks(k) for k in LINES]


def _active(t):
    for i in range(len(LINES)):
        nxt = ST[i + 1] if i + 1 < len(LINES) else END
        if (ST[i] - 0.2 if i else 0) <= t < nxt - 0.2:
            return i
    return len(LINES) - 1 if t < END else None


def _caption(t):
    i = _active(t)
    if i is None:
        return None, None
    cur = CHUNKS[i][0]
    for c in CHUNKS[i]:
        if t >= c[0] - 0.1:
            cur = c
    return i, cur


def _env(i, t):
    k = int((t - ST[i]) * 30)
    return float(ENV[i][k]) if 0 <= k < len(ENV[i]) else 0.0


# ------------------------------------------------------------------ Arjun
PANIC = dict(al1=2.5, al2=0.5, ar1=2.5, ar2=0.5, eye_wide=1.4, brow_l=1, brow_r=1,
             sweat=1, hair_wild=0.6, mc=-0.3, head_tilt=0.0, scratch=0, lid=0, sunglasses=0)
LISTEN = dict(al1=0.15, al2=-0.3, ar1=0.15, ar2=-0.3, eye_wide=1.0, brow_l=0.3, brow_r=0.3,
              sweat=0, hair_wild=0, mc=0.35, head_tilt=0.06, scratch=0, lid=0, sunglasses=0)
PUZZLED = dict(al1=0.2, al2=-0.3, ar1=2.2, ar2=1.9, eye_wide=1.15, brow_l=1, brow_r=-0.3,
               mc=-0.2, head_tilt=0.14, scratch=1, sweat=0, hair_wild=0, lid=0, sunglasses=0)
WORRY = dict(al1=0.9, al2=-1.9, ar1=0.9, ar2=-1.9, eye_wide=1.2, brow_l=0.9, brow_r=0.9,
             mc=-0.5, sweat=1, head_tilt=-0.05, scratch=0, hair_wild=0, lid=0, sunglasses=0)
HAPPY = dict(al1=2.6, al2=0.2, ar1=2.6, ar2=0.2, eye_wide=1.2, brow_l=0.8, brow_r=0.8,
             mc=0.95, teeth=1, sweat=0, head_tilt=0.0, scratch=0, hair_wild=0, lid=0,
             sunglasses=0)
SAD = dict(al1=0.05, al2=-0.1, ar1=0.05, ar2=-0.1, eye_wide=0.9, lid=0.45, brow_l=-0.3,
           brow_r=-0.3, mc=-0.6, teeth=0, sweat=0, head_tilt=0.12, scratch=0, hair_wild=0,
           sunglasses=0)
COOL = dict(al1=0.75, al2=-1.75, ar1=0.75, ar2=-1.75, eye_wide=1.0, lid=0, brow_l=0.4,
            brow_r=0.4, mc=0.8, teeth=0, sweat=0, head_tilt=-0.08, scratch=0, hair_wild=0,
            sunglasses=1)
POSES = [PANIC, LISTEN, PUZZLED, LISTEN, WORRY, LISTEN, PUZZLED, LISTEN, HAPPY, SAD, COOL]


def _arjun_track():
    keys = [(0.0, dict(PANIC))]
    for i in range(1, len(LINES)):
        keys.append((ST[i] - 0.25, {}))
        keys.append((ST[i] + 0.05, dict(POSES[i]), "back" if POSES[i] in (HAPPY, PANIC) else "io"))
    return Track(dict(ARJUN_BASE, x=ARJUN_X, y=1260, teeth=0), keys)


ARJUN = _arjun_track()


def _arjun_pose(t):
    p = ARJUN.at(t)
    i = _active(t)
    if i is not None and LINES[i]["who"] == "arjun":
        e = _env(i, t)
        p["mo"] = 0.06 + 0.55 * e
        p["mw"] = 0.85 + 0.15 * e
        p["head_turn"], p["look_x"] = 0.0, 0.0
        p["bob"] = -6 * e
    else:
        p["head_turn"], p["look_x"] = 0.45, 0.8      # looks at Nimi while she talks
    if i == 0:
        p["shake"] = 0.35
    if i == 8:
        p["bob"] = -30 * abs(math.sin((t - ST[8]) * 9))
    return p


# ------------------------------------------------------------------ set
def _desk(ctx, t, i):
    x0, y0 = 610, 1265
    for dx in (20, 330):
        rrect(ctx, x0 + dx, y0, 22, 330, 6)
        fill_out(ctx, (0.55, 0.33, 0.18), 4)
    rrect(ctx, x0 - 10, y0 - 26, 380, 34, 8)
    fill_out(ctx, (0.72, 0.45, 0.25), 5)
    # laptop
    lx, ly = x0 + 90, y0 - 26
    ctx.move_to(lx, ly)
    ctx.line_to(lx + 200, ly)
    ctx.line_to(lx + 190, ly - 12)
    ctx.line_to(lx + 10, ly - 12)
    ctx.close_path()
    fill_out(ctx, (0.75, 0.78, 0.82), 4)
    rrect(ctx, lx + 15, ly - 150, 170, 138, 10)
    fill_out(ctx, (0.25, 0.27, 0.31), 4)
    glow = 0.5 + 0.5 * math.sin(t * 3)
    rrect(ctx, lx + 27, ly - 138, 146, 114, 6)
    src(ctx, (0.2 + 0.2 * glow, 0.55, 0.62))
    ctx.fill()
    ellipse(ctx, lx + 100, ly - 81, 22, 22)
    src(ctx, Y_)
    ctx.fill()


def _nimi(ctx, t):
    u = ease_out(seg(t, ST[1] - 0.45, ST[1] - 0.05))
    if u <= 0.01:
        return
    i = _active(t)
    bob = 0.0
    if i is not None and LINES[i]["who"] == "nimi":
        bob = -10 * _env(i, t)
    x = lerp(W + 260, NIMI_X, u)
    soft_shadow(ctx, x, 1330, 150, 18, 0.2)
    draw_nimi_bust(ctx, x, 1215 + bob, 0.95, t)


# ------------------------------------------------------------------ panel helpers
def _pop(t, t0, d=0.35):
    return ease_back(seg(t, t0, t0 + d))


def _scaled(ctx, x, y, u, fn):
    if u <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(u, u)
    ctx.translate(-x, -y)
    fn()
    ctx.restore()


def _chip(ctx, x, y, w, h, label, fill=Y_, ink=None, size=40):
    rrect(ctx, x - w / 2, y - h / 2, w, h, h / 2)
    src(ctx, fill)
    ctx.fill()
    text(ctx, label, x, y + size * 0.36, size, ink or K_)


def _doc_icon(ctx, x, y, s, kind):
    rrect(ctx, x - 45 * s, y - 58 * s, 90 * s, 116 * s, 10 * s)
    fill_out(ctx, WHITE, 4 * s, K_)
    if kind == "doc":
        for j in range(4):
            rrect(ctx, x - 28 * s, y - 36 * s + j * 22 * s, (56 if j < 3 else 34) * s, 9 * s, 4 * s)
            src(ctx, GREY)
            ctx.fill()
    elif kind == "slides":
        rrect(ctx, x - 30 * s, y - 34 * s, 60 * s, 40 * s, 5 * s)
        src(ctx, ORANGE)
        ctx.fill()
        rrect(ctx, x - 30 * s, y + 18 * s, 60 * s, 9 * s, 4 * s)
        src(ctx, GREY)
        ctx.fill()
    elif kind == "code":
        text(ctx, "</>", x, y + 14 * s, 40 * s, TEAL_D)
    elif kind == "chat":
        text(ctx, "?", x, y + 22 * s, 64 * s, TEAL_D)


def _bot(ctx, x, y, s, col=TEAL):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    limb(ctx, [(0, -62), (0, -84)], 6, K_, 0)
    ellipse(ctx, 0, -88, 9, 9)
    src(ctx, Y_)
    ctx.fill()
    rrect(ctx, -48, -62, 96, 74, 22)
    fill_out(ctx, col, 5, K_)
    rrect(ctx, -34, -46, 68, 40, 14)
    src(ctx, K_)
    ctx.fill()
    for dx in (-15, 15):
        ellipse(ctx, dx, -26, 7, 9)
        src(ctx, (0.6, 1.0, 0.95))
        ctx.fill()
    rrect(ctx, -32, 14, 64, 40, 12)
    fill_out(ctx, col, 5, K_)
    ctx.restore()


def _clock(ctx, x, y, r, t):
    ellipse(ctx, x, y, r, r)
    fill_out(ctx, WHITE, 6, K_)
    for k in range(12):
        a = k * math.pi / 6
        limb(ctx, [(x + 0.78 * r * math.sin(a), y - 0.78 * r * math.cos(a)),
                   (x + 0.88 * r * math.sin(a), y - 0.88 * r * math.cos(a))], 4, K_, 0)
    for spd, ln, wd in ((0.5, 0.5, 9), (6.0, 0.75, 5)):
        a = t * spd
        limb(ctx, [(x, y), (x + ln * r * math.sin(a), y - ln * r * math.cos(a))], wd, K_, 0)
    ellipse(ctx, x, y, 8, 8)
    src(ctx, ORANGE)
    ctx.fill()


def _lock(ctx, x, y, s):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.arc(0, -30, 38, math.pi, 0)
    ctx.set_line_width(16)
    src(ctx, GREY)
    ctx.stroke()
    rrect(ctx, -60, -30, 120, 96, 16)
    fill_out(ctx, Y_, 5, K_)
    ellipse(ctx, 0, 8, 12, 12)
    src(ctx, K_)
    ctx.fill()
    rrect(ctx, -5, 10, 10, 30, 4)
    ctx.fill()
    ctx.restore()


# ------------------------------------------------------------------ panel scenes
def _title(ctx, s, y, size=58, col=Y_):
    ctx.select_font_face(FONT, 0, 1)
    while size > 36:
        ctx.set_font_size(size)
        if ctx.text_extents(s).x_advance <= PW - 90:
            break
        size -= 2
    text(ctx, s, W / 2, y, size, col)


def _scene(ctx, i, t):
    t0 = ST[i] - 0.2
    cx = W / 2
    if i == 0:
        _title(ctx, "DUE BY MONDAY", PY + 85)
        for j, (kind, lab) in enumerate((("doc", "REPORT"), ("slides", "SLIDES"), ("code", "CODE FIXES"))):
            x = cx + (j - 1) * 290
            u = _pop(t, 0.25 + j * 0.45)
            _scaled(ctx, x, PY + 250, u, lambda x=x, kind=kind: _doc_icon(ctx, x, PY + 240, 1.2, kind))
            if u > 0.5:
                text(ctx, lab, x, PY + 385, 38, WHITE)
        if t > 2.2:
            a = 0.5 + 0.5 * math.sin(t * 14)
            text(ctx, "!!!", cx + 330, PY + 85, 58, RED, alpha=a)
    elif i in (1, 2):
        _title(ctx, "NEW: GEMINI AGENT", PY + 95, 64)
        text(ctx, "“A UNIVERSAL AGENT FOR WORK”", cx, PY + 165, 40, WHITE)
        _scaled(ctx, cx, PY + 300, _pop(t, ST[1] + 0.3),
                lambda: _bot(ctx, cx, PY + 330, 1.25, Y_))
        _chip(ctx, cx, PY + 425, 520, 62, "GOOGLE CLOUD · OCT 8", TEAL, WHITE, 34)
        if i == 2:
            u = _pop(t, ST[2])
            _scaled(ctx, cx + 300, PY + 300, u,
                    lambda: text(ctx, "?", cx + 300, PY + 350, 150, Y_))
            _scaled(ctx, cx - 300, PY + 300, u,
                    lambda: text(ctx, "1", cx - 300, PY + 350, 150, Y_))
    elif i == 3:
        _title(ctx, "ONE PROMPT BOX", PY + 85)
        rrect(ctx, PX + 70, PY + 125, PW - 140, 90, 45)
        fill_out(ctx, WHITE, 5, Y_)
        n = int(max(0, t - ST[3]) * 18)
        text(ctx, "Ask Gemini agent..."[:n], PX + 115, PY + 185, 38, (0.35, 0.35, 0.4), "left")
        for j, (kind, lab) in enumerate((("chat", "ANSWERS"), ("doc", "DOCUMENTS"), ("code", "CODE"))):
            x = cx + (j - 1) * 290
            u = _pop(t, ST[3] + 1.4 + j * 0.55)
            _scaled(ctx, x, PY + 330, u, lambda x=x, kind=kind: _doc_icon(ctx, x, PY + 320, 0.95, kind))
            if u > 0.5:
                text(ctx, lab, x, PY + 435, 36, WHITE)
    elif i == 4:
        _title(ctx, "IT WILL TAKE... DAYS?", PY + 85)
        _clock(ctx, cx, PY + 280, 140, t)
        a = 0.6 + 0.4 * math.sin(t * 10)
        text(ctx, "…", cx + 230, PY + 300, 90, Y_, alpha=a)
    elif i in (5, 6):
        _title(ctx, "HOURS... OR EVEN DAYS", PY + 85)
        _clock(ctx, PX + 150, PY + 270, 100, t * 4)
        _bot(ctx, cx - 20, PY + 300, 1.1, Y_)
        u_s = seg(t, ST[5] + 2.6, ST[5] + 3.0)
        for j in range(3):
            u = _pop(t, ST[5] + 2.8 + j * 0.3)
            bx, by = PX + PW - 120, PY + 165 + j * 92
            if u > 0.01:
                limb(ctx, [(cx + 45, PY + 270), (bx - 45, by)], 4, GREY, 0)
            _scaled(ctx, bx, by, u, lambda bx=bx, by=by: _bot(ctx, bx, by + 12, 0.5, TEAL))
        if u_s > 0.5:
            text(ctx, "TEMPORARY HELPER AGENTS", cx, PY + 445, 36, WHITE)
        if i == 6:
            k = _pop(t, ST[6])
            _scaled(ctx, cx, PY + 200, k, lambda: _chip(ctx, cx, PY + 200, 600, 74,
                                                       "HELPERS FOR HELPERS?!", RED, WHITE, 40))
    elif i == 7:
        _title(ctx, "BEST MODEL FOR EACH JOB", PY + 85)
        _bot(ctx, cx, PY + 280, 1.0, Y_)
        for j, (lab, col) in enumerate((("GEMINI", TEAL), ("CLAUDE", ORANGE))):
            x = cx + (-1 if j == 0 else 1) * 290
            u = _pop(t, ST[7] + 2.2 + j * 0.9)
            if u > 0.01:
                limb(ctx, [(cx + (-1 if j == 0 else 1) * 60, PY + 260), (x, PY + 260)], 5, GREY, 0)
            _scaled(ctx, x, PY + 260, u,
                    lambda x=x, lab=lab, col=col: _chip(ctx, x, PY + 260, 250, 80, lab, col, WHITE, 42))
        text(ctx, "IT PICKS PER TASK", cx, PY + 430, 36, WHITE)
    elif i == 8:
        _title(ctx, "DOWNLOAD?", PY + 85)
        u = seg(t, ST[8] + 0.2, ST[8] + 1.2)
        rrect(ctx, PX + 120, PY + 240, PW - 240, 60, 30)
        fill_out(ctx, (0.25, 0.27, 0.31), 4, WHITE)
        if u > 0:
            rrect(ctx, PX + 126, PY + 246, (PW - 252) * u, 48, 24)
            src(ctx, GREEN)
            ctx.fill()
        text(ctx, "%d%%" % int(u * 99), cx, PY + 380, 54, WHITE)
    elif i == 9:
        _title(ctx, "NOT FOR EVERYONE YET", PY + 85)
        _scaled(ctx, cx, PY + 230, _pop(t, ST[9] + 0.1), lambda: _lock(ctx, cx, PY + 230, 1.2))
        u = _pop(t, ST[9] + 1.6)
        _scaled(ctx, cx, PY + 385, u, lambda: _chip(ctx, cx, PY + 385, 720, 74,
                                                   "PRIVATE PREVIEW · BUSINESSES", Y_, K_, 38))
    elif i == 10:
        _title(ctx, "THIS WEEKEND'S AGENT:", PY + 85)
        u = _pop(t, ST[10] + 0.6)
        _scaled(ctx, cx, PY + 270, u, lambda: _chip(ctx, cx, PY + 270, 520, 130, "ARJUN", Y_, K_, 84))
        if u > 0.5:
            text(ctx, "(HUMAN EDITION)", cx, PY + 410, 38, WHITE)


def _panel(ctx, t):
    i = _active(t)
    if i is None:
        return
    group = {2: 1, 6: 5}.get(i, i)
    t0 = 0.0 if group == 0 else ST[group] - 0.2
    u = ease_back(seg(t, t0, t0 + 0.35))
    ctx.save()
    ctx.translate(W / 2, PY + PH / 2)
    ctx.scale(lerp(0.85, 1.0, u), lerp(0.85, 1.0, u))
    ctx.translate(-W / 2, -(PY + PH / 2))
    rrect(ctx, PX, PY, PW, PH, 36)
    src(ctx, PANEL, 1.0)
    ctx.fill_preserve()
    src(ctx, Y_)
    ctx.set_line_width(6)
    ctx.stroke()
    ctx.rectangle(PX, PY, PW, PH)
    ctx.clip()
    _scene(ctx, i, t)
    ctx.restore()


# ------------------------------------------------------------------ frame
def render_frame(t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    draw_home_bg(ctx)
    draw_sunbeam(ctx, 0.08)
    i = _active(t)
    _desk(ctx, t, i)
    p = _arjun_pose(t)
    soft_shadow(ctx, p["x"], 1600, 130, 22)
    draw_arjun(ctx, p, t)
    _nimi(ctx, t)
    # dim the top so the panel pops
    g = cairo.LinearGradient(0, 0, 0, 820)
    g.add_color_stop_rgba(0, 0.05, 0.05, 0.07, 0.75)
    g.add_color_stop_rgba(1, 0.05, 0.05, 0.07, 0.0)
    ctx.rectangle(0, 0, W, 820)
    ctx.set_source(g)
    ctx.fill()
    _panel(ctx, t)
    ci, chunk = _caption(t)
    if chunk:
        who = LINES[ci]["who"]
        tag = "ARJUN" if who == "arjun" else "NIMI"
        pop = ease_back(seg(t, chunk[0] - 0.1, chunk[0] + 0.12))
        brand.caption(ctx, chunk[1], y=1500, size=CAP_SIZE, pop=max(0.85, pop))
        _chip(ctx, 210, 1500 - 125, 190, 50, tag, Y_ if who == "arjun" else TEAL,
              K_ if who == "arjun" else WHITE, 30)
    brand.watermark(ctx)
    brand.end_card(ctx, t, END)
    return surf
