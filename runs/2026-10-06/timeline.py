"""2026-10-06 lab: Nobel Prize in Medicine for optogenetics (contract: DURATION + render_frame)."""
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
TEAL_D = (0.08, 0.42, 0.46)
ORANGE = (0.96, 0.55, 0.18)
BLUE = (0.18, 0.45, 0.98)
BLUE_L = (0.55, 0.75, 1.0)
GREEN = (0.30, 0.68, 0.30)
GREEN_D = (0.16, 0.45, 0.18)
PINK = (0.93, 0.45, 0.55)
GOLD = (0.93, 0.72, 0.18)
GREY = (0.55, 0.55, 0.55)
# (dark lead-in, yellow-on-black keyword)
HEADS = [
    ("LIGHT-SWITCH FOR THE BRAIN", "ON / OFF"),
    ("NOBEL PRIZE IN MEDICINE 2026", "3 WINNERS"),
    ("WHERE IT BEGAN", "GREEN ALGA"),
    ("THE SECRET PROTEIN", "CHANNELRHODOPSIN"),
    ("HOW IT WORKS", "LIGHT = SIGNAL"),
    ("2005 · RAT NERVE CELLS", "FIRED BY LIGHT"),
    ("THE NEW FIELD", "OPTOGENETICS"),
    ("WHAT IT REVEALS", "HOW BRAINS WORK"),
    ("2021 · A BLIND PATIENT", "PARTIAL SIGHT"),
    ("POND SCUM TO NOBEL", "LIGHT IS A SWITCH"),
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


def _neuron(ctx, x, y, s, lit=0.0, draw=1.0):
    """Cartoon neuron: soma, dendrites, axon; `lit` glows it yellow, `draw` grows the branches."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    if lit > 0.01:
        _glow(ctx, 0, 0, 230, Y_, 0.55 * lit)
    for k in range(6):
        a = k / 6 * 2 * math.pi + 0.4
        if 0.9 < a < 2.2:
            continue   # axon side
        L = 150 * draw
        ex, ey = L * math.cos(a), L * math.sin(a)
        ctx.move_to(0, 0)
        ctx.curve_to(ex * 0.4, ey * 0.4 + 20, ex * 0.7, ey * 0.7 - 15, ex, ey)
        for b in (-0.5, 0.5):
            ctx.move_to(ex * 0.75, ey * 0.75)
            ctx.line_to(ex * 0.75 + 55 * draw * math.cos(a + b), ey * 0.75 + 55 * draw * math.sin(a + b))
    _stroke(ctx, K_, 20)
    ctx.move_to(0, 0)
    ctx.curve_to(40, 120, -30, 200, 20, 330 * draw)
    _stroke(ctx, K_, 20)
    body = (lerp(0.93, 0.99, lit), lerp(0.55, 0.85, lit), lerp(0.55, 0.15, lit))
    for c, w in ((K_, 20), (body, 12)):
        pass
    ctx.save()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ellipse(ctx, 0, 0, 62, 56)
    src(ctx, body)
    ctx.fill_preserve()
    src(ctx, K_)
    ctx.set_line_width(7)
    ctx.stroke()
    ellipse(ctx, 6, -4, 20, 18)
    src(ctx, K_, 0.75)
    ctx.fill()
    ctx.restore()
    # axon terminals
    if draw > 0.9:
        for b in (-30, 0, 30):
            ctx.move_to(20, 330)
            ctx.line_to(20 + b, 375)
        _stroke(ctx, K_, 14)
    ctx.restore()


def _beam(ctx, x0, y0, x1, y1, w, c=BLUE, a=0.6):
    """Tapered light beam from (x0,y0) to (x1,y1)."""
    ang = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(ang), math.cos(ang)
    ctx.move_to(x0 + nx * 10, y0 + ny * 10)
    ctx.line_to(x1 + nx * w, y1 + ny * w)
    ctx.line_to(x1 - nx * w, y1 - ny * w)
    ctx.line_to(x0 - nx * 10, y0 - ny * 10)
    ctx.close_path()
    g = cairo.LinearGradient(x0, y0, x1, y1)
    g.add_color_stop_rgba(0, c[0], c[1], c[2], a)
    g.add_color_stop_rgba(1, c[0], c[1], c[2], a * 0.25)
    ctx.set_source(g)
    ctx.fill()


def _torch(ctx, x, y, ang, on=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    rrect(ctx, -110, -32, 120, 64, 16)
    src(ctx, (0.25, 0.27, 0.32))
    ctx.fill_preserve()
    src(ctx, K_)
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.move_to(10, -32)
    ctx.line_to(55, -52)
    ctx.line_to(55, 52)
    ctx.line_to(10, 32)
    ctx.close_path()
    src(ctx, (0.40, 0.42, 0.48))
    ctx.fill_preserve()
    src(ctx, K_)
    ctx.stroke()
    if on > 0.01:
        _glow(ctx, 58, 0, 70, BLUE_L, 0.9 * on)
    ctx.restore()


def _alga(ctx, x, y, s, t, ang=0.0):
    """Single-celled green alga: oval cell, two flagella, orange eyespot."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(s, s)
    for side in (-1, 1):
        ctx.move_to(70, side * 12)
        for q in range(1, 21):
            u = q / 20
            ctx.line_to(70 + 190 * u, side * (12 + 60 * u) + 22 * math.sin(u * 7 - t * 14 * side))
        _stroke(ctx, GREEN_D, 7)
    ellipse(ctx, 0, 0, 90, 66)
    g = cairo.RadialGradient(-20, -20, 10, 0, 0, 95)
    g.add_color_stop_rgb(0, 0.62, 0.88, 0.45)
    g.add_color_stop_rgb(1, GREEN[0], GREEN[1], GREEN[2])
    ctx.set_source(g)
    ctx.fill_preserve()
    src(ctx, GREEN_D)
    ctx.set_line_width(7)
    ctx.stroke()
    ellipse(ctx, -20, 5, 34, 28)
    src(ctx, GREEN_D, 0.6)
    ctx.fill()
    ellipse(ctx, 40, -28, 13, 10)
    src(ctx, ORANGE)
    ctx.fill()
    ctx.restore()


def _membrane(ctx, y, x0=60, x1=W - 60, gap=None):
    """Phospholipid bilayer: two rows of heads with tails; leaves a gap (x, w) for the channel."""
    for row, dy in ((0, -60), (1, 60)):
        for x in range(x0, x1, 38):
            if gap and gap[0] - gap[1] / 2 - 20 < x < gap[0] + gap[1] / 2 + 20:
                continue
            ty = y + dy + (30 if row == 0 else -30)
            ctx.move_to(x - 6, y + dy)
            ctx.line_to(x - 6, ty)
            ctx.move_to(x + 6, y + dy)
            ctx.line_to(x + 6, ty)
            _stroke(ctx, (0.75, 0.60, 0.40), 4)
            ellipse(ctx, x, y + dy, 17, 17)
            src(ctx, (0.96, 0.70, 0.45))
            ctx.fill_preserve()
            src(ctx, (0.55, 0.35, 0.20))
            ctx.set_line_width(3)
            ctx.stroke()


def _channel(ctx, x, y, open_):
    """Channelrhodopsin as two teal halves that slide apart when light opens it."""
    d = lerp(8, 46, open_)
    for side in (-1, 1):
        cx = x + side * (52 + d)
        rrect(ctx, cx - 50, y - 105, 100, 210, 34)
        src(ctx, TEAL)
        ctx.fill_preserve()
        src(ctx, TEAL_D)
        ctx.set_line_width(7)
        ctx.stroke()
        ellipse(ctx, cx, y - 30, 16, 16)
        src(ctx, Y_ if open_ > 0.5 else (0.35, 0.40, 0.45))
        ctx.fill()


def _ion(ctx, x, y, a=1.0):
    ellipse(ctx, x, y, 24, 24)
    src(ctx, PINK, a)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.set_line_width(4)
    ctx.stroke()
    ctx.move_to(x - 11, y)
    ctx.line_to(x + 11, y)
    ctx.move_to(x, y - 11)
    ctx.line_to(x, y + 11)
    _stroke(ctx, WH, 5, a)


def _spike_trace(ctx, x0, y0, w, h, u, spikes):
    """Voltage trace drawn left->right up to u (0..1); spikes at given fractions."""
    ctx.move_to(x0, y0)
    n = 160
    for q in range(1, int(n * u) + 1):
        f = q / n
        v = 0
        for sp in spikes:
            dd = (f - sp) * 60
            if -0.5 < dd < 2.5:
                v += math.exp(-((dd - 0.3) ** 2) * 3) - 0.25 * math.exp(-((dd - 1.4) ** 2) * 2)
        ctx.line_to(x0 + w * f, y0 - h * v)
    _stroke(ctx, K_, 7)


def _medal(ctx, x, y, r, k=1.0, t=0.0):
    """Generic gold medal (no real emblem): ribbon, disc, laurel arcs, star."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(k, k)
    for side in (-1, 1):
        ctx.move_to(side * 30, -r - 140)
        ctx.line_to(side * 95, -r - 140)
        ctx.line_to(side * 45, -r * 0.6)
        ctx.line_to(side * -10, -r * 0.6)
        ctx.close_path()
        src(ctx, TEAL if side < 0 else ORANGE)
        ctx.fill()
    _glow(ctx, 0, 0, r * 1.6, Y_, 0.35 + 0.1 * math.sin(t * 3))
    g = cairo.RadialGradient(-r * 0.3, -r * 0.3, r * 0.1, 0, 0, r)
    g.add_color_stop_rgb(0, 1.0, 0.92, 0.55)
    g.add_color_stop_rgb(1, GOLD[0] * 0.85, GOLD[1] * 0.8, GOLD[2])
    ctx.arc(0, 0, r, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill_preserve()
    src(ctx, (0.55, 0.38, 0.05))
    ctx.set_line_width(8)
    ctx.stroke()
    for side in (-1, 1):
        for j in range(6):
            a = math.pi / 2 + side * (0.5 + j * 0.32)
            lx, ly = r * 0.68 * math.cos(a), r * 0.68 * math.sin(a)
            ellipse(ctx, lx, ly, 14, 8)
            src(ctx, (0.62, 0.45, 0.08))
            ctx.fill()
    ctx.move_to(0, -r * 0.42)
    for j in range(1, 10):
        a = -math.pi / 2 + j * math.pi / 5
        rr = r * (0.42 if j % 2 == 0 else 0.18)
        ctx.line_to(rr * math.cos(a), rr * math.sin(a))
    ctx.close_path()
    src(ctx, (0.62, 0.45, 0.08))
    ctx.fill()
    ctx.restore()


def _dna(ctx, x, y, h, t, k=1.0):
    for strand in (0, 1):
        ctx.move_to(x + 70 * math.sin(t * 2 + strand * math.pi), y - h / 2)
        for q in range(1, 41):
            yy = y - h / 2 + h * q / 40
            ctx.line_to(x + 70 * math.sin(t * 2 + q * 0.35 + strand * math.pi), yy)
        _stroke(ctx, TEAL if strand else ORANGE, 10, k)
    for q in range(2, 40, 4):
        yy = y - h / 2 + h * q / 40
        ctx.move_to(x + 70 * math.sin(t * 2 + q * 0.35), yy)
        ctx.line_to(x + 70 * math.sin(t * 2 + q * 0.35 + math.pi), yy)
        _stroke(ctx, K_, 5, 0.6 * k)


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


def _brain(ctx, x, y, s):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-300, 40)
    ctx.curve_to(-340, -120, -220, -260, -60, -250)
    ctx.curve_to(40, -300, 230, -260, 290, -140)
    ctx.curve_to(360, -40, 320, 120, 200, 150)
    ctx.curve_to(150, 230, 40, 200, 20, 170)
    ctx.curve_to(-80, 230, -280, 200, -300, 40)
    ctx.close_path()
    src(ctx, (0.98, 0.78, 0.80))
    ctx.fill_preserve()
    src(ctx, K_)
    ctx.set_line_width(9)
    ctx.stroke()
    for (a, b, c, d, e, f) in ((-220, -60, -140, -160, -40, -100), (-60, -180, 40, -120, 140, -190),
                               (-200, 80, -100, 0, 0, 80), (60, -30, 160, 40, 240, -40),
                               (-60, 140, 20, 60, 120, 130)):
        ctx.move_to(a, b)
        ctx.curve_to(c, d, c, d, e, f)
    _stroke(ctx, (0.80, 0.45, 0.50), 7)
    ctx.restore()


def _eye(ctx, x, y, r, light=0.0):
    ellipse(ctx, x, y, r * 1.6, r)
    src(ctx, WH)
    ctx.fill_preserve()
    src(ctx, K_)
    ctx.set_line_width(8)
    ctx.stroke()
    ellipse(ctx, x, y, r * 0.62, r * 0.62)
    src(ctx, (0.35, 0.55, 0.75))
    ctx.fill()
    ellipse(ctx, x, y, r * 0.3, r * 0.3)
    src(ctx, K_)
    ctx.fill()
    if light > 0.01:
        _glow(ctx, x, y, r * 1.4, Y_, 0.5 * light)


def _pill(ctx, x, y, w, h, s, fill, fg, size=44, a=1.0):
    rrect(ctx, x - w / 2, y - h / 2, w, h, h / 2)
    src(ctx, fill, a)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.set_line_width(5)
    ctx.stroke()
    text(ctx, s, x, y + size * 0.35, size, fg, alpha=a)


# ------------------------------------------------------------------ scenes
def _scene(ctx, i, t):
    lt = t - _scene_start(i)
    if i == 0:   # torch flicks a neuron on/off
        on = 1.0 if (lt % 1.6) < 0.9 else 0.0
        _neuron(ctx, W / 2 + 60, VIS_Y - 120, 1.25, lit=on)
        if on:
            _beam(ctx, 230, VIS_Y + 210, W / 2 + 30, VIS_Y - 100, 110)
        _torch(ctx, 230, VIS_Y + 210, -0.85, on)
        x0 = W / 2 + 230
        _pill(ctx, x0, VIS_Y + 290, 230, 96, "ON" if on else "OFF", Y_ if on else (0.25, 0.25, 0.28),
              K_ if on else WH, 56)
    elif i == 1:   # medal + three name cards
        k = ease_back(seg(lt, 0.0, 0.6))
        _medal(ctx, W / 2, VIS_Y - 160, 150, k, t)
        names = ("KARL DEISSEROTH", "PETER HEGEMANN", "GEORG NAGEL")
        for j, nm in enumerate(names):
            u = ease_back(seg(lt, 1.8 + j * 1.1, 2.2 + j * 1.1))
            if u > 0.01:
                y = VIS_Y + 120 + j * 112
                ctx.save()
                ctx.translate(W / 2, y)
                ctx.scale(u, u)
                _pill(ctx, 0, 0, 720, 92, nm, K_ if j != 1 else TEAL, WH, 50)
                ctx.restore()
    elif i == 2:   # alga swims toward a lamp
        lx, ly = W - 170, VIS_Y - 60
        _glow(ctx, lx, ly, 260, Y_, 0.85)
        ellipse(ctx, lx, ly, 70, 70)
        src(ctx, (1, 0.95, 0.6))
        ctx.fill()
        for j in range(10):
            a = j / 10 * 2 * math.pi + t * 0.5
            ctx.move_to(lx + 90 * math.cos(a), ly + 90 * math.sin(a))
            ctx.line_to(lx + 135 * math.cos(a), ly + 135 * math.sin(a))
        _stroke(ctx, ORANGE, 8)
        u = ease_io(seg(lt, 0.2, 3.6))
        ax = lerp(260, lx - 330, u)
        _alga(ctx, ax, VIS_Y + 20 + 30 * math.sin(lt * 3), 1.35, t, ang=math.pi - 0.15)
        _pill(ctx, 300, VIS_Y + 300, 420, 92, "1 CELL", GREEN, WH, 52, ease_out(seg(lt, 0.6, 1.0)))
    elif i == 3:   # membrane with the channel protein; light opens it
        cy = VIS_Y - 20
        _membrane(ctx, cy, gap=(W / 2, 290))
        op = ease_io(seg(lt, 3.6, 4.4))
        if lt > 3.2:
            _beam(ctx, W / 2, VIS_Y - 420, W / 2, cy - 110, 120, BLUE, 0.55)
        _channel(ctx, W / 2, cy, op)
        lab = ease_out(seg(lt, 1.0, 1.5))
        _arrow(ctx, 240, VIS_Y + 260, W / 2 - 110, cy + 90, TEAL_D, 8, lab)
        text(ctx, "PROTEIN GATE", 250, VIS_Y + 320, 46, TEAL_D, alpha=lab)
        text(ctx, "OPEN" if op > 0.5 else "CLOSED", W - 230, VIS_Y + 320, 52,
             ORANGE if op > 0.5 else GREY)
    elif i == 4:   # blue light -> ions rush in -> electrical spike
        cy = VIS_Y - 160
        _membrane(ctx, cy, gap=(W / 2, 290))
        _beam(ctx, W / 2, VIS_Y - 520, W / 2, cy - 110, 120, BLUE, 0.6)
        _channel(ctx, W / 2, cy, 1.0)
        for j in range(7):
            ph = (lt * 0.7 + j / 7) % 1.0
            if lt < 0.8 + j * 0.15:
                continue
            _ion(ctx, W / 2 + 20 * math.sin(j * 2.1), lerp(cy - 190, cy + 210, ph), min(1, (1 - ph) * 3))
        u = seg(lt, 1.6, 4.8)
        rrect(ctx, 110, VIS_Y + 140, W - 220, 230, 24)
        src(ctx, WH, 0.9)
        ctx.fill_preserve()
        src(ctx, K_)
        ctx.set_line_width(5)
        ctx.stroke()
        _spike_trace(ctx, 140, VIS_Y + 320, W - 280, 150, u, (0.35, 0.7))
        text(ctx, "SIGNAL!", W - 240, VIS_Y + 200, 44, ORANGE, alpha=ease_out(seg(lt, 2.4, 2.8)))
    elif i == 5:   # DNA -> neuron; flashes of light trigger spikes
        u = ease_out(seg(lt, 0.0, 0.8))
        _dna(ctx, 220, VIS_Y - 200, 420, t, u)
        _arrow(ctx, 340, VIS_Y - 200, 520, VIS_Y - 200, K_, 10, ease_io(seg(lt, 0.8, 1.6)))
        flash = (lt > 2.4) and ((lt - 2.4) % 1.2) < 0.35
        if flash:
            _beam(ctx, W - 80, VIS_Y - 560, W / 2 + 230, VIS_Y - 280, 120, BLUE, 0.6)
        _neuron(ctx, W / 2 + 230, VIS_Y - 280, 0.9, lit=1.0 if flash else 0.0, draw=ease_out(seg(lt, 1.2, 2.2)))
        text(ctx, "RAT NERVE CELL", W / 2 + 230, VIS_Y + 130, 42, K_, alpha=ease_out(seg(lt, 1.8, 2.3)))
        rrect(ctx, 110, VIS_Y + 170, W - 220, 150, 24)
        src(ctx, WH, 0.9)
        ctx.fill_preserve()
        src(ctx, K_)
        ctx.set_line_width(5)
        ctx.stroke()
        n_sp = max(0, int((lt - 2.4) / 1.2) + 1) if lt > 2.4 else 0
        sp = tuple(0.12 + 0.2 * j for j in range(min(n_sp, 4)))
        _spike_trace(ctx, 140, VIS_Y + 280, W - 280, 90, seg(lt, 2.0, 6.4), sp)
    elif i == 6:   # brain with chosen neurons toggling
        _brain(ctx, W / 2, VIS_Y - 40, 1.35)
        pts = ((-200, -160), (-60, -230), (120, -180), (260, -60), (-250, 40), (40, -40), (180, 120), (-120, 140))
        for j, (px, py) in enumerate(pts):
            on = ((int(lt * 2.2) + j * 3) % 4) == 0 if lt > 1.0 else False
            x, y = W / 2 + px * 1.35, VIS_Y - 40 + py * 1.35
            if on:
                _glow(ctx, x, y, 70, Y_, 0.9)
            ellipse(ctx, x, y, 20, 20)
            src(ctx, Y_ if on else (0.45, 0.30, 0.35))
            ctx.fill_preserve()
            src(ctx, K_)
            ctx.set_line_width(4)
            ctx.stroke()
        _pill(ctx, W / 2, VIS_Y + 340, 520, 92, "LIVING BRAIN", K_, Y_, 50, ease_out(seg(lt, 0.8, 1.2)))
    elif i == 7:   # three research areas pop in
        _brain(ctx, W / 2, VIS_Y - 170, 0.8)
        labels = (("MEMORY", TEAL), ("BEHAVIOUR", ORANGE), ("BRAIN DISORDERS", K_))
        for j, (s, c) in enumerate(labels):
            u = ease_back(seg(lt, 0.3 + j * 0.7, 0.7 + j * 0.7))
            if u > 0.01:
                y = VIS_Y + 80 + j * 110
                ctx.save()
                ctx.translate(W / 2, y)
                ctx.scale(u, u)
                _pill(ctx, 0, 0, 640, 90, s, c, WH, 50)
                ctx.restore()
    elif i == 8:   # eye + light goggles, view returns
        gy = VIS_Y - 200
        rrect(ctx, 130, gy - 130, W - 260, 260, 110)
        src(ctx, (0.18, 0.18, 0.22))
        ctx.fill_preserve()
        src(ctx, K_)
        ctx.set_line_width(8)
        ctx.stroke()
        light = ease_io(seg(lt, 2.0, 3.4))
        for ex in (W / 2 - 200, W / 2 + 200):
            _eye(ctx, ex, gy, 70, light)
            ellipse(ctx, ex, gy, 165, 105)
            src(ctx, (0.55, 0.75, 1.0), 0.25 + 0.35 * light)
            ctx.fill()
        text(ctx, "LIGHT GOGGLES", W / 2, gy + 200, 44, K_)
        # "blurry -> shapes" panel
        px, py = W / 2, VIS_Y + 150
        rrect(ctx, px - 300, py - 110, 600, 220, 26)
        src(ctx, (0.15, 0.15, 0.18))
        ctx.fill()
        ctx.save()
        rrect(ctx, px - 300, py - 110, 600, 220, 26)
        ctx.clip()
        a = light
        rrect(ctx, px - 200, py - 40, 120, 110, 10)
        src(ctx, (0.9, 0.9, 0.9), a)
        ctx.fill()
        ellipse(ctx, px + 120, py + 15, 60, 60)
        src(ctx, Y_, a)
        ctx.fill()
        ctx.restore()
        text(ctx, "40 YRS BLIND", 260, VIS_Y + 330, 42, GREY, alpha=1 - light * 0.4)
        text(ctx, "SEES SHAPES", W - 260, VIS_Y + 330, 42, ORANGE, alpha=light)
    elif i == 9:   # alga -> medal
        _alga(ctx, 240, VIS_Y - 80, 0.95, t, ang=math.pi)
        _arrow(ctx, 400, VIS_Y - 80, 620, VIS_Y - 80, K_, 12, ease_io(seg(lt, 0.4, 1.2)))
        k = ease_back(seg(lt, 1.0, 1.6))
        if k > 0.01:
            _medal(ctx, W - 240, VIS_Y - 20, 120, k, t)
        on = (lt % 1.0) < 0.6
        _neuron(ctx, W / 2, VIS_Y + 260, 0.55, lit=1.0 if on else 0.0)


def _headline(ctx, i, t):
    t0 = _scene_start(i)
    lead, key = HEADS[i]
    a = ease_out(seg(t, t0 + 0.05, t0 + 0.4))
    text(ctx, lead, W / 2, 380, 46, K_, alpha=a)
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
