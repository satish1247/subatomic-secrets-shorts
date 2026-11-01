"""2026-11-01 lab: Teghaza 001, a 4.1-billion-year-old Mars meteorite found in the Sahara (contract: DURATION + render_frame)."""
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
ROCK = (0.86, 0.55, 0.58)
ROCK_D = (0.55, 0.30, 0.34)
SAND = (0.93, 0.78, 0.50)
SAND_D = (0.80, 0.62, 0.35)
MARS = (0.80, 0.36, 0.20)
MARS_D = (0.55, 0.22, 0.12)
BLUE = (0.22, 0.52, 0.86)
GREEN = (0.30, 0.72, 0.36)
LEAD = (0.45, 0.47, 0.52)
# (dark lead-in, yellow-on-black keyword)
HEADS = [
    ("NOT FROM EARTH", "A PIECE OF MARS"),
    ("FOUND IN MALI, 2022", "TEGHAZA 001"),
    ("HOW OLD IS IT?", "ZIRCON CLOCK"),
    ("AT LEAST", "4.1 BILLION YRS"),
    ("WHERE ON MARS?", "13 POSSIBLE SITES"),
    ("HIDDEN CLUE", "ANCIENT WATER"),
    ("PUBLISHED IN SCIENCE", "LED BY NASA JPL"),
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
ROCK_PTS = [(-1.0, -0.15), (-0.75, -0.62), (-0.2, -0.8), (0.35, -0.7), (0.85, -0.42),
            (1.0, 0.1), (0.7, 0.55), (0.15, 0.72), (-0.45, 0.62), (-0.9, 0.35)]


def _rock(ctx, x, y, r, rot=0.0, a=1.0, glow=0.0):
    """The rose-coloured meteorite: a lumpy polygon with speckles."""
    if glow > 0:
        _glow(ctx, x, y, r * 1.7, Y_, 0.5 * glow * a)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    pts = ROCK_PTS
    ctx.move_to(pts[0][0] * r, pts[0][1] * r)
    for k in range(len(pts)):
        p0, p1 = pts[k], pts[(k + 1) % len(pts)]
        mx, my = (p0[0] + p1[0]) / 2 * r * 1.05, (p0[1] + p1[1]) / 2 * r * 1.05
        ctx.curve_to(mx, my, mx, my, p1[0] * r, p1[1] * r)
    ctx.close_path()
    g = cairo.LinearGradient(-r, -r, r, r)
    g.add_color_stop_rgba(0, 0.97, 0.72, 0.74, a)
    g.add_color_stop_rgba(1, ROCK_D[0], ROCK_D[1], ROCK_D[2], a)
    ctx.set_source(g)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.set_line_width(6)
    ctx.stroke()
    for (sx, sy, sr) in [(-0.4, -0.2, 0.08), (0.2, 0.25, 0.06), (0.5, -0.3, 0.05),
                         (-0.15, 0.4, 0.05), (0.05, -0.45, 0.04), (-0.6, 0.15, 0.04)]:
        ctx.arc(sx * r, sy * r, sr * r, 0, 2 * math.pi)
        src(ctx, (0.45, 0.22, 0.26), 0.7 * a)
        ctx.fill()
    ctx.restore()


def _mars(ctx, x, y, r, a=1.0, t=0.0, craters=True):
    _glow(ctx, x, y, r * 1.35, ORANGE, 0.35 * a)
    g = cairo.RadialGradient(x - r * 0.35, y - r * 0.35, r * 0.1, x, y, r)
    g.add_color_stop_rgba(0, 0.95, 0.55, 0.32, a)
    g.add_color_stop_rgba(1, MARS_D[0], MARS_D[1], MARS_D[2], a)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.set_line_width(max(3, r * 0.03))
    ctx.stroke()
    if craters:
        ctx.save()
        ctx.arc(x, y, r, 0, 2 * math.pi)
        ctx.clip()
        for (cx, cy, cr) in [(-0.3, -0.4, 0.10), (0.35, -0.2, 0.07), (-0.05, 0.1, 0.06),
                             (-0.45, 0.35, 0.09), (0.25, 0.45, 0.11), (0.55, 0.2, 0.06),
                             (0.0, 0.62, 0.07), (-0.6, -0.05, 0.05)]:
            ctx.arc(x + cx * r, y + cy * r, cr * r, 0, 2 * math.pi)
            src(ctx, MARS_D, 0.55 * a)
            ctx.fill()
        ctx.restore()


def _dunes(ctx, y, a=1.0):
    ctx.move_to(0, y)
    for k in range(0, W + 1, 20):
        ctx.line_to(k, y + 30 * math.sin(k / 160.0) + 18 * math.sin(k / 70.0 + 1))
    ctx.line_to(W, H)
    ctx.line_to(0, H)
    ctx.close_path()
    ctx.set_source(cairo.LinearGradient(0, y, 0, y + 420))
    g = cairo.LinearGradient(0, y, 0, H)
    g.add_color_stop_rgba(0, SAND[0], SAND[1], SAND[2], a)
    g.add_color_stop_rgba(1, SAND_D[0], SAND_D[1], SAND_D[2], a)
    ctx.set_source(g)
    ctx.fill()
    ctx.move_to(0, y)
    for k in range(0, W + 1, 20):
        ctx.line_to(k, y + 30 * math.sin(k / 160.0) + 18 * math.sin(k / 70.0 + 1))
    src(ctx, K_, a)
    ctx.set_line_width(5)
    ctx.stroke()


def _crystal(ctx, x, y, s, a=1.0):
    """Zircon: an elongated bipyramid crystal outline."""
    pts = [(0, -1.0), (0.42, -0.6), (0.42, 0.6), (0, 1.0), (-0.42, 0.6), (-0.42, -0.6)]
    ctx.move_to(x + pts[0][0] * s, y + pts[0][1] * s)
    for p in pts[1:]:
        ctx.line_to(x + p[0] * s, y + p[1] * s)
    ctx.close_path()
    g = cairo.LinearGradient(x - s, y - s, x + s, y + s)
    g.add_color_stop_rgba(0, 1.0, 0.92, 0.75, 0.95 * a)
    g.add_color_stop_rgba(1, 0.90, 0.62, 0.40, 0.95 * a)
    ctx.set_source(g)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.set_line_width(6)
    ctx.stroke()
    ctx.move_to(x - 0.42 * s, y - 0.6 * s)
    ctx.line_to(x + 0.42 * s, y - 0.6 * s)
    ctx.move_to(x - 0.42 * s, y + 0.6 * s)
    ctx.line_to(x + 0.42 * s, y + 0.6 * s)
    _stroke(ctx, K_, 3, 0.5 * a)


def _pin(ctx, x, y, s, c=Y_, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(0, 0)
    ctx.curve_to(-22, -30, -22, -58, 0, -58)
    ctx.curve_to(22, -58, 22, -30, 0, 0)
    src(ctx, c, a)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.set_line_width(4)
    ctx.stroke()
    ctx.arc(0, -40, 7, 0, 2 * math.pi)
    src(ctx, K_, a)
    ctx.fill()
    ctx.restore()


def _drop(ctx, x, y, s, a=1.0):
    ctx.move_to(x, y - s)
    ctx.curve_to(x + s * 0.9, y + s * 0.1, x + s * 0.6, y + s * 0.9, x, y + s * 0.9)
    ctx.curve_to(x - s * 0.6, y + s * 0.9, x - s * 0.9, y + s * 0.1, x, y - s)
    src(ctx, BLUE, a)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.set_line_width(4)
    ctx.stroke()


def _orbiter(ctx, x, y, ang, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.rectangle(-70, -14, 46, 28)
    ctx.rectangle(24, -14, 46, 28)
    src(ctx, TEAL, a)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.set_line_width(4)
    ctx.stroke()
    rrect(ctx, -22, -20, 44, 40, 8)
    src(ctx, (0.85, 0.85, 0.88), a)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.stroke()
    ctx.restore()


# ------------------------------------------------------------------ scenes
def _scene(ctx, i, t):
    lt = t - _scene_start(i)
    cx, cy = W / 2, VIS_Y
    if i == 0:   # Mars far away, rock flies to Earth's desert
        _dunes(ctx, 1230)
        _mars(ctx, 830, 700, 110, t=t)
        u = ease_io(seg(lt, 0.2, 1.6))
        x, y = lerp(780, 470, u), lerp(760, 1130, u)
        # dashed trail
        ctx.set_dash([18, 16])
        ctx.move_to(780, 760)
        ctx.line_to(x, y)
        _stroke(ctx, MARS_D, 6, 0.8)
        ctx.set_dash([])
        r = lerp(40, 150, u)
        _rock(ctx, x, y, r, rot=lt * 0.3 * (1 - u), glow=0.6 + 0.4 * math.sin(t * 4))
        if lt > 1.7:
            k = ease_back(seg(lt, 1.7, 2.1))
            _pill(ctx, 470, 1340, 380 * k + 1, 70, "FROM MARS" if k > 0.6 else "", Y_, K_, 46)
    elif i == 1:   # desert find + name tag
        _glow(ctx, 860, 690, 140, Y_, 0.6)
        ctx.arc(860, 690, 70, 0, 2 * math.pi)
        src(ctx, Y_)
        ctx.fill()
        _dunes(ctx, 1080)
        k = ease_back(seg(lt, 0.1, 0.6))
        _rock(ctx, cx, 1110, 150 * k + 1, glow=0.3)
        tk = ease_back(seg(lt, 0.9, 1.3))
        if tk > 0.01:
            _pill(ctx, cx, 860, 520 * tk + 1, 92, "TEGHAZA 001" if tk > 0.6 else "", K_, Y_, 58)
            ctx.move_to(cx, 906)
            ctx.line_to(cx, 990)
            _stroke(ctx, K_, 6, tk)
        mk = ease_back(seg(lt, 1.8, 2.2))
        if mk > 0.01:
            _pill(ctx, 230, 700, 300 * mk + 1, 70, "MALI" if mk > 0.6 else "", WH, K_, 44)
            _pill(ctx, 230, 790, 300 * mk + 1, 70, "2022" if mk > 0.6 else "", WH, K_, 44)
    elif i == 2:   # zircon clock: uranium -> lead
        _rock(ctx, 230, 760, 110)
        u = ease_out(seg(lt, 0.3, 1.0))
        # magnifier ring
        ctx.arc(640, 1010, 300 * u + 1, 0, 2 * math.pi)
        src(ctx, WH, 0.95)
        ctx.fill_preserve()
        _stroke(ctx, K_, 10)
        ctx.move_to(300, 800)
        ctx.line_to(640 - 300 * u * 0.72, 1010 - 300 * u * 0.69)
        _stroke(ctx, K_, 6, 0.6 * u)
        if u > 0.5:
            _crystal(ctx, 640, 1010, 230 * u)
            prog = seg(lt, 2.0, 6.0)
            dots = [(-0.18, -0.55), (0.12, -0.35), (-0.1, -0.12), (0.2, 0.05), (-0.2, 0.22),
                    (0.08, 0.4), (-0.05, 0.62), (0.22, -0.65), (-0.24, 0.5), (0.0, -0.8)]
            for k, (dx, dy) in enumerate(dots):
                turned = prog > (k + 0.5) / len(dots) * 0.8
                c = LEAD if turned else GREEN
                ctx.arc(640 + dx * 230, 1010 + dy * 230, 17, 0, 2 * math.pi)
                src(ctx, c)
                ctx.fill_preserve()
                _stroke(ctx, K_, 3)
        lk = ease_out(seg(lt, 1.0, 1.4))
        _pill(ctx, 230, 1180, 300, 70, "URANIUM", GREEN, K_, 40, a=lk)
        _arrow(ctx, 230, 1230, 230, 1290, K_, 8, u=lk)
        _pill(ctx, 230, 1340, 300, 70, "LEAD", LEAD, WH, 40, a=ease_out(seg(lt, 2.4, 2.8)))
        # clock icon
        ck = ease_back(seg(lt, 4.0, 4.4))
        if ck > 0.01:
            ctx.arc(900, 720, 80 * ck, 0, 2 * math.pi)
            src(ctx, Y_)
            ctx.fill_preserve()
            _stroke(ctx, K_, 6)
            ang = t * 3
            ctx.move_to(900, 720)
            ctx.line_to(900 + 55 * ck * math.sin(ang), 720 - 55 * ck * math.cos(ang))
            ctx.move_to(900, 720)
            ctx.line_to(900 + 35 * ck * math.sin(ang / 12), 720 - 35 * ck * math.cos(ang / 12))
            _stroke(ctx, K_, 7)
    elif i == 3:   # 4.1 billion years + one of three oldest
        u = ease_out(seg(lt, 0.2, 2.2))
        val = 4.1 * u
        text(ctx, "%.1f" % val, cx, 830, 230, K_)
        text(ctx, "BILLION YEARS", cx, 920, 64, MARS_D)
        k = seg(lt, 3.2, 3.6)
        if k > 0:
            text(ctx, "ONE OF THE 3 OLDEST", cx, 1060, 52, K_, alpha=k)
            text(ctx, "MARS METEORITES ON EARTH", cx, 1120, 44, K_, alpha=k)
            for n, x in enumerate((300, 540, 780)):
                kk = ease_back(seg(lt, 3.6 + n * 0.25, 4.0 + n * 0.25))
                if kk > 0.01:
                    hl = n == 1
                    _rock(ctx, x, 1255, 75 * kk, rot=n * 1.3, glow=0.8 if hl else 0)
            if seg(lt, 4.5, 4.8) > 0:
                _pill(ctx, 540, 1365, 280, 56, "TEGHAZA 001", K_, Y_, 34,
                      a=seg(lt, 4.5, 4.8))
    elif i == 4:   # Mars + orbiter + 13 pins in the south
        R = 300
        _mars(ctx, cx, 1010, R, t=t)
        ang = lt * 0.6 - 1.2
        ok = ease_out(seg(lt, 0.2, 0.7))
        _orbiter(ctx, cx + 400 * math.cos(ang), 1010 + 380 * math.sin(ang) * 0.45 - 30, ang + 1.57, a=ok)
        if seg(lt, 0.5, 1.0) > 0:
            _pill(ctx, 230, 640, 280, 58, "ORBITER", TEAL, WH, 36, a=seg(lt, 0.5, 1.0))
        # southern highlands band
        hk = seg(lt, 2.0, 2.6)
        if hk > 0:
            ctx.save()
            ctx.arc(cx, 1010, R, 0, 2 * math.pi)
            ctx.clip()
            ctx.rectangle(cx - R, 1050, 2 * R, R)
            src(ctx, Y_, 0.22 * hk)
            ctx.fill()
            ctx.restore()
            _pill(ctx, cx, 1360, 560, 62, "SOUTHERN HIGHLANDS", Y_, K_, 36, a=hk)
        pins = [(-0.55, 0.30), (-0.35, 0.22), (-0.15, 0.35), (0.05, 0.25), (0.25, 0.33),
                (0.45, 0.24), (0.6, 0.42), (-0.48, 0.52), (-0.25, 0.58), (0.0, 0.5),
                (0.2, 0.6), (0.4, 0.55), (-0.05, 0.75)]
        for n, (px, py) in enumerate(pins):
            pk = ease_back(seg(lt, 4.2 + n * 0.12, 4.5 + n * 0.12))
            if pk > 0.01:
                _pin(ctx, cx + px * R, 1010 + py * R, 0.75 * pk)
        if lt > 4.2:
            n = min(13, int((lt - 4.2) / 0.12) + 1)
            _pill(ctx, 880, 650, 220, 90, str(n), K_, Y_, 64)
    elif i == 5:   # water seeping underground
        # cross-section: surface strip + deep hot rock
        top = 760
        ctx.rectangle(80, top, W - 160, 600)
        g = cairo.LinearGradient(0, top, 0, top + 600)
        g.add_color_stop_rgb(0, 0.85, 0.50, 0.32)
        g.add_color_stop_rgb(0.5, 0.62, 0.30, 0.20)
        g.add_color_stop_rgb(1, 0.50, 0.18, 0.12)
        ctx.set_source(g)
        ctx.fill_preserve()
        _stroke(ctx, K_, 6)
        text(ctx, "MARS SURFACE", 110, top + 55, 36, WH, align="left")
        hot = seg(lt, 2.5, 4.0)
        _glow(ctx, cx, top + 470, 260, ORANGE, 0.8 * hot)
        _rock(ctx, cx, top + 470, 95, glow=0)
        for n in range(6):
            x = 230 + n * 125
            ph = ((lt * 0.5 + n * 0.17) % 1.0)
            if lt > 0.4:
                _drop(ctx, x, top - 70 + 0 * ph, 22)
                yy = top + 20 + ph * 330
                _drop(ctx, x + 20 * math.sin(ph * 6), yy, 16, a=1 - ph)
        if hot > 0:
            _pill(ctx, 820, top + 270, 240, 56, "HOT ROCK", ORANGE, K_, 34, a=hot)
        wk = ease_back(seg(lt, 3.2, 3.6))
        if wk > 0.01:
            _pill(ctx, cx, 615, 860 * wk + 1, 74, "WATER > 4.1 BILLION YRS AGO" if wk > 0.6 else "", BLUE, WH, 40)
    elif i == 6:   # journal card
        k = ease_back(seg(lt, 0.1, 0.6))
        ctx.save()
        ctx.translate(cx, 1000)
        ctx.scale(k, k)
        ctx.rotate(-0.04)
        rrect(ctx, -300, -340, 600, 680, 26)
        src(ctx, WH)
        ctx.fill_preserve()
        _stroke(ctx, K_, 8)
        ctx.rectangle(-300, -340, 600, 120)
        src(ctx, (0.75, 0.12, 0.12))
        ctx.fill()
        text(ctx, "Science", 0, -255, 72, WH)
        _rock(ctx, 0, -40, 130, glow=0.4)
        for n in range(4):
            ctx.rectangle(-220, 150 + n * 40, 440 - (n % 2) * 120, 14)
            src(ctx, GREY, 0.5)
            ctx.fill()
        ctx.restore()
        mk = ease_out(seg(lt, 3.8, 4.4))
        if mk > 0:
            _mars(ctx, 900, 690, 80 * mk + 1)
            ctx.set_dash([14, 12])
            ctx.move_to(840, 740)
            ctx.line_to(lerp(840, 700, mk), lerp(740, 830, mk))
            _stroke(ctx, MARS_D, 5, mk)
            ctx.set_dash([])

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
