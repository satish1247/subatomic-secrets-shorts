"""2026-11-11 story: Spotify AI DJ gets 9 new voices + less-chatter setting, Arjun & Nimi (contract: DURATION + render_frame)."""
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
POSES = [PANIC, LISTEN, LISTEN, PUZZLED, LISTEN, LISTEN, HAPPY, LISTEN, LISTEN, PUZZLED, LISTEN, COOL]


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
    if i == 6:
        p["bob"] = -24 * abs(math.sin((t - ST[6]) * 9))
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
    rrect(ctx, lx + 27, ly - 138, 146, 114, 6)
    src(ctx, (0.20, 0.42, 0.62))
    ctx.fill()
    for j in range(3):
        rrect(ctx, lx + 40, ly - 120 + j * 26, 120 - 30 * j, 12, 6)
        src(ctx, WHITE, 0.7)
        ctx.fill()
    if i == 0 or (i is None and t < 1):
        for k in range(3):
            ph = ((t * 0.7) + k / 3.0) % 1.0
            _note(ctx, lx + 40 + 60 * k, ly - 160 - 140 * ph, 0.55, alpha=1 - ph)
        text(ctx, "BLAH", lx + 100, ly - 330, 46, RED, alpha=0.5 + 0.5 * math.sin(t * 8))


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


# ------------------------------------------------------------------ extra icons
def _browser(ctx, x, y, w, h, dark):
    rrect(ctx, x - w / 2, y - h / 2, w, h, 14)
    fill_out(ctx, (0.30, 0.32, 0.36) if dark else WHITE, 4, K_)
    rrect(ctx, x - w / 2, y - h / 2, w, 30, 14)
    src(ctx, GREY)
    ctx.fill()
    for k in range(3):
        ellipse(ctx, x - w / 2 + 22 + k * 22, y - h / 2 + 15, 6, 6)
        src(ctx, (RED, ORANGE, GREEN)[k])
        ctx.fill()
    if dark:
        s = min(w, h) * 0.22
        limb(ctx, [(x - s, y + 15 - s), (x + s, y + 15 + s)], 12, RED, 0)
        limb(ctx, [(x + s, y + 15 - s), (x - s, y + 15 + s)], 12, RED, 0)
    else:
        for j in range(3):
            rrect(ctx, x - w / 2 + 20, y - h / 2 + 50 + j * 26, (w - 40) * (0.9 - 0.2 * j), 12, 6)
            src(ctx, GREY)
            ctx.fill()


def _bug(ctx, x, y, s, col=RED):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for k in (-1, 1):
        for j in range(3):
            limb(ctx, [(k * 30, -15 + j * 22), (k * 62, -28 + j * 30)], 6, K_, 0)
        limb(ctx, [(k * 10, -48), (k * 26, -78)], 5, K_, 0)
    ellipse(ctx, 0, 0, 38, 50)
    fill_out(ctx, col, 5, K_)
    ellipse(ctx, 0, -50, 22, 18)
    fill_out(ctx, K_, 3, K_)
    limb(ctx, [(0, -30), (0, 48)], 4, K_, 0)
    ctx.restore()


def _pie(ctx, x, y, r, frac):
    ellipse(ctx, x, y, r, r)
    fill_out(ctx, (0.30, 0.32, 0.36), 5, K_)
    if frac > 0:
        ctx.move_to(x, y)
        ctx.arc(x, y, r, -math.pi / 2, -math.pi / 2 + 2 * math.pi * frac)
        ctx.close_path()
        src(ctx, Y_)
        ctx.fill()
    ellipse(ctx, x, y, r, r)
    src(ctx, K_)
    ctx.set_line_width(5)
    ctx.stroke()


def _magnifier(ctx, x, y, s):
    limb(ctx, [(x + 40 * s, y + 40 * s), (x + 95 * s, y + 95 * s)], 22 * s, (0.55, 0.33, 0.18), 4)
    ellipse(ctx, x, y, 58 * s, 58 * s)
    src(ctx, (0.75, 0.92, 1.0), 0.45)
    ctx.fill_preserve()
    src(ctx, K_)
    ctx.set_line_width(12 * s)
    ctx.stroke()


def _server(ctx, x, y, s):
    for j in range(3):
        rrect(ctx, x - 110 * s, y - 120 * s + j * 82 * s, 220 * s, 70 * s, 12 * s)
        fill_out(ctx, (0.30, 0.32, 0.36), 4, K_)
        ellipse(ctx, x + 75 * s, y - 85 * s + j * 82 * s, 9 * s, 9 * s)
        src(ctx, GREEN)
        ctx.fill()
        for k in range(3):
            rrect(ctx, x - 90 * s, y - 95 * s + j * 82 * s + k * 14 * s, 110 * s, 6 * s, 3 * s)
            src(ctx, GREY)
            ctx.fill()


def _shield(ctx, x, y, s, check=True):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(0, -90)
    ctx.curve_to(40, -70, 70, -70, 80, -70)
    ctx.curve_to(80, 10, 50, 60, 0, 95)
    ctx.curve_to(-50, 60, -80, 10, -80, -70)
    ctx.curve_to(-70, -70, -40, -70, 0, -90)
    ctx.close_path()
    fill_out(ctx, GREEN, 6, K_)
    if check:
        limb(ctx, [(-35, 0), (-8, 28), (40, -30)], 16, WHITE, 0)
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


def _laptop(ctx, x, y, s, t, screen=(0.20, 0.42, 0.62), island=0.0, glow=0.0):
    """Generic cartoon laptop (no logos). y = hinge line."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-230, 0)
    ctx.line_to(230, 0)
    ctx.line_to(200, 30)
    ctx.line_to(-200, 30)
    ctx.close_path()
    fill_out(ctx, (0.75, 0.78, 0.82), 4, K_)
    rrect(ctx, -190, -260, 380, 255, 18)
    fill_out(ctx, (0.18, 0.19, 0.22), 4, K_)
    rrect(ctx, -172, -244, 344, 224, 10)
    src(ctx, screen)
    ctx.fill()
    if glow > 0:
        rrect(ctx, -172, -244, 344, 224, 10)
        src(ctx, WHITE, 0.55 * glow)
        ctx.fill()
    for j in range(3):
        rrect(ctx, -140, -190 + j * 40, 230 - 50 * j, 16, 8)
        src(ctx, WHITE, 0.55)
        ctx.fill()
    if island > 0:
        w = lerp(70, 200, island)
        rrect(ctx, -w / 2, -236, w, 34, 17)
        src(ctx, (0.0, 0.0, 0.0))
        ctx.fill()
        if island > 0.6:
            ellipse(ctx, w / 2 - 22, -219, 8, 8)
            src(ctx, GREEN)
            ctx.fill()
    ctx.restore()


def _finger(ctx, x, y, s):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -16, 0, 32, 90, 16)
    fill_out(ctx, (0.93, 0.72, 0.55), 4, K_)
    rrect(ctx, -34, 70, 68, 90, 26)
    fill_out(ctx, (0.93, 0.72, 0.55), 4, K_)
    ctx.restore()


def _ripple(ctx, x, y, t, col=WHITE):
    ph = (t * 1.6) % 1.0
    ctx.arc(x, y, 12 + 50 * ph, 0, 2 * math.pi)
    src(ctx, col, 1 - ph)
    ctx.set_line_width(6)
    ctx.stroke()


def _tag(ctx, x, y, s, label, sw):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(sw)
    ctx.scale(s, s)
    limb(ctx, [(0, -150), (0, -95)], 5, K_, 0)
    ctx.move_to(-110, -60)
    ctx.line_to(0, -110)
    ctx.line_to(110, -60)
    ctx.line_to(110, 90)
    ctx.line_to(-110, 90)
    ctx.close_path()
    fill_out(ctx, Y_, 6, K_)
    ellipse(ctx, 0, -70, 12, 12)
    src(ctx, K_)
    ctx.fill()
    text(ctx, label, 0, 45, 90, K_)
    ctx.restore()


def _calendar(ctx, x, y, s, top, big):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -120, -110, 240, 230, 22)
    fill_out(ctx, WHITE, 6, K_)
    rrect(ctx, -120, -110, 240, 70, 22)
    src(ctx, RED)
    ctx.fill()
    ctx.rectangle(-120, -60, 240, 20)
    ctx.fill()
    text(ctx, top, 0, -58, 44, WHITE)
    text(ctx, big, 0, 85, 120, K_)
    ctx.restore()


def _bubble(ctx, x, y, w, h, label, fill=WHITE, ink=None, size=34, tail=-1):
    rrect(ctx, x - w / 2, y - h / 2, w, h, 22)
    fill_out(ctx, fill, 4, K_)
    ctx.move_to(x + tail * (w / 2 - 50), y + h / 2 - 2)
    ctx.line_to(x + tail * (w / 2 - 20), y + h / 2 + 28)
    ctx.line_to(x + tail * (w / 2 - 90), y + h / 2 - 2)
    ctx.close_path()
    fill_out(ctx, fill, 4, K_)
    rrect(ctx, x - w / 2 + 4, y + h / 2 - 12, w - 8, 10, 4)
    src(ctx, fill)
    ctx.fill()
    text(ctx, label, x, y + size * 0.36, size, ink or K_)


def _step(ctx, x, y, w, n, label, u, col=Y_):
    if u <= 0.01:
        return
    def _f():
        rrect(ctx, x - w / 2, y - 38, w, 76, 38)
        src(ctx, col)
        ctx.fill()
        ellipse(ctx, x - w / 2 + 38, y, 28, 28)
        src(ctx, K_)
        ctx.fill()
        text(ctx, str(n), x - w / 2 + 38, y + 13, 36, col)
        text(ctx, label, x + 28, y + 13, 36, K_)
    _scaled(ctx, x, y, u, _f)


# ------------------------------------------------------------------ music icons
def _note(ctx, x, y, s, col=None, alpha=1.0):
    col = col or Y_
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.rotate(-0.35)
    ellipse(ctx, 0, 0, 30, 22)
    src(ctx, col, alpha)
    ctx.fill()
    ctx.restore()
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.rectangle(22, -110, 9, 110)
    src(ctx, col, alpha)
    ctx.fill()
    ctx.move_to(31, -110)
    ctx.curve_to(60, -95, 70, -70, 52, -45)
    ctx.set_line_width(9)
    ctx.stroke()
    ctx.restore()


def _toggle(ctx, x, y, s, on):
    """on in 0..1"""
    w, h = 220 * s, 110 * s
    rrect(ctx, x - w / 2, y - h / 2, w, h, h / 2)
    col = tuple(lerp(a, b, on) for a, b in zip(GREY, GREEN))
    fill_out(ctx, col, 5, K_)
    kx = lerp(x - w / 2 + h / 2, x + w / 2 - h / 2, on)
    ellipse(ctx, kx, y, h / 2 - 10 * s, h / 2 - 10 * s)
    fill_out(ctx, WHITE, 4, K_)


def _speaker(ctx, x, y, s, muted=False, t=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-70, -30)
    ctx.line_to(-30, -30)
    ctx.line_to(20, -75)
    ctx.line_to(20, 75)
    ctx.line_to(-30, 30)
    ctx.line_to(-70, 30)
    ctx.close_path()
    fill_out(ctx, WHITE, 6, K_)
    if muted:
        limb(ctx, [(50, -40), (120, 40)], 14, RED, 0)
        limb(ctx, [(120, -40), (50, 40)], 14, RED, 0)
    else:
        for k in range(3):
            a = 0.6 + 0.4 * math.sin(t * 6 - k)
            ctx.arc(20, 0, 45 + 30 * k, -0.7, 0.7)
            src(ctx, Y_, a)
            ctx.set_line_width(10)
            ctx.stroke()
    ctx.restore()


def _dj(ctx, x, y, s, col=TEAL, t=0.0):
    """Generic cartoon DJ bot with headphones (no logos)."""
    _bot(ctx, x, y, s, col)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.arc(0, -30, 62, math.pi * 1.05, math.pi * 1.95)
    src(ctx, K_)
    ctx.set_line_width(10)
    ctx.stroke()
    for dx in (-58, 58):
        rrect(ctx, dx - 14, -46, 28, 44, 10)
        fill_out(ctx, ORANGE, 4, K_)
    ctx.restore()


def _mic(ctx, x, y, s):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    limb(ctx, [(0, 20), (0, 110)], 14, K_, 0)
    rrect(ctx, -60, 105, 120, 18, 9)
    src(ctx, K_)
    ctx.fill()
    ctx.arc(0, -10, 62, 0, math.pi)
    src(ctx, GREY)
    ctx.set_line_width(10)
    ctx.stroke()
    rrect(ctx, -42, -110, 84, 140, 42)
    fill_out(ctx, (0.30, 0.32, 0.36), 5, K_)
    for j in range(4):
        limb(ctx, [(-28, -80 + j * 22), (28, -80 + j * 22)], 4, GREY, 0)
    ctx.restore()


def _wave(ctx, x, y, w, h, t, col=None, flat=False):
    col = col or Y_
    n = 15
    for k in range(n):
        amp = 0.15 if flat else 0.3 + 0.7 * abs(math.sin(t * 5 + k * 0.9))
        bh = h * amp
        bx = x - w / 2 + k * w / n
        rrect(ctx, bx, y - bh / 2, w / n * 0.6, bh, 6)
        src(ctx, col)
        ctx.fill()


# ------------------------------------------------------------------ panel scenes
def _scene(ctx, i, t):
    cx = W / 2
    if i == 0:
        _title(ctx, "TALKS. EVERY. SONG.", PY + 85)
        items = ("note", "BLAH", "note", "BLAH", "note")
        for k, it in enumerate(items):
            x = PX + 110 + k * (PW - 220) / 4
            u = _pop(t, 0.3 + k * 0.45)
            if it == "note":
                _scaled(ctx, x, PY + 280, u, lambda x=x: _note(ctx, x - 15, PY + 330, 1.0))
            else:
                _scaled(ctx, x, PY + 280, u, lambda x=x: _bubble(ctx, x, PY + 270, 170, 80, "BLAH",
                                                                 WHITE, RED, 36, 1))
    elif i == 1:
        _title(ctx, "NEW: LESS CHATTER", PY + 85)
        u = _pop(t, ST[1] + 0.3)
        _scaled(ctx, PX + 210, PY + 300, u, lambda: _calendar(ctx, PX + 210, PY + 300, 0.85, "NOV", "10"))
        u2 = _pop(t, ST[1] + 1.3)
        _scaled(ctx, PX + 610, PY + 210, u2, lambda: _chip(ctx, PX + 610, PY + 210, 400, 70,
                                                          "SPOTIFY AI DJ", Y_, K_, 38))
        on = ease_out(seg(t, ST[1] + 2.6, ST[1] + 3.0))
        _scaled(ctx, PX + 610, PY + 340, u2, lambda: _toggle(ctx, PX + 610, PY + 340, 1.0, on))
    elif i == 2:
        _title(ctx, "DJ ONLY SPEAKS WHEN...", PY + 85)
        d = LINES[2]["dur"]
        _step(ctx, cx, PY + 200, 700, 1, "YOUR SESSION STARTS", _pop(t, ST[2] + d * 0.35))
        _step(ctx, cx, PY + 300, 700, 2, "YOU ASK FOR NEW MUSIC", _pop(t, ST[2] + d * 0.6), GREEN)
        _speaker(ctx, cx, PY + 400, 0.45, muted=t < ST[2] + d * 0.3, t=t)
    elif i == 3:
        _title(ctx, "SAME VOICE AGAIN?", PY + 85)
        _dj(ctx, cx - 180, PY + 330, 1.2, GREY, t)
        _wave(ctx, cx + 170, PY + 290, 300, 120, t, GREY, flat=True)
        text(ctx, "zzz", cx + 170, PY + 410, 60, GREY, alpha=0.6 + 0.4 * math.sin(t * 4))
    elif i == 4:
        _title(ctx, "9 NEW VOICES", PY + 85)
        u = _pop(t, ST[4] + 0.6, 0.45)
        _scaled(ctx, PX + 220, PY + 290, u, lambda: text(ctx, "9", PX + 220, PY + 360, 230, Y_))
        u2 = _pop(t, ST[4] + 2.2)
        _scaled(ctx, PX + 600, PY + 220, u2, lambda: _chip(ctx, PX + 600, PY + 220, 420, 80,
                                                          "7 ENGLISH", Y_, K_, 44))
        u3 = _pop(t, ST[4] + 3.1)
        _scaled(ctx, PX + 600, PY + 340, u3, lambda: _chip(ctx, PX + 600, PY + 340, 420, 80,
                                                          "2 SPANISH", TEAL, WHITE, 44))
    elif i == 5:
        _title(ctx, "5 ENGLISH ACCENTS", PY + 85)
        d = LINES[5]["dur"]
        labs = ("BRITISH", "AMERICAN", "IRISH", "AUSTRALIAN", "INDIAN")
        pos = ((PX + 220, PY + 180), (PX + 600, PY + 180), (PX + 220, PY + 275),
               (PX + 600, PY + 275), (cx, PY + 370))
        for k, lab in enumerate(labs):
            u = _pop(t, ST[5] + 0.3 + k * d * 0.11)
            x, y = pos[k]
            fill = ORANGE if lab == "INDIAN" else Y_
            _scaled(ctx, x, y, u, lambda x=x, y=y, lab=lab, fill=fill:
                    _chip(ctx, x, y, 340, 70, lab, fill, K_, 38))
        u = _pop(t, ST[5] + d * 0.75)
        _scaled(ctx, cx, PY + 440, u, lambda: text(ctx, "EACH WITH ITS OWN PERSONALITY", cx, PY + 452, 30, WHITE))
    elif i == 6:
        _title(ctx, "INDIAN ACCENT!", PY + 85)
        _dj(ctx, cx - 150, PY + 360 - 50 * abs(math.sin((t - ST[6]) * 7)), 1.2, ORANGE, t)
        _wave(ctx, cx + 200, PY + 290, 300, 150, t, Y_)
    elif i == 7:
        _title(ctx, "ORIGINAL VOICE: X", PY + 85)
        u = _pop(t, ST[7] + 0.6)
        def _x():
            ellipse(ctx, PX + 250, PY + 290, 120, 120)
            fill_out(ctx, Y_, 6, K_)
            text(ctx, "X", PX + 250, PY + 340, 150, K_)
        _scaled(ctx, PX + 250, PY + 290, u, _x)
        u2 = _pop(t, ST[7] + 1.8)
        _scaled(ctx, PX + 640, PY + 290, u2, lambda: _chip(ctx, PX + 640, PY + 290, 380, 80,
                                                          "STILL THERE", GREEN, WHITE, 42))
    elif i == 8:
        _title(ctx, "WHO GETS IT?", PY + 85)
        u = _pop(t, ST[8] + 0.6)
        _scaled(ctx, cx, PY + 210, u, lambda: _chip(ctx, cx, PY + 210, 560, 80,
                                                   "PREMIUM LISTENERS", Y_, K_, 42))
        u2 = _pop(t, ST[8] + 1.8)
        _scaled(ctx, cx, PY + 330, u2, lambda: _chip(ctx, cx, PY + 330, 700, 80,
                                                    "MARKETS WITH DJ", TEAL, WHITE, 42))
        u3 = _pop(t, ST[8] + 2.6)
        _scaled(ctx, cx, PY + 420, u3, lambda: text(ctx, "ROLLING OUT NOW", cx, PY + 432, 32, WHITE))
    elif i == 9:
        _title(ctx, "A QUIET DJ?", PY + 85)
        _dj(ctx, cx - 170, PY + 340, 1.1, TEAL, t)
        _speaker(ctx, cx + 150, PY + 290, 0.9, muted=True)
    elif i == 10:
        _title(ctx, "MORE MUSIC. LESS TALK.", PY + 85)
        for k in range(5):
            ph = ((t - ST[10]) * 0.5 + k / 5.0) % 1.0
            _note(ctx, PX + 120 + ph * (PW - 200), PY + 330 + 40 * math.sin(k * 2 + t * 3), 0.9)
        u = _pop(t, ST[10] + 1.0)
        _scaled(ctx, cx, PY + 440, u, lambda: _chip(ctx, cx, PY + 440, 380, 50,
                                                   "CHATTER: OFF", RED, WHITE, 30))
    elif i == 11:
        _title(ctx, "ARJUN ON THE MIC", PY + 85)
        _mic(ctx, cx - 120, PY + 280, 1.2)
        _wave(ctx, cx + 180, PY + 290, 260, 150, t, ORANGE)


def _panel(ctx, t):
    i = _active(t)
    if i is None:
        return
    group = i
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
