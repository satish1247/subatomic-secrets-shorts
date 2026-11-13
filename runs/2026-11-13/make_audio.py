"""2026-11-13 step 1: voice lines -> lines.json (timings) + audio.wav (voice + SFX)."""
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

# (caption text, spoken text) - spoken text spells out abbreviations for the TTS
LINES = [
    ("This owl swallowed a cockroach 47 million years ago. And that last meal just revealed a secret.",
     "This owl swallowed a cockroach, forty-seven million years ago. And that last meal just revealed a secret."),
    ("Scientists found the fossil in Germany's Messel Pit and named it Masillastrix blattophaga: the cockroach eater.",
     "Scientists found the fossil in Germany's Messel Pit, and named it Masilla-strix blatto-phaga. The cockroach eater."),
    ("Let's bust two owl myths.",
     "Let's bust two owl myths."),
    ("Myth number one: owls have always hunted at night.",
     "Myth number one: owls have always hunted at night."),
    ("Fact: this early owl probably hunted by day. The cockroach in its stomach had iridescent wings, a trait linked to daytime insects.",
     "Fact: this early owl probably hunted by day. The cockroach in its stomach had iridescent wings, a trait linked to daytime insects."),
    ("Its upper wing bones were short and stocky too, unlike the slender ones of today's night owls.",
     "Its upper wing bones were short and stocky too, unlike the slender ones of today's night owls."),
    ("Myth number two: owls became night hunters right from the start.",
     "Myth number two: owls became night hunters right from the start."),
    ("Fact: the team thinks night hunting evolved later, sometime between about 47 and 34 million years ago.",
     "Fact: the team thinks night hunting evolved later, sometime between about forty-seven and thirty-four million years ago."),
    ("Owl fossils are rare, so this timeline could still change. And the owl might have snacked at dawn or dusk.",
     "Owl fossils are rare, so this timeline could still change. And the owl might have snacked at dawn or dusk."),
    ("So the ultimate night hunter may have started out as a daytime bird.",
     "So the ultimate night hunter may have started out as a daytime bird."),
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
GAP, LEAD, END_CARD = 0.5, 0.35, 1.4


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
        if i in (3, 6):   # myth: stamp X at the end of the line
            mix.add(k["start"] + k["dur"] + 0.05, sfx.pop(), 0.6)
        if i in (4, 7):   # fact reveal
            mix.add(k["start"] - 0.2, sfx.ting(), 0.35)
        elif i:
            mix.add(k["start"] - 0.25, sfx.swish(0.3), 0.25)
    mix.add(0.0, sfx.riser(0.6), 0.2)
    mix.add(duration - END_CARD, sfx.ting(2600, 0.8), 0.25)
    mix.add(0.0, sfx.pad(duration, (110, 165, 220)), 1.0)
    mix.write(os.path.join(HERE, "audio.wav"))
    with open(os.path.join(HERE, "lines.json"), "w", encoding="utf8") as f:
        json.dump({"duration": duration, "lines": timings}, f, indent=2)
    print("duration", duration, [k["dur"] for k in timings])


if __name__ == "__main__":
    main()
