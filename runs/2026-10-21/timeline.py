"""2026-10-21 mythfact: one hacker's AI agents breached sites at 100+ companies (contract: DURATION + render_frame)."""
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
HOOK, WHAT, TWO, MYTH1, FACT1, VICTIMS, MYTH2, FACT2, CAUGHT, OUTRO = range(10)
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
    text(ctx, "MYTH vs FACT · AI HACKING", -W / 2 + 80 + (1 - u) * -300, 20, 52, K_, align="left", alpha=u)
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



ORANGE = (0.96, 0.55, 0.18)


def _agent(ctx, x, y, s, t, a=1.0, col=None, seed=0):
    """Tiny AI agent bot: round head with antenna and two glowing eyes."""
    if a <= 0.01 or s <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y + 5 * math.sin(t * 6 + seed))
    ctx.scale(s, s)
    ctx.move_to(0, -34)
    ctx.line_to(0, -54)
    src(ctx, GREY, a)
    ctx.set_line_width(5)
    ctx.stroke()
    ellipse(ctx, 0, -58, 8, 8)
    src(ctx, col or Y_, a)
    ctx.fill()
    rrect(ctx, -40, -34, 80, 64, 20)
    src(ctx, (0.85, 0.87, 0.9), a)
    ctx.fill()
    rrect(ctx, -30, -22, 60, 34, 12)
    src(ctx, K_, a)
    ctx.fill()
    for ex in (-13, 13):
        ellipse(ctx, ex, -5, 7, 7)
        src(ctx, col or TEAL, a)
        ctx.fill()
    ctx.restore()


def _laptop(ctx, x, y, s, a=1.0, screen=None):
    """Generic laptop. (x, y) = bottom centre."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -170, -250, 340, 220, 18)
    src(ctx, (0.3, 0.32, 0.37), a)
    ctx.fill()
    rrect(ctx, -152, -234, 304, 188, 10)
    src(ctx, screen or (0.05, 0.12, 0.10), a)
    ctx.fill()
    for r in range(5):   # code lines
        w = 80 + (r * 53) % 150
        rrect(ctx, -132, -214 + r * 32, w, 12, 6)
        src(ctx, TEAL if r % 2 else Y_, 0.8 * a)
        ctx.fill()
    ctx.move_to(-200, -30)
    ctx.line_to(200, -30)
    ctx.line_to(230, 0)
    ctx.line_to(-230, 0)
    ctx.close_path()
    src(ctx, (0.55, 0.57, 0.62), a)
    ctx.fill()
    ctx.restore()


def _browser(ctx, x, y, w, h, a=1.0, state=0.0, label=None):
    """Website window. state 0 = normal, 1 = breached (red). (x, y) = top-left."""
    if a <= 0.01:
        return
    rrect(ctx, x, y, w, h, 10)
    src(ctx, (0.92, 0.93, 0.95), a)
    ctx.fill()
    rrect(ctx, x, y, w, h * 0.22, 10)
    src(ctx, (0.62, 0.64, 0.68), a)
    ctx.fill()
    for q in range(3):
        ellipse(ctx, x + 12 + q * 13, y + h * 0.11, 4, 4)
        src(ctx, (RED, Y_, TEAL)[q], a)
        ctx.fill()
    for r in range(2):
        rrect(ctx, x + 10, y + h * (0.38 + r * 0.24), w * (0.7 - r * 0.25), h * 0.1, 4)
        src(ctx, GREY, a)
        ctx.fill()
    if state > 0.01:
        rrect(ctx, x, y, w, h, 10)
        src(ctx, RED, 0.55 * state * a)
        ctx.fill()
        ctx.set_line_width(5)
        rrect(ctx, x, y, w, h, 10)
        src(ctx, RED, state * a)
        ctx.stroke()
    if label:
        text(ctx, label, x + w / 2, y + h + 44, 36, WHITE, alpha=a)


def _person(ctx, x, y, s, a=1.0, col=None):
    """Plain generic silhouette (no likeness). (x, y) = bottom centre."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ellipse(ctx, 0, -150, 34, 34)
    src(ctx, col or WHITE, a)
    ctx.fill()
    ctx.move_to(-55, 0)
    ctx.curve_to(-55, -90, -40, -110, 0, -110)
    ctx.curve_to(40, -110, 55, -90, 55, 0)
    ctx.close_path()
    ctx.fill()
    ctx.restore()


def _bag(ctx, x, y, s, a=1.0):
    """Money bag with a dollar sign. (x, y) = bottom centre."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-30, -150)
    ctx.curve_to(-120, -110, -110, 0, 0, 0)
    ctx.curve_to(110, 0, 120, -110, 30, -150)
    ctx.close_path()
    src(ctx, (0.80, 0.66, 0.36), a)
    ctx.fill()
    rrect(ctx, -34, -172, 68, 26, 10)
    src(ctx, (0.62, 0.48, 0.24), a)
    ctx.fill()
    text(ctx, "$", 0, -28, 100, K_, alpha=a)
    ctx.restore()


def _shield(ctx, x, y, s, a=1.0, col=None):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(0, -120)
    ctx.line_to(95, -85)
    ctx.curve_to(95, 10, 50, 80, 0, 115)
    ctx.curve_to(-50, 80, -95, 10, -95, -85)
    ctx.close_path()
    src(ctx, col or TEAL, a)
    ctx.fill()
    text(ctx, "?", 0, 40, 130, WHITE, alpha=a)
    ctx.restore()


def _magnifier(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(45, 45)
    ctx.line_to(110, 110)
    src(ctx, Y_, a)
    ctx.set_line_width(26)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    ellipse(ctx, 0, 0, 70, 70)
    src(ctx, (1, 1, 1), 0.15 * a)
    ctx.fill_preserve()
    src(ctx, Y_, a)
    ctx.set_line_width(16)
    ctx.stroke()
    ctx.restore()


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
GRID = [(c, r) for r in range(4) for c in range(5)]


def _site_grid(ctx, x0, y0, t, a, hit_from, every=0.18, cw=160, ch=110, gap=24):
    for n, (c, r) in enumerate(GRID):
        x, y = x0 + c * (cw + gap), y0 + r * (ch + gap)
        st = ease_out(seg(t, hit_from + ((n * 7) % 20) * every, hit_from + ((n * 7) % 20) * every + 0.25))
        _browser(ctx, x, y, cw, ch, a, st if n % 3 != 1 else 0.0)


def _intro(ctx, i, t):
    if i == HOOK:
        _headline(ctx, 0.0, t, "ONE HACKER", "A SWARM OF AI AGENTS")
        k = ease_out(seg(t, 0.1, 0.6))
        _laptop(ctx, W / 2, 1390, 0.9, k)
        lt = t - LINES[HOOK]["start"]
        for j in range(7):   # agents fly out of the laptop in a fan
            u = ease_out(seg(lt, 0.4 + j * 0.15, 1.6 + j * 0.15))
            ang = math.pi * (0.15 + 0.7 * j / 6)
            x = W / 2 - math.cos(ang) * 380 * u
            y = 1230 - math.sin(ang) * 420 * u
            _agent(ctx, x, y, 0.95, t, k * min(1, u * 4), seed=j)
        u = ease_back(seg(lt, 2.6, 3.0))
        if u > 0.01:
            _plate(ctx, W / 2, 760, "100+ COMPANIES HIT", WHITE, RED, u, 54)
    elif i == WHAT:
        t0 = _st(WHAT)
        lt = t - LINES[WHAT]["start"]
        n = int(1200 * ease_out(seg(lt, 0.2, 2.6)))
        k = ease_back(seg(t, t0, t0 + 0.35))
        if k > 0.01:
            ctx.save()
            ctx.translate(W / 2, 560)
            ctx.scale(k, k)
            text(ctx, "{:,}+".format(n), 0, 0, 130, Y_)
            ctx.restore()
        text(ctx, "WEBSITES TARGETED", W / 2, 650, 48, WHITE, alpha=ease_out(seg(t, t0 + 0.3, t0 + 0.7)))
        a = ease_out(seg(lt, -0.1, 0.4))
        _site_grid(ctx, 80, 760, lt, a, 0.4, every=0.15)
        for j in range(4):   # agents roaming over the grid
            px = 120 + ((lt * 260 + j * 230) % 840)
            py = 820 + j * 134
            _agent(ctx, px, py, 0.6, t, a, col=RED, seed=j)
        _plate(ctx, W / 2, 1365, "REUTERS EXCLUSIVE", K_, Y_, ease_back(seg(lt, 1.0, 1.4)), 46)
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
    first = i in (MYTH1, FACT1, VICTIMS)
    m, f = (MYTH1, FACT1) if first else (MYTH2, FACT2)
    um = ease_out(seg(t, _st(m), _st(m) + 0.4))
    _panel(ctx, TOP[0], TOP[1], RED, "MYTH", um)
    stamp = ease_back(seg(t, _end(m) + 0.05, _end(m) + 0.35))
    dim = um * (1 - 0.45 * stamp)
    claim = ("NEEDS A WHOLE", "TEAM OF EXPERTS") if first else ("AI HACKING", "COSTS A FORTUNE")
    for j, ln in enumerate(claim):
        text(ctx, ln, W / 2, TOP[0] + 110 + j * 70, 58, WHITE, alpha=dim)
    if first:
        for j in range(5):
            _person(ctx, 230 + j * 130, TOP[0] + 410, 0.95, dim, col=(0.8, 0.82, 0.86))
    else:
        for j in range(3):
            _bag(ctx, 330 + j * 170, TOP[0] + 410, 0.95 - 0.1 * abs(j - 1), dim)
    _xstamp(ctx, W - 210, TOP[0] + 300, 85, stamp)
    if i == m:
        return
    uf = ease_out(seg(t, _st(f), _st(f) + 0.4))
    _panel(ctx, BOT[0], BOT[1], TEAL, "FACT", uf)
    _check(ctx, W - 160, BOT[0] + 4, 46, ease_back(seg(t, _st(f) + 0.2, _st(f) + 0.6)))
    if i == FACT1:
        lt = t - LINES[FACT1]["start"]
        text(ctx, "1 HACKER + AI AGENTS", W / 2, BOT[0] + 110, 62, Y_, alpha=ease_out(seg(lt, 0.2, 0.6)))
        _person(ctx, 250, BOT[0] + 410, 1.0, uf, col=Y_)
        _laptop(ctx, 250, BOT[0] + 420, 0.45, uf)
        for j in range(6):
            u = ease_back(seg(lt, 1.2 + j * 0.25, 1.6 + j * 0.25))
            _agent(ctx, 520 + (j % 3) * 140, BOT[0] + 220 + (j // 3) * 130, 0.8 * u, t, uf, seed=j)
    elif i == VICTIMS:
        lt = t - LINES[VICTIMS]["start"]
        k = ease_out(seg(lt, -0.2, 0.3))
        n = int(100 * ease_out(seg(lt, 0.0, 1.6)))
        text(ctx, "%d+" % n, W / 2, BOT[0] + 150, 110, Y_, alpha=k)
        text(ctx, "COMPANIES' WEBSITES REACHED", W / 2, BOT[0] + 210, 40, WHITE, alpha=k)
        _plate(ctx, 330, BOT[0] + 320, "JOHN DEERE", K_, Y_, ease_back(seg(lt, 2.4, 2.8)), 50)
        _plate(ctx, 760, BOT[0] + 320, "SHARKNINJA", WHITE, RED, ease_back(seg(lt, 3.2, 3.6)), 50)
        text(ctx, "+ MANY MORE", W / 2, BOT[0] + 420, 40, GREY, alpha=ease_out(seg(lt, 3.6, 4.0)))
    elif i == FACT2:
        lt = t - LINES[FACT2]["start"]
        n = int(50 * ease_out(seg(lt, 0.3, 1.8)))
        text(ctx, "~$%d" % n, W / 2, BOT[0] + 190, 140, Y_, alpha=uf)
        text(ctx, "OF AI PER BREAK-IN", W / 2, BOT[0] + 260, 46, WHITE, alpha=uf)
        _agent(ctx, 170, BOT[0] + 190, 0.9, t, uf)
        _browser(ctx, 820, BOT[0] + 130, 160, 110, uf, ease_out(seg(lt, 1.8, 2.2)))
        u = ease_back(seg(lt, 3.6, 4.0))
        if u > 0.01:
            _plate(ctx, W / 2, BOT[0] + 380, "ROUGH ESTIMATE", K_, Y_, u, 50)
    else:   # CAUGHT: exposed control panel under a magnifier
        lt = t - LINES[CAUGHT]["start"]
        k = ease_out(seg(lt, -0.2, 0.3))
        rrect(ctx, 150, BOT[0] + 90, 560, 320, 18)
        src(ctx, (0.1, 0.11, 0.14), k)
        ctx.fill_preserve()
        src(ctx, GREY, k)
        ctx.set_line_width(4)
        ctx.stroke()
        text(ctx, "CONTROL PANEL", 430, BOT[0] + 150, 40, WHITE, alpha=k)
        for r in range(4):
            _agent(ctx, 220, BOT[0] + 225 + r * 56, 0.42, t, k, seed=r)
            rrect(ctx, 270, BOT[0] + 210 + r * 56, 380, 22, 8)
            src(ctx, TEAL if r % 2 else Y_, 0.7 * k)
            ctx.fill()
        u = ease_io(seg(lt, 0.6, 1.6))
        _magnifier(ctx, lerp(980, 820, u), BOT[0] + 220, 0.9, k * min(1, u * 3))
        s = ease_back(seg(lt, 2.0, 2.35))
        if s > 0.01:
            ctx.save()
            ctx.translate(430, BOT[0] + 390)
            ctx.rotate(-0.08)
            ctx.scale(s, s)
            rrect(ctx, -170, -45, 340, 90, 14)
            src(ctx, RED)
            ctx.fill()
            text(ctx, "EXPOSED", 0, 18, 56, WHITE)
            ctx.restore()


def _outro(ctx, t):
    t0 = _st(OUTRO)
    lt = t - LINES[OUTRO]["start"]
    _headline(ctx, t0, t, "DATA TAKEN?")
    text(ctx, "STILL UNCLEAR", W / 2, 650, 48, WHITE, alpha=ease_out(seg(t, t0 + 0.3, t0 + 0.7)))
    k = ease_out(seg(t, t0, t0 + 0.4))
    _browser(ctx, W / 2 - 300, 760, 600, 420, k)
    u = ease_back(seg(lt, 2.2, 2.6))
    if u > 0.01:
        _shield(ctx, W / 2, 990, 1.1 * u, 1.0)
        text(ctx, "IS YOUR SITE READY?", W / 2, 1300, 58, Y_, alpha=ease_out(seg(lt, 2.4, 2.8)))


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
        elif i <= CAUGHT:
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
