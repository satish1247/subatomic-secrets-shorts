"""2026-10-31 countdown: Google's Suncatcher satellite answers its first AI prompt from orbit (contract: DURATION + render_frame)."""
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
    ("AI IN SPACE", "FIRST ANSWER FROM ORBIT", None),
    ("PROJECT SUNCATCHER", "\"HELLO WORLD\" FROM ORBIT", None),
    ("3 THINGS TO KNOW", "", None),
    ("DATA CENTER IN ORBIT", "LAUNCHED OCT 1 \u2022 4 TPUs", 3),
    ("POWER IS TIGHT", "1 CHIP AT A TIME \u2022 ~20 MIN", 2),
    ("FIRST ANSWER: A POEM", "GEMMA 4 HAIKU \u2022 SVALBARD", 1),
    ("NEXT: 2027", "2 SATELLITES \u2022 LASER LINKS", None),
    ("AI IN ORBIT?", "", None),
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




def _earth(ctx, t, a=1.0, cy=1720, r=900):
    """Big Earth limb at the bottom: ocean gradient, drifting land blobs, thin atmosphere glow."""
    ctx.save()
    ctx.arc(W / 2, cy + r, r, 0, 2 * math.pi)
    ctx.clip()
    g = cairo.LinearGradient(0, cy, 0, cy + 400)
    g.add_color_stop_rgba(0, 0.12, 0.42, 0.70, a)
    g.add_color_stop_rgba(1, 0.03, 0.12, 0.30, a)
    ctx.set_source(g)
    ctx.paint()
    for q in range(6):
        x = ((q * 260 + t * 22) % 1500) - 200
        ellipse(ctx, x, cy + 70 + (q % 3) * 50, 120 + (q % 2) * 60, 34)
        src(ctx, (0.25, 0.55, 0.32), 0.8 * a)
        ctx.fill()
    ctx.restore()
    ctx.arc(W / 2, cy + r, r + 10, math.pi, 2 * math.pi)
    src(ctx, (0.45, 0.80, 1.0), 0.35 * a)
    ctx.set_line_width(14)
    ctx.stroke()


def _stars(ctx, t, a=1.0):
    for q in range(60):
        x = (q * 157) % W
        y = 260 + (q * 89) % 1300
        tw = 0.35 + 0.35 * math.sin(t * 2.2 + q)
        ellipse(ctx, x, y, 2.5, 2.5)
        src(ctx, (1, 1, 1), tw * a)
        ctx.fill()


def _chip(ctx, x, y, s, on=1.0, a=1.0):
    """Generic AI accelerator chip (no logos): square die with pins; 'on' glows yellow."""
    for j in range(4):
        d = -s * 0.3 + j * s * 0.2
        for (px, py, pw, ph) in ((x + d - 4, y - s * 0.62, 8, s * 0.14), (x + d - 4, y + s * 0.48, 8, s * 0.14),
                                 (x - s * 0.62, y + d - 4, s * 0.14, 8), (x + s * 0.48, y + d - 4, s * 0.14, 8)):
            ctx.rectangle(px, py, pw, ph)
    src(ctx, FRAME, a)
    ctx.fill()
    rrect(ctx, x - s / 2, y - s / 2, s, s, s * 0.12)
    src(ctx, PANEL, a)
    ctx.fill_preserve()
    src(ctx, FRAME, a)
    ctx.set_line_width(4)
    ctx.stroke()
    if on > 0.01:
        rrect(ctx, x - s * 0.32, y - s * 0.32, s * 0.64, s * 0.64, s * 0.08)
        src(ctx, Y_, a * on)
        ctx.fill()
    text(ctx, "TPU", x, y + s * 0.11, s * 0.28, K_ if on > 0.5 else GREY, alpha=a)


def _satellite(ctx, x, y, s=1.0, a=1.0, t=0.0, chips_on=0):
    """Fridge-sized box with two solar wings and a small dish."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for side in (-1, 1):   # solar wings
        ctx.move_to(side * 70, 0)
        ctx.line_to(side * 110, 0)
        src(ctx, FRAME, a)
        ctx.set_line_width(8)
        ctx.stroke()
        bx = 110 if side > 0 else -330
        rrect(ctx, bx, -70, 220, 140, 10)
        g = cairo.LinearGradient(bx, -70, bx + 220, 70)
        g.add_color_stop_rgba(0, 0.10, 0.22, 0.55, a)
        g.add_color_stop_rgba(1, 0.16, 0.38, 0.75, a)
        ctx.set_source(g)
        ctx.fill_preserve()
        src(ctx, FRAME, a)
        ctx.set_line_width(4)
        ctx.stroke()
        for c in range(1, 4):
            ctx.move_to(bx + c * 55, -70)
            ctx.line_to(bx + c * 55, 70)
        ctx.move_to(bx, 0)
        ctx.line_to(bx + 220, 0)
        src(ctx, (1, 1, 1), 0.25 * a)
        ctx.set_line_width(2)
        ctx.stroke()
        glint = 0.5 + 0.5 * math.sin(t * 1.7 + side)
        rrect(ctx, bx + 10, -62, 60, 124, 8)
        src(ctx, (1, 1, 1), 0.10 * glint * a)
        ctx.fill()
    rrect(ctx, -70, -95, 140, 190, 16)   # body
    src(ctx, (0.85, 0.72, 0.30), a)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.set_line_width(4)
    ctx.stroke()
    for j in range(4):   # 4 chip lights on the body
        lx, ly = -30 + (j % 2) * 60, -40 + (j // 2) * 60
        rrect(ctx, lx - 20, ly - 20, 40, 40, 6)
        src(ctx, Y_ if j < chips_on else PANEL, a)
        ctx.fill()
    ctx.move_to(0, 95)   # dish
    ctx.line_to(0, 125)
    src(ctx, FRAME, a)
    ctx.set_line_width(6)
    ctx.stroke()
    ctx.arc(0, 150, 32, math.pi * 1.1, math.pi * 1.9)
    ctx.set_line_width(8)
    ctx.stroke()
    ctx.restore()


def _bubble(ctx, x, y, w, h, label, col, a=1.0, tail_up=False, size=40):
    rrect(ctx, x - w / 2, y - h / 2, w, h, 26)
    src(ctx, col, a)
    ctx.fill()
    ty = y - h / 2 if tail_up else y + h / 2
    d = -1 if tail_up else 1
    ctx.move_to(x - 24, ty)
    ctx.line_to(x, ty + 30 * d)
    ctx.line_to(x + 24, ty)
    ctx.close_path()
    ctx.fill()
    text(ctx, label, x, y + size * 0.36, size, K_, alpha=a)


def _beam(ctx, x0, y0, x1, y1, u, col, a=1.0, dash=True):
    if u <= 0:
        return
    ctx.move_to(x0, y0)
    ctx.line_to(lerp(x0, x1, u), lerp(y0, y1, u))
    if dash:
        ctx.set_dash([18, 12], -40 * u)
    src(ctx, col, a)
    ctx.set_line_width(7)
    ctx.stroke()
    ctx.set_dash([])


def _dish(ctx, x, y, a=1.0):
    """Ground station dish."""
    ctx.move_to(x - 40, y + 60)
    ctx.line_to(x, y)
    ctx.line_to(x + 40, y + 60)
    src(ctx, FRAME, a)
    ctx.set_line_width(8)
    ctx.stroke()
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(-0.5)
    ctx.arc(0, 0, 70, math.pi * 1.05, math.pi * 1.95)
    ctx.close_path()
    src(ctx, (1, 1, 1), a)
    ctx.fill()
    ctx.restore()


def _icon(ctx, i, t, k):
    t0 = _card_start(i)
    lt = t - t0
    cx = W / 2
    if i == 0:   # satellite over Earth, beam down, reply up
        _earth(ctx, t, k, cy=1330, r=1100)
        sx = cx + 120 * math.sin(t * 0.4)
        _satellite(ctx, sx, ICON_Y - 80, 0.9 * _pop(lt, 0.1), k, t, chips_on=1)
        u = seg(lt, 0.9, 1.8)
        _beam(ctx, sx, ICON_Y + 60, cx - 60, 1330, ease_out(u), Y_, k)
        f = 0.5 + 0.5 * math.sin(t * 8)
        if lt > 1.8:
            text(ctx, "AI", sx, ICON_Y - 210, 60, Y_, alpha=k * (0.6 + 0.4 * f))
    elif i == 1:   # prompt goes up, reply comes down
        _earth(ctx, t, k, cy=1360, r=1100)
        _satellite(ctx, cx + 180, ICON_Y - 170, 0.7, k, t, chips_on=1)
        _dish(ctx, cx - 250, 1270, k)
        u1 = ease_out(seg(lt, 0.3, 1.6))
        _beam(ctx, cx - 230, 1260, cx + 150, ICON_Y - 80, u1, TEAL, k)
        a1 = k * ease_out(seg(lt, 0.6, 1.0))
        _bubble(ctx, cx - 260, ICON_Y + 30, 300, 90, "PROMPT ↑", TEAL, a1, size=40)
        u2 = ease_out(seg(lt, 2.6, 3.8))
        _beam(ctx, cx + 200, ICON_Y - 60, cx - 200, 1250, u2, Y_, k)
        a2 = k * ease_out(seg(lt, 3.4, 3.8))
        _bubble(ctx, cx + 200, ICON_Y + 120, 300, 90, "REPLY ↓", Y_, a2, tail_up=True, size=40)
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
    elif i == 3:   # calendar OCT 1 + rocket streak, then satellite with 4 chips lighting up
        a1 = k * (1 - seg(lt, 3.0, 3.4))
        if a1 > 0.01:
            ctx.save()
            ctx.translate(320, ICON_Y)
            ctx.scale(_pop(lt, 0.2) * 0.85, _pop(lt, 0.2) * 0.85)
            rrect(ctx, -170, -190, 340, 380, 34)
            src(ctx, (1, 1, 1), a1)
            ctx.fill()
            rrect(ctx, -170, -190, 340, 105, 34)
            src(ctx, Y_, a1)
            ctx.fill()
            ctx.rectangle(-170, -120, 340, 35)
            ctx.fill()
            text(ctx, "OCT", 0, -118, 50, K_, alpha=a1)
            text(ctx, "1", 0, 105, 170, K_, alpha=a1)
            ctx.restore()
            ru = ease_in(seg(lt, 1.0, 2.6))   # rising rocket (generic)
            ry = lerp(ICON_Y + 120, ICON_Y - 160, ru)
            rx = 760
            a1r = a1 * seg(lt, 0.8, 1.0) * (1 - seg(lt, 2.3, 2.6))
            ctx.move_to(rx, ry - 70)
            ctx.line_to(rx + 26, ry - 20)
            ctx.line_to(rx + 26, ry + 70)
            ctx.line_to(rx - 26, ry + 70)
            ctx.line_to(rx - 26, ry - 20)
            ctx.close_path()
            src(ctx, (1, 1, 1), a1r)
            ctx.fill()
            fl = 0.7 + 0.3 * math.sin(t * 30)
            ctx.move_to(rx - 20, ry + 70)
            ctx.line_to(rx, ry + 70 + 90 * fl)
            ctx.line_to(rx + 20, ry + 70)
            ctx.close_path()
            src(ctx, ORANGE, a1r)
            ctx.fill()
            _button(ctx, 760, ICON_Y + 290, 400, 80, "RIDESHARE", col=TEAL, a=a1 * ease_out(seg(lt, 1.2, 1.6)), size=38)
        a2 = k * seg(lt, 3.2, 3.6)
        if a2 > 0.01:
            on = int(min(4, max(0, (lt - 3.8) / 0.4 + 1))) if lt > 3.8 else 0
            _satellite(ctx, cx, ICON_Y - 60, 1.0, a2, t, chips_on=on)
            for j in range(4):
                xx = cx - 330 + j * 220
                u = ease_back(seg(lt, 3.8 + 0.4 * j, 4.2 + 0.4 * j))
                if u > 0.01:
                    ctx.save()
                    ctx.translate(xx, ICON_Y + 210)
                    ctx.scale(u, u)
                    _chip(ctx, 0, 0, 120, 1.0, a2)
                    ctx.restore()
            _button(ctx, cx, ICON_Y + 345, 480, 76, "BUILT WITH PLANET", a=a2 * ease_out(seg(lt, 5.6, 6.0)), size=36)
    elif i == 4:   # 4 chips, only one on; battery + 20 min timer
        for j in range(4):
            xx = cx - 330 + j * 220
            on = 1.0 if j == 0 else 0.0
            _chip(ctx, xx, ICON_Y - 120, 140, on, k * (1.0 if j == 0 else 0.55))
            if j > 0 and lt > 1.2:
                ctx.move_to(xx - 60, ICON_Y - 190)
                ctx.line_to(xx + 60, ICON_Y - 50)
                src(ctx, RED, k * ease_out(seg(lt, 1.2 + 0.15 * j, 1.5 + 0.15 * j)))
                ctx.set_line_width(12)
                ctx.set_line_cap(cairo.LINE_CAP_ROUND)
                ctx.stroke()
                ctx.set_line_cap(cairo.LINE_CAP_BUTT)
        tu = _pop(lt, 2.0)

        def timer():
            ctx.arc(0, 0, 140, 0, 2 * math.pi)
            src(ctx, PANEL)
            ctx.fill_preserve()
            src(ctx, (1, 1, 1))
            ctx.set_line_width(8)
            ctx.stroke()
            sweep = 2 * math.pi * ease_out(seg(lt, 2.3, 4.2))
            ctx.move_to(0, 0)
            ctx.arc(0, 0, 120, -math.pi / 2, -math.pi / 2 + sweep)
            ctx.close_path()
            src(ctx, Y_, 0.85)
            ctx.fill()
        _scaled(ctx, 330, ICON_Y + 150, tu, timer)
        text(ctx, "~20 MIN", 330, ICON_Y + 350, 46, (1, 1, 1), alpha=k * seg(lt, 2.2, 2.6))

        def battery():
            rrect(ctx, -110, -60, 220, 120, 16)
            src(ctx, (1, 1, 1))
            ctx.set_line_width(8)
            ctx.stroke()
            rrect(ctx, 112, -22, 20, 44, 6)
            ctx.fill()
            lvl = 1 - 0.75 * seg(lt, 2.3, 4.2)
            rrect(ctx, -96, -46, 192 * lvl, 92, 8)
            src(ctx, ORANGE if lvl < 0.5 else TEAL)
            ctx.fill()
        _scaled(ctx, 760, ICON_Y + 150, _pop(lt, 2.2), battery)
        text(ctx, "SOLAR POWER", 760, ICON_Y + 350, 40, (1, 1, 1), alpha=k * seg(lt, 2.4, 2.8))
    elif i == 5:   # prompt card -> haiku card (placeholder lines) -> Svalbard ground pass
        _earth(ctx, t, k, cy=1360, r=1100)
        fade = 1 - seg(lt, 4.3, 4.7)
        a1 = k * ease_out(seg(lt, 0.3, 0.7)) * fade
        if a1 > 0.01:
            _panel(ctx, 140, 850, 800, 110, a1)
            text(ctx, "\"WRITE A HAIKU ABOUT SPACE\"", cx, 920, 40, (1, 1, 1), alpha=a1)
        a2 = k * ease_out(seg(lt, 2.0, 2.4)) * fade
        if a2 > 0.01:
            _panel(ctx, 240, 1000, 600, 240, a2, edge=Y_)
            text(ctx, "HAIKU", cx, 1060, 44, Y_, alpha=a2)
            for j, frac in enumerate((0.55, 0.85, 0.55)):   # 5-7-5 shaped lines
                f = ease_out(seg(lt, 2.4 + 0.5 * j, 2.9 + 0.5 * j))
                lw = 460 * frac * f
                if lw > 1:
                    rrect(ctx, cx - lw / 2, 1100 + j * 46, lw, 20, 10)
                    src(ctx, (1, 1, 1), 0.8 * a2)
                    ctx.fill()
        a3 = k * ease_out(seg(lt, 4.5, 4.9))
        if a3 > 0.01:
            _satellite(ctx, cx + 230, 1010, 0.6, a3, t, chips_on=1)
            _dish(ctx, cx - 280, 1290, a3)
            _beam(ctx, cx + 230, 1090, cx - 260, 1280, ease_out(seg(lt, 4.9, 5.8)), Y_, a3)
            _button(ctx, cx - 140, 870, 500, 80, "SVALBARD, NORWAY", col=TEAL, a=a3, size=36)
    elif i == 6:   # two satellites, laser link
        _stars(ctx, t, k)
        u = ease_out(seg(lt, 0.2, 1.0))
        _satellite(ctx, lerp(cx, 260, u), ICON_Y - 40, 0.55, k, t, chips_on=4)
        _satellite(ctx, lerp(cx, 820, u), ICON_Y + 120, 0.55, k * u, t, chips_on=4)
        lu = seg(lt, 1.4, 2.0)
        if lu > 0:
            x0, y0, x1, y1 = 330, ICON_Y - 30, 750, ICON_Y + 110
            ctx.move_to(x0, y0)
            ctx.line_to(lerp(x0, x1, lu), lerp(y0, y1, lu))
            src(ctx, RED, k * (0.75 + 0.25 * math.sin(t * 20)))
            ctx.set_line_width(8)
            ctx.stroke()
            src(ctx, (1, 0.6, 0.6), k * 0.25)
            ctx.set_line_width(22)
            ctx.move_to(x0, y0)
            ctx.line_to(lerp(x0, x1, lu), lerp(y0, y1, lu))
            ctx.stroke()
        _button(ctx, cx, ICON_Y + 340, 360, 84, "LASER LINK", col=RED, a=k * ease_out(seg(lt, 2.0, 2.4)), size=42)
    elif i == 7:   # satellite circling Earth + question mark
        _earth(ctx, t, k, cy=1330, r=1100)
        ang = lt * 0.9
        _satellite(ctx, cx + 260 * math.cos(ang), ICON_Y - 20 + 60 * math.sin(ang), 0.6, k, t, chips_on=1)
        q = _pop(lt, 0.3)
        _scaled(ctx, cx, ICON_Y - 300, q, lambda: text(ctx, "?", 0, 50, 160, Y_))


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

