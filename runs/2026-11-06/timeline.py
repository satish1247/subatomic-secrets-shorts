"""2026-11-06 lab: self-charging toothbrush whose PVDF bristles make electricity to zap bacteria (contract: DURATION + render_frame)."""
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
BLUE = (0.22, 0.52, 0.86)
GREEN = (0.30, 0.72, 0.36)
GREEN_D = (0.16, 0.45, 0.20)
PURPLE = (0.55, 0.35, 0.75)
# (dark lead-in, yellow-on-black keyword)
HEADS = [
    ("NO BATTERY NEEDED", "SELF-POWERED BRUSH"),
    ("WHO BUILT IT?", "PEKING UNIVERSITY"),
    ("THE SECRET", "PVDF BRISTLES"),
    ("BRUSH -> CHARGE ->", "REACTIVE OXYGEN"),
    ("LAB TEST", "53% vs 9%"),
    ("REAL PEOPLE", "115 VOLUNTEERS"),
    ("PUBLISHED IN", "SCIENCE ADVANCES"),
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



# ------------------------------------------------------------------ props
def _toothbrush(ctx, x, y, s, rot=0.0, wig=0.0, a=1.0, glow=0.0):
    """Horizontal toothbrush, head on the right, bristles pointing down. (x, y) = head centre."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    if glow > 0:
        _glow(ctx, 0, 60, 230, Y_, 0.55 * glow * a)
    # handle
    ctx.move_to(-560, -18)
    ctx.curve_to(-300, -40, -200, -30, -110, -26)
    ctx.line_to(-110, 26)
    ctx.curve_to(-200, 30, -300, 40, -560, 18)
    ctx.curve_to(-600, 16, -600, -16, -560, -18)
    ctx.close_path()
    g = cairo.LinearGradient(0, -40, 0, 40)
    g.add_color_stop_rgba(0, 0.30, 0.78, 0.80, a)
    g.add_color_stop_rgba(1, TEAL[0] * 0.8, TEAL[1] * 0.8, TEAL[2] * 0.8, a)
    ctx.set_source(g)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.set_line_width(6)
    ctx.stroke()
    ellipse(ctx, -420, 0, 60, 14)
    src(ctx, WH, 0.5 * a)
    ctx.fill()
    # head
    rrect(ctx, -130, -34, 260, 60, 28)
    src(ctx, TEAL, a)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.set_line_width(6)
    ctx.stroke()
    # bristles (piezo, yellowish-white)
    for n in range(9):
        bx = -105 + n * 26
        bend = wig * math.sin(n * 0.9 + wig * 3) * 18
        ctx.move_to(bx, 26)
        ctx.curve_to(bx, 70, bx + bend * 0.5, 100, bx + bend, 124)
        _stroke(ctx, K_, 16, a)
        ctx.move_to(bx, 26)
        ctx.curve_to(bx, 70, bx + bend * 0.5, 100, bx + bend, 124)
        _stroke(ctx, (0.98, 0.95, 0.78), 10, a)
    ctx.restore()


def _bolt(ctx, x, y, s, a=1.0, c=Y_):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    pts = [(-8, -40), (14, -40), (2, -8), (18, -8), (-12, 42), (-2, 6), (-18, 6)]
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.close_path()
    src(ctx, c, a)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.set_line_width(3.5)
    ctx.stroke()
    ctx.restore()


def _battery_x(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -70, -36, 130, 72, 12)
    src(ctx, WH, a)
    ctx.fill_preserve()
    _stroke(ctx, K_, 7, a)
    ctx.rectangle(60, -16, 16, 32)
    src(ctx, K_, a)
    ctx.fill()
    ctx.rectangle(-58, -24, 40, 48)
    src(ctx, GREEN, a)
    ctx.fill()
    ctx.move_to(-90, -60)
    ctx.line_to(100, 60)
    _stroke(ctx, RED, 14, a)
    ctx.restore()


def _tooth(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-100, -60)
    ctx.curve_to(-110, -130, -40, -140, 0, -110)
    ctx.curve_to(40, -140, 110, -130, 100, -60)
    ctx.curve_to(95, 0, 80, 40, 70, 120)
    ctx.curve_to(62, 160, 30, 160, 24, 120)
    ctx.curve_to(16, 60, -16, 60, -24, 120)
    ctx.curve_to(-30, 160, -62, 160, -70, 120)
    ctx.curve_to(-80, 40, -95, 0, -100, -60)
    ctx.close_path()
    src(ctx, WH, a)
    ctx.fill_preserve()
    _stroke(ctx, K_, 7, a)
    ellipse(ctx, -45, -75, 22, 12)
    src(ctx, (0.85, 0.92, 0.98), a)
    ctx.fill()
    ctx.restore()


def _microbe(ctx, x, y, r, dead=0.0, a=1.0, t=0.0):
    """S. mutans-like cocci: a short chain of 3 balls with a face; dead -> grey + X eyes."""
    col = (lerp(GREEN[0], GREY[0], dead), lerp(GREEN[1], GREY[1], dead), lerp(GREEN[2], GREY[2], dead))
    wob = 0.06 * math.sin(t * 6 + x) * (1 - dead)
    for k in (-1, 1, 0):
        cx = x + k * r * 1.5
        cy = y + k * r * 0.25 * math.sin(t * 3)
        ctx.arc(cx, cy, r * (1 + wob), 0, 2 * math.pi)
        src(ctx, col, a)
        ctx.fill_preserve()
        _stroke(ctx, K_, max(3, r * 0.12), a)
    # face on middle ball
    e = r * 0.32
    if dead < 0.5:
        for sx in (-1, 1):
            ctx.arc(x + sx * e, y - r * 0.15, r * 0.12, 0, 2 * math.pi)
            src(ctx, K_, a)
            ctx.fill()
        ctx.arc(x, y + r * 0.2, r * 0.3, 0.2, math.pi - 0.2)
        _stroke(ctx, K_, max(2, r * 0.08), a)
    else:
        for sx in (-1, 1):
            ex, ey, d = x + sx * e, y - r * 0.15, r * 0.13
            ctx.move_to(ex - d, ey - d)
            ctx.line_to(ex + d, ey + d)
            ctx.move_to(ex + d, ey - d)
            ctx.line_to(ex - d, ey + d)
            _stroke(ctx, K_, max(2, r * 0.08), a)
        ctx.move_to(x - r * 0.25, y + r * 0.35)
        ctx.line_to(x + r * 0.25, y + r * 0.35)
        _stroke(ctx, K_, max(2, r * 0.08), a)


def _ros(ctx, x, y, s, a=1.0):
    """Reactive oxygen: red O with a dot (radical)."""
    ctx.arc(x, y, 22 * s, 0, 2 * math.pi)
    src(ctx, RED, a)
    ctx.fill_preserve()
    _stroke(ctx, K_, 3, a)
    text(ctx, "O", x, y + 11 * s, 30 * s, WH, alpha=a)
    ctx.arc(x + 22 * s, y - 18 * s, 6 * s, 0, 2 * math.pi)
    src(ctx, Y_, a)
    ctx.fill()


def _person(ctx, x, y, s, c, a=1.0):
    ctx.arc(x, y - 22 * s, 13 * s, 0, 2 * math.pi)
    src(ctx, c, a)
    ctx.fill()
    ctx.move_to(x - 20 * s, y + 26 * s)
    ctx.curve_to(x - 20 * s, y - 6 * s, x + 20 * s, y - 6 * s, x + 20 * s, y + 26 * s)
    ctx.close_path()
    ctx.fill()


def _building(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-190, -90)
    ctx.line_to(0, -190)
    ctx.line_to(190, -90)
    ctx.close_path()
    src(ctx, Y_, a)
    ctx.fill_preserve()
    _stroke(ctx, K_, 7, a)
    for n in range(5):
        ctx.rectangle(-160 + n * 72, -80, 34, 200)
        src(ctx, WH, a)
        ctx.fill_preserve()
        _stroke(ctx, K_, 5, a)
    ctx.rectangle(-200, 120, 400, 40)
    src(ctx, K_, a)
    ctx.fill()
    ctx.restore()


# ------------------------------------------------------------------ scenes
def _scene(ctx, i, t):
    lt = t - _scene_start(i)
    cx = W / 2
    if i == 0:   # brush slides in, wiggles, sparks; no battery
        u = ease_out(seg(lt, 0.0, 0.8))
        bx = lerp(1500, 700, u)
        wig = math.sin(t * 9) * min(1, lt)
        _tooth(ctx, 700, 1150, 1.1)
        _toothbrush(ctx, bx + 20 * math.sin(t * 9), 860, 1.0, wig=wig, glow=0.6 + 0.3 * math.sin(t * 7))
        for n in range(5):
            ph = (lt * 1.6 + n * 0.21) % 1.0
            if lt > 0.6:
                _bolt(ctx, bx - 110 + n * 55 + 30 * math.sin(n * 2), 1010 + ph * 60, 0.9, a=1 - ph)
        k = ease_back(seg(lt, 1.6, 2.0))
        if k > 0.01:
            _battery_x(ctx, 230, 1210, 0.9 * k)
    elif i == 1:   # university + tooth = dental school
        k = ease_back(seg(lt, 0.1, 0.6))
        _building(ctx, 360, 950, 1.0 * k + 0.01)
        k2 = ease_back(seg(lt, 0.8, 1.2))
        if k2 > 0.01:
            _tooth(ctx, 800, 930, 0.9 * k2)
        p1 = ease_back(seg(lt, 1.3, 1.7))
        if p1 > 0.01:
            _pill(ctx, 360, 1230, 420 * p1 + 1, 72, "UNIVERSITY" if p1 > 0.6 else "", WH, K_, 42)
        p2 = ease_back(seg(lt, 2.6, 3.0))
        if p2 > 0.01:
            _pill(ctx, 800, 1230, 420 * p2 + 1, 72, "DENTAL SCHOOL" if p2 > 0.6 else "", Y_, K_, 42)
        if lt > 2.4:
            text(ctx, "+", 580, 965, 110, K_, alpha=ease_out(seg(lt, 2.4, 2.7)))
    elif i == 2:   # one bristle bends -> charges appear
        u = math.sin(lt * 2.4)
        bend = 160 * u
        x0, y0, y1 = cx, 700, 1250
        ctx.move_to(x0, y0)
        ctx.curve_to(x0, y0 + 250, x0 + bend * 0.5, y1 - 120, x0 + bend, y1)
        _stroke(ctx, K_, 64)
        ctx.move_to(x0, y0)
        ctx.curve_to(x0, y0 + 250, x0 + bend * 0.5, y1 - 120, x0 + bend, y1)
        _stroke(ctx, (0.98, 0.95, 0.78), 50)
        rrect(ctx, x0 - 160, y0 - 70, 320, 80, 30)
        src(ctx, TEAL)
        ctx.fill_preserve()
        _stroke(ctx, K_, 6)
        lk = ease_back(seg(lt, 0.6, 1.0))
        if lk > 0.01:
            _pill(ctx, 260, 860, 300 * lk + 1, 70, "PVDF" if lk > 0.6 else "", Y_, K_, 46)
        ch = ease_out(seg(lt, 2.0, 2.6)) * abs(u)
        for n in range(5):
            s_ = n / 4
            yy = lerp(y0 + 80, y1 - 40, s_)
            xx = x0 + bend * (s_ ** 2)
            for side, sym, col in ((-1, "+", RED), (1, "-", BLUE)):
                sx = xx + side * 70 * (1 if u >= 0 else -1)
                ctx.arc(sx, yy, 26, 0, 2 * math.pi)
                src(ctx, col, ch)
                ctx.fill()
                text(ctx, sym, sx, yy + 14, 44, WH, alpha=ch)
        if lt > 3.4:
            k = ease_back(seg(lt, 3.4, 3.8))
            _pill(ctx, W / 2, 1335, 440 * k + 1, 70, "BEND = CHARGE" if k > 0.6 else "", K_, Y_, 38)
    elif i == 3:   # saliva + sparks -> ROS -> bacteria hurt
        _tooth(ctx, 300, 1000, 1.0)
        # saliva puddle
        ellipse(ctx, 640, 1180, 360, 70)
        src(ctx, BLUE, 0.25)
        ctx.fill()
        for n in range(3):
            if lt > 0.3 + n * 0.3:
                _bolt(ctx, 520 + n * 110, 1100 + 10 * math.sin(t * 8 + n), 1.0)
        bugs = [(800, 840), (930, 1000), (760, 1050), (900, 760)]
        hit = ease_out(seg(lt, 3.0, 4.2))
        for n, (bx, by) in enumerate(bugs):
            _microbe(ctx, bx, by, 34, dead=seg(lt, 3.4 + n * 0.25, 3.8 + n * 0.25), t=t)
        if lt > 1.5:
            for n in range(6):
                ph = ((lt - 1.5) * 0.7 + n / 6) % 1.0
                tx, ty = bugs[n % 4]
                sx, sy = 600 + (n % 3) * 90, 1090
                _ros(ctx, lerp(sx, tx - 60, ph), lerp(sy, ty + 40, ph), 1.0, a=min(1, (lt - 1.5) * 2))
        k = ease_back(seg(lt, 0.8, 1.2))
        if k > 0.01:
            _pill(ctx, 640, 1300, 300 * k + 1, 64, "SALIVA" if k > 0.6 else "", BLUE, WH, 38)
    elif i == 4:   # bar chart 53 vs 9
        base = 1300
        top = 720
        for n, (lab, val, col, x) in enumerate((("NEW PVDF", 53, Y_, 360), ("NYLON", 9, GREY, 740))):
            g = ease_out(seg(lt, 0.6 + n * 3.4, 1.6 + n * 3.4))
            hh = (base - top) * val / 60 * g
            rrect(ctx, x - 110, base - hh, 220, hh + 1, 18)
            src(ctx, col)
            ctx.fill_preserve()
            _stroke(ctx, K_, 6, 1 if g > 0 else 0)
            if g > 0.05:
                text(ctx, "%d%%" % val, x, base - hh - 30, 76, K_)
                text(ctx, lab, x, base + 60, 42, K_)
        ctx.move_to(160, base)
        ctx.line_to(940, base)
        _stroke(ctx, K_, 8)
        k = ease_back(seg(lt, 0.1, 0.5))
        _microbe(ctx, 860, 625, 26 * k + 1, dead=seg(lt, 1.6, 2.2), t=t)
        text(ctx, "bacteria killed (lab)", 450, 640, 40, K_, alpha=ease_out(seg(lt, 0.3, 0.7)))
    elif i == 5:   # 115 volunteers, 3 months, 3 wins
        shown = int(115 * ease_out(seg(lt, 0.0, 2.2)))
        for n in range(115):
            if n >= shown:
                break
            r_, c_ = divmod(n, 15)
            _person(ctx, 125 + c_ * 59, 650 + r_ * 56, 0.85, TEAL if n % 2 else ORANGE)
        k = ease_back(seg(lt, 2.4, 2.8))
        if k > 0.01:
            _pill(ctx, cx, 1140, 400 * k + 1, 70, "3 MONTHS" if k > 0.6 else "", K_, Y_, 44)
        spots = ((cx - 290, 1240, 320), (cx + 290, 1240, 320), (cx, 1330, 600))
        labs = ("LESS PLAQUE", "LESS BLEEDING", "LESS GUM INFLAMMATION")
        order = (0, 2, 1)   # spoken order: plaque, gum inflammation, bleeding
        for n, lab in enumerate(labs):
            p = ease_back(seg(lt, 3.8 + order[n] * 0.8, 4.2 + order[n] * 0.8))
            if p > 0.01:
                x_, y_, w_ = spots[n]
                _pill(ctx, x_, y_, w_ * p + 1, 64, lab if p > 0.6 else "", GREEN, WH, 32)
    elif i == 6:   # journal card + more testing
        k = ease_back(seg(lt, 0.1, 0.6))
        ctx.save()
        ctx.translate(360, 960)
        ctx.scale(k, k)
        ctx.rotate(-0.04)
        rrect(ctx, -230, -300, 460, 600, 26)
        src(ctx, WH)
        ctx.fill_preserve()
        _stroke(ctx, K_, 8)
        ctx.rectangle(-230, -300, 460, 120)
        src(ctx, (0.75, 0.12, 0.12))
        ctx.fill()
        text(ctx, "Science", 0, -250, 56, WH)
        text(ctx, "Advances", 0, -198, 44, WH)
        _toothbrush(ctx, 120, -60, 0.42, rot=-0.15, wig=math.sin(t * 6), glow=0.4)
        for n in range(4):
            ctx.rectangle(-170, 110 + n * 40, 340 - (n % 2) * 100, 14)
            src(ctx, GREY, 0.5)
            ctx.fill()
        ctx.restore()
        mk = ease_back(seg(lt, 1.8, 2.2))
        if mk > 0.01:
            _pill(ctx, 800, 820, 360 * mk + 1, 70, "MORE TESTS" if mk > 0.6 else "", ORANGE, K_, 40)
            text(ctx, "NEEDED", 800, 920, 46, K_, alpha=seg(lt, 2.0, 2.3))
        zk = seg(lt, 3.6, 4.0)
        if zk > 0:
            _microbe(ctx, 800, 1150, 40, dead=seg(lt, 4.2, 4.6), t=t)
            for n in range(3):
                _bolt(ctx, 700 + n * 100, 1060 + 8 * math.sin(t * 9 + n), 0.9, a=zk)

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

