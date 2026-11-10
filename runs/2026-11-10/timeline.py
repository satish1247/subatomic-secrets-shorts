"""2026-11-10 countdown: Anthropic releases Claude Fable 5.2 and Mythos 5.2, 3 things to know (contract: DURATION + render_frame)."""
import json
import math
import os
import cairo
from gfx import FONT, W, H, ease_back, ease_out, ease_io, ease_in, seg, src, text, ellipse, rrect, lerp, wrap
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
RED = (0.88, 0.18, 0.15)
PANEL = (0.13, 0.14, 0.17)
WHITE = (1, 1, 1)
GREY = (0.55, 0.58, 0.63)
# (headline, subline, countdown number or None)
CARDS = [
    ("2 NEW CLAUDE MODELS", "FABLE 5.2 + MYTHOS 5.2", None),
    ("ONE FOR EVERYONE", "MYTHOS 5.2: VETTED ORGS ONLY", None),
    ("3 THINGS TO KNOW", "", None),
    ("FASTER + CHEAPER", "UP TO 30% FASTER \u2022 $8 / 1M INPUT", 3),
    ("SAME BRAIN", "DIFFERENT SAFETY BRAKES", 2),
    ("FERMAT IN ~30 HOURS", "1,000 AGENTS \u2022 PER ANTHROPIC", 1),
    ("ONE TWIST", "\"AM I BEING TESTED?\"", None),
    ("TRUST IT?", "", None),
]
GLASS = (0.10, 0.12, 0.16)
FRAME = (0.78, 0.80, 0.84)
ICON_Y = 1040
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
    if len(out) > 1 and len(cur) < 3:   # avoid one-word caption tails
        prev = out[-2].split()
        out[-2:] = [" ".join(prev[:-2]), " ".join(prev[-2:] + cur)]
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
    g.add_color_stop_rgb(0, 0.04, 0.05, 0.07)
    g.add_color_stop_rgb(0.65, 0.06, 0.09, 0.11)
    g.add_color_stop_rgb(1, 0.05, 0.16, 0.17)
    ctx.set_source(g)
    ctx.paint()
    # drifting dot grid
    off = (t * 18) % 90
    for gx in range(-1, 14):
        for gy in range(-1, 23):
            x, y = gx * 90 + 45, gy * 90 + off
            a = 0.10 + 0.08 * math.sin(t * 1.5 + gx * 0.7 + gy * 0.4)
            ellipse(ctx, x, y, 3, 3)
            src(ctx, TEAL, a)
            ctx.fill()


# ------------------------------------------------------------------ drawing helpers
def _panel(ctx, x, y, w, h, a=1.0, fill=PANEL, edge=None, r=28):
    rrect(ctx, x, y, w, h, r)
    src(ctx, fill, a)
    ctx.fill_preserve()
    src(ctx, edge or (1, 1, 1), 0.25 * a if edge is None else a)
    ctx.set_line_width(4)
    ctx.stroke()


def _pop(t, t0, d=0.35):
    return ease_back(seg(t, t0, t0 + d))


def _scaled(ctx, x, y, u, fn):
    if u <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(u, u)
    fn()
    ctx.restore()


def _text_lines(ctx, x, y, w, n, a=1.0, col=GREY, gap=42, frac=1.0):
    """Placeholder text lines (grey bars); frac reveals them left-to-right."""
    for j in range(n):
        lw = w * (0.92 if j < n - 1 else 0.55) * clamp_(frac * n - j)
        if lw > 1:
            rrect(ctx, x, y + j * gap, lw, 18, 9)
            src(ctx, col, a)
            ctx.fill()


def clamp_(v):
    return max(0.0, min(1.0, v))


def _button(ctx, x, y, w, h, label, col=None, a=1.0, size=36):
    rrect(ctx, x - w / 2, y - h / 2, w, h, h / 2)
    src(ctx, col or Y_, a)
    ctx.fill()
    text(ctx, label, x, y + size * 0.36, size, K_, alpha=a)


def _bars(ctx, x, y, w, h, u, a=1.0):
    vals = (0.45, 0.8, 0.6, 0.95, 0.7)
    bw = w / len(vals)
    for j, v in enumerate(vals):
        hh = h * v * ease_out(seg(u, j * 0.12, j * 0.12 + 0.5))
        rrect(ctx, x + j * bw + 8, y + h - hh, bw - 16, hh, 8)
        src(ctx, TEAL if j % 2 else Y_, a)
        ctx.fill()




def _model_card(ctx, x, y, s, label, col, a=1.0, t=0.0, lock=False):
    """Generic AI model tile: rounded glass card with a glowing spark core (no logos)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -170, -200, 340, 400, 40)
    src(ctx, GLASS, a)
    ctx.fill_preserve()
    src(ctx, col, a)
    ctx.set_line_width(6)
    ctx.stroke()
    g = 0.75 + 0.25 * math.sin(t * 3 + x)
    for r_, al in ((95, 0.18), (70, 0.35)):
        ellipse(ctx, 0, -40, r_ * g, r_ * g)
        src(ctx, col, al * a)
        ctx.fill()
    _spark(ctx, 0, -40, 52, col, a)
    text(ctx, label, 0, 140, 44, (1, 1, 1), alpha=a)
    if lock:
        _lock(ctx, 120, -150, 0.6, a)
    ctx.restore()


def _spark(ctx, x, y, r, col, a=1.0):
    """Four-point star."""
    ctx.move_to(x, y - r)
    for k_ in range(4):
        ang = -math.pi / 2 + k_ * math.pi / 2
        ctx.line_to(x + 0.22 * r * math.cos(ang + math.pi / 4) * 1.4, y + 0.22 * r * math.sin(ang + math.pi / 4) * 1.4)
        ctx.line_to(x + r * math.cos(ang + math.pi / 2), y + r * math.sin(ang + math.pi / 2))
    ctx.close_path()
    src(ctx, (1, 1, 1), a)
    ctx.fill()


def _lock(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.arc(0, -30, 42, math.pi, 2 * math.pi)
    src(ctx, FRAME, a)
    ctx.set_line_width(16)
    ctx.stroke()
    rrect(ctx, -65, -30, 130, 105, 16)
    src(ctx, ORANGE, a)
    ctx.fill()
    ellipse(ctx, 0, 15, 14, 14)
    src(ctx, K_, a)
    ctx.fill()
    ctx.restore()


def _person(ctx, x, y, s, col, a=1.0):
    ellipse(ctx, x, y - 34 * s, 20 * s, 20 * s)
    src(ctx, col, a)
    ctx.fill()
    rrect(ctx, x - 26 * s, y - 8 * s, 52 * s, 56 * s, 22 * s)
    ctx.fill()


def _brain(ctx, x, y, s, col, a=1.0):
    """Simple two-lobe brain glyph."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for side in (-1, 1):
        for (bx, by, br) in ((48, -40, 52), (70, 20, 50), (30, 50, 44), (22, -2, 50)):
            ellipse(ctx, side * bx, by, br, br)
            src(ctx, col, a)
            ctx.fill()
    ctx.move_to(0, -95)
    ctx.line_to(0, 95)
    src(ctx, K_, 0.6 * a)
    ctx.set_line_width(6)
    ctx.stroke()
    for side in (-1, 1):
        ctx.move_to(side * 30, -50)
        ctx.curve_to(side * 70, -30, side * 30, 0, side * 75, 15)
        ctx.move_to(side * 20, 30)
        ctx.curve_to(side * 50, 45, side * 60, 60, side * 40, 80)
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.restore()


def _shield(ctx, x, y, s, col, fill=1.0, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(0, -90)
    ctx.line_to(75, -60)
    ctx.curve_to(75, 20, 40, 70, 0, 95)
    ctx.curve_to(-40, 70, -75, 20, -75, -60)
    ctx.close_path()
    src(ctx, col, a * (0.25 + 0.75 * fill))
    ctx.fill_preserve()
    src(ctx, (1, 1, 1), a)
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.restore()


def _gauge(ctx, x, y, r, u, a=1.0):
    """Speedometer: arc, ticks, needle swept by u."""
    ctx.arc(x, y, r, math.pi, 2 * math.pi)
    src(ctx, FRAME, a)
    ctx.set_line_width(14)
    ctx.stroke()
    ctx.arc(x, y, r, math.pi, math.pi + math.pi * u)
    src(ctx, Y_, a)
    ctx.set_line_width(14)
    ctx.stroke()
    ang = math.pi + math.pi * u
    ctx.move_to(x, y)
    ctx.line_to(x + (r - 30) * math.cos(ang), y + (r - 30) * math.sin(ang))
    src(ctx, (1, 1, 1), a)
    ctx.set_line_width(10)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    ctx.set_line_cap(cairo.LINE_CAP_BUTT)
    ellipse(ctx, x, y, 18, 18)
    ctx.fill()


def _tag(ctx, x, y, label, col, a=1.0, w=260, h=120, size=70):
    ctx.move_to(x - w / 2, y - h / 2)
    ctx.line_to(x + w / 2 - 40, y - h / 2)
    ctx.line_to(x + w / 2, y)
    ctx.line_to(x + w / 2 - 40, y + h / 2)
    ctx.line_to(x - w / 2, y + h / 2)
    ctx.close_path()
    src(ctx, col, a)
    ctx.fill()
    ellipse(ctx, x + w / 2 - 44, y, 10, 10)
    src(ctx, K_, a)
    ctx.fill()
    text(ctx, label, x - 20, y + size * 0.36, size, K_, alpha=a)


def _icon(ctx, i, t, k):
    t0 = _card_start(i)
    lt = t - t0
    cx = W / 2
    if i == 0:   # two model tiles pop in side by side
        _model_card(ctx, cx - 210, ICON_Y + 10, 0.95 * _pop(lt, 0.2), "FABLE 5.2", Y_, k, t)
        _model_card(ctx, cx + 210, ICON_Y + 10, 0.95 * _pop(lt, 0.6), "MYTHOS 5.2", TEAL, k, t)
    elif i == 1:   # Fable: crowd of people; Mythos: lock + few verified badges
        _model_card(ctx, cx - 230, ICON_Y - 60, 0.75, "FABLE 5.2", Y_, k, t)
        for j in range(8):
            u = ease_back(seg(lt, 0.4 + 0.08 * j, 0.7 + 0.08 * j))
            if u > 0.01:
                _person(ctx, cx - 380 + (j % 4) * 100, ICON_Y + 170 + (j // 4) * 120, 0.9 * u, (1, 1, 1), k)
        a2 = k * ease_out(seg(lt, 2.0, 2.5))
        if a2 > 0.01:
            _model_card(ctx, cx + 230, ICON_Y - 60, 0.75, "MYTHOS 5.2", TEAL, a2, t, lock=True)
            for j in range(2):
                u = ease_back(seg(lt, 3.2 + 0.2 * j, 3.6 + 0.2 * j))
                if u > 0.01:
                    xx = cx + 170 + j * 120
                    _person(ctx, xx, ICON_Y + 230, 0.9 * u, TEAL, a2)
                    ellipse(ctx, xx + 30, ICON_Y + 170, 20 * u, 20 * u)
                    src(ctx, Y_, a2)
                    ctx.fill()
            _button(ctx, cx + 230, ICON_Y + 360, 300, 70, "VERIFIED", col=TEAL, a=a2 * ease_out(seg(lt, 3.8, 4.2)), size=34)
    elif i == 2:   # three numbered cards
        for j in range(3):
            u = ease_back(seg(lt, 0.15 * j, 0.15 * j + 0.4))
            if u > 0.01:
                xx = cx + (j - 1) * 300
                ctx.save()
                ctx.translate(xx, ICON_Y + 20)
                ctx.scale(u, u)
                rrect(ctx, -120, -150, 240, 300, 36)
                src(ctx, Y_)
                ctx.fill()
                text(ctx, str(3 - j), 0, 70, 220, K_)
                ctx.restore()
    elif i == 3:   # speedometer then price tag $10 -> $8
        u = ease_out(seg(lt, 0.8, 2.6))
        _gauge(ctx, cx, ICON_Y + 20, 230, 0.55 + 0.4 * u, k)
        text(ctx, "UP TO +30%", cx, ICON_Y + 110, 56, Y_, alpha=k * ease_out(seg(lt, 1.6, 2.0)))
        a2 = k * ease_out(seg(lt, 3.6, 4.0))
        if a2 > 0.01:
            _tag(ctx, cx - 230, ICON_Y + 300, "$10", GREY, a2)
            su = ease_out(seg(lt, 4.6, 5.0))
            if su > 0:
                ctx.move_to(cx - 360, ICON_Y + 300)
                ctx.line_to(lerp(cx - 360, cx - 100, su), ICON_Y + 300)
                src(ctx, RED, a2)
                ctx.set_line_width(12)
                ctx.stroke()
            _scaled(ctx, cx + 230, ICON_Y + 300, _pop(lt, 5.2), lambda: _tag(ctx, 0, 0, "$8", Y_, a2))
    elif i == 4:   # one brain, two shields (strong vs relaxed)
        _scaled(ctx, cx, ICON_Y - 140, _pop(lt, 0.2), lambda: _brain(ctx, 0, 0, 1.1, (0.95, 0.62, 0.70), k))
        text(ctx, "SAME MODEL", cx, ICON_Y + 10, 46, (1, 1, 1), alpha=k * ease_out(seg(lt, 0.8, 1.2)))
        a2 = k * ease_out(seg(lt, 2.2, 2.6))
        if a2 > 0.01:
            _shield(ctx, cx - 230, ICON_Y + 180, 1.15, Y_, 1.0, a2)
            text(ctx, "FABLE", cx - 230, ICON_Y + 330, 42, Y_, alpha=a2)
            text(ctx, "STRONG", cx - 230, ICON_Y + 190, 28, K_, alpha=a2)
            f = 1 - 0.8 * ease_out(seg(lt, 3.6, 4.6))
            _shield(ctx, cx + 230, ICON_Y + 180, 1.15, TEAL, f, a2)
            text(ctx, "MYTHOS", cx + 230, ICON_Y + 330, 42, TEAL, alpha=a2)
            text(ctx, "LOOSER", cx + 230, ICON_Y + 190, 28, (1, 1, 1), alpha=a2 * seg(lt, 4.0, 4.4))
            text(ctx, "CYBER \u2022 BIO", cx, ICON_Y + 190, 30, GREY, alpha=a2 * ease_out(seg(lt, 4.8, 5.2)))
    elif i == 5:   # agent grid fills, equation, 30 h vs 11 days bars
        cols, rows = 25, 8   # 200 dots stand in for 1,000 agents
        fill = ease_io(seg(lt, 0.6, 5.0))
        for j in range(cols * rows):
            xx = 150 + (j % cols) * 32
            yy = ICON_Y - 210 + (j // cols) * 32
            on = (j / (cols * rows)) < fill
            ellipse(ctx, xx, yy, 10, 10)
            src(ctx, Y_ if on else PANEL, k)
            ctx.fill()
        text(ctx, "x 1,000 AGENTS", cx, ICON_Y + 90, 40, (1, 1, 1), alpha=k * ease_out(seg(lt, 0.8, 1.2)))
        a2 = k * ease_out(seg(lt, 2.0, 2.4))
        if a2 > 0.01:
            _panel(ctx, 170, ICON_Y + 120, 740, 100, a2, edge=Y_)
            text(ctx, "aⁿ + bⁿ ≠ cⁿ   ✓", cx, ICON_Y + 188, 52, Y_, alpha=a2)
        a3 = k * ease_out(seg(lt, 6.6, 7.0))
        if a3 > 0.01:
            bu = ease_out(seg(lt, 6.8, 7.6))
            rrect(ctx, 360, ICON_Y + 225, 540 * 30 / 264 * bu + 10, 50, 12)
            src(ctx, Y_, a3)
            ctx.fill()
            text(ctx, "~30 H", 210, ICON_Y + 265, 40, Y_, alpha=a3)
            bu2 = ease_out(seg(lt, 8.6, 9.6))
            rrect(ctx, 360, ICON_Y + 295, 540 * bu2 + 10, 50, 12)
            src(ctx, GREY, a3)
            ctx.fill()
            text(ctx, "11 DAYS", 210, ICON_Y + 335, 40, GREY, alpha=a3 * seg(lt, 8.6, 8.9))
    elif i == 6:   # model tile under a magnifier, question marks
        _model_card(ctx, cx, ICON_Y + 20, 0.9, "FABLE 5.2", Y_, k, t)
        mx = cx + 160 * math.sin(lt * 1.2)
        my = ICON_Y - 60 + 40 * math.cos(lt * 1.2)
        ctx.arc(mx, my, 110, 0, 2 * math.pi)
        src(ctx, (1, 1, 1), 0.12 * k)
        ctx.fill_preserve()
        src(ctx, (1, 1, 1), k)
        ctx.set_line_width(14)
        ctx.stroke()
        ctx.move_to(mx + 78, my + 78)
        ctx.line_to(mx + 170, my + 170)
        ctx.set_line_width(26)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
        ctx.set_line_cap(cairo.LINE_CAP_BUTT)
        for j in range(3):
            q = _pop(lt, 1.0 + 0.5 * j)
            _scaled(ctx, cx - 330 + j * 330, ICON_Y - 280 + (j % 2) * 40, q,
                    lambda: text(ctx, "?", 0, 30, 100, ORANGE if j == 1 else Y_))
    elif i == 7:   # question mark over the two tiles
        _model_card(ctx, cx - 210, ICON_Y + 80, 0.7, "FABLE", Y_, k, t)
        _model_card(ctx, cx + 210, ICON_Y + 80, 0.7, "MYTHOS", TEAL, k, t)
        q = _pop(lt, 0.3)
        _scaled(ctx, cx, ICON_Y - 250, q, lambda: text(ctx, "?", 0, 50, 160, Y_))


def _number(ctx, n, t, t0):
    """Big yellow countdown number that slams in."""
    u = ease_back(seg(t, t0, t0 + 0.35), 2.2)
    if u <= 0.01:
        return
    ctx.save()
    ctx.translate(W / 2, 470)
    ctx.scale(lerp(1.8, 1.0, min(1, u)), lerp(1.8, 1.0, min(1, u)))
    ellipse(ctx, 0, 0, 110, 110)
    src(ctx, Y_)
    ctx.fill()
    text(ctx, str(n), 0, 62, 170, K_)
    ctx.restore()


def _headline(ctx, i, t):
    t0 = _card_start(i)
    k = ease_back(seg(t, t0, t0 + 0.35))
    head, sub, num = CARDS[i]
    hy = 700 if num else 560
    if num:
        _number(ctx, num, t, t0)
    size = 118
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    while ctx.text_extents(head).x_advance > W - 140 and size > 60:
        size -= 4
        ctx.set_font_size(size)
    ctx.save()
    ctx.translate(W / 2, hy)
    ctx.scale(k, k)
    text(ctx, head, 0, 0, size, Y_ if not num else (1, 1, 1))
    ctx.restore()
    if sub:
        text(ctx, sub, W / 2, hy + 80, 40, (1, 1, 1) if not num else Y_, alpha=ease_out(seg(t, t0 + 0.3, t0 + 0.7)))
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
        brand.caption(ctx, ctext, 1540, CAP_SIZE, pop=pk * pulse)
    _wipe(ctx, t)
    brand.watermark(ctx)
    brand.end_card(ctx, t, DURATION - 1.4)
    surf.flush()
    return surf

