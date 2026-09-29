"""QA report for a rendered Short: spec checks + contact sheets to inspect by eye.

usage: python engine/qa.py runs/2026-09-30
Writes runs/<date>/qa/sheet_*.png and prints PASS/FAIL lines. Exit code 1 on any spec failure.
"""
import json
import os
import re
import subprocess
import sys

MAX_DURATION, MIN_DURATION = 59.0, 20.0
MAX_MB = 45


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration,size:stream=codec_type,width,height,r_frame_rate",
                          "-of", "json", path], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def loudness(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "ebur128",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?\d+\.\d) LUFS", err)
    return float(m[-1]) if m else None


def sheets(path, out_dir, duration):
    os.makedirs(out_dir, exist_ok=True)
    per, k, t = 10.0, 0, 0.0
    while t < duration:
        dst = os.path.join(out_dir, "sheet_%02d.png" % k)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t), "-t", str(per),
                        "-i", path, "-vf", "fps=2,scale=216:384,tile=10x2",
                        "-frames:v", "1", dst], check=True)
        print("sheet %s covers %.1f-%.1fs" % (dst, t, min(duration, t + per)))
        t += per
        k += 1


def main(run_dir):
    path = os.path.join(run_dir, "short.mp4")
    info = probe(path)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    has_audio = any(s["codec_type"] == "audio" for s in info["streams"])
    dur = float(info["format"]["duration"])
    mb = int(info["format"]["size"]) / 1e6
    lufs = loudness(path) if has_audio else None
    checks = [
        ("resolution 1080x1920", v["width"] == 1080 and v["height"] == 1920),
        ("30 fps", v["r_frame_rate"] == "30/1"),
        ("duration %.2fs within %d-%ds" % (dur, MIN_DURATION, MAX_DURATION),
         MIN_DURATION <= dur <= MAX_DURATION),
        ("size %.1f MB <= %d" % (mb, MAX_MB), mb <= MAX_MB),
        ("has audio", has_audio),
        ("loudness %s LUFS within -16..-12" % lufs, lufs is not None and -16 <= lufs <= -12),
    ]
    ok = True
    for name, passed in checks:
        print(("PASS " if passed else "FAIL ") + name)
        ok = ok and passed
    sheets(path, os.path.join(run_dir, "qa"), dur)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
