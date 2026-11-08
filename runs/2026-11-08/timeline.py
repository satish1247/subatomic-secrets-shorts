"""2026-11-08 newsflash: Meta's Muse AI agent gets real-time voice chats and expressive avatars (contract: DURATION + render_frame)."""
import json
import math
import os
import cairo
from gfx import W, H, ease_back, ease_out, ease_io, ease_in, clamp, seg, src, text, ellipse, rrect, lerp, wrap
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
    ("TALKING AI", "META'S MUSE GETS A VOICE AND A FACE"),
    ("NOV 5 · US", "ROLLING OUT ON MOBILE · WEB · MAC"),
    ("3 WAYS", "VOICE ONLY · SIDE AVATAR · FULL SCREEN"),
    ("CUT IN", "IT KEEPS WORKING IN THE BACKGROUND"),
    ("IN SYNC", "NEW MODEL: MUSE REALTIME AVATAR"),
    ("META'S TEST", "RATERS PREFERRED IT · PER META"),
    ("WHAT'S NEXT", "AI GLASSES · MUSE CHARM · NO DATE YET"),
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
    text(ctx, "BREAKING · AI TALKS BACK", -W / 2 + 90 + (1 - u) * -300, 20, 56, K_, align="left", alpha=u)
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




# ------------------------------------------------------------------ talking-avatar props (generic, no logos)
SKIN = (0.98, 0.80, 0.42)
PURPLE = (0.45, 0.36, 0.90)


def _mouth_open(t):
    """Lip-sync value 0..1 from the active voice line's envelope."""
    i = _active(t)
    if i is None:
        return 0.0
    f = int((t - LINES[i]["start"]) * 30)
    return clamp(ENV[i][f] * 1.4) if 0 <= f < len(ENV[i]) else 0.0


def _face(ctx, x, y, r, t, a=1.0, talk=None, col=None):
    """Friendly cartoon AI avatar: round head, antenna, blinking eyes, lip-synced mouth."""
    if a <= 0.01:
        return
    m = _mouth_open(t) if talk is None else talk
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(r / 100.0, r / 100.0)
    g = cairo.RadialGradient(0, 0, 60, 0, 0, 170)
    g.add_color_stop_rgba(0, 1, 0.85, 0.2, 0.35 * a)
    g.add_color_stop_rgba(1, 1, 0.85, 0.2, 0)
    ctx.set_source(g)
    ellipse(ctx, 0, 0, 170, 170)
    ctx.fill()
    ctx.move_to(0, -100)
    ctx.line_to(0, -138)
    src(ctx, (1, 1, 1), a)
    ctx.set_line_width(8)
    ctx.stroke()
    ellipse(ctx, 0, -146, 14, 14)
    src(ctx, ORANGE, a)
    ctx.fill()
    ellipse(ctx, 0, 0, 100, 100)
    src(ctx, col or SKIN, a)
    ctx.fill()
    blink = 0.12 if (t % 3.1) < 0.12 else 1.0
    for ex in (-36, 36):
        ellipse(ctx, ex, -18, 13, 17 * blink)
        src(ctx, K_, a)
        ctx.fill()
        ellipse(ctx, ex + 4, -24, 4, 5 * blink)
        src(ctx, (1, 1, 1), a)
        ctx.fill()
    for ex in (-60, 60):
        ellipse(ctx, ex, 18, 14, 9)
        src(ctx, (0.95, 0.55, 0.45), 0.6 * a)
        ctx.fill()
    ellipse(ctx, 0, 38, 30, 6 + 22 * m)
    src(ctx, (0.45, 0.10, 0.12), a)
    ctx.fill()
    ctx.restore()


def _wave(ctx, x, y, w, h, t, a=1.0, col=None, n=13):
    """Voice waveform bars that follow the envelope."""
    m = _mouth_open(t)
    for j in range(n):
        xx = x - w / 2 + w * (j + 0.5) / n
        hh = h * (0.25 + 0.75 * m * (0.5 + 0.5 * math.sin(t * 9 + j * 1.3)))
        rrect(ctx, xx - 9, y - hh / 2, 18, hh, 9)
        src(ctx, col or Y_, a)
        ctx.fill()


def _phone_btn(ctx, x, y, s, a=1.0, ring=0.0):
    """Round phone-call button (generic handset glyph)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    if ring > 0.01:
        ellipse(ctx, 0, 0, 60 + 40 * ring, 60 + 40 * ring)
        src(ctx, GREEN, 0.4 * (1 - ring) * a)
        ctx.fill()
    ellipse(ctx, 0, 0, 60, 60)
    src(ctx, GREEN, a)
    ctx.fill()
    ctx.rotate(-0.6)
    rrect(ctx, -30, -10, 60, 20, 10)
    src(ctx, (1, 1, 1), a)
    ctx.fill()
    rrect(ctx, -34, -22, 18, 34, 8)
    ctx.fill()
    rrect(ctx, 16, -22, 18, 34, 8)
    ctx.fill()
    ctx.restore()


def _chat_lines(ctx, x, y, w, n, a=1.0):
    for j in range(n):
        ww = w * (0.9 if j % 2 == 0 else 0.6)
        xx = x - w / 2 if j % 2 == 0 else x + w / 2 - ww
        rrect(ctx, xx, y + j * 54, ww, 38, 19)
        src(ctx, (0.30, 0.32, 0.38) if j % 2 == 0 else TEAL, a)
        ctx.fill()


def _mode(ctx, x, y, mode, t, u):
    """Mini phone showing one of the three call modes."""
    if u <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(u, u)
    _phone(ctx, 0, 0, 0.62)
    if mode == 0:
        _wave(ctx, 0, -20, 130, 110, t, 1.0, Y_, n=7)
    elif mode == 1:
        _chat_lines(ctx, -10, -130, 120, 4)
        _face(ctx, 0, 110, 38, t)
    else:
        _face(ctx, 0, -10, 72, t)
    ctx.restore()


def _glasses(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    src(ctx, (1, 1, 1), a)
    ctx.set_line_width(14)
    for ex in (-95, 95):
        rrect(ctx, ex - 80, -55, 160, 110, 40)
        ctx.stroke()
    ctx.move_to(-15, -20)
    ctx.curve_to(-5, -40, 5, -40, 15, -20)
    ctx.stroke()
    ctx.move_to(-175, -30)
    ctx.line_to(-215, -45)
    ctx.move_to(175, -30)
    ctx.line_to(215, -45)
    ctx.stroke()
    for ex in (-95, 95):
        rrect(ctx, ex - 72, -47, 144, 94, 34)
        src(ctx, (0.30, 0.55, 0.85), 0.35 * a)
        ctx.fill()
    ctx.restore()


def _charm(ctx, x, y, s, t, a=1.0):
    """Small generic pendant gadget."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-60, -140)
    ctx.line_to(0, -70)
    ctx.line_to(60, -140)
    src(ctx, GREY, a)
    ctx.set_line_width(6)
    ctx.stroke()
    ellipse(ctx, 0, 0, 72, 72)
    src(ctx, (0.85, 0.87, 0.90), a)
    ctx.fill()
    ellipse(ctx, 0, 0, 50, 50)
    src(ctx, K_, a)
    ctx.fill()
    ellipse(ctx, 0, 0, 16 + 4 * math.sin(t * 4), 16 + 4 * math.sin(t * 4))
    src(ctx, Y_, a)
    ctx.fill()
    ctx.restore()


def _icon(ctx, i, t, k):
    t0 = _card_start(i)
    lt = t - t0
    if i == 0:   # phone rings, avatar face pops up and talks
        _phone(ctx, W / 2, ICON_Y + 40, 1.12 * k, k)
        u = ease_back(seg(lt, 0.3, 0.8))
        _face(ctx, W / 2, ICON_Y - 30, 125 * u, t, k)
        _wave(ctx, W / 2, ICON_Y + 200, 230, 70, t, k)
        _pill(ctx, W / 2 - 330, ICON_Y - 200, "VOICE", ease_back(seg(lt, 1.6, 2.0)), col=Y_, size=44, w=230)
        _pill(ctx, W / 2 + 330, ICON_Y - 200, "FACE", ease_back(seg(lt, 2.4, 2.8)), col=TEAL, fg=(1, 1, 1), size=44, w=230)
        _pill(ctx, W / 2 + 330, ICON_Y + 160, "REAL TIME", ease_back(seg(lt, 3.4, 3.8)), col=(1, 1, 1), size=40, w=300)
    elif i == 1:   # calendar + three platforms
        _calendar(ctx, W / 2, ICON_Y - 140, 0.9, "NOV", "5", ease_back(seg(lt, 0.2, 0.6)) * k)
        _pill(ctx, W / 2, ICON_Y + 30, "US ROLLOUT", ease_back(seg(lt, 1.6, 2.0)), col=Y_, size=44, w=380)
        for j, (lab, d) in enumerate((("MOBILE", 3.6), ("WEB", 4.3), ("MAC", 5.0))):
            uu = ease_back(seg(lt, d, d + 0.4))
            xx = W / 2 + (j - 1) * 320
            if uu > 0.01:
                if j == 0:
                    _phone(ctx, xx, ICON_Y + 230, 0.38 * uu)
                elif j == 1:
                    rrect(ctx, xx - 110 * uu, ICON_Y + 150, 220 * uu, 150 * uu, 14)
                    src(ctx, (0.85, 0.87, 0.90))
                    ctx.fill()
                    rrect(ctx, xx - 100 * uu, ICON_Y + 180, 200 * uu, 110 * uu, 8)
                    src(ctx, (0.20, 0.45, 0.70))
                    ctx.fill()
                    for d_ in range(3):
                        ellipse(ctx, xx - 90 * uu + d_ * 18 * uu, ICON_Y + 165, 5 * uu, 5 * uu)
                        src(ctx, (0.4, 0.4, 0.45))
                        ctx.fill()
                else:
                    _laptop(ctx, xx, ICON_Y + 230, 0.62 * uu)
                text(ctx, lab, xx, ICON_Y + 380, 40, (1, 1, 1), alpha=uu)
    elif i == 2:   # tap phone icon -> three modes
        u0 = ease_back(seg(lt, 0.1, 0.5))
        ring = (lt * 1.2) % 1.0 if lt < 1.6 else 0.0
        _phone_btn(ctx, W / 2, ICON_Y - 210, 0.9 * u0, k, ring)
        text(ctx, "PHONE ICON", W / 2 + 190, ICON_Y - 195, 40, (1, 1, 1), align="left", alpha=u0)
        if lt < 1.6:
            _cursor(ctx, W / 2 + 40, ICON_Y - 170 + 20 * math.sin(lt * 6), 0.8, k)
        for j, d in enumerate((1.4, 2.3, 3.4)):
            _mode(ctx, W / 2 + (j - 1) * 330, ICON_Y + 130, j, t, ease_back(seg(lt, d, d + 0.4)))
        for j, (lab, d) in enumerate((("VOICE", 1.6), ("SIDE", 2.5), ("FULL", 3.6))):
            uu = ease_out(seg(lt, d, d + 0.4))
            text(ctx, lab, W / 2 + (j - 1) * 330, ICON_Y + 345, 40, Y_, alpha=uu)
    elif i == 3:   # interrupt: you cut in, gears keep turning
        _face(ctx, W / 2 - 220, ICON_Y - 40, 105, t, k)
        cut = ease_back(seg(lt, 0.9, 1.3))
        if cut > 0.01:
            ctx.save()
            ctx.translate(W / 2 + 190, ICON_Y - 210)
            ctx.scale(cut, cut)
            rrect(ctx, -250, -60, 500, 120, 40)
            src(ctx, (1, 1, 1))
            ctx.fill()
            ctx.move_to(-120, 55)
            ctx.line_to(-170, 100)
            ctx.line_to(-70, 55)
            ctx.fill()
            text(ctx, "WAIT, ONE MORE...", 0, 15, 40, K_)
            ctx.restore()
        ug = ease_out(seg(lt, 2.2, 2.7))
        if ug > 0.01:
            rrect(ctx, W / 2 + 10, ICON_Y + 30, 380, 260, 30)
            src(ctx, (0.16, 0.17, 0.21), ug)
            ctx.fill()
            _gear(ctx, W / 2 + 130, ICON_Y + 140, 48, t, Y_, ug)
            _gear(ctx, W / 2 + 230, ICON_Y + 200, 32, -t * 1.5, TEAL, ug)
            for j in range(3):
                rrect(ctx, W / 2 + 280, ICON_Y + 80 + j * 50, 80 * ((t * 0.5 + j * 0.3) % 1), 24, 12)
                src(ctx, ORANGE, ug)
                ctx.fill()
            text(ctx, "STILL WORKING", W / 2 + 200, ICON_Y + 340, 38, GREY2, alpha=ug)
    elif i == 4:   # same speech tokens -> voice + lips
        u1 = ease_out(seg(lt, 0.3, 1.2))
        rrect(ctx, W / 2 - 340, ICON_Y - 280, 680, 110, 26)
        src(ctx, PURPLE, u1)
        ctx.fill()
        text(ctx, "META SUPERINTELLIGENCE LABS", W / 2, ICON_Y - 213, 34, (1, 1, 1), alpha=u1)
        ut = ease_out(seg(lt, 3.0, 4.2))
        for j in range(7):
            xx = W / 2 - 300 + j * 100
            uu = ease_back(seg(lt, 3.0 + j * 0.12, 3.4 + j * 0.12))
            if uu > 0.01:
                rrect(ctx, xx - 38 * uu, ICON_Y - 110 - 38 * uu, 76 * uu, 76 * uu, 16)
                src(ctx, Y_)
                ctx.fill()
                text(ctx, "%d" % ((j * 37 + 11) % 90 + 10), xx, ICON_Y - 96, 34 * uu, K_)
        text(ctx, "SPEECH TOKENS", W / 2, ICON_Y - 10, 40, GREY2, alpha=ut)
        us = ease_out(seg(lt, 4.8, 5.4))
        if us > 0.01:
            for side in (-1, 1):
                ctx.move_to(W / 2 + side * 80, ICON_Y + 20)
                ctx.line_to(W / 2 + side * 250, ICON_Y + 110)
                src(ctx, (1, 1, 1), us)
                ctx.set_line_width(6)
                ctx.stroke()
            _wave(ctx, W / 2 - 270, ICON_Y + 210, 260, 110, t, us, TEAL, n=7)
            text(ctx, "VOICE", W / 2 - 270, ICON_Y + 340, 40, TEAL, alpha=us)
            _face(ctx, W / 2 + 270, ICON_Y + 210, 85, t, us)
            text(ctx, "LIPS", W / 2 + 270, ICON_Y + 340, 40, Y_, alpha=us)
            _check(ctx, W / 2, ICON_Y + 210, ease_back(seg(lt, 6.2, 6.6)))
    elif i == 5:   # Meta's own rater test (no scores shown: none published in sources)
        labs = ("MUSE", "RUNWAY", "HEYGEN")
        cols = (SKIN, (0.70, 0.72, 0.78), (0.70, 0.72, 0.78))
        for j in range(3):
            xx = W / 2 + (j - 1) * 320
            uu = ease_back(seg(lt, 0.4 + j * 0.35, 0.8 + j * 0.35))
            if uu > 0.01:
                rrect(ctx, xx - 140, ICON_Y - 120, 280, 330, 30)
                src(ctx, (0.16, 0.17, 0.21), uu)
                ctx.fill()
                _face(ctx, xx, ICON_Y + 10, 80 * uu, t, k, talk=(None if j == 0 else 0.15), col=cols[j])
                text(ctx, labs[j], xx, ICON_Y + 180, 40, (1, 1, 1), alpha=uu)
        uc = ease_back(seg(lt, 2.0, 2.4))
        if uc > 0.01:
            _check(ctx, W / 2 - 320 + 110, ICON_Y - 110, uc)
            text(ctx, "PREFERRED", W / 2 - 320, ICON_Y - 170, 40, Y_, alpha=uc)
        st = ease_back(seg(lt, 3.6, 4.0))
        if st > 0.01:
            ctx.save()
            ctx.translate(W / 2, ICON_Y + 320)
            ctx.rotate(-0.06)
            ctx.scale(st, st)
            rrect(ctx, -300, -55, 600, 110, 20)
            src(ctx, ORANGE)
            ctx.set_line_width(8)
            ctx.stroke()
            text(ctx, "META'S OWN TEST", 0, 18, 52, ORANGE)
            ctx.restore()
    elif i == 6:   # glasses + charm, no date
        _glasses(ctx, W / 2 - 200, ICON_Y - 120, 0.95 * ease_back(seg(lt, 0.4, 0.9)), k)
        _charm(ctx, W / 2 + 300, ICON_Y - 90, 1.0 * ease_back(seg(lt, 1.6, 2.1)), t, k)
        text(ctx, "AI GLASSES", W / 2 - 200, ICON_Y + 20, 40, (1, 1, 1), alpha=ease_out(seg(lt, 0.8, 1.2)))
        text(ctx, "MUSE CHARM", W / 2 + 300, ICON_Y + 20, 40, (1, 1, 1), alpha=ease_out(seg(lt, 2.0, 2.4)))
        _pill(ctx, W / 2, ICON_Y + 120, "NO DATE YET", ease_back(seg(lt, 2.6, 3.0)), col=RED, fg=(1, 1, 1), size=42, w=400)
        uq = ease_back(seg(lt, 3.4, 3.9))
        if uq > 0.01:
            _face(ctx, W / 2 - 90, ICON_Y + 290, 70 * uq, t, k)
            text(ctx, "?", W / 2 + 60, ICON_Y + 330, 130 * uq, Y_)


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
