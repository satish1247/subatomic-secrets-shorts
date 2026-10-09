"""2026-10-09 countdown: GPT-6 brings Intelligent UI to ChatGPT (contract: DURATION + render_frame)."""
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
    ("NOT JUST TEXT", "AI ANSWERS GET AN INTERFACE", None),
    ("INTELLIGENT UI", "NEW WITH GPT-6", None),
    ("3 THINGS IT DOES", "", None),
    ("RECIPES & MAPS", "THE ANSWER FITS THE QUESTION", 3),
    ("MINI TOOLS", "BUILT ON REQUEST", 2),
    ("BUILT LIVE", "WHILE THE ANSWER IS WRITTEN", 1),
    ("PLAIN TEXT TOO", "WHEN TEXT IS BEST", None),
    ("ROLLING OUT", "PAID FIRST · FREE & GO NEXT DAY", None),
]
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


def _cursor_hand(ctx, x, y, s=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(0, 0)
    ctx.line_to(0, 70)
    ctx.line_to(18, 54)
    ctx.line_to(32, 84)
    ctx.line_to(44, 78)
    ctx.line_to(30, 50)
    ctx.line_to(54, 48)
    ctx.close_path()
    src(ctx, (1, 1, 1))
    ctx.fill_preserve()
    src(ctx, K_)
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.restore()


def _icon(ctx, i, t, k):
    t0 = _card_start(i)
    lt = t - t0
    cx = W / 2
    if i == 0:   # a plain text bubble that turns into widgets
        _panel(ctx, 140, ICON_Y - 230, 800, 480, k)
        m = ease_io(seg(lt, 1.0, 1.6))
        _text_lines(ctx, 200, ICON_Y - 170, 680, 6, (1 - m) * k)
        if m > 0.01:
            _scaled(ctx, cx - 190, ICON_Y - 100, _pop(lt, 1.2), lambda: _button(ctx, 0, 0, 280, 90, "TAP ME"))
            _scaled(ctx, cx + 190, ICON_Y - 100, _pop(lt, 1.4), lambda: _button(ctx, 0, 0, 280, 90, "COMPARE", TEAL))
            _bars(ctx, 220, ICON_Y - 20, 640, 220, seg(lt, 1.5, 2.6), k)
        text(ctx, "TEXT", 260, ICON_Y + 305, 46, GREY, alpha=k)
        text(ctx, "→", cx, ICON_Y + 305, 60, Y_, alpha=k)
        text(ctx, "INTERFACE", 790, ICON_Y + 305, 46, Y_, alpha=k * (0.3 + 0.7 * m))
    elif i == 1:   # a chat answer made of components
        _panel(ctx, 120, ICON_Y - 260, 840, 600, k)
        items = [("BUTTONS", 0.4), ("FORMS", 1.3), ("CHARTS", 2.2), ("GRAPHICS", 3.1)]
        for j, (lab, tt) in enumerate(items):
            u = _pop(lt, tt)
            if u <= 0.01:
                continue
            col, row = j % 2, j // 2
            x, y = 170 + col * 400, ICON_Y - 220 + row * 280

            def draw(j=j, lab=lab):
                rrect(ctx, 0, 0, 340, 240, 22)
                src(ctx, (1, 1, 1), 0.08)
                ctx.fill()
                if j == 0:
                    _button(ctx, 170, 80, 240, 74, "YES")
                    _button(ctx, 170, 165, 240, 74, "NO", TEAL)
                elif j == 1:
                    for r in range(2):
                        rrect(ctx, 30, 40 + r * 80, 280, 56, 12)
                        src(ctx, (1, 1, 1), 0.9)
                        ctx.fill()
                        rrect(ctx, 46, 60 + r * 80, 120, 16, 8)
                        src(ctx, GREY)
                        ctx.fill()
                    _button(ctx, 170, 205, 180, 44, "SEND", Y_, size=26)
                elif j == 2:
                    _bars(ctx, 30, 20, 280, 200, seg(lt, tt, tt + 1.2))
                else:
                    ellipse(ctx, 120, 120, 70, 70)
                    src(ctx, ORANGE)
                    ctx.fill()
                    ctx.move_to(170, 200)
                    ctx.line_to(240, 60)
                    ctx.line_to(310, 200)
                    ctx.close_path()
                    src(ctx, TEAL)
                    ctx.fill()
            ctx.save()
            ctx.translate(x + 170, y + 120)
            ctx.scale(u, u)
            ctx.translate(-170, -120)
            draw()
            ctx.restore()
            text(ctx, lab, x + 170, y + 268, 32, Y_, alpha=min(1, u))
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
    elif i == 3:   # recipe + timeline (left), road trip map (right)
        _panel(ctx, 80, ICON_Y - 200, 440, 520, k)
        text(ctx, "RECIPE", 300, ICON_Y - 140, 44, Y_, alpha=k)
        steps = ("PREP", "BOIL", "SIMMER", "SERVE")
        for j, lab in enumerate(steps):
            u = ease_out(seg(lt, 0.4 + j * 0.35, 0.8 + j * 0.35))
            y = ICON_Y - 70 + j * 95
            ellipse(ctx, 130, y, 18, 18)
            src(ctx, TEAL if u > 0.5 else GREY, k)
            ctx.fill()
            if j < 3:
                ctx.move_to(130, y + 18)
                ctx.line_to(130, y + 77)
                src(ctx, GREY, k)
                ctx.set_line_width(5)
                ctx.stroke()
            rrect(ctx, 170, y - 26, 300 * u, 52, 14)
            src(ctx, Y_ if j == 2 else (1, 1, 1), 0.9 * k)
            ctx.fill()
            if u > 0.6:
                text(ctx, lab, 190, y + 14, 34, K_, align="left")
        # map
        mu = seg(lt, 3.0, 3.4)
        _panel(ctx, 560, ICON_Y - 200, 440, 520, k * max(0.35, mu), fill=(0.16, 0.30, 0.28))
        text(ctx, "ROAD TRIP", 780, ICON_Y - 140, 44, Y_, alpha=k * max(0.35, mu))
        pts = [(620, ICON_Y + 260), (720, ICON_Y + 120), (860, ICON_Y + 150), (930, ICON_Y - 50)]
        prog = ease_io(seg(lt, 3.4, 5.4)) * (len(pts) - 1)
        ctx.move_to(*pts[0])
        for j in range(1, len(pts)):
            f = clamp_(prog - (j - 1))
            if f <= 0:
                break
            ctx.line_to(lerp(pts[j - 1][0], pts[j][0], f), lerp(pts[j - 1][1], pts[j][1], f))
        ctx.set_dash([18, 12])
        src(ctx, (1, 1, 1), 0.9)
        ctx.set_line_width(8)
        ctx.stroke()
        ctx.set_dash([])
        for j, (px, py) in enumerate(pts):
            u = _pop(lt, 3.4 + j * 0.65)
            _scaled(ctx, px, py, u, lambda j=j: _pin(ctx, ORANGE if j in (0, 3) else Y_))
    elif i == 4:   # bill splitter + savings calc + tiny game
        u = _pop(lt, 0.2)

        def splitter():
            _panel(ctx, -230, -150, 460, 300, 1, fill=(1, 1, 1))
            text(ctx, "BILL SPLITTER", 0, -90, 40, K_)
            text(ctx, "120 ÷ 4", 0, -10, 64, TEAL)
            _button(ctx, 0, 85, 300, 80, "= 30 EACH", Y_, 40)
        _scaled(ctx, 300, ICON_Y - 55, u, splitter)

        def savings():
            _panel(ctx, -200, -150, 400, 300, 1)
            text(ctx, "SAVINGS", 0, -95, 40, Y_)
            rrect(ctx, -150, -40, 300, 20, 10)
            src(ctx, GREY)
            ctx.fill()
            f = 0.5 + 0.4 * math.sin(lt * 1.6)
            rrect(ctx, -150, -40, 300 * f, 20, 10)
            src(ctx, TEAL)
            ctx.fill()
            ellipse(ctx, -150 + 300 * f, -30, 26, 26)
            src(ctx, Y_)
            ctx.fill()
            _bars(ctx, -150, 10, 300, 120, 1.0)
        _scaled(ctx, 790, ICON_Y - 55, _pop(lt, 1.4), savings)

        def game():
            _panel(ctx, -170, -125, 340, 250, 1)
            ctx.set_line_width(8)
            src(ctx, (1, 1, 1))
            for q in (-1, 1):
                ctx.move_to(q * 45, -110)
                ctx.line_to(q * 45, 110)
                ctx.move_to(-135, q * 72)
                ctx.line_to(135, q * 72)
            ctx.stroke()
            marks = [(-90, -72, "X"), (0, 0, "O"), (90, 72, "X"), (90, -72, "O")]
            for j, (mx, my, m) in enumerate(marks):
                if lt > 3.2 + j * 0.5:
                    text(ctx, m, mx, my + 22, 64, Y_ if m == "X" else TEAL)
        _scaled(ctx, cx, ICON_Y + 250, _pop(lt, 3.0), game)
    elif i == 5:   # interface assembling while text is still streaming
        _panel(ctx, 120, ICON_Y - 215, 840, 545, k)
        frac = seg(lt, 0.2, 4.6)
        _text_lines(ctx, 170, ICON_Y - 175, 740, 3, k, frac=frac * 1.4)
        blocks = [(170, ICON_Y - 60, 360, 140), (550, ICON_Y - 60, 360, 140),
                  (170, ICON_Y + 100, 740, 140)]
        for j, (x, y, w, h) in enumerate(blocks):
            u = ease_out(seg(lt, 0.8 + j * 1.1, 1.4 + j * 1.1))
            rrect(ctx, x, y, w, h, 20)
            src(ctx, (1, 1, 1), 0.06)
            ctx.fill()
            if u > 0.01:
                rrect(ctx, x, y, w, h * u, 20)
                src(ctx, (Y_, TEAL, ORANGE)[j], 0.9)
                ctx.fill()
        if frac < 1 and int(lt * 3) % 2 == 0:
            rrect(ctx, 170 + 740 * min(1, frac * 1.4) % 740, ICON_Y - 97, 8, 40, 3)
            src(ctx, Y_)
            ctx.fill()
        text(ctx, "STREAMING…" if frac < 1 else "DONE", cx, ICON_Y + 300, 44, Y_, alpha=k)
    elif i == 6:   # plain text answer
        _panel(ctx, 160, ICON_Y - 200, 760, 360, k)
        text(ctx, "Aa", 250, ICON_Y - 110, 64, Y_, alpha=k, align="left")
        _text_lines(ctx, 230, ICON_Y - 40, 620, 4, k, col=(1, 1, 1), frac=seg(lt, 0.3, 1.6))
        _cursor_hand(ctx, 760, ICON_Y + 60 + 10 * math.sin(lt * 4), 1.1)
    elif i == 7:   # two calendar tiles
        for j, (day, lab, col) in enumerate((("7", "PAID PLANS", Y_), ("8", "FREE & GO", TEAL))):
            u = _pop(lt, 0.2 + j * 2.2)
            x = 300 + j * 480

            def cal(day=day, lab=lab, col=col):
                rrect(ctx, -180, -200, 360, 400, 34)
                src(ctx, (1, 1, 1))
                ctx.fill()
                rrect(ctx, -180, -200, 360, 110, 34)
                src(ctx, col)
                ctx.fill()
                ctx.rectangle(-180, -130, 360, 40)
                ctx.fill()
                text(ctx, "OCT", 0, -125, 52, K_)
                text(ctx, day, 0, 110, 200, K_)
            _scaled(ctx, x, ICON_Y - 20, u, cal)
            if u > 0.01:
                text(ctx, lab, x, ICON_Y + 260, 48, col, alpha=min(1, u))
        a = ease_out(seg(lt, 1.6, 2.2))
        text(ctx, "→", cx, ICON_Y + 10, 90, (1, 1, 1), alpha=a)


def _pin(ctx, col):
    ctx.move_to(0, 0)
    ctx.curve_to(-40, -50, -36, -90, 0, -90)
    ctx.curve_to(36, -90, 40, -50, 0, 0)
    src(ctx, col)
    ctx.fill_preserve()
    src(ctx, K_)
    ctx.set_line_width(5)
    ctx.stroke()
    ellipse(ctx, 0, -60, 13, 13)
    src(ctx, K_)
    ctx.fill()


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
