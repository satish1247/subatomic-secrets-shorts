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
    ("Scientists can switch brain cells on and off... with light. And it just won a Nobel Prize.",
     "Scientists can switch brain cells on and off, with light. And it just won a Nobel Prize."),
    ("On October 5th, the Nobel Prize in Medicine went to Karl Deisseroth, Peter Hegemann and Georg Nagel.",
     "On October fifth, the Nobel Prize in Medicine went to Karl Dyce-roth, Peter Hegg-eh-man, and Georg Nah-gel."),
    ("It started with a tiny, single-celled green alga that swims toward light.",
     "It started with a tiny, single-celled green alga that swims toward light."),
    ("Hegemann and Nagel found why: channelrhodopsin, a protein gate that opens when light hits it.",
     "Hegg-eh-man and Nah-gel found why: channel-rho-dopsin, a protein gate that opens when light hits it."),
    ("Shine blue light, the gate opens, charged ions rush in, and the cell fires an electrical signal.",
     "Shine blue light, the gate opens, charged ions rush in, and the cell fires an electrical signal."),
    ("In 2005, Deisseroth's lab put this gene into rat nerve cells, and made them fire with blue light.",
     "In two thousand and five, Dyce-roth's lab put this gene into rat nerve cells, and made them fire with blue light."),
    ("That's optogenetics. Researchers can now switch chosen nerve cells on or off in a living brain.",
     "That's opto-genetics. Researchers can now switch chosen nerve cells on, or off, in a living brain."),
    ("It's helping scientists decode memory, behaviour and brain disorders.",
     "It's helping scientists decode memory, behaviour, and brain disorders."),
    ("In 2021, a man blind for 40 years partly regained sight with an algae protein in his eye and light-emitting goggles.",
     "In twenty twenty-one, a man blind for forty years partly regained sight, with an algae protein in his eye, and light-emitting goggles."),
    ("From pond algae to a Nobel Prize. Light really can flip a switch in the brain.",
     "From pond algae, to a Nobel Prize. Light really can flip a switch in the brain."),
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
        voice.synthesize_wav(text, w, syn_config=SynthesisConfig(speaker_id=PIPER_SPEAKER, length_scale=0.9))
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
GAP, LEAD, END_CARD = 0.38, 0.35, 1.4


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
            mix.add(k["start"] - 0.12, sfx.bloop(500, 900), 0.18)
    mix.add(0.0, sfx.riser(0.6), 0.2)
    mix.add(0.3, sfx.bell(1.2), 0.15)
    mix.add(duration - END_CARD, sfx.ting(2600, 0.8), 0.25)
    mix.add(0.0, sfx.pad(duration, (196, 247, 294), 0.035), 1.0)
    mix.write(os.path.join(HERE, "audio.wav"))
    with open(os.path.join(HERE, "lines.json"), "w", encoding="utf8") as f:
        json.dump({"duration": duration, "lines": timings}, f, indent=2)
    print("duration", duration, [k["dur"] for k in timings])


if __name__ == "__main__":
    main()
