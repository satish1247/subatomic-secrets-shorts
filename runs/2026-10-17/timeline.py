"""2026-10-17 mythfact: Meta's Muse Spark Open runs on two Mac Studios (contract: DURATION + render_frame)."""
import json
import math
import os
import cairo
from gfx import W, H, ease_back, ease_out, ease_io, seg, src, text, ellipse, rrect, lerp, wrap, FONT
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
WHITE = (1, 1, 1)
TEAL = (0.14, 0.60, 0.62)
RED = (0.88, 0.20, 0.20)
GREY = (0.55, 0.56, 0.60)
CAP_SIZE = 64
# line index -> scene
HOOK, WHAT, TWO, MYTH1, FACT1, DOWNLOAD, MYTH2, FACT2, CONTEXT, OUTRO = range(10)
TOP = (430, 880)      # myth panel y-range
BOT = (920, 1370)     # fact panel y-range


def _chunks(line):
    """Split a voice line into caption chunks of at most 2 wrapped lines, timed by characters."""
    probe = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 8, 8))
    out, cur = [], []
    for w in line["text"].split():
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
        res.append((t, c))
        t += line["dur"] * len(c) / total
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


def _st(i):
    return 0.0 if i == 0 else LINES[i]["start"] - 0.3


def _end(i):
    return LINES[i]["start"] + LINES[i]["dur"]


# ------------------------------------------------------------------ background
def _background(ctx, t):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.06, 0.06, 0.08)
    g.add_color_stop_rgb(1, 0.01, 0.01, 0.02)
    ctx.set_source(g)
    ctx.paint()
    for i in range(80):
        x = (i * 173.3 + t * (6 + i % 5 * 5)) % W
        y = (i * 311.7) % H
        r = 1.5 + i % 3
        ellipse(ctx, x, y, r, r)
        src(ctx, WHITE, 0.15 + 0.15 * math.sin(t * 2 + i))
        ctx.fill()
    u = ease_out(seg(t, 0.0, 0.5))
    ctx.save()
    ctx.translate(W / 2, 330)
    ctx.rotate(-0.07)
    ctx.rectangle(-W * u, -52, 2 * W * u, 104)
    src(ctx, Y_)
    ctx.fill()
    text(ctx, "MYTH vs FACT · OPEN AI", -W / 2 + 80 + (1 - u) * -300, 20, 52, K_, align="left", alpha=u)
    ctx.restore()


# ------------------------------------------------------------------ props
def _plate(ctx, x, y, label, fg, bg, u, size=56, strike=0.0):
    """Name tag: rounded plate with text; optional red strike-through."""
    if u <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(u, u)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    tw = ctx.text_extents(label).x_advance
    w = tw + 80
    rrect(ctx, -w / 2, -size * 0.95, w, size * 1.6, 22)
    src(ctx, bg)
    ctx.fill()
    text(ctx, label, 0, size * 0.32, size, fg)
    if strike > 0.01:
        ctx.move_to(-w / 2 - 10, 0)
        ctx.line_to(-w / 2 - 10 + (w + 20) * strike, -6)
        src(ctx, RED)
        ctx.set_line_width(14)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
    ctx.restore()


def _xstamp(ctx, x, y, r, u):
    if u <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(-0.12)
    ctx.scale(u, u)
    ellipse(ctx, 0, 0, r * 1.25, r * 1.25)
    src(ctx, RED, 0.9)
    ctx.set_line_width(12)
    ctx.stroke()
    for sgn in (-1, 1):
        ctx.move_to(-r * 0.7, -r * 0.7 * sgn)
        ctx.line_to(r * 0.7, r * 0.7 * sgn)
    ctx.set_line_width(24)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    ctx.restore()


def _check(ctx, x, y, r, u):
    if u <= 0.01:
        return
    ellipse(ctx, x, y, r * u, r * u)
    src(ctx, TEAL)
    ctx.fill()
    ctx.move_to(x - r * 0.45, y)
    ctx.line_to(x - r * 0.1, y + r * 0.38)
    ctx.line_to(x + r * 0.5, y - r * 0.42)
    src(ctx, WHITE, u)
    ctx.set_line_width(r * 0.2)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()


def _panel(ctx, y0, y1, col, label, u, label_col=WHITE):
    if u <= 0.01:
        return
    rrect(ctx, 60, y0, W - 120, y1 - y0, 36)
    src(ctx, col, 0.22 * u)
    ctx.fill_preserve()
    src(ctx, col, 0.9 * u)
    ctx.set_line_width(6)
    ctx.stroke()
    rrect(ctx, 100, y0 - 34, 230, 72, 22)
    src(ctx, col, u)
    ctx.fill()
    text(ctx, label, 215, y0 + 20, 50, label_col, alpha=u)


def _para(ctx, s, x, y, size, col, max_w, a=1.0, lh=1.18):
    for j, ln in enumerate(wrap(ctx, s, size, max_w)):
        text(ctx, ln, x, y + j * size * lh, size, col, alpha=a)




def _rack(ctx, x, y, w, h, t, a=1.0, seed=0):
    """Server rack: dark cabinet with blinking LED rows. (x, y) = top-left."""
    rrect(ctx, x, y, w, h, 14)
    src(ctx, (0.17, 0.18, 0.22), a)
    ctx.fill_preserve()
    src(ctx, (0.45, 0.47, 0.52), a)
    ctx.set_line_width(4)
    ctx.stroke()
    rows = int((h - 30) / 42)
    for r in range(rows):
        ry = y + 18 + r * 42
        rrect(ctx, x + 12, ry, w - 24, 30, 6)
        src(ctx, (0.08, 0.09, 0.11), a)
        ctx.fill()
        for q in range(3):
            on = math.sin(t * (3 + q) + r * 1.7 + seed * 2.3 + q) > 0
            ellipse(ctx, x + w - 34 - q * 20, ry + 15, 5, 5)
            src(ctx, (TEAL if q else Y_) if on else (0.25, 0.26, 0.3), a)
            ctx.fill()


def _mac(ctx, x, y, s, t, a=1.0, glow=0.0):
    """Generic compact desktop box (no brand marks). (x, y) = bottom centre."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ellipse(ctx, 0, 6, 150, 16)
    src(ctx, (0, 0, 0), 0.4 * a)
    ctx.fill()
    if glow > 0.01:
        rrect(ctx, -158, -168, 316, 176, 40)
        src(ctx, Y_, 0.45 * glow * a)
        ctx.set_line_width(10)
        ctx.stroke()
    rrect(ctx, -140, -150, 280, 150, 30)
    g = cairo.LinearGradient(0, -150, 0, 0)
    g.add_color_stop_rgba(0, 0.90, 0.91, 0.93, a)
    g.add_color_stop_rgba(1, 0.66, 0.68, 0.72, a)
    ctx.set_source(g)
    ctx.fill_preserve()
    src(ctx, (0.35, 0.37, 0.42), a)
    ctx.set_line_width(4)
    ctx.stroke()
    rrect(ctx, -140, -150, 280, 26, 13)   # top lid line
    src(ctx, (1, 1, 1), 0.35 * a)
    ctx.fill()
    for q in range(2):   # front ports
        rrect(ctx, -100 + q * 34, -62, 18, 26, 5)
        src(ctx, (0.2, 0.2, 0.24), a)
        ctx.fill()
    ellipse(ctx, 100, -48, 7, 7)   # power light
    src(ctx, Y_, a * (0.6 + 0.4 * math.sin(t * 4)))
    ctx.fill()
    ctx.restore()


def _chip(ctx, x, y, size, label, a=1.0, col=None):
    s = size / 2
    for q in range(4):
        for side in (-1, 1):
            off = -s * 0.6 + q * s * 0.4
            ctx.rectangle(x + off - 6, y + side * (s + 16) - 10, 12, 20)
            ctx.rectangle(x + side * (s + 16) - 10, y + off - 6, 20, 12)
    src(ctx, GREY, a)
    ctx.fill()
    rrect(ctx, x - s, y - s, size, size, size * 0.12)
    src(ctx, col or Y_, a)
    ctx.fill()
    text(ctx, label, x, y + size * 0.13, size * 0.34, K_, alpha=a)


def _cloud(ctx, x, y, s, a=1.0, col=WHITE):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for cx, cy, r in ((-60, 10, 55), (0, -25, 70), (65, 5, 58), (0, 30, 50)):
        ctx.new_sub_path()
        ctx.arc(cx, cy, r, 0, 2 * math.pi)
    src(ctx, col, a)
    ctx.fill()
    ctx.restore()


def _arrow_down(ctx, x, y, s, a=1.0, col=Y_):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-22, -60)
    ctx.line_to(22, -60)
    ctx.line_to(22, 0)
    ctx.line_to(52, 0)
    ctx.line_to(0, 55)
    ctx.line_to(-52, 0)
    ctx.line_to(-22, 0)
    ctx.close_path()
    src(ctx, col, a)
    ctx.fill()
    ctx.restore()


def _building(ctx, x, y, w, h, t, a=1.0):
    """Data-centre hall: wide box with racks visible through a glass front. (x, y) = top-left."""
    rrect(ctx, x, y, w, h, 18)
    src(ctx, (0.12, 0.13, 0.16), a)
    ctx.fill_preserve()
    src(ctx, (0.4, 0.42, 0.48), a)
    ctx.set_line_width(5)
    ctx.stroke()
    rrect(ctx, x + 20, y - 46, w - 40, 56, 12)
    src(ctx, (0.2, 0.21, 0.25), a)
    ctx.fill()
    text(ctx, "DATA CENTER", x + w / 2, y - 6, 38, GREY, alpha=a)
    n = 5
    rw = (w - 60) / n
    for j in range(n):
        _rack(ctx, x + 30 + j * rw + 6, y + 30, rw - 12, h - 60, t, a, seed=j)


def _toy(ctx, x, y, s, t, a=1.0):
    """Tiny wind-up toy robot."""
    ctx.save()
    ctx.translate(x, y + 6 * math.sin(t * 8))
    ctx.scale(s, s)
    rrect(ctx, -50, -120, 100, 80, 18)          # head
    src(ctx, ORANGE, a)
    ctx.fill()
    for ex in (-20, 20):
        ellipse(ctx, ex, -82, 11, 11)
        src(ctx, K_, a)
        ctx.fill()
    ctx.move_to(0, -120)
    ctx.line_to(0, -150)
    src(ctx, GREY, a)
    ctx.set_line_width(6)
    ctx.stroke()
    ellipse(ctx, 0, -156, 10, 10)
    src(ctx, RED, a)
    ctx.fill()
    rrect(ctx, -60, -36, 120, 90, 16)           # body
    src(ctx, TEAL, a)
    ctx.fill()
    ctx.save()                                   # wind-up key
    ctx.translate(72, 10)
    ctx.rotate(t * 6)
    ctx.rectangle(-4, -26, 8, 52)
    src(ctx, Y_, a)
    ctx.fill()
    ctx.restore()
    for lx in (-30, 30):
        rrect(ctx, lx - 14, 54, 28, 34, 8)
        src(ctx, GREY, a)
        ctx.fill()
    ctx.restore()


def _house(ctx, x, y, s, a=1.0):
    """House outline. (x, y) = bottom centre."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-230, 0)
    ctx.line_to(-230, -230)
    ctx.line_to(0, -400)
    ctx.line_to(230, -230)
    ctx.line_to(230, 0)
    ctx.close_path()
    src(ctx, (1, 1, 1), 0.08 * a)
    ctx.fill_preserve()
    src(ctx, Y_, a)
    ctx.set_line_width(14)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke()
    ctx.restore()


ORANGE = (0.96, 0.55, 0.18)


def _headline(ctx, t0, t, head, sub=None, y=560, col=None, size=110):
    kk = ease_back(seg(t, t0, t0 + 0.35))
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    while ctx.text_extents(head).x_advance > W - 160 and size > 60:
        size -= 4
        ctx.set_font_size(size)
    if kk > 0.01:
        ctx.save()
        ctx.translate(W / 2, y)
        ctx.scale(kk, kk)
        text(ctx, head, 0, 0, size, col or Y_)
        ctx.restore()
    if sub:
        text(ctx, sub, W / 2, y + 85, 44, WHITE, alpha=ease_out(seg(t, t0 + 0.3, t0 + 0.7)))


# ------------------------------------------------------------------ scenes
def _intro(ctx, i, t):
    if i == HOOK:
        _headline(ctx, 0.0, t, "GIANT AI", "JUST LEFT THE DATA CENTER")
        k = ease_out(seg(t, 0.1, 0.6))
        _building(ctx, 90, 900, 560, 330, t, k)
        # glowing AI chip walks out of the hall onto a desk
        lt = t - LINES[HOOK]["start"]
        u = ease_io(seg(lt, 0.4, 2.0))
        cx = lerp(370, 850, u)
        cy = lerp(1060, 1120, u) - 30 * abs(math.sin(lt * 7)) * (0 < u < 1)
        ctx.rectangle(700, 1240, 300, 22)        # desk top
        src(ctx, (0.55, 0.40, 0.26), k)
        ctx.fill()
        for lx in (720, 960):
            ctx.rectangle(lx, 1262, 20, 110)
            ctx.fill()
        ellipse(ctx, cx, cy, 110, 110)
        src(ctx, Y_, 0.18 * k)
        ctx.fill()
        _chip(ctx, cx, cy, 120, "AI", k)
    elif i == WHAT:
        t0 = _st(WHAT)
        _headline(ctx, t0, t, "MUSE SPARK OPEN", "NEW OPEN-WEIGHT AI MODEL")
        lt = t - LINES[WHAT]["start"]

        def cal():
            rrect(ctx, -170, -190, 340, 380, 34)
            src(ctx, WHITE)
            ctx.fill()
            rrect(ctx, -170, -190, 340, 105, 34)
            src(ctx, Y_)
            ctx.fill()
            ctx.rectangle(-170, -120, 340, 35)
            ctx.fill()
            text(ctx, "OCT", 0, -118, 50, K_)
            text(ctx, "15", 0, 105, 180, K_)
        u = ease_back(seg(lt, 0.2, 0.55))
        if u > 0.01:
            ctx.save()
            ctx.translate(W / 2, 1010)
            ctx.scale(u, u)
            cal()
            ctx.restore()
        _plate(ctx, 300, 1330, "META", K_, Y_, ease_back(seg(lt, 1.4, 1.8)), 64)
        text(ctx, "+", W / 2, 1352, 90, WHITE, alpha=ease_out(seg(lt, 2.4, 2.7)))
        _plate(ctx, 780, 1330, "APPLE", WHITE, TEAL, ease_back(seg(lt, 2.6, 3.0)), 64)
    else:   # TWO myths teaser
        t0 = _st(TWO)
        _headline(ctx, t0, t, "2 MYTHS", size=130)
        for j in range(2):
            u = ease_back(seg(t, t0 + 0.4 + j * 0.3, t0 + 0.8 + j * 0.3))
            if u > 0.01:
                ctx.save()
                ctx.translate(W / 2 + (j - 0.5) * 420, 1050)
                ctx.rotate((j - 0.5) * 0.12)
                ctx.scale(u, u)
                rrect(ctx, -170, -80, 340, 160, 28)
                src(ctx, RED)
                ctx.fill()
                text(ctx, "MYTH %d" % (j + 1), 0, 22, 66, WHITE)
                ctx.restore()


def _mythfact(ctx, i, t):
    first = i in (MYTH1, FACT1, DOWNLOAD)
    m, f = (MYTH1, FACT1) if first else (MYTH2, FACT2)
    um = ease_out(seg(t, _st(m), _st(m) + 0.4))
    _panel(ctx, TOP[0], TOP[1], RED, "MYTH", um)
    stamp = ease_back(seg(t, _end(m) + 0.05, _end(m) + 0.35))
    dim = um * (1 - 0.45 * stamp)
    claim = ("ONLY RUNS IN A", "HUGE DATA CENTER") if first else ("OPEN MODELS ARE", "SMALL TOYS")
    for j, ln in enumerate(claim):
        text(ctx, ln, W / 2, TOP[0] + 110 + j * 70, 58, WHITE, alpha=dim)
    if first:
        for j in range(6):
            _rack(ctx, 150 + j * 130, TOP[0] + 230, 110, 190, t, dim, seed=j)
    else:
        _toy(ctx, W / 2, TOP[0] + 330, 0.85, t, dim)
    _xstamp(ctx, W - 210, TOP[0] + 300, 85, stamp)
    if i == m:
        return
    uf = ease_out(seg(t, _st(f), _st(f) + 0.4))
    _panel(ctx, BOT[0], BOT[1], TEAL, "FACT", uf)
    _check(ctx, W - 160, BOT[0] + 4, 46, ease_back(seg(t, _st(f) + 0.2, _st(f) + 0.6)))
    if i == FACT1:
        lt = t - LINES[FACT1]["start"]
        for j in range(2):
            u = ease_back(seg(lt, 0.5 + j * 0.5, 0.9 + j * 0.5))
            x = 330 + j * 420
            if u > 0.01:
                _mac(ctx, x, BOT[0] + 300, 1.0 * u, t, 1.0, glow=ease_out(seg(lt, 3.0, 3.5)))
        cable = ease_io(seg(lt, 1.6, 2.2))
        if cable > 0.01:
            ctx.move_to(470, BOT[0] + 240)
            ctx.curve_to(520, BOT[0] + 330, 580, BOT[0] + 330, lerp(470, 610, cable), BOT[0] + 240)
            src(ctx, Y_)
            ctx.set_line_width(8)
            ctx.stroke()
        text(ctx, "2 × MAC STUDIO", W / 2, BOT[0] + 110, 62, Y_, alpha=ease_out(seg(lt, 0.5, 0.9)))
        u = ease_back(seg(lt, 3.0, 3.4))
        if u > 0.01:
            _plate(ctx, W / 2, BOT[0] + 390, "M5 ULTRA CHIP", K_, Y_, u, 50)
    elif i == DOWNLOAD:
        lt = t - LINES[DOWNLOAD]["start"]
        k = ease_out(seg(lt, -0.2, 0.3))
        _cloud(ctx, 260, BOT[0] + 200, 0.95, k)
        text(ctx, "HUGGING FACE", 260, BOT[0] + 360, 42, WHITE, alpha=k)
        drop = (lt * 1.4) % 1.0
        _arrow_down(ctx, 260, BOT[0] + 190 + 40 * drop, 0.8, k * (1 - drop * 0.5))
        text(ctx, "WEIGHTS", 700, BOT[0] + 150, 58, Y_, alpha=k)
        p = ease_io(seg(lt, 0.3, 2.3))
        rrect(ctx, 480, BOT[0] + 200, 440, 50, 25)
        src(ctx, (1, 1, 1), 0.2 * k)
        ctx.fill()
        if p > 0.01:
            rrect(ctx, 480, BOT[0] + 200, 440 * p, 50, 25)
            src(ctx, Y_, k)
            ctx.fill()
        text(ctx, "%d%%" % int(p * 100), 700, BOT[0] + 320, 52, WHITE, alpha=k)
        text(ctx, "FREE DOWNLOAD", 700, BOT[0] + 400, 40, TEAL, alpha=k * ease_out(seg(lt, 1.8, 2.2)))
    elif i == FACT2:
        lt = t - LINES[FACT2]["start"]
        n = int(816 * ease_out(seg(lt, 0.3, 2.0)))
        text(ctx, "%dB" % n, 300, BOT[0] + 190, 120, Y_, alpha=uf)
        text(ctx, "PARAMETERS", 300, BOT[0] + 250, 38, WHITE, alpha=uf)
        # parameter grid: 12 x 8 cells, only a few light up per token
        act = ease_out(seg(lt, 3.0, 3.5))
        cols, rows = 10, 8
        for gx in range(cols):
            for gy in range(rows):
                x, y = 560 + gx * 40, BOT[0] + 80 + gy * 40
                idx = gx * rows + gy
                lit = act > 0.01 and (idx * 37 + int(lt * 3) * 11) % 19 == 0
                rrect(ctx, x, y, 30, 30, 6)
                src(ctx, Y_ if lit else (1, 1, 1), (1.0 if lit else 0.22) * uf)
                ctx.fill()
        u = ease_back(seg(lt, 3.2, 3.6))
        if u > 0.01:
            _plate(ctx, W / 2, BOT[0] + 395, "ONLY ~42B ACTIVE PER TOKEN", K_, Y_, u, 46)
    else:   # CONTEXT: a long scroll unrolls
        lt = t - LINES[CONTEXT]["start"]
        k = ease_out(seg(lt, -0.2, 0.3))
        p = ease_io(seg(lt, 0.2, 1.8))
        x0, x1 = 130, lerp(220, W - 130, p)
        rrect(ctx, x0, BOT[0] + 90, x1 - x0, 170, 16)
        src(ctx, (0.96, 0.93, 0.84), k)
        ctx.fill()
        for r in range(4):
            xx = x0 + 30
            while xx < x1 - 50:
                ww = 40 + (int(xx) * 7 + r * 13) % 50
                rrect(ctx, xx, BOT[0] + 115 + r * 36, min(ww, x1 - 50 - xx), 14, 7)
                src(ctx, (0.45, 0.45, 0.5), k)
                ctx.fill()
                xx += ww + 16
        ellipse(ctx, x1, BOT[0] + 175, 34, 95)
        src(ctx, (0.85, 0.80, 0.68), k)
        ctx.fill()
        n = int(1000000 * ease_out(seg(lt, 0.2, 1.8)))
        text(ctx, "{:,}".format(n), W / 2, BOT[0] + 370, 96, Y_, alpha=k)
        text(ctx, "TOKENS AT ONCE", W / 2, BOT[0] + 425, 40, WHITE, alpha=k)


def _outro(ctx, t):
    t0 = _st(OUTRO)
    lt = t - LINES[OUTRO]["start"]
    _headline(ctx, t0, t, "ONE CATCH")
    k = ease_out(seg(t, t0, t0 + 0.4))
    # license document
    ctx.save()
    ctx.translate(W / 2, 830)
    ctx.rotate(-0.04)
    rrect(ctx, -260, -200, 520, 400, 24)
    src(ctx, WHITE, k)
    ctx.fill()
    text(ctx, "LICENSE", 0, -120, 56, K_, alpha=k)
    for r in range(5):
        rrect(ctx, -200, -70 + r * 44, 400 if r < 4 else 240, 16, 8)
        src(ctx, GREY, k)
        ctx.fill()
    s = ease_back(seg(lt, 1.0, 1.35))
    if s > 0.01:
        ctx.save()
        ctx.translate(30, 120)
        ctx.rotate(-0.12)
        ctx.scale(s, s)
        rrect(ctx, -250, -70, 500, 140, 16)
        src(ctx, WHITE)
        ctx.fill_preserve()
        src(ctx, RED)
        ctx.set_line_width(10)
        ctx.stroke()
        text(ctx, "LIMITED", 0, -8, 50, RED)
        text(ctx, "COMMERCIAL USE", 0, 46, 44, RED)
        ctx.restore()
    ctx.restore()
    u = ease_out(seg(lt, 2.4, 2.9))
    if u > 0.01:
        _house(ctx, W / 2, 1375, 0.58, u)
        _mac(ctx, W / 2, 1360, 0.5, t, u)
        text(ctx, "AI AT HOME?", W / 2, 1120, 58, Y_, alpha=u)


def _wipe(ctx, t):
    """Yellow wipe at scene changes."""
    for i in (MYTH1, MYTH2, OUTRO):
        u = seg(t, _st(i) - 0.2, _st(i) + 0.2)
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
    if i is None and t < END + 0.3:   # keep the outro under the end-card wipe
        _outro(ctx, t)
    if i is not None:
        if i <= TWO:
            _intro(ctx, i, t)
        elif i <= CONTEXT:
            _mythfact(ctx, i, t)
        else:
            _outro(ctx, t)
        line = LINES[i]
        c0, ctext = _caption_text(i, t)
        pk = ease_back(seg(t, c0 - 0.2, c0 + 0.1))
        f = int((t - line["start"]) * 30)
        pulse = 1 + 0.03 * (ENV[i][f] if 0 <= f < len(ENV[i]) else 0)
        brand.caption(ctx, ctext, 1510, CAP_SIZE, pop=pk * pulse)
    _wipe(ctx, t)
    brand.watermark(ctx)
    brand.end_card(ctx, t, DURATION - 1.4)
    surf.flush()
    return surf
