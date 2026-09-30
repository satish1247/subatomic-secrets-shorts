"""2026-09-30 newsflash: Starship reaches orbit on Flight 14 (contract: DURATION + render_frame)."""
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
    ("26 SATELLITES", "ONE ROCKET"),
    ("FIRST ORBIT", "STARSHIP · FLIGHT 14 · SEPT 28"),
    ("275 KM UP", "ALL 26 RELEASED"),
    ("1 Tbps", "PER STARLINK V3 · ~10x OLDER VERSION"),
    ("TOO BIG", "FOR FALCON 9 · UP TO 60 PER STARSHIP"),
    ("WHY IT MATTERS", ""),
]
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
    text(ctx, "BREAKING · SPACE TECH", -W / 2 + 90 + (1 - u) * -300, 20, 56, K_, align="left", alpha=u)
    ctx.restore()


# ------------------------------------------------------------------ icons
def _satellite(ctx, x, y, s, ang=0.0, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(s, s)
    for side in (-1, 1):   # solar panels
        rrect(ctx, side * 38 - (70 if side < 0 else 0), -26, 70, 52, 4)
        src(ctx, (0.15, 0.35, 0.75), a)
        ctx.fill_preserve()
        src(ctx, (0.8, 0.85, 0.95), a)
        ctx.set_line_width(3)
        ctx.stroke()
        for k in range(1, 4):
            xx = side * 38 + (k * 17.5 - 70 if side < 0 else k * 17.5)
            ctx.move_to(xx, -26)
            ctx.line_to(xx, 26)
        ctx.stroke()
    rrect(ctx, -34, -30, 68, 60, 10)
    src(ctx, (0.85, 0.87, 0.9), a)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.set_line_width(4)
    ctx.stroke()
    ellipse(ctx, 0, 0, 12, 12)
    src(ctx, Y_, a)
    ctx.fill()
    ctx.restore()


def _rocket(ctx, x, y, s, flame=0.0, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    # flame
    if flame > 0:
        for k, (c, w) in enumerate(((ORANGE, 46), (Y_, 30), ((1, 1, 0.9), 14))):
            ctx.move_to(-w, 250)
            ctx.curve_to(-w * 0.8, 250 + 150 * flame, 0, 250 + (260 - k * 50) * flame, 0, 250 + (260 - k * 50) * flame)
            ctx.curve_to(0, 250 + (260 - k * 50) * flame, w * 0.8, 250 + 150 * flame, w, 250)
            ctx.close_path()
            src(ctx, c, a * 0.95)
            ctx.fill()
    # body (stainless steel)
    g = cairo.LinearGradient(-60, 0, 60, 0)
    g.add_color_stop_rgb(0, 0.55, 0.58, 0.62)
    g.add_color_stop_rgb(0.45, 0.93, 0.95, 0.97)
    g.add_color_stop_rgb(1, 0.50, 0.53, 0.57)
    ctx.move_to(-60, 250)
    ctx.line_to(-60, -150)
    ctx.curve_to(-60, -250, -20, -300, 0, -310)
    ctx.curve_to(20, -300, 60, -250, 60, -150)
    ctx.line_to(60, 250)
    ctx.close_path()
    ctx.set_source(g)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.set_line_width(5)
    ctx.stroke()
    # flaps
    for side in (-1, 1):
        ctx.move_to(side * 60, -190)
        ctx.line_to(side * 95, -150)
        ctx.line_to(side * 60, -120)
        ctx.close_path()
        ctx.move_to(side * 60, 160)
        ctx.line_to(side * 105, 230)
        ctx.line_to(side * 60, 240)
        ctx.close_path()
    src(ctx, (0.35, 0.37, 0.4), a)
    ctx.fill()
    ctx.restore()


def _earth(ctx, x, y, r):
    g = cairo.RadialGradient(x - r * 0.3, y - r * 0.3, r * 0.1, x, y, r)
    g.add_color_stop_rgb(0, 0.30, 0.65, 0.95)
    g.add_color_stop_rgb(1, 0.05, 0.22, 0.50)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    for dx, dy, rx, ry in ((-0.3, -0.2, 0.28, 0.2), (0.25, 0.15, 0.22, 0.3), (-0.1, 0.45, 0.2, 0.1)):
        ellipse(ctx, x + dx * r, y + dy * r, rx * r, ry * r)
        src(ctx, (0.25, 0.62, 0.35), 0.9)
        ctx.fill()
    # atmosphere glow
    g = cairo.RadialGradient(x, y, r, x, y, r * 1.15)
    g.add_color_stop_rgba(0, 0.5, 0.8, 1, 0.5)
    g.add_color_stop_rgba(1, 0.5, 0.8, 1, 0)
    ctx.arc(x, y, r * 1.15, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()


def _icon(ctx, i, t, k):
    t0 = _card_start(i)
    lt = t - t0
    if i == 0:   # rocket rising with a stack of satellites around it
        _rocket(ctx, W / 2, ICON_Y + 60 - 40 * ease_out(seg(lt, 0, 3)), 0.9 * k, flame=0.7 + 0.3 * math.sin(t * 30))
        for j in range(8):
            ang = j / 8 * 2 * math.pi + lt * 0.6
            _satellite(ctx, W / 2 + 330 * math.cos(ang), ICON_Y + 30 + 190 * math.sin(ang), 0.55 * k, ang * 0.3)
    elif i == 1:   # first orbit: ship circling the Earth
        _earth(ctx, W / 2, ICON_Y + 40, 200 * k)
        ctx.arc(W / 2, ICON_Y + 40, 290 * k, 0, 2 * math.pi)
        src(ctx, Y_, 0.6)
        ctx.set_line_width(5)
        ctx.set_dash([18, 14])
        ctx.stroke()
        ctx.set_dash([])
        ang = -math.pi / 2 + ease_io(seg(lt, 0.2, 5.5)) * 2 * math.pi
        ctx.save()
        ctx.translate(W / 2 + 290 * math.cos(ang), ICON_Y + 40 + 290 * math.sin(ang))
        ctx.rotate(ang + math.pi)
        _rocket(ctx, 0, 0, 0.25 * k, flame=0.5)
        ctx.restore()
    elif i == 2:   # satellites spilling out, altitude marker
        _earth(ctx, W / 2, ICON_Y + 900, 700)
        ctx.move_to(170, ICON_Y + 170)
        ctx.line_to(170, ICON_Y - 170)
        src(ctx, Y_, k)
        ctx.set_line_width(6)
        ctx.stroke()
        text(ctx, "275 km", 190, ICON_Y + 15, 48, Y_, align="left", alpha=k)
        n = min(26, int(seg(lt, 0.3, 6.5) * 26) + 1)
        for j in range(n):
            col, row = j % 7, j // 7
            x = 450 + col * 80 + (row % 2) * 40
            y = ICON_Y - 200 + row * 95 + 6 * math.sin(t * 2 + j)
            _satellite(ctx, x, y, 0.42 * k, 0.2 * math.sin(t + j))
        text(ctx, "%d / 26" % n, W / 2 + 120, ICON_Y + 250, 64, (1, 1, 1), alpha=k)
    elif i == 3:   # capacity bars: old vs V3
        v = ease_out(seg(lt, 0.8, 3.5))
        for j, (lab, frac, col) in enumerate((("OLDER", 0.1, (0.6, 0.6, 0.65)), ("V3", 1.0, Y_))):
            y = ICON_Y - 110 + j * 200
            text(ctx, lab, 150, y + 55, 50, (1, 1, 1), align="left", alpha=k)
            rrect(ctx, 360, y, 580, 80, 20)
            src(ctx, (1, 1, 1), 0.12 * k)
            ctx.fill()
            rrect(ctx, 360, y, max(40, 580 * frac * v), 80, 20)
            src(ctx, col, k)
            ctx.fill()
        _satellite(ctx, W / 2, ICON_Y - 270, 0.9 * k, 0.1 * math.sin(t * 1.5))
    elif i == 4:   # size compare: small rocket vs Starship
        _rocket(ctx, 360, ICON_Y + 60, 0.55 * k)
        _rocket(ctx, 720, ICON_Y - 10, 0.95 * k)
        text(ctx, "FALCON 9", 360, ICON_Y + 290, 44, (1, 1, 1), alpha=k)
        text(ctx, "STARSHIP", 720, ICON_Y + 290, 44, Y_, alpha=k)
        # V3 too big: red X over small rocket
        u = ease_back(seg(lt, 1.5, 1.9))
        if u > 0.01:
            ctx.save()
            ctx.translate(360, ICON_Y - 20)
            ctx.scale(u, u)
            for sgn in (-1, 1):
                ctx.move_to(-80, -80 * sgn)
                ctx.line_to(80, 80 * sgn)
            src(ctx, (0.9, 0.15, 0.15))
            ctx.set_line_width(22)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.stroke()
            ctx.restore()
        u2 = ease_out(seg(lt, 3.0, 4.2))
        if u2 > 0.01:
            text(ctx, "UP TO 60", 720, ICON_Y + 365, 60, Y_, alpha=u2)
    elif i == 5:   # why it matters: rocket + check
        _earth(ctx, W / 2, ICON_Y + 900, 700)
        _rocket(ctx, W / 2 - 280, ICON_Y - 20, 0.7 * k, flame=0.8 + 0.2 * math.sin(t * 30))
        for j, s in enumerate(("REAL CARGO", "TO ORBIT")):
            u = ease_back(seg(lt, 0.8 + j * 0.9, 1.2 + j * 0.9))
            if u > 0.01:
                y = ICON_Y - 120 + j * 150
                ellipse(ctx, W / 2 - 60, y - 18, 34 * u, 34 * u)
                src(ctx, TEAL)
                ctx.fill()
                ctx.move_to(W / 2 - 76, y - 18)
                ctx.line_to(W / 2 - 64, y - 4)
                ctx.line_to(W / 2 - 42, y - 34)
                src(ctx, (1, 1, 1), u)
                ctx.set_line_width(7)
                ctx.stroke()
                text(ctx, s, W / 2 - 5, y, 58, (1, 1, 1), align="left", alpha=u)


def _headline(ctx, i, t):
    t0 = _card_start(i)
    k = ease_back(seg(t, t0, t0 + 0.35))
    head, sub = CARDS[i]
    size = 128 if len(head) <= 11 else 104
    ctx.save()
    ctx.translate(W / 2, 560)
    ctx.scale(k, k)
    text(ctx, head, 0, 0, size, Y_)
    ctx.restore()
    if sub:
        text(ctx, sub, W / 2, 650, 38, (1, 1, 1), alpha=ease_out(seg(t, t0 + 0.3, t0 + 0.7)))
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
