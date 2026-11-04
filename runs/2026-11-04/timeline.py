"""2026-11-04 mythfact: Google's Dreambeans AI story app comes to India (contract: DURATION + render_frame)."""
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
HOOK, WHAT, TWO, MYTH1, FACT1, VEO, MYTH2, FACT2, DETAILS, OUTRO = range(10)
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
    text(ctx, "MYTH vs FACT · AI STORIES", -W / 2 + 80 + (1 - u) * -300, 20, 52, K_, align="left", alpha=u)
    ctx.restore()


# ------------------------------------------------------------------ props
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




ORANGE = (0.96, 0.55, 0.18)
CREAM = (0.99, 0.94, 0.83)
PURPLE = (0.55, 0.42, 0.85)
NAVY = (0.12, 0.16, 0.30)


def _picture(ctx, x, y, w, h, t, a=1.0, scene=0):
    """Tiny illustrated storybook picture (sky, sun, hills, house) clipped to a rounded rect."""
    ctx.save()
    rrect(ctx, x, y, w, h, 14)
    ctx.clip()
    sky = [(0.55, 0.80, 0.95), (0.98, 0.72, 0.45), (0.30, 0.30, 0.60)][scene % 3]
    src(ctx, sky, a)
    ctx.paint_with_alpha(a)
    ellipse(ctx, x + w * 0.78, y + h * 0.28, h * 0.13, h * 0.13)
    src(ctx, Y_ if scene % 3 != 2 else WHITE, a)
    ctx.fill()
    for k, col in enumerate(((0.36, 0.70, 0.40), (0.24, 0.56, 0.32))):
        ctx.move_to(x, y + h)
        for q in range(9):
            xx = x + w * q / 8
            ctx.line_to(xx, y + h * (0.62 + 0.08 * k) + math.sin(q * 1.3 + k + scene) * h * 0.06)
        ctx.line_to(x + w, y + h)
        ctx.close_path()
        src(ctx, col, a)
        ctx.fill()
    hx, hy = x + w * 0.3, y + h * 0.58
    ctx.rectangle(hx - w * 0.08, hy, w * 0.16, h * 0.18)
    src(ctx, CREAM, a)
    ctx.fill()
    ctx.move_to(hx - w * 0.11, hy)
    ctx.line_to(hx, hy - h * 0.14)
    ctx.line_to(hx + w * 0.11, hy)
    ctx.close_path()
    src(ctx, RED, a)
    ctx.fill()
    ctx.restore()


def _book(ctx, cx, cy, s, t, a=1.0, open_=1.0, scene=0):
    """Open storybook: two pages, left picture, right text lines. (cx, cy) = spine centre."""
    if a <= 0.01 or s <= 0.01:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    rrect(ctx, -330, -210, 660, 420, 26)
    src(ctx, ORANGE, a)
    ctx.fill()
    pw = 300 * open_
    rrect(ctx, -pw - 8, -190, pw, 380, 12)
    src(ctx, CREAM, a)
    ctx.fill()
    rrect(ctx, 8, -190, 300, 380, 12)
    src(ctx, CREAM, a)
    ctx.fill()
    if open_ > 0.6:
        _picture(ctx, -pw + 16, -165, pw - 48, 330, t, a * seg(open_, 0.6, 1.0), scene)
    for r in range(6):
        ww = 230 - (r * 37) % 90
        rrect(ctx, 38, -150 + r * 52, ww, 16, 8)
        src(ctx, (0.55, 0.50, 0.45), 0.8 * a)
        ctx.fill()
    ctx.move_to(0, -200)
    ctx.line_to(0, 200)
    src(ctx, (0.75, 0.38, 0.12), a)
    ctx.set_line_width(6)
    ctx.stroke()
    ctx.restore()


def _phone(ctx, cx, cy, s, a=1.0, screen=None):
    if a <= 0.01 or s <= 0.01:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    rrect(ctx, -130, -250, 260, 500, 40)
    src(ctx, (0.18, 0.19, 0.22), a)
    ctx.fill()
    rrect(ctx, -115, -230, 230, 460, 30)
    src(ctx, screen or NAVY, a)
    ctx.fill()
    rrect(ctx, -35, -222, 70, 14, 7)
    src(ctx, K_, a)
    ctx.fill()
    ctx.restore()


def _app(ctx, kind, x, y, s, a=1.0, label=None):
    """Generic (non-branded) app tiles: mail, calendar, photos, video."""
    if a <= 0.01 or s <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -70, -70, 140, 140, 32)
    src(ctx, WHITE, a)
    ctx.fill()
    if kind == "mail":
        rrect(ctx, -46, -32, 92, 64, 8)
        src(ctx, RED, a)
        ctx.fill()
        ctx.move_to(-46, -28)
        ctx.line_to(0, 8)
        ctx.line_to(46, -28)
        src(ctx, WHITE, a)
        ctx.set_line_width(7)
        ctx.stroke()
    elif kind == "cal":
        rrect(ctx, -46, -42, 92, 86, 10)
        src(ctx, TEAL, a)
        ctx.fill()
        ctx.rectangle(-46, -22, 92, 66)
        src(ctx, WHITE, a)
        ctx.fill()
        for q in range(3):
            for r in range(2):
                ctx.rectangle(-36 + q * 26, -12 + r * 24, 18, 16)
        src(ctx, TEAL, 0.8 * a)
        ctx.fill()
    elif kind == "photo":
        rrect(ctx, -46, -38, 92, 76, 10)
        src(ctx, (0.55, 0.80, 0.95), a)
        ctx.fill()
        ctx.move_to(-46, 38)
        ctx.line_to(-12, -6)
        ctx.line_to(10, 18)
        ctx.line_to(26, 2)
        ctx.line_to(46, 38)
        ctx.close_path()
        src(ctx, (0.30, 0.65, 0.38), a)
        ctx.fill()
        ellipse(ctx, 24, -18, 9, 9)
        src(ctx, Y_, a)
        ctx.fill()
    else:  # video
        rrect(ctx, -48, -34, 96, 68, 16)
        src(ctx, ORANGE, a)
        ctx.fill()
        ctx.move_to(-14, -18)
        ctx.line_to(20, 0)
        ctx.line_to(-14, 18)
        ctx.close_path()
        src(ctx, WHITE, a)
        ctx.fill()
    ctx.restore()
    if label:
        text(ctx, label, x, y + 70 * s + 44, 34, WHITE, alpha=a)


def _promptbox(ctx, cx, cy, w, t, a=1.0, typed=1.0):
    rrect(ctx, cx - w / 2, cy - 55, w, 110, 55)
    src(ctx, WHITE, a)
    ctx.fill()
    s = "Write a story about..."
    n = int(len(s) * typed)
    text(ctx, s[:n] + ("|" if int(t * 3) % 2 else ""), cx - w / 2 + 50, cy + 16, 44, (0.35, 0.36, 0.40), align="left", alpha=a)


def _sparkle(ctx, x, y, r, a=1.0, col=None):
    ctx.move_to(x, y - r)
    ctx.curve_to(x + r * 0.15, y - r * 0.15, x + r * 0.15, y - r * 0.15, x + r, y)
    ctx.curve_to(x + r * 0.15, y + r * 0.15, x + r * 0.15, y + r * 0.15, x, y + r)
    ctx.curve_to(x - r * 0.15, y + r * 0.15, x - r * 0.15, y + r * 0.15, x - r, y)
    ctx.curve_to(x - r * 0.15, y - r * 0.15, x - r * 0.15, y - r * 0.15, x, y - r)
    src(ctx, col or Y_, a)
    ctx.fill()


def _lock(ctx, x, y, s, a=1.0):
    if a <= 0.01 or s <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.arc(0, -40, 50, math.pi, 2 * math.pi)
    src(ctx, GREY, a)
    ctx.set_line_width(18)
    ctx.stroke()
    rrect(ctx, -75, -40, 150, 120, 20)
    src(ctx, Y_, a)
    ctx.fill()
    ellipse(ctx, 0, 10, 14, 14)
    src(ctx, K_, a)
    ctx.fill()
    ctx.rectangle(-6, 10, 12, 36)
    ctx.fill()
    ctx.restore()


def _bin(ctx, x, y, s, a=1.0):
    if a <= 0.01 or s <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -70, -80, 140, 20, 8)
    src(ctx, WHITE, a)
    ctx.fill()
    rrect(ctx, -20, -98, 40, 22, 6)
    ctx.fill()
    ctx.move_to(-58, -52)
    ctx.line_to(58, -52)
    ctx.line_to(46, 80)
    ctx.line_to(-46, 80)
    ctx.close_path()
    ctx.fill()
    for q in (-24, 0, 24):
        ctx.move_to(q, -30)
        ctx.line_to(q * 0.85, 60)
    src(ctx, K_, a)
    ctx.set_line_width(8)
    ctx.stroke()
    ctx.restore()


def _headline(ctx, t0, t, head, sub=None, y=560, col=None, size=110):
    kk = ease_back(seg(t, t0, t0 + 0.35))
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    while ctx.text_extents(head).x_advance > W - 160 and size > 60:
        size -= 4
        ctx.set_font_size(size)
    if kk > 0.01:
        ctx.save()
        ctx.translate(W / 2, y)
        ctx.scale(kk, kk)
        text(ctx, head, 0, 0, size, col or Y_)
        ctx.restore()
    if sub:
        text(ctx, sub, W / 2, y + 85, 44, WHITE, alpha=ease_out(seg(t, t0 + 0.3, t0 + 0.7)))


def _india_pin(ctx, x, y, s, a=1.0):
    """Map pin with 'INDIA' tag (no flag/map outline)."""
    if a <= 0.01 or s <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(0, 0)
    ctx.curve_to(-70, -80, -70, -160, 0, -160)
    ctx.curve_to(70, -160, 70, -80, 0, 0)
    src(ctx, ORANGE, a)
    ctx.fill()
    ellipse(ctx, 0, -110, 26, 26)
    src(ctx, WHITE, a)
    ctx.fill()
    ctx.restore()


# ------------------------------------------------------------------ scenes
def _intro(ctx, i, t):
    if i == HOOK:
        _headline(ctx, 0.0, t, "YOUR DAY", "AS AN AI STORYBOOK")
        lt = t - LINES[HOOK]["start"]
        op = ease_io(seg(lt, 0.2, 1.3))
        _book(ctx, W / 2, 1010, 1.15 * ease_back(seg(lt, -0.3, 0.3)), t, 1.0, op, scene=int(lt / 1.2) % 3)
        for j in range(6):
            ph = (t * 0.7 + j / 6) % 1
            _sparkle(ctx, W / 2 + math.cos(j * 2.1) * 420 * ph, 1010 - 300 * ph, 22 * (1 - ph), op * (1 - ph))
        u = ease_back(seg(lt, 2.7, 3.1))
        if u > 0.01:
            _india_pin(ctx, 860, 1340, 0.9 * u, 1.0)
            _plate(ctx, W / 2 - 60, 1330, "NOW IN INDIA", K_, Y_, u, 58)
    elif i == WHAT:
        t0 = _st(WHAT)
        lt = t - LINES[WHAT]["start"]
        _headline(ctx, t0, t, "DREAMBEANS", "A GOOGLE LABS EXPERIMENT", size=120)
        k = ease_out(seg(lt, -0.2, 0.3))
        # simple globe-free route: US tag -> India tag
        _plate(ctx, 270, 900, "US", WHITE, GREY, ease_back(seg(lt, 0.4, 0.8)), 64)
        _plate(ctx, 790, 900, "INDIA", K_, Y_, ease_back(seg(lt, 1.8, 2.2)), 64)
        u = ease_io(seg(lt, 0.9, 1.9))
        if u > 0.01:
            ctx.move_to(370, 900)
            ctx.curve_to(480, 780, 580, 780, 370 + 300 * u, 860 - 0 * u)
            src(ctx, Y_, k)
            ctx.set_line_width(8)
            ctx.set_dash([18, 14])
            ctx.stroke()
            ctx.set_dash([])
        _phone(ctx, W / 2, 1110, 0.55 * k, k)
        _book(ctx, W / 2, 1110, 0.26 * k, t, k, 1.0, scene=1)
        u2 = ease_back(seg(lt, 2.4, 2.8))
        if u2 > 0.01:
            _plate(ctx, W / 2, 1330, "1ST COUNTRY OUTSIDE THE US", WHITE, TEAL, u2, 46)
    else:
        t0 = _st(TWO)
        _headline(ctx, t0, t, "2 MYTHS", size=130)
        for j in range(2):
            u = ease_back(seg(t, t0 + 0.4 + j * 0.3, t0 + 0.8 + j * 0.3))
            if u > 0.01:
                ctx.save()
                ctx.translate(W / 2 + (j - 0.5) * 420, 1050)
                ctx.rotate((j - 0.5) * 0.12)
                ctx.scale(u, u)
                rrect(ctx, -170, -80, 340, 160, 28)
                src(ctx, RED)
                ctx.fill()
                text(ctx, "MYTH %d" % (j + 1), 0, 22, 66, WHITE)
                ctx.restore()


def _mythfact(ctx, i, t):
    first = i in (MYTH1, FACT1, VEO)
    m, f = (MYTH1, FACT1) if first else (MYTH2, FACT2)
    um = ease_out(seg(t, _st(m), _st(m) + 0.4))
    _panel(ctx, TOP[0], TOP[1], RED, "MYTH", um)
    stamp = ease_back(seg(t, _end(m) + 0.05, _end(m) + 0.35))
    dim = um * (1 - 0.45 * stamp)
    claim = ("YOU HAVE TO", "TYPE A PROMPT") if first else ("IT MIXES LANGUAGES", "LIKE HINGLISH")
    for j, ln in enumerate(claim):
        text(ctx, ln, W / 2, TOP[0] + 110 + j * 70, 58, WHITE, alpha=dim)
    lm = t - LINES[m]["start"]
    if first:
        _promptbox(ctx, 420, TOP[0] + 330, 600, t, dim, ease_out(seg(lm, 0.1, 1.6)))
    else:
        _plate(ctx, 250, TOP[0] + 320, "HINDI", K_, Y_, um, 54)
        text(ctx, "+", 420, TOP[0] + 340, 80, WHITE, alpha=dim)
        _plate(ctx, 640, TOP[0] + 320, "ENGLISH", K_, WHITE, um, 54)
    _xstamp(ctx, W - 190, TOP[0] + 300, 80, stamp)
    if i == m:
        return
    uf = ease_out(seg(t, _st(f), _st(f) + 0.4))
    _panel(ctx, BOT[0], BOT[1], TEAL, "FACT", uf)
    _check(ctx, W - 160, BOT[0] + 4, 46, ease_back(seg(t, _st(f) + 0.2, _st(f) + 0.6)))
    if i == FACT1:
        lt = t - LINES[FACT1]["start"]
        text(ctx, "NO PROMPT NEEDED", W / 2, BOT[0] + 100, 62, Y_, alpha=ease_out(seg(lt, 0.2, 0.6)))
        kinds = (("mail", "MAIL"), ("cal", "CALENDAR"), ("photo", "PHOTOS"))
        bx, by = 790, BOT[0] + 285
        for j, (kd, lb) in enumerate(kinds):
            u = ease_back(seg(lt, 2.0 + j * 0.9, 2.4 + j * 0.9))
            ax, ay = 200, BOT[0] + 175 + j * 92
            _app(ctx, kd, ax, ay, 0.55 * u, uf)
            text(ctx, lb, ax + 60, ay + 13, 34, WHITE, align="left", alpha=uf * min(1, u))
            fl = seg(lt, 2.6 + j * 0.9, 3.4 + j * 0.9)
            if 0 < fl < 1:
                _sparkle(ctx, lerp(ax + 240, bx - 150, ease_io(fl)), lerp(ay, by, ease_io(fl)), 20, uf)
        _book(ctx, bx, by, 0.55 * ease_back(seg(lt, 0.8, 1.2)), t, uf, ease_io(seg(lt, 1.2, 2.0)),
              scene=int(max(0, lt - 2.5) / 1.5) % 3)
    elif i == VEO:
        lt = t - LINES[VEO]["start"]
        k = ease_out(seg(lt, -0.2, 0.3))
        text(ctx, "SOME STORIES MOVE", W / 2, BOT[0] + 100, 58, Y_, alpha=k)
        fx, fy, fw, fh = 230, BOT[0] + 150, 620, 250
        rrect(ctx, fx - 20, fy - 20, fw + 40, fh + 40, 22)
        src(ctx, K_, k)
        ctx.fill()
        for q in range(9):
            for yy in (fy - 14, fy + fh + 2):
                rrect(ctx, fx + 10 + q * 68, yy, 34, 12, 4)
                src(ctx, GREY, k)
                ctx.fill()
        _picture(ctx, fx, fy, fw, fh, t, k, scene=int(lt * 1.5) % 3)
        bx = fx + (lt * 160) % fw
        ellipse(ctx, bx, fy + fh * 0.35 + 18 * math.sin(lt * 8), 14, 9)
        src(ctx, K_, k)
        ctx.fill()
        _plate(ctx, W / 2, BOT[0] + 455 - 20, "ANIMATED WITH VEO", K_, Y_, ease_back(seg(lt, 1.6, 2.0)), 40)
    elif i == FACT2:
        lt = t - LINES[FACT2]["start"]
        n = int(14 * ease_out(seg(lt, 0.3, 1.5)))
        text(ctx, "%d" % n, 250, BOT[0] + 220, 150, Y_, alpha=uf)
        text(ctx, "LANGUAGES", 250, BOT[0] + 285, 42, WHITE, alpha=uf)
        langs = ("ENGLISH", "HINDI", "TAMIL", "BENGALI")
        for j, lg in enumerate(langs):
            u = ease_back(seg(lt, 1.2 + j * 0.6, 1.6 + j * 0.6))
            _plate(ctx, 700 + (j % 2) * 0 - 0, BOT[0] + 140 + j * 70, lg, K_, Y_ if j == 0 else WHITE, u * uf, 40)
        text(ctx, "+ 10 MORE", 700, BOT[0] + 430, 34, GREY, alpha=uf * ease_out(seg(lt, 3.6, 4.0)))
        u = ease_back(seg(lt, 5.0, 5.4))
        if u > 0.01:
            _plate(ctx, 250, BOT[0] + 400, "ONE AT A TIME", WHITE, RED, u, 40)
    else:  # DETAILS
        lt = t - LINES[DETAILS]["start"]
        k = ease_out(seg(lt, -0.2, 0.3))
        _plate(ctx, 290, BOT[0] + 140, "FREE", K_, Y_, ease_back(seg(lt, 0.1, 0.5)), 60)
        _plate(ctx, 720, BOT[0] + 140, "ANDROID + iOS", WHITE, K_, ease_back(seg(lt, 0.7, 1.1)), 48)
        _plate(ctx, W / 2, BOT[0] + 235, "18+ ONLY", WHITE, ORANGE, ease_back(seg(lt, 1.8, 2.2)), 46)
        u = ease_back(seg(lt, 3.0, 3.4))
        if u > 0.01:
            _lock(ctx, 330, BOT[0] + 340, 0.6 * u, uf)
            text(ctx, "PRIVATE", 330, BOT[0] + 420, 34, WHITE, alpha=uf * min(1, u))
        u = ease_back(seg(lt, 4.3, 4.7))
        if u > 0.01:
            _bin(ctx, 750, BOT[0] + 335, 0.55 * u, uf)
            text(ctx, "DELETE ANYTIME", 750, BOT[0] + 420, 34, WHITE, alpha=uf * min(1, u))


def _outro(ctx, t):
    t0 = _st(OUTRO)
    lt = t - LINES[OUTRO]["start"]
    _headline(ctx, t0, t, "IT CAN GET THINGS WRONG", size=90)
    text(ctx, "GOOGLE'S OWN WARNING", W / 2, 650, 44, WHITE, alpha=ease_out(seg(t, t0 + 0.3, t0 + 0.7)))
    k = ease_out(seg(t, t0, t0 + 0.4))
    _book(ctx, W / 2, 1000, 0.95 * k, t, k, 1.0, scene=2)
    q = ease_back(seg(lt, 0.6, 1.0))
    if q > 0.01:
        ctx.save()
        ctx.translate(W / 2 + 320, 820)
        ctx.scale(q, q)
        ellipse(ctx, 0, 0, 70, 70)
        src(ctx, RED)
        ctx.fill()
        text(ctx, "?", 0, 34, 100, WHITE)
        ctx.restore()
    u = ease_back(seg(lt, 2.2, 2.6))
    if u > 0.01:
        _plate(ctx, W / 2, 1330, "WOULD YOU LET AI WRITE YOUR DAY?", K_, Y_, u, 42)


def _wipe(ctx, t):
    for i in (MYTH1, MYTH2, OUTRO):
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
    if i is None and t < END + 0.3:
        _outro(ctx, t)
    if i is not None:
        if i <= TWO:
            _intro(ctx, i, t)
        elif i <= DETAILS:
            _mythfact(ctx, i, t)
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
