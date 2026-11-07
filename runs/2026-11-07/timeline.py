"""2026-11-07 cosmic: ESA Hera sends first close-up of Didymos & Dimorphos (DART crash site) (contract: DURATION + render_frame)."""
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
    ("4 YEARS LATER", "BACK TO THE CRASH"),
    ("SEPT 2022", "DART HITS DIMORPHOS"),
    ("MOON'S ORBIT", "~32 MIN SHORTER"),
    ("ESA'S HERA", "FIRST CLOSE-UP"),
    ("NEVER SEEN BY DART", "THE OTHER SIDE"),
    ("ON THE SURFACE", "BOULDERS & GROOVES"),
    ("SIZE", "~780 M vs ~150 M"),
    ("NEXT STEP", "CRASH-SITE PROBE"),
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
    text(ctx, name, 0, 66, 26 if len(name) < 7 else 21, WH)
    ctx.restore()


def _pill(ctx, s, x, y, size, fg, bg, a=1.0, pad=36):
    ctx.select_font_face(gfx.FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    w = ctx.text_extents(s).x_advance + pad * 2
    rrect(ctx, x - w / 2, y - size * 0.95, w, size * 1.45, size * 0.5)
    src(ctx, bg, 0.9 * a)
    ctx.fill()
    text(ctx, s, x, y, size, fg, alpha=a)



ROCK = (0.62, 0.58, 0.54)
MOON = (0.70, 0.66, 0.60)


def _blob(seed, n=22):
    out = []
    for q in range(n):
        a = 2 * math.pi * q / n
        out.append(1 + 0.10 * math.sin(3 * a + seed) + 0.06 * math.sin(7 * a + 2 * seed) + 0.04 * math.cos(11 * a + seed))
    return out


BLOB_D = _blob(1.3)
BLOB_M = _blob(4.1)


def _asteroid(ctx, x, y, r, c=ROCK, a=1.0, rot=0.0, blob=None, craters=True, lit=1.0, detail=0.0):
    """Lumpy grey rubble-pile asteroid: lit from upper-left, craters, optional boulders/grooves."""
    if a <= 0.01 or r <= 1:
        return
    blob = blob or BLOB_D
    n = len(blob)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    for q in range(n + 1):
        ang = 2 * math.pi * (q % n) / n
        px, py = r * blob[q % n] * math.cos(ang), r * blob[q % n] * math.sin(ang) * 0.86
        ctx.move_to(px, py) if q == 0 else ctx.line_to(px, py)
    ctx.close_path()
    g = cairo.RadialGradient(-r * 0.4, -r * 0.4, r * 0.1, 0, 0, r * 1.15)
    g.add_color_stop_rgba(0, min(1, c[0] * 1.35 * lit), min(1, c[1] * 1.35 * lit), min(1, c[2] * 1.35 * lit), a)
    g.add_color_stop_rgba(0.6, c[0] * 0.8, c[1] * 0.8, c[2] * 0.8, a)
    g.add_color_stop_rgba(1, c[0] * 0.18, c[1] * 0.18, c[2] * 0.2, a)
    ctx.set_source(g)
    ctx.fill_preserve()
    ctx.clip()
    # equatorial ridge
    ctx.move_to(-r * 1.1, r * 0.02)
    ctx.curve_to(-r * 0.4, -r * 0.08, r * 0.4, -r * 0.08, r * 1.1, r * 0.02)
    src(ctx, (1, 1, 1), 0.10 * a)
    ctx.set_line_width(max(2, r * 0.06))
    ctx.stroke()
    if craters:
        for px, py, rr in ((-0.35, -0.3, 0.16), (0.3, 0.25, 0.20), (0.1, -0.45, 0.10), (-0.2, 0.42, 0.12), (0.5, -0.1, 0.09)):
            ellipse(ctx, px * r, py * r, rr * r, rr * r * 0.75)
            src(ctx, (0, 0, 0), 0.25 * a)
            ctx.fill()
            ellipse(ctx, px * r - rr * r * 0.15, py * r - rr * r * 0.15, rr * r * 0.8, rr * r * 0.55)
            src(ctx, (1, 1, 1), 0.06 * a)
            ctx.fill()
    if detail > 0.01:   # boulders + groove/ridge lines
        for s in range(int(26 * detail)):
            bx = r * (-0.8 + ((s * 0.377) % 1.6))
            by = r * (-0.6 + ((s * 0.613) % 1.2))
            br = r * (0.025 + 0.02 * (s % 3))
            ellipse(ctx, bx, by, br, br * 0.8)
            src(ctx, (0.92, 0.9, 0.86), 0.55 * a)
            ctx.fill()
            ellipse(ctx, bx + br * 0.4, by + br * 0.5, br, br * 0.5)
            src(ctx, (0, 0, 0), 0.3 * a)
            ctx.fill()
        for q in range(5):
            u = seg(detail, q * 0.15, q * 0.15 + 0.4)
            if u <= 0:
                continue
            yy = r * (-0.5 + 0.25 * q)
            ctx.move_to(-r * 0.9, yy)
            ctx.curve_to(-r * 0.3, yy - r * 0.15, r * 0.2, yy + r * 0.12, -r * 0.9 + r * 1.8 * u, yy - r * 0.05)
            src(ctx, (0, 0, 0), 0.35 * a)
            ctx.set_line_width(max(2, r * 0.025))
            ctx.stroke()
    ctx.restore()


def _probe(ctx, x, y, s, a=1.0, ang=0.0, panels=True, col=GOLD):
    """Generic spacecraft: gold box, two solar wings (no logos)."""
    if a <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(s, s)
    if panels:
        for sx in (-1, 1):
            rrect(ctx, sx * 40 - (90 if sx < 0 else 0), -26, 90, 52, 4)
            src(ctx, (0.15, 0.25, 0.55), a)
            ctx.fill_preserve()
            src(ctx, CYAN, 0.7 * a)
            ctx.set_line_width(2)
            ctx.stroke()
            for k in range(1, 3):
                ctx.move_to(sx * 40 + (k * 30 - 90 if sx < 0 else k * 30), -26)
                ctx.rel_line_to(0, 52)
                ctx.stroke()
    rrect(ctx, -40, -34, 80, 68, 8)
    src(ctx, col, a)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.set_line_width(3)
    ctx.stroke()
    ellipse(ctx, 0, 0, 14, 14)
    src(ctx, K_, a)
    ctx.fill()
    ctx.restore()


def _flashburst(ctx, x, y, u):
    if 0 < u < 1:
        _glow(ctx, x, y, 40 + 260 * u, (1.0, 0.92, 0.6), 0.9 * (1 - u))
        for q in range(14):
            ang = q * 2 * math.pi / 14 + 0.3
            d = 30 + 240 * u * (0.7 + 0.3 * ((q * 7) % 5) / 5)
            ellipse(ctx, x + d * math.cos(ang), y + d * math.sin(ang), 6 * (1 - u) + 2, 6 * (1 - u) + 2)
            src(ctx, (0.9, 0.85, 0.75), 1 - u)
            ctx.fill()


def _pair(ctx, cx, cy, t, R=190, mr=48, orb=330, phase=0.0, a=1.0, orbit=True, speed=0.35):
    if orbit:
        _orbit(ctx, cx, cy, orb, orb * 0.32, WH, 0.22 * a, dash=True)
    ang = phase + t * speed
    mx, my = cx + orb * math.cos(ang), cy + orb * 0.32 * math.sin(ang)
    behind = math.sin(ang) < 0
    if behind:
        _asteroid(ctx, mx, my, mr, MOON, a, t * 0.3, BLOB_M)
    _asteroid(ctx, cx, cy, R, ROCK, a, 0.0)
    if not behind:
        _asteroid(ctx, mx, my, mr, MOON, a, t * 0.3, BLOB_M)
    return mx, my


def _orbit(ctx, x, y, rx, ry, c, a=1.0, w=3, dash=False):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(1, ry / rx)
    ctx.arc(0, 0, rx, 0, 2 * math.pi)
    ctx.restore()
    if dash:
        ctx.set_dash([14, 12])
    src(ctx, c, a)
    ctx.set_line_width(w)
    ctx.stroke()
    ctx.set_dash([])


def _scene(ctx, i, t, k):
    lt = t - _scene_start(i)
    cx, cy = W / 2, VIS_Y
    if i == 0:   # streak hits the moon, flash, then a second probe glides in
        mx, my = cx + 230, cy - 120
        _asteroid(ctx, cx - 60, cy + 40, 200, ROCK, 1.0, 0.0)
        _asteroid(ctx, mx, my, 55, MOON, 1.0, t * 0.3, BLOB_M)
        u = seg(lt, 0.2, 1.1)
        if u < 1:
            px, py = lerp(cx + 560, mx, ease_in(u)), lerp(cy - 650, my, ease_in(u))
            ctx.move_to(px, py)
            ctx.line_to(px + 120, py - 140)
            src(ctx, Y_, 0.6)
            ctx.set_line_width(6)
            ctx.stroke()
            _probe(ctx, px, py, 0.35, 1.0, 0.7, panels=False)
        _flashburst(ctx, mx, my, seg(lt, 1.1, 2.4))
        h = ease_out(seg(lt, 2.6, 4.2))
        if h > 0.01:
            _probe(ctx, lerp(-160, cx - 330, h), lerp(cy - 520, cy - 380, h), 0.8, h, 0.15)
            _pill(ctx, "EUROPE IS BACK", cx, cy + 360, 46, K_, Y_, ease_back(seg(lt, 3.4, 3.9)))
    elif i == 1:   # labelled pair, DART dives into the moon
        mx, my = _pair(ctx, cx, cy, 0.0, phase=0.6)
        a = ease_back(seg(lt, 0.6, 1.0))
        if a > 0.01:
            _pill(ctx, "DIDYMOS", cx - 40, cy + 300, 44, WH, TEAL, a)
            _pill(ctx, "DIMORPHOS (MOON)", mx - 20, my + 110, 34, K_, Y_, ease_back(seg(lt, 2.4, 2.8)))
        u = seg(lt, 1.0, 2.6)
        if u < 1 and u > 0:
            px, py = lerp(cx - 520, mx, ease_in(u)), lerp(cy - 400, my, ease_in(u))
            _probe(ctx, px, py, 0.4, 1.0, -0.8, panels=True)
            text(ctx, "DART", px - 70, py - 50, 36, Y_)
        _flashburst(ctx, mx, my, seg(lt, 2.6, 3.8))
    elif i == 2:   # orbit before vs after
        _asteroid(ctx, cx, cy - 20, 150, ROCK, 1.0)
        p = ease_out(seg(lt, 0.2, 1.0))
        _orbit(ctx, cx, cy - 20, 360, 130, WH, 0.35 * p, dash=True)
        q = ease_out(seg(lt, 1.4, 2.4))
        _orbit(ctx, cx, cy - 20, 360 - 40 * q, 130 - 14 * q, Y_, 0.9 * q, w=5)
        ang = t * 0.6
        _asteroid(ctx, cx + (360 - 40 * q) * math.cos(ang), cy - 20 + (130 - 14 * q) * math.sin(ang), 36, MOON, 1.0, t, BLOB_M)
        b = ease_back(seg(lt, 0.6, 1.1))
        if b > 0.01:
            _pill(ctx, "BEFORE: 11 H 55 MIN", cx, cy + 250, 42, WH, (0.2, 0.2, 0.3), b)
        c = ease_back(seg(lt, 2.2, 2.7))
        if c > 0.01:
            _pill(ctx, "AFTER: 11 H 23 MIN", cx, cy + 350, 42, K_, Y_, c)
    elif i == 3:   # Hera with camera cone toward the pair, distance tag
        _pair(ctx, cx + 170, cy + 120, t, R=150, mr=38, orb=250, phase=0.4)
        hx, hy = cx - 300, cy - 300
        c = ease_out(seg(lt, 0.6, 1.6))
        if c > 0.01:
            ctx.move_to(hx + 20, hy + 20)
            ctx.line_to(cx + 170 - 300 * c, cy + 120 - 40 * c)
            ctx.line_to(cx + 170 + 120 * c, cy + 120 + 260 * c)
            ctx.close_path()
            src(ctx, CYAN, 0.16)
            ctx.fill()
        _probe(ctx, hx, hy, 0.9, 1.0, 0.25)
        text(ctx, "HERA", hx, hy - 70, 40, Y_, alpha=ease_out(seg(lt, 0.3, 0.8)))
        d = ease_back(seg(lt, 3.4, 3.9))
        if d > 0.01:
            _pill(ctx, "FROM ~60 KM AWAY", cx, cy + 330, 48, K_, Y_, d)
    elif i == 4:   # two views of Didymos: DART's side vs Hera's side
        for q, (lab, col) in enumerate((("DART'S VIEW", WH), ("HERA'S VIEW", Y_))):
            a = ease_back(seg(lt, 0.2 + 0.7 * q, 0.6 + 0.7 * q))
            if a <= 0.01:
                continue
            x = cx - 230 + 460 * q
            _asteroid(ctx, x, cy, 170 * a, ROCK, 1.0, math.pi * q, detail=0.6 * q)
            _pill(ctx, lab, x, cy + 260, 38, K_ if q else WH, col if q else (0.2, 0.2, 0.3), a)
        n = ease_back(seg(lt, 1.6, 2.0))
        if n > 0.01:
            _pill(ctx, "NEW!", cx + 230, cy - 230, 40, K_, Y_, n)
    elif i == 5:   # big close-up, boulders and grooves appear, debris arcs from the moon
        det = seg(lt, 0.2, 3.2)
        _asteroid(ctx, cx, cy + 40, 330, ROCK, 1.0, 0.1, detail=det)
        mx, my = cx + 380, cy - 330
        _asteroid(ctx, mx, my, 50, MOON, 1.0, t * 0.3, BLOB_M)
        u = seg(lt, 2.4, 4.4)
        if u > 0:
            for q in range(6):
                v = min(1, u * 1.3 - q * 0.05)
                if v <= 0:
                    continue
                ex, ey = cx - 200 + q * 70, cy - 120 + (q % 3) * 60
                px = lerp(mx, ex, v)
                py = lerp(my, ey, v) - 160 * math.sin(math.pi * v)
                ellipse(ctx, px, py, 8, 8)
                src(ctx, (0.95, 0.85, 0.65), 0.9)
                ctx.fill()
            _pill(ctx, "DEBRIS FROM THE CRASH?", cx, cy - 330, 40, K_, Y_, ease_back(seg(lt, 3.0, 3.5)))
    elif i == 6:   # to-scale size comparison
        s = 0.42
        a = ease_back(seg(lt, 0.2, 0.7))
        _asteroid(ctx, cx - 120, cy, 780 / 2 * s * a, ROCK, 1.0, 0.0, craters=True)
        text(ctx, "DIDYMOS ~780 M", cx - 120, cy + 230, 38, WH, alpha=a)
        b = ease_back(seg(lt, 2.6, 3.1))
        _asteroid(ctx, cx + 300, cy + 40, 150 / 2 * s * b + 0.01, MOON, 1.0, 0.0, BLOB_M, craters=False)
        if b > 0.01:
            text(ctx, "DIMORPHOS", cx + 300, cy + 120, 34, Y_, alpha=b)
            text(ctx, "~150 M", cx + 300, cy + 165, 34, Y_, alpha=b)
    elif i == 7:   # Hera moves in; small Earth with a shield ring
        z = ease_io(seg(lt, 0.0, 4.5))
        _pair(ctx, cx + 80, cy - 40, t, R=120 + 60 * z, mr=30 + 14 * z, orb=220 + 80 * z, phase=1.2)
        _probe(ctx, lerp(cx - 420, cx - 250, z), lerp(cy - 420, cy - 300, z), 0.7, 1.0, 0.3)
        e = ease_back(seg(lt, 2.4, 2.9))
        if e > 0.01:
            ex, ey = cx - 300, cy + 210
            _glow(ctx, ex, ey, 110 * e, BLUE, 0.5)
            ellipse(ctx, ex, ey, 60 * e, 60 * e)
            src(ctx, BLUE)
            ctx.fill()
            ellipse(ctx, ex - 15 * e, ey - 10 * e, 25 * e, 18 * e)
            src(ctx, (0.3, 0.75, 0.35))
            ctx.fill()
            ctx.arc(ex, ey, 95 * e, 0, 2 * math.pi)
            src(ctx, Y_, 0.9)
            ctx.set_line_width(6)
            ctx.stroke()
            text(ctx, "EARTH", ex, ey + 140, 34, WH, alpha=e)
            _pill(ctx, "PLANETARY DEFENCE", cx + 170, cy + 230, 40, K_, Y_, ease_back(seg(lt, 3.0, 3.5)))


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
