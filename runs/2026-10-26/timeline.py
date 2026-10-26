"""2026-10-26 lab: dwarf reedsnakes roll like wheels to escape, ~4x faster than slithering (contract: DURATION + render_frame)."""
import json
import math
import os
import cairo
from gfx import W, H, ease_back, ease_out, ease_io, seg, src, text, ellipse, rrect, lerp, wrap
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
WH = (1, 1, 1)
CREAM = (0.99, 0.96, 0.88)
GRID = (0.85, 0.80, 0.68)
TEAL = (0.14, 0.60, 0.62)
ORANGE = (0.96, 0.55, 0.18)
RED = (0.88, 0.25, 0.22)
GREY = (0.55, 0.55, 0.55)
SNAKE = (0.50, 0.33, 0.20)
SNAKE_D = (0.24, 0.15, 0.09)
BELLY = (0.93, 0.80, 0.55)
SOIL = (0.62, 0.47, 0.32)
# (dark lead-in, yellow-on-black keyword)
HEADS = [
    ("NOT SLITHERING", "IT ROLLS"),
    ("MEET THE", "DWARF REEDSNAKE"),
    ("FILMED IN JAPAN", "13 SNAKES"),
    ("TOP SPEED", "3.7 m/s"),
    ("HOW IT ROLLS", "LEFT, RIGHT"),
    ("THE STRANGEST PART", "STEADY HEAD"),
    ("TIGHT SPACE", "20 cm TRACK"),
    ("CURRENT BIOLOGY", "TOHO UNIVERSITY"),
]
VIS_Y = 1000
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
def _background(ctx, t):
    src(ctx, CREAM)
    ctx.paint()
    off = (t * 6) % 60
    for x in range(0, W + 60, 60):
        ctx.move_to(x - off, 0)
        ctx.line_to(x - off, H)
    for y in range(0, H + 60, 60):
        ctx.move_to(0, y + off)
        ctx.line_to(W, y + off)
    src(ctx, GRID, 0.45)
    ctx.set_line_width(2)
    ctx.stroke()


# ------------------------------------------------------------------ props
def _glow(ctx, x, y, r, c, a=1.0):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, c[0], c[1], c[2], a)
    g.add_color_stop_rgba(1, c[0], c[1], c[2], 0)
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()


def _stroke(ctx, c, w, a=1.0):
    src(ctx, c, a)
    ctx.set_line_width(w)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke()

def _arrow(ctx, x0, y0, x1, y1, c=K_, w=10, u=1.0):
    x1, y1 = lerp(x0, x1, u), lerp(y0, y1, u)
    ctx.move_to(x0, y0)
    ctx.line_to(x1, y1)
    _stroke(ctx, c, w)
    if u > 0.2:
        a = math.atan2(y1 - y0, x1 - x0)
        ctx.move_to(x1, y1)
        ctx.line_to(x1 - 34 * math.cos(a - 0.5), y1 - 34 * math.sin(a - 0.5))
        ctx.move_to(x1, y1)
        ctx.line_to(x1 - 34 * math.cos(a + 0.5), y1 - 34 * math.sin(a + 0.5))
        _stroke(ctx, c, w)


def _pill(ctx, x, y, w, h, s, fill, fg, size=44, a=1.0):
    rrect(ctx, x - w / 2, y - h / 2, w, h, h / 2)
    src(ctx, fill, a)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.set_line_width(5)
    ctx.stroke()
    text(ctx, s, x, y + size * 0.35, size, fg, alpha=a)


PURPLE = (0.55, 0.36, 0.80)

# ------------------------------------------------------------------ snake
def _head(ctx, x, y, ang, s=1.0, a=1.0):
    """Snake head pointing along ang, with eye and flicking tongue."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(s, s)
    ctx.move_to(40, 0)
    ctx.line_to(62, 0)
    ctx.move_to(62, 0)
    ctx.line_to(74, -8)
    ctx.move_to(62, 0)
    ctx.line_to(74, 8)
    _stroke(ctx, RED, 5, a)
    ellipse(ctx, 6, 0, 44, 30)
    src(ctx, SNAKE, a)
    ctx.fill_preserve()
    src(ctx, SNAKE_D, a)
    ctx.set_line_width(6)
    ctx.stroke()
    ellipse(ctx, 18, -12, 8, 8)
    src(ctx, K_, a)
    ctx.fill()
    ellipse(ctx, 20, -14, 3, 3)
    src(ctx, WH, a)
    ctx.fill()
    ctx.restore()


def _body(ctx, pts, w=44, roll=0.0, a=1.0):
    """Thick snake body along a polyline; animated dashed bands show rotation."""
    def path():
        ctx.move_to(*pts[0])
        for p in pts[1:]:
            ctx.line_to(*p)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    path()
    src(ctx, SNAKE_D, a)
    ctx.set_line_width(w + 12)
    ctx.stroke()
    path()
    src(ctx, SNAKE, a)
    ctx.set_line_width(w)
    ctx.stroke()
    path()
    ctx.set_dash([w * 0.35, w * 0.9], -roll)
    src(ctx, BELLY, 0.85 * a)
    ctx.set_line_width(w * 0.8)
    ctx.set_line_cap(cairo.LINE_CAP_BUTT)
    ctx.stroke()
    ctx.set_dash([])
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)


def _wheel(ctx, cx, cy, R, t, a=1.0, speed=1.0, hl=None):
    """Rolling snake: a body loop with bands running round it, head held out in front at a fixed height.
    hl: None, or 'L'/'R' to highlight the side currently striking."""
    roll = t * 520 * speed
    pts = []
    a0 = -0.95
    for q in range(46):
        ang = a0 - q * (5.25 / 45)          # body runs back round the loop (anticlockwise) to the tail
        pts.append((cx + R * math.cos(ang), cy + R * math.sin(ang)))
    # neck from loop to steady head
    hx, hy = cx + R * 1.25, cy - R * 0.95
    neck = [(hx - 50, hy + 6), (cx + R * 1.0, cy - R * 0.75), pts[0]]
    _body(ctx, neck[::-1] + [], 44, 0, a)
    _body(ctx, pts, 44, -roll, a)
    if hl:
        side = 1 if hl == "R" else -1
        ang = math.pi / 2 + side * 0.55
        gx, gy = cx + R * math.cos(ang), cy + R * math.sin(ang)
        _glow(ctx, gx, gy + 20, 120, Y_, 0.9 * a)
        for q in range(5):
            dx = (q - 2) * 34
            ctx.move_to(gx + dx, gy + R * 0.0 + 46)
            ctx.line_to(gx + dx * 1.6, gy + 80)
        _stroke(ctx, ORANGE, 6, a)
    _head(ctx, hx, hy, 0.0, 1.0, a)
    # motion arcs behind the loop
    for q in range(3):
        r = R + 50 + q * 26
        ctx.arc_negative(cx, cy, r, math.pi * 1.15 - q * 0.05, math.pi * 0.70 + q * 0.08)
        _stroke(ctx, GREY, 6, 0.5 * a)


def _ground(ctx, y, a=1.0):
    ctx.rectangle(0, y, W, 26)
    src(ctx, SOIL, a)
    ctx.fill()
    for q in range(0, W, 70):
        ellipse(ctx, q + 20, y + 13, 8, 5)
        src(ctx, SNAKE_D, 0.4 * a)
        ctx.fill()


def _wavy(ctx, x0, x1, y, amp, t, a=1.0, w=40):
    """Slithering snake (lateral undulation) heading right."""
    pts = []
    n = 40
    for q in range(n + 1):
        x = lerp(x0, x1, q / n)
        pts.append((x, y + amp * math.sin(q / n * 2.6 * math.pi - t * 6)))
    _body(ctx, pts, w, 0, a)
    dx = pts[-1][0] - pts[-2][0]
    dy = pts[-1][1] - pts[-2][1]
    _head(ctx, pts[-1][0] + 18, pts[-1][1], math.atan2(dy, dx), 0.9, a)


def _camera(ctx, x, y, ang, s=1.0, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(s, s)
    rrect(ctx, -70, -45, 120, 90, 16)
    src(ctx, K_, a)
    ctx.fill()
    ctx.move_to(50, -22)
    ctx.line_to(95, -40)
    ctx.line_to(95, 40)
    ctx.line_to(50, 22)
    ctx.close_path()
    src(ctx, K_, a)
    ctx.fill()
    ellipse(ctx, -10, 0, 26, 26)
    src(ctx, TEAL, a)
    ctx.fill()
    ellipse(ctx, -46, -30, 7, 7)
    src(ctx, RED, a)
    ctx.fill()
    ctx.restore()


def _bar(ctx, x, y, w, h, c, label, val, u, a=1.0):
    rrect(ctx, x, y, max(h, w * u), h, h / 2)
    src(ctx, c, a)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.set_line_width(5)
    ctx.stroke()
    text(ctx, label, x, y - 24, 40, K_, align="left", alpha=a)
    if u > 0.95:
        text(ctx, val, x + w * u - 20, y + h * 0.68, 40, K_ if c != K_ else WH, align="right", alpha=a)


# ------------------------------------------------------------------ scenes
def _scene(ctx, i, t):
    lt = t - _scene_start(i)
    cx, cy = W / 2, VIS_Y
    if i == 0:   # snake wheel rolls in from the left
        _ground(ctx, cy + 200)
        u = ease_out(seg(lt, 0.0, 1.6))
        x = lerp(-250, cx - 60, u)
        _wheel(ctx, x, cy + 30, 150, t, speed=1.0 + 1.5 * (1 - u))
        k = ease_back(seg(lt, 1.7, 2.1))
        if k > 0.01:
            _pill(ctx, cx, cy - 240, 420 * k, 90 * k, "ESCAPE MODE", Y_, K_, 46 * k)
    elif i == 1:   # slithering snake + Borneo pill
        _ground(ctx, cy + 120)
        _wavy(ctx, 150, 840, cy + 40, 45, t)
        k = ease_back(seg(lt, 0.6, 1.0))
        if k > 0.01:
            _pill(ctx, cx - 210, cy - 200, 280 * k, 84 * k, "TINY", WH, K_, 46 * k)
        k2 = ease_back(seg(lt, 2.4, 2.8))
        if k2 > 0.01:
            _pill(ctx, cx + 180, cy - 200, 340 * k2, 84 * k2, "BORNEO", TEAL, WH, 46 * k2)
    elif i == 2:   # three cameras at different angles on one rolling snake
        _ground(ctx, cy + 170)
        _wheel(ctx, cx - 30, cy + 30, 120, t)
        for j, (x, y, ang) in enumerate(((180, cy - 260, 0.75), (cx, cy - 330, math.pi / 2), (900, cy - 260, math.pi - 0.75))):
            k = ease_back(seg(lt, 0.4 + 0.5 * j, 0.8 + 0.5 * j))
            if k > 0.01:
                _camera(ctx, x, y, ang, 0.9 * k)
        k = ease_back(seg(lt, 2.6, 3.0))
        if k > 0.01:
            _pill(ctx, cx, cy + 270, 460 * k, 84 * k, "3 SPECIES", Y_, K_, 46 * k)
    elif i == 3:   # slither vs roll bars, x4 stamp
        x0, w = 140, 800
        u1 = ease_out(seg(lt, 0.5, 1.3))
        _bar(ctx, x0, cy - 200, w * 0.25, 80, TEAL, "SLITHERING", "", u1)
        L = LINES[3]
        base = L["start"] - _scene_start(3)
        u2 = ease_out(seg(lt, 1.0, 2.6))
        _bar(ctx, x0, cy + 20, w, 80, ORANGE, "ROLLING", "3.7 m/s", u2)
        k = ease_back(seg(lt, base + L["dur"] * 0.55, base + L["dur"] * 0.55 + 0.4))
        if k > 0.01:
            ctx.save()
            ctx.translate(cx, cy + 260)
            ctx.rotate(-0.12)
            ctx.scale(k, k)
            rrect(ctx, -170, -85, 340, 170, 30)
            src(ctx, K_)
            ctx.fill()
            text(ctx, "~4x", 0, 38, 110, Y_)
            ctx.restore()
    elif i == 4:   # alternating left / right strokes
        _ground(ctx, cy + 220)
        L = LINES[4]
        base = L["start"] - _scene_start(4)
        alt = lt > base + L["dur"] * 0.25
        side = "L" if int((lt - base) / 0.45) % 2 == 0 else "R"
        _wheel(ctx, cx - 40, cy + 30, 170, t, hl=side if alt else None)
        if alt:
            for s_, x in (("L", cx - 300), ("R", cx + 220)):
                on = s_ == side
                rrect(ctx, x - 50, cy - 330, 100, 100, 20)
                src(ctx, Y_ if on else WH)
                ctx.fill_preserve()
                src(ctx, K_)
                ctx.set_line_width(5)
                ctx.stroke()
                text(ctx, s_, x, cy - 255, 70, K_)
        k = ease_back(seg(lt, 0.3, 0.7)) * (0 if alt else 1)
        if k > 0.01:
            _pill(ctx, cx, cy - 280, 440 * k, 84 * k, "NOT A STIFF TUBE", WH, K_, 42 * k)
    elif i == 5:   # steady head on a dashed level line while the body spins
        _ground(ctx, cy + 230)
        R = 170
        hy = cy + 40 - R * 0.95
        ctx.move_to(80, hy)
        ctx.line_to(W - 80, hy)
        ctx.set_dash([24, 18])
        _stroke(ctx, TEAL, 6)
        ctx.set_dash([])
        _wheel(ctx, cx - 100, cy + 40, R, t, speed=1.6)
        k = ease_back(seg(lt, 1.6, 2.0))
        if k > 0.01:
            _pill(ctx, cx + 110, hy - 120, 520 * k, 84 * k, "FACING FORWARD", TEAL, WH, 42 * k)
    elif i == 6:   # narrow track with ruler
        y0, y1 = cy - 140, cy + 220
        for y in (y0, y1):
            rrect(ctx, 60, y - 14, W - 120, 28, 14)
            src(ctx, GREY)
            ctx.fill()
        u = seg(lt, 0.0, 2.7)
        _wheel(ctx, lerp(150, 760, u), cy + 60, 120, t, speed=1.4)
        k = ease_out(seg(lt, 0.8, 1.3))
        if k > 0.01:
            x = 990
            _arrow(ctx, x, y0 + 40, x, y1 - 40, K_, 8, k)
            _arrow(ctx, x, y1 - 40, x, y0 + 40, K_, 8, k)
            _pill(ctx, x - 40, cy + 40, 170, 76, "20 cm", Y_, K_, 40, k)
    elif i == 7:   # journal page + rolling snake
        k = ease_back(seg(lt, 0.1, 0.5))
        ctx.save()
        ctx.translate(cx, cy - 60)
        ctx.scale(k, k)
        rrect(ctx, -300, -260, 600, 520, 26)
        src(ctx, WH)
        ctx.fill_preserve()
        src(ctx, K_)
        ctx.set_line_width(6)
        ctx.stroke()
        rrect(ctx, -300, -260, 600, 90, 26)
        src(ctx, TEAL)
        ctx.fill()
        text(ctx, "NEW STUDY", 0, -200, 44, WH)
        for q in range(3):
            rrect(ctx, -240, -130 + q * 44, 480 - q * 90, 18, 9)
            src(ctx, GRID)
            ctx.fill()
        ctx.restore()
        if k > 0.5:
            _wheel(ctx, cx - 40, cy + 110, 80, t, a=min(1, (k - 0.5) * 2))
        L = LINES[7]
        base = L["start"] - _scene_start(7)
        k2 = ease_back(seg(lt, base + L["dur"] * 0.5, base + L["dur"] * 0.5 + 0.4))
        if k2 > 0.01:
            _pill(ctx, cx, cy + 300, 420 * k2, 96 * k2, "JUST ROLL", Y_, K_, 50 * k2)


def _headline(ctx, i, t):
    t0 = _scene_start(i)
    lead, key = HEADS[i]
    a = ease_out(seg(t, t0 + 0.05, t0 + 0.4))
    text(ctx, lead, W / 2, 345, 46, K_, alpha=a)
    k = ease_back(seg(t, t0 + 0.15, t0 + 0.5))
    size = 100 if len(key) <= 10 else 80 if len(key) <= 14 else 70
    if k > 0.01:
        ctx.save()
        ctx.translate(W / 2, 480)
        ctx.scale(k, k)
        ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(size)
        tw = ctx.text_extents(key).x_advance
        rrect(ctx, -tw / 2 - 34, -size * 0.95, tw + 68, size * 1.3, 24)
        src(ctx, K_)
        ctx.fill()
        text(ctx, key, 0, 0, size, Y_)
        ctx.restore()


def _wipe(ctx, t):
    """Yellow lab-slide wipe at each scene change."""
    for i in range(1, len(LINES)):
        u = seg(t, _scene_start(i) - 0.2, _scene_start(i) + 0.2)
        if 0 < u < 1:
            x = lerp(-W, W, u)
            ctx.rectangle(x, 0, W, H)
            src(ctx, Y_, 0.9 * math.sin(math.pi * u))
            ctx.fill()


def render_frame(t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    _background(ctx, t)
    i = _active(t)
    if i is not None:
        k = ease_out(seg(t, _scene_start(i), _scene_start(i) + 0.4))
        ctx.save()
        ctx.push_group()
        _scene(ctx, i, t)
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
    _wipe(ctx, t)
    brand.watermark(ctx)
    brand.end_card(ctx, t, DURATION - 1.4)
    surf.flush()
    return surf
