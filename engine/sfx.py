"""Synthesised sound-effect primitives and a simple stereo mixer (48 kHz).

See examples/arjun_fan/audio.py for a full, timed sound-design example.
"""
import math
import wave
import numpy as np

SR = 48000
RNG = np.random.default_rng(3)


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
    return np.convolve(x, kern / kern.sum(), mode="same")


def noise(dur):
    return RNG.normal(0, 1, int(dur * SR))


def tone(freq, dur, kind="sine"):
    t = tt(dur)
    ph = 2 * np.pi * np.cumsum(np.broadcast_to(freq, t.shape)) / SR
    return 2 / np.pi * np.arcsin(np.sin(ph)) if kind == "tri" else np.sin(ph)


def pluck(freq, dur=0.35, damp=0.994):
    """Karplus-Strong plucked string (pizzicato stingers)."""
    n, p = int(dur * SR), int(SR / freq)
    buf = RNG.uniform(-1, 1, p)
    out = np.empty(n)
    for i in range(n):
        j = i % p
        out[i] = buf[j]
        buf[j] = damp * 0.5 * (buf[j] + buf[(i + 1) % p])
    return out * env(n, 0.001, 0.05)


def swish(dur=0.22):
    return lp_fast(noise(dur) * np.sin(np.linspace(0, np.pi, int(dur * SR))) ** 2, 2500)


def bloop(f0, f1, dur=0.18):
    f = np.geomspace(f0, f1, int(dur * SR))
    return tone(f, dur) * env(len(f), 0.004, dur * 0.6)


def ting(freq=2400, dur=0.6):
    return sum(tone(freq * k, dur) / k ** 1.5 for k in (1, 2.76, 5.4)) * np.exp(-tt(dur) * 7)


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


def riser(dur=1.0, f0=200, f1=1200):
    f = np.geomspace(f0, f1, int(dur * SR))
    return (tone(f, dur, "tri") * 0.3 + lp_fast(noise(dur), 3000) * 0.4) * np.linspace(0, 1, len(f)) ** 2


def bell(dur=1.2):
    t = tt(dur)
    return sum(tone(1320 * k, dur) * np.exp(-t * (3 + 2 * i)) / (i + 1)
               for i, k in enumerate((1, 2.0, 2.99, 4.1)))


def pad(dur, freqs=(220, 277, 330), level=0.05):
    """Soft sustained chord bed (cosmic / lab styles)."""
    x = sum(tone(f * (1 + 0.002 * np.sin(2 * np.pi * 0.2 * tt(dur))), dur) for f in freqs)
    return x * env(len(x), 1.0, 1.5) * level


class Mix:
    def __init__(self, duration):
        self.n = int(duration * SR)
        self.l = np.zeros(self.n)
        self.r = np.zeros(self.n)

    def add(self, t0, x, gain=1.0, pan=0.0):
        i = int(t0 * SR)
        if i >= self.n or i < 0:
            return
        x = np.asarray(x)[: self.n - i] * gain
        self.l[i:i + len(x)] += x * math.sqrt((1 - pan) / 2)
        self.r[i:i + len(x)] += x * math.sqrt((1 + pan) / 2)

    def write(self, path):
        st = np.stack([self.l, self.r], 1)
        st = np.tanh(st * 1.2) / np.tanh(1.2)
        peak = np.abs(st).max()
        if peak > 0:
            st *= 0.89 / peak
        with wave.open(path, "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(SR)
            wf.writeframes((st * 32767).astype(np.int16).tobytes())


def load_wav(path):
    """Mono float array from a 48 kHz 16-bit wav (as produced by engine/tts.py)."""
    with wave.open(path) as wf:
        if wf.getframerate() != SR:
            raise ValueError("%s must be %d Hz" % (path, SR))
        a = np.frombuffer(wf.readframes(wf.getnframes()), np.int16) / 32768.0
        return a.reshape(-1, wf.getnchannels()).mean(1)


def envelope(path, fps=30):
    """Per-frame 0..1 loudness envelope of a voice line (lip-sync, caption pulses)."""
    a = load_wav(path)
    hop = SR // fps
    rms = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a), hop)])
    return np.clip(rms / (rms.max() * 0.6 + 1e-9), 0, 1)
