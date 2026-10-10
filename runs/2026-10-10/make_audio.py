"""2026-10-10 step 1: voice lines -> lines.json (timings) + audio.wav (voice + SFX)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
import certifi  # noqa: E402
if os.path.exists("/root/.ccr/ca-bundle.crt"):  # sandbox egress proxy re-terminates TLS
    certifi.where = lambda: "/root/.ccr/ca-bundle.crt"
import sfx  # noqa: E402
from tts import synth, default_voice  # noqa: E402

# (speaker, caption text, spoken text)
LINES = [
    ("arjun", "Nimi! My boss wants a report, slides AND code fixes by Monday!",
     "Nimi! My boss wants a report, slides, and code fixes, by Monday!"),
    ("nimi", "Relax. On October 8, Google Cloud announced Gemini agent, a \"universal agent for work.\"",
     "Relax. On October eighth, Google Cloud announced Gemini agent, a universal agent for work."),
    ("arjun", "One agent? For all of that?",
     "One agent? For all of that?"),
    ("nimi", "From one prompt box, it can answer questions, draft documents and write code.",
     "From one prompt box, it can answer questions, draft documents, and write code."),
    ("arjun", "But my report will take days!",
     "But my report will take days!"),
    ("nimi", "It's built for tasks that run for hours, or even days. It can even create temporary helper agents for each job.",
     "It's built for tasks that run for hours, or even days. It can even create temporary helper agents for each job."),
    ("arjun", "Helpers... for my helper?",
     "Helpers... for my helper?"),
    ("nimi", "And it picks the best model for each job, including Google's Gemini and Anthropic's Claude.",
     "And it picks the best model for each job, including Google's Gemini, and Anthropic's Claude."),
    ("arjun", "Perfect! Let me download it!",
     "Perfect! Let me download it!"),
    ("nimi", "Sorry, Arjun. Right now it's a private preview for business customers.",
     "Sorry, Arjun. Right now, it's a private preview for business customers."),
    ("arjun", "So this weekend... I am the agent.",
     "So this weekend... I am the agent."),
]
PIPER_URL = "https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-libritts-high.tar.gz"
PIPER_DIR = os.environ.get("PIPER_DIR", os.path.join(HERE, "..", "..", ".piper"))
PIPER_SPEAKER = {"arjun": 3, "nimi": 20}   # LibriTTS (CC BY 4.0) speakers
PIPER_SCALE = {"arjun": 0.92, "nimi": 0.95}


def piper_synth(text, out_wav, who):
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
        voice.synthesize_wav(text, w, syn_config=SynthesisConfig(
            speaker_id=PIPER_SPEAKER[who], length_scale=PIPER_SCALE[who]))
    trim = ("silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
            "silenceremove=start_periods=1:start_threshold=-50dB,areverse")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", trim,
                    "-ac", "1", "-ar", "48000", out_wav], check=True)
    os.remove(raw)
    with wave.open(out_wav) as wf:
        return wf.getnframes() / wf.getframerate()


def voice_line(text, out_wav, who):
    try:
        return synth(text, out_wav, voice=default_voice(who), rate="+6%")
    except Exception as err:  # edge-tts endpoint unreachable from the sandbox
        print("edge-tts unavailable (%s); using piper fallback" % str(err)[:80])
        return piper_synth(text, out_wav, who)


GAP, LEAD, END_CARD = 0.35, 0.25, 1.4


def main():
    t, timings = LEAD, []
    for i, (who, line, spoken) in enumerate(LINES):
        wav = os.path.join(HERE, "line_%d.wav" % i)
        d = voice_line(spoken, wav, who)
        timings.append({"who": who, "text": line, "start": round(t, 3), "dur": round(d, 3),
                        "wav": os.path.basename(wav)})
        t += d + GAP
    duration = round(t + END_CARD, 2)
    mix = sfx.Mix(duration)
    for i, k in enumerate(timings):
        mix.add(k["start"], sfx.load_wav(os.path.join(HERE, k["wav"])), 1.0)
        if i in (1, 3, 5, 7, 9):
            mix.add(k["start"] - 0.2, sfx.bloop(500, 1100), 0.18, 0.3)
    mix.add(0.0, sfx.boing(0.5), 0.12)
    mix.add(timings[6]["start"] - 0.2, sfx.pop(), 0.25)
    mix.add(timings[8]["start"] - 0.1, sfx.ting(2200, 0.6), 0.18)
    mix.add(timings[10]["start"] - 0.25, sfx.thud(), 0.4)
    mix.add(duration - END_CARD, sfx.ting(2600, 0.8), 0.25)
    mix.add(0.0, sfx.pad(duration, (131, 165, 196)), 1.0)
    mix.write(os.path.join(HERE, "audio.wav"))
    with open(os.path.join(HERE, "lines.json"), "w", encoding="utf8") as f:
        json.dump({"duration": duration, "lines": timings}, f, indent=2)
    print("duration", duration, [k["dur"] for k in timings])


if __name__ == "__main__":
    main()
