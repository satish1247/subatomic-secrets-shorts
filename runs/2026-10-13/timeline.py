"""2026-10-13 countdown: Meta releases Muse Wonder (contract: DURATION + render_frame)."""
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
    ("META IS IN", "THE FRONTIER AI RACE", None),
    ("MUSE WONDER", "META SUPERINTELLIGENCE LABS", None),
    ("3 THINGS TO KNOW", "", None),
    ("TWO MODELS", "WONDER + WONDER FULL", 3),
    ("BUILT FOR AGENTS", "PERSONAL + PROFESSIONAL", 2),
    ("NOT FREE", "PAID PLANS ONLY", 1),
    ("META'S CLAIM", "ON PAR AT CODING", None),
    ("THE CATCH", "NO OUTSIDE CONFIRMATION YET", None),
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
    if i == 0:   # race: three lanes, the yellow runner surges to the front
        _panel(ctx, 100, ICON_Y - 240, 880, 560, k)
        text(ctx, "FRONTIER", 880, ICON_Y - 175, 34, GREY, align="right", alpha=k)
        ctx.move_to(890, ICON_Y - 150)
        ctx.line_to(890, ICON_Y + 290)
        ctx.set_dash([16, 12])
        src(ctx, (1, 1, 1), 0.7 * k)
        ctx.set_line_width(6)
        ctx.stroke()
        ctx.set_dash([])
        lanes = [("LAB A", 0.86, TEAL), ("LAB B", 0.84, ORANGE), ("META", None, Y_)]
        for j, (lab, pos, col) in enumerate(lanes):
            y = ICON_Y - 80 + j * 140
            ctx.move_to(160, y + 50)
            ctx.line_to(920, y + 50)
            src(ctx, (1, 1, 1), 0.12 * k)
            ctx.set_line_width(3)
            ctx.stroke()
            if pos is None:
                pos = lerp(0.35, 0.86, ease_out(seg(lt, 0.3, 2.0)))
            x = lerp(200, 880, pos)
            for q in range(5):   # speed trail
                ellipse(ctx, x - 40 - q * 34, y, 22 - q * 3, 22 - q * 3)
                src(ctx, col, (0.35 - q * 0.06) * k)
                ctx.fill()
            ellipse(ctx, x, y, 36, 36)
            src(ctx, col, k)
            ctx.fill()
            text(ctx, lab, 170, y - 48, 34, col, align="left", alpha=k)
    elif i == 1:   # calendar tile + a model family appearing
        def cal():
            rrect(ctx, -180, -200, 360, 400, 34)
            src(ctx, (1, 1, 1))
            ctx.fill()
            rrect(ctx, -180, -200, 360, 110, 34)
            src(ctx, Y_)
            ctx.fill()
            ctx.rectangle(-180, -130, 360, 40)
            ctx.fill()
            text(ctx, "OCT", 0, -125, 52, K_)
            text(ctx, "12", 0, 110, 190, K_)
        _scaled(ctx, 290, ICON_Y, _pop(lt, 0.2), cal)
        u = _pop(lt, 1.6)

        def family():
            _panel(ctx, -230, -200, 460, 400, 1)
            for r in range(3):   # a stack of model "layers"
                y = -120 + r * 85
                rrect(ctx, -170 + r * 20, y, 340 - r * 40, 60, 16)
                src(ctx, (Y_, TEAL, ORANGE)[r], 0.95)
                ctx.fill()
            text(ctx, "NEW MODELS", 0, 175, 40, Y_)
        _scaled(ctx, 770, ICON_Y, u, family)
        text(ctx, "MUSE WONDER", cx, ICON_Y + 300, 56, (1, 1, 1), alpha=k * ease_out(seg(lt, 2.4, 2.9)))
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
    elif i == 3:   # two model cards, the second one bigger
        def chip(size, col, glow):
            s = size / 2
            for q in range(4):   # pins
                for side in (-1, 1):
                    off = -s * 0.6 + q * s * 0.4
                    ctx.rectangle(off - 8, side * (s + 22) - 14, 16, 28)
                    ctx.rectangle(side * (s + 22) - 14, off - 8, 28, 16)
            src(ctx, GREY)
            ctx.fill()
            rrect(ctx, -s, -s, size, size, 22)
            src(ctx, col)
            ctx.fill()
            rrect(ctx, -s * 0.55, -s * 0.55, size * 0.55, size * 0.55, 14)
            src(ctx, K_, 0.8)
            ctx.fill()
            if glow:
                rrect(ctx, -s - 12, -s - 12, size + 24, size + 24, 30)
                src(ctx, Y_, 0.5 + 0.3 * math.sin(lt * 4))
                ctx.set_line_width(6)
                ctx.stroke()
        _scaled(ctx, 300, ICON_Y - 10, _pop(lt, 1.0), lambda: chip(220, TEAL, False))
        _scaled(ctx, 740, ICON_Y - 30, _pop(lt, 2.3), lambda: chip(320, Y_, True))
        text(ctx, "WONDER", 300, ICON_Y + 210, 48, TEAL, alpha=k * ease_out(seg(lt, 1.2, 1.6)))
        text(ctx, "WONDER FULL", 740, ICON_Y + 250, 48, Y_, alpha=k * ease_out(seg(lt, 2.5, 2.9)))
        text(ctx, "MOST CAPABLE YET", 740, ICON_Y + 310, 34, (1, 1, 1), alpha=k * ease_out(seg(lt, 4.0, 4.4)))
    elif i == 4:   # agent ticking off a task list: personal + work
        _panel(ctx, 140, ICON_Y - 250, 800, 590, k)
        tasks = [("PLAN A TRIP", "HOME"), ("SORT MY INBOX", "WORK"),
                 ("COMPARE PRICES", "HOME"), ("DRAFT A REPORT", "WORK")]
        for j, (lab, tag) in enumerate(tasks):
            y = ICON_Y - 170 + j * 125
            done = ease_back(seg(lt, 0.8 + j * 0.9, 1.1 + j * 0.9))
            rrect(ctx, 190, y - 40, 80, 80, 18)
            src(ctx, (1, 1, 1), 0.9 * k)
            ctx.set_line_width(5)
            ctx.stroke()
            if done > 0.01:
                ctx.save()
                ctx.translate(230, y)
                ctx.scale(done, done)
                ctx.move_to(-24, 0)
                ctx.line_to(-6, 20)
                ctx.line_to(28, -24)
                src(ctx, Y_)
                ctx.set_line_width(12)
                ctx.set_line_cap(cairo.LINE_CAP_ROUND)
                ctx.stroke()
                ctx.restore()
            text(ctx, lab, 300, y + 14, 42, (1, 1, 1), align="left", alpha=k)
            rrect(ctx, 750, y - 26, 150, 52, 26)
            src(ctx, TEAL if tag == "WORK" else ORANGE, k)
            ctx.fill()
            text(ctx, tag, 825, y + 12, 30, K_, alpha=k)
        text(ctx, "AGENT AT WORK", cx, ICON_Y + 300, 40, Y_, alpha=k)
    elif i == 5:   # two price tags, then a locked "Wonder Full" card
        def tag(label, col):
            ctx.move_to(-150, -70)
            ctx.line_to(110, -70)
            ctx.line_to(170, 0)
            ctx.line_to(110, 70)
            ctx.line_to(-150, 70)
            ctx.close_path()
            src(ctx, col)
            ctx.fill()
            ellipse(ctx, 105, 0, 14, 14)
            src(ctx, PANEL)
            ctx.fill()
            text(ctx, label, -30, 26, 72, K_)
        text(ctx, "MUSE APP · PER MONTH", cx, ICON_Y - 210, 40, (1, 1, 1), alpha=k)
        _scaled(ctx, 300, ICON_Y - 90, _pop(lt, 1.5), lambda: tag("$20", Y_))
        _scaled(ctx, 760, ICON_Y - 90, _pop(lt, 2.4), lambda: tag("$100", ORANGE))
        u = _pop(lt, 4.3)

        def locked():
            _panel(ctx, -360, -95, 720, 190, 1)
            # padlock
            ctx.arc(-260, -10, 34, math.pi, 0)
            src(ctx, Y_)
            ctx.set_line_width(12)
            ctx.stroke()
            rrect(ctx, -310, -10, 100, 80, 14)
            ctx.fill()
            text(ctx, "WONDER FULL", 60, -12, 50, Y_)
            text(ctx, "MUSE CODE ONLY", 60, 50, 40, (1, 1, 1))
        _scaled(ctx, cx, ICON_Y + 190, u, locked)
    elif i == 6:   # code window with three equal bars
        _panel(ctx, 140, ICON_Y - 240, 800, 560, k)
        text(ctx, "</>", cx, ICON_Y - 140, 80, Y_, alpha=k)
        rows = [("MUSE WONDER", Y_), ("CHATGPT", TEAL), ("CLAUDE", ORANGE)]
        for j, (lab, col) in enumerate(rows):
            y = ICON_Y - 40 + j * 110
            u = ease_out(seg(lt, 0.3 + j * 0.25, 1.3 + j * 0.25))
            text(ctx, lab, 190, y + 12, 38, (1, 1, 1), align="left", alpha=k)
            rrect(ctx, 580, y - 24, 300 * u, 48, 24)
            src(ctx, col, k)
            ctx.fill()
        text(ctx, "META'S CLAIM", cx, ICON_Y + 290, 40, GREY, alpha=k)
    elif i == 7:   # magnifier over the claim with a question mark
        _panel(ctx, 160, ICON_Y - 200, 760, 300, k)
        text(ctx, "“ON PAR AT CODING”", cx, ICON_Y - 30, 56, (1, 1, 1), alpha=k)
        mx = lerp(300, 760, ease_io(seg(lt, 0.2, 2.2)))
        my = ICON_Y - 40
        ctx.arc(mx, my, 110, 0, 2 * math.pi)
        src(ctx, (1, 1, 1), 0.08)
        ctx.fill_preserve()
        src(ctx, Y_)
        ctx.set_line_width(14)
        ctx.stroke()
        ctx.move_to(mx + 78, my + 78)
        ctx.line_to(mx + 170, my + 170)
        ctx.set_line_width(28)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
        q = _pop(lt, 2.2)
        _scaled(ctx, cx, ICON_Y + 260, q, lambda: (rrect(ctx, -300, -55, 600, 110, 55), src(ctx, ORANGE), ctx.fill(),
                                                   text(ctx, "NOT YET VERIFIED", 0, 18, 50, K_)))


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
