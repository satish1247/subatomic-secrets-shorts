"""Shared drawing primitives, palette, easing and keyframe tracks."""
import math
import cairo

W, H, FPS, DURATION = 1080, 1920, 30, 30.0
import os
import sys
FONT = os.environ.get("VIDEO_FONT") or ("Arial Rounded MT Bold" if sys.platform == "win32" else "DejaVu Sans")

# ---------------------------------------------------------------- palette
OUT = (0.20, 0.12, 0.08)
SKIN = (0.80, 0.55, 0.36)
SKIN_D = (0.66, 0.41, 0.26)
SKIN_L = (0.90, 0.66, 0.47)
HAIR = (0.13, 0.09, 0.07)
SHIRT = (0.98, 0.76, 0.24)
SHIRT_D = (0.90, 0.58, 0.13)
STRIPE = (0.94, 0.47, 0.16)
PANTS = (0.38, 0.27, 0.22)
PANTS_D = (0.27, 0.19, 0.16)
GAMCHA = (0.88, 0.30, 0.20)
TEAL = (0.14, 0.60, 0.62)
TEAL_D = (0.08, 0.42, 0.46)
TEAL_L = (0.45, 0.80, 0.78)
CREAM = (0.99, 0.94, 0.83)
ORANGE = (0.96, 0.55, 0.18)
YELLOW = (0.99, 0.82, 0.30)
WHITE = (1, 1, 1)
STEEL = (0.40, 0.53, 0.60)
STEEL_L = (0.72, 0.80, 0.84)


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, u):
    return a + (b - a) * u


def seg(t, a, b):
    """Normalised progress of t through [a, b]."""
    if b <= a:
        return 1.0 if t >= b else 0.0
    return clamp((t - a) / (b - a))


def ease_io(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


def ease_out(u):
    u = clamp(u)
    return 1 - (1 - u) ** 3


def ease_in(u):
    u = clamp(u)
    return u ** 3


def ease_back(u, s=1.8):
    u = clamp(u) - 1
    return 1 + u * u * ((s + 1) * u + s)


EASES = {
    "io": ease_io, "out": ease_out, "in": ease_in, "back": ease_back,
    "lin": clamp, "step": lambda u: 1.0 if u >= 1 else 0.0,
}


def _is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


class Track:
    """Cumulative keyframes: each key only lists params that change.

    keys: [(time, {param: value}, ease_name?), ...]; the ease applies to the
    segment arriving at that key. Non-numeric params switch on arrival.
    """

    def __init__(self, base, keys):
        self.times, self.states, self.eases = [], [], []
        cur = dict(base)
        for key in keys:
            cur = {**cur, **key[1]}
            self.times.append(key[0])
            self.states.append(cur)
            self.eases.append(EASES[key[2] if len(key) > 2 else "io"])

    def at(self, t):
        if t <= self.times[0]:
            return dict(self.states[0])
        for i in range(1, len(self.times)):
            if t < self.times[i]:
                a, b = self.states[i - 1], self.states[i]
                u = self.eases[i](seg(t, self.times[i - 1], self.times[i]))
                return {
                    k: lerp(a[k], b[k], u) if _is_num(a[k]) and _is_num(b[k])
                    else (b[k] if u >= 1 else a[k])
                    for k in b
                }
        return dict(self.states[-1])


# ---------------------------------------------------------------- shapes
def ellipse(ctx, x, y, rx, ry):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(max(rx, 0.01), max(ry, 0.01))
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()


def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def quad_to(ctx, cx, cy, x, y):
    x0, y0 = ctx.get_current_point()
    ctx.curve_to(x0 + 2 / 3 * (cx - x0), y0 + 2 / 3 * (cy - y0),
                 x + 2 / 3 * (cx - x), y + 2 / 3 * (cy - y), x, y)


def src(ctx, c, a=1.0):
    if isinstance(c, cairo.Pattern):
        ctx.set_source(c)
    elif len(c) == 4:
        ctx.set_source_rgba(*c)
    else:
        ctx.set_source_rgba(c[0], c[1], c[2], a)


def fill_out(ctx, fill, lw=5.0, out=OUT, alpha=1.0):
    src(ctx, fill, alpha)
    ctx.fill_preserve()
    if lw > 0:
        src(ctx, out, alpha)
        ctx.set_line_width(lw)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke()
    else:
        ctx.new_path()


def shade(c, k):
    return tuple(clamp(v * k) for v in c[:3])


def vgrad(y0, y1, c0, c1):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *c0[:3])
    g.add_color_stop_rgb(1, *c1[:3])
    return g


def hgrad(x0, x1, c0, c1):
    g = cairo.LinearGradient(x0, 0, x1, 0)
    g.add_color_stop_rgb(0, *c0[:3])
    g.add_color_stop_rgb(1, *c1[:3])
    return g


def rgrad(x, y, r, c0, c1, fx=None, fy=None):
    g = cairo.RadialGradient(x if fx is None else fx, y if fy is None else fy,
                             0, x, y, r)
    g.add_color_stop_rgb(0, *c0[:3])
    g.add_color_stop_rgb(1, *c1[:3])
    return g


def limb(ctx, pts, width, color, lw=5.0, out=OUT):
    """Thick outlined stroke through pts (round caps)."""
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    for w, c in ((width + 2 * lw, out), (width, color)):
        ctx.move_to(*pts[0])
        for p in pts[1:]:
            ctx.line_to(*p)
        src(ctx, c)
        ctx.set_line_width(w)
        ctx.stroke()


def soft_shadow(ctx, x, y, rx, ry, a=0.28):
    g = cairo.RadialGradient(0, 0, 0, 0, 0, 1)
    g.add_color_stop_rgba(0, 0.15, 0.08, 0.05, a)
    g.add_color_stop_rgba(1, 0.15, 0.08, 0.05, 0)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(rx, ry)
    ctx.set_source(g)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()


def text(ctx, s, x, y, size, color=OUT, align="center", alpha=1.0):
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    ext = ctx.text_extents(s)
    if align == "center":
        x -= ext.x_advance / 2
    elif align == "right":
        x -= ext.x_advance
    ctx.move_to(x, y)
    src(ctx, color, alpha)
    ctx.show_text(s)
    ctx.new_path()


def wrap(ctx, s, size, max_w):
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    lines, cur = [], ""
    for word in s.split():
        trial = (cur + " " + word).strip()
        if ctx.text_extents(trial).x_advance > max_w and cur:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines
