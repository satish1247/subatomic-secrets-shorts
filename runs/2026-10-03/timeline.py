"""2026-10-03 newsflash: Apple Pay launches in India (contract: DURATION + render_frame)."""
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
    ("APPLE PAY", "NOW LIVE IN INDIA"),
    ("1 BANK", "AXIS BANK IS FIRST"),
    ("CARDS ONLY", "AXIS VISA & MASTERCARD CREDIT CARDS"),
    ("NO UPI", "AND NO RUPAY AT LAUNCH"),
    ("FEE FIGHT", "HDFC · ICICI · SBI CARD NOT IN YET"),
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
    text(ctx, "BREAKING · TECH INDIA", -W / 2 + 90 + (1 - u) * -300, 20, 56, K_, align="left", alpha=u)
    ctx.restore()


# ------------------------------------------------------------------ icons
def _phone(ctx, x, y, s, a=1.0, screen=None):
    """Generic smartphone (no brand marks)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -110, -220, 220, 440, 36)
    src(ctx, (0.16, 0.16, 0.19), a)
    ctx.fill_preserve()
    src(ctx, (0.75, 0.77, 0.8), a)
    ctx.set_line_width(6)
    ctx.stroke()
    rrect(ctx, -95, -200, 190, 400, 24)
    g = cairo.LinearGradient(0, -200, 0, 200)
    g.add_color_stop_rgb(0, 0.12, 0.30, 0.45)
    g.add_color_stop_rgb(1, 0.05, 0.10, 0.18)
    ctx.set_source(g)
    ctx.fill()
    rrect(ctx, -30, -192, 60, 14, 7)
    src(ctx, (0, 0, 0), a)
    ctx.fill()
    if screen:
        screen(ctx)
    ctx.restore()


def _card(ctx, x, y, s, label="CREDIT", col=None, ang=0.0, a=1.0):
    """Generic bank card with text label only."""
    col = col or TEAL
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(s, s)
    rrect(ctx, -170, -105, 340, 210, 22)
    g = cairo.LinearGradient(-170, -105, 170, 105)
    g.add_color_stop_rgb(0, *col)
    g.add_color_stop_rgb(1, *[c * 0.55 for c in col])
    ctx.set_source(g)
    ctx.fill_preserve()
    src(ctx, (1, 1, 1), 0.5 * a)
    ctx.set_line_width(3)
    ctx.stroke()
    rrect(ctx, -135, -55, 60, 44, 8)
    src(ctx, Y_, a)
    ctx.fill()
    for j in range(4):
        rrect(ctx, -135 + j * 68, 25, 52, 16, 6)
        src(ctx, (1, 1, 1), 0.7 * a)
        ctx.fill()
    text(ctx, label, 150, 85, 30, (1, 1, 1), align="right", alpha=a)
    ctx.restore()


def _waves(ctx, x, y, t, a=1.0, n=3):
    """Contactless 'tap' arcs."""
    for j in range(n):
        u = (t * 1.2 + j / n) % 1
        ctx.arc(x, y, 40 + 110 * u, -0.6, 0.6)
        src(ctx, Y_, a * (1 - u))
        ctx.set_line_width(10)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()


def _bank(ctx, x, y, s, label, col=Y_, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-150, -90)
    ctx.line_to(0, -170)
    ctx.line_to(150, -90)
    ctx.close_path()
    src(ctx, col, a)
    ctx.fill()
    for j in range(4):
        ctx.rectangle(-120 + j * 70, -75, 30, 150)
    ctx.rectangle(-160, 85, 320, 30)
    ctx.fill()
    ctx.restore()
    text(ctx, label, x, y + 190 * s, 44 * min(1.0, s + 0.2), col, alpha=a)


def _xmark(ctx, x, y, r, u, w=22):
    if u <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(u, u)
    for sgn in (-1, 1):
        ctx.move_to(-r, -r * sgn)
        ctx.line_to(r, r * sgn)
    src(ctx, RED)
    ctx.set_line_width(w)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    ctx.restore()


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


def _terminal(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -90, -150, 180, 300, 26)
    src(ctx, (0.85, 0.86, 0.88), a)
    ctx.fill()
    rrect(ctx, -65, -125, 130, 80, 10)
    src(ctx, (0.1, 0.35, 0.3), a)
    ctx.fill()
    for r in range(3):
        for c in range(3):
            ellipse(ctx, -45 + c * 45, -10 + r * 45, 15, 15)
            src(ctx, (0.35, 0.36, 0.4), a)
            ctx.fill()
    ctx.restore()


def _icon(ctx, i, t, k):
    t0 = _card_start(i)
    lt = t - t0
    if i == 0:   # phone tapping a card terminal
        ph_x = lerp(W / 2 - 60, W / 2 - 160, ease_io(seg(lt, 0.3, 1.2)))
        _terminal(ctx, W / 2 + 230, ICON_Y + 40, 1.0 * k)
        _phone(ctx, ph_x, ICON_Y + 20, 0.95 * k, k)
        _waves(ctx, ph_x + 120, ICON_Y + 20, t, k)
        u = ease_back(seg(lt, 1.4, 1.8))
        if u > 0.01:
            text(ctx, "TAP TO PAY", W / 2, ICON_Y + 330, 60, (1, 1, 1), alpha=u)
    elif i == 1:   # one bank
        _bank(ctx, W / 2, ICON_Y - 20, 1.1 * k, "AXIS BANK", Y_, k)
        u = ease_back(seg(lt, 0.8, 1.2))
        if u > 0.01:
            ellipse(ctx, W / 2 + 230, ICON_Y - 180, 70 * u, 70 * u)
            src(ctx, TEAL)
            ctx.fill()
            text(ctx, "1", W / 2 + 230, ICON_Y - 152, 84 * u, (1, 1, 1))
    elif i == 2:   # credit cards + phone + watch
        for j, lab in enumerate(("VISA", "MASTERCARD")):
            u = ease_back(seg(lt, 0.2 + j * 0.4, 0.6 + j * 0.4))
            if u > 0.01:
                _card(ctx, W / 2 - 170 + j * 40, ICON_Y - 170 + j * 130, 1.0 * u, lab,
                      TEAL if j == 0 else ORANGE, -0.08 + j * 0.06)
        u = ease_out(seg(lt, 2.4, 3.0))
        if u > 0.01:
            _phone(ctx, W / 2 + 260, ICON_Y + 30, 0.7 * u, u)
            # simple watch
            ctx.save()
            ctx.translate(W / 2 + 260, ICON_Y + 300)
            ctx.scale(u, u)
            rrect(ctx, -26, -110, 52, 220, 14)
            src(ctx, (0.3, 0.3, 0.34))
            ctx.fill()
            rrect(ctx, -60, -70, 120, 140, 30)
            src(ctx, (0.16, 0.16, 0.19))
            ctx.fill_preserve()
            src(ctx, (0.75, 0.77, 0.8))
            ctx.set_line_width(5)
            ctx.stroke()
            ctx.restore()
        u2 = ease_out(seg(lt, 4.2, 4.8))
        if u2 > 0.01:
            text(ctx, "+ ONLINE", W / 2 - 150, ICON_Y + 300, 60, Y_, alpha=u2)
    elif i == 3:   # UPI and RuPay crossed out; UPI is the giant
        r = 210 * k
        ellipse(ctx, W / 2 - 140, ICON_Y + 10, r, r)
        src(ctx, (0.20, 0.55, 0.30), 0.9)
        ctx.fill()
        text(ctx, "UPI", W / 2 - 140, ICON_Y + 40, 110 * k, (1, 1, 1))
        _card(ctx, W / 2 + 260, ICON_Y - 120, 0.75 * k, "RUPAY", GREY, 0.1)
        _xmark(ctx, W / 2 - 140, ICON_Y + 10, 130, ease_back(seg(lt, 0.6, 1.0)), 28)
        _xmark(ctx, W / 2 + 260, ICON_Y - 120, 90, ease_back(seg(lt, 1.6, 2.0)))
        text(ctx, "RUPAY", W / 2 + 260, ICON_Y + 60, 48, GREY, alpha=k)
        u = ease_out(seg(lt, 3.2, 3.8))
        if u > 0.01:
            text(ctx, "MOST OF INDIA'S", W / 2, ICON_Y + 300, 52, (1, 1, 1), alpha=u)
            text(ctx, "DIGITAL PAYMENTS", W / 2, ICON_Y + 365, 52, Y_, alpha=u)
    elif i == 4:   # three banks waiting + fee scale
        for j, lab in enumerate(("HDFC", "ICICI", "SBI CARD")):
            u = ease_out(seg(lt, 0.2 + j * 0.35, 0.6 + j * 0.35))
            if u > 0.01:
                _bank(ctx, 220 + j * 320, ICON_Y - 140, 0.6, lab, GREY, u)
        u = ease_out(seg(lt, 3.5, 4.3))
        if u > 0.01:
            for j, (lab, val, frac, col) in enumerate((("APPLE WANTS", "~0.2%", 1.0, Y_),
                                                       ("BANKS OFFERED", "LESS", 0.72, GREY))):
                y = ICON_Y + 120 + j * 150
                text(ctx, lab, 90, y + 50, 36, (1, 1, 1), align="left", alpha=u)
                rrect(ctx, 480, y, 360, 70, 18)
                src(ctx, (1, 1, 1), 0.12 * u)
                ctx.fill()
                rrect(ctx, 480, y, max(30, 360 * frac * ease_out(seg(lt, 3.8 + j * 0.5, 4.8 + j * 0.5))), 70, 18)
                src(ctx, col, u)
                ctx.fill()
                text(ctx, val, 860, y + 50, 40, col, align="left", alpha=u)
    elif i == 5:   # tap to pay yes, UPI no
        _phone(ctx, W / 2 - 320, ICON_Y + 20, 0.85 * k, k)
        for j, s_ in enumerate(("TAP TO PAY", "CARDS ONLY", "NO UPI")):
            u = ease_back(seg(lt, 0.8 + j * 1.6, 1.2 + j * 1.6))
            if u > 0.01:
                y = ICON_Y - 140 + j * 150
                if j == 2:
                    _xmark(ctx, W / 2 - 75, y - 18, 26, u, 12)
                else:
                    _check(ctx, W / 2 - 75, y - 18, u)
                text(ctx, s_, W / 2 - 15, y, 54, (1, 1, 1), align="left", alpha=u)


def _headline(ctx, i, t):
    t0 = _card_start(i)
    k = ease_back(seg(t, t0, t0 + 0.35))
    head, sub = CARDS[i]
    size = 128 if len(head) <= 11 else 104
    ctx.save()
    ctx.translate(W / 2, 560)
    ctx.scale(k, k)
    text(ctx, head, 0, 0, size, Y_)
    ctx.restore()
    if sub:
        text(ctx, sub, W / 2, 650, 38, (1, 1, 1), alpha=ease_out(seg(t, t0 + 0.3, t0 + 0.7)))
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
