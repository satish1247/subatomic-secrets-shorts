"""2026-10-18 Step 1: voice lines -> lines.json (timings) + audio.wav (voice + SFX)."""
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
    ("Astronomers say they've found the first known green star.",
     "Astronomers say they've found the first known green star."),
    ("Stars shine in every colour at once. Even our Sun's light peaks in blue-green, but the mix looks white.",
     "Stars shine in every colour at once. Even our Sun's light peaks in blue-green, but the mix looks white."),
    ("This one is a white dwarf, the dead core of a star, called WD J1330+6435.",
     "This one is a white dwarf, the dead core of a star, called W D J thirteen thirty, plus sixty-four thirty-five."),
    ("Its secret? It pulled in rocky debris from its own planetary system, loading its atmosphere with sodium, calcium and lithium.",
     "Its secret? It pulled in rocky debris from its own planetary system, loading its atmosphere with sodium, calcium and lithium."),
    ("That dense sodium soaks up yellow, orange and some red light. What's left looks chartreuse green.",
     "That dense sodium soaks up yellow, orange and some red light. What's left looks chartreuse green."),
    ("No one has seen it glow green in a telescope. The University of Warwick team worked out its true colour from its light and a model of human vision.",
     "No one has seen it glow green in a telescope. The University of Warwick team worked out its true colour from its light, and a model of human vision."),
    ("They also found what may be the reddest star ever recorded: a pink white dwarf coloured by carbon.",
     "They also found what may be the reddest star ever recorded: a pink white dwarf, coloured by carbon."),
    ("Roughly one in thirty white dwarfs may hide an unusual colour. Space is more colourful than it looks.",
     "Roughly one in thirty white dwarfs may hide an unusual colour. Space is more colourful than it looks."),
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
