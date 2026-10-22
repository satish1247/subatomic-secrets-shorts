"""2026-10-22 countdown: Nvidia + Agile Robots unveil the Agile ONE SN reference humanoid (contract: DURATION + render_frame)."""
import json
import math
import os
import cairo
from gfx import limb, FONT, W, H, ease_back, ease_out, ease_io, ease_in, seg, src, text, ellipse, rrect, lerp, wrap
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
    ("NEW HUMANOID", "BUILT FOR ROBOT LABS", None),
    ("AGILE ONE SN", "NVIDIA + AGILE ROBOTS", None),
    ("3 THINGS TO KNOW", "", None),
    ("COMPACT", "ABOUT 1.4 M TALL", 3),
    ("SMART HANDS", "20 DEGREES OF FREEDOM EACH", 2),
    ("READY TO LEARN", "GR00T AI + JETSON THOR", 1),
    ("WEEKS \u2192 DAYS", "NVIDIA'S CLAIM", None),
    ("1,000\u20132,000", "HUMANOIDS PLANNED", None),
]
STEEL_L = (0.80, 0.85, 0.89)
STEEL = (0.45, 0.52, 0.58)
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


def _robot(ctx, x, y, hpx, t, wave=0.0, a=1.0):
    """Generic humanoid (no real branding): feet at (x, y), hpx pixels tall."""
    s = hpx / 560.0
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.push_group()
    bob = 4 * math.sin(t * 2.4)
    for side in (-1, 1):   # legs + feet
        limb(ctx, [(side * 36, -210), (side * 42, -105), (side * 40, -12)], 44, STEEL, 5, K_)
        rrect(ctx, side * 40 - 34, -24, 68, 26, 12)
        src(ctx, STEEL_L)
        ctx.fill_preserve()
        src(ctx, K_)
        ctx.set_line_width(5)
        ctx.stroke()
    ctx.translate(0, bob)
    rrect(ctx, -64, -250, 128, 60, 22)   # pelvis
    src(ctx, STEEL)
    ctx.fill_preserve()
    src(ctx, K_)
    ctx.set_line_width(5)
    ctx.stroke()
    # left arm hangs, right arm waves
    limb(ctx, [(-96, -415), (-124, -325), (-118, -238)], 34, STEEL, 5, K_)
    ang = wave * (0.5 + 0.35 * math.sin(t * 7))
    ex, ey = 126 + 30 * wave, -325 - 120 * wave
    hx, hy = ex + 10 + 60 * math.sin(ang) * wave, ey - 95 * wave + 87 * (1 - wave)
    limb(ctx, [(96, -415), (ex, ey), (hx, hy)], 34, STEEL, 5, K_)
    for (px, py) in ((-118, -232), (hx, hy)):
        ellipse(ctx, px, py, 24, 24)
        src(ctx, STEEL_L)
        ctx.fill_preserve()
        src(ctx, K_)
        ctx.stroke()
    rrect(ctx, -86, -450, 172, 210, 34)   # torso
    src(ctx, (0.93, 0.95, 0.97))
    ctx.fill_preserve()
    src(ctx, K_)
    ctx.stroke()
    ellipse(ctx, 0, -360, 26, 26)
    src(ctx, Y_, 0.75 + 0.25 * math.sin(t * 3))
    ctx.fill()
    ctx.rectangle(-16, -470, 32, 24)   # neck
    src(ctx, STEEL)
    ctx.fill()
    rrect(ctx, -60, -566, 120, 104, 34)   # head
    src(ctx, (0.93, 0.95, 0.97))
    ctx.fill_preserve()
    src(ctx, K_)
    ctx.stroke()
    rrect(ctx, -46, -536, 92, 40, 20)   # visor
    src(ctx, K_)
    ctx.fill()
    blink = 0.15 if (t % 3.1) < 0.12 else 1.0
    for ex_ in (-20, 20):
        ellipse(ctx, ex_, -516, 9, 9 * blink)
        src(ctx, Y_)
        ctx.fill()
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(a)
    ctx.restore()


def _person(ctx, x, y, hpx, a):
    """Neutral grey human silhouette for scale."""
    s = hpx / 560.0
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ellipse(ctx, 0, -500, 52, 60)
    rrect(ctx, -82, -430, 164, 230, 60)
    for side in (-1, 1):
        rrect(ctx, side * 44 - 30, -230, 60, 230, 28)
        rrect(ctx, side * 100 - 22, -420, 44, 200, 22)
    src(ctx, GREY, 0.55 * a)
    ctx.fill()
    ctx.restore()


def _hand(ctx, x, y, t, k):
    """Big five-finger robot hand with joint dots that flex."""
    ctx.save()
    ctx.translate(x, y)
    rrect(ctx, -150, -40, 300, 200, 50)
    src(ctx, STEEL_L, k)
    ctx.fill_preserve()
    src(ctx, K_, k)
    ctx.set_line_width(6)
    ctx.stroke()
    fingers = [(-150, 90, 150, -1.05), (-100, -40, 200, -0.08), (-33, -40, 230, -0.02),
               (35, -40, 215, 0.03), (102, -40, 180, 0.09)]
    for j, (fx, fy, ln, base) in enumerate(fingers):
        flex = 0.07 * (0.5 + 0.5 * math.sin(t * 3 + j * 0.7))
        pts, px, py, ang = [(fx, fy)], fx, fy, base
        for q in range(3):
            ang += -flex if j == 0 else flex
            px += math.sin(ang) * ln / 3
            py -= math.cos(ang) * ln / 3
            pts.append((px, py))
        limb(ctx, pts, 46, STEEL, 6, K_)
        for (qx, qy) in pts[1:]:
            ellipse(ctx, qx, qy, 10, 10)
            src(ctx, Y_, k)
            ctx.fill()
        if j == 1:   # touch ripples from the middle fingertip
            for r in range(3):
                ph = (t * 0.9 + r / 3.0) % 1.0
                ctx.arc(px, py, 30 + 120 * ph, 0, 2 * math.pi)
                src(ctx, TEAL, (1 - ph) * 0.8 * k)
                ctx.set_line_width(6)
                ctx.stroke()
    ctx.restore()


def _chip(ctx, label, col):
    for q in range(4):
        for side in (-1, 1):
            off = -66 + q * 44
            ctx.rectangle(off - 8, side * 132 - 14, 16, 28)
            ctx.rectangle(side * 132 - 14, off - 8, 28, 16)
    src(ctx, GREY)
    ctx.fill()
    rrect(ctx, -110, -110, 220, 220, 24)
    src(ctx, col)
    ctx.fill()
    rrect(ctx, -70, -70, 140, 140, 16)
    src(ctx, K_, 0.85)
    ctx.fill()
    text(ctx, label, 0, 11, 30, col)


def _icon(ctx, i, t, k):
    t0 = _card_start(i)
    lt = t - t0
    cx = W / 2
    if i == 0:   # robot waving in a lab
        _panel(ctx, 100, ICON_Y - 270, 880, 610, k)
        for q in range(7):   # floor grid
            yy = ICON_Y + 210 + q * 18
            ctx.move_to(120, yy)
            ctx.line_to(960, yy)
        src(ctx, TEAL, 0.25 * k)
        ctx.set_line_width(2)
        ctx.stroke()
        text(ctx, "ROBOT LAB", 140, ICON_Y - 210, 34, GREY, align="left", alpha=k)
        u = ease_back(seg(lt, 0.2, 0.7))
        _robot(ctx, cx, ICON_Y + 300, 520 * max(u, 0.01), t, wave=ease_out(seg(lt, 0.8, 1.3)), a=k)
        for q in range(4):   # sparkles
            ph = (t * 0.7 + q * 0.25) % 1.0
            sx, sy = (250, 820, 300, 760)[q], ICON_Y - 150 + q * 90
            r = 16 * math.sin(ph * math.pi)
            ctx.move_to(sx - r, sy)
            ctx.line_to(sx + r, sy)
            ctx.move_to(sx, sy - r)
            ctx.line_to(sx, sy + r)
            src(ctx, Y_, k)
            ctx.set_line_width(5)
            ctx.stroke()
    elif i == 1:   # calendar Oct 21 + Berlin pin
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
            text(ctx, "21", 0, 110, 190, K_)
        _scaled(ctx, 290, ICON_Y, _pop(lt, 0.2), cal)

        def place():
            _panel(ctx, -230, -200, 460, 400, 1)
            ctx.save()
            ctx.translate(0, 40)
            ctx.scale(1.6, 1.6)
            _pin(ctx, Y_)
            ctx.restore()
            text(ctx, "BERLIN", 0, 140, 56, (1, 1, 1))
        _scaled(ctx, 770, ICON_Y, _pop(lt, 1.4), place)
        u = ease_out(seg(lt, 2.6, 3.1))
        _button(ctx, cx, ICON_Y + 300, 560, 90, "GTC BERLIN 2026", a=k * u, size=44)
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
    elif i == 3:   # height comparison with a ruler
        g = ICON_Y + 320
        ppm = 300   # pixels per metre
        ctx.move_to(130, g)
        ctx.line_to(950, g)
        src(ctx, (1, 1, 1), 0.5 * k)
        ctx.set_line_width(4)
        ctx.stroke()
        for m in range(3):   # ruler ticks 0..2 m
            for q in range(10):
                yy = g - (m + q / 10.0) * ppm
                if yy < ICON_Y - 200:
                    continue
                ctx.move_to(150, yy)
                ctx.line_to(150 + (40 if q == 0 else 20), yy)
            if g - m * ppm > ICON_Y - 180:
                text(ctx, "%d M" % m, 200, g - m * ppm + 12, 32, GREY, align="left", alpha=k)
        src(ctx, (1, 1, 1), 0.6 * k)
        ctx.set_line_width(3)
        ctx.stroke()
        _person(ctx, 760, g, 1.75 * ppm * 0.98, k)
        grow = ease_out(seg(lt, 0.8, 2.0))
        _robot(ctx, 470, g, max(1.40 * ppm * grow, 1), t, a=k)
        if grow > 0.98:
            yy = g - 1.40 * ppm
            ctx.move_to(300, yy)
            ctx.line_to(640, yy)
            ctx.set_dash([14, 10])
            src(ctx, Y_, k)
            ctx.set_line_width(5)
            ctx.stroke()
            ctx.set_dash([])
            _button(ctx, 470, yy - 50, 200, 64, "1.4 M", a=k * ease_out(seg(lt, 2.0, 2.4)), size=38)
    elif i == 4:   # robot hand with chips for each fact
        _panel(ctx, 100, ICON_Y - 200, 880, 590, k)
        _hand(ctx, 400, ICON_Y + 170, t, k)
        tags = [("20 DoF", Y_, 1.2), ("1,000\u00d7/S", TEAL, 2.6), ("TOUCH", ORANGE, 4.0)]
        for j, (lab, col, at) in enumerate(tags):
            u = _pop(lt, at)
            _scaled(ctx, 790, ICON_Y - 70 + j * 150, u,
                    lambda lab=lab, col=col: _button(ctx, 0, 0, 290, 96, lab, col=col, size=44))
    elif i == 5:   # AI + computer flow into the robot
        _robot(ctx, 790, ICON_Y + 320, 520, t, a=k)
        items = [("THOR", Y_, ICON_Y - 40, 0.8), ("GR00T", TEAL, ICON_Y + 230, 2.2)]
        for lab, col, yy, at in items:
            u = _pop(lt, at)
            _scaled(ctx, 300, yy, u * 0.72, lambda lab=lab, col=col: _chip(ctx, lab, col))
            f = seg(lt, at + 0.5, at + 1.5)
            if f > 0:
                ctx.move_to(400, yy)
                ctx.line_to(lerp(400, 700, f), lerp(yy, ICON_Y + 10, f))
                ctx.set_dash([18, 12], -t * 60)
                src(ctx, col, k)
                ctx.set_line_width(8)
                ctx.stroke()
                ctx.set_dash([])
        text(ctx, "JETSON THOR COMPUTER", 300, ICON_Y + 100, 30, (1, 1, 1), alpha=k * ease_out(seg(lt, 1.2, 1.6)))
        text(ctx, "GR00T ROBOT AI", 300, ICON_Y + 370, 30, (1, 1, 1), alpha=k * ease_out(seg(lt, 2.6, 3.0)))
    elif i == 6:   # setup time bar shrinks: weeks -> days
        _panel(ctx, 100, ICON_Y - 230, 880, 520, k)
        text(ctx, "LAB SETUP TIME", cx, ICON_Y - 150, 44, (1, 1, 1), alpha=k)
        text(ctx, "BEFORE", 150, ICON_Y - 50, 34, GREY, align="left", alpha=k)
        rrect(ctx, 150, ICON_Y - 20, 780, 80, 40)
        src(ctx, ORANGE, k)
        ctx.fill()
        text(ctx, "WEEKS", 540, ICON_Y + 36, 48, K_, alpha=k)
        u = ease_out(seg(lt, 0.6, 1.8))
        text(ctx, "WITH THIS KIT", 150, ICON_Y + 120, 34, GREY, align="left", alpha=k)
        wbar = lerp(780, 220, u)
        rrect(ctx, 150, ICON_Y + 150, wbar, 80, 40)
        src(ctx, Y_, k)
        ctx.fill()
        text(ctx, "DAYS" if u > 0.6 else "WEEKS", 150 + wbar / 2, ICON_Y + 206, 48, K_, alpha=k)
    elif i == 7:   # rows of robots popping in + date badge
        n = 0
        for r in range(2):
            for c in range(5):
                u = ease_back(seg(lt, 0.3 + n * 0.18, 0.6 + n * 0.18))
                if u > 0.01:
                    _robot(ctx, 170 + c * 185, ICON_Y - 20 + r * 280, 240 * u, t + n, a=k)
                n += 1
        u = _pop(lt, 2.8)
        _scaled(ctx, cx, ICON_Y + 330, u, lambda: _button(ctx, 0, 0, 520, 100, "DUE EARLY 2027", col=Y_, size=50))


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
