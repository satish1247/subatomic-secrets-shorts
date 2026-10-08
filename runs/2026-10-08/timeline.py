"""2026-10-08 newsflash: Surface Laptop Ultra with Nvidia RTX Spark (contract: DURATION + render_frame)."""
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
    ("NVIDIA INSIDE", "THE WHOLE BRAIN OF A WINDOWS LAPTOP"),
    ("$2,599", "SURFACE LAPTOP ULTRA PRE-ORDERS OPEN"),
    ("RTX SPARK", "ONE SUPERCHIP · CPU + GPU"),
    ("128 GB", "SHARED UNIFIED MEMORY"),
    ("ON-DEVICE", "BIG AI MODELS RUN ON THE LAPTOP"),
    ("OCT 16", "RTX SPARK LAPTOPS SHIP"),
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
    text(ctx, "BREAKING · AI HARDWARE", -W / 2 + 90 + (1 - u) * -300, 20, 56, K_, align="left", alpha=u)
    ctx.restore()


# ------------------------------------------------------------------ icons
GREEN = (0.46, 0.73, 0.0)


def _laptop(ctx, x, y, s, a=1.0, screen=None):
    """Generic laptop (no brand marks): screen centred at (x, y)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -300, -200, 600, 380, 26)
    src(ctx, (0.17, 0.17, 0.2), a)
    ctx.fill_preserve()
    src(ctx, (0.72, 0.74, 0.78), a)
    ctx.set_line_width(6)
    ctx.stroke()
    rrect(ctx, -275, -178, 550, 336, 14)
    g = cairo.LinearGradient(0, -178, 0, 158)
    g.add_color_stop_rgb(0, 0.10, 0.18, 0.30)
    g.add_color_stop_rgb(1, 0.03, 0.05, 0.10)
    ctx.set_source(g)
    ctx.fill()
    ctx.move_to(-360, 190)
    ctx.line_to(360, 190)
    ctx.line_to(320, 230)
    ctx.line_to(-320, 230)
    ctx.close_path()
    src(ctx, (0.62, 0.64, 0.68), a)
    ctx.fill()
    rrect(ctx, -60, 190, 120, 12, 6)
    src(ctx, (0.4, 0.42, 0.46), a)
    ctx.fill()
    if screen:
        screen(ctx)
    ctx.restore()


def _chip(ctx, x, y, s, t, a=1.0, label="RTX SPARK"):
    """Generic glowing superchip with pins."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    glow = 0.5 + 0.5 * math.sin(t * 4)
    for r, al in ((210, 0.10), (180, 0.16)):
        rrect(ctx, -r, -r, 2 * r, 2 * r, 40)
        src(ctx, GREEN, al * a * (0.6 + 0.4 * glow))
        ctx.fill()
    for j in range(7):
        for side in range(4):
            ctx.save()
            ctx.rotate(side * math.pi / 2)
            rrect(ctx, -105 + j * 32, -175, 14, 35, 4)
            src(ctx, (0.8, 0.8, 0.82), a)
            ctx.fill()
            ctx.restore()
    rrect(ctx, -140, -140, 280, 280, 22)
    src(ctx, (0.13, 0.14, 0.16), a)
    ctx.fill_preserve()
    src(ctx, GREEN, a)
    ctx.set_line_width(6)
    ctx.stroke()
    rrect(ctx, -100, -100, 200, 200, 14)
    src(ctx, (0.2, 0.22, 0.25), a)
    ctx.fill()
    text(ctx, label, 0, 14, 38, GREEN, alpha=a)
    ctx.restore()


def _cores(ctx, x, y, cols, rows, cell, gap, col, frac, a=1.0):
    n = cols * rows
    lit = int(n * frac)
    w = cols * (cell + gap) - gap
    h = rows * (cell + gap) - gap
    for j in range(n):
        cx = x - w / 2 + (j % cols) * (cell + gap)
        cy = y - h / 2 + (j // cols) * (cell + gap)
        rrect(ctx, cx, cy, cell, cell, max(2, cell * 0.2))
        src(ctx, col if j < lit else (0.25, 0.26, 0.3), a)
        ctx.fill()


def _cloud(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for cx, cy, r in ((-70, 10, 60), (0, -30, 85), (75, 10, 60)):
        ellipse(ctx, cx, cy, r, r)
        src(ctx, (0.85, 0.88, 0.92), a)
        ctx.fill()
    rrect(ctx, -130, 0, 260, 70, 35)
    ctx.fill()
    ctx.restore()


def _net(ctx, x, y, s, t, a=1.0):
    """Tiny neural network diagram (the 'AI model')."""
    layers = (3, 5, 5, 2)
    pts = []
    for li, n in enumerate(layers):
        pts.append([(x + (li - 1.5) * 110 * s, y + (k_ - (n - 1) / 2) * 60 * s) for k_ in range(n)])
    for li in range(len(layers) - 1):
        for p in pts[li]:
            for q in pts[li + 1]:
                ctx.move_to(*p)
                ctx.line_to(*q)
    src(ctx, (1, 1, 1), 0.25 * a)
    ctx.set_line_width(2)
    ctx.stroke()
    for li, col in enumerate(pts):
        for k_, (px, py) in enumerate(col):
            pulse = 0.5 + 0.5 * math.sin(t * 5 - li * 1.2 + k_)
            ellipse(ctx, px, py, 14 * s, 14 * s)
            src(ctx, Y_ if pulse > 0.6 else TEAL, a)
            ctx.fill()


def _xmark(ctx, x, y, r, u, w=22):
    if u <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(u, u)
    for sgn in (-1, 1):
        ctx.move_to(-r, -r * sgn)
        ctx.line_to(r, r * sgn)
    src(ctx, RED)
    ctx.set_line_width(w)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    ctx.restore()


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


def _icon(ctx, i, t, k):
    t0 = _card_start(i)
    lt = t - t0
    if i == 0:   # laptop with a glowing chip "brain"
        _laptop(ctx, W / 2, ICON_Y - 40, 1.1 * k, k,
                lambda c: _chip(c, 0, -10, 0.55 * ease_back(seg(lt, 0.4, 0.9)) + 0.001, t))
        u = ease_out(seg(lt, 1.2, 1.7))
        if u > 0.01:
            text(ctx, "CPU + GPU + AI", W / 2, ICON_Y + 330, 60, Y_, alpha=u)
    elif i == 1:   # laptop + price tag
        _laptop(ctx, W / 2 - 80, ICON_Y - 40, 0.9 * k, k)
        u = ease_back(seg(lt, 0.8, 1.2))
        if u > 0.01:
            ctx.save()
            ctx.translate(W / 2 + 250, ICON_Y - 210)
            ctx.rotate(0.18)
            ctx.scale(u, u)
            ctx.move_to(-150, -70)
            ctx.line_to(120, -70)
            ctx.line_to(170, 0)
            ctx.line_to(120, 70)
            ctx.line_to(-150, 70)
            ctx.close_path()
            src(ctx, Y_)
            ctx.fill()
            ellipse(ctx, 120, 0, 14, 14)
            src(ctx, K_)
            ctx.fill()
            text(ctx, "$2,599", -20, 22, 64, K_)
            ctx.restore()
        u2 = ease_out(seg(lt, 3.0, 3.6))
        if u2 > 0.01:
            text(ctx, "PRE-ORDERS OPEN", W / 2, ICON_Y + 320, 60, (1, 1, 1), alpha=u2)
            text(ctx, "STARTING PRICE", W / 2, ICON_Y + 385, 40, Y_, alpha=u2)
    elif i == 2:   # CPU cores vs GPU cores
        _chip(ctx, W / 2, ICON_Y - 210, 0.55 * k, t, k)
        u = ease_out(seg(lt, 1.6, 2.2))
        if u > 0.01:
            _cores(ctx, W / 2 - 250, ICON_Y + 80, 5, 4, 46, 10, Y_, ease_out(seg(lt, 1.8, 3.6)), u)
            text(ctx, "20", W / 2 - 250, ICON_Y + 265, 84, Y_, alpha=u)
            text(ctx, "ARM CPU CORES", W / 2 - 250, ICON_Y + 320, 34, (1, 1, 1), alpha=u)
        u2 = ease_out(seg(lt, 4.6, 5.2))
        if u2 > 0.01:
            _cores(ctx, W / 2 + 230, ICON_Y + 80, 16, 12, 12, 5, GREEN, ease_out(seg(lt, 4.8, 7.5)), u2)
            text(ctx, "6,144", W / 2 + 230, ICON_Y + 265, 84, GREEN, alpha=u2)
            text(ctx, "GPU CORES", W / 2 + 230, ICON_Y + 320, 34, (1, 1, 1), alpha=u2)
    elif i == 3:   # shared memory pool
        for j, (lab, col, x) in enumerate((("CPU", Y_, W / 2 - 260), ("GPU", GREEN, W / 2 + 260))):
            rrect(ctx, x - 110, ICON_Y - 260, 220, 140, 20)
            src(ctx, col, k)
            ctx.fill()
            text(ctx, lab, x, ICON_Y - 170, 64, K_, alpha=k)
            ctx.move_to(x, ICON_Y - 110)
            ctx.line_to(x + (W / 2 - x) * 0.4, ICON_Y + 20)
            src(ctx, (1, 1, 1), 0.6 * k)
            ctx.set_line_width(8)
            ctx.stroke()
        fill = ease_io(seg(lt, 0.3, 2.6))
        rrect(ctx, 140, ICON_Y + 40, W - 280, 120, 26)
        src(ctx, (1, 1, 1), 0.12 * k)
        ctx.fill()
        rrect(ctx, 140, ICON_Y + 40, max(40, (W - 280) * fill), 120, 26)
        src(ctx, TEAL, k)
        ctx.fill()
        text(ctx, "%d GB" % round(128 * fill), W / 2, ICON_Y + 122, 64, (1, 1, 1), alpha=k)
        text(ctx, "ONE MEMORY POOL", W / 2, ICON_Y + 260, 52, Y_, alpha=ease_out(seg(lt, 1.2, 1.8)))
    elif i == 4:   # AI model on the laptop, cloud crossed out
        _laptop(ctx, W / 2 - 120, ICON_Y + 10, 0.8 * k, k, lambda c: _net(c, 0, -10, 1.0, t))
        _cloud(ctx, W / 2 + 300, ICON_Y - 230, 0.8 * k, k)
        _xmark(ctx, W / 2 + 300, ICON_Y - 230, 80, ease_back(seg(lt, 1.0, 1.4)))
        u = ease_out(seg(lt, 2.0, 2.6))
        if u > 0.01:
            text(ctx, "UP TO 120 BILLION", W / 2, ICON_Y + 300, 60, Y_, alpha=u)
            text(ctx, "PARAMETERS · ON-DEVICE", W / 2, ICON_Y + 365, 44, (1, 1, 1), alpha=u)
    elif i == 5:   # sandboxed agent + partner names + ship date
        u = ease_out(seg(lt, 0.2, 0.7))
        rrect(ctx, W / 2 - 330, ICON_Y - 300, 300, 230, 24)
        src(ctx, TEAL, u)
        ctx.set_line_width(8)
        ctx.set_dash([22, 14])
        ctx.stroke()
        ctx.set_dash([])
        ellipse(ctx, W / 2 - 180, ICON_Y - 200 + 8 * math.sin(t * 3), 50, 50)
        src(ctx, Y_, u)
        ctx.fill()
        for ex in (-18, 18):
            ellipse(ctx, W / 2 - 180 + ex, ICON_Y - 205 + 8 * math.sin(t * 3), 8, 8)
            src(ctx, K_, u)
            ctx.fill()
        text(ctx, "AI AGENT SANDBOX", W / 2 - 180, ICON_Y - 30, 34, TEAL, alpha=u)
        # calendar
        u2 = ease_back(seg(lt, 0.6, 1.0))
        if u2 > 0.01:
            ctx.save()
            ctx.translate(W / 2 + 200, ICON_Y - 185)
            ctx.scale(u2, u2)
            rrect(ctx, -130, -115, 260, 230, 22)
            src(ctx, (1, 1, 1))
            ctx.fill()
            rrect(ctx, -130, -115, 260, 70, 22)
            src(ctx, RED)
            ctx.fill()
            text(ctx, "OCT", 0, -64, 44, (1, 1, 1))
            text(ctx, "16", 0, 80, 110, K_)
            ctx.restore()
        for j, nm in enumerate(("ASUS", "DELL", "HP", "LENOVO", "MSI")):
            u3 = ease_back(seg(lt, 4.5 + j * 0.45, 4.9 + j * 0.45))
            if u3 > 0.01:
                x = W / 2 + (j % 3 - 1) * 300 + (150 if j >= 3 else 0)
                y = ICON_Y + 110 + (j // 3) * 150
                ctx.save()
                ctx.translate(x, y)
                ctx.scale(u3, u3)
                rrect(ctx, -130, -55, 260, 110, 24)
                src(ctx, (1, 1, 1), 0.12)
                ctx.fill()
                text(ctx, nm, 0, 18, 50, (1, 1, 1))
                ctx.restore()
    elif i == 6:   # data center -> desk
        for j in range(3):
            rrect(ctx, W / 2 - 400 + j * 70, ICON_Y - 300, 60, 260, 8)
            src(ctx, (0.35, 0.37, 0.42), k)
            ctx.fill()
            for r in range(6):
                ellipse(ctx, W / 2 - 370 + j * 70, ICON_Y - 270 + r * 40, 7, 7)
                src(ctx, GREEN if (r + j + int(t * 4)) % 3 else Y_, k)
                ctx.fill()
        u = ease_io(seg(lt, 0.6, 1.6))
        ctx.move_to(W / 2 - 150, ICON_Y - 170)
        ctx.line_to(W / 2 - 150 + 240 * u, ICON_Y - 170)
        src(ctx, Y_, k)
        ctx.set_line_width(14)
        ctx.stroke()
        if u > 0.9:
            ctx.move_to(W / 2 + 120, ICON_Y - 170)
            ctx.line_to(W / 2 + 80, ICON_Y - 200)
            ctx.line_to(W / 2 + 80, ICON_Y - 140)
            ctx.close_path()
            ctx.fill()
        _laptop(ctx, W / 2 + 300, ICON_Y - 170, 0.45 * k, k, lambda c: _chip(c, 0, -10, 0.5, t))
        for j, s_ in enumerate(("BIG AI, ON-DEVICE", "RUNS ON THE LAPTOP")):
            u2 = ease_back(seg(lt, 1.2 + j * 1.2, 1.6 + j * 1.2))
            if u2 > 0.01:
                y = ICON_Y + 110 + j * 150
                _check(ctx, W / 2 - 330, y - 18, u2)
                text(ctx, s_, W / 2 - 270, y, 56, (1, 1, 1), align="left", alpha=u2)


def _headline(ctx, i, t):
    t0 = _card_start(i)
    k = ease_back(seg(t, t0, t0 + 0.35))
    head, sub = CARDS[i]
    size = 128 if len(head) <= 11 else 92
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
