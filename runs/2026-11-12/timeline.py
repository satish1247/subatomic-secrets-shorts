"""2026-11-12 newsflash: Google DeepMind AlphaProof Code math-checks Signal's encryption core (contract: DURATION + render_frame)."""
import json
import math
import os
import cairo
from gfx import W, H, ease_back, ease_out, ease_io, ease_in, clamp, seg, src, text, ellipse, rrect, lerp, wrap
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
    ("MATH-CHECKED", "AI TESTS SIGNAL'S ENCRYPTION CODE"),
    ("NOV 10", "ALPHAPROOF CODE BY GOOGLE DEEPMIND"),
    ("LEAN PROOFS", "A COMPUTER CHECKS EVERY STEP"),
    ("MACHINE CODE", "DOWN TO WHAT THE CHIP RUNS"),
    ("~4 WEEKS", "NOT YEARS · PER DEEPMIND"),
    ("BUG TEST", "2 OLD, FIXED BUGS PUT BACK"),
    ("THE LIMITS", "NO NEW FLAWS · NOT THE WHOLE APP"),
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
    text(ctx, "BREAKING · AI PROVES CODE", -W / 2 + 90 + (1 - u) * -300, 20, 56, K_, align="left", alpha=u)
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


def _phone(ctx, x, y, s, a=1.0, on=1.0):
    """Generic smartphone; on=0 dims the screen."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -150, -280, 300, 560, 44)
    src(ctx, (0.80, 0.82, 0.86), a)
    ctx.fill()
    rrect(ctx, -134, -262, 268, 524, 32)
    src(ctx, (0.10, 0.12, 0.16) if on > 0.5 else (0.03, 0.03, 0.04), a)
    ctx.fill()
    rrect(ctx, -40, -250, 80, 16, 8)
    src(ctx, (0.80, 0.82, 0.86), a)
    ctx.fill()
    ctx.restore()


def _spark(ctx, x, y, s, col, a=1.0):
    """Four-point sparkle (generic 'AI' glyph)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    pts = []
    for j in range(8):
        r = 80 if j % 2 == 0 else 20
        th = -math.pi / 2 + j * math.pi / 4
        pts.append((r * math.cos(th), r * math.sin(th)))
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.close_path()
    src(ctx, col, a)
    ctx.fill()
    ctx.restore()


def _shield(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(0, -120)
    ctx.line_to(100, -80)
    ctx.curve_to(100, 30, 60, 90, 0, 125)
    ctx.curve_to(-60, 90, -100, 30, -100, -80)
    ctx.close_path()
    src(ctx, TEAL, a)
    ctx.fill()
    ctx.move_to(-40, 0)
    ctx.line_to(-8, 34)
    ctx.line_to(46, -30)
    src(ctx, (1, 1, 1), a)
    ctx.set_line_width(16)
    ctx.stroke()
    ctx.restore()


def _redx(ctx, x, y, r, u):
    if u <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(u, u)
    ctx.move_to(-r, -r)
    ctx.line_to(r, r)
    ctx.move_to(r, -r)
    ctx.line_to(-r, r)
    src(ctx, RED)
    ctx.set_line_width(26)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    ctx.restore()



def _lock(ctx, x, y, s, a=1.0, col=None):
    col = col or Y_
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.arc(0, -40, 55, math.pi, 2 * math.pi)
    ctx.line_to(55, 0)
    ctx.move_to(-55, 0)
    ctx.line_to(-55, -40)
    src(ctx, (0.85, 0.87, 0.90), a)
    ctx.set_line_width(22)
    ctx.stroke()
    rrect(ctx, -85, -10, 170, 140, 22)
    src(ctx, col, a)
    ctx.fill()
    ellipse(ctx, 0, 45, 18, 18)
    src(ctx, K_, a)
    ctx.fill()
    ctx.rectangle(-7, 50, 14, 40)
    ctx.fill()
    ctx.restore()


def _bubble(ctx, x, y, w, h, col, a, left=True):
    rrect(ctx, x - w / 2, y - h / 2, w, h, 26)
    tx = x - w / 2 + 30 if left else x + w / 2 - 30
    ctx.move_to(tx - 14, y + h / 2 - 2)
    ctx.line_to(tx + (-22 if left else 22), y + h / 2 + 26)
    ctx.line_to(tx + 14, y + h / 2 - 2)
    src(ctx, col, a)
    ctx.fill()
    for j in range(3):
        rrect(ctx, x - w / 2 + 26, y - h / 2 + 22 + j * 26, (w - 52) * (0.9 - 0.25 * j), 12, 6)
        src(ctx, K_, a * 0.35)
        ctx.fill()


def _robot(ctx, x, y, s, t, a=1.0, col=None):
    """Small generic AI agent glyph."""
    col = col or TEAL
    ctx.save()
    ctx.translate(x, y + 6 * math.sin(t * 4 + x))
    ctx.scale(s, s)
    ctx.move_to(0, -95)
    ctx.line_to(0, -70)
    src(ctx, (1, 1, 1), a)
    ctx.set_line_width(8)
    ctx.stroke()
    ellipse(ctx, 0, -100, 12, 12)
    src(ctx, Y_, a)
    ctx.fill()
    rrect(ctx, -70, -70, 140, 110, 30)
    src(ctx, col, a)
    ctx.fill()
    blink = 0.15 if (t * 1.3 + x * 0.01) % 3 < 0.12 else 1
    for ex in (-28, 28):
        ellipse(ctx, ex, -20, 14, 16 * blink)
        src(ctx, (1, 1, 1), a)
        ctx.fill()
    rrect(ctx, -26, 10, 52, 10, 5)
    src(ctx, (1, 1, 1), a)
    ctx.fill()
    ctx.restore()


def _person(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ellipse(ctx, 0, -60, 38, 38)
    src(ctx, (1, 1, 1), a)
    ctx.fill()
    ctx.arc(0, 60, 70, math.pi, 2 * math.pi)
    ctx.close_path()
    ctx.fill()
    ctx.restore()


LEAN = ["theorem session_secret :", "  attacker_knows k → False", "  := by intro h; cases h", "lemma ratchet_step :",
        "  fresh (next_key s)", "  := by simp [kdf_spec]", "theorem msg_private :", "  ∀ m, ¬ leaks m", "  := by exact proof_42"]


def _code_panel(ctx, x, y, t, t0, a=1.0):
    w, h = 760, 520
    rrect(ctx, x - w / 2, y - h / 2, w, h, 28)
    src(ctx, (0.10, 0.11, 0.14), a)
    ctx.fill_preserve()
    src(ctx, TEAL, a)
    ctx.set_line_width(5)
    ctx.stroke()
    for j, c in enumerate((RED, ORANGE, GREEN)):
        ellipse(ctx, x - w / 2 + 40 + j * 36, y - h / 2 + 34, 11, 11)
        src(ctx, c, a)
        ctx.fill()
    ctx.save()
    rrect(ctx, x - w / 2 + 10, y - h / 2 + 64, w - 20, h - 80, 18)
    ctx.clip()
    off = (t - t0) * 70
    for j in range(16):
        yy = y - h / 2 + 110 + j * 52 - off % 52
        idx = (j + int(off // 52)) % len(LEAN)
        text(ctx, LEAN[idx], x - w / 2 + 40, yy, 32, (0.80, 0.86, 0.95), align="left", alpha=a)
        if idx % 3 == 2:
            text(ctx, "✓", x + w / 2 - 50, yy, 38, GREEN, alpha=a)
    ctx.restore()


def _bug(ctx, x, y, s, t, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.set_line_width(8)
    src(ctx, (0.15, 0.15, 0.15), a)
    for side in (-1, 1):
        for j in range(3):
            wig = 6 * math.sin(t * 12 + j)
            ctx.move_to(side * 40, -20 + j * 30)
            ctx.line_to(side * 85, -35 + j * 35 + wig)
    ctx.move_to(-15, -60)
    ctx.line_to(-35, -95)
    ctx.move_to(15, -60)
    ctx.line_to(35, -95)
    src(ctx, (1, 1, 1), a)
    ctx.stroke()
    ellipse(ctx, 0, 10, 52, 68)
    src(ctx, ORANGE, a)
    ctx.fill()
    ellipse(ctx, 0, -55, 34, 28)
    src(ctx, (0.25, 0.20, 0.18), a)
    ctx.fill()
    ctx.move_to(0, -40)
    ctx.line_to(0, 75)
    src(ctx, (0.25, 0.20, 0.18), a)
    ctx.set_line_width(5)
    ctx.stroke()
    for (dx, dy) in ((-22, -5), (22, 10), (-18, 35)):
        ellipse(ctx, dx, dy, 9, 9)
        ctx.fill()
    ctx.restore()


def _bar_row(ctx, y, label, frac, col, u, a=1.0):
    x0, wmax = 140, W - 280
    text(ctx, label, x0, y - 30, 44, (1, 1, 1), align="left", alpha=a)
    rrect(ctx, x0, y, wmax, 70, 35)
    src(ctx, (1, 1, 1), 0.12 * a)
    ctx.fill()
    ww = max(70, wmax * frac * u)
    rrect(ctx, x0, y, ww, 70, 35)
    src(ctx, col, a)
    ctx.fill()


def _icon(ctx, i, t, k):
    t0 = _card_start(i)
    lt = t - t0
    cx, cy = W / 2, ICON_Y
    if i == 0:
        _phone(ctx, cx, cy + 40, 1.0 * k)
        u1 = ease_back(seg(lt, 0.3, 0.7))
        u2 = ease_back(seg(lt, 0.9, 1.3))
        if u1 > 0.01:
            _bubble(ctx, cx - 30, cy - 120, 200 * u1, 110 * u1, (1, 1, 1), 1, True)
        if u2 > 0.01:
            _bubble(ctx, cx + 30, cy + 20, 200 * u2, 110 * u2, Y_, 1, False)
        ul = ease_back(seg(lt, 1.5, 1.9))
        if ul > 0.01:
            _lock(ctx, cx, cy + 190, 0.8 * ul)
        # magnifier sweeping = AI check
        us = seg(lt, 1.8, 5.5)
        if us > 0:
            mx = cx + 230 * math.cos(us * 6)
            my = cy + 60 + 170 * math.sin(us * 4)
            ellipse(ctx, mx, my, 70, 70)
            src(ctx, TEAL, 0.25)
            ctx.fill()
            ctx.arc(mx, my, 70, 0, 2 * math.pi)
            src(ctx, TEAL)
            ctx.set_line_width(14)
            ctx.stroke()
            ctx.move_to(mx + 50, my + 50)
            ctx.line_to(mx + 110, my + 110)
            ctx.set_line_width(22)
            ctx.stroke()
            _spark(ctx, mx, my, 0.45, Y_)
    elif i == 1:
        _calendar(ctx, cx, cy - 150, 0.9, "NOV", "10", k)
        uh = ease_back(seg(lt, 0.9, 1.3))
        ua = ease_back(seg(lt, 2.6, 3.0))
        if uh > 0.01:
            _person(ctx, cx - 250, cy + 150, 0.9 * uh)
            _person(ctx, cx - 160, cy + 160, 0.7 * uh, 0.7)
            _pill(ctx, cx - 230, cy + 300, "HUMANS: GOALS", uh, (1, 1, 1), K_, 38, 400)
        if ua > 0.01:
            for j in range(3):
                _robot(ctx, cx + 160 + j * 100, cy + 150 + (j % 2) * 20, 0.65 * ua, t)
            _pill(ctx, cx + 280, cy + 300, "AI: PROOFS", ua, TEAL, (1, 1, 1), 38, 320)
        if ua > 0.01:
            ctx.move_to(cx - 5, cy + 300)
            ctx.line_to(cx + 70, cy + 300)
            src(ctx, Y_, ua)
            ctx.set_line_width(10)
            ctx.stroke()
            ctx.move_to(cx + 70, cy + 280)
            ctx.line_to(cx + 95, cy + 300)
            ctx.line_to(cx + 70, cy + 320)
            ctx.fill()
    elif i == 2:
        ctx.save()
        ctx.translate(cx, cy)
        ctx.scale(k, k)
        ctx.translate(-cx, -cy)
        _code_panel(ctx, cx, cy, t, t0)
        ctx.restore()
        um = ease_back(seg(lt, 3.2, 3.6))
        _pill(ctx, cx, cy + 340, "MILLIONS OF LINES", um, Y_, K_, 46, 560)
    elif i == 3:
        ctx.save()
        ctx.rectangle(0, 700, W, 700)
        ctx.clip()
        for j in range(14):
            col_x = 120 + j * 64
            for r in range(8):
                yy = 720 + ((r * 90 + t * 160 + j * 37) % 720)
                d = abs(col_x - cx)
                if yy > cy - 130 and d < 270:
                    continue
                text(ctx, "01"[(r + j + int(t * 3)) % 2], col_x, yy, 40, GREEN, alpha=0.55 * k)
        ctx.restore()
        _chip(ctx, cx, cy + 100, 1.3 * k)
        uc = ease_back(seg(lt, 2.5, 2.9))
        _check(ctx, cx + 160, cy - 40, uc)
    elif i == 4:
        uy = ease_out(seg(lt, 0.3, 1.6))
        uw = ease_out(seg(lt, 1.6, 2.2))
        _bar_row(ctx, cy - 120, "USUALLY: YEARS", 1.0, (0.55, 0.56, 0.60), uy, k)
        _bar_row(ctx, cy + 120, "AI + HUMANS: ~4 WEEKS", 0.12, Y_, uw, k)
        for j in range(4):
            uu = ease_back(seg(lt, 2.2 + j * 0.2, 2.5 + j * 0.2))
            if uu > 0.01:
                _calendar(ctx, 220 + j * 210, cy + 330, 0.55, "WEEK", str(j + 1), uu)
    elif i == 5:
        for j, bx in enumerate((cx - 220, cx + 220)):
            ub = ease_back(seg(lt, 0.2 + j * 0.4, 0.6 + j * 0.4))
            if ub > 0.01:
                _bug(ctx, bx, cy, 1.4 * ub, t)
                _pill(ctx, bx, cy + 190, "OLD BUG #%d" % (j + 1), ub, (1, 1, 1), K_, 38, 320)
            ux = ease_back(seg(lt, 3.6 + j * 0.4, 3.9 + j * 0.4))
            _redx(ctx, bx, cy, 120, ux)
        ui = ease_back(seg(lt, 4.6, 5.0))
        _pill(ctx, cx, cy + 330, "PROVED INSECURE", ui, RED, (1, 1, 1), 48, 560)
    elif i == 6:
        _shield(ctx, cx, cy - 20, 1.3 * k)
        u1 = ease_back(seg(lt, 0.4, 0.8))
        u2 = ease_back(seg(lt, 1.6, 2.0))
        _pill(ctx, cx, cy + 230, "NO NEW FLAWS FOUND", u1, TEAL, (1, 1, 1), 42, 600)
        _pill(ctx, cx, cy + 350, "CORE CODE · NOT WHOLE APP", u2, (1, 1, 1), K_, 40, 780)


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
