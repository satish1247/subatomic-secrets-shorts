"""2026-10-12 newsflash: Anthropic bars needless cruelty toward Claude (contract: DURATION + render_frame)."""
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
    ("BE NICE?", "NEW RULES FOR HOW YOU TREAT AN AI"),
    ("NOV 12", "CLAUDE USAGE POLICY UPDATE TAKES EFFECT"),
    ("NO CRUELTY", "SUSTAINED + NEEDLESS ABUSE IS BARRED"),
    ("STILL OK", "WHAT THE RULE DOES NOT COVER"),
    ("CHAT ENDED", "THE MAIN PENALTY"),
    ("SINCE 2025", "NOT A BRAND-NEW POWER"),
    ("ALL USERS", "EVEN THE FREE PLAN"),
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
    text(ctx, "BREAKING · AI RULES", -W / 2 + 90 + (1 - u) * -300, 20, 56, K_, align="left", alpha=u)
    ctx.restore()


# ------------------------------------------------------------------ icons
GREEN = (0.46, 0.73, 0.0)


def _laptop(ctx, x, y, s, a=1.0, screen=None):
    """Generic laptop (no brand marks): screen centred at (x, y)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -300, -200, 600, 380, 26)
    src(ctx, (0.17, 0.17, 0.2), a)
    ctx.fill_preserve()
    src(ctx, (0.72, 0.74, 0.78), a)
    ctx.set_line_width(6)
    ctx.stroke()
    rrect(ctx, -275, -178, 550, 336, 14)
    g = cairo.LinearGradient(0, -178, 0, 158)
    g.add_color_stop_rgb(0, 0.10, 0.18, 0.30)
    g.add_color_stop_rgb(1, 0.03, 0.05, 0.10)
    ctx.set_source(g)
    ctx.fill()
    ctx.move_to(-360, 190)
    ctx.line_to(360, 190)
    ctx.line_to(320, 230)
    ctx.line_to(-320, 230)
    ctx.close_path()
    src(ctx, (0.62, 0.64, 0.68), a)
    ctx.fill()
    rrect(ctx, -60, 190, 120, 12, 6)
    src(ctx, (0.4, 0.42, 0.46), a)
    ctx.fill()
    if screen:
        screen(ctx)
    ctx.restore()


def _chip(ctx, x, y, s, t, a=1.0, label="RTX SPARK"):
    """Generic glowing superchip with pins."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    glow = 0.5 + 0.5 * math.sin(t * 4)
    for r, al in ((210, 0.10), (180, 0.16)):
        rrect(ctx, -r, -r, 2 * r, 2 * r, 40)
        src(ctx, GREEN, al * a * (0.6 + 0.4 * glow))
        ctx.fill()
    for j in range(7):
        for side in range(4):
            ctx.save()
            ctx.rotate(side * math.pi / 2)
            rrect(ctx, -105 + j * 32, -175, 14, 35, 4)
            src(ctx, (0.8, 0.8, 0.82), a)
            ctx.fill()
            ctx.restore()
    rrect(ctx, -140, -140, 280, 280, 22)
    src(ctx, (0.13, 0.14, 0.16), a)
    ctx.fill_preserve()
    src(ctx, GREEN, a)
    ctx.set_line_width(6)
    ctx.stroke()
    rrect(ctx, -100, -100, 200, 200, 14)
    src(ctx, (0.2, 0.22, 0.25), a)
    ctx.fill()
    text(ctx, label, 0, 14, 38, GREEN, alpha=a)
    ctx.restore()


def _cores(ctx, x, y, cols, rows, cell, gap, col, frac, a=1.0):
    n = cols * rows
    lit = int(n * frac)
    w = cols * (cell + gap) - gap
    h = rows * (cell + gap) - gap
    for j in range(n):
        cx = x - w / 2 + (j % cols) * (cell + gap)
        cy = y - h / 2 + (j // cols) * (cell + gap)
        rrect(ctx, cx, cy, cell, cell, max(2, cell * 0.2))
        src(ctx, col if j < lit else (0.25, 0.26, 0.3), a)
        ctx.fill()


def _cloud(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for cx, cy, r in ((-70, 10, 60), (0, -30, 85), (75, 10, 60)):
        ellipse(ctx, cx, cy, r, r)
        src(ctx, (0.85, 0.88, 0.92), a)
        ctx.fill()
    rrect(ctx, -130, 0, 260, 70, 35)
    ctx.fill()
    ctx.restore()


def _net(ctx, x, y, s, t, a=1.0):
    """Tiny neural network diagram (the 'AI model')."""
    layers = (3, 5, 5, 2)
    pts = []
    for li, n in enumerate(layers):
        pts.append([(x + (li - 1.5) * 110 * s, y + (k_ - (n - 1) / 2) * 60 * s) for k_ in range(n)])
    for li in range(len(layers) - 1):
        for p in pts[li]:
            for q in pts[li + 1]:
                ctx.move_to(*p)
                ctx.line_to(*q)
    src(ctx, (1, 1, 1), 0.25 * a)
    ctx.set_line_width(2)
    ctx.stroke()
    for li, col in enumerate(pts):
        for k_, (px, py) in enumerate(col):
            pulse = 0.5 + 0.5 * math.sin(t * 5 - li * 1.2 + k_)
            ellipse(ctx, px, py, 14 * s, 14 * s)
            src(ctx, Y_ if pulse > 0.6 else TEAL, a)
            ctx.fill()


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


def _robot(ctx, x, y, s, t, a=1.0, mood="neutral"):
    """Generic friendly AI robot head (no brand marks)."""
    ctx.save()
    ctx.translate(x, y + 6 * math.sin(t * 2.2))
    ctx.scale(s, s)
    ctx.move_to(0, -170)
    ctx.line_to(0, -215)
    src(ctx, (0.8, 0.8, 0.84), a)
    ctx.set_line_width(10)
    ctx.stroke()
    ellipse(ctx, 0, -225, 20, 20)
    src(ctx, Y_, a)
    ctx.fill()
    rrect(ctx, -190, -170, 380, 300, 70)
    src(ctx, (0.88, 0.89, 0.92), a)
    ctx.fill()
    rrect(ctx, -150, -130, 300, 210, 50)
    src(ctx, (0.10, 0.12, 0.16), a)
    ctx.fill()
    blink = 0.15 if (t * 0.7) % 3 < 0.12 else 1.0
    for ex in (-60, 60):
        ellipse(ctx, ex, -50, 26, 26 * blink)
        src(ctx, TEAL if mood != "sad" else (0.5, 0.7, 1.0), a)
        ctx.fill()
    if mood == "sad":
        ctx.arc_negative(0, 50, 50, -0.3, -math.pi + 0.3)
    else:
        ctx.arc(0, 0, 50, 0.4, math.pi - 0.4)
    src(ctx, TEAL, a)
    ctx.set_line_width(10)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    if mood == "sad":
        ellipse(ctx, 75, -10 + (t * 40) % 50, 9, 14)
        src(ctx, (0.5, 0.7, 1.0), a)
        ctx.fill()
    ctx.restore()


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


def _icon(ctx, i, t, k):
    t0 = _card_start(i)
    lt = t - t0
    if i == 0:   # angry user bubble -> sad robot
        _robot(ctx, W / 2 + 170, ICON_Y - 40, 0.9 * k, t, k, "sad")
        u = ease_back(seg(lt, 0.2, 0.6))
        if u > 0.01:
            ctx.save()
            ctx.translate(W / 2 - 230, ICON_Y - 220)
            ctx.scale(u, u)
            _bubble(ctx, 0, 0, 330, 150, RED, 1, -1)
            text(ctx, "#@!%&!", 0, 26, 76, (1, 1, 1))
            ctx.restore()
        u2 = ease_out(seg(lt, 1.6, 2.2))
        if u2 > 0.01:
            text(ctx, "JUST FOR FUN?", W / 2, ICON_Y + 310, 64, Y_, alpha=u2)
    elif i == 1:   # announced Oct 8 -> effective Nov 12
        _calendar(ctx, W / 2 - 230, ICON_Y - 150, 1.0, "OCT", "8", ease_back(seg(lt, 0.1, 0.5)))
        text(ctx, "ANNOUNCED", W / 2 - 230, ICON_Y + 30, 40, (1, 1, 1), alpha=ease_out(seg(lt, 0.4, 0.8)))
        u = ease_io(seg(lt, 0.9, 1.6))
        if u > 0.01:
            ctx.move_to(W / 2 - 70, ICON_Y - 150)
            ctx.line_to(W / 2 - 70 + 120 * u, ICON_Y - 150)
            src(ctx, Y_)
            ctx.set_line_width(14)
            ctx.stroke()
        _calendar(ctx, W / 2 + 230, ICON_Y - 150, 1.0, "NOV", "12", ease_back(seg(lt, 2.4, 2.8)))
        text(ctx, "IN EFFECT", W / 2 + 230, ICON_Y + 30, 40, Y_, alpha=ease_out(seg(lt, 2.7, 3.1)))
        u2 = ease_out(seg(lt, 1.0, 1.6))
        if u2 > 0.01:
            rrect(ctx, W / 2 - 300, ICON_Y + 120, 600, 220, 24)
            src(ctx, (1, 1, 1), 0.10 * u2)
            ctx.fill()
            text(ctx, "USAGE POLICY", W / 2, ICON_Y + 200, 60, (1, 1, 1), alpha=u2)
            text(ctx, "ANTHROPIC · CLAUDE", W / 2, ICON_Y + 275, 44, TEAL, alpha=u2)
    elif i == 2:   # policy page with NO stamp
        ctx.save()
        ctx.translate(W / 2, ICON_Y + 10)
        rrect(ctx, -230, -250, 460, 500, 24)
        src(ctx, (0.95, 0.95, 0.92), k)
        ctx.fill()
        for r in range(8):
            ww = 360 if r % 3 else 260
            rrect(ctx, -180, -190 + r * 56, ww * ease_out(seg(lt, 0.1 + r * 0.08, 0.5 + r * 0.08)), 18, 9)
            src(ctx, (0.6, 0.6, 0.62), k)
            ctx.fill()
        ctx.restore()
        u = ease_back(seg(lt, 1.4, 1.8))
        if u > 0.01:
            ctx.save()
            ctx.translate(W / 2, ICON_Y + 10)
            ctx.rotate(-0.22)
            ctx.scale(1.6 - 0.6 * u, 1.6 - 0.6 * u)
            rrect(ctx, -250, -80, 500, 160, 20)
            src(ctx, RED, u)
            ctx.set_line_width(14)
            ctx.stroke()
            text(ctx, "NEEDLESS", 0, -6, 64, RED, alpha=u)
            text(ctx, "CRUELTY", 0, 60, 64, RED, alpha=u)
            ctx.restore()
        u2 = ease_out(seg(lt, 2.6, 3.2))
        if u2 > 0.01:
            text(ctx, "REPEATED + POINTLESS", W / 2, ICON_Y + 330, 56, Y_, alpha=u2)
    elif i == 3:   # still allowed checklist
        items = ("VENTING", "PUSHBACK", "DARK CREATIVE WRITING", "TESTING & RESEARCH")
        starts = (0.2, 1.3, 2.4, 3.6)
        for j, s_ in enumerate(items):
            u2 = ease_back(seg(lt, starts[j], starts[j] + 0.4))
            if u2 > 0.01:
                y = ICON_Y - 240 + j * 150
                rrect(ctx, 110, y - 62, W - 220, 110, 26)
                src(ctx, (1, 1, 1), 0.10 * u2)
                ctx.fill()
                _check(ctx, 190, y - 8, u2)
                text(ctx, s_, 260, y + 12, 56 if len(s_) < 16 else 46, (1, 1, 1), align="left", alpha=u2)
    elif i == 4:   # chat window ended
        rrect(ctx, 150, ICON_Y - 330, W - 300, 560, 30)
        src(ctx, (0.13, 0.14, 0.17), k)
        ctx.fill_preserve()
        src(ctx, (0.4, 0.42, 0.46), k)
        ctx.set_line_width(4)
        ctx.stroke()
        _bubble(ctx, W / 2 + 120, ICON_Y - 240, 360, 80, RED, 0.85 * k, 1)
        _bubble(ctx, W / 2 - 120, ICON_Y - 120, 360, 80, TEAL, 0.85 * k, -1)
        u = ease_back(seg(lt, 0.9, 1.3))
        if u > 0.01:
            ctx.save()
            ctx.translate(W / 2, ICON_Y + 20)
            ctx.scale(u, u)
            rrect(ctx, -340, -55, 680, 110, 55)
            src(ctx, Y_)
            ctx.fill()
            text(ctx, "CONVERSATION ENDED", 0, 16, 44, K_)
            ctx.restore()
        u2 = ease_back(seg(lt, 3.0, 3.4))
        if u2 > 0.01:
            ctx.save()
            ctx.translate(W / 2, ICON_Y + 160)
            ctx.scale(u2, u2)
            rrect(ctx, -200, -45, 400, 90, 45)
            src(ctx, TEAL)
            ctx.fill()
            text(ctx, "+ NEW CHAT", 0, 16, 46, (1, 1, 1))
            ctx.restore()
    elif i == 5:   # since August 2025
        _calendar(ctx, W / 2, ICON_Y - 160, 1.2, "AUG", "2025", ease_back(seg(lt, 0.2, 0.6)))
        u = ease_out(seg(lt, 1.2, 1.8))
        if u > 0.01:
            text(ctx, "CLAUDE COULD ALREADY", W / 2, ICON_Y + 150, 54, (1, 1, 1), alpha=u)
            text(ctx, "END ABUSIVE CHATS", W / 2, ICON_Y + 225, 64, Y_, alpha=u)
    elif i == 6:   # all users, bans unknown
        for j in range(7):
            u2 = ease_back(seg(lt, 0.1 + j * 0.12, 0.5 + j * 0.12))
            if u2 > 0.01:
                x = W / 2 + (j - 3) * 130
                y = ICON_Y - 210
                ellipse(ctx, x, y - 50, 34 * u2, 34 * u2)
                src(ctx, Y_ if j == 3 else (0.85, 0.87, 0.9))
                ctx.fill()
                ellipse(ctx, x, y + 40, 52 * u2, 46 * u2)
                ctx.fill()
        text(ctx, "FREE · PAID · EVERYONE", W / 2, ICON_Y - 50, 50, (1, 1, 1), alpha=ease_out(seg(lt, 0.8, 1.3)))
        u3 = ease_back(seg(lt, 2.4, 2.8))
        if u3 > 0.01:
            ctx.save()
            ctx.translate(W / 2, ICON_Y + 170)
            ctx.scale(u3, u3)
            rrect(ctx, -330, -90, 660, 180, 30)
            src(ctx, (1, 1, 1), 0.12)
            ctx.fill()
            text(ctx, "ACCOUNT BANS?", 0, -8, 64, (1, 1, 1))
            text(ctx, "NOT SPECIFIED", 0, 58, 44, ORANGE)
            ctx.restore()
    elif i == 7:   # why it matters
        _robot(ctx, W / 2, ICON_Y - 170, 0.75 * k, t, k, "happy")
        for j, s_ in enumerate(("HOW WE TREAT AI...", "IS NOW IN THE RULEBOOK")):
            u2 = ease_back(seg(lt, 1.2 + j * 1.4, 1.6 + j * 1.4))
            if u2 > 0.01:
                y = ICON_Y + 130 + j * 140
                _check(ctx, 170, y - 18, u2)
                text(ctx, s_, 230, y, 48, (1, 1, 1), align="left", alpha=u2)


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
