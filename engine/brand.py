"""Subatomic Secrets branding: logo watermark and end-card, drawn with cairo."""
import json
import math
import os
import cairo
from gfx import W, H, text, src, ease_back, seg, wrap, rrect

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND_YELLOW = (0.99, 0.80, 0.02)
BRAND_BLACK = (0.07, 0.07, 0.07)
MIN_CAPTION = 46
_CACHE = {}


def channel():
    if "ch" not in _CACHE:
        with open(os.path.join(ROOT, "brand", "channel.json"), encoding="utf8") as f:
            _CACHE["ch"] = json.load(f)
    return _CACHE["ch"]


def _logo():
    if "logo" not in _CACHE:
        _CACHE["logo"] = cairo.ImageSurface.create_from_png(
            os.path.join(ROOT, "brand", "logo.png"))
    return _CACHE["logo"]


def paint_logo(ctx, cx, cy, size, alpha=1.0, round_=True):
    img = _logo()
    iw = img.get_width()
    k = size / iw
    ctx.save()
    ctx.translate(cx - size / 2, cy - size / 2)
    ctx.scale(k, k)
    if round_:
        ctx.arc(iw / 2, iw / 2, iw / 2, 0, 2 * math.pi)
        ctx.clip()
    ctx.set_source_surface(img, 0, 0)
    ctx.paint_with_alpha(alpha)
    ctx.restore()


def caption(ctx, s, y=1480, size=66, pop=1.0):
    """Burned-in caption: up to 2 wrapped lines on a black pill, yellow outline, safe-area aware."""
    if pop <= 0.01 or not s:
        return
    lines = wrap(ctx, s, size, W - 200)
    while len(lines) > 2 and size > MIN_CAPTION:   # shrink to fit, never drop words
        size -= 4
        lines = wrap(ctx, s, size, W - 200)
    lh = size * 1.2
    h = lh * len(lines) + 40
    ctx.save()
    ctx.translate(W / 2, y)
    ctx.scale(pop, pop)
    ctx.translate(-W / 2, -y)
    rrect(ctx, 70, y - h / 2, W - 140, h, 34)
    src(ctx, BRAND_BLACK, 0.88)
    ctx.fill_preserve()
    src(ctx, BRAND_YELLOW)
    ctx.set_line_width(5)
    ctx.stroke()
    for i, line in enumerate(lines):
        text(ctx, line, W / 2, y - h / 2 + 20 + size * 0.85 + i * lh, size, (1, 1, 1))
    ctx.restore()


def watermark(ctx, alpha=0.85):
    """Small round logo, top-right, inside the Shorts safe area."""
    paint_logo(ctx, W - 120, 200, 130, alpha)


def end_card(ctx, t, t0):
    """Brand end-card from t0 to the end (use ~1.2 s): yellow wipe, logo pop, tagline."""
    if t < t0:
        return
    u = seg(t, t0, t0 + 0.25)
    ctx.rectangle(0, H * (1 - u), W, H * u)
    src(ctx, BRAND_YELLOW)
    ctx.fill()
    k = ease_back(seg(t, t0 + 0.15, t0 + 0.45))
    if k > 0.01:
        paint_logo(ctx, W / 2, H * 0.40, 560 * k, round_=False)
        y = H * 0.64
        text(ctx, "Follow for daily secrets", W / 2, y, 52, BRAND_BLACK)
        text(ctx, "EVERY FACT. EVERYWHERE.", W / 2, y + 70, 38, BRAND_BLACK)
