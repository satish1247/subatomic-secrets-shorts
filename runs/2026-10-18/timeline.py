"""2026-10-18 cosmic: astronomers identify the first known green star (WD J1330+6435) (contract: DURATION + render_frame)."""
import json
import math
import os
import cairo
from gfx import W, H, ease_back, ease_out, ease_io, ease_in, seg, src, text, ellipse, rrect, lerp, wrap
import brand
import gfx
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
WH = (1, 1, 1)
TEAL = (0.14, 0.60, 0.62)
ORANGE = (0.96, 0.55, 0.18)
RED = (0.90, 0.20, 0.20)
CYAN = (0.45, 0.85, 1.0)
ICE = (0.80, 0.92, 1.0)
BLUE = (0.35, 0.65, 1.0)
GOLD = (0.95, 0.75, 0.25)
RUST = (0.78, 0.36, 0.18)
SAND = (0.86, 0.52, 0.30)
DUST = (0.55, 0.24, 0.12)
GREEN = (0.62, 0.95, 0.30)
PINK = (1.0, 0.55, 0.62)
SUNC = (1.0, 0.92, 0.70)
# (white lead-in, yellow keyword)
HEADS = [
    ("ASTRONOMERS SAY", "FIRST GREEN STAR"),
    ("WHY NO GREEN STARS?", "ALL COLOURS = WHITE"),
    ("A DEAD STAR'S CORE", "WD J1330+6435"),
    ("THE SECRET", "PLANET DEBRIS"),
    ("SODIUM FILTER", "CHARTREUSE GREEN"),
    ("NOT SEEN BY EYE", "MODELLED COLOUR"),
    ("BONUS FIND", "REDDEST STAR?"),
    ("ROUGHLY", "1 IN 30"),
]
VIS_Y = 1010
CAP_SIZE = 62


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


def _scene_start(i):
    return 0.0 if i == 0 else LINES[i]["start"] - 0.3


# ------------------------------------------------------------------ background
STARS = [((i * 173.3) % W, (i * 311.7 + (i % 7) * 53) % H, i % 3) for i in range(160)]


def _background(ctx, t):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.02, 0.03, 0.10)
    g.add_color_stop_rgb(0.6, 0.03, 0.05, 0.16)
    g.add_color_stop_rgb(1, 0.0, 0.0, 0.02)
    ctx.set_source(g)
    ctx.paint()
    # faint nebula glow
    for cx, cy, r, c in ((260, 700, 520, (0.35, 0.15, 0.55)), (850, 1300, 600, (0.10, 0.30, 0.55))):
        ng = cairo.RadialGradient(cx, cy, 0, cx, cy, r)
        ng.add_color_stop_rgba(0, c[0], c[1], c[2], 0.22)
        ng.add_color_stop_rgba(1, c[0], c[1], c[2], 0)
        ctx.set_source(ng)
        ctx.paint()
    # three parallax layers drifting slowly
    for i, (x, y, layer) in enumerate(STARS):
        sp = (4, 10, 20)[layer]
        xx = (x - t * sp) % W
        yy = (y + t * sp * 0.3) % H
        r = (1.2, 2.0, 3.0)[layer]
        ellipse(ctx, xx, yy, r, r)
        src(ctx, WH, 0.35 + 0.3 * math.sin(t * 1.7 + i) * (layer == 2) + 0.15 * layer)
        ctx.fill()


# ------------------------------------------------------------------ props
def _glow(ctx, x, y, r, c, a=1.0):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, c[0], c[1], c[2], a)
    g.add_color_stop_rgba(1, c[0], c[1], c[2], 0)
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()


def _star(ctx, x, y, r, c, t=0.0, rays=True):
    """Glowing star: halo, soft rays, bright core tinted c."""
    _glow(ctx, x, y, r * 3.2, c, 0.28)
    _glow(ctx, x, y, r * 1.9, c, 0.55)
    if rays:
        for q in range(8):
            a = q * math.pi / 4 + t * 0.15
            ln = r * (2.4 if q % 2 == 0 else 1.6) * (1 + 0.06 * math.sin(t * 3 + q))
            ctx.move_to(x + r * 0.6 * math.cos(a), y + r * 0.6 * math.sin(a))
            ctx.line_to(x + ln * math.cos(a), y + ln * math.sin(a))
            src(ctx, c, 0.45)
            ctx.set_line_width(max(2, r * 0.07))
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.stroke()
    g = cairo.RadialGradient(x - r * 0.25, y - r * 0.25, r * 0.05, x, y, r)
    g.add_color_stop_rgb(0, 1, 1, 1)
    g.add_color_stop_rgb(0.55, *[0.5 + 0.5 * v for v in c])
    g.add_color_stop_rgb(1, *c)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()


SPEC = [(0.55, 0.20, 0.95), (0.25, 0.40, 1.0), (0.20, 0.80, 0.95), (0.35, 0.90, 0.35),
        (1.0, 0.92, 0.20), (1.0, 0.60, 0.15), (0.95, 0.20, 0.18)]
SPEC_NAMES = ["VIOLET", "BLUE", "CYAN", "GREEN", "YELLOW", "ORANGE", "RED"]


def _spectrum(ctx, x0, y, w, h, dim=None, a=1.0):
    """Seven colour bands; dim maps band index -> darkening 0..1."""
    bw = w / len(SPEC)
    for q, c in enumerate(SPEC):
        rrect(ctx, x0 + q * bw + 3, y, bw - 6, h, 10)
        src(ctx, c, a)
        ctx.fill()
        d = (dim or {}).get(q, 0)
        if d > 0:
            rrect(ctx, x0 + q * bw + 3, y, bw - 6, h, 10)
            src(ctx, (0.02, 0.02, 0.06), 0.85 * d * a)
            ctx.fill()


def _chip(ctx, sym, name, x, y, c, a):
    if a <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(a, a)
    rrect(ctx, -85, -85, 170, 170, 26)
    src(ctx, K_, 0.9)
    ctx.fill_preserve()
    src(ctx, c)
    ctx.set_line_width(6)
    ctx.stroke()
    text(ctx, sym, 0, 18, 84, c)
    text(ctx, name, 0, 66, 26, WH)
    ctx.restore()


def _pill(ctx, s, x, y, size, fg, bg, a=1.0, pad=36):
    ctx.select_font_face(gfx.FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    w = ctx.text_extents(s).x_advance + pad * 2
    rrect(ctx, x - w / 2, y - size * 0.95, w, size * 1.45, size * 0.5)
    src(ctx, bg, 0.9 * a)
    ctx.fill()
    text(ctx, s, x, y, size, fg, alpha=a)


def _rock(ctx, x, y, s, rot):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.move_to(-20 * s, -8 * s)
    for px, py in ((-6, -20), (16, -14), (22, 4), (8, 18), (-14, 16), (-22, 2)):
        ctx.line_to(px * s, py * s)
    ctx.close_path()
    src(ctx, (0.55, 0.45, 0.38))
    ctx.fill_preserve()
    src(ctx, (0.30, 0.24, 0.20))
    ctx.set_line_width(2)
    ctx.stroke()
    ctx.restore()


def _eye(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-110, 0)
    ctx.curve_to(-50, -70, 50, -70, 110, 0)
    ctx.curve_to(50, 70, -50, 70, -110, 0)
    src(ctx, WH, a)
    ctx.fill()
    ellipse(ctx, 0, 0, 42, 42)
    src(ctx, GREEN, a)
    ctx.fill()
    ellipse(ctx, 0, 0, 18, 18)
    src(ctx, K_, a)
    ctx.fill()
    ctx.restore()


# ------------------------------------------------------------------ scenes
def _scene(ctx, i, t, k):
    lt = t - _scene_start(i)
    cx, cy = W / 2, VIS_Y
    if i == 0:   # a plain white star field, then one star bursts green
        for q, (x, y) in enumerate(((220, 760), (860, 820), (300, 1250), (820, 1280), (170, 1020), (930, 1080))):
            _star(ctx, x, y, 16, WH, t, rays=False)
        u = ease_back(seg(lt, 0.2, 0.9))
        if u > 0.01:
            _star(ctx, cx, cy, 120 * u, GREEN, t)
        a = ease_back(seg(lt, 1.6, 2.1))
        if a > 0.01:
            _pill(ctx, "FIRST KNOWN", cx, cy + 270, 50, K_, Y_, a)
    elif i == 1:   # spectrum bands fly into one white star; Sun peaks blue-green
        x0, w = 110, W - 220
        u = ease_io(seg(lt, 2.2, 3.8))
        bw = w / len(SPEC)
        for q, c in enumerate(SPEC):
            bx = lerp(x0 + q * bw + 3, cx - 20, u)
            by = lerp(cy - 300, cy + 60, u)
            rrect(ctx, bx, by, lerp(bw - 6, 40, u), lerp(110, 40, u), 10)
            src(ctx, c, 1 - 0.8 * u)
            ctx.fill()
            text(ctx, SPEC_NAMES[q][:3], x0 + q * bw + bw / 2, cy - 140, 30, WH, alpha=1 - u)
        # peak marker on blue-green
        pk = ease_out(seg(lt, 0.8, 1.4)) * (1 - u)
        if pk > 0.01:
            mx = x0 + 2.6 * bw
            ctx.move_to(mx, cy - 330)
            ctx.line_to(mx - 22, cy - 370)
            ctx.line_to(mx + 22, cy - 370)
            ctx.close_path()
            src(ctx, Y_, pk)
            ctx.fill()
            text(ctx, "SUN'S PEAK", mx, cy - 390, 36, Y_, alpha=pk)
        s = ease_out(seg(lt, 3.4, 4.2))
        if s > 0.01:
            _star(ctx, cx, cy + 80, 110 * s, SUNC, t)
            _pill(ctx, "= WHITE", cx, cy + 290, 52, K_, Y_, s)
    elif i == 2:   # big star collapses into a tiny dense white dwarf
        u = ease_io(seg(lt, 0.3, 2.2))
        r = lerp(300, 46, u)
        c = (lerp(1.0, 0.92, u), lerp(0.55, 0.95, u), lerp(0.30, 1.0, u))
        _star(ctx, cx, cy - 20, r, c, t, rays=u > 0.9)
        if u > 0.95:
            ctx.arc(cx, cy - 20, 300, 0, 2 * math.pi)
            src(ctx, WH, 0.25)
            ctx.set_dash([14, 12])
            ctx.set_line_width(3)
            ctx.stroke()
            ctx.set_dash([])
        a = ease_back(seg(lt, 2.4, 2.9))
        if a > 0.01:
            _pill(ctx, "WHITE DWARF", cx, cy + 270, 52, K_, Y_, a)
    elif i == 3:   # rocky debris spirals in; Na, Ca, Li chips pop
        _star(ctx, cx, cy - 110, 70, WH, t)
        for q in range(14):
            ph = q / 14.0 * 2 * math.pi
            f = ((lt * 0.35 + q / 14.0) % 1.0)
            rr = lerp(330, 70, f)
            ang = ph + f * 5
            _rock(ctx, cx + rr * math.cos(ang), cy - 110 + rr * 0.55 * math.sin(ang), 1.2 * (1 - 0.6 * f), ang)
        L = LINES[3]
        base = L["start"] - _scene_start(3)
        for j, (sym, name, c) in enumerate((("Na", "SODIUM", Y_), ("Ca", "CALCIUM", WH), ("Li", "LITHIUM", PINK))):
            a = ease_back(seg(lt, base + L["dur"] * (0.68 + j * 0.1), base + L["dur"] * (0.68 + j * 0.1) + 0.4))
            _chip(ctx, sym, name, cx + (j - 1) * 240, cy + 225, c, a)
    elif i == 4:   # sodium dims yellow/orange/red -> star turns green
        x0, w = 110, W - 220
        u = ease_io(seg(lt, 0.6, 2.4))
        _spectrum(ctx, x0, cy - 330, w, 110, {4: u, 5: u, 6: 0.6 * u})
        if u > 0.05:
            text(ctx, "ABSORBED BY SODIUM", x0 + w * 5.5 / 7, cy - 160, 32, WH, alpha=u)
        g = ease_out(seg(lt, 2.4, 3.6))
        c = (lerp(1.0, GREEN[0], g), lerp(1.0, GREEN[1], g), lerp(1.0, GREEN[2], g))
        _star(ctx, cx, cy + 130, 105, c, t)
    elif i == 5:   # crossed-out eyepiece -> light + vision model -> green swatch
        ex, ey = cx - 250, cy - 120
        ctx.arc(ex, ey, 110, 0, 2 * math.pi)
        src(ctx, K_, 0.9)
        ctx.fill_preserve()
        src(ctx, WH, 0.8)
        ctx.set_line_width(10)
        ctx.stroke()
        _glow(ctx, ex, ey, 60, WH, 0.5)
        x = ease_back(seg(lt, 0.4, 0.9))
        if x > 0.01:
            for sg in (1, -1):
                ctx.move_to(ex - 90 * x, ey - 90 * x * sg)
                ctx.line_to(ex + 90 * x, ey + 90 * x * sg)
            src(ctx, RED)
            ctx.set_line_width(18)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.stroke()
        text(ctx, "TELESCOPE VIEW", ex, ey + 170, 34, WH)
        # starlight curve + eye model
        a = ease_out(seg(lt, 2.4, 3.0))
        if a > 0.01:
            gx, gy = cx + 250, cy - 120
            rrect(ctx, gx - 160, gy - 110, 320, 220, 20)
            src(ctx, K_, 0.85 * a)
            ctx.fill()
            ctx.move_to(gx - 140, gy + 70)
            for q in range(29):
                xx = gx - 140 + q * 10
                yy = gy + 70 - 120 * math.exp(-((q - 11) / 6.0) ** 2) + (40 if 17 < q < 26 else 0)
                ctx.line_to(xx, min(yy, gy + 80))
            src(ctx, CYAN, a)
            ctx.set_line_width(5)
            ctx.stroke()
            text(ctx, "STARLIGHT", gx, gy + 170, 34, WH, alpha=a)
        e = ease_back(seg(lt, 3.6, 4.2))
        if e > 0.01:
            _eye(ctx, cx - 140, cy + 180, 0.9 * e, e)
            text(ctx, "+", cx - 140 + 150, cy + 200, 70, WH, alpha=e)
        s = ease_back(seg(lt, 5.0, 5.5))
        if s > 0.01:
            rrect(ctx, cx + 110, cy + 100, 220, 160, 24)
            src(ctx, GREEN, s)
            ctx.fill()
            text(ctx, "TRUE COLOUR", cx + 220, cy + 310, 32, GREEN, alpha=s)
    elif i == 6:   # green star slides aside, pink carbon star appears
        u = ease_io(seg(lt, 0.2, 1.0))
        _star(ctx, lerp(cx, cx - 270, u), cy - 40, lerp(100, 60, u), GREEN, t)
        p = ease_back(seg(lt, 0.9, 1.5))
        if p > 0.01:
            _star(ctx, cx + 200, cy - 40, 110 * p, PINK, t)
        c = ease_back(seg(lt, 3.0, 3.5))
        if c > 0.01:
            _chip(ctx, "C", "CARBON", cx + 200, cy + 215, PINK, c)
    elif i == 7:   # 30 dots; one glows a colour
        cols, rows = 6, 5
        for q in range(30):
            x = cx - 375 + (q % cols) * 150
            y = cy - 330 + (q // cols) * 150
            a = ease_out(seg(lt, 0.05 * q, 0.05 * q + 0.3))
            if q == 20 and a > 0.01:
                g = ease_back(seg(lt, 2.4, 2.9))
                c = (lerp(1, GREEN[0], g), lerp(1, GREEN[1], g), lerp(1, GREEN[2], g))
                _star(ctx, x, y, 26 + 14 * g, c, t, rays=g > 0.5)
            elif a > 0.01:
                _glow(ctx, x, y, 40, WH, 0.35 * a)
                ellipse(ctx, x, y, 20, 20)
                src(ctx, WH, a)
                ctx.fill()


def _headline(ctx, i, t):
    t0 = _scene_start(i)
    lead, key = HEADS[i]
    a = ease_out(seg(t, t0 + 0.05, t0 + 0.4))
    text(ctx, lead, W / 2, 400, 46, WH, alpha=a)
    k = ease_back(seg(t, t0 + 0.15, t0 + 0.5))
    size = 108 if len(key) <= 10 else 84 if len(key) <= 15 else 72
    ctx.select_font_face(gfx.FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    while size > 40:
        ctx.set_font_size(size)
        if ctx.text_extents(key).x_advance <= W - 140:
            break
        size -= 4
    if k > 0.01:
        ctx.save()
        ctx.translate(W / 2, 510)
        ctx.scale(k, k)
        text(ctx, key, 0, 0, size, Y_)
        ctx.restore()


def _flash(ctx, t):
    """Soft white bloom across each scene change (cosmic 'reveal')."""
    for i in range(1, len(LINES)):
        u = seg(t, _scene_start(i) - 0.15, _scene_start(i) + 0.25)
        if 0 < u < 1:
            src(ctx, (0.85, 0.92, 1.0), 0.55 * math.sin(math.pi * u))
            ctx.paint()


def render_frame(t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    _background(ctx, t)
    i = _active(t)
    if i is not None:
        k = ease_out(seg(t, _scene_start(i), _scene_start(i) + 0.4))
        ctx.save()
        ctx.push_group()
        _scene(ctx, i, t, k)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(max(k, 0.01))
        ctx.restore()
        _headline(ctx, i, t)
        line = LINES[i]
        c0, ctext = _caption_text(i, t)
        pk = ease_back(seg(t, c0 - 0.2, c0 + 0.1))
        f = int((t - line["start"]) * 30)
        pulse = 1 + 0.03 * (ENV[i][f] if 0 <= f < len(ENV[i]) else 0)
        brand.caption(ctx, ctext, 1500, CAP_SIZE, pop=pk * pulse)
    _flash(ctx, t)
    brand.watermark(ctx)
    brand.end_card(ctx, t, DURATION - 1.4)
    surf.flush()
    return surf
