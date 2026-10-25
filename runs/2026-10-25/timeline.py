"""2026-10-25 countdown: Apple iPhone Duo, the first foldable iPhone, goes on sale (contract: DURATION + render_frame)."""
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
    ("FOLDING IPHONE", "ON SALE NOW", None),
    ("IPHONE DUO", "FROM $1,999", None),
    ("3 THINGS TO KNOW", "", None),
    ("TWO SCREENS", "5.4\" OUTSIDE \u2022 7.6\" INSIDE", 3),
    ("THIN BUT HEAVY", "5.2 MM OPEN \u2022 254 G", 2),
    ("NO FACE ID", "TOUCH ID IN THE SIDE BUTTON", 1),
    ("SOLD OUT FAST", "NEW ORDERS: LATE JAN 2027", None),
    ("WOULD YOU FOLD?", "", None),
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



def _screen(ctx, x, y, w, h, t, a=1.0, glow=0.0):
    """Generic phone panel: titanium frame + dark glass + abstract app tiles (no real UI/logos)."""
    rrect(ctx, x - 8, y - 8, w + 16, h + 16, 34)
    src(ctx, FRAME, a)
    ctx.fill()
    rrect(ctx, x, y, w, h, 28)
    g = cairo.LinearGradient(x, y, x + w, y + h)
    g.add_color_stop_rgba(0, 0.10, 0.20, 0.30, a)
    g.add_color_stop_rgba(1, 0.05, 0.25, 0.27, a)
    ctx.set_source(g)
    ctx.fill()
    cols = max(2, int(w // 110))
    rows = max(2, int(h // 120))
    tw, th = w / cols, h / rows
    for c in range(cols):
        for r in range(rows):
            ph = math.sin(t * 2 + c * 0.9 + r * 0.6)
            rrect(ctx, x + c * tw + 16, y + r * th + 16, tw - 32, th - 32, 18)
            col = (Y_, TEAL, ORANGE, (1, 1, 1))[(c + r * 2) % 4]
            src(ctx, col, a * (0.55 + 0.15 * ph))
            ctx.fill()
    if glow > 0:
        rrect(ctx, x - 14, y - 14, w + 28, h + 28, 40)
        src(ctx, Y_, glow * a)
        ctx.set_line_width(6)
        ctx.stroke()


def _foldphone(ctx, cx, cy, h, u, t, a=1.0):
    """Book-style foldable seen from the front, centred on cx; u=0 folded (one panel), u=1 open (two)."""
    w = h * 0.71   # each half, roughly the Duo's folded aspect
    left = cx - w * (1 + u) / 2
    hinge = left + w * u
    if u > 0.03:   # left half swings open (fake 3D: horizontal squash)
        ctx.save()
        ctx.translate(hinge, 0)
        ctx.scale(u, 1.0)
        _screen(ctx, -w, cy - h / 2, w, h, t, a)
        ctx.restore()
    _screen(ctx, hinge, cy - h / 2, w, h, t, a)
    if u > 0.05:   # hinge line
        ctx.move_to(hinge, cy - h / 2 - 8)
        ctx.line_to(hinge, cy + h / 2 + 8)
        src(ctx, (1, 1, 1), 0.35 * a * u)
        ctx.set_line_width(3)
        ctx.stroke()
    return left, hinge, w


def _dimension(ctx, x0, y0, x1, y1, label, a, col=None, size=44):
    col = col or Y_
    ctx.move_to(x0, y0)
    ctx.line_to(x1, y1)
    src(ctx, col, a)
    ctx.set_line_width(5)
    ctx.stroke()
    for (px, py) in ((x0, y0), (x1, y1)):
        ellipse(ctx, px, py, 9, 9)
        ctx.fill()
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    _button(ctx, mx, my, 40 + len(label) * size * 0.62, size * 1.6, label, col=col, a=a, size=size)


def _calendar(ctx, mon, day):
    rrect(ctx, -170, -190, 340, 380, 34)
    src(ctx, (1, 1, 1))
    ctx.fill()
    rrect(ctx, -170, -190, 340, 105, 34)
    src(ctx, Y_)
    ctx.fill()
    ctx.rectangle(-170, -120, 340, 35)
    ctx.fill()
    text(ctx, mon, 0, -118, 50, K_)
    text(ctx, day, 0, 105, 170 if len(day) <= 2 else 120, K_)


def _face_id(ctx, a):
    """Corner brackets + simple face glyph."""
    src(ctx, (1, 1, 1), a)
    ctx.set_line_width(12)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for sx in (-1, 1):
        for sy in (-1, 1):
            ctx.move_to(sx * 130, sy * 60)
            ctx.line_to(sx * 130, sy * 130)
            ctx.line_to(sx * 60, sy * 130)
    ctx.stroke()
    for ex in (-40, 40):
        ctx.move_to(ex, -40)
        ctx.line_to(ex, -15)
    ctx.move_to(0, -20)
    ctx.line_to(0, 20)
    ctx.line_to(-12, 20)
    ctx.stroke()
    ctx.arc(0, 30, 50, 0.25 * math.pi, 0.75 * math.pi)
    ctx.stroke()
    ctx.set_line_cap(cairo.LINE_CAP_BUTT)


def _fingerprint(ctx, a, u=1.0, col=None):
    col = col or Y_
    src(ctx, col, a)
    ctx.set_line_width(9)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for j in range(5):
        r = 24 + j * 24
        span = math.pi * (1.45 - 0.08 * j) * u
        ctx.new_sub_path()
        ctx.save()
        ctx.scale(0.8, 1.0)
        ctx.arc(0, 10, r, -math.pi / 2 - span / 2 - 0.3 * (j % 2), -math.pi / 2 + span / 2)
        ctx.restore()
        ctx.stroke()
    ctx.set_line_cap(cairo.LINE_CAP_BUTT)


def _icon(ctx, i, t, k):
    t0 = _card_start(i)
    lt = t - t0
    cx = W / 2
    if i == 0:   # phone unfolds with a sparkle
        u = ease_io(seg(lt, 0.3, 1.6))
        _foldphone(ctx, cx, ICON_Y + 40, 560, u, t, k)
        for q in range(4):
            ph = (t * 0.7 + q * 0.25) % 1.0
            sx, sy = (150, 930, 190, 900)[q], ICON_Y - 220 + q * 150
            r = 18 * math.sin(ph * math.pi)
            ctx.move_to(sx - r, sy)
            ctx.line_to(sx + r, sy)
            ctx.move_to(sx, sy - r)
            ctx.line_to(sx, sy + r)
            src(ctx, Y_, k)
            ctx.set_line_width(5)
            ctx.stroke()
    elif i == 1:   # calendar Oct 23 + price tag
        _scaled(ctx, 300, ICON_Y, _pop(lt, 0.2), lambda: _calendar(ctx, "OCT", "23"))

        def tag():
            ctx.move_to(-220, -110)
            ctx.line_to(150, -110)
            ctx.line_to(230, 0)
            ctx.line_to(150, 110)
            ctx.line_to(-220, 110)
            ctx.close_path()
            src(ctx, Y_)
            ctx.fill()
            ellipse(ctx, 185, 0, 14, 14)
            src(ctx, K_)
            ctx.fill()
            text(ctx, "$1,999", -45, 30, 88, K_)
            text(ctx, "STARTING PRICE", -40, 82, 28, K_)
        _scaled(ctx, 760, ICON_Y, _pop(lt, 2.4) * 0.92, tag)
        u = ease_out(seg(lt, 3.6, 4.1))
        _button(ctx, cx, ICON_Y + 320, 640, 90, "FIRST FOLDABLE IPHONE", a=k * u, size=42)
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
    elif i == 3:   # folded 5.4" -> open 7.6"
        u = ease_io(seg(lt, 3.0, 4.2))
        h = 500
        top, bot = ICON_Y + 30 - h / 2, ICON_Y + 30 + h / 2
        left, hinge, w = _foldphone(ctx, cx, ICON_Y + 30, h, u, t, k)
        if u < 0.05:   # outer screen diagonal
            a = k * ease_out(seg(lt, 0.8, 1.3))
            _dimension(ctx, hinge + 30, bot - 30, hinge + w - 30, top + 30, "5.4\"", a)
        if u > 0.95:   # inner screen diagonal
            a = k * ease_out(seg(lt, 4.2, 4.7))
            _dimension(ctx, left + 30, bot - 30, left + 2 * w - 30, top + 30, "7.6\"", a)
        text(ctx, "OUTSIDE" if u < 0.5 else "INSIDE", cx, ICON_Y + 345, 44, (1, 1, 1), alpha=k)
    elif i == 4:   # side profile thin slab -> scale 254 g
        u1 = ease_out(seg(lt, 0.3, 1.0))
        a1 = k * (1 - seg(lt, 4.0, 4.4))
        if a1 > 0.01:
            _panel(ctx, 100, ICON_Y - 240, 880, 560, a1)
            text(ctx, "SIDE VIEW, OPEN", cx, ICON_Y - 160, 40, GREY, alpha=a1)
            sw = 760 * u1
            rrect(ctx, cx - sw / 2, ICON_Y - 20, sw, 34, 17)
            src(ctx, FRAME, a1)
            ctx.fill()
            if u1 > 0.95:
                ctx.move_to(cx + 300, ICON_Y - 50)
                ctx.line_to(cx + 300, ICON_Y - 22)
                ctx.move_to(cx + 300, ICON_Y + 44)
                ctx.line_to(cx + 300, ICON_Y + 16)
                src(ctx, Y_, a1)
                ctx.set_line_width(5)
                ctx.stroke()
                _button(ctx, cx, ICON_Y + 170, 300, 96, "5.2 MM", a=a1 * ease_out(seg(lt, 1.1, 1.5)), size=54)
        a2 = k * seg(lt, 4.0, 4.4)
        if a2 > 0.01:   # weighing scale
            drop = ease_back(seg(lt, 4.2, 4.8))
            ctx.save()
            src(ctx, FRAME, a2)
            rrect(ctx, cx - 300, ICON_Y + 180, 600, 140, 30)
            ctx.fill()
            rrect(ctx, cx - 340, ICON_Y + 140, 680, 44, 22)
            src(ctx, (1, 1, 1), a2)
            ctx.fill()
            rrect(ctx, cx - 150, ICON_Y + 210, 300, 84, 14)
            src(ctx, K_, a2)
            ctx.fill()
            grams = int(254 * ease_out(seg(lt, 4.6, 5.6)))
            text(ctx, "%d G" % grams, cx, ICON_Y + 272, 60, Y_, alpha=a2)
            yy = lerp(ICON_Y - 400, ICON_Y + 30, drop)
            rrect(ctx, cx - 180, yy, 360, 110, 30)   # folded phone lying flat
            src(ctx, FRAME, a2)
            ctx.fill()
            rrect(ctx, cx - 165, yy + 14, 330, 82, 22)
            src(ctx, GLASS, a2)
            ctx.fill()
            ctx.restore()
            _button(ctx, cx, ICON_Y - 170, 600, 84, "HEAVIEST IPHONE YET", col=ORANGE,
                    a=a2 * ease_out(seg(lt, 5.8, 6.2)), size=42)
    elif i == 5:   # Face ID crossed out -> fingerprint on side button
        a1 = k * (1 - seg(lt, 2.0, 2.4))
        if a1 > 0.01:
            _scaled(ctx, cx, ICON_Y, _pop(lt, 0.1), lambda: _face_id(ctx, a1))
            c = seg(lt, 0.9, 1.3)
            if c > 0:
                ctx.move_to(cx - 190, ICON_Y - 190)
                ctx.line_to(lerp(cx - 190, cx + 190, c), lerp(ICON_Y - 190, ICON_Y + 190, c))
                src(ctx, RED, a1)
                ctx.set_line_width(22)
                ctx.set_line_cap(cairo.LINE_CAP_ROUND)
                ctx.stroke()
                ctx.set_line_cap(cairo.LINE_CAP_BUTT)
        a2 = k * seg(lt, 2.2, 2.6)
        if a2 > 0.01:
            _screen(ctx, cx - 300, ICON_Y - 250, 330, 470, t, a2)
            bx, by = cx + 38, ICON_Y - 150   # side button on the right edge
            rrect(ctx, bx - 6, by, 22, 120, 10)
            src(ctx, Y_, a2)
            ctx.fill()
            f = ease_out(seg(lt, 2.8, 3.6))
            ctx.save()
            ctx.translate(cx + 240, ICON_Y - 40)
            _fingerprint(ctx, a2, f)
            ctx.restore()
            ctx.move_to(bx + 30, by + 60)
            ctx.line_to(lerp(bx + 30, cx + 140, f), lerp(by + 60, ICON_Y - 40, f))
            ctx.set_dash([14, 10])
            src(ctx, Y_, a2)
            ctx.set_line_width(5)
            ctx.stroke()
            ctx.set_dash([])
            _button(ctx, cx, ICON_Y + 320, 420, 86, "TOUCH ID", a=a2 * ease_out(seg(lt, 3.4, 3.8)), size=48)
    elif i == 6:   # 30-minute timer -> calendar JAN 2027 + SOLD OUT stamp
        def timer():
            ctx.arc(0, 0, 150, 0, 2 * math.pi)
            src(ctx, PANEL)
            ctx.fill_preserve()
            src(ctx, (1, 1, 1))
            ctx.set_line_width(8)
            ctx.stroke()
            sweep = 2 * math.pi * ease_out(seg(lt, 0.8, 3.0))
            ctx.move_to(0, 0)
            ctx.arc(0, 0, 130, -math.pi / 2, -math.pi / 2 + sweep)
            ctx.close_path()
            src(ctx, Y_, 0.85)
            ctx.fill()
            text(ctx, "30 MIN", 0, 210, 48, (1, 1, 1))
        _scaled(ctx, 300, ICON_Y - 40, _pop(lt, 0.2), timer)
        _scaled(ctx, 780, ICON_Y - 40, _pop(lt, 4.6) * 0.85, lambda: _calendar(ctx, "JAN", "2027"))
        f = seg(lt, 4.2, 4.7)
        if f > 0:
            ctx.move_to(470, ICON_Y - 40)
            ctx.line_to(lerp(470, 610, f), ICON_Y - 40)
            src(ctx, Y_, k)
            ctx.set_line_width(10)
            ctx.stroke()
        s = ease_back(seg(lt, 1.6, 2.0), 2.4)
        if s > 0.01:
            ctx.save()
            ctx.translate(cx, ICON_Y + 290)
            ctx.rotate(-0.12)
            ctx.scale(lerp(1.6, 1.0, min(1, s)), lerp(1.6, 1.0, min(1, s)))
            rrect(ctx, -250, -62, 500, 124, 18)
            src(ctx, RED, k)
            ctx.set_line_width(10)
            ctx.stroke()
            text(ctx, "SOLD OUT", 0, 30, 84, RED, alpha=k)
            ctx.restore()
    elif i == 7:   # phone opens and closes, question mark
        u = 0.5 + 0.5 * math.sin((lt - 0.2) * 2.6 - math.pi / 2)
        _foldphone(ctx, cx, ICON_Y + 20, 470, u, t, k)
        q = _pop(lt, 0.4)
        _scaled(ctx, cx, ICON_Y - 340, q, lambda: text(ctx, "?", 0, 50, 160, Y_))


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

