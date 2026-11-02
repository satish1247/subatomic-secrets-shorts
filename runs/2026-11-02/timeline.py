"""2026-11-02 newsflash: Apple Intelligence comes to China, with Alibaba's Qwen (contract: DURATION + render_frame)."""
import json
import math
import os
import cairo
from gfx import W, H, ease_back, ease_out, ease_io, seg, src, text, ellipse, rrect, lerp, wrap
import brand
import sfx

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "lines.json"), encoding="utf8") as _f:
    DATA = json.load(_f)
DURATION = DATA["duration"]
LINES = DATA["lines"]
ENV = [sfx.envelope(os.path.join(HERE, k["wav"])) for k in LINES]
END = DURATION - 1.4
Y_ = brand.BRAND_YELLOW
K_ = brand.BRAND_BLACK
TEAL = (0.14, 0.60, 0.62)
ORANGE = (0.96, 0.55, 0.18)
CARDS = [
    ("APPLE AI → CHINA", "FIRST APPLE INTELLIGENCE FEATURES IN CHINA"),
    ("QWEN INSIDE", "APPLE + ALIBABA · ANNOUNCED OCT 31"),
    ("WHERE IT WORKS", "SIRI · WRITING TOOLS · VISUAL INTELLIGENCE"),
    ("NOV 4 → DEC", "DEV BETA FIRST, THEN iOS 27.3"),
    ("YOUR DATA", "PER ALIBABA"),
    ("THE CATCH", "WWDC SIRI UPGRADE NOT INCLUDED"),
    ("WHY IT MATTERS", ""),
]
RED = (0.90, 0.18, 0.18)
GREY = (0.55, 0.56, 0.60)
ICON_Y = 990
CAP_SIZE = 64


def _chunks(line):
    """Split a voice line into caption chunks of at most 2 wrapped lines, timed by characters."""
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
    total = sum(len(c) for c in out)
    t, res = line["start"], []
    for c in out:
        d = line["dur"] * len(c) / total
        res.append((t, c))
        t += d
    return res


CHUNKS = [_chunks(k) for k in LINES]


def _caption_text(i, t):
    cur = CHUNKS[i][0]
    for c in CHUNKS[i]:
        if t >= c[0] - 0.1:
            cur = c
    return cur


def _active(t):
    for i, k in enumerate(LINES):
        nxt = LINES[i + 1]["start"] if i + 1 < len(LINES) else END
        if (k["start"] - 0.3 if i else 0) <= t < nxt - 0.3:
            return i
    return len(LINES) - 1 if t < END else None


def _card_start(i):
    return 0.0 if i == 0 else LINES[i]["start"] - 0.3


# ------------------------------------------------------------------ background
def _background(ctx, t):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.06, 0.06, 0.08)
    g.add_color_stop_rgb(1, 0.01, 0.01, 0.02)
    ctx.set_source(g)
    ctx.paint()
    for i in range(90):
        x = (i * 173.3 + t * (6 + i % 5 * 5)) % W
        y = (i * 311.7) % H
        r = 1.5 + i % 3
        ellipse(ctx, x, y, r, r)
        src(ctx, (1, 1, 1), 0.2 + 0.2 * math.sin(t * 2 + i))
        ctx.fill()
    # diagonal BREAKING band
    u = ease_out(seg(t, 0.0, 0.5))
    ctx.save()
    ctx.translate(W / 2, 330)
    ctx.rotate(-0.07)
    ctx.rectangle(-W * u, -52, 2 * W * u, 104)
    src(ctx, Y_)
    ctx.fill()
    text(ctx, "BREAKING · APPLE AI", -W / 2 + 90 + (1 - u) * -300, 20, 56, K_, align="left", alpha=u)
    ctx.restore()


# ------------------------------------------------------------------ icons
GREY2 = (0.85, 0.87, 0.90)
GREEN = (0.30, 0.90, 0.40)


def _check(ctx, x, y, u):
    if u <= 0.01:
        return
    ellipse(ctx, x, y, 40 * u, 40 * u)
    src(ctx, TEAL)
    ctx.fill()
    ctx.move_to(x - 18, y)
    ctx.line_to(x - 4, y + 15)
    ctx.line_to(x + 20, y - 17)
    src(ctx, (1, 1, 1), u)
    ctx.set_line_width(8)
    ctx.stroke()


def _calendar(ctx, x, y, s, top, big, u):
    if u <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * u, s * u)
    rrect(ctx, -130, -115, 260, 230, 22)
    src(ctx, (1, 1, 1))
    ctx.fill()
    rrect(ctx, -130, -115, 260, 70, 22)
    src(ctx, RED)
    ctx.fill()
    text(ctx, top, 0, -64, 44, (1, 1, 1))
    text(ctx, big, 0, 80, 110 if len(big) <= 2 else 76, K_)
    ctx.restore()


def _pill(ctx, x, y, label, u, col=None, fg=None, size=46, w=None):
    if u <= 0.01:
        return
    col = col or (1, 1, 1)
    fg = fg or K_
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(u, u)
    ww = w or (len(label) * size * 0.62 + 80)
    rrect(ctx, -ww / 2, -45, ww, 90, 45)
    src(ctx, col)
    ctx.fill()
    text(ctx, label, 0, size * 0.36, size, fg)
    ctx.restore()


def _rack(ctx, x, y, s, t, on=1.0, a=1.0):
    """Server rack; on=1 lights blink, on=0 dark."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -110, -190, 220, 380, 18)
    src(ctx, (0.18, 0.19, 0.23), a)
    ctx.fill_preserve()
    src(ctx, (0.55, 0.57, 0.62), a)
    ctx.set_line_width(6)
    ctx.stroke()
    for r in range(5):
        yy = -160 + r * 68
        rrect(ctx, -85, yy, 170, 50, 8)
        src(ctx, (0.10, 0.10, 0.13), a)
        ctx.fill()
        for j in range(3):
            lit = on * (0.5 + 0.5 * math.sin(t * 7 + r * 1.3 + j * 2.1))
            ellipse(ctx, 40 + j * 16, yy + 25, 5, 5)
            src(ctx, GREEN if lit > 0.3 else (0.2, 0.25, 0.2), a)
            ctx.fill()
        rrect(ctx, -70, yy + 18, 70, 14, 4)
        src(ctx, (0.30, 0.31, 0.36), a)
        ctx.fill()
    ctx.restore()


def _bolt(ctx, x, y, s, col=None, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(15, -80)
    ctx.line_to(-45, 10)
    ctx.line_to(-5, 10)
    ctx.line_to(-20, 80)
    ctx.line_to(45, -15)
    ctx.line_to(5, -15)
    ctx.close_path()
    src(ctx, col or Y_, a)
    ctx.fill()
    ctx.restore()


def _plug(ctx, x, y, s, a=1.0):
    """Plug body pointing right, cable to the left."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-400, 0)
    ctx.curve_to(-250, 60, -150, -40, -60, 0)
    src(ctx, (0.35, 0.36, 0.40), a)
    ctx.set_line_width(22)
    ctx.stroke()
    rrect(ctx, -70, -55, 110, 110, 18)
    src(ctx, GREY2, a)
    ctx.fill()
    for dy in (-25, 25):
        rrect(ctx, 40, dy - 9, 50, 18, 5)
        src(ctx, (0.75, 0.62, 0.20), a)
        ctx.fill()
    ctx.restore()


def _socket(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -75, -90, 150, 180, 26)
    src(ctx, (1, 1, 1), a)
    ctx.fill()
    for dy in (-25, 25):
        rrect(ctx, -30, dy - 9, 60, 18, 5)
        src(ctx, K_, a)
        ctx.fill()
    ctx.restore()


def _building(ctx, x, y, s, t, on=1.0, a=1.0):
    """Data-centre building with vents and a roof unit."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -170, -110, 340, 220, 14)
    src(ctx, (0.26, 0.27, 0.32), a)
    ctx.fill_preserve()
    src(ctx, (0.60, 0.62, 0.68), a)
    ctx.set_line_width(5)
    ctx.stroke()
    rrect(ctx, -120, -150, 90, 40, 8)
    rrect(ctx, 30, -150, 90, 40, 8)
    src(ctx, (0.40, 0.42, 0.47), a)
    ctx.fill()
    for j in range(5):
        for r in range(2):
            lit = on * (0.5 + 0.5 * math.sin(t * 5 + j + r * 2))
            rrect(ctx, -140 + j * 58, -70 + r * 70, 46, 40, 6)
            src(ctx, Y_ if lit > 0.35 else (0.15, 0.15, 0.18), a * (0.9 if lit > 0.35 else 1))
            ctx.fill()
    ctx.restore()


def _pin(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(0, 90)
    ctx.curve_to(-30, 40, -70, 0, -70, -40)
    ctx.arc(0, -40, 70, math.pi, 0)
    ctx.curve_to(70, 0, 30, 40, 0, 90)
    src(ctx, RED, a)
    ctx.fill()
    ellipse(ctx, 0, -40, 28, 28)
    src(ctx, (1, 1, 1), a)
    ctx.fill()
    ctx.restore()


def _pylon(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    src(ctx, GREY2, a)
    ctx.set_line_width(9)
    ctx.move_to(-90, 220)
    ctx.line_to(-20, -200)
    ctx.line_to(20, -200)
    ctx.line_to(90, 220)
    for yy, w in ((-140, 130), (-60, 160)):
        ctx.move_to(-w, yy)
        ctx.line_to(w, yy)
    for k in range(4):
        y0 = -200 + k * 105
        y1 = y0 + 105
        x0 = -20 - 70 * (k / 4)
        x1 = -20 - 70 * ((k + 1) / 4)
        ctx.move_to(x0, y0)
        ctx.line_to(-x1, y1)
        ctx.move_to(-x0, y0)
        ctx.line_to(x1, y1)
    ctx.stroke()
    ctx.restore()


def _gauge(ctx, x, y, r, val, vmax, mark=None, a=1.0):
    a0, a1 = math.pi * 0.85, math.pi * 2.15
    ctx.arc(x, y, r, a0, a1)
    src(ctx, (0.25, 0.26, 0.30), a)
    ctx.set_line_width(40)
    ctx.stroke()
    av = a0 + (a1 - a0) * val / vmax
    ctx.arc(x, y, r, a0, av)
    src(ctx, Y_, a)
    ctx.stroke()
    if mark is not None:
        am = a0 + (a1 - a0) * mark / vmax
        ctx.move_to(x + (r - 40) * math.cos(am), y + (r - 40) * math.sin(am))
        ctx.line_to(x + (r + 40) * math.cos(am), y + (r + 40) * math.sin(am))
        src(ctx, TEAL, a)
        ctx.set_line_width(10)
        ctx.stroke()
    ctx.move_to(x, y)
    ctx.line_to(x + (r - 60) * math.cos(av), y + (r - 60) * math.sin(av))
    src(ctx, (1, 1, 1), a)
    ctx.set_line_width(12)
    ctx.stroke()
    ellipse(ctx, x, y, 22, 22)
    ctx.fill()


def _hourglass(ctx, x, y, s, t, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -90, -150, 180, 22, 8)
    rrect(ctx, -90, 128, 180, 22, 8)
    src(ctx, ORANGE, a)
    ctx.fill()
    ctx.move_to(-70, -128)
    ctx.line_to(70, -128)
    ctx.line_to(8, 0)
    ctx.line_to(70, 128)
    ctx.line_to(-70, 128)
    ctx.line_to(-8, 0)
    ctx.close_path()
    src(ctx, (1, 1, 1), 0.25 * a)
    ctx.fill_preserve()
    src(ctx, GREY2, a)
    ctx.set_line_width(6)
    ctx.stroke()
    u = (t * 0.25) % 1
    top = 100 * (1 - u)
    ctx.move_to(-70 * top / 128, -top)
    ctx.line_to(70 * top / 128, -top)
    ctx.line_to(4, -6)
    ctx.line_to(-4, -6)
    ctx.close_path()
    src(ctx, Y_, a)
    ctx.fill()
    bh = 20 + 90 * u
    ctx.move_to(-70, 128)
    ctx.line_to(70, 128)
    ctx.line_to(70 - 62 * bh / 128, 128 - bh)
    ctx.line_to(-70 + 62 * bh / 128, 128 - bh)
    ctx.close_path()
    ctx.fill()
    ctx.move_to(0, 0)
    ctx.line_to(0, 128 - bh)
    ctx.set_line_width(4)
    ctx.stroke()
    ctx.restore()


def _chip(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    src(ctx, GREY2, a)
    ctx.set_line_width(10)
    for k in range(5):
        d = -80 + k * 40
        for (x0, y0, x1, y1) in ((d, -100, d, -135), (d, 100, d, 135), (-100, d, -135, d), (100, d, 135, d)):
            ctx.move_to(x0, y0)
            ctx.line_to(x1, y1)
    ctx.stroke()
    rrect(ctx, -105, -105, 210, 210, 20)
    src(ctx, (0.20, 0.21, 0.25), a)
    ctx.fill()
    rrect(ctx, -60, -60, 120, 120, 12)
    src(ctx, TEAL, a)
    ctx.fill()
    text(ctx, "AI", 0, 20, 56, (1, 1, 1), alpha=a)
    ctx.restore()


def _phone(ctx, x, y, s, a=1.0, on=1.0):
    """Generic smartphone; on=0 dims the screen."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -150, -280, 300, 560, 44)
    src(ctx, (0.80, 0.82, 0.86), a)
    ctx.fill()
    rrect(ctx, -134, -262, 268, 524, 32)
    src(ctx, (0.10, 0.12, 0.16) if on > 0.5 else (0.03, 0.03, 0.04), a)
    ctx.fill()
    rrect(ctx, -40, -250, 80, 16, 8)
    src(ctx, (0.80, 0.82, 0.86), a)
    ctx.fill()
    ctx.restore()


def _notif(ctx, x, y, w, title, body, u, col=None):
    """Notification banner sliding/popping in."""
    if u <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(u, u)
    rrect(ctx, -w / 2, -70, w, 140, 28)
    src(ctx, (1, 1, 1))
    ctx.fill()
    ellipse(ctx, -w / 2 + 62, 0, 34, 34)
    src(ctx, col or Y_)
    ctx.fill()
    _spark(ctx, -w / 2 + 62, 0, 0.32, K_)
    text(ctx, title, -w / 2 + 116, -14, 34, K_, align="left")
    text(ctx, body, -w / 2 + 116, 36, 30, (0.35, 0.36, 0.40), align="left")
    ctx.restore()


def _spark(ctx, x, y, s, col, a=1.0):
    """Four-point sparkle (generic 'AI' glyph)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    pts = []
    for j in range(8):
        r = 80 if j % 2 == 0 else 20
        th = -math.pi / 2 + j * math.pi / 4
        pts.append((r * math.cos(th), r * math.sin(th)))
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.close_path()
    src(ctx, col, a)
    ctx.fill()
    ctx.restore()


def _bell(ctx, x, y, s, t, a=1.0, wig=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(wig * 0.25 * math.sin(t * 28))
    ctx.scale(s, s)
    ctx.move_to(-70, 50)
    ctx.curve_to(-70, -90, 70, -90, 70, 50)
    ctx.line_to(90, 75)
    ctx.line_to(-90, 75)
    ctx.close_path()
    src(ctx, Y_, a)
    ctx.fill()
    ellipse(ctx, 0, 92, 20, 20)
    ctx.fill()
    ellipse(ctx, 0, -82, 12, 12)
    ctx.fill()
    ctx.restore()


def _tile(ctx, x, y, s, kind, a=1.0):
    """Generic app tile: mail, cal, chat, doc."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    cols = {"mail": TEAL, "cal": RED, "chat": ORANGE, "doc": (0.35, 0.45, 0.85)}
    rrect(ctx, -80, -80, 160, 160, 34)
    src(ctx, cols[kind], a)
    ctx.fill()
    src(ctx, (1, 1, 1), a)
    ctx.set_line_width(9)
    if kind == "mail":
        ctx.rectangle(-48, -32, 96, 64)
        ctx.move_to(-48, -32)
        ctx.line_to(0, 8)
        ctx.line_to(48, -32)
        ctx.stroke()
    elif kind == "cal":
        rrect(ctx, -46, -40, 92, 84, 10)
        ctx.stroke()
        ctx.move_to(-46, -14)
        ctx.line_to(46, -14)
        ctx.stroke()
        for j in range(3):
            ellipse(ctx, -24 + j * 24, 14, 7, 7)
            ctx.fill()
    elif kind == "chat":
        rrect(ctx, -50, -40, 100, 64, 18)
        ctx.stroke()
        ctx.move_to(-20, 24)
        ctx.line_to(-34, 46)
        ctx.line_to(4, 24)
        ctx.stroke()
    else:
        rrect(ctx, -38, -48, 76, 96, 8)
        ctx.stroke()
        for j in range(3):
            ctx.move_to(-22, -22 + j * 22)
            ctx.line_to(22, -22 + j * 22)
        ctx.stroke()
    ctx.restore()


def _badge(ctx, x, y, u, label="!", col=None):
    if u <= 0.01:
        return
    ellipse(ctx, x, y, 30 * u, 30 * u)
    src(ctx, col or RED)
    ctx.fill()
    text(ctx, label, x, y + 15 * u, 42 * u, (1, 1, 1))


def _cloud(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for (cx, cy, r) in ((-90, 20, 70), (0, -30, 95), (95, 15, 75)):
        ellipse(ctx, cx, cy, r, r)
    ctx.rectangle(-160, 20, 320, 70)
    src(ctx, (1, 1, 1), a)
    ctx.fill()
    ctx.restore()


def _gear(ctx, x, y, r, t, col, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(t * 2.0)
    for j in range(8):
        ctx.save()
        ctx.rotate(j * math.pi / 4)
        ctx.rectangle(-r * 0.18, -r * 1.25, r * 0.36, r * 0.5)
        ctx.restore()
    ellipse(ctx, 0, 0, r, r)
    src(ctx, col, a)
    ctx.fill()
    ellipse(ctx, 0, 0, r * 0.4, r * 0.4)
    src(ctx, (1, 1, 1), a)
    ctx.fill()
    ctx.restore()


def _laptop(ctx, x, y, s, on=1.0, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -150, -110, 300, 190, 14)
    src(ctx, (0.75, 0.77, 0.82), a)
    ctx.fill()
    rrect(ctx, -136, -96, 272, 162, 8)
    src(ctx, lerp_c((0.03, 0.03, 0.04), (0.20, 0.45, 0.70), on), a)
    ctx.fill()
    ctx.move_to(-185, 80)
    ctx.line_to(185, 80)
    ctx.line_to(160, 105)
    ctx.line_to(-160, 105)
    ctx.close_path()
    src(ctx, (0.62, 0.64, 0.70), a)
    ctx.fill()
    ctx.restore()


def lerp_c(c0, c1, u):
    return tuple(lerp(p, q, u) for p, q in zip(c0, c1))


def _sun(ctx, x, y, r, t, a=1.0):
    for j in range(12):
        th = j * math.pi / 6 + t * 0.3
        ctx.move_to(x + (r + 20) * math.cos(th), y + (r + 20) * math.sin(th))
        ctx.line_to(x + (r + 60) * math.cos(th), y + (r + 60) * math.sin(th))
    src(ctx, ORANGE, a)
    ctx.set_line_width(12)
    ctx.stroke()
    ellipse(ctx, x, y, r, r)
    src(ctx, Y_, a)
    ctx.fill()


def _shield(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(0, -120)
    ctx.line_to(100, -80)
    ctx.curve_to(100, 30, 60, 90, 0, 125)
    ctx.curve_to(-60, 90, -100, 30, -100, -80)
    ctx.close_path()
    src(ctx, TEAL, a)
    ctx.fill()
    ctx.move_to(-40, 0)
    ctx.line_to(-8, 34)
    ctx.line_to(46, -30)
    src(ctx, (1, 1, 1), a)
    ctx.set_line_width(16)
    ctx.stroke()
    ctx.restore()


def _cursor(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(0, 0)
    ctx.line_to(0, 62)
    ctx.line_to(16, 48)
    ctx.line_to(28, 74)
    ctx.line_to(40, 68)
    ctx.line_to(28, 43)
    ctx.line_to(48, 42)
    ctx.close_path()
    src(ctx, (1, 1, 1), a)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.set_line_width(4)
    ctx.stroke()
    ctx.restore()


def _screen_ui(ctx, x, y, s, lt, a=1.0):
    """Laptop with simple windows on screen and an AI cursor clicking buttons."""
    _laptop(ctx, x, y, s, on=1.0, a=a)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -120, -84, 140, 70, 8)
    src(ctx, (1, 1, 1), 0.85 * a)
    ctx.fill()
    rrect(ctx, 30, -84, 90, 140, 8)
    src(ctx, (1, 1, 1), 0.6 * a)
    ctx.fill()
    for j in range(3):
        rrect(ctx, -110, -74 + j * 20, 100 - j * 25, 10, 5)
        src(ctx, (0.55, 0.57, 0.62), a)
        ctx.fill()
    btns = ((-90, 30), (75, -40), (-20, 30), (75, 20))
    for j, (bx, by) in enumerate(btns):
        rrect(ctx, bx - 28, by - 12, 56, 24, 12)
        hit = (lt * 0.8) % 4 > j
        src(ctx, Y_ if hit else TEAL, a)
        ctx.fill()
    ph = (lt * 0.8) % 4
    j = int(ph) % 4
    u = ease_io(ph - int(ph))
    p0, p1 = btns[j - 1], btns[j]
    cx, cy = lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u)
    if u > 0.85:
        ellipse(ctx, p1[0], p1[1], 30 * (u - 0.85) / 0.15 + 10, 30 * (u - 0.85) / 0.15 + 10)
        src(ctx, Y_, 0.5 * a)
        ctx.set_line_width(4)
        ctx.stroke()
    ctx.restore()
    _cursor(ctx, x + cx * s, y + cy * s, 0.9 * s, a)


def _tag(ctx, x, y, s, label, price, col, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-230, -90)
    ctx.line_to(110, -90)
    ctx.line_to(170, 0)
    ctx.line_to(110, 90)
    ctx.line_to(-230, 90)
    ctx.close_path()
    src(ctx, col, a)
    ctx.fill()
    ellipse(ctx, 120, 0, 14, 14)
    src(ctx, K_, a)
    ctx.fill()
    text(ctx, label, -50, -22, 34, K_, alpha=a)
    text(ctx, price, -45, 50, 46, K_, alpha=a)
    ctx.restore()


def _bar(ctx, x, base, w, h, col, a=1.0):
    if h <= 1:
        return
    rrect(ctx, x - w / 2, base - h, w, h, 14)
    src(ctx, col, a)
    ctx.fill()


def _ring(ctx, x, y, r, frac, col, label, val, a=1.0):
    ctx.arc(x, y, r, 0, 2 * math.pi)
    src(ctx, (0.25, 0.26, 0.30), a)
    ctx.set_line_width(34)
    ctx.stroke()
    if frac > 0.002:
        ctx.arc(x, y, r, -math.pi / 2, -math.pi / 2 + 2 * math.pi * frac)
        src(ctx, col, a)
        ctx.stroke()
    text(ctx, val, x, y + 22, 64, (1, 1, 1), alpha=a)
    text(ctx, label, x, y + r + 75, 40, col, alpha=a)


def _orb(ctx, x, y, r, t, a=1.0, label=None):
    """Glowing AI orb with a sparkle (generic assistant glyph, no logos)."""
    g = cairo.RadialGradient(x, y, 0, x, y, r * 1.6)
    g.add_color_stop_rgba(0, 1, 0.9, 0.3, 0.55 * a)
    g.add_color_stop_rgba(1, 1, 0.8, 0.0, 0)
    ctx.set_source(g)
    ellipse(ctx, x, y, r * 1.6, r * 1.6)
    ctx.fill()
    ellipse(ctx, x, y, r * (1 + 0.04 * math.sin(t * 5)), r * (1 + 0.04 * math.sin(t * 5)))
    src(ctx, Y_, a)
    ctx.fill()
    _spark(ctx, x, y, r / 95, K_, a)
    if label:
        text(ctx, label, x, y + r + 60, 44, (1, 1, 1), alpha=a)


def _phone_ai(ctx, x, y, s, t, a=1.0, label=None):
    _phone(ctx, x, y, s, a)
    _orb(ctx, x, y - 40 * s, 90 * s, t, a)
    if label:
        text(ctx, label, x, y + 160 * s, 40 * s, (1, 1, 1), alpha=a)


def _toggle(ctx, x, y, u, a=1.0):
    rrect(ctx, x - 90, y - 48, 180, 96, 48)
    src(ctx, lerp_c(GREY, TEAL, u), a)
    ctx.fill()
    ellipse(ctx, x - 42 + 84 * u, y, 38, 38)
    src(ctx, (1, 1, 1), a)
    ctx.fill()


def _redx(ctx, x, y, r, u):
    if u <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(u, u)
    ctx.move_to(-r, -r)
    ctx.line_to(r, r)
    ctx.move_to(r, -r)
    ctx.line_to(-r, r)
    src(ctx, RED)
    ctx.set_line_width(26)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    ctx.restore()


def _photo(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -80, -80, 160, 160, 34)
    src(ctx, TEAL, a)
    ctx.fill()
    ctx.move_to(-56, 46)
    ctx.line_to(-14, -10)
    ctx.line_to(14, 22)
    ctx.line_to(30, 4)
    ctx.line_to(56, 46)
    ctx.close_path()
    src(ctx, (1, 1, 1), a)
    ctx.fill()
    ellipse(ctx, 30, -34, 14, 14)
    ctx.fill()
    ctx.restore()


def _icon(ctx, i, t, k):
    t0 = _card_start(i)
    lt = t - t0
    if i == 0:   # a phone lights up with an AI orb; CHINA pill
        _phone_ai(ctx, W / 2, ICON_Y + 20, 1.0 * k, t, k)
        _pill(ctx, W / 2, ICON_Y + 330, "COMING TO CHINA", ease_back(seg(lt, 1.2, 1.6)), col=Y_, w=600)
        u = ease_back(seg(lt, 3.0, 3.4))
        if u > 0.01:
            _pill(ctx, W / 2 + 300, ICON_Y - 200, "+ PARTNER AI", u, col=TEAL, fg=(1, 1, 1), size=38, w=340)
    elif i == 1:   # APPLE + ALIBABA -> QWEN in the phone
        u1 = ease_back(seg(lt, 0.9, 1.3))
        u2 = ease_back(seg(lt, 1.7, 2.1))
        _pill(ctx, W / 2 - 240, ICON_Y - 240, "APPLE", u1, col=(1, 1, 1), size=48, w=360)
        text(ctx, "+", W / 2, ICON_Y - 222, 90, Y_, alpha=u2)
        _pill(ctx, W / 2 + 240, ICON_Y - 240, "ALIBABA", u2, col=(1, 1, 1), size=48, w=360)
        u3 = ease_back(seg(lt, 3.2, 3.7))
        if u3 > 0.01:
            _phone_ai(ctx, W / 2, ICON_Y + 120, 0.75 * u3, t, u3)
            _pill(ctx, W / 2 + 300, ICON_Y + 70, "QWEN", ease_back(seg(lt, 3.8, 4.2)), col=Y_, size=52, w=260)
    elif i == 2:   # three places + photos & PDFs
        items = (("SIRI", 0.5), ("WRITING TOOLS", 1.6), ("VISUAL INTELLIGENCE", 2.6))
        for j, (s_, st) in enumerate(items):
            _pill(ctx, W / 2, ICON_Y - 250 + j * 115, s_, ease_back(seg(lt, st, st + 0.4)),
                  col=Y_ if j == 0 else (1, 1, 1), size=44, w=700)
        u = ease_back(seg(lt, 4.6, 5.0))
        if u > 0.01:
            _photo(ctx, W / 2 - 170, ICON_Y + 220, 1.0 * u, 1)
            text(ctx, "PHOTOS", W / 2 - 170, ICON_Y + 345, 36, GREY2, alpha=u)
        u = ease_back(seg(lt, 5.6, 6.0))
        if u > 0.01:
            _tile(ctx, W / 2 + 170, ICON_Y + 220, 1.0 * u, "doc")
            text(ctx, "PDFs", W / 2 + 170, ICON_Y + 345, 36, GREY2, alpha=u)
    elif i == 3:   # calendars
        _calendar(ctx, W / 2 - 220, ICON_Y - 60, 1.1, "NOV", "4", ease_back(seg(lt, 0.4, 0.8)))
        text(ctx, "DEV BETA", W / 2 - 220, ICON_Y + 150, 44, (1, 1, 1), alpha=ease_out(seg(lt, 0.8, 1.2)))
        ua = ease_out(seg(lt, 3.2, 3.8))
        if ua > 0.01:
            ctx.move_to(W / 2 - 70, ICON_Y - 60)
            ctx.line_to(W / 2 - 70 + 140 * ua, ICON_Y - 60)
            src(ctx, Y_)
            ctx.set_line_width(12)
            ctx.stroke()
        _calendar(ctx, W / 2 + 220, ICON_Y - 60, 1.1, "2026", "DEC", ease_back(seg(lt, 3.6, 4.0)))
        text(ctx, "EVERYONE", W / 2 + 220, ICON_Y + 150, 44, (1, 1, 1), alpha=ease_out(seg(lt, 4.0, 4.4)))
        _pill(ctx, W / 2, ICON_Y + 300, "iOS 27.3", ease_back(seg(lt, 5.2, 5.6)), col=Y_, size=52, w=360)
    elif i == 4:   # no training + you switch it on
        _shield(ctx, W / 2 - 220, ICON_Y - 80, 1.25 * k, k)
        text(ctx, "NOT USED", W / 2 - 220, ICON_Y + 130, 40, (1, 1, 1), alpha=k)
        text(ctx, "FOR TRAINING", W / 2 - 220, ICON_Y + 180, 40, (1, 1, 1), alpha=k)
        u = ease_back(seg(lt, 3.0, 3.4))
        if u > 0.01:
            ctx.save()
            ctx.translate(W / 2 + 220, ICON_Y - 80)
            ctx.scale(u * 1.3, u * 1.3)
            _toggle(ctx, 0, 0, ease_io(seg(lt, 4.0, 4.5)))
            ctx.restore()
            text(ctx, "YOU CHOOSE", W / 2 + 220, ICON_Y + 130, 40, (1, 1, 1), alpha=u)
            text(ctx, "TO TURN IT ON", W / 2 + 220, ICON_Y + 180, 40, (1, 1, 1), alpha=u)
    elif i == 5:   # new Siri crossed out
        _phone_ai(ctx, W / 2, ICON_Y + 70, 0.85 * k, t, k)
        _pill(ctx, W / 2, ICON_Y - 215, "NEW, SMARTER SIRI", ease_back(seg(lt, 1.2, 1.6)), col=(1, 1, 1), size=44, w=620)
        _redx(ctx, W / 2, ICON_Y + 70, 150, ease_back(seg(lt, 3.6, 4.0)))
        _pill(ctx, W / 2, ICON_Y + 365, "NOT IN FIRST RELEASE", ease_back(seg(lt, 4.0, 4.4)), col=RED, fg=(1, 1, 1), size=42, w=640)
    elif i == 6:   # why it matters
        _phone_ai(ctx, W / 2 - 230, ICON_Y - 120, 0.75 * k, t, k)
        u = ease_back(seg(lt, 1.2, 1.6))
        _pill(ctx, W / 2 + 200, ICON_Y - 210, "REACHES CHINA", u, col=Y_, size=40, w=440)
        u = ease_back(seg(lt, 3.0, 3.4))
        _pill(ctx, W / 2 + 200, ICON_Y - 80, "PARTNER: QWEN", u, col=(1, 1, 1), size=40, w=440)
        u3 = ease_back(seg(lt, 4.8, 5.2))
        if u3 > 0.01:
            _tile(ctx, W / 2 - 230, ICON_Y + 250, 0.8 * u3, "chat")
            text(ctx, "ELSEWHERE:", W / 2 - 110, ICON_Y + 235, 38, GREY2, align="left", alpha=u3)
            text(ctx, "CHATGPT IN SIRI", W / 2 - 110, ICON_Y + 285, 44, (1, 1, 1), align="left", alpha=u3)


def _xq(ctx, x, y, u):
    ellipse(ctx, x, y, 40 * u, 40 * u)
    src(ctx, ORANGE)
    ctx.fill()
    text(ctx, "!", x, y + 18 * u, 54 * u, (1, 1, 1))


def _headline(ctx, i, t):
    t0 = _card_start(i)
    k = ease_back(seg(t, t0, t0 + 0.35))
    head, sub = CARDS[i]
    size = 128 if len(head) <= 9 else (108 if len(head) <= 11 else 92)
    ctx.save()
    ctx.translate(W / 2, 560)
    ctx.scale(k, k)
    text(ctx, head, 0, 0, size, Y_)
    ctx.restore()
    if sub:
        ss = 38
        while ss > 26 and len(wrap(ctx, sub, ss, W - 120)) > 1:
            ss -= 2
        text(ctx, sub, W / 2, 650, ss, (1, 1, 1), alpha=ease_out(seg(t, t0 + 0.3, t0 + 0.7)))
    return k


def _wipe(ctx, t):
    """Yellow wipe across each card change."""
    for i in range(1, len(LINES)):
        u = seg(t, _card_start(i) - 0.2, _card_start(i) + 0.2)
        if 0 < u < 1:
            x = lerp(-W * 1.3, W * 1.3, ease_io(u))
            ctx.save()
            ctx.translate(x + W / 2, H / 2)
            ctx.rotate(0.25)
            ctx.rectangle(-W * 0.45, -H, W * 0.9, 2 * H)
            src(ctx, Y_)
            ctx.fill()
            ctx.restore()


def render_frame(t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    _background(ctx, t)
    i = _active(t)
    if i is not None:
        k = ease_out(seg(t, _card_start(i), _card_start(i) + 0.4))
        _icon(ctx, i, t, max(k, 0.01))
        _headline(ctx, i, t)
        line = LINES[i]
        c0, ctext = _caption_text(i, t)
        pk = ease_back(seg(t, c0 - 0.2, c0 + 0.1))
        f = int((t - line["start"]) * 30)
        pulse = 1 + 0.03 * (ENV[i][f] if 0 <= f < len(ENV[i]) else 0)
        brand.caption(ctx, ctext, 1500, CAP_SIZE, pop=pk * pulse)
    _wipe(ctx, t)
    brand.watermark(ctx)
    brand.end_card(ctx, t, DURATION - 1.4)
    surf.flush()
    return surf
