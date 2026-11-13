"""2026-11-13 mythfact: 47-million-year-old Messel owl probably hunted by day (contract: DURATION + render_frame)."""
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
HOOK, WHAT, TWO, MYTH1, FACT1, BONES, MYTH2, FACT2, CAVEAT, OUTRO = range(10)
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
    text(ctx, "MYTH vs FACT · FOSSIL OWL", -W / 2 + 80 + (1 - u) * -300, 20, 52, K_, align="left", alpha=u)
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






ORANGE = (0.96, 0.55, 0.18)
BROWN = (0.55, 0.36, 0.22)
DBROWN = (0.36, 0.22, 0.13)
TAN = (0.86, 0.72, 0.52)
STONE = (0.36, 0.34, 0.31)
BONE = (0.93, 0.89, 0.80)
SKY = (0.50, 0.78, 0.95)
NIGHT = (0.10, 0.12, 0.28)


def _sun(ctx, x, y, r, t, a=1.0):
    if a <= 0.01 or r <= 0.5:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(t * 0.6)
    for q in range(10):
        ctx.save()
        ctx.rotate(q * math.pi / 5)
        rrect(ctx, r * 1.2, -r * 0.09, r * 0.45, r * 0.18, r * 0.09)
        src(ctx, Y_, a)
        ctx.fill()
        ctx.restore()
    ctx.restore()
    ellipse(ctx, x, y, r, r)
    src(ctx, Y_, a)
    ctx.fill()


def _moon(ctx, x, y, r, a=1.0):
    if a <= 0.01 or r <= 0.5:
        return
    ctx.save()
    ctx.push_group()
    ellipse(ctx, x, y, r, r)
    src(ctx, (0.95, 0.93, 0.80))
    ctx.fill()
    ctx.set_operator(cairo.OPERATOR_CLEAR)
    ellipse(ctx, x + r * 0.45, y - r * 0.25, r * 0.85, r * 0.85)
    ctx.fill()
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(a)
    ctx.restore()


def _owl(ctx, cx, cy, s, t, a=1.0, fossil=False, glow=0.0, blink=True):
    """Cartoon owl (generic) centred at (cx, cy); s=1 -> ~300 px tall. fossil=True draws a stone-grey outline version."""
    if a <= 0.01 or s <= 0.01:
        return
    body = (0.62, 0.60, 0.56) if fossil else BROWN
    belly = (0.72, 0.70, 0.66) if fossil else TAN
    dark = (0.45, 0.43, 0.40) if fossil else DBROWN
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    # ear tufts
    for sg in (-1, 1):
        ctx.move_to(sg * 60, -95)
        ctx.line_to(sg * 95, -165)
        ctx.line_to(sg * 25, -115)
        ctx.close_path()
        src(ctx, dark, a)
        ctx.fill()
    ellipse(ctx, 0, 0, 115, 150)
    src(ctx, body, a)
    ctx.fill()
    ellipse(ctx, 0, 45, 75, 95)
    src(ctx, belly, a)
    ctx.fill()
    for r in range(3):
        for q in range(3):
            ctx.move_to(-38 + q * 38 - 10, 15 + r * 35)
            ctx.curve_to(-38 + q * 38 - 5, 25 + r * 35, -38 + q * 38 + 5, 25 + r * 35, -38 + q * 38 + 10, 15 + r * 35)
    src(ctx, dark, 0.6 * a)
    ctx.set_line_width(5)
    ctx.stroke()
    # wings
    for sg in (-1, 1):
        ctx.move_to(sg * 95, -40)
        ctx.curve_to(sg * 150, 10, sg * 140, 100, sg * 85, 135)
        ctx.curve_to(sg * 100, 60, sg * 95, 10, sg * 95, -40)
        src(ctx, dark, a)
        ctx.fill()
    # eyes
    bl = 1.0
    if blink:
        ph = (t * 0.45) % 1
        bl = 0.12 if ph < 0.04 else 1.0
    for sg in (-1, 1):
        ellipse(ctx, sg * 45, -70, 44, 44)
        src(ctx, WHITE if not fossil else (0.80, 0.78, 0.74), a)
        ctx.fill()
        ellipse(ctx, sg * 45, -70, 34, 34)
        src(ctx, ORANGE if not fossil else (0.6, 0.58, 0.55), a)
        ctx.fill()
        ellipse(ctx, sg * 45, -70, 18, 18 * bl)
        src(ctx, K_, a)
        ctx.fill()
    ctx.move_to(-14, -45)
    ctx.line_to(14, -45)
    ctx.line_to(0, -15)
    ctx.close_path()
    src(ctx, Y_ if not fossil else (0.55, 0.53, 0.50), a)
    ctx.fill()
    # feet
    for sg in (-1, 1):
        for q in (-1, 0, 1):
            ctx.move_to(sg * 35, 140)
            ctx.line_to(sg * 35 + q * 14, 165)
    src(ctx, ORANGE if not fossil else dark, a)
    ctx.set_line_width(8)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    if glow > 0.01:  # x-ray stomach spot
        g = cairo.RadialGradient(0, 60, 0, 0, 60, 70)
        g.add_color_stop_rgba(0, 0.3, 0.9, 0.8, 0.85 * glow * a)
        g.add_color_stop_rgba(1, 0.3, 0.9, 0.8, 0)
        ctx.set_source(g)
        ellipse(ctx, 0, 60, 70, 70)
        ctx.fill()
        _roach(ctx, 0, 60, 0.32, t, glow * a)
    ctx.restore()


def _roach(ctx, cx, cy, s, t, a=1.0, rot=0.0):
    """Cockroach seen from above with iridescent (blue-green-purple shifting) wings."""
    if a <= 0.01 or s <= 0.01:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(rot)
    ctx.scale(s, s)
    for sg in (-1, 1):  # legs
        for q in (-1, 0, 1):
            ctx.move_to(sg * 40, q * 45)
            ctx.line_to(sg * 110, q * 60 + 25)
            ctx.line_to(sg * 135, q * 70 + 60)
    src(ctx, DBROWN, a)
    ctx.set_line_width(9)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    for sg in (-1, 1):  # antennae
        ctx.move_to(sg * 12, -130)
        ctx.curve_to(sg * 40, -200, sg * 90, -220, sg * 120, -260)
    ctx.set_line_width(6)
    ctx.stroke()
    ellipse(ctx, 0, -115, 38, 30)
    src(ctx, DBROWN, a)
    ctx.fill()
    ellipse(ctx, 0, -80, 62, 34)
    src(ctx, (0.30, 0.20, 0.14), a)
    ctx.fill()
    sh = math.sin(t * 2.2)
    for sg in (-1, 1):
        ctx.save()
        ctx.translate(sg * 26, 30)
        ctx.rotate(sg * 0.08)
        g = cairo.LinearGradient(-60, -110 + 40 * sh, 60, 110 - 40 * sh)
        g.add_color_stop_rgb(0.0, 0.15, 0.75, 0.70)
        g.add_color_stop_rgb(0.45 + 0.15 * sh, 0.20, 0.45, 0.95)
        g.add_color_stop_rgb(1.0, 0.45, 0.85, 0.35)
        ctx.set_source(g)
        ellipse(ctx, 0, 0, 40, 120)
        ctx.save()
        ctx.clip()
        ctx.paint_with_alpha(a)
        ctx.restore()
        # vein lines
        for v in (-18, 0, 18):
            ctx.move_to(v * 0.5, -110)
            ctx.curve_to(v, -40, v, 40, v * 1.2, 110)
        src(ctx, WHITE, 0.35 * a)
        ctx.set_line_width(3)
        ctx.stroke()
        ctx.restore()
    ctx.restore()


def _bone(ctx, x, y, length, thick, a=1.0, col=BONE, rot=0.0):
    """Humerus-like bone: shaft with knobbed ends."""
    if a <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    rrect(ctx, -length / 2, -thick / 2, length, thick, thick / 2)
    src(ctx, col, a)
    ctx.fill()
    for sg in (-1, 1):
        for q in (-1, 1):
            ellipse(ctx, sg * length / 2, q * thick * 0.55, thick * 0.75, thick * 0.75)
            ctx.fill()
    ctx.restore()


def _slab(ctx, cx, cy, w, h, a=1.0):
    """Shale slab (Messel oil shale is dark) with layer lines."""
    rrect(ctx, cx - w / 2, cy - h / 2, w, h, 26)
    src(ctx, STONE, a)
    ctx.fill_preserve()
    src(ctx, (0.22, 0.21, 0.19), a)
    ctx.set_line_width(6)
    ctx.stroke()
    for q in range(5):
        yy = cy - h / 2 + h * (q + 1) / 6
        ctx.move_to(cx - w / 2 + 20, yy)
        for k in range(1, 9):
            ctx.line_to(cx - w / 2 + 20 + (w - 40) * k / 8, yy + math.sin(k * 1.7 + q) * 6)
    src(ctx, (0.28, 0.27, 0.25), a)
    ctx.set_line_width(3)
    ctx.stroke()


# ------------------------------------------------------------------ scenes
def _intro(ctx, i, t):
    if i == HOOK:
        _headline(ctx, 0.0, t, "47 MILLION YEARS OLD", "AND ITS LAST MEAL IS STILL INSIDE", size=100)
        lt = t - LINES[HOOK]["start"]
        k = ease_back(seg(lt, -0.3, 0.3))
        _owl(ctx, W / 2, 1060, 1.35 * k, t, 1.0, glow=ease_out(seg(lt, 1.4, 2.4)))
        u = ease_back(seg(lt, 2.0, 2.4))
        if u > 0.01:
            _plate(ctx, 820, 870, "COCKROACH!", K_, Y_, u, 46)
            ctx.move_to(720, 905)
            ctx.line_to(600, 1080)
            src(ctx, Y_, min(1, u))
            ctx.set_line_width(7)
            ctx.stroke()
        q = ease_back(seg(lt, 3.6, 4.0))
        if q > 0.01:
            ctx.save()
            ctx.translate(250, 860)
            ctx.scale(q, q)
            ellipse(ctx, 0, 0, 70, 70)
            src(ctx, RED)
            ctx.fill()
            text(ctx, "?", 0, 34, 100, WHITE)
            ctx.restore()
    elif i == WHAT:
        t0 = _st(WHAT)
        lt = t - LINES[WHAT]["start"]
        _headline(ctx, t0, t, "MESSEL PIT, GERMANY", "A FAMOUS FOSSIL SITE", size=96)
        k = ease_out(seg(lt, -0.2, 0.4))
        _slab(ctx, W / 2, 950, 760, 440, k)
        _owl(ctx, W / 2, 960, 0.95 * k, t, k * ease_out(seg(lt, 0.3, 1.0)), fossil=True, blink=False)
        u = ease_back(seg(lt, 1.9, 2.3))
        if u > 0.01:
            _plate(ctx, W / 2, 1250, "MASILLASTRIX BLATTOPHAGA", K_, Y_, u, 48)
        u2 = ease_back(seg(lt, 4.0, 4.4))
        if u2 > 0.01:
            _plate(ctx, W / 2, 1350, "= \"THE COCKROACH EATER\"", WHITE, TEAL, u2, 44)
    else:
        t0 = _st(TWO)
        _headline(ctx, t0, t, "2 OWL MYTHS", size=120)
        for j in range(2):
            u = ease_back(seg(t, t0 + 0.3 + j * 0.25, t0 + 0.7 + j * 0.25))
            if u > 0.01:
                ctx.save()
                ctx.translate(W / 2 + (j - 0.5) * 420, 1000)
                ctx.rotate((j - 0.5) * 0.12)
                ctx.scale(u, u)
                rrect(ctx, -170, -80, 340, 160, 28)
                src(ctx, RED)
                ctx.fill()
                text(ctx, "MYTH %d" % (j + 1), 0, 22, 66, WHITE)
                ctx.restore()


def _mythfact(ctx, i, t):
    first = i in (MYTH1, FACT1, BONES)
    m, f = (MYTH1, FACT1) if first else (MYTH2, FACT2)
    um = ease_out(seg(t, _st(m), _st(m) + 0.4))
    _panel(ctx, TOP[0], TOP[1], RED, "MYTH", um)
    stamp = ease_back(seg(t, _end(m) + 0.05, _end(m) + 0.35))
    dim = um * (1 - 0.45 * stamp)
    claim = ("OWLS HAVE ALWAYS", "HUNTED AT NIGHT") if first else ("NIGHT HUNTERS", "FROM THE START")
    for j, ln in enumerate(claim):
        text(ctx, ln, W / 2, TOP[0] + 110 + j * 70, 58, WHITE, alpha=dim)
    # night sky mini-scene
    rrect(ctx, 200, TOP[0] + 220, 520, 190, 24)
    src(ctx, NIGHT, dim)
    ctx.fill()
    for q in range(9):
        ellipse(ctx, 230 + q * 55, TOP[0] + 245 + (q * 37) % 60, 3, 3)
        src(ctx, WHITE, dim * (0.5 + 0.5 * math.sin(t * 3 + q)))
        ctx.fill()
    _moon(ctx, 640, TOP[0] + 280, 40, dim)
    _owl(ctx, 400, TOP[0] + 320, 0.5 * um, t, dim)
    if not first:
        text(ctx, "ALWAYS", 560, TOP[0] + 385, 40, Y_, alpha=dim)
    _xstamp(ctx, W - 190, TOP[0] + 300, 80, stamp)
    if i == m:
        return
    uf = ease_out(seg(t, _st(f), _st(f) + 0.4))
    _panel(ctx, BOT[0], BOT[1], TEAL, "FACT", uf)
    _check(ctx, W - 160, BOT[0] + 4, 46, ease_back(seg(t, _st(f) + 0.2, _st(f) + 0.6)))
    if i == FACT1:
        lt = t - LINES[FACT1]["start"]
        text(ctx, "PROBABLY HUNTED BY DAY", W / 2, BOT[0] + 100, 58, Y_, alpha=ease_out(seg(lt, 0.2, 0.6)))
        _sun(ctx, 230, BOT[0] + 250, 55 * ease_back(seg(lt, 0.4, 0.9)), t, uf)
        _roach(ctx, 690, BOT[0] + 270, 0.62 * ease_back(seg(lt, 2.4, 2.9)), t, uf, rot=0.25)
        u = ease_back(seg(lt, 3.6, 4.0))
        if u > 0.01:
            _plate(ctx, 690, BOT[0] + 420, "IRIDESCENT WINGS", K_, Y_, u, 36)
        u = ease_back(seg(lt, 5.4, 5.8))
        if u > 0.01:
            _plate(ctx, 230, BOT[0] + 420, "= DAYTIME", WHITE, ORANGE, u, 36)
    elif i == BONES:
        lt = t - LINES[BONES]["start"]
        k = ease_out(seg(lt, -0.2, 0.3))
        text(ctx, "UPPER WING BONE", W / 2, BOT[0] + 100, 56, Y_, alpha=k)
        g1 = ease_out(seg(lt, 0.4, 1.2))
        _bone(ctx, W / 2, BOT[0] + 180, 300 * g1 + 1, 46, uf * min(1, g1 * 3))
        text(ctx, "THIS FOSSIL OWL: SHORT & STOCKY", W / 2, BOT[0] + 285, 38, WHITE, alpha=uf * ease_out(seg(lt, 1.0, 1.4)))
        g2 = ease_out(seg(lt, 2.2, 3.0))
        _bone(ctx, W / 2, BOT[0] + 350, 520 * g2 + 1, 22, uf * min(1, g2 * 3), col=(0.80, 0.82, 0.86))
        text(ctx, "NIGHT OWLS TODAY: SLENDER", W / 2, BOT[0] + 425, 38, WHITE, alpha=uf * ease_out(seg(lt, 2.8, 3.2)))
    elif i == FACT2:
        lt = t - LINES[FACT2]["start"]
        text(ctx, "NIGHT HUNTING CAME LATER", W / 2, BOT[0] + 100, 56, Y_, alpha=uf)
        x0, x1, yb = 150, W - 150, BOT[0] + 250
        g = ease_io(seg(lt, 0.4, 1.6))
        ctx.move_to(x0, yb)
        ctx.line_to(lerp(x0, x1, g), yb)
        src(ctx, WHITE, uf)
        ctx.set_line_width(10)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
        # 47 Ma at left (x0+120), 34 Ma at x0+600, today at x1
        xa, xb = x0 + 110, x0 + 560
        h = ease_out(seg(lt, 3.3, 4.6))
        if h > 0.01:
            rrect(ctx, xa, yb - 40, (xb - xa) * h, 80, 20)
            src(ctx, Y_, 0.35 * uf)
            ctx.fill()
        for xx, lab, tt in ((xa, "47", 2.6), (xb, "34", 4.4), (x1, "TODAY", 1.4)):
            u = ease_back(seg(lt, tt, tt + 0.4))
            if u > 0.01:
                ellipse(ctx, xx, yb, 18 * u, 18 * u)
                src(ctx, Y_ if lab != "TODAY" else WHITE, uf)
                ctx.fill()
                text(ctx, lab, xx, yb + 90, 54 if lab != "TODAY" else 40, Y_ if lab != "TODAY" else WHITE, alpha=uf * min(1, u))
        text(ctx, "MILLION YEARS AGO", (xa + xb) / 2, yb + 150, 36, WHITE, alpha=uf * ease_out(seg(lt, 4.6, 5.0)))
        _sun(ctx, xa, yb - 95, 30 * ease_back(seg(lt, 2.8, 3.2)), t, uf)
        _moon(ctx, xb + 10, yb - 95, 34 * ease_back(seg(lt, 4.6, 5.0)), uf)
    else:  # CAVEAT
        lt = t - LINES[CAVEAT]["start"]
        k = ease_out(seg(lt, -0.2, 0.3))
        text(ctx, "WHAT'S STILL UNCERTAIN", W / 2, BOT[0] + 100, 54, Y_, alpha=k)
        u = ease_back(seg(lt, 0.3, 0.7))
        if u > 0.01:
            _bone(ctx, 300, BOT[0] + 205, 150 * u, 26, uf, rot=0.3)
            _bone(ctx, 330, BOT[0] + 235, 110 * u, 22, uf, rot=-0.5)
            text(ctx, "RARE FOSSILS", 310, BOT[0] + 340, 40, WHITE, alpha=uf * min(1, u))
        u = ease_back(seg(lt, 1.8, 2.2))
        if u > 0.01:
            _plate(ctx, 310, BOT[0] + 400, "TIMELINE MAY CHANGE", K_, WHITE, u, 32)
        u = ease_back(seg(lt, 3.0, 3.4))
        if u > 0.01:
            cx, cy = 770, BOT[0] + 285
            ctx.save()
            ctx.rectangle(cx - 160, cy - 140, 320, 140)
            ctx.clip()
            _sun(ctx, cx, cy, 55 * u, t, uf)
            ctx.restore()
            ctx.move_to(cx - 170, cy)
            ctx.line_to(cx + 170, cy)
            src(ctx, WHITE, uf)
            ctx.set_line_width(8)
            ctx.stroke()
            text(ctx, "DAWN OR DUSK?", cx, cy + 50, 40, WHITE, alpha=uf * min(1, u))


def _outro(ctx, t):
    t0 = _st(OUTRO)
    lt = t - LINES[OUTRO]["start"]
    _headline(ctx, t0, t, "BORN A DAY BIRD?", size=110)
    k = ease_out(seg(t, t0, t0 + 0.4))
    m = ease_io(seg(lt, 0.8, 2.4))
    rrect(ctx, 140, 720, W - 280, 560, 40)
    src(ctx, (lerp(SKY[0], NIGHT[0], m), lerp(SKY[1], NIGHT[1], m), lerp(SKY[2], NIGHT[2], m)), k)
    ctx.fill()
    ctx.save()
    rrect(ctx, 140, 720, W - 280, 560, 40)
    ctx.clip()
    _sun(ctx, 800, lerp(840, 1240, m), 60, t, k * (1 - m))
    _moon(ctx, 800, lerp(1240, 840, m), 55, k * m)
    ctx.restore()
    _owl(ctx, W / 2 - 80, 1010, 1.0 * k, t, k)
    u = ease_back(seg(lt, 1.2, 1.6))
    if u > 0.01:
        _plate(ctx, W / 2, 1355, "DAY HUNTER  >  NIGHT HUNTER", K_, Y_, u, 42)
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




def _wipe(ctx, t):
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
    if i is None and t < END + 0.3:
        _outro(ctx, t)
    if i is not None:
        if i <= TWO:
            _intro(ctx, i, t)
        elif i <= CAVEAT:
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
