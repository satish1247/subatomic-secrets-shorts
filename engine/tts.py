"""Neural English voice via edge-tts -> 48 kHz mono wav.

usage: python engine/tts.py "Text to speak" out.wav [--voice en-US-AndrewNeural] [--rate +5%]
Prints the duration in seconds. Default voices live in brand/channel.json -> voice.
"""
import argparse
import asyncio
import json
import os
import subprocess
import time
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RETRIES = 4


def default_voice(role="narrator"):
    with open(os.path.join(ROOT, "brand", "channel.json"), encoding="utf8") as f:
        return json.load(f)["voice"][role]


def synth(text, out_wav, voice=None, rate="+0%", pitch="+0Hz"):
    import edge_tts  # lazy: the rest of the engine works without it
    voice = voice or default_voice()
    mp3 = os.path.splitext(out_wav)[0] + ".mp3"
    for attempt in range(RETRIES):
        try:
            asyncio.run(edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(mp3))
            break
        except edge_tts.exceptions.EdgeTTSException as err:  # transient service hiccups
            if attempt == RETRIES - 1:
                raise RuntimeError("edge-tts failed after %d attempts: %s" % (RETRIES, err)) from err
            time.sleep(2 * (attempt + 1))
    trim = ("silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
            "silenceremove=start_periods=1:start_threshold=-50dB,areverse")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-af", trim,
                    "-ac", "1", "-ar", "48000", out_wav], check=True)
    os.remove(mp3)
    with wave.open(out_wav) as wf:
        return wf.getnframes() / wf.getframerate()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("text")
    ap.add_argument("out")
    ap.add_argument("--voice")
    ap.add_argument("--rate", default="+0%")
    ap.add_argument("--pitch", default="+0Hz")
    a = ap.parse_args()
    print("%.3f" % synth(a.text, a.out, a.voice, a.rate, a.pitch))
