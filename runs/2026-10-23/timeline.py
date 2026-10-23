"""2026-10-23 newsflash: Anthropic opens Claude Duet, a proactive AI agent (contract: DURATION + render_frame)."""
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
    ("IT COMES FIRST", "NEW AI AGENT FROM ANTHROPIC · OCT 21"),
    ("CLAUDE DUET", "A PROACTIVE AI AGENT"),
    ("MORNING BRIEF", "YOUR ACTION ITEMS, EACH MORNING"),
    ("KEEPS WORKING", "IN THE CLOUD, EVEN WITH YOUR DEVICES OFF"),
    ("ASKS FIRST", "YOU APPROVE BEFORE IT ACTS"),
    ("WAITLIST", "EARLY RESEARCH PREVIEW"),
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
    text(ctx, "BREAKING · AI AGENTS", -W / 2 + 90 + (1 - u) * -300, 20, 56, K_, align="left", alpha=u)
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


def _icon(ctx, i, t, k):
    t0 = _card_start(i)
    lt = t - t0
    if i == 0:   # phone gets a message from the agent, unprompted
        _phone(ctx, W / 2, ICON_Y + 20, 0.95 * k, k)
        _bell(ctx, W / 2, ICON_Y + 120, 0.9 * k, t, a=k * 0.9, wig=seg(lt, 0.8, 1.0) * (1 - seg(lt, 2.0, 2.4)))
        u = ease_back(seg(lt, 0.8, 1.2))
        _notif(ctx, W / 2, ICON_Y - 120, 640, "AI AGENT", "Here's what needs you today", u)
        _pill(ctx, W / 2, ICON_Y + 330, "BEFORE YOU ASK", ease_back(seg(lt, 2.6, 3.0)), col=Y_, w=600)
    elif i == 1:   # hub-and-spoke: connected apps -> agent
        cx, cy = W / 2, ICON_Y - 20
        kinds = ("mail", "cal", "chat", "doc")
        pos = [(cx - 300, cy - 230), (cx + 300, cy - 230), (cx - 300, cy + 190), (cx + 300, cy + 190)]
        for j, (kind, (x, y)) in enumerate(zip(kinds, pos)):
            u = ease_back(seg(lt, 0.9 + j * 0.2, 1.3 + j * 0.2))
            if u > 0.01:
                ctx.move_to(cx, cy)
                ctx.line_to(x, y)
                src(ctx, GREY, 0.6 * u)
                ctx.set_line_width(6)
                ctx.stroke()
                ph = (t * 0.9 + j * 0.25) % 1
                ellipse(ctx, lerp(x, cx, ph), lerp(y, cy, ph), 10, 10)
                src(ctx, Y_, u)
                ctx.fill()
                _tile(ctx, x, y, 0.9 * u, kind)
        for r, al in ((130, 0.12), (100, 0.25)):
            ellipse(ctx, cx, cy, r * k, r * k)
            src(ctx, Y_, al)
            ctx.fill()
        ellipse(ctx, cx, cy, 80 * k, 80 * k)
        src(ctx, Y_)
        ctx.fill()
        _spark(ctx, cx, cy, 0.7 * k, K_)
        _badge(ctx, pos[0][0] + 70, pos[0][1] - 70, ease_back(seg(lt, 3.0, 3.4)))
        _pill(ctx, W / 2, ICON_Y + 340, "NEEDS YOUR ATTENTION", ease_back(seg(lt, 3.3, 3.7)), col=Y_, w=760)
    elif i == 2:   # morning brief card
        rise = ease_out(seg(lt, 0.0, 1.2))
        _sun(ctx, W / 2 + 250, ICON_Y - 170 + 80 * (1 - rise), 70, t, a=k)
        u = ease_back(seg(lt, 0.3, 0.7))
        if u > 0.01:
            ctx.save()
            ctx.translate(W / 2 - 40, ICON_Y + 60)
            ctx.scale(u, u)
            rrect(ctx, -330, -260, 660, 520, 34)
            src(ctx, (1, 1, 1))
            ctx.fill()
            text(ctx, "TODAY'S BRIEF", -280, -175, 52, K_, align="left")
            for j in range(3):
                uj = ease_out(seg(lt, 1.0 + j * 0.45, 1.4 + j * 0.45))
                y = -70 + j * 120
                rrect(ctx, -280, y - 30, 60, 60, 12)
                src(ctx, (0.85, 0.86, 0.90))
                ctx.fill()
                if uj > 0.01:
                    ctx.move_to(-268, y)
                    ctx.line_to(-252, y + 16)
                    ctx.line_to(-230, y - 16)
                    src(ctx, TEAL, uj)
                    ctx.set_line_width(9)
                    ctx.stroke()
                rrect(ctx, -190, y - 18, (420 - j * 80) * max(uj, 0.05), 36, 18)
                src(ctx, (0.80, 0.81, 0.85))
                ctx.fill()
            ctx.restore()
    elif i == 3:   # tasks continue in the cloud while devices are off
        _tile(ctx, W / 2 - 300, ICON_Y - 210, 0.9 * k, "cal", k)
        _check(ctx, W / 2 - 230, ICON_Y - 280, ease_back(seg(lt, 1.6, 2.0)))
        text(ctx, "SCHEDULE MEETINGS", W / 2 - 200, ICON_Y - 190, 44, (1, 1, 1), align="left", alpha=ease_out(seg(lt, 1.0, 1.4)))
        uc = ease_back(seg(lt, 2.2, 2.6))
        if uc > 0.01:
            _cloud(ctx, W / 2, ICON_Y - 30, 0.95 * uc)
            _gear(ctx, W / 2 - 40, ICON_Y - 20, 46 * uc, t, TEAL)
            _gear(ctx, W / 2 + 50, ICON_Y + 10, 30 * uc, -t, ORANGE)
        dark = ease_io(seg(lt, 4.0, 4.6))
        _laptop(ctx, W / 2 - 200, ICON_Y + 250, 0.7 * k, on=1 - dark, a=k)
        _phone(ctx, W / 2 + 230, ICON_Y + 240, 0.42 * k, k, on=1 - dark)
        u2 = ease_out(seg(lt, 4.5, 4.9))
        if u2 > 0.01:
            text(ctx, "OFF", W / 2 - 200, ICON_Y + 225, 48, GREY, alpha=u2)
            text(ctx, "OFF", W / 2 + 230, ICON_Y + 255, 40, GREY, alpha=u2)
        if uc > 0.01:
            pw = 400 * ((lt * 0.12) % 1)
            rrect(ctx, W / 2 - 200, ICON_Y + 90, 400, 22, 11)
            src(ctx, (0.25, 0.26, 0.30), uc)
            ctx.fill()
            rrect(ctx, W / 2 - 200, ICON_Y + 90, max(pw, 22), 22, 11)
            src(ctx, Y_, uc)
            ctx.fill()
    elif i == 4:   # approval before actions
        _shield(ctx, W / 2, ICON_Y - 210, 0.9 * k, k)
        rows = (("SEND A MESSAGE", 1.6), ("MAKE A PAYMENT", 2.5), ("SIGN A DOCUMENT", 3.3), ("DELETE ANYTHING", 4.1))
        for j, (s_, st) in enumerate(rows):
            u2 = ease_back(seg(lt, st, st + 0.4))
            if u2 > 0.01:
                y = ICON_Y - 50 + j * 95
                _badge(ctx, 250, y - 16, u2, "?", ORANGE)
                text(ctx, s_, 310, y, 50, (1, 1, 1), align="left", alpha=u2)
        _pill(ctx, W / 2, ICON_Y + 330, "YOU SAY YES FIRST", ease_back(seg(lt, 4.6, 5.0)), col=Y_, w=680)
    elif i == 5:   # preview + waitlist + caveat
        _hourglass(ctx, W / 2, ICON_Y - 200, 0.75 * k, t, k)
        items = (("RESEARCH PREVIEW", 0.9, (1, 1, 1)), ("PRO & MAX PLANS", 2.6, (1, 1, 1)), ("US ONLY, FOR NOW", 3.6, (1, 1, 1)))
        for j, (s_, st, c) in enumerate(items):
            _pill(ctx, W / 2, ICON_Y - 10 + j * 110, s_, ease_back(seg(lt, st, st + 0.4)), col=c, size=42, w=640)
        u3 = ease_back(seg(lt, 5.4, 5.8))
        if u3 > 0.01:
            _xq(ctx, 150, ICON_Y + 342, u3)
            text(ctx, "CAN MISJUDGE WHAT'S URGENT", 210, ICON_Y + 360, 46, ORANGE, align="left", alpha=u3)
    elif i == 6:   # ask -> answer  vs  it comes to you
        ua = ease_back(seg(lt, 0.3, 0.7))
        if ua > 0.01:
            _tile(ctx, W / 2 - 260, ICON_Y - 230, 1.0 * ua, "chat")
            text(ctx, "YOU ASK", W / 2 - 260, ICON_Y - 90, 40, GREY2, alpha=ua)
        ar = ease_io(seg(lt, 1.6, 2.2))
        if ar > 0.01:
            ctx.move_to(W / 2 - 130, ICON_Y - 230)
            ctx.line_to(W / 2 - 130 + 220 * ar, ICON_Y - 230)
            src(ctx, Y_)
            ctx.set_line_width(14)
            ctx.stroke()
        ub = ease_back(seg(lt, 2.2, 2.6))
        if ub > 0.01:
            _bell(ctx, W / 2 + 260, ICON_Y - 240, 1.0 * ub, t, wig=1.0)
            text(ctx, "IT COMES TO YOU", W / 2 + 260, ICON_Y - 90, 40, Y_, alpha=ub)
        rivals = (("CLAUDE DUET", 3.0), ("OPENAI · DOTS", 4.6), ("META · MUSE", 5.6))
        for j, (s_, st) in enumerate(rivals):
            _pill(ctx, W / 2, ICON_Y + 50 + j * 110, s_, ease_back(seg(lt, st, st + 0.4)),
                  col=Y_ if j == 0 else (1, 1, 1), size=44, w=600)


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
