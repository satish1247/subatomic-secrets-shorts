"""Props (railway fan, phone, switchboard, stool, bulb) and screen bubbles."""
import math
from gfx import (OUT, CREAM, WHITE, STEEL_L,
                 ellipse, rrect, quad_to, src, fill_out, rgrad, vgrad,
                 hgrad, limb, text, wrap, clamp)

FAN_R, FAN_RY = 175, 64


def _blade_path(ctx, a):
    ctx.save()
    ctx.scale(1, FAN_RY / FAN_R)
    ctx.rotate(a)
    ctx.move_to(22, -14)
    ctx.curve_to(70, -40, 150, -44, 158, -8)
    ctx.curve_to(160, 20, 90, 30, 22, 14)
    ctx.close_path()
    ctx.restore()


def draw_fan(ctx, x, y, fs, angle, speed, attached=False, label=False, tilt=0.0):
    """Indian-railway style caged ceiling fan, seen from slightly below.

    (x, y) = cage centre. speed in rev/s controls motion blur.
    """
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(tilt)
    ctx.scale(fs, fs)
    if attached:
        limb(ctx, [(0, -150), (0, -70)], 18, STEEL_L, 4)
    ctx.move_to(-58, -64)
    ctx.line_to(-58, -8)
    quad_to(ctx, 0, 14, 58, -8)
    ctx.line_to(58, -64)
    ctx.close_path()
    fill_out(ctx, hgrad(-58, 58, (0.52, 0.66, 0.74), (0.28, 0.38, 0.46)))
    ellipse(ctx, 0, -64, 58, 18)
    fill_out(ctx, (0.60, 0.73, 0.80))
    if label:
        rrect(ctx, -36, -52, 72, 26, 4)
        fill_out(ctx, CREAM, 3)
        text(ctx, "110V DC", 0, -33, 15, (0.75, 0.15, 0.1))
    ellipse(ctx, 0, 0, FAN_R, FAN_RY)
    src(ctx, (0.20, 0.30, 0.36), 0.35)
    ctx.fill()
    blur = clamp(speed / 3.0)
    if blur > 0.05:
        ellipse(ctx, 0, 0, 160, 160 * FAN_RY / FAN_R)
        src(ctx, (0.55, 0.72, 0.78), 0.35 * blur)
        ctx.fill()
    ghosts = 1 + int(blur * 5)
    for g in range(ghosts):
        off = -g * 0.16 * blur
        alpha = 1.0 if ghosts == 1 else 0.5 * (ghosts - g) / ghosts
        for b in range(3):
            _blade_path(ctx, angle + off + b * 2 * math.pi / 3)
            fill_out(ctx, (0.47, 0.64, 0.72), 3.5 if ghosts == 1 else 0, alpha=alpha)
    ellipse(ctx, 0, 0, 30, 13)
    fill_out(ctx, (0.35, 0.47, 0.55), 4)
    ctx.set_line_width(2.6)
    src(ctx, (0.80, 0.86, 0.88))
    for r in (55, 95, 135):
        ellipse(ctx, 0, 0, r, r * FAN_RY / FAN_R)
        ctx.stroke()
    for i in range(24):
        a = i * math.pi / 12
        ctx.move_to(30 * math.cos(a), 30 * math.sin(a) * FAN_RY / FAN_R)
        ctx.line_to(FAN_R * math.cos(a), FAN_R * math.sin(a) * FAN_RY / FAN_R)
    ctx.stroke()
    ellipse(ctx, 0, 0, FAN_R, FAN_RY)
    src(ctx, OUT)
    ctx.set_line_width(14)
    ctx.stroke_preserve()
    src(ctx, STEEL_L)
    ctx.set_line_width(8)
    ctx.stroke()
    ctx.restore()


def draw_wire(ctx, x0, y0, x1, y1, sag, color, w=9):
    mx, my = (x0 + x1) / 2, max(y0, y1) + sag
    ctx.set_line_cap(1)
    for lw, c in ((w + 6, OUT), (w, color)):
        ctx.move_to(x0, y0)
        quad_to(ctx, mx, my, x1, y1)
        src(ctx, c)
        ctx.set_line_width(lw)
        ctx.stroke()


def draw_plug(ctx, x, y, color=(0.2, 0.2, 0.22)):
    rrect(ctx, x - 14, y - 16, 28, 32, 6)
    fill_out(ctx, color, 4)
    for dx in (-6, 6):
        ctx.rectangle(x + dx - 2, y - 28, 4, 12)
    src(ctx, (0.85, 0.7, 0.3))
    ctx.fill()


def draw_phone(ctx, x, y, ang=0.0, glow=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    rrect(ctx, -24, -44, 48, 88, 10)
    fill_out(ctx, (0.12, 0.12, 0.15), 4)
    rrect(ctx, -18, -36, 36, 70, 5)
    src(ctx, (0.25 + 0.5 * glow, 0.75, 0.80))
    ctx.fill()
    ctx.restore()


def draw_switchboard(ctx, x, y):
    rrect(ctx, x - 85, y - 110, 170, 220, 14)
    fill_out(ctx, vgrad(y - 110, y + 110, (1, 0.98, 0.92), (0.88, 0.85, 0.78)))
    for i, up in enumerate((True, False, True)):
        bx = x - 55 + i * 55
        rrect(ctx, bx - 18, y - 88, 36, 56, 6)
        fill_out(ctx, WHITE, 3.5)
        rrect(ctx, bx - 12, y - 82 if up else y - 60, 24, 22, 4)
        src(ctx, (0.8, 0.3, 0.2) if up else (0.7, 0.7, 0.7))
        ctx.fill()
    ellipse(ctx, x, y + 25, 38, 38)
    fill_out(ctx, WHITE, 3.5)
    for dx, dy in ((0, -14), (-13, 10), (13, 10)):
        ellipse(ctx, x + dx, y + 25 + dy, 5, 5)
        src(ctx, OUT)
        ctx.fill()
    text(ctx, "230V AC", x, y + 95, 22, (0.75, 0.15, 0.1))


def draw_stool(ctx, x, top_y, floor_y):
    for dx in (-40, 40, -80, 80):
        limb(ctx, [(x + dx * 0.9, top_y + 10), (x + dx, floor_y)], 16,
             (0.55, 0.32, 0.16) if abs(dx) > 50 else (0.45, 0.25, 0.12), 4)
    ctx.rectangle(x - 108, top_y, 216, 26)
    fill_out(ctx, (0.62, 0.36, 0.18))
    ellipse(ctx, x, top_y, 108, 24)
    fill_out(ctx, rgrad(x - 30, top_y - 10, 130, (0.85, 0.58, 0.32), (0.66, 0.40, 0.2)))


def draw_bulb(ctx, x, y, s, glow):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.set_source_rgba(1, 0.92, 0.5, 0.35 * glow)
    ctx.arc(0, 0, 120, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_line_cap(1)
    src(ctx, (1, 0.8, 0.2))
    ctx.set_line_width(9)
    for i in range(9):
        a = -math.pi + i * math.pi / 8
        ctx.move_to(78 * math.cos(a), 78 * math.sin(a))
        ctx.line_to((78 + 30 * glow) * math.cos(a), (78 + 30 * glow) * math.sin(a))
    ctx.stroke()
    ctx.arc(0, 0, 55, 0, 2 * math.pi)
    fill_out(ctx, rgrad(0, 0, 150, (1, 0.95, 0.6), (1, 0.85, 0.3)), 6)
    rrect(ctx, -26, 45, 52, 36, 6)
    fill_out(ctx, STEEL_L, 5)
    ctx.restore()


def draw_puff(ctx, x, y, u):
    """Dust puff, u in [0,1]."""
    if not 0 < u < 1:
        return
    for i in range(8):
        a = i * math.pi / 4 + 0.3
        r = 30 + 110 * u
        ellipse(ctx, x + r * math.cos(a), y + r * math.sin(a) * 0.6,
                30 + 30 * u, 26 + 24 * u)
        src(ctx, (0.93, 0.88, 0.80), 0.85 * (1 - u))
        ctx.fill()


# ---------------------------------------------------------------- bubbles
def _cloud_circles(x, y, w, h):
    n = 12
    return [(x + (w / 2) * math.cos(i * 2 * math.pi / n),
             y + (h / 2) * math.sin(i * 2 * math.pi / n),
             0.26 * min(w, h) + 0.05 * w * (i % 2)) for i in range(n)]


def _scaled(ctx, x, y, k):
    ctx.translate(x, y)
    ctx.scale(k, k)
    ctx.translate(-x, -y)


def thought_bubble(ctx, x, y, w, h, tail, pop, content=None):
    """Cloud bubble centred (x, y); tail = (tx, ty) point near the head."""
    if pop <= 0.01:
        return
    ctx.save()
    _scaled(ctx, x, y, pop)
    circles = _cloud_circles(x, y, w * 0.82, h * 0.72)
    tx, ty = tail
    by = y + h * 0.42
    small = [(x + (tx - x) * f, by + (ty - by) * f, r)
             for f, r in ((0.35, 26), (0.62, 18), (0.85, 12))]
    for grow, color in ((6, OUT), (0, WHITE)):
        for cx, cy, r in circles + small:
            ctx.arc(cx, cy, r + grow, 0, 2 * math.pi)
            src(ctx, color)
            ctx.fill()
        ellipse(ctx, x, y, w * 0.47 + grow, h * 0.42 + grow)
        src(ctx, color)
        ctx.fill()
    if content:
        ctx.save()
        ellipse(ctx, x, y, w * 0.47, h * 0.42)
        ctx.clip()
        content()
        ctx.restore()
    ctx.restore()


def speech_bubble(ctx, s, x, y, w, tail, pop, size=54):
    """Rounded speech bubble; (x, y) = top centre."""
    if pop <= 0.01:
        return
    lines = wrap(ctx, s, size, w - 80)
    lh = size * 1.22
    h = lh * len(lines) + 70
    ctx.save()
    _scaled(ctx, tail[0], tail[1], pop)
    tx, ty = tail
    for stroke_w, c in ((12, OUT), (0, WHITE)):
        rrect(ctx, x - w / 2, y, w, h, 46)
        ctx.move_to(tx - 45, y + h - 4)
        ctx.line_to(tx, ty)
        ctx.line_to(tx + 25, y + h - 4)
        ctx.close_path()
        src(ctx, c)
        if stroke_w:
            ctx.set_line_width(stroke_w)
            ctx.set_line_join(1)
            ctx.stroke()
        else:
            ctx.fill()
    for i, line in enumerate(lines):
        text(ctx, line, x, y + 35 + size * 0.8 + i * lh, size, OUT)
    ctx.restore()
    return h
