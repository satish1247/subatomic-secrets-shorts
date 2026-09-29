"""Synthesised sound design + voice mix, synced to story.py timings.

usage: python audio.py  -> build/audio.wav (48 kHz stereo, 30 s)
"""
import math
import os
import wave
import numpy as np
import story as S

SR = 48000
N = int(30.0 * SR)
HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(3)


# ---------------------------------------------------------------- primitives
def tt(dur):
    return np.arange(int(dur * SR)) / SR


def env(n, a=0.005, r=0.1):
    e = np.ones(n)
    na, nr = max(1, min(n, int(a * SR))), max(1, min(n, int(r * SR)))
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e


def lp_fast(x, cutoff):
    """Approximate one-pole lowpass by convolving with an exponential kernel."""
    k = max(1, int(SR / (2 * math.pi * cutoff)))
    kern = np.exp(-np.arange(6 * k) / k)
    kern /= kern.sum()
    return np.convolve(x, kern, mode="same")


def noise(dur):
    return RNG.normal(0, 1, int(dur * SR))


def tone(freq, dur, kind="sine"):
    t = tt(dur)
    ph = 2 * np.pi * np.cumsum(np.broadcast_to(freq, t.shape)) / SR
    if kind == "tri":
        return 2 / np.pi * np.arcsin(np.sin(ph))
    return np.sin(ph)


def pluck(freq, dur=0.35, damp=0.994):
    """Karplus-Strong plucked string."""
    n = int(dur * SR)
    p = int(SR / freq)
    buf = RNG.uniform(-1, 1, p)
    out = np.empty(n)
    for i in range(n):
        j = i % p
        out[i] = buf[j]
        buf[j] = damp * 0.5 * (buf[j] + buf[(i + 1) % p])
    return out * env(n, 0.001, 0.05)


class Mix:
    def __init__(self):
        self.l = np.zeros(N)
        self.r = np.zeros(N)

    def add(self, t0, x, gain=1.0, pan=0.0):
        i = int(t0 * SR)
        if i >= N:
            return
        x = x[: N - i] * gain
        self.l[i:i + len(x)] += x * math.sqrt((1 - pan) / 2)
        self.r[i:i + len(x)] += x * math.sqrt((1 + pan) / 2)


# ---------------------------------------------------------------- sfx
def swish(dur=0.22):
    y = noise(dur) * np.sin(np.linspace(0, np.pi, int(dur * SR))) ** 2
    return lp_fast(y, 2500)


def bloop(f0, f1, dur=0.18):
    f = np.geomspace(f0, f1, int(dur * SR))
    return tone(f, dur) * env(len(f), 0.004, dur * 0.6)


def ting(freq=2400, dur=0.6):
    x = sum(tone(freq * k, dur) / k ** 1.5 for k in (1, 2.76, 5.4))
    return x * np.exp(-tt(dur) * 7)


def boing(dur=0.6, f0=180):
    t = tt(dur)
    f = f0 * (1 + 0.4 * np.exp(-t * 6) * np.sin(2 * np.pi * 14 * t)) * (1 + 0.8 * np.exp(-t * 8))
    return tone(f, dur, "tri") * np.exp(-t * 5)


def thud(dur=0.25, f=70):
    t = tt(dur)
    return (tone(f * (1 + np.exp(-t * 30)), dur) * np.exp(-t * 18)
            + lp_fast(noise(dur), 400) * np.exp(-t * 30) * 2)


def pop():
    t = tt(0.12)
    return (lp_fast(noise(0.12), 3000) * np.exp(-t * 60) * 4
            + tone(900 * np.exp(-t * 20), 0.12) * np.exp(-t * 40))


def rustle(dur=0.4, bright=3000):
    n = int(dur * SR)
    x = lp_fast(noise(dur), bright) - lp_fast(noise(dur), 300) * 0.5
    am = (RNG.random(n // 800 + 1) ** 2).repeat(800)[:n]
    return x * lp_fast(am, 40) * 3 * env(n, 0.02, 0.08)


def cricket(dur=0.5):
    t = tt(dur)
    gate = (np.sin(2 * np.pi * 30 * t) > 0.3) * (np.sin(2 * np.pi * 3 * t) > 0)
    return tone(4300, dur) * gate * env(len(t), 0.01, 0.05)


def bell(dur=1.2):
    t = tt(dur)
    return sum(tone(1320 * k, dur) * np.exp(-t * (3 + 2 * i)) / (i + 1)
               for i, k in enumerate((1, 2.0, 2.99, 4.1)))


def ring(dur=0.42):
    t = tt(dur)
    x = (tone(440, dur) + tone(480, dur)) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 20 * t)))
    return x * env(len(t), 0.01, 0.04) * 0.5


def whistle(mix, t0, freqs):
    for i, f in enumerate(freqs):
        d = 0.16
        v = tone(f * (1 + 0.01 * np.sin(2 * np.pi * 6 * tt(d))), d)
        mix.add(t0 + i * 0.18, v * env(len(v), 0.02, 0.05), 0.05)


def pizz_line(mix, t0, notes, step=0.2, gain=0.3):
    for i, n in enumerate(notes):
        if n:
            mix.add(t0 + i * step, pluck(440 * 2 ** ((n - 69) / 12)), gain, -0.2 + 0.1 * (i % 3))


# ---------------------------------------------------------------- beds
def train_bed(mix):
    dur = 15.3
    t = tt(dur)
    rumble = lp_fast(noise(dur), 120) * 3.0
    clack = np.zeros(len(t))
    for k in range(int(dur / 0.62)):
        for off in (0.0, 0.11):
            i = int((k * 0.62 + off + 0.05) * SR)
            b = lp_fast(noise(0.05), 1800) * np.exp(-tt(0.05) * 90) * 3
            clack[i:i + len(b)] += b[: len(clack) - i]
    mix.add(0, (rumble + clack) * env(len(t), 0.05, 0.5), 0.22)
    fs = np.array([S.fan_speed(x) for x in t[::480]]).repeat(480)[: len(t)]
    ang = 2 * np.pi * np.cumsum(fs * 3) / SR
    whir = lp_fast(noise(dur), 900) * (0.55 + 0.45 * np.sin(ang)) * (fs / S.FAN_RPS)
    hum = tone(100, dur) * (fs / S.FAN_RPS) * 0.15
    mix.add(0, (whir * 2 + hum) * env(len(t), 0.02, 0.4), 0.16)


def home_bed(mix):
    room = lp_fast(noise(15.0), 300) * 0.4
    mix.add(15.0, room * env(len(room), 0.3, 0.5), 0.12)
    for bt in (15.6, 18.3, 20.2, 26.7, 28.9):
        for k in range(3):
            mix.add(bt + k * 0.09, bloop(3200, 4200, 0.06), 0.025, 0.6)


# ---------------------------------------------------------------- timeline
def step_times(x0, x1, t0, t1):
    """Times the walk cycle (phase = x/38) crosses a step."""
    period = 38 * math.pi
    k0, k1 = math.ceil(min(x0, x1) / period), math.floor(max(x0, x1) / period)
    return [t0 + (k * period - x0) / (x1 - x0) * (t1 - t0) for k in range(k0, k1 + 1)]


def train_events(mix):
    mix.add(1.5, bloop(300, 520, 0.2), 0.08)
    mix.add(3.12, bloop(400, 1400, 0.25), 0.25)
    mix.add(3.2, ting(2600), 0.12)
    for t0 in (4.25, 5.5, 6.75):
        mix.add(t0, swish(), 0.35, -0.3 if t0 < 5 else 0.3)
    mix.add(6.1, rustle(0.45, 5000), 0.3, 0.5)
    mix.add(7.7, ting(3000), 0.15)
    pizz_line(mix, 7.75, [40, 0, 43, 0, 45, 0, 43, 40], 0.2)
    for k in range(10):
        mix.add(7.95 + k * 0.157, rustle(0.1, 2500), 0.12)
    mix.add(9.6, swish(0.35), 0.35)
    mix.add(9.75, bloop(200, 120, 0.25), 0.2)
    gust = lp_fast(noise(0.8), 1500)
    mix.add(10.6, gust * env(len(gust), 0.1, 0.2), 0.35)
    flutter = tone(90, 0.75, "tri") * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 28 * tt(0.75))))
    mix.add(10.65, flutter * env(len(flutter), 0.05, 0.15), 0.12)
    for t0 in (11.45, 11.75):
        mix.add(t0, bloop(500, 300, 0.15), 0.18)
        mix.add(t0, rustle(0.15, 6000), 0.2)
    mix.add(S.T_POP, pop(), 0.6)
    mix.add(S.T_POP + 0.02, boing(0.7), 0.35)
    mix.add(S.T_POP + 0.05, lp_fast(noise(0.5), 800) * np.exp(-tt(0.5) * 6), 0.35)
    for t0 in (12.3, 12.5):
        mix.add(t0, boing(0.3, 260), 0.12)
    for t0 in (12.6, 12.8):
        mix.add(t0, swish(0.18), 0.25)
    mix.add(13.0, bloop(420, 180, 0.2), 0.3)
    mix.add(13.05, swish(0.3), 0.3)
    mix.add(13.4, thud(), 0.5)
    for st in step_times(620, 1420, 13.45, 15.0):
        mix.add(st, pluck(1200, 0.08), 0.18)
    pizz_line(mix, 13.5, [40, 0, 43, 45, 0, 43, 40, 0], 0.19)
    whistle(mix, 13.7, [988, 880, 1047, 988])
    mix.add(14.7, swish(0.6), 0.6)


def home_events(mix):
    for st in step_times(-250, 430, 15.0, 15.95):
        mix.add(st, thud(0.12, 110), 0.25)
    mix.add(16.45, thud(0.3, 60), 0.5)
    mix.add(16.47, ting(1700, 0.4), 0.08)
    for i, n in enumerate((60, 64, 67, 72)):
        mix.add(16.95 + i * 0.07, pluck(440 * 2 ** ((n - 69) / 12), 0.6), 0.28)
    for i in range(10):
        mix.add(17.35 + i * 0.05, tone(523 * 2 ** (i * 2 / 12), 0.8) * np.exp(-tt(0.8) * 4), 0.05)
    wind = lp_fast(noise(1.5), 700)
    mix.add(17.4, wind * env(len(wind), 0.4, 0.5), 0.2)
    mix.add(18.75, pop(), 0.2)
    mix.add(19.05, rustle(0.4), 0.3, -0.3)
    for t0, pan in ((19.1, 0.4), (19.8, -0.4), (20.5, 0.4)):
        mix.add(t0, swish(0.2), 0.3, pan)
        mix.add(t0 + 0.1, rustle(0.25), 0.18, -0.3)
    for k in range(5):
        mix.add(21.25 + k * 0.165, rustle(0.1, 4000), 0.35)
    for i, t0 in enumerate((21.25, 21.5, 21.75)):
        mix.add(t0, bloop(500 + 120 * i, 900 + 150 * i, 0.15), 0.2)
    mix.add(22.2, thud(0.12, 110), 0.2)
    mix.add(22.6, rustle(0.35), 0.35, 0.3)
    mix.add(22.95, rustle(0.25, 5000), 0.3)
    mix.add(23.2, cricket(0.55), 0.06, 0.5)
    mix.add(23.75, bell(), 0.3)
    mix.add(24.1, pop(), 0.25)
    mix.add(24.12, ting(2000, 0.5), 0.1)
    mix.add(25.2, rustle(0.3), 0.3, 0.3)
    for k in range(2):
        mix.add(25.38 + k * 0.08, tone(1400, 0.05) * env(2400, 0.002, 0.01), 0.1, 0.4)
    mix.add(25.5, ring(), 0.35, 0.4)
    mix.add(25.9, pop()[:2000], 0.2, 0.4)
    mix.add(29.6, ting(2800, 0.8), 0.15)
    pizz_line(mix, 29.55, [60, 67, 72], 0.08, 0.22)


def load_voice(name):
    with wave.open(os.path.join(HERE, "audio", name)) as wf:
        if wf.getframerate() != SR or wf.getnchannels() != 1:
            raise ValueError("%s must be mono %d Hz" % (name, SR))
        return np.frombuffer(wf.readframes(wf.getnframes()), np.int16) / 32768.0


def main():
    mix = Mix()
    train_bed(mix)
    home_bed(mix)
    train_events(mix)
    home_events(mix)
    thought = load_voice("thought_slow.wav")
    d = int(0.12 * SR)
    echo = np.concatenate([thought, np.zeros(d)])
    echo[d:] += thought * 0.3
    mix.add(S.T_THOUGHT, echo, 0.55)
    mix.add(S.T_SPEECH, load_voice("line_fast.wav"), 0.95)
    st = np.stack([mix.l, mix.r], 1)
    st = np.tanh(st * 1.2) / np.tanh(1.2)
    st *= 0.89 / np.abs(st).max()
    os.makedirs(os.path.join(HERE, "build"), exist_ok=True)
    out = os.path.join(HERE, "build", "audio.wav")
    with wave.open(out, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((st * 32767).astype(np.int16).tobytes())
    print(out)


if __name__ == "__main__":
    main()
