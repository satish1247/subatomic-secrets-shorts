"""2026-10-20 newsflash: Microsoft exits Nscale UK AI data centre over grid power (contract: DURATION + render_frame)."""
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
TEAL = (0.14, 0.60, 0.62)
ORANGE = (0.96, 0.55, 0.18)
CARDS = [
    ("NO POWER", "MICROSOFT WALKS AWAY FROM AN AI DATA CENTRE"),
    ("THE SITE", "NSCALE · LOUGHTON, ESSEX"),
    ("2030s", "WHEN ENOUGH POWER COULD ARRIVE (REPORTED)"),
    ("50 MW", "PLANNED SIZE · ROOM TO GROW TO 90 MW"),
    ("ONE SITE", "MICROSOFT + NSCALE ELSEWHERE"),
    ("13 YEARS", "LONGEST GRID-QUEUE DELAYS (REUTERS)"),
    ("WHY IT MATTERS", ""),
]
RED = (0.90, 0.18, 0.18)
GREY = (0.55, 0.56, 0.60)
ICON_Y = 990
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
    g.add_color_stop_rgb(0, 0.06, 0.06, 0.08)
    g.add_color_stop_rgb(1, 0.01, 0.01, 0.02)
    ctx.set_source(g)
    ctx.paint()
    for i in range(90):
        x = (i * 173.3 + t * (6 + i % 5 * 5)) % W
        y = (i * 311.7) % H
        r = 1.5 + i % 3
        ellipse(ctx, x, y, r, r)
        src(ctx, (1, 1, 1), 0.2 + 0.2 * math.sin(t * 2 + i))
        ctx.fill()
    # diagonal BREAKING band
    u = ease_out(seg(t, 0.0, 0.5))
    ctx.save()
    ctx.translate(W / 2, 330)
    ctx.rotate(-0.07)
    ctx.rectangle(-W * u, -52, 2 * W * u, 104)
    src(ctx, Y_)
    ctx.fill()
    text(ctx, "BREAKING · AI POWER", -W / 2 + 90 + (1 - u) * -300, 20, 56, K_, align="left", alpha=u)
    ctx.restore()


# ------------------------------------------------------------------ icons
GREY2 = (0.85, 0.87, 0.90)
GREEN = (0.30, 0.90, 0.40)


def _check(ctx, x, y, u):
    if u <= 0.01:
        return
    ellipse(ctx, x, y, 40 * u, 40 * u)
    src(ctx, TEAL)
    ctx.fill()
    ctx.move_to(x - 18, y)
    ctx.line_to(x - 4, y + 15)
    ctx.line_to(x + 20, y - 17)
    src(ctx, (1, 1, 1), u)
    ctx.set_line_width(8)
    ctx.stroke()


def _calendar(ctx, x, y, s, top, big, u):
    if u <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * u, s * u)
    rrect(ctx, -130, -115, 260, 230, 22)
    src(ctx, (1, 1, 1))
    ctx.fill()
    rrect(ctx, -130, -115, 260, 70, 22)
    src(ctx, RED)
    ctx.fill()
    text(ctx, top, 0, -64, 44, (1, 1, 1))
    text(ctx, big, 0, 80, 110 if len(big) <= 2 else 76, K_)
    ctx.restore()


def _pill(ctx, x, y, label, u, col=None, fg=None, size=46, w=None):
    if u <= 0.01:
        return
    col = col or (1, 1, 1)
    fg = fg or K_
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(u, u)
    ww = w or (len(label) * size * 0.62 + 80)
    rrect(ctx, -ww / 2, -45, ww, 90, 45)
    src(ctx, col)
    ctx.fill()
    text(ctx, label, 0, size * 0.36, size, fg)
    ctx.restore()


def _rack(ctx, x, y, s, t, on=1.0, a=1.0):
    """Server rack; on=1 lights blink, on=0 dark."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -110, -190, 220, 380, 18)
    src(ctx, (0.18, 0.19, 0.23), a)
    ctx.fill_preserve()
    src(ctx, (0.55, 0.57, 0.62), a)
    ctx.set_line_width(6)
    ctx.stroke()
    for r in range(5):
        yy = -160 + r * 68
        rrect(ctx, -85, yy, 170, 50, 8)
        src(ctx, (0.10, 0.10, 0.13), a)
        ctx.fill()
        for j in range(3):
            lit = on * (0.5 + 0.5 * math.sin(t * 7 + r * 1.3 + j * 2.1))
            ellipse(ctx, 40 + j * 16, yy + 25, 5, 5)
            src(ctx, GREEN if lit > 0.3 else (0.2, 0.25, 0.2), a)
            ctx.fill()
        rrect(ctx, -70, yy + 18, 70, 14, 4)
        src(ctx, (0.30, 0.31, 0.36), a)
        ctx.fill()
    ctx.restore()


def _bolt(ctx, x, y, s, col=None, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(15, -80)
    ctx.line_to(-45, 10)
    ctx.line_to(-5, 10)
    ctx.line_to(-20, 80)
    ctx.line_to(45, -15)
    ctx.line_to(5, -15)
    ctx.close_path()
    src(ctx, col or Y_, a)
    ctx.fill()
    ctx.restore()


def _plug(ctx, x, y, s, a=1.0):
    """Plug body pointing right, cable to the left."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-400, 0)
    ctx.curve_to(-250, 60, -150, -40, -60, 0)
    src(ctx, (0.35, 0.36, 0.40), a)
    ctx.set_line_width(22)
    ctx.stroke()
    rrect(ctx, -70, -55, 110, 110, 18)
    src(ctx, GREY2, a)
    ctx.fill()
    for dy in (-25, 25):
        rrect(ctx, 40, dy - 9, 50, 18, 5)
        src(ctx, (0.75, 0.62, 0.20), a)
        ctx.fill()
    ctx.restore()


def _socket(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -75, -90, 150, 180, 26)
    src(ctx, (1, 1, 1), a)
    ctx.fill()
    for dy in (-25, 25):
        rrect(ctx, -30, dy - 9, 60, 18, 5)
        src(ctx, K_, a)
        ctx.fill()
    ctx.restore()


def _building(ctx, x, y, s, t, on=1.0, a=1.0):
    """Data-centre building with vents and a roof unit."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -170, -110, 340, 220, 14)
    src(ctx, (0.26, 0.27, 0.32), a)
    ctx.fill_preserve()
    src(ctx, (0.60, 0.62, 0.68), a)
    ctx.set_line_width(5)
    ctx.stroke()
    rrect(ctx, -120, -150, 90, 40, 8)
    rrect(ctx, 30, -150, 90, 40, 8)
    src(ctx, (0.40, 0.42, 0.47), a)
    ctx.fill()
    for j in range(5):
        for r in range(2):
            lit = on * (0.5 + 0.5 * math.sin(t * 5 + j + r * 2))
            rrect(ctx, -140 + j * 58, -70 + r * 70, 46, 40, 6)
            src(ctx, Y_ if lit > 0.35 else (0.15, 0.15, 0.18), a * (0.9 if lit > 0.35 else 1))
            ctx.fill()
    ctx.restore()


def _pin(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(0, 90)
    ctx.curve_to(-30, 40, -70, 0, -70, -40)
    ctx.arc(0, -40, 70, math.pi, 0)
    ctx.curve_to(70, 0, 30, 40, 0, 90)
    src(ctx, RED, a)
    ctx.fill()
    ellipse(ctx, 0, -40, 28, 28)
    src(ctx, (1, 1, 1), a)
    ctx.fill()
    ctx.restore()


def _pylon(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    src(ctx, GREY2, a)
    ctx.set_line_width(9)
    ctx.move_to(-90, 220)
    ctx.line_to(-20, -200)
    ctx.line_to(20, -200)
    ctx.line_to(90, 220)
    for yy, w in ((-140, 130), (-60, 160)):
        ctx.move_to(-w, yy)
        ctx.line_to(w, yy)
    for k in range(4):
        y0 = -200 + k * 105
        y1 = y0 + 105
        x0 = -20 - 70 * (k / 4)
        x1 = -20 - 70 * ((k + 1) / 4)
        ctx.move_to(x0, y0)
        ctx.line_to(-x1, y1)
        ctx.move_to(-x0, y0)
        ctx.line_to(x1, y1)
    ctx.stroke()
    ctx.restore()


def _gauge(ctx, x, y, r, val, vmax, mark=None, a=1.0):
    a0, a1 = math.pi * 0.85, math.pi * 2.15
    ctx.arc(x, y, r, a0, a1)
    src(ctx, (0.25, 0.26, 0.30), a)
    ctx.set_line_width(40)
    ctx.stroke()
    av = a0 + (a1 - a0) * val / vmax
    ctx.arc(x, y, r, a0, av)
    src(ctx, Y_, a)
    ctx.stroke()
    if mark is not None:
        am = a0 + (a1 - a0) * mark / vmax
        ctx.move_to(x + (r - 40) * math.cos(am), y + (r - 40) * math.sin(am))
        ctx.line_to(x + (r + 40) * math.cos(am), y + (r + 40) * math.sin(am))
        src(ctx, TEAL, a)
        ctx.set_line_width(10)
        ctx.stroke()
    ctx.move_to(x, y)
    ctx.line_to(x + (r - 60) * math.cos(av), y + (r - 60) * math.sin(av))
    src(ctx, (1, 1, 1), a)
    ctx.set_line_width(12)
    ctx.stroke()
    ellipse(ctx, x, y, 22, 22)
    ctx.fill()


def _hourglass(ctx, x, y, s, t, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -90, -150, 180, 22, 8)
    rrect(ctx, -90, 128, 180, 22, 8)
    src(ctx, ORANGE, a)
    ctx.fill()
    ctx.move_to(-70, -128)
    ctx.line_to(70, -128)
    ctx.line_to(8, 0)
    ctx.line_to(70, 128)
    ctx.line_to(-70, 128)
    ctx.line_to(-8, 0)
    ctx.close_path()
    src(ctx, (1, 1, 1), 0.25 * a)
    ctx.fill_preserve()
    src(ctx, GREY2, a)
    ctx.set_line_width(6)
    ctx.stroke()
    u = (t * 0.25) % 1
    top = 100 * (1 - u)
    ctx.move_to(-70 * top / 128, -top)
    ctx.line_to(70 * top / 128, -top)
    ctx.line_to(4, -6)
    ctx.line_to(-4, -6)
    ctx.close_path()
    src(ctx, Y_, a)
    ctx.fill()
    bh = 20 + 90 * u
    ctx.move_to(-70, 128)
    ctx.line_to(70, 128)
    ctx.line_to(70 - 62 * bh / 128, 128 - bh)
    ctx.line_to(-70 + 62 * bh / 128, 128 - bh)
    ctx.close_path()
    ctx.fill()
    ctx.move_to(0, 0)
    ctx.line_to(0, 128 - bh)
    ctx.set_line_width(4)
    ctx.stroke()
    ctx.restore()


def _chip(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    src(ctx, GREY2, a)
    ctx.set_line_width(10)
    for k in range(5):
        d = -80 + k * 40
        for (x0, y0, x1, y1) in ((d, -100, d, -135), (d, 100, d, 135), (-100, d, -135, d), (100, d, 135, d)):
            ctx.move_to(x0, y0)
            ctx.line_to(x1, y1)
    ctx.stroke()
    rrect(ctx, -105, -105, 210, 210, 20)
    src(ctx, (0.20, 0.21, 0.25), a)
    ctx.fill()
    rrect(ctx, -60, -60, 120, 120, 12)
    src(ctx, TEAL, a)
    ctx.fill()
    text(ctx, "AI", 0, 20, 56, (1, 1, 1), alpha=a)
    ctx.restore()


def _icon(ctx, i, t, k):
    t0 = _card_start(i)
    lt = t - t0
    if i == 0:   # unplugged data centre goes dark
        dark = ease_io(seg(lt, 1.6, 2.4))
        for dx in (-250, 0, 250):
            _rack(ctx, W / 2 + dx, ICON_Y - 120, 0.75 * k, t, on=1 - dark, a=k)
        _socket(ctx, W / 2 + 330, ICON_Y + 230, 0.7, k)
        px = lerp(W / 2 + 230, W / 2 + 60, ease_io(seg(lt, 0.9, 1.6)))
        _plug(ctx, px, ICON_Y + 230, 0.75, k)
        sp = seg(lt, 1.5, 2.1)
        if 0 < sp < 1:
            for j in range(6):
                ang = j * 1.05 + 0.4
                r = 40 + 90 * sp
                cx = W / 2 + 270
                ctx.move_to(cx + 20 * math.cos(ang), ICON_Y + 230 + 20 * math.sin(ang))
                ctx.line_to(cx + r * math.cos(ang), ICON_Y + 230 + r * math.sin(ang))
            src(ctx, Y_, 1 - sp)
            ctx.set_line_width(8)
            ctx.stroke()
        u2 = ease_back(seg(lt, 2.4, 2.8))
        if u2 > 0.01:
            _pill(ctx, W / 2, ICON_Y + 380, "NOT ENOUGH ELECTRICITY", u2, col=Y_, w=760)
    elif i == 1:   # map pin + data centre + anchor customer
        _pin(ctx, W / 2, ICON_Y - 215, 0.7, ease_back(seg(lt, 0.1, 0.5)))
        u = ease_out(seg(lt, 0.4, 0.9))
        if u > 0.01:
            text(ctx, "LOUGHTON, ESSEX", W / 2, ICON_Y - 110, 58, (1, 1, 1), alpha=u)
            text(ctx, "NEAR LONDON, UK", W / 2, ICON_Y - 50, 42, TEAL, alpha=u)
        ub = ease_back(seg(lt, 1.6, 2.0))
        if ub > 0.01:
            _building(ctx, W / 2, ICON_Y + 120, 0.8 * ub, t, on=1.0)
            text(ctx, "NSCALE (PLANNED)", W / 2, ICON_Y + 255, 42, GREY2, alpha=ub)
        _pill(ctx, W / 2, ICON_Y + 360, "ANCHOR CUSTOMER: MICROSOFT", ease_back(seg(lt, 3.6, 4.0)), col=Y_, size=42, w=860)
    elif i == 2:   # pylon + 2030s
        _pylon(ctx, W / 2 - 240, ICON_Y - 40, 0.95 * k, k)
        text(ctx, "UK POWER NETWORKS", W / 2 - 240, ICON_Y + 250, 38, GREY2, alpha=k)
        _calendar(ctx, W / 2 + 200, ICON_Y - 110, 1.0, "POWER", "2030s", ease_back(seg(lt, 2.6, 3.0)))
        _pill(ctx, W / 2 + 200, ICON_Y + 90, "EARLY–MID 2030s", ease_back(seg(lt, 4.0, 4.4)), col=Y_, size=40, w=470)
        u4 = ease_out(seg(lt, 4.6, 5.0))
        if u4 > 0.01:
            text(ctx, "(REPORTED)", W / 2 + 200, ICON_Y + 190, 40, GREY, alpha=u4)
        for j in range(3):
            ph = (t * 0.8 + j / 3) % 1
            _bolt(ctx, lerp(W / 2 - 150, W / 2 + 60, ph), ICON_Y - 160 + 40 * j, 0.4, a=k * (1 - ph) * 0.8)
    elif i == 3:   # gauge 0->50, mark 90
        v = 50 * ease_out(seg(lt, 0.3, 1.6))
        _gauge(ctx, W / 2, ICON_Y - 10, 250, v, 100, mark=90 if lt > 2.0 else None, a=k)
        text(ctx, "%d MW" % round(v), W / 2, ICON_Y + 110, 80, Y_, alpha=k)
        _bolt(ctx, W / 2, ICON_Y - 110, 0.9, a=k)
        u2 = ease_out(seg(lt, 2.0, 2.4))
        if u2 > 0.01:
            text(ctx, "90", W / 2 + 330, ICON_Y - 30, 50, TEAL, alpha=u2)
        text(ctx, "MEGAWATTS PLANNED", W / 2, ICON_Y + 330, 46, (1, 1, 1), alpha=ease_out(seg(lt, 0.8, 1.2)))
    elif i == 4:   # single site + other projects
        _building(ctx, W / 2, ICON_Y - 210, 0.6 * k, t, on=0.0, a=k)
        ux = ease_back(seg(lt, 0.5, 0.9))
        if ux > 0.01:
            ctx.save()
            ctx.translate(W / 2 + 190, ICON_Y - 270)
            ctx.scale(ux, ux)
            ellipse(ctx, 0, 0, 42, 42)
            src(ctx, RED)
            ctx.fill()
            text(ctx, "1", 0, 20, 56, (1, 1, 1))
            ctx.restore()
        _pill(ctx, W / 2, ICON_Y - 50, "“SINGLE-SITE DECISION”", ease_back(seg(lt, 1.0, 1.4)), col=(1, 1, 1), size=42, w=760)
        items = (("NORWAY", 4.6), ("PORTUGAL", 5.3), ("UNITED STATES", 6.0))
        for j, (s_, st) in enumerate(items):
            u2 = ease_back(seg(lt, st, st + 0.4))
            if u2 > 0.01:
                y = ICON_Y + 90 + j * 105
                _check(ctx, 300, y - 18, u2)
                text(ctx, s_, 370, y, 54, (1, 1, 1), align="left", alpha=u2)
    elif i == 5:   # grid queue
        _hourglass(ctx, W / 2 + 310, ICON_Y - 120, 0.9 * k, t, k)
        _socket(ctx, 160, ICON_Y - 120, 0.55, k)
        for j in range(3):
            u = ease_back(seg(lt, 0.4 + j * 0.25, 0.8 + j * 0.25))
            if u > 0.01:
                _building(ctx, 330 + j * 165, ICON_Y - 120, 0.42 * u, t, on=0.0)
        u3 = ease_out(seg(lt, 1.2, 1.6))
        if u3 > 0.01:
            text(ctx, "WAITING FOR A GRID CONNECTION", W / 2, ICON_Y + 60, 40, GREY2, alpha=u3)
        _pill(ctx, W / 2, ICON_Y + 200, "UP TO 13 YEARS OF DELAY", ease_back(seg(lt, 4.6, 5.0)), col=Y_, w=820)
    elif i == 6:   # chips -> power
        _chip(ctx, W / 2 - 230, ICON_Y - 180, 0.85 * k, k)
        ua = ease_io(seg(lt, 2.0, 2.6))
        if ua > 0.01:
            ctx.move_to(W / 2 - 80, ICON_Y - 180)
            ctx.line_to(W / 2 - 80 + 140 * ua, ICON_Y - 180)
            src(ctx, Y_)
            ctx.set_line_width(14)
            ctx.stroke()
        ub = ease_back(seg(lt, 2.6, 3.0))
        if ub > 0.01:
            for r, al in ((150, 0.12), (120, 0.2)):
                ellipse(ctx, W / 2 + 240, ICON_Y - 180, r * ub, r * ub)
                src(ctx, Y_, al)
                ctx.fill()
            _bolt(ctx, W / 2 + 240, ICON_Y - 180, 1.4 * ub)
        for j, (s_, st) in enumerate((("CHIPS STILL MATTER", 1.0), ("POWER IS THE NEW LIMIT", 3.0), ("SOME GRIDS CAN'T KEEP UP", 4.6))):
            u2 = ease_back(seg(lt, st, st + 0.4))
            if u2 > 0.01:
                y = ICON_Y + 70 + j * 120
                _check(ctx, 150, y - 18, u2) if j == 0 else _xq(ctx, 150, y - 18, u2)
                text(ctx, s_, 210, y, 50, (1, 1, 1), align="left", alpha=u2)


def _xq(ctx, x, y, u):
    ellipse(ctx, x, y, 40 * u, 40 * u)
    src(ctx, ORANGE)
    ctx.fill()
    text(ctx, "!", x, y + 18 * u, 54 * u, (1, 1, 1))


def _headline(ctx, i, t):
    t0 = _card_start(i)
    k = ease_back(seg(t, t0, t0 + 0.35))
    head, sub = CARDS[i]
    size = 128 if len(head) <= 9 else (108 if len(head) <= 11 else 92)
    ctx.save()
    ctx.translate(W / 2, 560)
    ctx.scale(k, k)
    text(ctx, head, 0, 0, size, Y_)
    ctx.restore()
    if sub:
        ss = 38
        while ss > 26 and len(wrap(ctx, sub, ss, W - 120)) > 1:
            ss -= 2
        text(ctx, sub, W / 2, 650, ss, (1, 1, 1), alpha=ease_out(seg(t, t0 + 0.3, t0 + 0.7)))
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
        brand.caption(ctx, ctext, 1500, CAP_SIZE, pop=pk * pulse)
    _wipe(ctx, t)
    brand.watermark(ctx)
    brand.end_card(ctx, t, DURATION - 1.4)
    surf.flush()
    return surf
