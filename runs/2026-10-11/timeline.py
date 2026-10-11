"""2026-10-11 mythfact: Tesla drops the "Full Self-Driving" name in Europe (contract: DURATION + render_frame)."""
import json
import math
import os
import cairo
from gfx import W, H, ease_back, ease_out, ease_io, seg, src, text, ellipse, rrect, lerp, wrap, FONT
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
WHITE = (1, 1, 1)
TEAL = (0.14, 0.60, 0.62)
RED = (0.88, 0.20, 0.20)
GREY = (0.55, 0.56, 0.60)
CAP_SIZE = 64
# line index -> scene
HOOK, RENAME, TWO, MYTH1, FACT1, MINISTRY, MYTH2, FACT2, USA, OUTRO = range(10)
TOP = (430, 880)      # myth panel y-range
BOT = (920, 1370)     # fact panel y-range


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


def _st(i):
    return 0.0 if i == 0 else LINES[i]["start"] - 0.3


def _end(i):
    return LINES[i]["start"] + LINES[i]["dur"]


# ------------------------------------------------------------------ background
def _background(ctx, t):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.06, 0.06, 0.08)
    g.add_color_stop_rgb(1, 0.01, 0.01, 0.02)
    ctx.set_source(g)
    ctx.paint()
    for i in range(80):
        x = (i * 173.3 + t * (6 + i % 5 * 5)) % W
        y = (i * 311.7) % H
        r = 1.5 + i % 3
        ellipse(ctx, x, y, r, r)
        src(ctx, WHITE, 0.15 + 0.15 * math.sin(t * 2 + i))
        ctx.fill()
    u = ease_out(seg(t, 0.0, 0.5))
    ctx.save()
    ctx.translate(W / 2, 330)
    ctx.rotate(-0.07)
    ctx.rectangle(-W * u, -52, 2 * W * u, 104)
    src(ctx, Y_)
    ctx.fill()
    text(ctx, "MYTH vs FACT · SELF-DRIVING", -W / 2 + 80 + (1 - u) * -300, 20, 52, K_, align="left", alpha=u)
    ctx.restore()


# ------------------------------------------------------------------ props
def _car(ctx, x, y, s, t, a=1.0, driver=True):
    """Generic hatchback, side view, no brand marks. (x, y) = road contact centre."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ellipse(ctx, 0, 0, 330, 22)
    src(ctx, (0, 0, 0), 0.45 * a)
    ctx.fill()
    # body
    ctx.move_to(-330, -60)
    ctx.curve_to(-335, -120, -310, -140, -260, -145)
    ctx.line_to(-150, -150)
    ctx.curve_to(-100, -240, -40, -255, 60, -255)
    ctx.curve_to(150, -255, 200, -200, 240, -150)
    ctx.curve_to(310, -140, 335, -120, 335, -70)
    ctx.line_to(335, -45)
    ctx.line_to(-330, -45)
    ctx.close_path()
    g = cairo.LinearGradient(0, -255, 0, -45)
    g.add_color_stop_rgba(0, 0.92, 0.93, 0.96, a)
    g.add_color_stop_rgba(1, 0.62, 0.65, 0.72, a)
    ctx.set_source(g)
    ctx.fill_preserve()
    src(ctx, (0.25, 0.27, 0.32), a)
    ctx.set_line_width(5)
    ctx.stroke()
    # windows
    ctx.move_to(-125, -152)
    ctx.curve_to(-85, -225, -40, -235, 40, -235)
    ctx.line_to(40, -152)
    ctx.close_path()
    ctx.move_to(60, -235)
    ctx.curve_to(140, -235, 180, -195, 215, -152)
    ctx.line_to(60, -152)
    ctx.close_path()
    src(ctx, (0.13, 0.20, 0.30), a)
    ctx.fill()
    if driver:   # silhouette with hands on the wheel
        ellipse(ctx, 120, -195, 24, 26)
        src(ctx, (0.85, 0.65, 0.45), a)
        ctx.fill()
        ctx.move_to(158, -185)
        ctx.line_to(170, -160)
        src(ctx, (0.1, 0.1, 0.1), a)
        ctx.set_line_width(8)
        ctx.stroke()
    # lights + door line
    rrect(ctx, 300, -120, 30, 22, 8)
    src(ctx, Y_, a)
    ctx.fill()
    rrect(ctx, -330, -118, 22, 22, 8)
    src(ctx, RED, a)
    ctx.fill()
    ctx.move_to(50, -150)
    ctx.line_to(50, -55)
    src(ctx, (0.35, 0.37, 0.42), a)
    ctx.set_line_width(3)
    ctx.stroke()
    # wheels
    for wx in (-205, 210):
        ellipse(ctx, wx, -40, 62, 62)
        src(ctx, (0.08, 0.08, 0.09), a)
        ctx.fill()
        ellipse(ctx, wx, -40, 34, 34)
        src(ctx, (0.70, 0.72, 0.76), a)
        ctx.fill()
        for j in range(5):
            ang = t * 9 + j * 2 * math.pi / 5
            ctx.move_to(wx, -40)
            ctx.line_to(wx + 30 * math.cos(ang), -40 + 30 * math.sin(ang))
        src(ctx, (0.35, 0.36, 0.4), a)
        ctx.set_line_width(5)
        ctx.stroke()
    ctx.restore()


def _road(ctx, y, t, a=1.0, x0=0, x1=W):
    ctx.rectangle(x0, y, x1 - x0, 14)
    src(ctx, (0.3, 0.31, 0.35), a)
    ctx.fill()
    off = (t * 420) % 160
    for j in range(-1, int((x1 - x0) / 160) + 2):
        x = x1 - j * 160 - off
        if x0 <= x <= x1 - 80:
            rrect(ctx, x, y + 40, 80, 10, 5)
            src(ctx, Y_, 0.5 * a)
            ctx.fill()


def _plate(ctx, x, y, label, fg, bg, u, size=56, strike=0.0):
    """Name tag: rounded plate with text; optional red strike-through."""
    if u <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(u, u)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    tw = ctx.text_extents(label).x_advance
    w = tw + 80
    rrect(ctx, -w / 2, -size * 0.95, w, size * 1.6, 22)
    src(ctx, bg)
    ctx.fill()
    text(ctx, label, 0, size * 0.32, size, fg)
    if strike > 0.01:
        ctx.move_to(-w / 2 - 10, 0)
        ctx.line_to(-w / 2 - 10 + (w + 20) * strike, -6)
        src(ctx, RED)
        ctx.set_line_width(14)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
    ctx.restore()


def _xstamp(ctx, x, y, r, u):
    if u <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(-0.12)
    ctx.scale(u, u)
    ellipse(ctx, 0, 0, r * 1.25, r * 1.25)
    src(ctx, RED, 0.9)
    ctx.set_line_width(12)
    ctx.stroke()
    for sgn in (-1, 1):
        ctx.move_to(-r * 0.7, -r * 0.7 * sgn)
        ctx.line_to(r * 0.7, r * 0.7 * sgn)
    ctx.set_line_width(24)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    ctx.restore()


def _check(ctx, x, y, r, u):
    if u <= 0.01:
        return
    ellipse(ctx, x, y, r * u, r * u)
    src(ctx, TEAL)
    ctx.fill()
    ctx.move_to(x - r * 0.45, y)
    ctx.line_to(x - r * 0.1, y + r * 0.38)
    ctx.line_to(x + r * 0.5, y - r * 0.42)
    src(ctx, WHITE, u)
    ctx.set_line_width(r * 0.2)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()


def _wheel_icon(ctx, x, y, r, t, a=1.0):
    ellipse(ctx, x, y, r, r)
    src(ctx, WHITE, a)
    ctx.set_line_width(r * 0.18)
    ctx.stroke()
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(0.35 * math.sin(t * 2.5))
    for ang in (math.pi / 2, math.pi * 7 / 6, -math.pi / 6):
        ctx.move_to(0, 0)
        ctx.line_to(r * math.cos(ang), r * math.sin(ang))
    ctx.set_line_width(r * 0.16)
    ctx.stroke()
    ellipse(ctx, 0, 0, r * 0.22, r * 0.22)
    ctx.fill()
    ctx.restore()


def _pedal_icon(ctx, x, y, r, col, a=1.0, press=0.0):
    rrect(ctx, x - r * 0.55, y - r + press * r * 0.3, r * 1.1, r * 1.8, r * 0.25)
    src(ctx, col, a)
    ctx.fill()
    for j in range(3):
        ctx.move_to(x - r * 0.35, y - r * 0.5 + j * r * 0.5 + press * r * 0.3)
        ctx.line_to(x + r * 0.35, y - r * 0.5 + j * r * 0.5 + press * r * 0.3)
    src(ctx, K_, a)
    ctx.set_line_width(5)
    ctx.stroke()


def _eye(ctx, x, y, r, t, a=1.0):
    blink = 1 - 0.9 * max(0, 1 - abs(((t * 0.6) % 3) - 1.5) * 8)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(1, max(0.1, blink))
    ctx.move_to(-r, 0)
    ctx.curve_to(-r * 0.5, -r * 0.75, r * 0.5, -r * 0.75, r, 0)
    ctx.curve_to(r * 0.5, r * 0.75, -r * 0.5, r * 0.75, -r, 0)
    src(ctx, WHITE, a)
    ctx.fill()
    ellipse(ctx, 0, 0, r * 0.38, r * 0.38)
    src(ctx, TEAL, a)
    ctx.fill()
    ellipse(ctx, 0, 0, r * 0.17, r * 0.17)
    src(ctx, K_, a)
    ctx.fill()
    ctx.restore()


def _stars(ctx, x, y, r, t, a=1.0):
    """Ring of 12 stars (Europe)."""
    for j in range(12):
        ang = j * math.pi / 6 + 0.1 * math.sin(t)
        cx, cy = x + r * math.cos(ang), y + r * math.sin(ang)
        ctx.save()
        ctx.translate(cx, cy)
        for k in range(10):
            rr = 22 if k % 2 == 0 else 9
            th = -math.pi / 2 + k * math.pi / 5
            (ctx.move_to if k == 0 else ctx.line_to)(rr * math.cos(th), rr * math.sin(th))
        ctx.close_path()
        src(ctx, Y_, a)
        ctx.fill()
        ctx.restore()


def _panel(ctx, y0, y1, col, label, u, label_col=WHITE):
    if u <= 0.01:
        return
    rrect(ctx, 60, y0, W - 120, y1 - y0, 36)
    src(ctx, col, 0.22 * u)
    ctx.fill_preserve()
    src(ctx, col, 0.9 * u)
    ctx.set_line_width(6)
    ctx.stroke()
    rrect(ctx, 100, y0 - 34, 230, 72, 22)
    src(ctx, col, u)
    ctx.fill()
    text(ctx, label, 215, y0 + 20, 50, label_col, alpha=u)


def _para(ctx, s, x, y, size, col, max_w, a=1.0, lh=1.18):
    for j, ln in enumerate(wrap(ctx, s, size, max_w)):
        text(ctx, ln, x, y + j * size * lh, size, col, alpha=a)


# ------------------------------------------------------------------ scenes
def _intro(ctx, i, t):
    lt0 = t - _st(HOOK)
    k = ease_out(seg(lt0, 0.1, 0.6))
    _road(ctx, 1020, t, k)
    _car(ctx, W / 2 + lerp(-700, 0, ease_out(seg(lt0, 0.0, 0.9))), 1020, 1.25, t, k)
    if i <= RENAME:
        head = "NAME DROPPED" if i == HOOK else "NEW NAME"
        kk = ease_back(seg(t, _st(i), _st(i) + 0.35))
        ctx.save()
        ctx.translate(W / 2, 560)
        ctx.scale(kk, kk)
        text(ctx, head, 0, 0, 104, Y_)
        ctx.restore()
        text(ctx, "IN EUROPE", W / 2, 650, 44, WHITE, alpha=ease_out(seg(t, 0.4, 0.9)))
        strike = ease_io(seg(t, LINES[HOOK]["start"] + 1.2, LINES[HOOK]["start"] + 1.8))
        old_u = ease_back(seg(t, 0.3, 0.7)) * (1 - 0.35 * ease_out(seg(t, _st(RENAME), _st(RENAME) + 0.4)))
        _plate(ctx, W / 2, 1180, "FULL SELF-DRIVING", WHITE, (0.2, 0.21, 0.25), old_u, 60, strike)
        if i == RENAME:
            u = ease_back(seg(t, LINES[RENAME]["start"] + 0.6, LINES[RENAME]["start"] + 1.0))
            _plate(ctx, W / 2, 1300, "TESLA ASSISTED DRIVING", K_, Y_, u, 60)
    else:   # TWO myths teaser
        kk = ease_back(seg(t, _st(TWO), _st(TWO) + 0.35))
        ctx.save()
        ctx.translate(W / 2, 560)
        ctx.scale(kk, kk)
        text(ctx, "2 MYTHS", 0, 0, 130, Y_)
        ctx.restore()
        for j in range(2):
            u = ease_back(seg(t, LINES[TWO]["start"] + 1.6 + j * 0.35, LINES[TWO]["start"] + 2.0 + j * 0.35))
            if u > 0.01:
                ctx.save()
                ctx.translate(W / 2 + (j - 0.5) * 420, 1240)
                ctx.rotate((j - 0.5) * 0.12)
                ctx.scale(u, u)
                rrect(ctx, -170, -80, 340, 160, 28)
                src(ctx, RED)
                ctx.fill()
                text(ctx, "MYTH %d" % (j + 1), 0, 22, 66, WHITE)
                ctx.restore()


def _mythfact(ctx, i, t):
    first = i in (MYTH1, FACT1, MINISTRY)
    m, f = (MYTH1, FACT1) if first else (MYTH2, FACT2)
    um = ease_out(seg(t, _st(m), _st(m) + 0.4))
    _panel(ctx, TOP[0], TOP[1], RED, "MYTH", um)
    stamp = ease_back(seg(t, _end(m) + 0.05, _end(m) + 0.35))
    claim = "THE CAR DRIVES ITSELF" if first else "EUROPE HAS BANNED IT"
    cy = TOP[0] + 120
    _para(ctx, claim, W / 2, cy, 64 if first else 58, WHITE, W - 160, um * (1 - 0.45 * stamp))
    if first:   # empty-handed driver napping: zzz
        _car(ctx, W / 2, TOP[1] - 40, 0.62, t, um * (1 - 0.45 * stamp), driver=False)
    else:
        _stars(ctx, W / 2, TOP[0] + 330, 85, t, um * (1 - 0.45 * stamp))
        text(ctx, "EU", W / 2, TOP[0] + 352, 60, WHITE, alpha=um * (1 - 0.45 * stamp))
    _xstamp(ctx, W - 230, TOP[0] + 270, 90, stamp)
    if i == m:
        return
    uf = ease_out(seg(t, _st(f), _st(f) + 0.4))
    _panel(ctx, BOT[0], BOT[1], TEAL, "FACT", uf)
    _check(ctx, W - 160, BOT[0] + 4, 46, ease_back(seg(t, _st(f) + 0.2, _st(f) + 0.6)))
    lt = t - LINES[f]["start"]
    if first and i == FACT1:
        labels = (("STEER", 0.0), ("BRAKE", 0.5), ("ACCELERATE", 0.9))
        for j, (lab, d) in enumerate(labels):
            u = ease_back(seg(lt, 0.4 + d, 0.8 + d))
            if u <= 0.01:
                continue
            x = 260 + j * 280
            y = BOT[0] + 150
            ctx.save()
            ctx.translate(x, y)
            ctx.scale(u, u)
            if j == 0:
                _wheel_icon(ctx, 0, 0, 62, t)
            else:
                _pedal_icon(ctx, 0, 0, 50, RED if j == 1 else (0.46, 0.73, 0.0), 1.0,
                            0.5 + 0.5 * math.sin(t * 4 + j))
            ctx.restore()
            text(ctx, lab, x, y + 115, 40, WHITE, alpha=u)
        u2 = ease_out(seg(lt, 2.4, 2.9))
        if u2 > 0.01:
            rrect(ctx, 120, BOT[0] + 300, W - 240, 120, 30)
            src(ctx, Y_, u2)
            ctx.fill()
            _eye(ctx, 215, BOT[0] + 360, 46, t, u2)
            text(ctx, "DRIVER MUST SUPERVISE", 280, BOT[0] + 376, 44, K_, align="left", alpha=u2)
    elif first:   # MINISTRY
        lt = t - LINES[MINISTRY]["start"]
        u = ease_out(seg(lt, -0.2, 0.3))
        text(ctx, "GERMANY'S TRANSPORT MINISTRY", W / 2, BOT[0] + 120, 46, Y_, alpha=u)
        _plate(ctx, W / 2, BOT[0] + 245, "FULL SELF-DRIVING", WHITE, (0.2, 0.21, 0.25), u, 58)
        s = ease_back(seg(lt, 1.6, 2.0))
        if s > 0.01:
            ctx.save()
            ctx.translate(W / 2 + 40, BOT[0] + 360)
            ctx.rotate(-0.1)
            ctx.scale(s, s)
            rrect(ctx, -285, -55, 570, 110, 16)
            src(ctx, RED)
            ctx.set_line_width(10)
            ctx.stroke()
            text(ctx, "MISLEADING", 0, 24, 72, RED)
            ctx.restore()
    else:   # FACT2
        rows = (("NETHERLANDS", "APPROVED · APRIL 2026", 0.2), ("GERMANY", "BACKS EU-WIDE APPROVAL", 2.6))
        for j, (who, what, d) in enumerate(rows):
            u = ease_back(seg(lt, d, d + 0.4))
            if u <= 0.01:
                continue
            y = BOT[0] + 140 + j * 170
            _check(ctx, 175, y - 20, 42 * u, 1.0)
            text(ctx, who, 245, y - 2, 60, Y_, align="left", alpha=u)
            text(ctx, what, 245, y + 54, 42, WHITE, align="left", alpha=u)


def _usa(ctx, t):
    t0 = _st(USA)
    kk = ease_back(seg(t, t0, t0 + 0.35))
    ctx.save()
    ctx.translate(W / 2, 560)
    ctx.scale(kk, kk)
    text(ctx, "TWO NAMES", 0, 0, 120, Y_)
    ctx.restore()
    for j, (where, name, fg, bg, d) in enumerate((
            ("USA", "FULL SELF-DRIVING (SUPERVISED)", WHITE, (0.2, 0.21, 0.25), 0.3),
            ("EUROPE", "TESLA ASSISTED DRIVING", K_, Y_, 1.2))):
        u = ease_back(seg(t, t0 + d, t0 + d + 0.4))
        y = 860 + j * 300
        text(ctx, where, W / 2, y - 80, 52, WHITE, alpha=min(1, u))
        _plate(ctx, W / 2, y, name, fg, bg, u, 48)


def _outro(ctx, t):
    t0 = _st(OUTRO)
    k = ease_out(seg(t, t0, t0 + 0.4))
    _road(ctx, 1260, t, k)
    _car(ctx, W / 2, 1260, 0.95, t, k)
    for j, (s, col) in enumerate((("SAME TECH.", WHITE), ("NEW NAME.", Y_), ("WORDS MATTER.", Y_))):
        d = (0.0, 0.7, 1.4)[j]
        u = ease_back(seg(t, LINES[OUTRO]["start"] + d - 0.1, LINES[OUTRO]["start"] + d + 0.25))
        if u > 0.01:
            ctx.save()
            ctx.translate(W / 2, 560 + j * 150)
            ctx.scale(u, u)
            text(ctx, s, 0, 0, 104 if j < 2 else 90, col)
            ctx.restore()


def _wipe(ctx, t):
    """Yellow wipe at scene changes."""
    for i in (MYTH1, MYTH2, USA, OUTRO):
        u = seg(t, _st(i) - 0.2, _st(i) + 0.2)
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
        if i <= TWO:
            _intro(ctx, i, t)
        elif i <= FACT2:
            _mythfact(ctx, i, t)
        elif i == USA:
            _usa(ctx, t)
        else:
            _outro(ctx, t)
        line = LINES[i]
        c0, ctext = _caption_text(i, t)
        pk = ease_back(seg(t, c0 - 0.2, c0 + 0.1))
        f = int((t - line["start"]) * 30)
        pulse = 1 + 0.03 * (ENV[i][f] if 0 <= f < len(ENV[i]) else 0)
        brand.caption(ctx, ctext, 1510, CAP_SIZE, pop=pk * pulse)
    _wipe(ctx, t)
    brand.watermark(ctx)
    brand.end_card(ctx, t, DURATION - 1.4)
    surf.flush()
    return surf
