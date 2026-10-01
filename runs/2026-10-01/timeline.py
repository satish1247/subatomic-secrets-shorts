"""2026-10-01 cosmic: the first quantum computer to run in orbit (contract: DURATION + render_frame)."""
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
# (white lead-in, yellow keyword)
HEADS = [
    ("FIRST EVER", "QUANTUM IN SPACE"),
    ("UNIVERSITY OF VIENNA", "SHOEBOX-SIZED LAB"),
    ("JUNE 2025 · FALCON 9", "~550 KM UP"),
    ("IT COMPUTES WITH", "LIGHT"),
    ("SPACE FOUGHT BACK", "DETECTORS DOWN"),
    ("TOO MUCH SUNLIGHT", "~30 MIN PER ORBIT"),
    ("8 MONTHS IN ORBIT", "PHOTONS INTERFERE"),
    ("WHY IT MATTERS", "SMARTER SATELLITES"),
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


def _satellite(ctx, x, y, s, ang=0.0, glow=True):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(s, s)
    for side in (-1, 1):
        x0 = side * 50 - (90 if side < 0 else 0)
        rrect(ctx, x0, -30, 90, 60, 4)
        src(ctx, (0.15, 0.32, 0.72))
        ctx.fill_preserve()
        src(ctx, (0.8, 0.85, 0.95))
        ctx.set_line_width(3)
        ctx.stroke()
        for k in range(1, 4):
            xx = x0 + k * 22.5
            ctx.move_to(xx, -30)
            ctx.line_to(xx, 30)
        ctx.stroke()
        ctx.move_to(side * 40, 0)
        ctx.line_to(side * 50, 0)
        ctx.stroke()
    rrect(ctx, -40, -40, 80, 80, 10)
    src(ctx, (0.88, 0.89, 0.92))
    ctx.fill_preserve()
    src(ctx, K_)
    ctx.set_line_width(4)
    ctx.stroke()
    if glow:
        _glow(ctx, 0, 0, 34, CYAN, 0.9)
    ellipse(ctx, 0, 0, 10, 10)
    src(ctx, Y_)
    ctx.fill()
    ctx.restore()


def _rocket(ctx, x, y, s, flame=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    if flame > 0:
        for k, (c, w) in enumerate(((ORANGE, 30), (Y_, 20), ((1, 1, 0.9), 9))):
            ln = (220 - k * 45) * flame
            ctx.move_to(-w, 230)
            ctx.curve_to(-w * 0.8, 230 + ln * 0.6, 0, 230 + ln, 0, 230 + ln)
            ctx.curve_to(0, 230 + ln, w * 0.8, 230 + ln * 0.6, w, 230)
            ctx.close_path()
            src(ctx, c, 0.95)
            ctx.fill()
    ctx.move_to(-38, 230)
    ctx.line_to(-38, -180)
    ctx.curve_to(-38, -250, -12, -290, 0, -300)
    ctx.curve_to(12, -290, 38, -250, 38, -180)
    ctx.line_to(38, 230)
    ctx.close_path()
    src(ctx, (0.93, 0.94, 0.96))
    ctx.fill_preserve()
    src(ctx, K_)
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.rectangle(-38, -40, 76, 26)
    src(ctx, (0.15, 0.15, 0.18))
    ctx.fill()
    for side in (-1, 1):
        ctx.move_to(side * 38, 170)
        ctx.line_to(side * 70, 235)
        ctx.line_to(side * 38, 235)
        ctx.close_path()
    src(ctx, (0.15, 0.15, 0.18))
    ctx.fill()
    ctx.restore()


def _chip(ctx, x, y, w, h, t, k=1.0, photons=True):
    """Glass chip with six waveguides (the 'six-mode' circuit)."""
    rrect(ctx, x - w / 2, y - h / 2, w, h, 22)
    src(ctx, (0.55, 0.80, 0.95), 0.18 * k)
    ctx.fill_preserve()
    src(ctx, CYAN, 0.9 * k)
    ctx.set_line_width(4)
    ctx.stroke()
    ys = [y - h / 2 + h * (j + 0.5) / 6 for j in range(6)]
    for j, yy in enumerate(ys):
        ctx.move_to(x - w / 2 + 20, yy)
        for m in range(1, 4):
            xm = x - w / 2 + w * m / 4
            tgt = ys[j + 1] if j % 2 == 0 else ys[j - 1]
            if (j + m) % 2 == 0 and 0 <= j < 6:
                ctx.line_to(xm - 50, yy)
                ctx.curve_to(xm - 10, yy, xm - 10, (yy + tgt) / 2, xm, (yy + tgt) / 2)
                ctx.curve_to(xm + 10, (yy + tgt) / 2, xm + 10, yy, xm + 50, yy)
        ctx.line_to(x + w / 2 - 20, yy)
        src(ctx, WH, 0.55 * k)
        ctx.set_line_width(3)
        ctx.stroke()
    if photons:
        for j in (2, 3):
            u = ((t * 0.45 + j * 0.13) % 1.0)
            _photon(ctx, x - w / 2 + 20 + (w - 40) * u, ys[j], 0.8 * k)


def _rays(ctx, x, y, r0, r1, n, t, c, a):
    for j in range(n):
        ang = j / n * 2 * math.pi + t * 0.2
        ctx.move_to(x + r0 * math.cos(ang), y + r0 * math.sin(ang))
        ctx.line_to(x + r1 * math.cos(ang), y + r1 * math.sin(ang))
    src(ctx, c, a)
    ctx.set_line_width(5)
    ctx.stroke()


# ------------------------------------------------------------------ scenes
def _scene(ctx, i, t, k):
    lt = t - _scene_start(i)
    if i == 0:   # satellite glides over glowing Earth, quantum sparkle
        _earth(ctx, W / 2, VIS_Y + 820, 640)
        x = lerp(-150, W + 150, seg(lt, 0, 3.6))
        _satellite(ctx, x, VIS_Y - 40 + 30 * math.sin(lt * 2), 1.2, 0.15)
        for j in range(6):
            px = x - 120 - j * 70
            _photon(ctx, px, VIS_Y - 40 + 22 * math.sin(lt * 6 + j), 0.6)
    elif i == 1:   # shoebox with the chip inside, onto a satellite
        bx, by = W / 2, VIS_Y - 20
        lift = ease_io(seg(lt, 3.2, 5.6))
        s = lerp(1.0, 0.45, lift)
        ctx.save()
        ctx.translate(bx, by - 120 * lift)
        ctx.scale(s, s)
        rrect(ctx, -300, -160, 600, 320, 26)
        src(ctx, (0.62, 0.44, 0.28))
        ctx.fill_preserve()
        src(ctx, K_)
        ctx.set_line_width(6)
        ctx.stroke()
        rrect(ctx, -270, -130, 540, 260, 18)
        src(ctx, (0.06, 0.07, 0.14))
        ctx.fill()
        _chip(ctx, 0, 0, 480, 210, t, 1.0)
        ctx.restore()
        if lift > 0.05:
            _satellite(ctx, bx, by + 220, 1.3 * lift, 0.0)
        text(ctx, "SHOEBOX", bx, by + 250 if lift < 0.05 else by + 380, 54, Y_, alpha=1 - lift * 0.0)
    elif i == 2:   # rocket climbs, altitude gauge to ~550 km
        u = ease_io(seg(lt, 0.2, 5.5))
        _earth(ctx, W / 2, VIS_Y + 1150 + 300 * u, 900)
        _rocket(ctx, W / 2 + 120, lerp(VIS_Y + 260, VIS_Y - 80, u), 0.85, flame=0.75 + 0.25 * math.sin(t * 35))
        gx, top, bot = 200, VIS_Y - 300, VIS_Y + 300
        ctx.move_to(gx, bot)
        ctx.line_to(gx, top)
        src(ctx, WH, 0.5)
        ctx.set_line_width(6)
        ctx.stroke()
        yy = lerp(bot, top, u)
        ctx.move_to(gx, bot)
        ctx.line_to(gx, yy)
        src(ctx, Y_)
        ctx.set_line_width(10)
        ctx.stroke()
        ellipse(ctx, gx, yy, 14, 14)
        ctx.fill()
        text(ctx, "%d km" % int(550 * u), gx + 30, yy + 18, 50, Y_, align="left")
    elif i == 3:   # photons as glowing particles with wave trails
        for j in range(5):
            y0 = VIS_Y - 260 + j * 130
            ph = lt * 1.3 + j * 0.37
            x = (ph % 1.6) / 1.6 * (W + 300) - 150
            ctx.move_to(max(-50, x - 520), y0)
            for q in range(0, 520, 8):
                xx = x - 520 + q
                if xx < -50:
                    continue
                ctx.line_to(xx, y0 + 26 * math.sin(xx / 28.0 - lt * 8) * (q / 520))
            src(ctx, CYAN, 0.55)
            ctx.set_line_width(4)
            ctx.stroke()
            _photon(ctx, x, y0, 1.1)
        u = ease_back(seg(lt, 1.6, 2.1))
        if u > 0.01:
            text(ctx, "PHOTONS", W / 2, VIS_Y + 330, 84 * u, Y_)
    elif i == 4:   # six detectors, three knocked out; laser 20 -> 4 mW
        for j in range(6):
            x = 190 + j * 140
            y = VIS_Y - 170
            dead = j in (2, 3, 4)
            hit = dead and lt > 1.8 + 0.25 * (j - 2)
            rrect(ctx, x - 50, y - 70, 100, 140, 18)
            src(ctx, (0.25, 0.08, 0.08) if hit else (0.10, 0.25, 0.30))
            ctx.fill_preserve()
            src(ctx, RED if hit else TEAL)
            ctx.set_line_width(5)
            ctx.stroke()
            if hit:
                uu = ease_back(seg(lt, 1.8 + 0.25 * (j - 2), 2.1 + 0.25 * (j - 2)))
                ctx.save()
                ctx.translate(x, y)
                ctx.scale(uu, uu)
                for sg in (-1, 1):
                    ctx.move_to(-32, -32 * sg)
                    ctx.line_to(32, 32 * sg)
                src(ctx, RED)
                ctx.set_line_width(14)
                ctx.set_line_cap(cairo.LINE_CAP_ROUND)
                ctx.stroke()
                ctx.restore()
            else:
                _glow(ctx, x, y, 34, CYAN, 0.8)
        # laser power bar
        v = ease_io(seg(lt, 3.0, 4.8))
        mw = lerp(20, 4, v)
        bx, by = 170, VIS_Y + 130
        text(ctx, "LASER", bx, by - 20, 46, WH, align="left")
        rrect(ctx, bx, by, 740, 70, 20)
        src(ctx, WH, 0.12)
        ctx.fill()
        rrect(ctx, bx, by, max(40, 740 * mw / 20), 70, 20)
        src(ctx, (lerp(1, 0.9, v), lerp(0.8, 0.25, v), 0.1))
        ctx.fill()
        text(ctx, "%d mW" % round(mw), bx + 740, by + 150, 66, Y_, align="right")
    elif i == 5:   # sun, Earth, orbit with shadow arc
        ex, ey, r = W / 2 + 60, VIS_Y + 30, 220
        _glow(ctx, 110, VIS_Y - 30, 230, (1, 0.85, 0.3), 0.9)
        ellipse(ctx, 110, VIS_Y - 30, 85, 85)
        src(ctx, (1, 0.93, 0.6))
        ctx.fill()
        _rays(ctx, 110, VIS_Y - 30, 100, 150, 12, t, (1, 0.85, 0.3), 0.6)
        ro = 340
        # shadow cone behind Earth
        ctx.move_to(ex, ey - r)
        ctx.line_to(W + 50, ey - r * 0.9)
        ctx.line_to(W + 50, ey + r * 0.9)
        ctx.line_to(ex, ey + r)
        ctx.close_path()
        src(ctx, (0, 0, 0), 0.45)
        ctx.fill()
        ctx.arc(ex, ey, ro, 0, 2 * math.pi)
        src(ctx, WH, 0.35)
        ctx.set_line_width(4)
        ctx.set_dash([16, 12])
        ctx.stroke()
        ctx.set_dash([])
        half = math.asin(min(1.0, r / ro))
        ctx.arc(ex, ey, ro, -half, half)
        src(ctx, Y_)
        ctx.set_line_width(14)
        ctx.stroke()
        _earth(ctx, ex, ey, r, shadow=1.0)
        ang = -math.pi / 2 + lt * 1.1
        _satellite(ctx, ex + ro * math.cos(ang), ey + ro * math.sin(ang), 0.45, ang)
        text(ctx, "WORK ZONE", ex + ro - 10, ey + 15, 40, Y_, align="right")
        text(ctx, "30 min / 92 min", W / 2, VIS_Y + 330, 64, WH, alpha=ease_out(seg(lt, 1.5, 2.2)))
    elif i == 6:   # chip close-up: two photons meet and interfere
        _chip(ctx, W / 2, VIS_Y - 60, 860, 380, t, 1.0, photons=False)
        u = seg(lt, 0.6, 3.8)
        cx, cy = W / 2, VIS_Y - 60
        p1 = (lerp(cx - 400, cx, u), lerp(cy - 95, cy, u))
        p2 = (lerp(cx - 400, cx, u), lerp(cy + 95, cy, u))
        if u < 1:
            _photon(ctx, *p1, 1.3)
            _photon(ctx, *p2, 1.3, (1, 0.8, 0.4))
        else:   # interference ripples
            for q in range(4):
                rr = ((lt - 3.8) * 160 + q * 70) % 300
                ctx.arc(cx, cy, rr, 0, 2 * math.pi)
                src(ctx, Y_, max(0, 1 - rr / 300))
                ctx.set_line_width(6)
                ctx.stroke()
            _photon(ctx, cx, cy, 1.8, Y_)
        for j, s in enumerate(("MAKE PAIRS", "STEER", "INTERFERE")):
            uu = ease_back(seg(lt, 1.0 + j * 1.4, 1.4 + j * 1.4))
            if uu > 0.01:
                x = 200 + j * 340
                rrect(ctx, x - 150, VIS_Y + 230, 300, 90, 45)
                src(ctx, Y_ if j == 2 else TEAL, uu)
                ctx.fill()
                text(ctx, s, x, VIS_Y + 290, 40, K_ if j == 2 else WH, alpha=uu)
    elif i == 7:   # satellite scanning Earth, analysing on board
        _earth(ctx, W / 2, VIS_Y + 760, 600)
        sx, sy = W / 2, VIS_Y - 160
        sw = 0.5 + 0.5 * math.sin(lt * 1.6)
        ctx.move_to(sx, sy + 40)
        ctx.line_to(sx - 260 - 60 * sw, VIS_Y + 200)
        ctx.line_to(sx + 260 + 60 * sw, VIS_Y + 200)
        ctx.close_path()
        src(ctx, Y_, 0.18)
        ctx.fill()
        _satellite(ctx, sx, sy, 1.1, 0.05 * math.sin(lt))
        for j in range(3):
            uu = ease_back(seg(lt, 1.2 + j * 0.5, 1.5 + j * 0.5))
            if uu > 0.01:
                x = 270 + j * 270
                rrect(ctx, x - 90, VIS_Y + 220, 180, 120, 14)
                src(ctx, (0.08, 0.10, 0.20), uu)
                ctx.fill_preserve()
                src(ctx, CYAN, uu)
                ctx.set_line_width(4)
                ctx.stroke()
                ellipse(ctx, x, VIS_Y + 280, 34 * uu, 34 * uu)
                src(ctx, TEAL if j != 1 else Y_)
                ctx.fill()


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
