"""Story timeline: Arjun keyframes, shot list, fan state and pose resolution."""
import math
from gfx import Track, seg, lerp, ease_io, ease_out
from characters import ARJUN_BASE, set_ik, to_world

# ---------------------------------------------------------------- key times
T_POP = 11.95          # fan comes off the ceiling
T_THOUGHT = 7.95       # "Today is my lucky day."
T_SPEECH = 25.95       # "Hey, Nimi! ..."
SPEECH_LEN = 3.39
FAN_RPS = 2.5
FAN_DECAY = 2.2
CEIL_FAN = (540, 420)
STOOL_FAN = (300, 1262)
CARRY_LOCAL = (0, -150)

SIT = dict(ARJUN_BASE, x=540, y=1230, thigh=0.3, ll1=0.5, lr1=0.5, ll2=-0.45, lr2=-0.45,
           al1=0.1, al2=-0.6, ar1=0.1, ar2=-0.6, look_x=0.4, look_y=0.1, mc=0.25)

TRAIN = Track(SIT, [
    (0.0, {}), (1.4, {}),
    (1.9, {"look_x": 0, "look_y": -1, "head_up": 0.7}),
    (2.9, {}),
    (3.15, {"eye_wide": 1.4, "brow_l": 1, "brow_r": 1, "mo": 0.35, "mw": 0.5, "mc": 0}, "back"),
    (4.1, {}),
    (4.3, {"head_turn": -0.8, "look_x": -1, "look_y": 0, "head_up": 0, "eye_wide": 1.05,
           "mo": 0, "mw": 0.8, "mc": 0, "lid": 0.35, "brow_l": 0.2, "brow_r": 0.2,
           "brow_ang": 0.4}),
    (5.4, {}),
    (5.55, {"head_turn": 0.8, "look_x": 1}),
    (6.6, {}),
    (6.8, {"head_turn": 0, "look_x": 0, "look_y": -1, "head_up": 0.6, "lid": 0.2}),
    (7.35, {}),
    (7.7, {"lid": 0.45, "brow_l": 1, "brow_r": -0.4, "brow_ang": 0.7, "mc": 0.95,
           "ms": 0.7, "mw": 1.25, "head_up": 0.2, "head_tilt": 0.12, "look_y": -0.6,
           "look_x": 0.3, "al1": -0.35, "al2": -1.35, "ar1": -0.35, "ar2": -1.35}),
    (7.9, {"rub": 1}),
    (8.4, {"mo": 0.15, "teeth": 1}),
    (9.5, {"rub": 0}),
    (9.85, {"y": 1040, "bob": -40, "thigh": 0.8, "lid": 0, "brow_l": 0.3, "brow_r": 0.3,
            "brow_ang": 0, "mc": 0.5, "ms": 0, "mo": 0, "teeth": 0, "mw": 1,
            "head_tilt": 0, "head_up": 0.8, "look_y": -1, "look_x": 0,
            "al1": 0.6, "al2": -0.3, "ar1": 0.6, "ar2": -0.3}),
    (10.1, {"y": 910, "bob": 0, "thigh": 1.0, "ll1": 0.1, "lr1": 0.1, "ll2": 0, "lr2": 0}),
    (10.3, {"al1": 2.75, "al2": 0.15, "ar1": 2.75, "ar2": 0.15}),
    (10.55, {"ikl": 1, "ikr": 1, "bob": -12}),
    (10.65, {"hair_wild": 1, "eye_open": 0.35, "mo": 0.55, "mw": 0.8, "mc": -0.2,
             "shake": 1, "brow_ang": -0.3}, "out"),
    (11.35, {}),
    (11.45, {"hair_wild": 0.5, "shake": 0, "eye_open": 0.1, "eye_curve": -0.6,
             "mo": 0.3, "mc": -0.5, "teeth": 1, "bob": 15}),
    (11.6, {"bob": -8}), (11.75, {"bob": 18}), (11.9, {"bob": -5}),
    (12.05, {"bob": 30, "lean": -0.22, "hair_wild": 0, "eye_open": 1, "eye_curve": -1,
             "eye_wide": 1.35, "mo": 0.4, "mw": 0.55, "mc": 0, "teeth": 0,
             "brow_l": 1, "brow_r": 1, "head_up": 0, "look_y": 0}, "out"),
    (12.3, {"lean": 0.16, "bob": 10}),
    (12.5, {"lean": -0.07, "bob": 0}),
    (12.65, {"lean": 0, "mo": 0, "mc": 0.1, "eye_wide": 1.1, "head_turn": -0.7,
             "look_x": -1, "sweat": 1, "brow_l": 0.4, "brow_r": 0.4}),
    (12.85, {"head_turn": 0.7, "look_x": 1}),
    (13.0, {"head_turn": 0, "look_x": 0, "mc": 0.8, "mo": 0.1, "teeth": 1}),
    (13.2, {"x": 580, "y": 1010, "bob": -50}),
    (13.4, {"x": 620, "y": 1130, "bob": 0}),
    (13.45, {"walk": 1, "mo": 0.22, "mw": 0.35, "mc": 0, "teeth": 0, "look_y": -0.8,
             "look_x": 0.6, "head_turn": 0.3, "brow_l": 0.8, "brow_r": 0.8, "sweat": 0}),
    (15.0, {"x": 1420}, "lin"),
])

HIP = dict(al1=0.75, al2=-1.75, ar1=0.75, ar2=-1.75)

HOME = Track(dict(ARJUN_BASE, x=-250, y=1260), [
    (15.0, {"walk": 1, "ikl": 1, "ikr": 1, "mc": 0.9, "mo": 0.2, "teeth": 1, "lid": 0.25,
            "head_up": 0.2, "brow_l": 0.5, "brow_r": 0.5, "head_turn": 0.3}),
    (15.95, {"x": 430}, "lin"),
    (16.05, {"walk": 0}),
    (16.45, {"lean": -0.18, "bob": 45, "head_turn": -0.4, "look_x": -0.8, "look_y": 0.5}),
    (16.6, {}),
    (16.95, dict(HIP, x=560, lean=0, bob=0, ikl=0, ikr=0, head_turn=0, look_x=0,
                 look_y=0, head_up=0.3, eye_open=0.1, mc=1, mo=0.25, lid=0,
                 hand_l="fist", hand_r="fist")),
    (17.2, {}),
    (17.5, {"head_tilt": 0.15, "mo": 0.1, "mc": 0.9, "al1": -0.3, "al2": -2.0,
            "ar1": -0.3, "ar2": -2.0, "hand_l": "open", "hand_r": "open"}),
    (18.95, {}),
    (19.1, {"head_tilt": 0, "eye_open": 1, "head_up": 0, "mc": 0, "mo": 0, "teeth": 0,
            "head_turn": 0.7, "look_x": 1, "brow_l": 0.6, "brow_r": -0.2,
            "al1": -0.1, "al2": -1.9, "ar1": 0.2, "ar2": -0.4, "hand_l": "fist"}),
    (19.6, {}),
    (19.8, {"head_turn": -0.7, "look_x": -1}),
    (20.3, {}),
    (20.5, {"head_turn": 0.7, "look_x": 1, "lid": 0.3}),
    (20.95, {}),
    (21.15, {"head_turn": 0.1, "look_x": 0, "look_y": -0.8, "head_tilt": -0.12,
             "ar1": 2.6, "ar2": 1.5, "mc": -0.3, "ms": 0.6, "mw": 0.8, "brow_l": 0.8,
             "brow_r": -0.3, "brow_ang": -0.2, "lid": 0}),
    (21.25, {"scratch": 1}),
    (22.0, {"scratch": 0}),
    (22.4, {"x": 680, "head_tilt": 0, "ar1": 0.3, "ar2": -0.3, "ms": 0, "mc": -0.1,
            "brow_l": 0.3, "brow_r": 0.3, "brow_ang": 0, "look_y": 0.4, "look_x": 0.4,
            "head_turn": 0.2}),
    (22.6, {"ikr": 1}),
    (23.15, {}),
    (23.25, {"mc": -0.05, "eye_wide": 1.15, "look_x": -1, "look_y": 0,
             "head_turn": -0.6, "brow_l": 0, "brow_r": 0}),
    (23.55, {}),
    (23.75, {"ikr": 0, "ar1": 2.8, "ar2": 0.25, "hand_r": "fist", "al1": 0.2,
             "al2": -0.3, "hand_l": "open", "eye_wide": 1.45, "brow_l": 1.1,
             "brow_r": 1.1, "mo": 0.45, "mw": 0.6, "mc": 0.2, "head_turn": 0,
             "look_x": 0.3, "look_y": -1, "head_up": 0.5}, "back"),
    (24.1, {"mo": 0.3, "mw": 1.1, "mc": 0.9, "teeth": 1, "eye_wide": 1.15}),
    (24.95, {}),
    (25.2, {"ar1": 0.35, "ar2": 0.0, "look_x": 0.2, "look_y": 0.5, "head_up": 0}),
    (25.5, {"ar1": 1.5, "ar2": 2.4, "look_y": -0.3, "look_x": 0.6, "mo": 0, "mc": 0.4,
            "teeth": 0, "brow_l": 0.6, "brow_r": 0.6, "eye_wide": 1.05}),
    (26.5, {}),
    (26.8, {"al1": 1.25, "al2": 0.15, "head_turn": -0.3, "look_x": -0.8}),
    (27.6, {}),
    (27.9, {"al1": 0.2, "al2": -0.3, "head_turn": 0.1, "look_x": 0.3}),
    (29.35, {}),
    (29.65, dict(al1=0.75, al2=-1.75, ar1=0.4, ar2=-2.3, mc=1, mo=0.3, teeth=1,
                 lid=0.3, brow_l=0.7, brow_r=0.2, head_tilt=0.08, lean=-0.04,
                 look_x=0, look_y=0)),
    (30.0, {}),
])

# (t0, t1, scene, cam_from(cx, cy, zoom), cam_to)
SHOTS = [
    (0.0, 2.4, "train", (540, 900, 1.15), (540, 880, 1.22)),
    (2.4, 4.2, "train", (540, 680, 2.0), (540, 700, 2.15)),
    (4.2, 4.8, "train", (540, 860, 2.4), (545, 860, 2.45)),
    (4.8, 5.4, "train", (260, 880, 2.0), (250, 880, 2.1)),
    (5.4, 6.0, "train", (540, 860, 2.4), (535, 860, 2.45)),
    (6.0, 6.6, "train", (830, 880, 2.0), (840, 880, 2.1)),
    (6.6, 7.4, "train", (540, 720, 2.1), (540, 720, 2.2)),
    (7.4, 9.6, "train", (540, 860, 2.6), (540, 870, 2.9)),
    (9.6, 13.0, "train", (540, 900, 1.0), (540, 880, 1.08)),
    (13.0, 15.0, "train", (560, 960, 1.0), (600, 960, 1.0)),
    (15.0, 17.2, "home", (520, 1060, 1.05), (520, 1040, 1.1)),
    (17.2, 19.0, "home", (560, 820, 1.55), (560, 830, 1.65)),
    (19.0, 21.0, "home", (585, 1100, 1.3), (585, 1100, 1.36)),
    (21.0, 22.2, "home", (560, 900, 2.1), (560, 900, 2.25)),
    (22.2, 23.45, "home", (620, 1120, 1.3), (640, 1110, 1.35)),
    (23.45, 25.0, "home", (680, 880, 1.7), (680, 860, 1.8)),
    (25.0, 30.01, "home", (650, 960, 1.75), (660, 940, 1.95)),
]


def shot_at(t):
    for s in SHOTS:
        if s[0] <= t < s[1]:
            return s
    return SHOTS[-1]


def camera(t):
    t0, t1, scene, a, b = shot_at(t)
    u = ease_io(seg(t, t0, t1))
    cx, cy, z = (lerp(a[i], b[i], u) for i in range(3))
    rot = 0.0
    if scene == "train":
        cy += 3 * math.sin(t * 2 * math.pi * 1.1) / z
        rot = 0.004 * math.sin(t * 3.1)
    return scene, cx, cy, z, rot


# ---------------------------------------------------------------- fan state
def fan_angle(t):
    w = 2 * math.pi * FAN_RPS
    if t < T_POP:
        return w * t
    return w * (T_POP + (1 - math.exp(-FAN_DECAY * (t - T_POP))) / FAN_DECAY)


def fan_speed(t):
    return FAN_RPS if t < T_POP else FAN_RPS * math.exp(-FAN_DECAY * (t - T_POP))


def _aim_hands_at_fan(p, t, fan, w):
    if w > 0:
        set_ik(p, t, -1, fan[0] - 168, fan[1] + 8, w)
        set_ik(p, t, 1, fan[0] + 168, fan[1] + 8, w)


def train_pose(t):
    """Arjun pose + fan centre in the coach (hands IK'd onto the fan)."""
    p = TRAIN.at(t)
    if t < T_POP:
        jig = 10 * math.sin((t - 11.4) * 40) if 11.4 < t else 0.0
        fan = (CEIL_FAN[0], CEIL_FAN[1] + jig)
    else:
        carry = to_world(p, t, CARRY_LOCAL)
        u = ease_out(seg(t, T_POP, 12.2))
        fan = (lerp(CEIL_FAN[0], carry[0], u), lerp(CEIL_FAN[1] + 40, carry[1], u))
    _aim_hands_at_fan(p, t, fan, p["ikl"])
    return p, fan


def home_pose(t):
    p = HOME.at(t)
    fan = STOOL_FAN
    if t < 16.95:
        carry = to_world(p, t, CARRY_LOCAL)
        u = ease_io(seg(t, 16.05, 16.45))
        fan = (lerp(carry[0], STOOL_FAN[0], u), lerp(carry[1], STOOL_FAN[1], u))
        _aim_hands_at_fan(p, t, fan, p["ikl"])
    return p, fan
