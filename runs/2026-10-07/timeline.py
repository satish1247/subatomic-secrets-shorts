"""2026-10-07 cosmic: Nobel Prize in Physics 2026 - IceCube and cosmic neutrinos (contract: DURATION + render_frame)."""
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
TEAL = (0.14, 0.60, 0.62)
ORANGE = (0.96, 0.55, 0.18)
RED = (0.90, 0.20, 0.20)
CYAN = (0.45, 0.85, 1.0)
ICE = (0.80, 0.92, 1.0)
BLUE = (0.35, 0.65, 1.0)
GOLD = (0.95, 0.75, 0.25)
# (white lead-in, yellow keyword)
HEADS = [
    ("NOBEL PRIZE IN PHYSICS 2026", "ICE TELESCOPE"),
    ("EVERY SECOND", "100 TRILLION"),
    ("GHOST PARTICLES", "HARD TO CATCH"),
    ("1980s · FRANCIS HALZEN", "USE THE ICE"),
    ("ICECUBE", "5,160 SENSORS"),
    ("NEUTRINO HITS ICE", "BLUE FLASH"),
    ("2013 · FIRST EVIDENCE", "FROM DEEP SPACE"),
    ("TRACED TO", "BLACK HOLE JET"),
    ("OCTOBER 6, 2026", "NEW ASTRONOMY"),
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


def _photon(ctx, x, y, s=1.0, c=CYAN):
    _glow(ctx, x, y, 40 * s, c, 0.55)
    ellipse(ctx, x, y, 9 * s, 9 * s)
    src(ctx, WH)
    ctx.fill()




def _earth(ctx, x, y, r, shadow=0.0):
    g = cairo.RadialGradient(x - r * 0.3, y - r * 0.3, r * 0.1, x, y, r)
    g.add_color_stop_rgb(0, 0.30, 0.62, 0.95)
    g.add_color_stop_rgb(1, 0.04, 0.18, 0.45)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    ctx.save()
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.clip()
    for dx, dy, rx, ry in ((-0.3, -0.2, 0.28, 0.2), (0.25, 0.15, 0.22, 0.3), (-0.1, 0.45, 0.2, 0.1),
                           (0.45, -0.45, 0.15, 0.1)):
        ellipse(ctx, x + dx * r, y + dy * r, rx * r, ry * r)
        src(ctx, (0.25, 0.60, 0.35), 0.9)
        ctx.fill()
    if shadow > 0:   # night side on the right
        ctx.rectangle(x, y - r, r, 2 * r)
        src(ctx, (0, 0, 0.03), 0.6 * shadow)
        ctx.fill()
    ctx.restore()
    ag = cairo.RadialGradient(x, y, r, x, y, r * 1.12)
    ag.add_color_stop_rgba(0, 0.5, 0.8, 1, 0.5)
    ag.add_color_stop_rgba(1, 0.5, 0.8, 1, 0)
    ctx.arc(x, y, r * 1.12, 0, 2 * math.pi)
    ctx.set_source(ag)
    ctx.fill()




def _neutrino(ctx, x, y, s=1.0, c=BLUE, trail=0.0, ang=0.0):
    """Small glowing 'ghost' particle with an optional fading trail behind it (direction ang)."""
    if trail > 0:
        tx, ty = x - trail * math.cos(ang), y - trail * math.sin(ang)
        g = cairo.LinearGradient(tx, ty, x, y)
        g.add_color_stop_rgba(0, c[0], c[1], c[2], 0)
        g.add_color_stop_rgba(1, c[0], c[1], c[2], 0.8)
        ctx.move_to(tx, ty)
        ctx.line_to(x, y)
        ctx.set_source(g)
        ctx.set_line_width(6 * s)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
    _glow(ctx, x, y, 30 * s, c, 0.6)
    ellipse(ctx, x, y, 7 * s, 7 * s)
    src(ctx, WH)
    ctx.fill()


def _medal(ctx, x, y, r, t, k=1.0):
    _glow(ctx, x, y, r * 1.8, GOLD, 0.35 * k)
    g = cairo.RadialGradient(x - r * 0.3, y - r * 0.3, r * 0.1, x, y, r)
    g.add_color_stop_rgb(0, 1.0, 0.92, 0.55)
    g.add_color_stop_rgb(1, 0.72, 0.50, 0.10)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    ctx.arc(x, y, r * 0.84, 0, 2 * math.pi)
    src(ctx, (0.60, 0.40, 0.05), 0.8)
    ctx.set_line_width(max(2, r * 0.04))
    ctx.stroke()
    text(ctx, "NOBEL", x, y - r * 0.05, r * 0.30, (0.42, 0.27, 0.02))
    text(ctx, "PHYSICS", x, y + r * 0.30, r * 0.17, (0.42, 0.27, 0.02))
    sh = (t * 0.6) % 2.0   # moving shine
    if sh < 1:
        ctx.save()
        ctx.arc(x, y, r, 0, 2 * math.pi)
        ctx.clip()
        xx = x - r + 2 * r * sh
        ctx.move_to(xx - 30, y - r)
        ctx.line_to(xx + 30, y - r)
        ctx.line_to(xx - 30 + 60, y + r)
        ctx.line_to(xx - 90, y + r)
        ctx.close_path()
        src(ctx, WH, 0.25)
        ctx.fill()
        ctx.restore()


def _ice_block(ctx, x0, y0, w, h, a=1.0):
    g = cairo.LinearGradient(0, y0, 0, y0 + h)
    g.add_color_stop_rgba(0, 0.85, 0.94, 1.0, 0.95 * a)
    g.add_color_stop_rgba(0.08, 0.55, 0.75, 0.95, 0.85 * a)
    g.add_color_stop_rgba(1, 0.06, 0.20, 0.42, 0.9 * a)
    ctx.rectangle(x0, y0, w, h)
    ctx.set_source(g)
    ctx.fill()
    for j in range(7):   # faint ice strata
        yy = y0 + h * (0.15 + j * 0.12)
        ctx.move_to(x0, yy)
        ctx.curve_to(x0 + w * 0.3, yy - 10, x0 + w * 0.7, yy + 12, x0 + w, yy)
        src(ctx, WH, 0.07 * a)
        ctx.set_line_width(3)
        ctx.stroke()


def _sensor(ctx, x, y, r=9, lit=0.0):
    if lit > 0:
        _glow(ctx, x, y, r * 4.5, BLUE, 0.9 * lit)
    ellipse(ctx, x, y, r, r)
    src(ctx, (0.85, 0.90, 1.0) if lit < 0.3 else (0.85, 0.95, 1.0))
    ctx.fill()
    ellipse(ctx, x, y, r * 0.5, r * 0.5)
    src(ctx, (0.15, 0.18, 0.28) if lit < 0.3 else CYAN)
    ctx.fill()


def _station(ctx, x, y, s=1.0):
    """Simple generic lab hut on the ice surface."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -110, -90, 220, 90, 8)
    src(ctx, (0.75, 0.78, 0.82))
    ctx.fill_preserve()
    src(ctx, K_)
    ctx.set_line_width(4)
    ctx.stroke()
    for j in range(3):
        rrect(ctx, -85 + j * 62, -68, 44, 30, 4)
        src(ctx, Y_)
        ctx.fill()
    ctx.move_to(-130, -90)
    ctx.line_to(130, -90)
    ctx.line_to(110, -115)
    ctx.line_to(-110, -115)
    ctx.close_path()
    src(ctx, (0.30, 0.32, 0.36))
    ctx.fill()
    ctx.restore()


def _person(ctx, x, y, s, a=1.0):
    """Generic glowing outline figure (not a real person)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ellipse(ctx, 0, -230, 62, 70)
    ctx.move_to(-120, 170)
    ctx.curve_to(-125, -40, -100, -135, 0, -140)
    ctx.curve_to(100, -135, 125, -40, 120, 170)
    ctx.close_path()
    src(ctx, (0.25, 0.35, 0.60), 0.35 * a)
    ctx.fill_preserve()
    src(ctx, CYAN, 0.9 * a)
    ctx.set_line_width(5)
    ctx.stroke()
    ellipse(ctx, 0, -230, 62, 70)
    src(ctx, (0.25, 0.35, 0.60), 0.35 * a)
    ctx.fill_preserve()
    src(ctx, CYAN, 0.9 * a)
    ctx.stroke()
    ctx.restore()


def _bulb(ctx, x, y, s, on=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    if on > 0:
        _glow(ctx, 0, -20, 150, Y_, 0.55 * on)
    ctx.arc(0, -20, 60, math.radians(140), math.radians(40))
    ctx.line_to(26, 50)
    ctx.line_to(-26, 50)
    ctx.close_path()
    src(ctx, Y_ if on > 0.5 else (0.8, 0.8, 0.7))
    ctx.fill_preserve()
    src(ctx, K_)
    ctx.set_line_width(5)
    ctx.stroke()
    for j in range(3):
        rrect(ctx, -28, 54 + j * 15, 56, 11, 4)
        src(ctx, (0.6, 0.6, 0.65))
        ctx.fill()
    ctx.restore()


def _blackhole(ctx, x, y, r, t):
    # accretion disk
    for q in range(3):
        ellipse(ctx, x, y, r * (2.4 - q * 0.35), r * (0.55 - q * 0.08))
        src(ctx, (1.0, 0.55 + q * 0.15, 0.15), 0.35 + 0.2 * q)
        ctx.set_line_width(10 - q * 2)
        ctx.stroke()
    _glow(ctx, x, y, r * 2.2, ORANGE, 0.45)
    # jet (pointing up-right toward Earth side)
    for sgn in (1, -1):
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(-0.35)
        g = cairo.LinearGradient(0, 0, 0, -sgn * r * 5)
        g.add_color_stop_rgba(0, 0.7, 0.85, 1.0, 0.85)
        g.add_color_stop_rgba(1, 0.7, 0.85, 1.0, 0.0)
        wob = 6 * math.sin(t * 9)
        ctx.move_to(-r * 0.15, 0)
        ctx.line_to(-r * 0.55 + wob, -sgn * r * 5)
        ctx.line_to(r * 0.55 - wob, -sgn * r * 5)
        ctx.line_to(r * 0.15, 0)
        ctx.close_path()
        ctx.set_source(g)
        ctx.fill()
        ctx.restore()
    ellipse(ctx, x, y, r, r)
    src(ctx, (0, 0, 0))
    ctx.fill()
    ctx.arc(x, y, r * 1.05, 0, 2 * math.pi)
    src(ctx, (1.0, 0.8, 0.4), 0.9)
    ctx.set_line_width(4)
    ctx.stroke()


# ------------------------------------------------------------------ scenes
COLS = [140 + j * 100 for j in range(9)]   # sensor strings in the ice cross-section


def _ice_section(ctx, top, bot, lit=None):
    _ice_block(ctx, 60, top, W - 120, bot - top)
    for j, x in enumerate(COLS):
        ctx.move_to(x, top)
        ctx.line_to(x, bot - 20)
        src(ctx, WH, 0.35)
        ctx.set_line_width(2)
        ctx.stroke()
        for q in range(6):
            y = top + 120 + q * (bot - top - 160) / 5
            _sensor(ctx, x, y, 9, lit(x, y) if lit else 0.0)


def _scene(ctx, i, t, k):
    lt = t - _scene_start(i)
    if i == 0:   # gold medal rises out of a glowing ice slab
        _ice_block(ctx, 60, VIS_Y + 60, W - 120, 330)
        u = ease_back(seg(lt, 0.2, 1.0))
        _medal(ctx, W / 2, lerp(VIS_Y + 250, VIS_Y - 110, u), 210 * max(u, 0.05), t)
        for j in range(5):   # neutrinos rain into the ice
            ph = (lt * 0.7 + j * 0.21) % 1.0
            x = 170 + j * 185
            _neutrino(ctx, x + 60 * ph, lerp(VIS_Y - 330, VIS_Y + 360, ph), 0.8, trail=110, ang=math.atan2(700, 60))
    elif i == 1:   # streams of neutrinos fly straight through a generic figure
        _person(ctx, W / 2, VIS_Y + 30, 1.25)
        for j in range(14):
            y0 = VIS_Y - 300 + j * 46
            ph = (lt * 0.9 + j * 0.137) % 1.0
            x = lerp(-80, W + 80, ph)
            _neutrino(ctx, x, y0 + 10 * math.sin(j), 0.7, trail=140)
        n = int(100 * ease_out(seg(lt, 0.4, 2.4)))
        rrect(ctx, W / 2 - 330, VIS_Y + 290, 660, 110, 30)
        src(ctx, K_, 0.85)
        ctx.fill()
        text(ctx, "%d TRILLION / SEC" % n, W / 2, VIS_Y + 368, 62, Y_)
    elif i == 2:   # a net tries to catch them; they pass through walls of rock and a planet
        _earth(ctx, W / 2 + 230, VIS_Y + 20, 190)
        rrect(ctx, 230, VIS_Y - 230, 70, 470, 10)
        src(ctx, (0.45, 0.40, 0.36))
        ctx.fill()
        for j in range(6):
            y0 = VIS_Y - 200 + j * 80
            ph = (lt * 0.55 + j * 0.17) % 1.0
            _neutrino(ctx, lerp(-60, W + 60, ph), y0, 0.8, trail=150)
    elif i == 3:   # icy South Pole surface, flag, light-bulb idea
        _ice_block(ctx, 60, VIS_Y + 40, W - 120, 340)
        fx, fy = W / 2 + 220, VIS_Y + 40
        ctx.move_to(fx, fy)
        ctx.line_to(fx, fy - 230)
        src(ctx, WH)
        ctx.set_line_width(7)
        ctx.stroke()
        wv = 10 * math.sin(lt * 5)
        ctx.move_to(fx, fy - 230)
        ctx.curve_to(fx + 60, fy - 230 + wv, fx + 90, fy - 210 - wv, fx + 140, fy - 215)
        ctx.line_to(fx + 140, fy - 160)
        ctx.curve_to(fx + 90, fy - 155 - wv, fx + 60, fy - 175 + wv, fx, fy - 170)
        ctx.close_path()
        src(ctx, ORANGE)
        ctx.fill()
        text(ctx, "SOUTH POLE", fx + 70, fy + 70, 44, K_)
        on = seg(lt, 1.6, 1.9)
        _bulb(ctx, W / 2 - 220, VIS_Y - 150 - 12 * math.sin(lt * 3), 1.3 * ease_back(seg(lt, 0.3, 0.8)), on)
        a = ease_out(seg(lt, 3.0, 3.6))
        if a > 0:
            rrect(ctx, 140, VIS_Y + 150, 800, 100, 30)
            src(ctx, K_, 0.8 * a)
            ctx.fill()
            text(ctx, "ICE = GIANT DETECTOR", W / 2, VIS_Y + 220, 56, Y_, alpha=a)
    elif i == 4:   # cross-section: hut on top, strings of sensors, depth gauge
        top, bot = VIS_Y - 180, VIS_Y + 250
        u = ease_io(seg(lt, 0.3, 3.0))
        ctx.save()
        ctx.rectangle(0, 0, W, top + (bot - top) * max(u, 0.02))
        ctx.clip()
        _ice_section(ctx, top, bot)
        ctx.restore()
        _station(ctx, W / 2, top, 0.9)
        n = int(5160 * ease_out(seg(lt, 0.5, 4.0)))
        d = 2.45 * u
        text(ctx, "{:,} sensors".format(n), 90, VIS_Y + 345, 50, Y_, align="left")
        text(ctx, "%.2f km deep" % d, W - 90, VIS_Y + 345, 50, WH, align="right")
        text(ctx, "1 km³ of ice", W / 2, top - 150, 46, ICE, alpha=ease_out(seg(lt, 4.5, 5.2)))
    elif i == 5:   # neutrino strikes, blue cone of light, sensors light up
        top, bot = VIS_Y - 300, VIS_Y + 360
        hx, hy = W / 2 - 40, VIS_Y + 20
        u = seg(lt, 0.2, 1.4)
        fl = seg(lt, 1.4, 3.6)

        def lit(x, y):
            if fl <= 0:
                return 0.0
            dd = math.hypot(x - hx, y - hy)
            return max(0.0, 1 - abs(dd - fl * 520) / 160) + (0.35 if dd < fl * 520 else 0.0)
        _ice_section(ctx, top, bot, lit)
        if u < 1:
            _neutrino(ctx, lerp(hx - 380, hx, u), lerp(top - 120, hy, u), 1.2, trail=220,
                      ang=math.atan2(hy - top + 120, 380))
        else:
            r = 40 + fl * 520
            for q in range(3):
                rr = r - q * 60
                if rr > 0:
                    ctx.arc(hx, hy, rr, 0, 2 * math.pi)
                    src(ctx, BLUE, max(0, 0.7 - fl * 0.5 - q * 0.15))
                    ctx.set_line_width(10)
                    ctx.stroke()
            _glow(ctx, hx, hy, 140 * (1 - fl * 0.5), BLUE, 0.9)
    elif i == 6:   # neutrinos arrive from distant galaxies into the ice
        top = VIS_Y + 120
        _ice_section(ctx, top, VIS_Y + 400, lambda x, y: 0.6 * max(0, math.sin(lt * 3 + x / 90)) * (y < top + 150))
        for j, (gx, gy) in enumerate(((220, VIS_Y - 260), (860, VIS_Y - 300), (560, VIS_Y - 330))):
            ctx.save()
            ctx.translate(gx, gy)
            ctx.rotate(t * 0.3 + j)
            for q in range(2):
                ctx.save()
                ctx.rotate(q * math.pi)
                ctx.move_to(0, 0)
                ctx.curve_to(40, -10, 70, 20, 60, 60)
                src(ctx, (0.8, 0.7, 1.0), 0.8)
                ctx.set_line_width(8)
                ctx.stroke()
                ctx.restore()
            ctx.restore()
            _glow(ctx, gx, gy, 70, (0.8, 0.7, 1.0), 0.6)
            ph = (lt * 0.5 + j * 0.33) % 1.0
            tx, ty = W / 2 + (j - 1) * 220, top + 40
            _neutrino(ctx, lerp(gx, tx, ph), lerp(gy, ty, ph), 1.0, trail=120,
                      ang=math.atan2(ty - gy, tx - gx))
        a = ease_back(seg(lt, 0.5, 1.0))
        if a > 0.01:
            rrect(ctx, W / 2 - 260, VIS_Y - 110, 520, 100, 50)
            src(ctx, Y_, a)
            ctx.fill()
            text(ctx, "HIGH ENERGY", W / 2, VIS_Y - 40, 56, K_, alpha=a)
    elif i == 7:   # black hole jet -> neutrino -> Earth, distance label
        _blackhole(ctx, 260, VIS_Y - 170, 55, t)
        _earth(ctx, W - 210, VIS_Y + 130, 110)
        ph = seg(lt, 0.6, 4.2)
        sx, sy, ex, ey = 330, VIS_Y - 200, W - 260, VIS_Y + 90
        ctx.move_to(sx, sy)
        ctx.line_to(ex, ey)
        src(ctx, WH, 0.25)
        ctx.set_line_width(3)
        ctx.set_dash([14, 12])
        ctx.stroke()
        ctx.set_dash([])
        if ph < 1:
            _neutrino(ctx, lerp(sx, ex, ph), lerp(sy, ey, ph), 1.3, trail=160, ang=math.atan2(ey - sy, ex - sx))
        else:
            _glow(ctx, ex, ey, 150, BLUE, 0.7 * (1 - seg(lt, 4.2, 5.2)))
        a = ease_back(seg(lt, 1.2, 1.7))
        if a > 0.01:
            rrect(ctx, W / 2 - 340, VIS_Y + 260, 680, 100, 30)
            src(ctx, K_, 0.85 * a)
            ctx.fill()
            text(ctx, "3.7 BILLION LIGHT-YEARS", W / 2, VIS_Y + 328, 46, Y_, alpha=a)
    elif i == 8:   # medal + ice + rings: new window on the universe
        _ice_block(ctx, 60, VIS_Y + 120, W - 120, 280)
        for q in range(4):
            rr = ((lt * 140) + q * 90) % 360
            ctx.arc(W / 2, VIS_Y - 60, 200 + rr, 0, 2 * math.pi)
            src(ctx, BLUE, max(0, 0.6 - rr / 600))
            ctx.set_line_width(5)
            ctx.stroke()
        _medal(ctx, W / 2, VIS_Y - 60, 190 * ease_back(seg(lt, 0.1, 0.6)) + 1, t)
        a = ease_out(seg(lt, 2.4, 3.0))
        text(ctx, "FRANCIS HALZEN", W / 2, VIS_Y + 275, 60, K_, alpha=a)


def _headline(ctx, i, t):
    t0 = _scene_start(i)
    lead, key = HEADS[i]
    a = ease_out(seg(t, t0 + 0.05, t0 + 0.4))
    text(ctx, lead, W / 2, 400, 46, WH, alpha=a)
    k = ease_back(seg(t, t0 + 0.15, t0 + 0.5))
    size = 108 if len(key) <= 10 else 84 if len(key) <= 15 else 72
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
