"""Character rigs: Arjun (full body, FK + IK arms), Nimi (bust), passengers."""
import math
from gfx import (OUT, SKIN, HAIR, SHIRT, SHIRT_D, STRIPE, PANTS, PANTS_D,
                 GAMCHA, TEAL, TEAL_D, TEAL_L, CREAM, ORANGE, YELLOW, WHITE,
                 ellipse, rrect, quad_to, src, fill_out, shade, rgrad, hgrad,
                 vgrad, limb, clamp, lerp, text)

L1, L2 = 150, 140          # upper arm, forearm
T1, T2 = 165, 170          # thigh, shin
SHX, SHY = 88, -200        # shoulder joint
HIPX = 38
HEAD_Y = -335

ARJUN_BASE = dict(
    x=540, y=1230, s=1.0, lean=0.0, bob=0.0, shake=0.0,
    head_tilt=0.0, head_turn=0.0, head_up=0.0,
    look_x=0.0, look_y=0.0, eye_open=1.0, eye_wide=1.0, lid=0.0, eye_curve=-1.0,
    brow_l=0.0, brow_r=0.0, brow_ang=0.0,
    mw=1.0, mo=0.0, mc=0.35, ms=0.0, teeth=0.0,
    al1=0.15, al2=-0.3, ar1=0.15, ar2=-0.3,
    ll1=0.08, ll2=0.0, lr1=0.08, lr2=0.0, thigh=1.0,
    ikl=0.0, ikr=0.0, iklx=0.0, ikly=0.0, ikrx=0.0, ikry=0.0,
    hair_wild=0.0, sweat=0.0, walk=0.0, rub=0.0, scratch=0.0, wave=0.0,
    hand_l="open", hand_r="open", sunglasses=0.0,
)

ARJUN_STYLE = dict(skin=SKIN, hair="spiky", mustache=True)
NIMI_STYLE = dict(skin=(0.64, 0.42, 0.28), hair="hat", mustache=False, glasses=True)
AUNTIE_STYLE = dict(skin=(0.76, 0.52, 0.36), hair="bun", mustache=False,
                    bindi=True, earrings=True, rx=94, ry=104)


# ================================================================ kinematics
def _dir(th, side):
    return side * math.sin(th), math.cos(th)


def _ang(dx, dy, side):
    return math.atan2(side * dx, dy)


def _near(a, ref):
    while a - ref > math.pi:
        a -= 2 * math.pi
    while a - ref < -math.pi:
        a += 2 * math.pi
    return a


def _ik(sx, sy, tx, ty, side):
    dx, dy = tx - sx, ty - sy
    d = clamp(math.hypot(dx, dy), abs(L1 - L2) + 1, L1 + L2 - 1)
    th_t = _ang(dx, dy, side)
    a = math.acos(clamp((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d), -1, 1))
    best = None
    for th1 in (th_t + a, th_t - a):
        ux, uy = _dir(th1, side)
        ex, ey = sx + L1 * ux, sy + L1 * uy
        if best is None or side * ex > best[0]:
            best = (side * ex, th1, ex, ey)
    _, th1, ex, ey = best
    phi = _ang(tx - ex, ty - ey, side)
    return th1, _near(phi - th1, 0)


def solve(p, t):
    """Joint positions in body-local (unscaled) coordinates."""
    phase = p["x"] / 38.0
    J = {}
    for side, k in ((-1, "l"), (1, "r")):
        a1, a2 = p["a%s1" % k], p["a%s2" % k]
        a1 += p["walk"] * 0.22 * math.sin(phase) * side * (1 - p["ik" + k])
        a2 += p["rub"] * 0.28 * math.sin(t * 20 + side)
        if k == "r":
            a2 += p["scratch"] * 0.35 * math.sin(t * 24)
            a1 += p["wave"] * 0.2 * math.sin(t * 14)
        w = p["ik" + k]
        if w > 0:
            i1, i2 = _ik(side * SHX, SHY, p["ik%sx" % k], p["ik%sy" % k], side)
            a1 = lerp(a1, _near(i1, a1), w)
            a2 = lerp(a2, _near(i2, a2), w)
        sx, sy = side * SHX, SHY
        ux, uy = _dir(a1, side)
        ex, ey = sx + L1 * ux, sy + L1 * uy
        vx, vy = _dir(a1 + a2, side)
        J["arm" + k] = ((sx, sy), (ex, ey), (ex + L2 * vx, ey + L2 * vy), a1 + a2)

        lift = p["walk"] * max(0.0, math.sin(phase) * -side)
        b1 = p["l%s1" % k] + 0.3 * lift
        b2 = p["l%s2" % k] - 0.35 * lift
        hx, hy = side * HIPX, 0.0
        tl = T1 * p["thigh"] * (1 - 0.5 * lift)
        ux, uy = _dir(b1, side)
        kx, ky = hx + tl * ux, hy + tl * uy
        vx, vy = _dir(b1 + b2, side)
        J["leg" + k] = ((hx, hy), (kx, ky), (kx + T2 * vx, ky + T2 * vy))
    return J


def _origin(p, t):
    shake = p["shake"] * 7 * math.sin(t * 63)
    walk_bob = -p["walk"] * 9 * abs(math.sin(p["x"] / 38.0))
    return p["x"] + shake, p["y"] + p["bob"] + walk_bob


def to_world(p, t, pt):
    ox, oy = _origin(p, t)
    c, s = math.cos(p["lean"]), math.sin(p["lean"])
    x, y = pt[0] * p["s"], pt[1] * p["s"]
    return ox + c * x - s * y, oy + s * x + c * y


def to_local(p, t, wx, wy):
    ox, oy = _origin(p, t)
    c, s = math.cos(p["lean"]), math.sin(p["lean"])
    x, y = wx - ox, wy - oy
    return (c * x + s * y) / p["s"], (-s * x + c * y) / p["s"]


def set_ik(p, t, side, wx, wy, weight=1.0):
    """Aim a hand at a world point (mutates the per-frame pose copy)."""
    k = "l" if side < 0 else "r"
    p["ik%sx" % k], p["ik%sy" % k] = to_local(p, t, wx, wy)
    p["ik" + k] = weight


def hand_world(p, t, side):
    J = solve(p, t)
    return to_world(p, t, J["arml" if side < 0 else "armr"][2])


def head_world(p, t):
    return to_world(p, t, (0, HEAD_Y))


# ================================================================ head
def _eyes(ctx, p, st, sh, up):
    wide, opn = p["eye_wide"], p["eye_open"]
    for side in (-1, 1):
        ex, ey = side * 40 + sh, -8 + up
        if opn < 0.14:
            ctx.move_to(ex - 21, ey + 2)
            quad_to(ctx, ex, ey + 2 + p["eye_curve"] * 13, ex + 21, ey + 2)
            src(ctx, OUT)
            ctx.set_line_width(6)
            ctx.stroke()
            continue
        rx, ry = 23 * wide, 29 * wide * opn
        ellipse(ctx, ex, ey, rx, ry)
        src(ctx, WHITE)
        ctx.fill_preserve()
        ctx.save()
        ctx.clip()
        px = ex + p["look_x"] * 10 * wide
        py = ey + p["look_y"] * 12 * wide
        ellipse(ctx, px, py, 14 * wide, 14 * wide)
        src(ctx, (0.30, 0.17, 0.10))
        ctx.fill()
        ellipse(ctx, px, py, 8 * wide, 8 * wide)
        src(ctx, (0.05, 0.03, 0.02))
        ctx.fill()
        ellipse(ctx, px - 4 * wide, py - 5 * wide, 4.5 * wide, 4.5 * wide)
        src(ctx, WHITE)
        ctx.fill()
        if p["lid"] > 0.01:
            lid_y = ey - ry + p["lid"] * 1.25 * ry
            slope = side * p["brow_ang"] * 6
            ctx.move_to(ex - 40, ey - 60)
            ctx.line_to(ex + 40, ey - 60)
            ctx.line_to(ex + 40, lid_y - slope)
            ctx.line_to(ex - 40, lid_y + slope)
            ctx.close_path()
            src(ctx, shade(st["skin"], 0.95))
            ctx.fill()
            ctx.move_to(ex - 40, lid_y + slope)
            ctx.line_to(ex + 40, lid_y - slope)
            src(ctx, OUT)
            ctx.set_line_width(6)
            ctx.stroke()
        ctx.restore()
        ellipse(ctx, ex, ey, rx, ry)
        src(ctx, OUT)
        ctx.set_line_width(4.5)
        ctx.stroke()
        if st.get("glasses"):
            ellipse(ctx, ex, ey, 33, 33)
            src(ctx, (0.15, 0.15, 0.2))
            ctx.set_line_width(6)
            ctx.stroke()
    if st.get("glasses"):
        ctx.move_to(-7 + sh, -10 + up)
        ctx.line_to(7 + sh, -10 + up)
        ctx.stroke()


def _brows(ctx, p, sh, up):
    ctx.set_line_cap(1)
    for side, raise_ in ((-1, p["brow_l"]), (1, p["brow_r"])):
        bx, by = side * 42 + sh, -54 + up - raise_ * 15
        ang = p["brow_ang"]
        ctx.move_to(bx - side * 21, by + ang * 11)
        quad_to(ctx, bx, by - 9, bx + side * 22, by - ang * 3 + 2)
        src(ctx, HAIR)
        ctx.set_line_width(11)
        ctx.stroke()


def _mouth_path(ctx, lx, ly, rx, ry, mx, top, low):
    ctx.move_to(lx, ly)
    quad_to(ctx, mx, top, rx, ry)
    quad_to(ctx, mx, low, lx, ly)
    ctx.close_path()


def _mouth(ctx, p, sh, up):
    mx, my = sh * 1.2, 66 + up * 0.3
    w, o, c, k = 30 * p["mw"], p["mo"], p["mc"], p["ms"]
    lx, ly = mx - w, my - c * 12 - k * 9
    rx, ry = mx + w, my - c * 12 + k * 9
    if o < 0.06:
        ctx.move_to(lx, ly)
        quad_to(ctx, mx, my + c * 16, rx, ry)
        src(ctx, OUT)
        ctx.set_line_width(6)
        ctx.set_line_cap(1)
        ctx.stroke()
        return
    top, low = my - c * 3 - o * 6, my + o * 58 + c * 12 + 4
    _mouth_path(ctx, lx, ly, rx, ry, mx, top, low)
    src(ctx, (0.42, 0.10, 0.10))
    ctx.fill_preserve()
    ctx.save()
    ctx.clip()
    ellipse(ctx, mx, low - 4, w * 0.6, 14 + o * 10)
    src(ctx, (0.93, 0.45, 0.45))
    ctx.fill()
    if p["teeth"] > 0.5 or (c > 0.4 and o > 0.08):
        ctx.rectangle(mx - w, my - c * 14 - 20, 2 * w, 30)
        src(ctx, WHITE)
        ctx.fill()
    ctx.restore()
    _mouth_path(ctx, lx, ly, rx, ry, mx, top, low)
    src(ctx, OUT)
    ctx.set_line_width(5)
    ctx.stroke()


def _hair(ctx, p, t, st, rx, ry, sh, up):
    kind = st["hair"]
    if kind == "spiky":
        wild = p["hair_wild"]
        n = 13
        for i in range(n):
            a = math.radians(192 + 156 * i / (n - 1))
            if i % 2:
                r = rx + 24 + wild * 34 * (0.6 + 0.4 * math.sin(t * 41 + i * 1.7))
                a += wild * 0.14 * math.sin(t * 33 + i)
            else:
                r = rx + 5
            x, y = r * math.cos(a), r * math.sin(a) * ry / rx
            (ctx.move_to if i == 0 else ctx.line_to)(x, y)
        hs = sh * 0.5
        for x, y in ((rx * 0.96, -22), (64 + hs, -52 + up), (28 + hs, -42 + up),
                     (-4 + hs, -64 + up), (-40 + hs, -46 + up), (-rx * 0.96, -22)):
            ctx.line_to(x, y)
        ctx.close_path()
        fill_out(ctx, HAIR)
    elif kind == "bun":
        ctx.arc(0, 0, rx + 4, math.radians(185), math.radians(355))
        ctx.line_to(rx * 0.9, -10)
        quad_to(ctx, 45 + sh * 0.4, -62, sh * 0.4, -70)
        quad_to(ctx, -45 + sh * 0.4, -62, -rx * 0.9, -10)
        ctx.close_path()
        fill_out(ctx, HAIR)
    elif kind == "hat":
        ctx.save()
        ctx.translate(0, -30)
        ctx.scale(1, 0.9)
        ctx.arc(0, 0, rx + 10, math.pi, 2 * math.pi)
        ctx.restore()
        ctx.close_path()
        fill_out(ctx, rgrad(-30, -90, 150, (1, 0.9, 0.45), (0.95, 0.68, 0.12)))
        ctx.rectangle(-rx - 6, -52, 2 * rx + 12, 16)
        src(ctx, TEAL)
        ctx.fill()
        ellipse(ctx, 0, -30, rx + 26, 15)
        fill_out(ctx, (0.97, 0.74, 0.18))


def _face_extras(ctx, p, st, rx, sh, up):
    skin = st["skin"]
    ctx.move_to(sh * 1.3 - 8, 30 + up * 0.5)
    quad_to(ctx, sh * 1.3 + 2, 40 + up * 0.5, sh * 1.3 + 12, 28 + up * 0.5)
    src(ctx, shade(skin, 0.62))
    ctx.set_line_width(5)
    ctx.set_line_cap(1)
    ctx.stroke()
    if st.get("mustache"):
        mx, my = sh * 1.25, 47 + up * 0.4
        ctx.move_to(mx - 30, my + 6)
        quad_to(ctx, mx - 15, my - 8, mx, my - 1)
        quad_to(ctx, mx + 15, my - 8, mx + 30, my + 6)
        src(ctx, HAIR)
        ctx.set_line_width(7)
        ctx.stroke()
    if st.get("bindi"):
        ellipse(ctx, sh, -40 + up, 6, 6)
        src(ctx, (0.85, 0.1, 0.12))
        ctx.fill()
    if p["sweat"] > 0.02:
        s = p["sweat"]
        x, y = rx * 0.72 + sh * 0.3, -46
        ctx.move_to(x, y - 22 * s)
        ctx.curve_to(x + 12 * s, y, x + 12 * s, y + 14 * s, x, y + 14 * s)
        ctx.curve_to(x - 12 * s, y + 14 * s, x - 12 * s, y, x, y - 22 * s)
        fill_out(ctx, (0.75, 0.92, 1.0), 3)
    if p["sunglasses"] > 0.5:
        for side in (-1, 1):
            rrect(ctx, side * 40 + sh - 30, -26 + up, 60, 36, 12)
            fill_out(ctx, (0.1, 0.1, 0.12), 4)
        ctx.move_to(-10 + sh, -14 + up)
        ctx.line_to(10 + sh, -14 + up)
        ctx.set_line_width(6)
        ctx.stroke()


def draw_head(ctx, p, t, st):
    rx, ry = st.get("rx", 100), st.get("ry", 110)
    turn = p["head_turn"]
    sh, up = turn * 26, -p["head_up"] * 14
    skin = st["skin"]
    if st["hair"] == "bun":
        ellipse(ctx, -sh * 0.3 - 20, -ry + 10, 44, 38)
        fill_out(ctx, HAIR)
    for side in (-1, 1):
        ex = side * (rx - 4) + turn * 12
        ellipse(ctx, ex, 10 + up * 0.3, 17, 24)
        fill_out(ctx, shade(skin, 0.93))
        if st.get("earrings"):
            ellipse(ctx, ex, 40, 7, 7)
            fill_out(ctx, YELLOW, 3)
    ellipse(ctx, 0, 0, rx, ry)
    fill_out(ctx, rgrad(-25, -35, rx * 1.3, shade(skin, 1.12), shade(skin, 0.86)))
    for side in (-1, 1):
        ellipse(ctx, side * 57 + sh, 34 + up, 17, 10)
        src(ctx, (0.95, 0.42, 0.40), 0.28)
        ctx.fill()
    _eyes(ctx, p, st, sh, up)
    if st["hair"] != "hat":
        _brows(ctx, p, sh, up)
    _mouth(ctx, p, sh, up)
    _hair(ctx, p, t, st, rx, ry, sh, up)
    if st["hair"] == "hat":
        _brows(ctx, p, sh, up)
    _face_extras(ctx, p, st, rx, sh, up)


# ================================================================ body
def draw_hand(ctx, x, y, kind="open", skin=SKIN):
    if kind == "thumb":
        rrect(ctx, x - 7, y - 46, 17, 34, 8)
        fill_out(ctx, skin, 4)
    ellipse(ctx, x, y, 25, 24)
    fill_out(ctx, rgrad(x - 8, y - 8, 30, shade(skin, 1.1), shade(skin, 0.9)), 4.5)
    if kind in ("fist", "thumb"):
        ctx.set_line_width(3.5)
        for dy in (-6, 4):
            ctx.move_to(x - 10, y + dy)
            ctx.line_to(x + 8, y + dy)
        src(ctx, shade(skin, 0.6))
        ctx.stroke()


def _torso(ctx):
    ctx.move_to(-SHX + 4, -214)
    quad_to(ctx, 0, -232, SHX - 4, -214)
    quad_to(ctx, SHX + 10, -205, SHX + 6, -168)
    quad_to(ctx, 80, -60, 70, 8)
    ctx.line_to(-70, 8)
    quad_to(ctx, -80, -60, -SHX - 6, -168)
    quad_to(ctx, -SHX - 10, -205, -SHX + 4, -214)
    ctx.close_path()


def _shirt(ctx):
    _torso(ctx)
    fill_out(ctx, hgrad(-90, 90, SHIRT, SHIRT_D))
    ctx.save()
    _torso(ctx)
    ctx.clip()
    for x in range(-90, 100, 36):
        ctx.move_to(x, -240)
        ctx.line_to(x, 20)
    src(ctx, STRIPE, 0.55)
    ctx.set_line_width(9)
    ctx.stroke()
    ctx.move_to(-28, -224)
    ctx.line_to(0, -170)
    ctx.line_to(28, -224)
    ctx.close_path()
    src(ctx, shade(SKIN, 0.9))
    ctx.fill()
    ctx.restore()
    rrect(ctx, 24, -150, 42, 44, 6)
    src(ctx, SHIRT_D)
    ctx.fill_preserve()
    src(ctx, OUT)
    ctx.set_line_width(3.5)
    ctx.stroke()
    _torso(ctx)
    src(ctx, OUT)
    ctx.set_line_width(5)
    ctx.stroke()


def _gamcha(ctx):
    ctx.set_line_cap(1)
    for w, c in ((40, OUT), (30, GAMCHA)):
        ctx.move_to(-70, -212)
        quad_to(ctx, 0, -176, 70, -212)
        src(ctx, c)
        ctx.set_line_width(w)
        ctx.stroke()
    limb(ctx, [(-50, -200), (-60, -80)], 32, GAMCHA)
    ctx.set_line_width(4)
    src(ctx, CREAM, 0.8)
    for y in (-170, -140, -110):
        ctx.move_to(-72, y)
        ctx.line_to(-42, y + 2)
    ctx.stroke()


def _draw_body(ctx, J):
    for k in ("l", "r"):
        limb(ctx, list(J["leg" + k]), 60, PANTS)
    for k, side in (("l", -1), ("r", 1)):
        ax, ay = J["leg" + k][2]
        ellipse(ctx, ax + side * 10, ay + 14, 36, 16)
        fill_out(ctx, (0.30, 0.17, 0.10), 4)
    rrect(ctx, -74, -14, 148, 52, 22)
    fill_out(ctx, hgrad(-74, 74, PANTS, PANTS_D))
    rrect(ctx, -22, -250, 44, 60, 12)
    fill_out(ctx, shade(SKIN, 0.85))
    _shirt(ctx)
    _gamcha(ctx)


def _draw_arms(ctx, p, J):
    for k in ("l", "r"):
        s, e, h, _ = J["arm" + k]
        limb(ctx, [s, e, h], 34, SKIN)
        mx, my = lerp(s[0], e[0], 0.45), lerp(s[1], e[1], 0.45)
        limb(ctx, [s, (mx, my)], 50, SHIRT)
    for k in ("l", "r"):
        h = J["arm" + k][2]
        draw_hand(ctx, h[0], h[1], p["hand_" + k])


def draw_arjun(ctx, p, t, hold=None, style=ARJUN_STYLE):
    J = solve(p, t)
    ox, oy = _origin(p, t)

    def xf():
        ctx.translate(ox, oy)
        ctx.rotate(p["lean"])
        ctx.scale(p["s"], p["s"])

    ctx.save()
    xf()
    _draw_body(ctx, J)
    ctx.save()
    ctx.translate(0, HEAD_Y)
    ctx.rotate(p["head_tilt"])
    draw_head(ctx, p, t, style)
    ctx.restore()
    ctx.restore()
    if hold:
        hold()
    ctx.save()
    xf()
    _draw_arms(ctx, p, J)
    ctx.restore()


# ================================================================ Nimi
def draw_nimi_bust(ctx, x, y, s, t):
    """Electrician friend, waist up, thumbs-up. (x, y) = chest centre."""
    p = dict(ARJUN_BASE, mc=0.9, mo=0.28, teeth=1.0, brow_l=0.5, brow_r=0.5,
             look_x=0.2, head_tilt=0.08 * math.sin(t * 5))
    skin = NIMI_STYLE["skin"]
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-110, 40)
    quad_to(ctx, -118, -120, 0, -125)
    quad_to(ctx, 118, -120, 110, 40)
    ctx.close_path()
    fill_out(ctx, hgrad(-110, 110, TEAL, TEAL_D))
    limb(ctx, [(-60, -118), (-50, 40)], 16, ORANGE, 3)
    limb(ctx, [(60, -118), (50, 40)], 16, ORANGE, 3)
    rrect(ctx, -40, -40, 80, 60, 8)
    fill_out(ctx, TEAL_D, 4)
    limb(ctx, [(-18, -60), (-18, -30)], 8, (0.9, 0.2, 0.15), 3)
    limb(ctx, [(14, -58), (14, -30)], 8, YELLOW, 3)
    ctx.save()
    ctx.translate(0, -225)
    ctx.rotate(p["head_tilt"])
    draw_head(ctx, p, t, NIMI_STYLE)
    ctx.restore()
    limb(ctx, [(95, -95), (150, -30), (140, -140)], 34, skin)
    limb(ctx, [(95, -95), (125, -60)], 52, TEAL)
    draw_hand(ctx, 140, -140, "thumb", skin)
    ctx.restore()


# ================================================================ passengers
def _auntie_body(ctx, sk):
    ctx.move_to(-78, -10)
    ctx.line_to(78, -10)
    ctx.line_to(95, 225)
    ctx.line_to(-95, 225)
    ctx.close_path()
    fill_out(ctx, vgrad(0, 225, TEAL, TEAL_D))
    ctx.rectangle(-95, 200, 190, 22)
    src(ctx, ORANGE)
    ctx.fill()
    for side in (-1, 1):
        ellipse(ctx, side * 38, 232, 30, 12)
        fill_out(ctx, (0.55, 0.18, 0.14), 4)
    _torso(ctx)
    fill_out(ctx, hgrad(-90, 90, TEAL_L, TEAL))
    ctx.save()
    _torso(ctx)
    ctx.clip()
    ctx.move_to(-95, -230)
    ctx.line_to(-40, -230)
    ctx.line_to(95, -20)
    ctx.line_to(95, 30)
    ctx.close_path()
    src(ctx, ORANGE)
    ctx.fill()
    ctx.restore()
    _torso(ctx)
    src(ctx, OUT)
    ctx.set_line_width(5)
    ctx.stroke()
    limb(ctx, [(-88, -190), (-70, -60), (5, -20)], 32, sk)
    limb(ctx, [(88, -190), (72, -60), (-5, -30)], 32, sk)
    ellipse(ctx, 0, -28, 26, 8)
    src(ctx, YELLOW)
    ctx.set_line_width(5)
    ctx.stroke()
    draw_hand(ctx, 0, -25, "open", sk)
    rrect(ctx, -22, -250, 44, 60, 12)
    fill_out(ctx, shade(sk, 0.85))


def draw_auntie(ctx, x, y, t):
    """Sleeping lady in a turquoise saree, seated; pelvis at (x, y)."""
    sk = AUNTIE_STYLE["skin"]
    ctx.save()
    ctx.translate(x, y)
    _auntie_body(ctx, sk)
    p = dict(ARJUN_BASE, eye_open=0.0, eye_curve=1.0,
             mo=0.12 + 0.08 * math.sin(t * 2.2), mc=0.0, mw=0.45,
             head_tilt=0.32, brow_l=-0.2, brow_r=-0.2)
    ctx.save()
    ctx.translate(18, HEAD_Y + 12)
    ctx.rotate(p["head_tilt"])
    draw_head(ctx, p, t, AUNTIE_STYLE)
    ctx.restore()
    ctx.restore()
    for i in range(3):
        u = (t * 0.55 + i / 3) % 1
        text(ctx, "z", x + 90 + u * 70 + 10 * math.sin(u * 7),
             y - 420 - u * 150, 34 + 26 * u, TEAL_D, alpha=math.sin(u * math.pi))


def _newspaper(ctx):
    rrect(ctx, -170, -165, 340, 300, 6)
    fill_out(ctx, vgrad(-165, 135, (0.97, 0.95, 0.88), (0.86, 0.84, 0.77)))
    ctx.rectangle(-150, -148, 300, 40)
    src(ctx, (0.18, 0.18, 0.2))
    ctx.fill()
    text(ctx, "DAILY NEWS", 0, -118, 30, WHITE)
    ctx.rectangle(-150, -92, 130, 96)
    src(ctx, (0.62, 0.66, 0.68))
    ctx.fill()
    src(ctx, (0.45, 0.45, 0.48))
    ctx.set_line_width(6)
    for i in range(9):
        yy = -84 + i * 22
        ctx.move_to(0 if yy < 10 else -150, yy)
        ctx.line_to(150 - (i % 3) * 20, yy)
    ctx.stroke()
    ctx.move_to(0, -165)
    ctx.line_to(0, 135)
    src(ctx, (0.7, 0.68, 0.62))
    ctx.set_line_width(3)
    ctx.stroke()


def draw_uncle(ctx, x, y, t, flip=0.0):
    """Uncle hidden behind a newspaper, seated; pelvis at (x, y)."""
    ctx.save()
    ctx.translate(x, y)
    limb(ctx, [(-35, 0), (-40, 215)], 58, (0.45, 0.42, 0.40))
    limb(ctx, [(35, 0), (-30, 60), (-20, 205)], 58, (0.50, 0.47, 0.44))
    ellipse(ctx, -48, 232, 34, 14)
    fill_out(ctx, (0.25, 0.15, 0.1), 4)
    ellipse(ctx, -28, 222, 34, 14)
    fill_out(ctx, (0.25, 0.15, 0.1), 4)
    _torso(ctx)
    fill_out(ctx, hgrad(-90, 90, (0.95, 0.95, 0.9), (0.80, 0.82, 0.80)))
    ellipse(ctx, 0, HEAD_Y - 30, 92, 70)
    fill_out(ctx, rgrad(-20, HEAD_Y - 70, 110, (0.82, 0.60, 0.44), (0.66, 0.44, 0.30)))
    for side in (-1, 1):
        ellipse(ctx, side * 80, HEAD_Y - 10, 22, 30)
        fill_out(ctx, (0.85, 0.85, 0.85), 4)
    ctx.save()
    ctx.translate(0, -250)
    ctx.rotate(0.04 * math.sin(t * 1.3) + flip)
    _newspaper(ctx)
    for side in (-1, 1):
        draw_hand(ctx, side * 168, 0, "open", (0.74, 0.52, 0.36))
    ctx.restore()
    ctx.restore()
