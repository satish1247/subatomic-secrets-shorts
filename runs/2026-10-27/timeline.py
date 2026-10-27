"""2026-10-27 cosmic: NASA ends the Swift observatory mission ahead of re-entry (contract: DURATION + render_frame)."""
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
    ("NASA'S SWIFT", "FALLING TO EARTH"),
    ("BUILT FOR 2 YEARS", "LASTED ~22"),
    ("ITS JOB", "GAMMA-RAY BURSTS"),
    ("ITS CATCH", "2,000+ BURSTS"),
    ("WHY STOP?", "ATMOSPHERIC DRAG"),
    ("ROBOT RESCUE", "FAILED"),
    ("FINAL OBSERVATION", "OCT 20, 2026"),
    ("ITS LEGACY", "12 TB OF DATA"),
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



def _satellite(ctx, x, y, s, rot=0.0, a=1.0, glow=None):
    """Generic observatory: body, telescope tube, two solar wings (no real logo)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    if glow:
        _glow(ctx, 0, 0, 220, glow, 0.6 * a)
    for sg in (-1, 1):   # solar wings
        ctx.move_to(sg * 52, -6)
        ctx.line_to(sg * 80, -6)
        src(ctx, (0.75, 0.75, 0.8), a)
        ctx.set_line_width(6)
        ctx.stroke()
        rrect(ctx, sg * 80 if sg > 0 else -230, -48, 150, 84, 8)
        src(ctx, (0.12, 0.28, 0.62), a)
        ctx.fill_preserve()
        src(ctx, (0.65, 0.78, 1.0), a)
        ctx.set_line_width(3)
        ctx.stroke()
        for q in range(1, 4):
            xx = (80 + q * 37.5) * sg
            ctx.move_to(xx, -48)
            ctx.line_to(xx, 36)
            src(ctx, (0.65, 0.78, 1.0), 0.6 * a)
            ctx.set_line_width(2)
            ctx.stroke()
    rrect(ctx, -52, -60, 104, 120, 12)   # body
    src(ctx, (0.85, 0.85, 0.88), a)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.set_line_width(4)
    ctx.stroke()
    rrect(ctx, -40, -40, 80, 36, 6)
    src(ctx, GOLD, a)
    ctx.fill()
    rrect(ctx, -30, -150, 60, 92, 8)   # telescope tube
    src(ctx, WH, a)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.stroke()
    ellipse(ctx, 0, -150, 30, 9)
    src(ctx, (0.1, 0.1, 0.15), a)
    ctx.fill()
    ctx.restore()


def _earth(ctx, x, y, r, atm=1.0):
    _glow(ctx, x, y, r * (1.10 + 0.12 * atm), (0.45, 0.75, 1.0), 0.55)
    g = cairo.RadialGradient(x - r * 0.3, y - r * 0.3, r * 0.1, x, y, r)
    g.add_color_stop_rgb(0, 0.30, 0.62, 0.95)
    g.add_color_stop_rgb(1, 0.06, 0.20, 0.48)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    ctx.save()
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.clip()
    for px, py, rx, ry in ((-0.35, -0.25, 0.32, 0.18), (0.25, 0.1, 0.28, 0.22), (-0.1, 0.45, 0.22, 0.12)):
        ellipse(ctx, x + px * r, y + py * r, rx * r, ry * r)
        src(ctx, (0.25, 0.62, 0.32), 0.9)
        ctx.fill()
    ctx.restore()


def _burst(ctx, x, y, r, t, a=1.0):
    """Gamma-ray burst: violet-white flash with long spikes."""
    if a <= 0.01:
        return
    _glow(ctx, x, y, r * 3.5, (0.70, 0.45, 1.0), 0.45 * a)
    for q in range(12):
        ang = q * math.pi / 6 + t * 0.4
        ln = r * (3.2 if q % 3 == 0 else 1.8)
        ctx.move_to(x, y)
        ctx.line_to(x + ln * math.cos(ang), y + ln * math.sin(ang))
        src(ctx, (0.92, 0.85, 1.0), 0.7 * a)
        ctx.set_line_width(max(2, r * 0.08))
        ctx.stroke()
    _glow(ctx, x, y, r * 1.2, WH, a)


def _arrow(ctx, x, y0, y1, c, a=1.0, w=14):
    ctx.move_to(x, y0)
    ctx.line_to(x, y1 - 30)
    src(ctx, c, a)
    ctx.set_line_width(w)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    ctx.move_to(x - 34, y1 - 40)
    ctx.line_to(x, y1)
    ctx.line_to(x + 34, y1 - 40)
    ctx.close_path()
    ctx.fill()


def _scene(ctx, i, t, k):
    lt = t - _scene_start(i)
    cx, cy = W / 2, VIS_Y
    if i == 0:   # observatory sinking toward Earth, shaking
        _earth(ctx, cx, cy + 1150, 900)
        d = ease_in(seg(lt, 0.2, 2.6))
        sh = 6 * math.sin(t * 40) * d
        _satellite(ctx, cx + sh, cy - 120 + 160 * d, 0.95, 0.15 * math.sin(t * 2), glow=ORANGE if d > 0.3 else None)
        a = ease_back(seg(lt, 0.8, 1.3))
        if a > 0.01:
            _arrow(ctx, cx + 330, cy - 160, cy + 120, RED, a)
    elif i == 1:   # timeline: planned 2 years vs ~22
        x0, x1, y = 120, W - 120, cy - 40
        rrect(ctx, x0, y - 22, x1 - x0, 44, 22)
        src(ctx, WH, 0.15)
        ctx.fill()
        span = x1 - x0
        p = ease_out(seg(lt, 0.4, 1.4))
        rrect(ctx, x0, y - 22, max(44, span * 2 / 22 * p), 44, 22)
        src(ctx, CYAN)
        ctx.fill()
        text(ctx, "2004", x0 + 40, y - 60, 44, WH)
        if p > 0.5:
            text(ctx, "PLANNED", x0 + 120, y + 90, 36, CYAN, alpha=p)
        g = ease_io(seg(lt, 3.6, 6.2))
        if g > 0.01:
            rrect(ctx, x0, y + 150, max(44, span * g), 44, 22)
            src(ctx, Y_)
            ctx.fill()
            text(ctx, "ACTUAL", x0 + 100, y + 250, 36, Y_, alpha=min(1, g * 3))
            text(ctx, "2026", x0 + span * g - 40, y + 120, 44, WH, alpha=min(1, g * 3))
        _satellite(ctx, cx, cy - 330, 0.6, 0.0)
    elif i == 2:   # burst flashes, observatory swings to face it, stopwatch
        b = ease_out(seg(lt, 0.3, 0.9)) * (1 - 0.4 * seg(lt, 5.0, 8.0))
        bx, by = cx + 300, cy - 260
        _burst(ctx, bx, by, 70, t, b)
        turn = ease_io(seg(lt, 3.6, 5.2))
        ang0, ang1 = -0.9, math.atan2(by - (cy + 150), bx - (cx - 160)) + math.pi / 2
        _satellite(ctx, cx - 160, cy + 150, 0.75, lerp(ang0, ang1, turn))
        s = ease_back(seg(lt, 4.6, 5.1))
        if s > 0.01:
            _pill(ctx, "~1 MINUTE", cx + 220, cy + 260, 52, K_, Y_, s)
    elif i == 3:   # counters
        L = LINES[3]
        base = L["start"] - _scene_start(3)
        u = ease_out(seg(lt, base, base + 1.6))
        n = int(round(2000 * u, -1)) if u < 1 else 2000
        _burst(ctx, cx - 230, cy - 170, 45, t, 1.0)
        text(ctx, "{:,}{}".format(n, "+" if u >= 1 else ""), cx + 120, cy - 140, 110, Y_)
        text(ctx, "GAMMA-RAY BURSTS", cx, cy - 20, 40, WH)
        v = ease_out(seg(lt, base + 1.6, base + 3.0))
        if v > 0.01:
            m = int(round(1400 * v, -1)) if v < 1 else 1400
            _star(ctx, cx - 230, cy + 180, 40, ORANGE, t)
            text(ctx, "{:,}{}".format(m, "+" if v >= 1 else ""), cx + 120, cy + 210, 110, ORANGE, alpha=min(1, v * 3))
            text(ctx, "SUPERNOVAE", cx, cy + 330, 40, WH, alpha=min(1, v * 3))
    elif i == 4:   # Sun puffs atmosphere, orbit decays, no engine
        _star(ctx, 150, cy - 280, 90, SUNC, t)
        for q in range(3):
            f = (lt * 0.5 + q / 3.0) % 1.0
            ctx.arc(150, cy - 280, 120 + f * 320, -0.3, 1.2)
            src(ctx, Y_, 0.5 * (1 - f))
            ctx.set_line_width(6)
            ctx.stroke()
        ex, ey = cx + 120, cy + 100
        puff = ease_io(seg(lt, 0.8, 3.0))
        _earth(ctx, ex, ey, 150, atm=1 + 2.2 * puff)
        _glow(ctx, ex, ey, 150 * (1.25 + 0.5 * puff), (0.55, 0.8, 1.0), 0.35)
        f = ease_in(seg(lt, 2.0, 6.5))
        rr = lerp(260, 190, f)
        ang = -1.9 + lt * 0.7
        _satellite(ctx, ex + rr * math.cos(ang), ey + rr * math.sin(ang), 0.32, ang + math.pi / 2)
        c = ease_back(seg(lt, 4.6, 5.1))
        if c > 0.01:
            _pill(ctx, "NO ENGINE", cx + 250, cy - 330, 48, WH, RED, c)
    elif i == 5:   # rescue craft approaches, starts spinning, red X
        _satellite(ctx, cx + 170, cy - 60, 0.7, 0.1)
        ap = ease_out(seg(lt, 0.3, 2.2))
        rx, ry = lerp(-150, cx - 230, ap), lerp(cy + 400, cy + 160, ap)
        spin = ease_in(seg(lt, 2.4, 4.0)) * (lt - 2.4) * 6
        ctx.save()
        ctx.translate(rx, ry)
        ctx.rotate(spin)
        rrect(ctx, -55, -40, 110, 80, 12)
        src(ctx, (0.6, 0.62, 0.66))
        ctx.fill_preserve()
        src(ctx, K_)
        ctx.set_line_width(4)
        ctx.stroke()
        for sg in (-1, 1):
            ctx.move_to(sg * 55, 0)
            ctx.line_to(sg * 95, 0)
            src(ctx, TEAL)
            ctx.set_line_width(10)
            ctx.stroke()
        ctx.restore()
        text(ctx, "RESCUE CRAFT", rx, ry + 110, 32, WH, alpha=ap)
        x = ease_back(seg(lt, 3.8, 4.3))
        if x > 0.01:
            for sg in (1, -1):
                ctx.move_to(cx - 110 * x, cy + 40 - 110 * x * sg)
                ctx.line_to(cx + 110 * x, cy + 40 + 110 * x * sg)
            src(ctx, RED)
            ctx.set_line_width(26)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.stroke()
    elif i == 6:   # last look, then fiery fall toward Earth's limb
        _earth(ctx, cx, cy + 1150, 900)
        f = ease_in(seg(lt, 2.6, 6.4))
        sx, sy = lerp(cx - 120, cx + 160, f), lerp(cy - 250, cy + 60, f)
        if f > 0.05:
            for q in range(10):
                tq = q / 10.0
                _glow(ctx, sx - 120 * tq * f * 1.6, sy - 130 * tq * f * 1.6, 70 * (1 - tq), ORANGE, 0.5 * f)
        _satellite(ctx, sx, sy, lerp(0.7, 0.45, f), 0.6 * f, glow=ORANGE if f > 0.2 else None)
        c = ease_back(seg(lt, 0.4, 0.9)) * (1 - seg(lt, 2.4, 2.8))
        if c > 0.01:
            _pill(ctx, "LAST LOOK: OCT 20", cx, cy + 180, 50, K_, Y_, c)
        w = ease_back(seg(lt, 4.0, 4.5))
        if w > 0.01:
            _pill(ctx, "RE-ENTRY: WITHIN WEEKS", cx, cy + 260, 46, WH, ORANGE, w)
    elif i == 7:   # data stack + globe = public
        for q in range(4):
            a = ease_back(seg(lt, 0.1 * q, 0.1 * q + 0.4))
            if a > 0.01:
                y = cy + 120 - q * 90
                ellipse(ctx, cx - 200, y + 30, 150, 40)
                src(ctx, (0.10, 0.35, 0.55), a)
                ctx.fill()
                rrect(ctx, cx - 350, y - 30, 300, 60, 6)
                src(ctx, (0.15, 0.50, 0.75), a)
                ctx.fill()
                ellipse(ctx, cx - 200, y - 30, 150, 40)
                src(ctx, CYAN, a)
                ctx.fill()
        text(ctx, "12 TB", cx - 200, cy + 300, 70, Y_)
        g = ease_back(seg(lt, 1.6, 2.1))
        if g > 0.01:
            _earth(ctx, cx + 220, cy - 20, 150 * g)
            _pill(ctx, "PUBLIC", cx + 220, cy + 280, 54, K_, Y_, g)


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
