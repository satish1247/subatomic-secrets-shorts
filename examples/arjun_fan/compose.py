"""Per-frame composition: world layers, screen overlays, transition, post FX."""
import math
import os
import wave
import cairo
import numpy as np
from gfx import (W, H, FPS, OUT, ORANGE, TEAL, TEAL_D, WHITE, YELLOW,
                 seg, lerp, ease_back, ease_out, soft_shadow, src, text)
from characters import (ARJUN_BASE, draw_arjun, draw_auntie, draw_uncle, set_ik,
                        draw_nimi_bust, draw_hand, hand_world, head_world)
from props import (draw_fan, draw_wire, draw_plug, draw_phone, draw_switchboard,
                   draw_stool, draw_bulb, draw_puff, thought_bubble, speech_bubble)
from backgrounds import (draw_train_bg, draw_train_fg, draw_ceiling_stub,
                         draw_home_bg, draw_sunbeam, HOME_FLOOR, TRAIN_FLOOR)
import story as S

HERE = os.path.dirname(os.path.abspath(__file__))
_CACHE = {}
WIRE_REST = (840, 1320)
BLACK = (0.15, 0.15, 0.15)


# ---------------------------------------------------------------- helpers
def speech_env(t):
    if "env" not in _CACHE:
        with wave.open(os.path.join(HERE, "audio", "line_fast.wav")) as wf:
            sr = wf.getframerate()
            a = np.frombuffer(wf.readframes(wf.getnframes()), np.int16) / 32768.0
        hop = sr // FPS
        rms = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a), hop)])
        _CACHE["env"] = np.clip(rms / (rms.max() * 0.6), 0, 1)
    env = _CACHE["env"]
    i = int((t - S.T_SPEECH) * FPS)
    return float(env[i]) if 0 <= i < len(env) else 0.0


def to_screen(cam, x, y):
    _, cx, cy, z, _ = cam
    return W / 2 + (x - cx) * z, H / 2 + (y - cy) * z


# ---------------------------------------------------------------- train
def _wind(ctx, t, fan):
    a = seg(t, 10.6, 10.75) * (1 - seg(t, 11.3, 11.5))
    if a <= 0:
        return
    ctx.set_line_cap(1)
    for i in range(7):
        u = (t * 3 + i / 7) % 1
        x, y = fan[0] - 150 + i * 50, fan[1] + u * 180
        ctx.move_to(x, y + 60)
        ctx.curve_to(x + 20, y + 110, x - 20, y + 150, x + 5, y + 200)
        src(ctx, WHITE, 0.6 * a * (1 - u))
        ctx.set_line_width(7)
        ctx.stroke()


def draw_train(ctx, t):
    p, fan = S.train_pose(t)
    draw_train_bg(ctx, t)
    draw_ceiling_stub(ctx, S.CEIL_FAN[0], t, t - S.T_POP)
    attached = t < S.T_POP
    if attached:
        draw_fan(ctx, fan[0], fan[1], 1.0, S.fan_angle(t), S.fan_speed(t), attached=True)
    draw_auntie(ctx, 200, 1235, t)
    draw_uncle(ctx, 880, 1235, t, 0.08 * math.sin(seg(t, 6.15, 6.5) * math.pi))
    feet_y = TRAIN_FLOOR if p["y"] > 1000 else 1250
    soft_shadow(ctx, p["x"], feet_y + 10, 130, 22)

    def hold():
        if not attached:
            dt = t - S.T_POP
            tilt = 0.12 * math.sin(dt * 9) * math.exp(-dt * 1.5)
            draw_fan(ctx, fan[0], fan[1], 1.0, S.fan_angle(t), S.fan_speed(t), tilt=tilt)
    draw_arjun(ctx, p, t, hold)
    _wind(ctx, t, fan)
    draw_puff(ctx, S.CEIL_FAN[0], 300, seg(t, S.T_POP, S.T_POP + 0.7))
    draw_train_fg(ctx)
    return p


# ---------------------------------------------------------------- home
def _plug_pos(t, p):
    floor = (395, HOME_FLOOR - 10)
    if 19.0 <= t < 23.75:
        hx, hy = hand_world(p, t, -1)
        return hx, hy - 30, True
    if t >= 23.75:
        u = ease_out(seg(t, 23.75, 24.1))
        hx, hy = hand_world(S.HOME.at(23.74), 23.74, -1)
        return lerp(hx, floor[0], u), lerp(hy, floor[1], u), False
    return floor[0], floor[1], False


def _red_wire_end(t, p):
    if 22.6 <= t < 23.75:
        return hand_world(p, t, 1)
    if t >= 23.75:
        hx, hy = _home_pose(23.74)[0], None
        hx, hy = hand_world(hx, 23.74, 1)
        u = ease_out(seg(t, 23.75, 24.2))
        return lerp(hx, WIRE_REST[0], u), lerp(hy, WIRE_REST[1], u)
    return WIRE_REST


def _home_pose(t):
    p, fan = S.home_pose(t)
    if 22.6 <= t < 23.75:
        lx, ly = hand_world(p, t, -1)
        u = ease_out(seg(t, 22.6, 22.95))
        twist = 10 * math.sin(t * 30) * seg(t, 22.95, 23.0) * (1 - seg(t, 23.15, 23.2))
        set_ik(p, t, 1, lerp(WIRE_REST[0], lx + 45, u),
               lerp(WIRE_REST[1], ly + twist, u), p["ikr"])
    if S.T_SPEECH <= t < S.T_SPEECH + S.SPEECH_LEN:
        e = speech_env(t)
        p["mo"] = 0.06 + 0.55 * e
        p["mw"] = 0.85 + 0.15 * e
        p["brow_l"] = p["brow_r"] = 0.5 + 0.3 * e
    return p, fan


def _home_props(ctx, t, p, fan, placed, plug):
    draw_home_bg(ctx)
    draw_switchboard(ctx, 870, 1000)
    draw_wire(ctx, 885, 1110, 895, 1330, 10, BLACK)
    draw_stool(ctx, S.STOOL_FAN[0], 1330, HOME_FLOOR)
    if placed:
        soft_shadow(ctx, S.STOOL_FAN[0], 1340, 110, 18, 0.2)
        draw_fan(ctx, fan[0], fan[1], 1.0, 0.7, 0.0, label=True)
        if not plug[2]:
            draw_wire(ctx, fan[0] + 50, fan[1] - 20, plug[0], plug[1], 120, BLACK, 7)
            draw_plug(ctx, plug[0], plug[1])
    soft_shadow(ctx, p["x"], HOME_FLOOR + 10, 130, 22)
    red = _red_wire_end(t, p)
    draw_wire(ctx, 855, 1110, red[0], red[1], 30, (0.85, 0.2, 0.15))


def draw_home(ctx, t):
    p, fan = _home_pose(t)
    placed = t >= 16.45
    plug = _plug_pos(t, p)
    _home_props(ctx, t, p, fan, placed, plug)

    def hold():
        if not placed:
            draw_fan(ctx, fan[0], fan[1], 1.0, 0.7, 0.0, label=True)
    draw_arjun(ctx, p, t, hold)
    if plug[2]:
        draw_wire(ctx, fan[0] + 50, fan[1] - 20, plug[0], plug[1], 160, BLACK, 7)
        draw_plug(ctx, plug[0], plug[1])
        draw_hand(ctx, *hand_world(p, t, -1), "fist")
    if 22.6 <= t < 23.75:
        draw_hand(ctx, *hand_world(p, t, 1), "fist")
    if t >= 25.2:
        hx, hy = hand_world(p, t, 1)
        draw_phone(ctx, hx - 12, hy - 20, -0.25, seg(t, 25.3, 25.5))
        draw_hand(ctx, hx, hy, "fist")
    draw_sunbeam(ctx, 0.08)
    return p


# ---------------------------------------------------------------- overlays
def _pop(t, a, fade_a=None, fade_b=None):
    if t < a:
        return 0.0
    v = ease_back(seg(t, a, a + 0.25))
    if fade_a is not None:
        v *= 1 - ease_out(seg(t, fade_a, fade_b))
    return v


def _dream_content(ctx, t, x, y):
    ctx.rectangle(x - 400, y - 300, 800, 600)
    src(ctx, (0.75, 0.93, 0.95))
    ctx.fill()
    ctx.save()
    ctx.translate(x, y + 30)
    ctx.scale(0.56, 0.56)
    ctx.translate(-540, -960)
    draw_fan(ctx, 540, 640, 1.0, t * 16, 2.5, attached=True)
    ctx.rectangle(330, 1180, 420, 90)
    src(ctx, ORANGE)
    ctx.fill()
    mini = dict(ARJUN_BASE, x=540, y=1180, thigh=0.3, ll1=0.3, lr1=0.3,
                al1=2.6, al2=2.3, ar1=2.6, ar2=2.3, sunglasses=1, mc=1, mo=0.25,
                teeth=1, hair_wild=0.7, head_tilt=0.1)
    draw_arjun(ctx, mini, t)
    ctx.restore()
    for i in range(5):
        u = (t * 1.5 + i / 5) % 1
        ctx.move_to(x - 120 + i * 60, y - 90 + u * 60)
        ctx.line_to(x - 110 + i * 60, y - 50 + u * 60)
        src(ctx, WHITE, 0.8 * (1 - u))
        ctx.set_line_width(5)
        ctx.stroke()


def _question_marks(ctx, t, hx, hy):
    for i, t0 in enumerate((21.25, 21.5, 21.75)):
        k = ease_back(seg(t, t0, t0 + 0.2))
        if k <= 0.01:
            continue
        x = hx - 230 + i * 230
        y = hy - 330 - (i % 2) * 60 + 8 * math.sin(t * 6 + i)
        text(ctx, "?", x + 4, y + 4, 150 * k, OUT)
        text(ctx, "?", x, y, 150 * k, ORANGE)


def _nimi_content(ctx, t):
    ctx.rectangle(150, 150, 800, 560)
    src(ctx, (1.0, 0.96, 0.85))
    ctx.fill()
    draw_nimi_bust(ctx, 460, 650, 0.92, t)
    text(ctx, "Nimi", 760, 450, 66, TEAL_D)
    text(ctx, "electrician", 760, 498, 32, ORANGE)


def overlays(ctx, t, cam, p):
    hx, hy = to_screen(cam, *head_world(p, t))
    if 7.8 < t < 9.6:
        def lucky():
            text(ctx, "Today is my", 540, 415, 64, OUT)
            text(ctx, "lucky day!", 540, 492, 64, ORANGE)
        thought_bubble(ctx, 540, 440, 820, 340, (hx + 160, hy - 250),
                       _pop(t, S.T_THOUGHT - 0.1, 9.35, 9.55), lucky)
    if 17.3 < t < 19.0:
        thought_bubble(ctx, 540, 430, 800, 560, (hx + 60, hy - 200),
                       _pop(t, 17.35, 18.75, 18.95), lambda: _dream_content(ctx, t, 540, 430))
    if 21.2 < t < 22.2:
        _question_marks(ctx, t, hx, hy)
    if 23.7 < t < 24.35:
        k = ease_back(seg(t, 23.7, 23.9)) * (1 - seg(t, 24.15, 24.35))
        draw_bulb(ctx, hx + 20, hy - 360, 1.1 * k, 0.5 + 0.5 * math.sin(t * 20))
    if 24.1 < t < 25.0:
        thought_bubble(ctx, 540, 430, 800, 500, (hx + 40, hy - 240), _pop(t, 24.1),
                       lambda: _nimi_content(ctx, t))
    _call_overlays(ctx, t, cam, p, hx, hy)


def _call_overlays(ctx, t, cam, p, hx, hy):
    if 25.5 < t < 25.95:
        px, py = to_screen(cam, *hand_world(p, t, 1))
        for i in range(3):
            u = (t * 2.5 + i / 3) % 1
            ctx.arc(px + 40, py - 40, 40 + 70 * u, -1.2, 0.3)
            src(ctx, TEAL, 1 - u)
            ctx.set_line_width(8)
            ctx.stroke()
        text(ctx, "ring ring!", min(px + 20, W - 170), py - 250, 50, TEAL_D)
    if S.T_SPEECH - 0.05 < t < 29.75:
        speech_bubble(ctx, "Hey, Nimi! I got a fan. Can you come over to my house "
                      "and help me connect it?", 540, 230, 900, (hx - 70, hy - 230),
                      _pop(t, S.T_SPEECH - 0.05, 29.45, 29.7), 56)
    if t > 29.55:
        k = ease_back(seg(t, 29.55, 29.75))
        for dx, dy, r in ((170, -230, 38), (220, -150, 22)):
            _sparkle(ctx, hx + dx, hy + dy, r * k)


def _sparkle(ctx, x, y, r):
    if r <= 0.5:
        return
    ctx.move_to(x, y - r)
    for i in range(1, 8):
        a = -math.pi / 2 + i * math.pi / 4
        rr = r if i % 2 == 0 else r * 0.3
        ctx.line_to(x + rr * math.cos(a), y + rr * math.sin(a))
    ctx.close_path()
    src(ctx, YELLOW)
    ctx.fill_preserve()
    src(ctx, OUT)
    ctx.set_line_width(4)
    ctx.stroke()


def _wipe(ctx, t):
    u = seg(t, 14.72, 15.28)
    if not 0 < u < 1:
        return
    off = lerp(-2100, 3200, u)
    for dx, c in ((-120, TEAL), (0, ORANGE)):
        ctx.move_to(off - 1300 + dx, 0)
        ctx.line_to(off + 1100 - dx, 0)
        ctx.line_to(off + 1500 - dx, H)
        ctx.line_to(off - 900 + dx, H)
        ctx.close_path()
        src(ctx, c)
        ctx.fill()


# ---------------------------------------------------------------- post FX
def _paper():
    if "paper" not in _CACHE:
        rng = np.random.default_rng(7)
        coarse = np.kron(rng.normal(0, 1, (H // 8, W // 8)), np.ones((8, 8)))
        for _ in range(2):
            coarse = (coarse + np.roll(coarse, 4, 0) + np.roll(coarse, 4, 1)
                      + np.roll(coarse, -4, 0) + np.roll(coarse, -4, 1)) / 5
        v = 128 + 9 * coarse / coarse.std() + 6 * rng.normal(0, 1, (H, W))
        g = np.clip(v, 0, 255).astype(np.uint8)
        arr = np.empty((H, W, 4), np.uint8)
        arr[..., 0] = arr[..., 1] = arr[..., 2] = g
        arr[..., 3] = 255
        surf = cairo.ImageSurface.create_for_data(memoryview(arr), cairo.FORMAT_ARGB32, W, H)
        _CACHE["paper"] = (surf, arr)
    return _CACHE["paper"][0]


def post(ctx):
    ctx.set_operator(cairo.OPERATOR_SOFT_LIGHT)
    ctx.set_source_surface(_paper(), 0, 0)
    ctx.paint_with_alpha(0.55)
    ctx.set_operator(cairo.OPERATOR_OVER)
    g = cairo.RadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.75)
    g.add_color_stop_rgba(0, 0.2, 0.1, 0.05, 0)
    g.add_color_stop_rgba(1, 0.2, 0.1, 0.05, 0.35)
    ctx.set_source(g)
    ctx.paint()


# ---------------------------------------------------------------- frame
def render_frame(t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    cam = S.camera(t)
    scene, cx, cy, z, rot = cam
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.rotate(rot)
    ctx.scale(z, z)
    ctx.translate(-cx, -cy)
    p = draw_train(ctx, t) if scene == "train" else draw_home(ctx, t)
    ctx.restore()
    overlays(ctx, t, cam, p)
    _wipe(ctx, t)
    post(ctx)
    surf.flush()
    return surf
