"""Demo step 2: newsflash-style timeline (contract: DURATION + render_frame)."""
import json
import math
import os
import cairo
from gfx import W, H, ease_back, ease_out, seg, src, text, ellipse
import brand
import sfx

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "lines.json"), encoding="utf8") as _f:
    DATA = json.load(_f)
DURATION = DATA["duration"]
LINES = DATA["lines"]
ENV = [sfx.envelope(os.path.join(HERE, k["wav"])) for k in LINES]
KEYWORDS = ["SECRET", "8 MINUTES", "THE PAST", "1000s OF YEARS"]


def _active(t):
    for i, k in enumerate(LINES):
        nxt = LINES[i + 1]["start"] if i + 1 < len(LINES) else DURATION
        if k["start"] - 0.2 <= t < nxt - 0.2:
            return i
    return None


def _background(ctx, t):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.07, 0.07, 0.09)
    g.add_color_stop_rgb(1, 0.02, 0.02, 0.03)
    ctx.set_source(g)
    ctx.paint()
    for i in range(60):
        x = (i * 173.3 + t * (8 + i % 5 * 6)) % W
        y = (i * 311.7) % H
        ellipse(ctx, x, y, 2 + i % 3, 2 + i % 3)
        src(ctx, (1, 1, 1), 0.25 + 0.2 * math.sin(t * 2 + i))
        ctx.fill()
    u = ease_out(seg(t, 0.0, 0.6))
    ctx.save()
    ctx.translate(W / 2, 330)
    ctx.rotate(-0.08)
    ctx.rectangle(-W * u, -55, 2 * W * u, 110)
    src(ctx, brand.BRAND_YELLOW)
    ctx.fill()
    text(ctx, "DID YOU KNOW?", 0, 22, 64, brand.BRAND_BLACK, alpha=u)
    ctx.restore()


def _sun(ctx, t, i):
    k = ease_back(seg(t, LINES[i]["start"] - 0.2, LINES[i]["start"] + 0.3)) if i is not None else 1
    g = cairo.RadialGradient(W / 2, 900, 0, W / 2, 900, 330)
    g.add_color_stop_rgba(0, 1, 0.95, 0.6, 1)
    g.add_color_stop_rgba(0.55, 1, 0.8, 0.1, 0.9)
    g.add_color_stop_rgba(1, 1, 0.6, 0.0, 0)
    ctx.save()
    ctx.translate(W / 2, 900)
    ctx.scale(0.6 + 0.4 * k, 0.6 + 0.4 * k)
    ctx.translate(-W / 2, -900)
    ctx.set_source(g)
    ctx.arc(W / 2, 900, 330, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()
    for j in range(8):
        u = (t * 0.4 + j / 8) % 1
        ellipse(ctx, W / 2 + 60 * math.cos(j), 900 + u * 700, 10, 26)
        src(ctx, (1, 0.9, 0.4), 0.8 * (1 - u))
        ctx.fill()


def render_frame(t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    _background(ctx, t)
    i = _active(t)
    _sun(ctx, t, i)
    if i is not None:
        line = LINES[i]
        k = ease_back(seg(t, line["start"] - 0.2, line["start"] + 0.15))
        ctx.save()
        ctx.translate(W / 2, 560)
        ctx.scale(k, k)
        text(ctx, KEYWORDS[i], 0, 0, 110, brand.BRAND_YELLOW)
        ctx.restore()
        f = int((t - line["start"]) * 30)
        pulse = 1 + 0.03 * (ENV[i][f] if 0 <= f < len(ENV[i]) else 0)
        brand.caption(ctx, line["text"], 1480, 64, pop=k * pulse)
    brand.watermark(ctx)
    brand.end_card(ctx, t, DURATION - 1.4)
    surf.flush()
    return surf
