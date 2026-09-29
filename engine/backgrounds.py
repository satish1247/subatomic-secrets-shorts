"""Static-ish environments: Indian railway coach and Arjun's room."""
import math
from gfx import (OUT, TEAL, TEAL_D, ORANGE, YELLOW, WHITE, STEEL_L,
                 ellipse, rrect, quad_to, src, fill_out, shade, rgrad, vgrad, limb)

WIN = (170, 620, 740, 410)          # x, y, w, h of the coach window
SEAT_Y, TRAIN_FLOOR = 1250, 1470
HOME_FLOOR = 1600
BERTH = (0.13, 0.47, 0.58)


# ================================================================ train
def _scenery(ctx, t):
    x, y, w, h = WIN
    ctx.rectangle(x, y, w, h)
    src(ctx, vgrad(y, y + h, (0.62, 0.86, 0.90), (1.0, 0.90, 0.70)))
    ctx.fill()
    ellipse(ctx, x + 560, y + 110, 46, 46)
    src(ctx, (1, 0.93, 0.6))
    ctx.fill()
    off = -(t * 18) % 400
    ctx.move_to(x - 400, y + h)
    for i in range(12):
        hx = x - 400 + off + i * 200
        ctx.line_to(hx, y + 260)
        quad_to(ctx, hx + 100, y + 150 + 40 * (i % 3), hx + 200, y + 260)
    ctx.line_to(x + w + 400, y + h)
    ctx.close_path()
    src(ctx, (0.45, 0.70, 0.66))
    ctx.fill()
    ctx.rectangle(x, y + 280, w, h)
    src(ctx, vgrad(y + 280, y + h, (0.72, 0.80, 0.36), (0.55, 0.66, 0.25)))
    ctx.fill()
    off = -(t * 420) % 330
    for i in range(5):
        tx = x - 330 + off + i * 330
        limb(ctx, [(tx, y + 330), (tx, y + 250)], 12, (0.45, 0.3, 0.2), 0)
        ellipse(ctx, tx, y + 225, 60, 52)
        src(ctx, (0.25, 0.55, 0.35))
        ctx.fill()
    off = -(t * 900) % 520
    for i in range(3):
        px = x - 520 + off + i * 520
        limb(ctx, [(px, y + h), (px, y + 40)], 10, (0.35, 0.3, 0.3), 0)


def _coach_top(ctx):
    ctx.rectangle(-900, -900, 2880, 3720)
    src(ctx, vgrad(200, 1300, (0.93, 0.89, 0.79), (0.86, 0.82, 0.72)))
    ctx.fill()
    ctx.move_to(-900, -900)
    ctx.line_to(1980, -900)
    ctx.line_to(1980, 230)
    quad_to(ctx, 540, 290, -900, 230)
    ctx.close_path()
    src(ctx, vgrad(-100, 280, (0.99, 0.97, 0.90), (0.92, 0.88, 0.78)))
    ctx.fill_preserve()
    src(ctx, TEAL)
    ctx.set_line_width(12)
    ctx.stroke()
    for lx in (60, 760):
        rrect(ctx, lx, 150, 280, 26, 13)
        fill_out(ctx, (1, 1, 0.95), 4)
    rrect(ctx, 90, 470, 200, 100, 14)
    fill_out(ctx, (0.85, 0.42, 0.18))
    rrect(ctx, 150, 452, 80, 24, 10)
    fill_out(ctx, (0.5, 0.25, 0.12), 4)
    rrect(ctx, 760, 480, 190, 90, 30)
    fill_out(ctx, TEAL_D)
    for yy in (570, 590):
        limb(ctx, [(-900, yy), (1980, yy)], 8, STEEL_L, 3)


def _coach_window(ctx, t):
    x, y, w, h = WIN
    rrect(ctx, x - 30, y - 30, w + 60, h + 60, 34)
    fill_out(ctx, (0.55, 0.66, 0.68))
    ctx.save()
    ctx.rectangle(x, y, w, h)
    ctx.clip()
    _scenery(ctx, t)
    ctx.restore()
    ctx.rectangle(x, y, w, 40)
    src(ctx, (0.55, 0.62, 0.62))
    ctx.fill()
    for i in range(5):
        by = y + 80 + i * 68
        limb(ctx, [(x, by), (x + w, by)], 8, (0.78, 0.82, 0.83), 3)
    ctx.rectangle(x, y, w, h)
    src(ctx, OUT)
    ctx.set_line_width(5)
    ctx.stroke()


def _coach_berth(ctx):
    ctx.rectangle(-900, 1045, 2880, SEAT_Y - 1045)
    src(ctx, vgrad(1045, SEAT_Y, shade(BERTH, 1.15), shade(BERTH, 0.85)))
    ctx.fill()
    src(ctx, shade(BERTH, 0.7))
    ctx.set_line_width(4)
    for sx in range(-900, 1980, 135):
        ctx.move_to(sx, 1060)
        ctx.line_to(sx, SEAT_Y - 10)
    ctx.stroke()
    rrect(ctx, -900, SEAT_Y - 18, 2880, 70, 20)
    fill_out(ctx, vgrad(SEAT_Y - 18, SEAT_Y + 52, shade(BERTH, 1.25), shade(BERTH, 0.8)))
    ctx.rectangle(-900, SEAT_Y + 52, 2880, TRAIN_FLOOR - SEAT_Y - 52)
    src(ctx, (0.28, 0.26, 0.25))
    ctx.fill()
    ctx.rectangle(-900, TRAIN_FLOOR, 2880, 1400)
    src(ctx, vgrad(TRAIN_FLOOR, 1920, (0.62, 0.58, 0.52), (0.46, 0.43, 0.39)))
    ctx.fill()
    src(ctx, (0.4, 0.37, 0.33))
    ctx.set_line_width(3)
    for i in range(-6, 8):
        ctx.move_to(540 + i * 60, TRAIN_FLOOR)
        ctx.line_to(540 + i * 260, 2000)
    ctx.stroke()


def draw_train_bg(ctx, t):
    _coach_top(ctx)
    _coach_window(ctx, t)
    _coach_berth(ctx)


def draw_train_fg(ctx):
    for sx in (-1, 1):
        cx = 540 + sx * 640
        rrect(ctx, cx - 260, 1760, 520, 400, 60)
        fill_out(ctx, vgrad(1760, 1920, shade(BERTH, 0.8), shade(BERTH, 0.5)))


def draw_ceiling_stub(ctx, x, t, removed_for):
    """Fan mount plate; dangling wires once the fan is gone."""
    ellipse(ctx, x, 262, 50, 14)
    fill_out(ctx, STEEL_L, 4)
    if removed_for > 0:
        sw = 12 * math.sin(removed_for * 7) * math.exp(-removed_for * 0.8)
        for dx, c in ((-10, (0.85, 0.2, 0.15)), (10, (0.15, 0.15, 0.15))):
            ctx.move_to(x + dx, 265)
            quad_to(ctx, x + dx + sw, 300, x + dx * 2 + sw * 2, 330)
            src(ctx, c)
            ctx.set_line_width(7)
            ctx.stroke()


# ================================================================ home
def _room_wall(ctx):
    ctx.rectangle(-900, -900, 2880, 3720)
    src(ctx, vgrad(250, 1350, (0.98, 0.87, 0.68), (0.94, 0.77, 0.56)))
    ctx.fill()
    ctx.rectangle(-900, -900, 2880, 1150)
    src(ctx, (0.99, 0.94, 0.84))
    ctx.fill()
    limb(ctx, [(-900, 252), (1980, 252)], 14, (0.95, 0.80, 0.60), 4)
    limb(ctx, [(560, 258), (560, 300)], 8, STEEL_L, 3)
    ctx.arc(560, 312, 14, -1.3, 3.8)
    src(ctx, OUT)
    ctx.set_line_width(5)
    ctx.stroke()


def _room_window(ctx):
    rrect(ctx, 60, 440, 360, 460, 12)
    fill_out(ctx, (0.62, 0.38, 0.2), 5)
    ctx.rectangle(84, 464, 312, 412)
    src(ctx, vgrad(464, 876, (0.55, 0.82, 0.92), (0.98, 0.92, 0.72)))
    ctx.fill()
    ellipse(ctx, 330, 600, 70, 50)
    src(ctx, (0.35, 0.62, 0.38))
    ctx.fill()
    limb(ctx, [(240, 464), (240, 876)], 10, (0.62, 0.38, 0.2), 0)
    for cx, d in ((60, 1), (420, -1)):
        ctx.move_to(cx - 30 * d, 420)
        ctx.line_to(cx + 70 * d, 420)
        quad_to(ctx, cx + 30 * d, 700, cx + 55 * d, 930)
        ctx.line_to(cx - 30 * d, 930)
        ctx.close_path()
        fill_out(ctx, vgrad(420, 930, ORANGE, (0.85, 0.38, 0.12)))
    limb(ctx, [(20, 420), (460, 420)], 10, (0.5, 0.3, 0.15), 3)


def _room_calendar(ctx):
    rrect(ctx, 610, 470, 150, 200, 6)
    fill_out(ctx, WHITE, 4)
    ctx.rectangle(622, 482, 126, 80)
    src(ctx, vgrad(482, 562, (1, 0.7, 0.3), (0.95, 0.45, 0.25)))
    ctx.fill()
    ellipse(ctx, 685, 530, 20, 20)
    src(ctx, YELLOW)
    ctx.fill()
    src(ctx, (0.6, 0.6, 0.6))
    ctx.set_line_width(3)
    for r in range(4):
        for c in range(5):
            ctx.rectangle(626 + c * 24, 578 + r * 20, 14, 10)
    ctx.stroke()


def _room_floor(ctx):
    ctx.rectangle(-900, 1330, 2880, 40)
    src(ctx, TEAL)
    ctx.fill()
    ctx.rectangle(-900, 1370, 2880, HOME_FLOOR - 1370)
    src(ctx, (0.90, 0.70, 0.50))
    ctx.fill()
    ctx.rectangle(-900, HOME_FLOOR, 2880, 1400)
    src(ctx, vgrad(HOME_FLOOR, 2100, (0.82, 0.46, 0.28), (0.66, 0.34, 0.20)))
    ctx.fill()
    src(ctx, (0.62, 0.33, 0.20))
    ctx.set_line_width(3)
    for i in range(-8, 10):
        ctx.move_to(540 + i * 90, HOME_FLOOR)
        ctx.line_to(540 + i * 300, 2100)
    for yy in (1660, 1740, 1850, 1990):
        ctx.move_to(-900, yy)
        ctx.line_to(1980, yy)
    ctx.stroke()
    ellipse(ctx, 1010, 1560, 85, 95)
    fill_out(ctx, rgrad(980, 1520, 120, (0.86, 0.48, 0.28), (0.62, 0.30, 0.16)))
    ellipse(ctx, 1010, 1470, 40, 12)
    fill_out(ctx, (0.45, 0.2, 0.1), 4)


def draw_home_bg(ctx):
    _room_wall(ctx)
    _room_window(ctx)
    _room_calendar(ctx)
    _room_floor(ctx)


def draw_sunbeam(ctx, alpha=0.10):
    ctx.move_to(90, 470)
    ctx.line_to(400, 470)
    ctx.line_to(980, HOME_FLOOR + 200)
    ctx.line_to(420, HOME_FLOOR + 200)
    ctx.close_path()
    src(ctx, (1, 0.93, 0.6), alpha)
    ctx.fill()
