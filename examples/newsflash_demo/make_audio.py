"""Demo step 1: voice lines -> lines.json (timings) + audio.wav (voice + SFX).

usage (from repo root): python examples/newsflash_demo/make_audio.py
The routine writes an equivalent runs/<date>/make_audio.py each day.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
import sfx  # noqa: E402
from tts import synth  # noqa: E402

LINES = [
    "Here's a secret hiding in plain sight.",
    "The sunlight on your face right now left the Sun about eight minutes ago.",
    "So every time you see the Sun, you are looking into the past.",
    "And light from distant stars can be thousands of years old.",
]
GAP, LEAD, END_CARD = 0.45, 0.6, 1.4


def main():
    t, timings = LEAD, []
    for i, line in enumerate(LINES):
        wav = os.path.join(HERE, "line_%d.wav" % i)
        d = synth(line, wav)
        timings.append({"text": line, "start": round(t, 3), "dur": round(d, 3),
                        "wav": os.path.basename(wav)})
        t += d + GAP
    duration = round(t + END_CARD, 2)
    mix = sfx.Mix(duration)
    for k in timings:
        mix.add(k["start"], sfx.load_wav(os.path.join(HERE, k["wav"])), 1.0)
        mix.add(k["start"] - 0.25, sfx.swish(0.3), 0.25)
    mix.add(0.0, sfx.riser(0.6), 0.2)
    mix.add(duration - END_CARD, sfx.ting(2600, 0.8), 0.25)
    mix.add(0.0, sfx.pad(duration), 1.0)
    mix.write(os.path.join(HERE, "audio.wav"))
    with open(os.path.join(HERE, "lines.json"), "w", encoding="utf8") as f:
        json.dump({"duration": duration, "lines": timings}, f, indent=2)
    print("duration", duration)


if __name__ == "__main__":
    main()
