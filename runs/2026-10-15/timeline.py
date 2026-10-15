"""2026-10-15 cosmic: Perseverance sets the off-world driving record (contract: DURATION + render_frame)."""
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
# (white lead-in, yellow keyword)
HEADS = [
    ("MARS · NEW RECORD", "FARTHEST DRIVE"),
    ("OCTOBER 11, 2026", "45.22 KM"),
    ("OLD RECORD · OPPORTUNITY", "45.16 KM"),
    ("SAME DISTANCE", "15 YRS vs 5.5"),
    ("THE SECRET", "IT DRIVES ITSELF"),
    ("AUTONAV", "THINKING WHILE DRIVING"),
    ("EVERY LOOK", "600,000 POINTS"),
    ("PLAN: 12.4 MILES MAX", "INTO THE 2030s"),
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


def _mars(ctx, x, y, r, t=0.0):
    _glow(ctx, x, y, r * 1.35, ORANGE, 0.35)
    g = cairo.RadialGradient(x - r * 0.35, y - r * 0.35, r * 0.1, x, y, r)
    g.add_color_stop_rgb(0, 0.95, 0.55, 0.30)
    g.add_color_stop_rgb(1, 0.45, 0.14, 0.06)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    ctx.save()
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.clip()
    for dx, dy, rr in ((-0.35, -0.1, 0.12), (0.2, 0.3, 0.09), (0.4, -0.35, 0.07), (-0.1, 0.5, 0.1), (0.05, -0.5, 0.06)):
        xx = x + ((dx + t * 0.02 + 1.2) % 2.4 - 1.2) * r
        ellipse(ctx, xx, y + dy * r, rr * r, rr * r * 0.8)
        src(ctx, DUST, 0.6)
        ctx.fill()
    ellipse(ctx, x, y - r * 0.92, r * 0.35, r * 0.1)   # polar cap
    src(ctx, WH, 0.75)
    ctx.fill()
    ctx.rectangle(x + r * 0.2, y - r, r, 2 * r)        # terminator shadow
    src(ctx, (0, 0, 0.03), 0.35)
    ctx.fill()
    ctx.restore()


def _ground(ctx, y0, scroll=0.0):
    """Martian terrain from y0 down to y0+420 with scrolling rocks."""
    g = cairo.LinearGradient(0, y0, 0, y0 + 420)
    g.add_color_stop_rgb(0, 0.80, 0.42, 0.22)
    g.add_color_stop_rgb(1, 0.42, 0.16, 0.08)
    ctx.move_to(0, y0)
    for x in range(0, W + 60, 60):
        ctx.line_to(x, y0 - 18 * math.sin(x * 0.006 + 1.3) - 8 * math.sin(x * 0.021))
    ctx.line_to(W, y0 + 420)
    ctx.line_to(0, y0 + 420)
    ctx.close_path()
    ctx.set_source(g)
    ctx.fill()
    for j in range(9):
        x = ((j * 157 - scroll) % (W + 200)) - 100
        y = y0 + 60 + (j * 73) % 300
        s = 0.6 + (j % 3) * 0.35
        ellipse(ctx, x, y, 34 * s, 18 * s)
        src(ctx, DUST)
        ctx.fill()
        ellipse(ctx, x - 8 * s, y - 6 * s, 18 * s, 7 * s)
        src(ctx, SAND, 0.7)
        ctx.fill()


def _wheel(ctx, x, y, r, ang):
    ellipse(ctx, x, y, r, r)
    src(ctx, (0.22, 0.22, 0.25))
    ctx.fill()
    ellipse(ctx, x, y, r * 0.55, r * 0.55)
    src(ctx, (0.65, 0.66, 0.70))
    ctx.fill()
    for q in range(4):
        a = ang + q * math.pi / 2
        ctx.move_to(x, y)
        ctx.line_to(x + r * 0.9 * math.cos(a), y + r * 0.9 * math.sin(a))
        src(ctx, (0.15, 0.15, 0.18))
        ctx.set_line_width(max(2, r * 0.12))
        ctx.stroke()


def _rover(ctx, x, y, s=1.0, ang=0.0, cam=0.0):
    """Generic six-wheeled rover (bottom of wheels at y)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for wx in (-120, 0, 120):
        _wheel(ctx, wx, -38, 38, ang)
    ctx.move_to(-120, -38)
    ctx.line_to(-60, -100)
    ctx.line_to(0, -38)
    ctx.move_to(0, -38)
    ctx.line_to(60, -100)
    ctx.line_to(120, -38)
    src(ctx, (0.75, 0.75, 0.78))
    ctx.set_line_width(9)
    ctx.stroke()
    rrect(ctx, -150, -165, 300, 72, 10)                 # body
    src(ctx, (0.93, 0.93, 0.95))
    ctx.fill_preserve()
    src(ctx, K_)
    ctx.set_line_width(4)
    ctx.stroke()
    rrect(ctx, -140, -158, 120, 20, 5)
    src(ctx, Y_)
    ctx.fill()
    rrect(ctx, -205, -170, 60, 60, 8)                   # power unit at the back
    src(ctx, (0.45, 0.45, 0.50))
    ctx.fill()
    for q in range(4):
        ctx.move_to(-205 + q * 15 + 8, -170)
        ctx.line_to(-205 + q * 15 + 8, -110)
        src(ctx, (0.3, 0.3, 0.33))
        ctx.set_line_width(3)
        ctx.stroke()
    ctx.move_to(100, -165)                              # mast
    ctx.line_to(100, -300)
    src(ctx, (0.85, 0.85, 0.88))
    ctx.set_line_width(12)
    ctx.stroke()
    rrect(ctx, 70, -340, 80, 48, 8)                     # camera head
    src(ctx, (0.93, 0.93, 0.95))
    ctx.fill_preserve()
    src(ctx, K_)
    ctx.set_line_width(4)
    ctx.stroke()
    for ex in (98, 128):
        ellipse(ctx, ex, -316, 9, 9)
        src(ctx, (0.1, 0.1, 0.12))
        ctx.fill()
        if cam > 0:
            _glow(ctx, ex, -316, 26, CYAN, 0.8 * cam)
    ctx.move_to(-60, -165)                              # antenna
    ctx.line_to(-60, -215)
    src(ctx, (0.7, 0.7, 0.72))
    ctx.set_line_width(6)
    ctx.stroke()
    ellipse(ctx, -60, -222, 30, 9)
    src(ctx, (0.85, 0.85, 0.88))
    ctx.fill()
    ctx.restore()


def _tracks(ctx, x0, x1, y):
    for dy in (-6, 10):
        ctx.move_to(x0, y + dy)
        ctx.line_to(x1, y + dy)
        src(ctx, DUST, 0.8)
        ctx.set_line_width(7)
        ctx.set_dash([18, 10])
        ctx.stroke()
    ctx.set_dash([])


def _pill(ctx, s, x, y, size, fg, bg, a=1.0, pad=36):
    ctx.select_font_face(gfx.FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    w = ctx.text_extents(s).x_advance + pad * 2
    rrect(ctx, x - w / 2, y - size * 0.95, w, size * 1.45, size * 0.5)
    src(ctx, bg, 0.9 * a)
    ctx.fill()
    text(ctx, s, x, y, size, fg, alpha=a)


def _trophy(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    _glow(ctx, 0, -40, 150, GOLD, 0.4 * a)
    ctx.move_to(-70, -120)
    ctx.line_to(70, -120)
    ctx.curve_to(70, -20, 30, 10, 0, 10)
    ctx.curve_to(-30, 10, -70, -20, -70, -120)
    src(ctx, GOLD, a)
    ctx.fill()
    rrect(ctx, -12, 10, 24, 40, 4)
    ctx.fill()
    rrect(ctx, -50, 48, 100, 24, 6)
    ctx.fill()
    for sg in (1, -1):
        ctx.arc(sg * 78, -85, 26, 0, 2 * math.pi)
        src(ctx, GOLD, a)
        ctx.set_line_width(10)
        ctx.stroke()
    text(ctx, "#1", 0, -48, 64, K_, alpha=a)
    ctx.restore()


# ------------------------------------------------------------------ scenes
def _scene(ctx, i, t, k):
    lt = t - _scene_start(i)
    if i == 0:   # Mars rises, rover rolls in, trophy pops
        u = ease_out(seg(lt, 0.0, 1.2))
        _mars(ctx, W / 2, lerp(VIS_Y + 200, VIS_Y + 60, u), 300, t)
        rx = lerp(-200, W / 2 + 40, ease_out(seg(lt, 0.2, 1.8)))
        _rover(ctx, rx, VIS_Y - 160, 0.55, ang=lt * 4, cam=0.4)
        tk = ease_back(seg(lt, 1.8, 2.3))
        if tk > 0.01:
            _trophy(ctx, W / 2 - 280, VIS_Y - 240, 0.9 * tk)
    elif i == 1:   # driving on the ground, odometer counting up
        _ground(ctx, VIS_Y + 20, scroll=lt * 160)
        _tracks(ctx, 0, W / 2 - 150, VIS_Y + 200)
        _rover(ctx, W / 2 + 40, VIS_Y + 210, 0.85, ang=lt * 5, cam=0.3)
        v = 45.22 * ease_out(seg(lt, 0.3, 3.6))
        rrect(ctx, W / 2 - 300, VIS_Y - 330, 600, 170, 26)
        src(ctx, K_, 0.9)
        ctx.fill_preserve()
        src(ctx, Y_)
        ctx.set_line_width(5)
        ctx.stroke()
        text(ctx, "ODOMETER", W / 2, VIS_Y - 280, 36, WH)
        text(ctx, "%05.2f km" % v, W / 2, VIS_Y - 190, 84, Y_)
    elif i == 2:   # bar race: Opportunity vs Perseverance
        u = ease_io(seg(lt, 0.3, 3.0))
        x0, full = 120, 800
        rows = (("OPPORTUNITY", 45.16, TEAL, "28.06 mi"), ("PERSEVERANCE", 45.22, Y_, "28.10 mi"))
        for j, (name, km, c, mi) in enumerate(rows):
            y = VIS_Y - 170 + j * 260
            text(ctx, name, x0, y - 30, 48, WH, align="left")
            rrect(ctx, x0, y, full, 80, 20)
            src(ctx, WH, 0.12)
            ctx.fill()
            ww = full * (km / 45.22) * u * (0.985 if j == 0 else 1.0)
            if ww > 30:
                rrect(ctx, x0, y, ww, 80, 20)
                src(ctx, c)
                ctx.fill()
            text(ctx, mi, x0 + full, y + 140, 46, c, align="right", alpha=ease_out(seg(lt, 2.6, 3.2)))
        a = ease_back(seg(lt, 3.6, 4.1))
        if a > 0.01:
            _pill(ctx, "+60 METRES", W / 2, VIS_Y + 330, 52, K_, Y_, a)
    elif i == 3:   # years comparison: two timelines
        x0, per = 120, 840 / 15.0
        rows = (("OPPORTUNITY", 15.0, TEAL, "~15 YEARS"), ("PERSEVERANCE", 5.5, Y_, "~5.5 YEARS"))
        for j, (name, yrs, c, lab) in enumerate(rows):
            y = VIS_Y - 160 + j * 280
            text(ctx, name, x0, y - 30, 48, WH, align="left")
            u = ease_io(seg(lt, 0.3 + j * 0.4, 0.3 + j * 0.4 + 0.18 * yrs))
            for q in range(15):
                rrect(ctx, x0 + q * per + 4, y, per - 8, 70, 8)
                src(ctx, WH, 0.10)
                ctx.fill()
            ww = per * yrs * u
            if ww > 10:
                rrect(ctx, x0, y, ww, 70, 12)
                src(ctx, c)
                ctx.fill()
            text(ctx, lab, x0, y + 135, 46, c, align="left", alpha=ease_out(seg(lt, 1.0 + j * 1.2, 1.5 + j * 1.2)))
    elif i == 4:   # rover drives itself; 90% ring
        _ground(ctx, VIS_Y + 120, scroll=lt * 200)
        _rover(ctx, W / 2 - 200, VIS_Y + 300, 0.7, ang=lt * 6, cam=0.5 + 0.5 * math.sin(lt * 6))
        cx, cy, r = W / 2 + 230, VIS_Y - 120, 150
        u = ease_out(seg(lt, 1.0, 3.5))
        ctx.arc(cx, cy, r, 0, 2 * math.pi)
        src(ctx, WH, 0.15)
        ctx.set_line_width(34)
        ctx.stroke()
        if u > 0:
            ctx.arc(cx, cy, r, -math.pi / 2, -math.pi / 2 + 2 * math.pi * 0.9 * u)
            src(ctx, Y_)
            ctx.set_line_width(34)
            ctx.stroke()
        text(ctx, ">%d%%" % int(90 * u), cx, cy + 22, 62, WH)
        text(ctx, "SELF-DRIVEN", cx, cy + 230, 40, Y_, alpha=ease_out(seg(lt, 2.5, 3.0)))
        bk = ease_back(seg(lt, 0.2, 0.7))
        if bk > 0.01:
            _pill(ctx, "AUTONAV", W / 2 - 200, VIS_Y - 150, 50, K_, Y_, bk)
    elif i == 5:   # camera scan -> 3D hazard grid -> safe path
        top = VIS_Y - 260
        u = seg(lt, 0.3, 1.6)
        # perspective grid
        for q in range(9):
            yy = top + 40 + q * q * 7.5
            ctx.move_to(W / 2 - (200 + q * 55), yy)
            ctx.line_to(W / 2 + (200 + q * 55), yy)
            src(ctx, CYAN, 0.45 * min(1, u * 1.5))
            ctx.set_line_width(2)
            ctx.stroke()
        for q in range(-6, 7):
            ctx.move_to(W / 2 + q * 34, top + 40)
            ctx.line_to(W / 2 + q * 100, top + 40 + 64 * 7.5)
            src(ctx, CYAN, 0.45 * min(1, u * 1.5))
            ctx.stroke()
        rocks = ((-180, 150, 1.0), (130, 260, 1.3), (-60, 380, 1.1), (240, 120, 0.8), (-300, 330, 1.0))
        hz = ease_out(seg(lt, 1.6, 2.4))
        for dx, dy, s in rocks:
            x, y = W / 2 + dx, top + 40 + dy
            ellipse(ctx, x, y, 38 * s, 22 * s)
            src(ctx, DUST)
            ctx.fill()
            if hz > 0:
                ellipse(ctx, x, y, 62 * s, 40 * s)
                src(ctx, RED, 0.9 * hz)
                ctx.set_line_width(5)
                ctx.stroke()
        p = ease_io(seg(lt, 2.6, 4.6))
        if p > 0:
            pts = [(W / 2, top + 40 + 480), (W / 2 + 40, top + 40 + 330), (W / 2 - 60, top + 40 + 240),
                   (W / 2 - 10, top + 40 + 140), (W / 2 + 40, top + 40 + 50)]
            n = 1 + p * (len(pts) - 1)
            ctx.move_to(*pts[0])
            for q in range(1, len(pts)):
                if q <= n:
                    ctx.line_to(*pts[q])
                else:
                    f = n - (q - 1)
                    ctx.line_to(lerp(pts[q - 1][0], pts[q][0], f), lerp(pts[q - 1][1], pts[q][1], f))
                    break
            src(ctx, Y_)
            ctx.set_line_width(14)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.stroke()
        a = ease_back(seg(lt, 4.2, 4.7))
        if a > 0.01:
            _pill(ctx, "SAFE PATH", W / 2, VIS_Y + 360, 52, K_, Y_, a)
    elif i == 6:   # 20 points vs a dense cloud
        lx, rx, cy = 290, 790, VIS_Y - 20
        text(ctx, "SOJOURNER", lx, cy - 260, 44, TEAL)
        text(ctx, "PERSEVERANCE", rx, cy - 260, 44, Y_)
        for q in range(20):
            if seg(lt, 0.3 + q * 0.06, 0.4 + q * 0.06) > 0:
                ellipse(ctx, lx - 120 + (q % 5) * 60, cy - 150 + (q // 5) * 75, 12, 12)
                src(ctx, TEAL)
                ctx.fill()
        u = ease_in(seg(lt, 2.2, 4.5))
        n = int(1800 * u)
        for q in range(n):
            x = rx - 200 + (math.sin(q * 12.9898) * 43758.5453 % 1.0) * 400
            y = cy - 190 + (math.sin(q * 78.233) * 12543.1234 % 1.0) * 330
            ctx.rectangle(x, y, 4, 4)
            src(ctx, Y_, 0.85)
            ctx.fill()
        ctx.move_to(W / 2, cy - 230)
        ctx.line_to(W / 2, cy + 170)
        src(ctx, WH, 0.3)
        ctx.set_line_width(3)
        ctx.stroke()
        text(ctx, "20", lx, cy + 250, 80, TEAL, alpha=ease_out(seg(lt, 1.4, 1.8)))
        text(ctx, "{:,}".format(int(600000 * ease_out(seg(lt, 2.2, 4.6)))), rx, cy + 250, 80, Y_,
             alpha=ease_out(seg(lt, 2.2, 2.6)))
    elif i == 7:   # road to the horizon, 12.4 mile marker passed, 2030s sign
        hy = VIS_Y - 120
        g = cairo.LinearGradient(0, hy, 0, VIS_Y + 420)
        g.add_color_stop_rgb(0, 0.80, 0.42, 0.22)
        g.add_color_stop_rgb(1, 0.42, 0.16, 0.08)
        ctx.rectangle(0, hy, W, VIS_Y + 420 - hy)
        ctx.set_source(g)
        ctx.fill()
        _glow(ctx, W / 2, hy, 260, (1.0, 0.8, 0.6), 0.35)
        ctx.move_to(W / 2 - 14, hy)
        ctx.line_to(W / 2 + 14, hy)
        ctx.line_to(W / 2 + 260, VIS_Y + 420)
        ctx.line_to(W / 2 - 260, VIS_Y + 420)
        ctx.close_path()
        src(ctx, DUST, 0.7)
        ctx.fill()
        for q in range(8):   # moving track marks
            f = ((q / 8.0) + lt * 0.25) % 1.0
            y = hy + (VIS_Y + 420 - hy) * f * f
            ww = 4 + 30 * f * f
            rrect(ctx, W / 2 - ww / 2, y, ww, 6 + 18 * f * f, 3)
            src(ctx, SAND, 0.8)
            ctx.fill()
        _rover(ctx, W / 2, VIS_Y + 400, 0.6 + 0.04 * math.sin(lt * 2), ang=lt * 5, cam=0.3)
        m = ease_out(seg(lt, 0.4, 0.9))
        if m > 0.01:   # 12.4 mi marker on the left, ticked
            rrect(ctx, 90, VIS_Y - 70, 290, 120, 18)
            src(ctx, K_, 0.85 * m)
            ctx.fill()
            text(ctx, "12.4 mi", 235, VIS_Y + 5, 56, WH, alpha=m)
            ck = ease_back(seg(lt, 1.6, 2.0))
            if ck > 0.01:
                ctx.move_to(395, VIS_Y - 10)
                ctx.line_to(425, VIS_Y + 25)
                ctx.line_to(490, VIS_Y - 55)
                src(ctx, (0.3, 0.9, 0.5), ck)
                ctx.set_line_width(14)
                ctx.stroke()
        s = ease_back(seg(lt, 2.8, 3.4))
        if s > 0.01:
            _pill(ctx, "2030s +", W - 230, VIS_Y - 10, 56, K_, Y_, s)


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
