"""2026-10-16 newsflash: Amazon Bee Frontier and Bee Eclipse AI recorders (contract: DURATION + render_frame)."""
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
    ("IT REMEMBERS", "A GADGET THAT LISTENS TO YOUR DAY"),
    ("TWO DEVICES", "BEE FRONTIER + BEE ECLIPSE"),
    ("$74.99", "BEE FRONTIER · WEARABLE"),
    ("$99.99", "BEE ECLIPSE · PHONE ATTACHMENT"),
    ("AI MEMORY", "CONVERSATIONS IN, NOTES OUT"),
    ("PRIVACY?", "WHAT AMAZON SAYS"),
    ("14 DAYS", "FREE PLAN MEMORY"),
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
    text(ctx, "BREAKING · AI GADGETS", -W / 2 + 90 + (1 - u) * -300, 20, 56, K_, align="left", alpha=u)
    ctx.restore()


# ------------------------------------------------------------------ icons
GREY2 = (0.85, 0.87, 0.90)


def _band(ctx, x, y, s, t, a=1.0):
    """Generic wrist band with a round pod (no brand marks)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for sgn in (-1, 1):
        rrect(ctx, -70, sgn * 60 - (130 if sgn < 0 else 0) , 140, 130, 30)
        src(ctx, (0.30, 0.32, 0.36), a)
        ctx.fill()
    for r, al in ((150, 0.10), (125, 0.16)):
        ellipse(ctx, 0, 0, r, r)
        src(ctx, Y_, al * a * (0.7 + 0.3 * math.sin(t * 3)))
        ctx.fill()
    ellipse(ctx, 0, 0, 100, 100)
    src(ctx, (0.14, 0.15, 0.18), a)
    ctx.fill_preserve()
    src(ctx, GREY2, a)
    ctx.set_line_width(8)
    ctx.stroke()
    ellipse(ctx, 0, -55, 9, 9)
    src(ctx, (0.3, 0.9, 0.4) if (t * 1.5) % 1 < 0.6 else (0.2, 0.4, 0.25), a)
    ctx.fill()
    _wave(ctx, 0, 15, 120, 50, t, Y_, a)
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


def _bubble(ctx, x, y, w, h, col, a=1.0, tail=1):
    rrect(ctx, x - w / 2, y - h / 2, w, h, 34)
    ctx.move_to(x + tail * w * 0.25, y + h / 2 - 2)
    ctx.line_to(x + tail * w * 0.35, y + h / 2 + 40)
    ctx.line_to(x + tail * w * 0.10, y + h / 2 - 2)
    src(ctx, col, a)
    ctx.fill()


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


def _wave(ctx, x, y, w, h, t, col, a=1.0, n=9):
    for j in range(n):
        bx = x - w / 2 + j * w / (n - 1)
        bh = h * (0.25 + 0.75 * abs(math.sin(t * 6 + j * 0.9)))
        rrect(ctx, bx - 5, y - bh / 2, 10, bh, 5)
        src(ctx, col, a)
        ctx.fill()


def _phone(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -150, -300, 300, 600, 44)
    src(ctx, (0.20, 0.21, 0.25), a)
    ctx.fill_preserve()
    src(ctx, (0.65, 0.67, 0.72), a)
    ctx.set_line_width(6)
    ctx.stroke()
    ellipse(ctx, -85, -230, 26, 26)
    src(ctx, (0.08, 0.08, 0.1), a)
    ctx.fill()
    ctx.restore()


def _card(ctx, x, y, s, t, a=1.0):
    """Credit-card-sized recorder."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -120, -175, 240, 350, 26)
    g = cairo.LinearGradient(0, -175, 0, 175)
    g.add_color_stop_rgb(0, 0.96, 0.80, 0.20)
    g.add_color_stop_rgb(1, 0.86, 0.62, 0.05)
    ctx.set_source(g)
    ctx.fill()
    _wave(ctx, 0, 0, 140, 70, t, K_, a)
    ellipse(ctx, 0, -120, 9, 9)
    src(ctx, (0.85, 0.1, 0.1) if (t * 1.5) % 1 < 0.6 else (0.4, 0.1, 0.1), a)
    ctx.fill()
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


def _person(ctx, x, y, s, col, a=1.0):
    ellipse(ctx, x, y - 50 * s, 34 * s, 34 * s)
    src(ctx, col, a)
    ctx.fill()
    ellipse(ctx, x, y + 40 * s, 52 * s, 46 * s)
    ctx.fill()


def _lock(ctx, x, y, s, u):
    if u <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * u, s * u)
    ctx.arc(0, -40, 60, math.pi, 0)
    src(ctx, GREY2)
    ctx.set_line_width(22)
    ctx.stroke()
    rrect(ctx, -95, -40, 190, 150, 22)
    src(ctx, Y_)
    ctx.fill()
    ellipse(ctx, 0, 25, 18, 18)
    src(ctx, K_)
    ctx.fill()
    ctx.restore()


def _bin(ctx, x, y, s, u):
    if u <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * u, s * u)
    rrect(ctx, -110, -110, 220, 24, 10)
    src(ctx, GREY2)
    ctx.fill()
    rrect(ctx, -30, -135, 60, 30, 10)
    ctx.fill()
    ctx.move_to(-90, -80)
    ctx.line_to(90, -80)
    ctx.line_to(70, 120)
    ctx.line_to(-70, 120)
    ctx.close_path()
    ctx.fill()
    for dx in (-40, 0, 40):
        ctx.move_to(dx, -50)
        ctx.line_to(dx * 0.8, 90)
    src(ctx, (0.4, 0.42, 0.46))
    ctx.set_line_width(10)
    ctx.stroke()
    ctx.restore()


def _icon(ctx, i, t, k):
    t0 = _card_start(i)
    lt = t - t0
    if i == 0:   # band listening -> memory
        _band(ctx, W / 2, ICON_Y - 60, 1.3 * k, t, k)
        for j in range(3):
            r = 180 + ((t * 120 + j * 90) % 270)
            ctx.arc(W / 2, ICON_Y - 60, r, -0.6, 0.6)
            src(ctx, Y_, max(0, 0.6 - (r - 180) / 450) * k)
            ctx.set_line_width(10)
            ctx.stroke()
            ctx.arc(W / 2, ICON_Y - 60, r, math.pi - 0.6, math.pi + 0.6)
            ctx.stroke()
        u2 = ease_out(seg(lt, 1.6, 2.1))
        if u2 > 0.01:
            text(ctx, "LISTENS · REMEMBERS", W / 2, ICON_Y + 300, 60, Y_, alpha=u2)
    elif i == 1:   # two devices + date
        _calendar(ctx, W / 2, ICON_Y - 230, 0.8, "OCT", "15", ease_back(seg(lt, 0.1, 0.5)))
        u = ease_back(seg(lt, 2.2, 2.6))
        if u > 0.01:
            _band(ctx, W / 2 - 220, ICON_Y + 70, 0.85 * u, t, 1)
            text(ctx, "FRONTIER", W / 2 - 220, ICON_Y + 290, 50, (1, 1, 1), alpha=u)
        u2 = ease_back(seg(lt, 3.6, 4.0))
        if u2 > 0.01:
            _card(ctx, W / 2 + 220, ICON_Y + 70, 0.7 * u2, t, 1)
            text(ctx, "ECLIPSE", W / 2 + 220, ICON_Y + 290, 50, (1, 1, 1), alpha=u2)
    elif i == 2:   # Frontier specs
        _band(ctx, W / 2, ICON_Y - 120, 0.9 * k, t, k)
        items = (("WRIST OR CLIP-ON", 1.6), ("WATER RESISTANT", 3.4), ("UP TO 7 DAYS", 5.0))
        for j, (s_, st) in enumerate(items):
            _pill(ctx, W / 2, ICON_Y + 120 + j * 115, s_, ease_back(seg(lt, st, st + 0.4)),
                  col=Y_ if j == 2 else (1, 1, 1), size=46, w=640)
    elif i == 3:   # Eclipse snaps onto phone
        _phone(ctx, W / 2 - 150, ICON_Y - 70, 0.8 * k, k)
        u = ease_back(seg(lt, 1.2, 1.7))
        cx = lerp(W / 2 + 330, W / 2 + 40, ease_out(seg(lt, 1.2, 1.9)))
        if u > 0.01:
            _card(ctx, cx, ICON_Y - 70, 0.75, t, 1)
        u2 = ease_back(seg(lt, 1.9, 2.2))
        if u2 > 0.01:
            text(ctx, "SNAP!", W / 2 + 330, ICON_Y - 250, 60, Y_, alpha=u2)
        _pill(ctx, W / 2, ICON_Y + 240, "21+ DAYS BATTERY", ease_back(seg(lt, 3.6, 4.0)), col=Y_, w=640)
        _pill(ctx, W / 2, ICON_Y + 355, "COMING SOON", ease_back(seg(lt, 5.9, 6.3)), col=(1, 1, 1), w=640)
    elif i == 4:   # conversations -> notes
        bubbles = ((W / 2 - 230, ICON_Y - 260, TEAL, -1), (W / 2 - 170, ICON_Y - 120, ORANGE, 1))
        for j, (bx, by, col, tl) in enumerate(bubbles):
            ub = ease_back(seg(lt, 0.1 + j * 0.3, 0.5 + j * 0.3))
            if ub > 0.01:
                ctx.save()
                ctx.translate(bx, by)
                ctx.scale(ub, ub)
                _bubble(ctx, 0, 0, 300, 100, col, 1, tl)
                _wave(ctx, 0, 0, 160, 44, t + j, (1, 1, 1), 1)
                ctx.restore()
        u = ease_io(seg(lt, 1.0, 1.6))
        if u > 0.01:
            ctx.move_to(W / 2 + 20, ICON_Y - 190)
            ctx.line_to(W / 2 + 20 + 100 * u, ICON_Y - 190)
            src(ctx, Y_)
            ctx.set_line_width(14)
            ctx.stroke()
        rrect(ctx, W / 2 + 150, ICON_Y - 330, 300, 280, 22)
        src(ctx, (0.95, 0.95, 0.92), ease_out(seg(lt, 1.4, 1.8)))
        ctx.fill()
        for r in range(4):
            rrect(ctx, W / 2 + 185, ICON_Y - 290 + r * 60, 230 * ease_out(seg(lt, 1.6 + r * 0.1, 2.0 + r * 0.1)), 18, 9)
            src(ctx, (0.6, 0.6, 0.62))
            ctx.fill()
        items = (("SUMMARIES", 2.4), ("TO-DOS", 3.0), ("REMINDERS", 3.6))
        for j, (s_, st) in enumerate(items):
            u2 = ease_back(seg(lt, st, st + 0.4))
            if u2 > 0.01:
                y = ICON_Y + 70 + j * 120
                _check(ctx, 300, y - 14, u2)
                text(ctx, s_, 370, y + 6, 56, (1, 1, 1), align="left", alpha=u2)
    elif i == 5:   # privacy claims
        _wave(ctx, W / 2 - 230, ICON_Y - 190, 220, 120, t, TEAL, k)
        text(ctx, "AUDIO", W / 2 - 230, ICON_Y - 60, 46, (1, 1, 1), alpha=k)
        _bin(ctx, W / 2 + 230, ICON_Y - 170, 0.8, ease_back(seg(lt, 1.6, 2.0)))
        text(ctx, "DELETED", W / 2 + 230, ICON_Y - 30, 46, Y_, alpha=ease_out(seg(lt, 1.8, 2.2)))
        _lock(ctx, W / 2 - 280, ICON_Y + 190, 0.9, ease_back(seg(lt, 3.0, 3.4)))
        u3 = ease_out(seg(lt, 3.3, 3.8))
        if u3 > 0.01:
            text(ctx, "ENCRYPTED", W / 2 + 140, ICON_Y + 170, 54, (1, 1, 1), alpha=u3)
            text(ctx, "KEYS ON YOUR DEVICE", W / 2 + 140, ICON_Y + 235, 38, TEAL, alpha=u3)
        u4 = ease_out(seg(lt, 4.0, 4.5))
        if u4 > 0.01:
            text(ctx, "(AMAZON'S CLAIM)", W / 2, ICON_Y + 345, 40, GREY, alpha=u4)
    elif i == 6:   # free 14 days vs Pro
        _calendar(ctx, W / 2, ICON_Y - 160, 1.2, "FREE", "14", ease_back(seg(lt, 0.2, 0.6)))
        text(ctx, "DAYS OF MEMORY", W / 2, ICON_Y + 30, 50, (1, 1, 1), alpha=ease_out(seg(lt, 0.6, 1.0)))
        u2 = ease_back(seg(lt, 2.2, 2.6))
        if u2 > 0.01:
            ctx.save()
            ctx.translate(W / 2, ICON_Y + 210)
            ctx.scale(u2, u2)
            rrect(ctx, -330, -95, 660, 190, 30)
            src(ctx, Y_)
            ctx.fill()
            text(ctx, "BEE PRO", 0, -12, 64, K_)
            text(ctx, "$11.99 / MONTH", 0, 60, 50, K_)
            ctx.restore()
    elif i == 7:   # why it matters
        _band(ctx, W / 2, ICON_Y - 210, 0.7 * k, t, k)
        for j, dx in enumerate((-330, -200, 200, 330)):
            u2 = ease_back(seg(lt, 3.6 + j * 0.12, 4.0 + j * 0.12))
            if u2 > 0.01:
                _person(ctx, W / 2 + dx, ICON_Y - 190, 0.9 * u2, GREY2)
                text(ctx, "?", W / 2 + dx, ICON_Y - 290, 60, ORANGE, alpha=u2)
        for j, (s_, st) in enumerate((("AI MEMORY IS HERE", 1.2), ("BUT WHO ELSE IS RECORDED?", 3.8))):
            u2 = ease_back(seg(lt, st, st + 0.4))
            if u2 > 0.01:
                y = ICON_Y + 90 + j * 140
                _check(ctx, 150, y - 18, u2) if j == 0 else _xq(ctx, 150, y - 18, u2)
                text(ctx, s_, 210, y, 46, (1, 1, 1), align="left", alpha=u2)


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
