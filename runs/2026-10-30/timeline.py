"""2026-10-30 cosmic: Rubin Observatory finds dwarf planet candidate 2026 ED138 (contract: DURATION + render_frame)."""
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
    ("BEYOND PLUTO", "A NEW WORLD?"),
    ("MEET", "2026 ED138"),
    ("SPOTTED", "OCT 13, 2026"),
    ("HIDDEN AMONG", "MILLIONS OF STARS"),
    ("DISTANCE FROM SUN", "~46x EARTH'S"),
    ("SIZE (ESTIMATE)", "600-1,500 KM"),
    ("IF CONFIRMED", "DWARF PLANET #6"),
    ("NEXT STEP", "MEASURE ITS SIZE"),
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



def _world(ctx, x, y, r, c=ICE, a=1.0, t=0.0, glow=True):
    """Icy distant world: soft glow, shaded sphere, faint surface blotches."""
    if a <= 0.01 or r <= 1:
        return
    if glow:
        _glow(ctx, x, y, r * 1.7, c, 0.35 * a)
    g = cairo.RadialGradient(x - r * 0.35, y - r * 0.35, r * 0.05, x, y, r)
    g.add_color_stop_rgba(0, 1, 1, 1, a)
    g.add_color_stop_rgba(0.5, c[0], c[1], c[2], a)
    g.add_color_stop_rgba(1, c[0] * 0.25, c[1] * 0.25, c[2] * 0.35, a)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    ctx.save()
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.clip()
    for px, py, rr in ((-0.3, 0.1, 0.22), (0.25, -0.3, 0.15), (0.2, 0.4, 0.18)):
        ellipse(ctx, x + (px + 0.03 * math.sin(t * 0.3)) * r, y + py * r, rr * r, rr * r * 0.7)
        src(ctx, (0.55, 0.45, 0.55), 0.35 * a)
        ctx.fill()
    ctx.restore()


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


def _dome(ctx, x, y, s, a=1.0, slit=1.0):
    """Generic observatory building on a mountain ridge (no logos)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-420, 160)
    ctx.line_to(-200, 20)
    ctx.line_to(-60, 90)
    ctx.line_to(120, -10)
    ctx.line_to(420, 160)
    ctx.close_path()
    src(ctx, (0.10, 0.10, 0.16), a)
    ctx.fill()
    rrect(ctx, -110, -90, 220, 130, 10)
    src(ctx, (0.80, 0.82, 0.86), a)
    ctx.fill()
    ctx.arc(0, -90, 110, math.pi, 0)
    ctx.close_path()
    src(ctx, (0.92, 0.93, 0.96), a)
    ctx.fill()
    ctx.move_to(-18 * slit, -200)
    ctx.line_to(18 * slit, -200)
    ctx.line_to(26 * slit, -95)
    ctx.line_to(-26 * slit, -95)
    ctx.close_path()
    src(ctx, K_, a)
    ctx.fill()
    ctx.restore()


def _scene(ctx, i, t, k):
    lt = t - _scene_start(i)
    cx, cy = W / 2, VIS_Y
    if i == 0:   # Sun far left, Pluto orbit, new world fades in further out
        _star(ctx, -40, cy + 40, 70, SUNC, t)
        _orbit(ctx, -40, cy + 40, 600, 230, WH, 0.25)
        _world(ctx, -40 + 600 * math.cos(0.35), cy + 40 + 230 * math.sin(0.35), 26, (0.85, 0.75, 0.65), glow=False)
        text(ctx, "PLUTO", 520, cy + 190, 32, WH, alpha=0.8)
        _orbit(ctx, -40, cy + 40, 900, 330, CYAN, 0.45, dash=True)
        a = ease_out(seg(lt, 0.3, 1.4))
        q = ease_back(seg(lt, 1.6, 2.1))
        x0, y0 = -40 + 900 * math.cos(-0.25), cy + 40 + 330 * math.sin(-0.25)
        _world(ctx, x0, y0, 60 * a, ICE, a, t)
        if q > 0.01:
            text(ctx, "?", x0 + 95, y0 - 40, 110 * q, Y_)
    elif i == 1:   # observatory, beam up to the world, name tag
        _dome(ctx, cx, cy + 150, 1.0, slit=1.0)
        b = ease_out(seg(lt, 0.4, 1.6))
        if b > 0.01:
            ctx.move_to(cx - 20, cy - 40)
            ctx.line_to(cx + 20, cy - 40)
            ctx.line_to(cx + 260 * b, cy - 40 - 260 * b)
            ctx.line_to(cx + 160 * b, cy - 40 - 300 * b)
            ctx.close_path()
            src(ctx, CYAN, 0.18)
            ctx.fill()
        _world(ctx, cx + 210, cy - 330, 55, ICE, b, t)
        tag = ease_back(seg(lt, 1.2, 1.7))
        if tag > 0.01:
            _pill(ctx, "2026 ED138", cx - 160, cy - 250, 52, K_, Y_, tag)
        c = ease_back(seg(lt, 4.0, 4.5))
        if c > 0.01:
            _pill(ctx, "RUBIN OBSERVATORY, CHILE", cx, cy + 340, 40, WH, TEAL, c)
    elif i == 2:   # stack of survey frames from March to October
        months = ["MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT"]
        for q, m in enumerate(months):
            a = ease_back(seg(lt, 0.15 * q, 0.15 * q + 0.4))
            if a <= 0.01:
                continue
            col, row = q % 4, q // 4
            x, y = cx - 360 + col * 240, cy - 230 + row * 290
            rrect(ctx, x - 100, y - 110, 200, 220, 14)
            src(ctx, (0.06, 0.08, 0.18), a)
            ctx.fill_preserve()
            src(ctx, Y_ if m == "OCT" else WH, a * (1 if m == "OCT" else 0.5))
            ctx.set_line_width(5 if m == "OCT" else 3)
            ctx.stroke()
            for s in range(9):
                ellipse(ctx, x - 80 + (s * 53) % 160, y - 90 + (s * 37) % 150, 2.5, 2.5)
                src(ctx, WH, 0.7 * a)
                ctx.fill()
            ellipse(ctx, x - 60 + q * 14, y - 10 + q * 3, 6, 6)
            src(ctx, CYAN, a)
            ctx.fill()
            text(ctx, m, x, y + 150, 34, Y_ if m == "OCT" else WH, alpha=a)
        f = ease_back(seg(lt, 2.0, 2.5))
        if f > 0.01:
            _pill(ctx, "FOUND: OCT 13", cx, cy + 320, 50, K_, Y_, f)
    elif i == 3:   # crowded star field, one dot slowly moves, ring locks on
        for s in range(260):
            x = cx - 430 + (s * 97.3) % 860
            y = cy - 330 + (s * 61.7) % 660
            r = 1.5 + (s % 4)
            ellipse(ctx, x, y, r, r)
            src(ctx, (0.9, 0.9, 1.0) if s % 5 else (1.0, 0.85, 0.6), 0.5 + 0.1 * (s % 4))
            ctx.fill()
        mv = seg(lt, 0.5, 8.0)
        mx, my = cx - 250 + 420 * mv, cy + 60 - 120 * mv
        ellipse(ctx, mx, my, 6, 6)
        src(ctx, CYAN)
        ctx.fill()
        ring = ease_back(seg(lt, 4.2, 4.8))
        if ring > 0.01:
            for q in range(1, 6):
                px, py = mx - 84 * q * mv, my + 24 * q * mv
                ellipse(ctx, px, py, 4, 4)
                src(ctx, CYAN, 0.6 - 0.1 * q)
                ctx.fill()
            ctx.arc(mx, my, 60 * ring, 0, 2 * math.pi)
            src(ctx, Y_)
            ctx.set_line_width(6)
            ctx.stroke()
            _pill(ctx, "IT MOVES", mx, my - 100, 44, K_, Y_, ring)
    elif i == 4:   # distance bar Sun - Earth (1) - Pluto (~40) - ED138 (~46)
        x0, x1, y = 110, W - 110, cy - 40
        span = x1 - x0
        p = ease_out(seg(lt, 0.3, 2.2))
        ctx.move_to(x0, y)
        ctx.line_to(x0 + span * p, y)
        src(ctx, WH, 0.5)
        ctx.set_line_width(4)
        ctx.stroke()
        _star(ctx, x0, y, 34, SUNC, t, rays=False)
        text(ctx, "SUN", x0 + 10, y + 110, 32, WH)
        ex = x0 + span * 1 / 46
        ellipse(ctx, ex + 18, y, 9, 9)
        src(ctx, BLUE)
        ctx.fill()
        text(ctx, "EARTH = 1", ex + 120, y - 60, 30, BLUE)
        if p > 40 / 46:
            px = x0 + span * 40 / 46
            _world(ctx, px, y, 18, (0.85, 0.75, 0.65), glow=False)
            text(ctx, "PLUTO ~40", px - 20, y + 90, 30, WH)
        if p >= 0.999:
            _world(ctx, x1, y, 30, ICE, 1.0, t)
            text(ctx, "~46", x1 - 10, y - 70, 44, Y_)
        o = ease_back(seg(lt, 3.6, 4.1))
        if o > 0.01:
            _pill(ctx, "1 ORBIT = ~280 YEARS", cx, cy + 260, 52, K_, Y_, o)
    elif i == 5:   # size comparison: Pluto vs the uncertain range
        pr = 2377 / 2 * 0.14
        a = ease_out(seg(lt, 0.3, 1.0))
        _world(ctx, cx - 240, cy, pr * a, (0.85, 0.75, 0.65), a, t)
        text(ctx, "PLUTO", cx - 240, cy + pr + 70, 36, WH, alpha=a)
        text(ctx, "2,377 KM", cx - 240, cy + pr + 120, 32, WH, alpha=a)
        g = 0.5 + 0.5 * math.sin(t * 2.2)
        r = lerp(600, 1500, g) / 2 * 0.14
        b = ease_out(seg(lt, 1.0, 1.8))
        bx = cx + 250
        for rr, cc in ((1500 / 2 * 0.14, CYAN), (600 / 2 * 0.14, CYAN)):
            ctx.arc(bx, cy, rr, 0, 2 * math.pi)
            ctx.set_dash([10, 10])
            src(ctx, cc, 0.6 * b)
            ctx.set_line_width(3)
            ctx.stroke()
            ctx.set_dash([])
        _world(ctx, bx, cy, r * b, ICE, b, t, glow=False)
        text(ctx, "ED138", bx, cy + pr + 70, 36, Y_, alpha=b)
        text(ctx, "600-1,500 KM", bx, cy + pr + 120, 32, Y_, alpha=b)
    elif i == 6:   # five dwarf planet chips + a sixth "?" slot
        names = [("P", "PLUTO"), ("C", "CERES"), ("E", "ERIS"), ("H", "HAUMEA"), ("M", "MAKEMAKE")]
        L = LINES[6]
        base = L["start"] - _scene_start(6)
        for q, (sym, nm) in enumerate(names):
            a = ease_back(seg(lt, base + 2.6 + 0.45 * q, base + 3.0 + 0.45 * q))
            col, row = q % 3, q // 3
            _chip(ctx, sym, nm, cx - 270 + col * 270, cy - 170 + row * 260, WH, a)
        s = ease_back(seg(lt, 0.4, 0.9))
        if s > 0.01:
            _chip(ctx, "?", "ED138", cx + 270, cy + 90, Y_, s * (1 + 0.05 * math.sin(t * 5)))
    elif i == 7:   # several telescopes aim at the world; faint extra '?' worlds
        _world(ctx, cx, cy - 200, 70, ICE, 1.0, t)
        for q, x in enumerate((cx - 330, cx, cx + 330)):
            a = ease_back(seg(lt, 0.2 + 0.25 * q, 0.6 + 0.25 * q))
            if a <= 0.01:
                continue
            ctx.move_to(x, cy + 170)
            ctx.line_to(cx, cy - 200)
            src(ctx, CYAN, 0.35 * a)
            ctx.set_line_width(5)
            ctx.stroke()
            _dome(ctx, x, cy + 260, 0.45, a)
        m = ease_out(seg(lt, 3.4, 4.6))
        for x, y in ((cx - 340, cy - 330), (cx + 350, cy - 380), (cx + 300, cy + 40)):
            _world(ctx, x, y, 24 * m, (0.7, 0.75, 0.95), 0.7 * m, t)
            if m > 0.3:
                text(ctx, "?", x + 42, y - 22, 48, Y_, alpha=m)


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
