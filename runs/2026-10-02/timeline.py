"""2026-10-02 countdown: Figure retires its F.02 humanoids in molten steel (contract: DURATION + render_frame)."""
import json
import math
import os
import cairo
from gfx import W, H, ease_back, ease_out, ease_io, ease_in, seg, src, text, ellipse, rrect, lerp, wrap
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
TEAL = (0.14, 0.60, 0.62)
ORANGE = (0.96, 0.55, 0.18)
RED = (0.88, 0.18, 0.15)
STEEL = (0.78, 0.81, 0.85)
STEEL_D = (0.45, 0.48, 0.53)
# (headline, subline, countdown number or None)
CARDS = [
    ("MOLTEN STEEL", "RETIRED ROBOTS TAKE THE LEAP", None),
    ("F.03 IN · F.02 OUT", "NO SECRET PARTS LEFT BEHIND", None),
    ("3 WILD FACTS", "", None),
    ("ONLY FINLAND", "US & MEXICO FOUNDRIES SAID NO", 3),
    ("THEY JUMPED", "AI TRAINED IN SIMULATION", 2),
    ("24 HOURS", "6 MELTS · ~20 MIN EACH", 1),
    ("75 TONS", "OF MOLTEN STEEL", None),
    ("F.02 KEEPSAKES", "FROM THE LEFTOVER METAL", None),
]
ICON_Y = 1060
CAP_SIZE = 64


def _chunks(line):
    """Split a voice line into caption chunks of at most 2 wrapped lines, timed by characters."""
    probe = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 8, 8))
    words, out, cur = line["text"].split(), [], []
    for w in words:
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
        d = line["dur"] * len(c) / total
        res.append((t, c))
        t += d
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


def _card_start(i):
    return 0.0 if i == 0 else LINES[i]["start"] - 0.3


# ------------------------------------------------------------------ background
def _background(ctx, t):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.05, 0.04, 0.05)
    g.add_color_stop_rgb(0.6, 0.10, 0.05, 0.03)
    g.add_color_stop_rgb(1, 0.30, 0.10, 0.02)
    ctx.set_source(g)
    ctx.paint()
    # rising embers
    for i in range(70):
        sp = 40 + (i % 7) * 18
        y = H - ((i * 263.1 + t * sp) % (H + 100))
        x = (i * 151.7) % W + 20 * math.sin(t * 1.3 + i)
        r = 2 + i % 4
        a = 0.25 + 0.45 * (y / H)
        ellipse(ctx, x, y, r, r)
        src(ctx, ORANGE if i % 3 else Y_, a)
        ctx.fill()


# ------------------------------------------------------------------ drawing helpers
def _robot(ctx, x, y, s, pose=0.0, a=1.0, tint=STEEL, label=None):
    """Generic humanoid robot (no real branding). pose 0 = standing, 1 = arms up, knees tucked (jump)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    dark = tuple(c * 0.55 for c in tint)

    def limb(pts, w):
        ctx.move_to(*pts[0])
        for p in pts[1:]:
            ctx.line_to(*p)
        src(ctx, K_, a)
        ctx.set_line_width(w + 10)
        ctx.stroke_preserve()
        src(ctx, dark, a)
        ctx.set_line_width(w)
        ctx.stroke()
    # legs
    kx, ky = lerp(0, 35, pose), lerp(150, 110, pose)
    fx, fy = lerp(0, -10, pose), lerp(290, 190, pose)
    for side in (-1, 1):
        limb([(side * 32, 40), (side * (32 + kx * 0.4) + kx * 0.3, ky), (side * 34 + fx, fy)], 34)
    # arms
    for side in (-1, 1):
        ex, ey = side * lerp(92, 100, pose), lerp(-10, -150, pose)
        hx, hy = side * lerp(98, 70, pose), lerp(110, -250, pose)
        limb([(side * 70, -100), (ex, ey), (hx, hy)], 26)
    # torso
    rrect(ctx, -75, -125, 150, 180, 40)
    gr = cairo.LinearGradient(-75, 0, 75, 0)
    gr.add_color_stop_rgb(0, *dark)
    gr.add_color_stop_rgb(0.45, *tint)
    gr.add_color_stop_rgb(1, *dark)
    ctx.set_source(gr)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.set_line_width(6)
    ctx.stroke()
    if label:
        text(ctx, label, 0, -15, 34, K_, alpha=a)
    # head with visor
    rrect(ctx, -48, -230, 96, 92, 30)
    src(ctx, tint, a)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.set_line_width(6)
    ctx.stroke()
    rrect(ctx, -36, -205, 72, 34, 14)
    src(ctx, K_, a)
    ctx.fill()
    rrect(ctx, -28, -197, 56, 10, 5)
    src(ctx, TEAL, a)
    ctx.fill()
    ctx.restore()


def _crucible(ctx, x, y, w, t, a=1.0):
    """Glowing vat of molten steel; top lip at y."""
    ctx.save()
    # glow
    g = cairo.RadialGradient(x, y, 10, x, y, w * 0.9)
    g.add_color_stop_rgba(0, 1.0, 0.6, 0.1, 0.55 * a)
    g.add_color_stop_rgba(1, 1.0, 0.4, 0.0, 0.0)
    ctx.arc(x, y, w * 0.9, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    # body
    ctx.move_to(x - w / 2, y)
    ctx.line_to(x - w * 0.38, y + w * 0.55)
    ctx.line_to(x + w * 0.38, y + w * 0.55)
    ctx.line_to(x + w / 2, y)
    ctx.close_path()
    src(ctx, (0.22, 0.22, 0.25), a)
    ctx.fill_preserve()
    src(ctx, K_, a)
    ctx.set_line_width(8)
    ctx.stroke()
    # molten surface
    ellipse(ctx, x, y, w / 2, w * 0.09)
    g = cairo.RadialGradient(x, y, 5, x, y, w / 2)
    g.add_color_stop_rgb(0, 1.0, 0.95, 0.6)
    g.add_color_stop_rgb(0.5, 1.0, 0.65, 0.1)
    g.add_color_stop_rgb(1, 0.9, 0.25, 0.02)
    ctx.set_source(g)
    ctx.fill()
    for j in range(6):   # bubbles
        bx = x + (j - 2.5) * w * 0.14 + 10 * math.sin(t * 2 + j)
        r = 6 + 6 * abs(math.sin(t * 3 + j * 1.7))
        ellipse(ctx, bx, y + 4 * math.sin(j), r, r * 0.5)
        src(ctx, (1, 0.95, 0.7), 0.7 * a)
        ctx.fill()
    ctx.restore()


def _check(ctx, x, y, u, good=True):
    if u <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(u, u)
    ellipse(ctx, 0, 0, 52, 52)
    src(ctx, TEAL if good else RED)
    ctx.fill()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    src(ctx, (1, 1, 1))
    ctx.set_line_width(12)
    if good:
        ctx.move_to(-22, 0)
        ctx.line_to(-6, 18)
        ctx.line_to(24, -18)
    else:
        ctx.move_to(-20, -20)
        ctx.line_to(20, 20)
        ctx.move_to(20, -20)
        ctx.line_to(-20, 20)
    ctx.stroke()
    ctx.restore()


def _battery(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -110, -55, 200, 110, 18)
    src(ctx, (0.15, 0.15, 0.17), a)
    ctx.fill_preserve()
    src(ctx, (1, 1, 1), a)
    ctx.set_line_width(8)
    ctx.stroke()
    rrect(ctx, 90, -22, 22, 44, 6)
    ctx.fill()
    rrect(ctx, -95, -40, 120, 80, 10)
    src(ctx, (0.3, 0.85, 0.4), a)
    ctx.fill()
    text(ctx, "Li-ion", -10, 80, 34, (1, 1, 1), alpha=a)
    ctx.restore()


def _timer(ctx, x, y, r, frac, a=1.0):
    ellipse(ctx, x, y, r, r)
    src(ctx, (0.12, 0.12, 0.14), a)
    ctx.fill_preserve()
    src(ctx, Y_, a)
    ctx.set_line_width(10)
    ctx.stroke()
    if frac > 0:
        ctx.move_to(x, y)
        ctx.arc(x, y, r - 14, -math.pi / 2, -math.pi / 2 + 2 * math.pi * frac)
        ctx.close_path()
        src(ctx, ORANGE, 0.85 * a)
        ctx.fill()
    ctx.move_to(x, y)
    ang = -math.pi / 2 + 2 * math.pi * frac
    ctx.line_to(x + (r - 24) * math.cos(ang), y + (r - 24) * math.sin(ang))
    src(ctx, (1, 1, 1), a)
    ctx.set_line_width(8)
    ctx.stroke()


def _jump(ctx, lt, x0, y0, x1, y1, dur, s=0.6, crucible_y=None, arc=260):
    """Robot arcing from (x0,y0) into the vat at (x1,y1); returns True once it has sunk in."""
    u = seg(lt, 0, dur)
    if u >= 1:
        return True
    e = ease_in(u)
    x = lerp(x0, x1, u)
    y = lerp(y0, y1, e) - arc * math.sin(math.pi * u)
    ctx.save()
    if crucible_y is not None:   # hide what has sunk below the molten surface
        ctx.rectangle(0, 0, W, crucible_y + 10)
        ctx.clip()
    ctx.translate(x, y)
    ctx.rotate(0.5 * math.sin(math.pi * u))
    _robot(ctx, 0, 0, s, pose=min(1, u * 2.5))
    ctx.restore()
    return False


def _icon(ctx, i, t, k):
    t0 = _card_start(i)
    lt = t - t0
    if i == 0:   # robot leaps into the vat, loop
        cy = ICON_Y + 170
        _crucible(ctx, W / 2 + 120, cy, 420 * k, t)
        cyc = lt % 2.6
        if cyc < 0.5:
            _robot(ctx, W / 2 - 330, ICON_Y + 20, 0.55 * k, pose=0.0)
        else:
            _jump(ctx, cyc - 0.5, W / 2 - 330, ICON_Y + 20, W / 2 + 120, cy + 140, 1.1, 0.55 * k, crucible_y=cy)
        if 1.55 < cyc < 2.35:   # splash
            sp = seg(cyc, 1.55, 2.35)
            for j in range(9):
                ang = -math.pi * (0.15 + 0.7 * j / 8)
                rr = 160 * ease_out(sp)
                ellipse(ctx, W / 2 + 120 + rr * math.cos(ang), cy + rr * math.sin(ang) * 1.2 + 120 * sp * sp,
                        12 * (1 - sp) + 3, 12 * (1 - sp) + 3)
                src(ctx, (1, 0.8, 0.2), 1 - sp)
                ctx.fill()
    elif i == 1:   # new robot in, old robot out
        _robot(ctx, W / 2 - 230, ICON_Y - 20, 0.85 * k, tint=(0.95, 0.95, 0.97), label="F.03")
        u = ease_in(seg(lt, 2.0, 4.5))
        ctx.save()
        ctx.translate(W / 2 + 230 + 500 * u, ICON_Y - 20)
        ctx.rotate(0.5 * u)
        _robot(ctx, 0, 0, 0.85 * k, tint=(0.62, 0.64, 0.68), label="F.02", a=1 - 0.5 * u)
        ctx.restore()
        _check(ctx, W / 2 - 230, ICON_Y + 330, ease_back(seg(lt, 0.6, 1.0)), True)
        _check(ctx, W / 2 + 230, ICON_Y + 330, ease_back(seg(lt, 1.2, 1.6)), False)
    elif i == 2:   # three silhouettes stacked
        for j in range(3):
            u = ease_back(seg(lt, 0.15 * j, 0.15 * j + 0.4))
            if u > 0.01:
                xx = W / 2 + (j - 1) * 300
                ctx.save()
                ctx.translate(xx, ICON_Y + 40)
                ctx.scale(u, u)
                rrect(ctx, -120, -150, 240, 300, 36)
                src(ctx, Y_)
                ctx.fill()
                text(ctx, str(3 - j), 0, 70, 220, K_)
                ctx.restore()
    elif i == 3:   # US/Mexico X, Finland check, battery
        _battery(ctx, W / 2, ICON_Y - 170, 1.0 * k)
        rows = (("USA", False, 0.8), ("MEXICO", False, 1.6), ("FINLAND", True, 4.6))
        for j, (lab, good, tt) in enumerate(rows):
            y = ICON_Y + 30 + j * 130
            u = ease_out(seg(lt, tt - 0.3, tt))
            if u > 0.01:
                rrect(ctx, 200, y - 52, 680, 104, 26)
                src(ctx, (1, 1, 1), 0.10 * u)
                ctx.fill()
                text(ctx, lab, 260, y + 20, 58, Y_ if good else (1, 1, 1), align="left", alpha=u)
                _check(ctx, 800, y, ease_back(seg(lt, tt, tt + 0.35)), good)
    elif i == 4:   # airbag practice from a second-floor ledge
        rrect(ctx, 120, ICON_Y - 10, 260, 300, 10)
        src(ctx, (0.25, 0.25, 0.28))
        ctx.fill()
        for r in range(2):
            for c in range(2):
                rrect(ctx, 150 + c * 120, ICON_Y + 15 + r * 120, 80, 85, 8)
                src(ctx, Y_, 0.35)
                ctx.fill()
        text(ctx, "2ND FLOOR", 250, ICON_Y + 268, 34, (1, 1, 1), alpha=k)
        rrect(ctx, 560, ICON_Y + 200, 380, 110, 50)
        src(ctx, ORANGE, k)
        ctx.fill_preserve()
        src(ctx, K_, k)
        ctx.set_line_width(6)
        ctx.stroke()
        text(ctx, "AIRBAG", 750, ICON_Y + 270, 44, K_, alpha=k)
        cyc = lt % 2.8
        if cyc < 0.4:
            _robot(ctx, 290, ICON_Y - 126, 0.4 * k, pose=0.0)
        elif _jump(ctx, cyc - 0.4, 290, ICON_Y - 126, 750, ICON_Y + 84, 1.4, 0.4 * k, arc=60):
            _robot(ctx, 750, ICON_Y + 84, 0.4 * k, pose=0.6)
    elif i == 5:   # timer + six melt slots
        frac = ease_io(seg(lt, 0.3, 5.5))
        _timer(ctx, W / 2, ICON_Y - 20, 165 * k, frac)
        text(ctx, "~20 MIN", W / 2, ICON_Y - 5, 56, (1, 1, 1), alpha=k)
        for j in range(6):
            u = ease_back(seg(lt, 1.6 + j * 0.25, 1.9 + j * 0.25))
            x = W / 2 + (j - 2.5) * 140
            y = ICON_Y + 230
            ellipse(ctx, x, y, 52, 52)
            src(ctx, (1, 1, 1), 0.12)
            ctx.fill()
            if u > 0.01:
                ellipse(ctx, x, y, 52 * u, 52 * u)
                src(ctx, ORANGE)
                ctx.fill()
                text(ctx, str(j + 1), x, y + 18 * u, 50 * u, K_)
        text(ctx, "MELTS", W / 2, ICON_Y + 335, 44, Y_, alpha=ease_out(seg(lt, 3.0, 3.4)))
    elif i == 6:   # big furnace, Arnold credit as text
        cy = ICON_Y + 60
        _crucible(ctx, W / 2, cy, 640 * k, t)
        u = ease_back(seg(lt, 3.0, 3.4))
        if u > 0.01:
            ctx.save()
            ctx.translate(W / 2, ICON_Y - 210)
            ctx.scale(u, u)
            ctx.rotate(-0.04)
            rrect(ctx, -380, -70, 760, 140, 30)
            src(ctx, Y_)
            ctx.fill()
            text(ctx, "IDEA: SCHWARZENEGGER", 0, 20, 52, K_)
            ctx.restore()
    elif i == 7:   # glowing metal bars become keepsakes
        for j in range(3):
            u = ease_back(seg(lt, 0.2 + j * 0.3, 0.6 + j * 0.3))
            if u > 0.01:
                x = W / 2 + (j - 1) * 270
                y = ICON_Y + 20 + 6 * math.sin(t * 2 + j)
                ctx.save()
                ctx.translate(x, y)
                ctx.scale(u, u)
                rrect(ctx, -110, -60, 220, 120, 16)
                g = cairo.LinearGradient(0, -60, 0, 60)
                g.add_color_stop_rgb(0, 0.92, 0.93, 0.95)
                g.add_color_stop_rgb(1, 0.50, 0.52, 0.56)
                ctx.set_source(g)
                ctx.fill_preserve()
                src(ctx, K_)
                ctx.set_line_width(6)
                ctx.stroke()
                text(ctx, "F.02", 0, 16, 50, K_)
                ctx.restore()


def _number(ctx, n, t, t0):
    """Big yellow countdown number that slams in."""
    u = ease_back(seg(t, t0, t0 + 0.35), 2.2)
    if u <= 0.01:
        return
    ctx.save()
    ctx.translate(W / 2, 470)
    ctx.scale(lerp(1.8, 1.0, min(1, u)), lerp(1.8, 1.0, min(1, u)))
    ellipse(ctx, 0, 0, 110, 110)
    src(ctx, Y_)
    ctx.fill()
    text(ctx, str(n), 0, 62, 170, K_)
    ctx.restore()


def _headline(ctx, i, t):
    t0 = _card_start(i)
    k = ease_back(seg(t, t0, t0 + 0.35))
    head, sub, num = CARDS[i]
    hy = 700 if num else 560
    if num:
        _number(ctx, num, t, t0)
    size = 118 if len(head) <= 10 else 100
    ctx.save()
    ctx.translate(W / 2, hy)
    ctx.scale(k, k)
    text(ctx, head, 0, 0, size, Y_ if not num else (1, 1, 1))
    ctx.restore()
    if sub:
        text(ctx, sub, W / 2, hy + 80, 40, (1, 1, 1) if not num else Y_, alpha=ease_out(seg(t, t0 + 0.3, t0 + 0.7)))
    return k


def _wipe(ctx, t):
    """Yellow wipe across each card change."""
    for i in range(1, len(LINES)):
        u = seg(t, _card_start(i) - 0.2, _card_start(i) + 0.2)
        if 0 < u < 1:
            x = lerp(-W * 1.3, W * 1.3, ease_io(u))
            ctx.save()
            ctx.translate(x + W / 2, H / 2)
            ctx.rotate(0.25)
            ctx.rectangle(-W * 0.45, -H, W * 0.9, 2 * H)
            src(ctx, Y_)
            ctx.fill()
            ctx.restore()


def render_frame(t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    _background(ctx, t)
    i = _active(t)
    if i is not None:
        k = ease_out(seg(t, _card_start(i), _card_start(i) + 0.4))
        _icon(ctx, i, t, max(k, 0.01))
        _headline(ctx, i, t)
        line = LINES[i]
        c0, ctext = _caption_text(i, t)
        pk = ease_back(seg(t, c0 - 0.2, c0 + 0.1))
        f = int((t - line["start"]) * 30)
        pulse = 1 + 0.03 * (ENV[i][f] if 0 <= f < len(ENV[i]) else 0)
        brand.caption(ctx, ctext, 1540, CAP_SIZE, pop=pk * pulse)
    _wipe(ctx, t)
    brand.watermark(ctx)
    brand.end_card(ctx, t, DURATION - 1.4)
    surf.flush()
    return surf
