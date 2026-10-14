"""2026-10-14 lab: mirror-image molecules and the 2026 Nobel Prize in Chemistry (contract: DURATION + render_frame)."""
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
    ("SAME MOLECULE?", "MIRROR TWINS"),
    ("SAME ATOMS, FLIPPED", "LEFT vs RIGHT"),
    ("WHY YOUR NOSE KNOWS", "CHIRAL SENSORS"),
    ("LIFE PICKS A SIDE", "LEFT-HANDED"),
    ("IN AN ORDINARY LAB", "50 / 50"),
    ("KENSO SOAI", "SELF-COPYING"),
    ("A TINY HEAD START", "> 99.5%"),
    ("HENRI KAGAN", "PURER THAN EXPECTED"),
    ("NOBEL PRIZE IN CHEMISTRY 2026", "OCTOBER 7"),
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


def _ball(ctx, x, y, r, c, a=1.0):
    ellipse(ctx, x, y, r, r)
    g = cairo.RadialGradient(x - r * 0.35, y - r * 0.35, r * 0.1, x, y, r)
    g.add_color_stop_rgba(0, min(1, c[0] + 0.35), min(1, c[1] + 0.35), min(1, c[2] + 0.35), a)
    g.add_color_stop_rgba(1, c[0], c[1], c[2], a)
    ctx.set_source(g)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.set_line_width(max(3, r * 0.12))
    ctx.stroke()


def _chiral(ctx, x, y, s, flip=False, a=1.0, spin=0.0):
    """Tetrahedral 'carbon' with four different groups; flip=True draws its mirror image."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(-s if flip else s, s)
    pts = ((0, -150, WH, 34), (-135, 70, TEAL, 40), (120, 95, ORANGE, 46), (70, -40, PURPLE, 30))
    wob = 6 * math.sin(spin)
    for px, py, c, r in pts:
        ctx.move_to(0, 0)
        ctx.line_to(px, py + wob)
        _stroke(ctx, K_, 14, a)
    _ball(ctx, 0, 0, 52, (0.2, 0.2, 0.22), a)
    for px, py, c, r in pts:
        _ball(ctx, px, py + wob, r, c, a)
    ctx.restore()


def _mirror(ctx, x, y0, y1, a=1.0):
    ctx.save()
    ctx.set_dash([24, 18])
    ctx.move_to(x, y0)
    ctx.line_to(x, y1)
    _stroke(ctx, BLUE, 8, a)
    ctx.restore()


def _leaf(ctx, x, y, s):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(0, 60)
    ctx.curve_to(-70, 20, -60, -60, 0, -80)
    ctx.curve_to(60, -60, 70, 20, 0, 60)
    src(ctx, GREEN)
    ctx.fill_preserve()
    src(ctx, GREEN_D)
    ctx.set_line_width(6)
    ctx.stroke()
    ctx.move_to(0, 60)
    ctx.line_to(0, -60)
    _stroke(ctx, GREEN_D, 5)
    ctx.restore()


def _seeds(ctx, x, y, s):
    for j, (dx, dy, an) in enumerate(((-40, 10, 0.5), (0, -20, -0.3), (40, 15, 0.9), (5, 35, 0.1))):
        ctx.save()
        ctx.translate(x + dx * s, y + dy * s)
        ctx.rotate(an)
        ellipse(ctx, 0, 0, 34 * s, 13 * s)
        src(ctx, (0.55, 0.38, 0.20))
        ctx.fill_preserve()
        src(ctx, (0.30, 0.18, 0.08))
        ctx.set_line_width(4)
        ctx.stroke()
        ctx.restore()


def _hand(ctx, x, y, s, flip=False):
    """Simple cartoon open hand (palm facing viewer); flip mirrors it."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(-s if flip else s, s)
    skin = (0.98, 0.80, 0.62)
    for fx, fh in ((-60, 170), (-20, 200), (20, 190), (58, 150)):
        rrect(ctx, fx - 18, -fh, 36, fh + 20, 18)
        src(ctx, skin)
        ctx.fill_preserve()
        src(ctx, K_)
        ctx.set_line_width(6)
        ctx.stroke()
    ctx.save()
    ctx.translate(85, 40)
    ctx.rotate(0.9)
    rrect(ctx, -18, -120, 36, 130, 18)
    src(ctx, skin)
    ctx.fill_preserve()
    src(ctx, K_)
    ctx.stroke()
    ctx.restore()
    rrect(ctx, -82, -20, 164, 170, 50)
    src(ctx, skin)
    ctx.fill_preserve()
    src(ctx, K_)
    ctx.set_line_width(6)
    ctx.stroke()
    ctx.restore()


def _mark(ctx, x, y, ok, k=1.0):
    if k <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(k, k)
    ellipse(ctx, 0, 0, 52, 52)
    src(ctx, GREEN if ok else (0.85, 0.22, 0.22))
    ctx.fill()
    if ok:
        ctx.move_to(-24, 2)
        ctx.line_to(-6, 22)
        ctx.line_to(26, -20)
    else:
        ctx.move_to(-20, -20)
        ctx.line_to(20, 20)
        ctx.move_to(20, -20)
        ctx.line_to(-20, 20)
    _stroke(ctx, WH, 11)
    ctx.restore()


def _receptor(ctx, x, y, s):
    """A cup-shaped receptor with three coloured pockets (chiral binding site)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-220, -40)
    ctx.line_to(-220, 120)
    ctx.curve_to(-220, 180, 220, 180, 220, 120)
    ctx.line_to(220, -40)
    ctx.line_to(150, -40)
    ctx.line_to(150, 60)
    ctx.curve_to(150, 100, -150, 100, -150, 60)
    ctx.line_to(-150, -40)
    ctx.close_path()
    src(ctx, (0.80, 0.86, 0.95))
    ctx.fill_preserve()
    src(ctx, K_)
    ctx.set_line_width(7)
    ctx.stroke()
    for px, c in ((-110, TEAL), (0, PURPLE), (110, ORANGE)):
        ellipse(ctx, px, 70, 30, 18)
        src(ctx, c)
        ctx.fill()
    ctx.restore()


def _mini(ctx, x, y, s, left=True, a=1.0):
    """Small labelled molecule token: L (teal) or R (orange)."""
    c = TEAL if left else ORANGE
    _ball(ctx, x, y, 38 * s, c, a)
    text(ctx, "L" if left else "R", x, y + 15 * s, 42 * s, WH, alpha=a)


# ------------------------------------------------------------------ scenes
def _scene(ctx, i, t):
    lt = t - _scene_start(i)
    if i == 0:   # mirror twins: spearmint vs caraway
        _mirror(ctx, W / 2, VIS_Y - 360, VIS_Y + 330)
        _chiral(ctx, W / 2 - 250, VIS_Y - 80, 1.0, False, spin=t * 2)
        k = ease_out(seg(lt, 1.6, 2.4))
        _chiral(ctx, W / 2 + 250, VIS_Y - 80, 1.0, True, a=max(k, 0.01), spin=t * 2)
        _leaf(ctx, W / 2 - 250, VIS_Y + 210, 0.9)
        _pill(ctx, W / 2 - 250, VIS_Y + 330, 400, 84, "SPEARMINT", GREEN, WH, 46)
        if k > 0.01:
            _seeds(ctx, W / 2 + 250, VIS_Y + 210, 1.0)
            _pill(ctx, W / 2 + 250, VIS_Y + 330, 400, 84, "CARAWAY", (0.55, 0.38, 0.20), WH, 46, k)
    elif i == 1:   # hands are mirror images
        _mirror(ctx, W / 2, VIS_Y - 380, VIS_Y + 340)
        _hand(ctx, W / 2 - 230, VIS_Y - 120, 1.15, False)
        _hand(ctx, W / 2 + 230, VIS_Y - 120, 1.15, True)
        u = ease_out(seg(lt, 1.2, 1.8))
        _chiral(ctx, W / 2 - 230, VIS_Y + 220, 0.55, False, a=max(u, 0.01))
        _chiral(ctx, W / 2 + 230, VIS_Y + 220, 0.55, True, a=max(u, 0.01))
        text(ctx, "LEFT", W / 2 - 230, VIS_Y + 360, 48, TEAL_D, alpha=u)
        text(ctx, "RIGHT", W / 2 + 230, VIS_Y + 360, 48, ORANGE, alpha=u)
    elif i == 2:   # receptor fits one hand only
        _receptor(ctx, W / 2, VIS_Y + 30, 1.3)
        text(ctx, "SMELL RECEPTOR", W / 2, VIS_Y + 340, 46, K_)
        d = ease_io(seg(lt, 0.4, 1.6))
        flip = lt > 2.2
        if flip:
            d = ease_io(seg(lt, 2.2, 3.0))
        yy = lerp(VIS_Y - 360, VIS_Y - 110, d)
        _chiral(ctx, W / 2, yy, 0.8, flip)
        if not flip:
            _mark(ctx, W - 180, VIS_Y - 150, True, ease_back(seg(lt, 1.6, 1.9)))
        else:
            _mark(ctx, W - 180, VIS_Y - 150, False, ease_back(seg(lt, 3.0, 3.3)))
    elif i == 3:   # protein chain of left-handed amino acids
        n = 9
        for j in range(n):
            u = ease_back(seg(lt, 0.2 + j * 0.15, 0.5 + j * 0.15))
            px = 150 + j * 98
            py = VIS_Y - 60 + 90 * math.sin(j * 0.9 + t * 1.2)
            if j:
                ppx = 150 + (j - 1) * 98
                ppy = VIS_Y - 60 + 90 * math.sin((j - 1) * 0.9 + t * 1.2)
                ctx.move_to(ppx, ppy)
                ctx.line_to(px, py)
                _stroke(ctx, K_, 10, u)
            if u > 0.01:
                _mini(ctx, px, py, u, True)
        _pill(ctx, W / 2, VIS_Y + 220, 560, 92, "PROTEIN CHAIN", K_, Y_, 50, ease_out(seg(lt, 1.6, 2.0)))
        text(ctx, "ALMOST ALL  L", W / 2, VIS_Y + 350, 52, TEAL_D, alpha=ease_out(seg(lt, 2.0, 2.4)))
    elif i == 4:   # flask: 50/50 mix, question mark
        fx, fy = W / 2, VIS_Y - 20
        ctx.move_to(fx - 70, fy - 300)
        ctx.line_to(fx - 70, fy - 120)
        ctx.line_to(fx - 260, fy + 200)
        ctx.curve_to(fx - 280, fy + 250, fx - 250, fy + 270, fx - 210, fy + 270)
        ctx.line_to(fx + 210, fy + 270)
        ctx.curve_to(fx + 250, fy + 270, fx + 280, fy + 250, fx + 260, fy + 200)
        ctx.line_to(fx + 70, fy - 120)
        ctx.line_to(fx + 70, fy - 300)
        ctx.close_path()
        src(ctx, (0.85, 0.93, 0.98), 0.9)
        ctx.fill_preserve()
        src(ctx, K_)
        ctx.set_line_width(8)
        ctx.stroke()
        for j in range(10):
            px = fx - 170 + (j % 5) * 85 + 10 * math.sin(t * 2 + j)
            py = fy + 70 + (j // 5) * 95 + 8 * math.cos(t * 2.3 + j)
            _mini(ctx, px, py, 0.9, j % 2 == 0)
        k = ease_back(seg(lt, 2.8, 3.2))
        if k > 0.01:
            ctx.save()
            ctx.translate(W - 170, VIS_Y - 250)
            ctx.scale(k, k)
            text(ctx, "?", 0, 50, 190, ORANGE)
            ctx.restore()
        text(ctx, "5 L  :  5 R", W / 2, VIS_Y + 360, 52, K_)
    elif i == 5:   # self-copying: 1 -> 2 -> 4 -> 8
        gens = (1, 2, 4, 8)
        for g, n in enumerate(gens):
            u = ease_back(seg(lt, 0.3 + g * 0.8, 0.7 + g * 0.8))
            y = VIS_Y - 330 + g * 200
            for j in range(n):
                x = W / 2 + (j - (n - 1) / 2) * (110 if n == 8 else 170)
                if g and u > 0.01:
                    pj = j // 2
                    pn = gens[g - 1]
                    ppx = W / 2 + (pj - (pn - 1) / 2) * (110 if pn == 8 else 170)
                    ctx.move_to(ppx, y - 200 + 40)
                    ctx.line_to(x, y - 40)
                    _stroke(ctx, GREY, 6, u)
                if u > 0.01:
                    _mini(ctx, x, y, u * (0.9 if n == 8 else 1.0), True)
        text(ctx, "COPIES ITSELF", W / 2, VIS_Y + 390, 50, TEAL_D, alpha=ease_out(seg(lt, 2.8, 3.2)))
    elif i == 6:   # bars: 50.000025 / 49.999975 -> >99.5 / <0.5
        u = ease_io(seg(lt, 3.0, 5.2))
        bx, by, bh = 260, VIS_Y + 250, 560
        for j, (lab, c, v0, v1) in enumerate((("L", TEAL, 0.5, 0.995), ("R", ORANGE, 0.5, 0.005))):
            x = bx + j * 420
            v = lerp(v0, v1, u)
            rrect(ctx, x - 90, by - bh * v, 180, bh * v + 2, 16)
            src(ctx, c)
            ctx.fill_preserve()
            src(ctx, K_)
            ctx.set_line_width(6)
            ctx.stroke()
            text(ctx, lab, x, by + 70, 60, c)
        ctx.move_to(100, by)
        ctx.line_to(W - 100, by)
        _stroke(ctx, K_, 8)
        if u < 0.05:
            text(ctx, "50.000025%", bx, by - bh * 0.5 - 30, 44, K_)
            text(ctx, "49.999975%", bx + 420, by - bh * 0.5 - 30, 44, K_)
            text(ctx, "START", bx + 420, VIS_Y - 250, 50, GREY)
        else:
            text(ctx, "> 99.5%", bx, by - bh * lerp(0.5, 0.995, u) - 30, 56, TEAL_D)
            text(ctx, "AFTER COPYING", bx + 420, VIS_Y - 250, 50, ORANGE, alpha=u)
    elif i == 7:   # Kagan: impure catalyst, purer product (non-linear curve)
        gx, gy, gw, gh = 190, VIS_Y + 240, 700, 560
        ctx.move_to(gx, gy - gh)
        ctx.line_to(gx, gy)
        ctx.line_to(gx + gw, gy)
        _stroke(ctx, K_, 8)
        ctx.save()
        ctx.set_dash([18, 14])
        ctx.move_to(gx, gy)
        ctx.line_to(gx + gw, gy - gh)
        _stroke(ctx, GREY, 7)
        ctx.restore()
        u = ease_io(seg(lt, 0.8, 2.8))
        ctx.move_to(gx, gy)
        for q in range(1, int(60 * u) + 1):
            f = q / 60
            ctx.line_to(gx + gw * f, gy - gh * (1 - (1 - f) ** 2.6))
        _stroke(ctx, TEAL, 12)
        text(ctx, "CATALYST PURITY", gx + gw / 2, gy + 70, 42, K_)
        ctx.save()
        ctx.translate(gx - 50, gy - gh / 2)
        ctx.rotate(-math.pi / 2)
        text(ctx, "PRODUCT PURITY", 0, 0, 42, K_)
        ctx.restore()
        text(ctx, "EXPECTED", gx + gw - 120, gy - gh * 0.62, 40, GREY, alpha=ease_out(seg(lt, 0.4, 0.8)))
        text(ctx, "ACTUAL", gx + 210, gy - gh * 0.86, 46, TEAL_D, alpha=ease_out(seg(lt, 2.4, 2.8)))
    elif i == 8:   # medal, names, medicine capsule
        k = ease_back(seg(lt, 0.0, 0.6))
        _medal(ctx, W / 2, VIS_Y - 150, 140, k, t)
        for j, nm in enumerate(("HENRI KAGAN", "KENSO SOAI")):
            u = ease_back(seg(lt, 1.0 + j * 0.6, 1.4 + j * 0.6))
            if u > 0.01:
                ctx.save()
                ctx.translate(W / 2, VIS_Y + 110 + j * 110)
                ctx.scale(u, u)
                _pill(ctx, 0, 0, 620, 92, nm, K_ if j == 0 else TEAL, WH, 50)
                ctx.restore()
        u = ease_back(seg(lt, 3.6, 4.0))
        if u > 0.01:
            ctx.save()
            ctx.translate(W / 2, VIS_Y + 350)
            ctx.scale(u, u)
            ctx.rotate(-0.2)
            rrect(ctx, -110, -40, 110, 80, 40)
            src(ctx, ORANGE)
            ctx.fill()
            rrect(ctx, 0, -40, 110, 80, 40)
            src(ctx, WH)
            ctx.fill()
            rrect(ctx, -110, -40, 220, 80, 40)
            src(ctx, K_)
            ctx.set_line_width(6)
            ctx.stroke()
            ctx.restore()
            text(ctx, "MEDICINES", W / 2 + 270, VIS_Y + 365, 44, K_, alpha=u if u < 1 else 1)


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
