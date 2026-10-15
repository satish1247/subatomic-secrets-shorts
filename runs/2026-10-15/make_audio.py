"""2026-10-15 Step 1: voice lines -> lines.json (timings) + audio.wav (voice + SFX)."""
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
    ("A robot on Mars just became the farthest-driving vehicle on any other world.",
     "A robot on Mars just became the farthest-driving vehicle on any other world."),
    ("On October 11, NASA's Perseverance rover hit 45.22 kilometres on its odometer.",
     "On October eleventh, NASA's Perseverance rover hit forty-five point two two kilometres on its odometer."),
    ("That's 28.10 miles, just past the old record of 28.06 miles, set by the Opportunity rover.",
     "That's twenty-eight point one zero miles, just past the old record of twenty-eight point zero six miles, set by the Opportunity rover."),
    ("Opportunity needed nearly 15 years to drive that far. Perseverance did it in about five and a half.",
     "Opportunity needed nearly fifteen years to drive that far. Perseverance did it in about five and a half."),
    ("The secret? It mostly drives itself. Its AutoNav system has handled more than 90% of the distance.",
     "The secret? It mostly drives itself. Its Auto-Nav system has handled more than ninety percent of the distance."),
    ("It photographs the ground, builds a 3D map of hazards, and picks a safe path. NASA calls it thinking while driving.",
     "It photographs the ground, builds a 3D map of hazards, and picks a safe path. NASA calls it thinking while driving."),
    ("The first Mars rover, Sojourner, checked 20 points ahead. Perseverance checks 600,000 with every look.",
     "The first Mars rover, Sojourner, checked twenty points ahead. Perseverance checks six hundred thousand, with every look."),
    ("Its mission plan called for no more than 12.4 miles. NASA says it could keep rolling well into the 2030s.",
     "Its mission plan called for no more than twelve point four miles. NASA says it could keep rolling well into the twenty-thirties."),
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
