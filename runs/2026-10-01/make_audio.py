"""Step 1: voice lines -> lines.json (timings) + audio.wav (voice + SFX)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
import certifi  # noqa: E402
if os.path.exists("/root/.ccr/ca-bundle.crt"):  # sandbox egress proxy re-terminates TLS
    certifi.where = lambda: "/root/.ccr/ca-bundle.crt"
import sfx  # noqa: E402
from tts import synth  # noqa: E402

# (caption text, spoken text) - spoken text spells out numbers for the TTS
LINES = [
    ("A quantum computer just ran in space. For the first time ever.",
     "A quantum computer just ran in space. For the first time, ever."),
    ("A team led by the University of Vienna shrank a quantum lab to the size of a shoebox and put it on a tiny satellite.",
     "A team led by the University of Vienna shrank a quantum lab to the size of a shoebox, and put it on a tiny satellite."),
    ("It launched on a Falcon 9 rocket in June 2025, to an orbit about 550 kilometres up.",
     "It launched on a Falcon nine rocket in June twenty twenty-five, to an orbit about five hundred and fifty kilometres up."),
    ("Instead of electricity, it computes with single particles of light called photons.",
     "Instead of electricity, it computes with single particles of light, called photons."),
    ("But space fought back. Half of its six detectors failed, and its laser dimmed from 20 milliwatts to just 4.",
     "But space fought back. Half of its six detectors failed, and its laser dimmed from twenty milliwatts, to just four."),
    ("Sunlight swamped it too, so it worked in Earth's shadow, about 30 minutes of each 92-minute orbit.",
     "Sunlight swamped it too, so it worked in Earth's shadow: about thirty minutes of each ninety-two minute orbit."),
    ("Still, over eight months, it made pairs of photons, steered them through a programmable chip, and saw them interfere.",
     "Still, over eight months, it made pairs of photons, steered them through a programmable chip, and saw them interfere."),
    ("Real quantum physics, in orbit. One day, satellites could use chips like this to analyse their own images on board.",
     "Real quantum physics, in orbit. One day, satellites could use chips like this to analyse their own images, on board."),
]
PIPER_URL = "https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-libritts-high.tar.gz"
PIPER_DIR = os.environ.get("PIPER_DIR", os.path.join(HERE, "..", "..", ".piper"))
PIPER_SPEAKER = 20   # LibriTTS (CC BY 4.0) male speaker


def piper_synth(text, out_wav):
    """Offline fallback (SPEC 11): piper + LibriTTS voice -> 48 kHz mono wav, silence trimmed."""
    import subprocess
    import tarfile
    import urllib.request
    import wave
    from piper import PiperVoice
    from piper.config import SynthesisConfig
    model = os.path.join(PIPER_DIR, "en-us-libritts-high.onnx")
    if not os.path.exists(model):
        os.makedirs(PIPER_DIR, exist_ok=True)
        tgz = os.path.join(PIPER_DIR, "voice.tar.gz")
        urllib.request.urlretrieve(PIPER_URL, tgz)
        with tarfile.open(tgz) as tf:
            tf.extractall(PIPER_DIR)
    voice = PiperVoice.load(model)
    raw = os.path.splitext(out_wav)[0] + "_raw.wav"
    with wave.open(raw, "wb") as w:
        voice.synthesize_wav(text, w, syn_config=SynthesisConfig(speaker_id=PIPER_SPEAKER))
    trim = ("silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
            "silenceremove=start_periods=1:start_threshold=-50dB,areverse")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", trim,
                    "-ac", "1", "-ar", "48000", out_wav], check=True)
    os.remove(raw)
    with wave.open(out_wav) as wf:
        return wf.getnframes() / wf.getframerate()


def voice_line(text, out_wav):
    try:
        return synth(text, out_wav, rate="+6%")
    except Exception as err:  # edge-tts endpoint unreachable from the sandbox
        print("edge-tts unavailable (%s); using piper fallback" % str(err)[:80])
        return piper_synth(text, out_wav)
GAP, LEAD, END_CARD = 0.45, 0.35, 1.4


def main():
    t, timings = LEAD, []
    for i, (line, spoken) in enumerate(LINES):
        wav = os.path.join(HERE, "line_%d.wav" % i)
        d = voice_line(spoken, wav)
        timings.append({"text": line, "start": round(t, 3), "dur": round(d, 3),
                        "wav": os.path.basename(wav)})
        t += d + GAP
    duration = round(t + END_CARD, 2)
    mix = sfx.Mix(duration)
    for i, k in enumerate(timings):
        mix.add(k["start"], sfx.load_wav(os.path.join(HERE, k["wav"])), 1.0)
        if i:
            mix.add(k["start"] - 0.5, sfx.riser(0.5, 300, 900), 0.12)
    mix.add(0.0, sfx.riser(0.6), 0.2)
    mix.add(0.3, sfx.bell(1.2), 0.15)
    mix.add(duration - END_CARD, sfx.ting(2600, 0.8), 0.25)
    mix.add(0.0, sfx.pad(duration, (110, 165, 220, 277)), 1.0)
    mix.write(os.path.join(HERE, "audio.wav"))
    with open(os.path.join(HERE, "lines.json"), "w", encoding="utf8") as f:
        json.dump({"duration": duration, "lines": timings}, f, indent=2)
    print("duration", duration, [k["dur"] for k in timings])


if __name__ == "__main__":
    main()
