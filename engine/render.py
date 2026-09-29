"""Render a day's timeline to a YouTube Short.

Contract for runs/<date>/timeline.py:
    DURATION: float            # seconds, must be <= MAX_DURATION
    render_frame(t) -> cairo.ImageSurface (1080x1920 ARGB32)
Optional runs/<date>/audio.wav (48 kHz stereo) is muxed and loudness-normalised.

usage: python engine/render.py runs/2026-09-30            -> runs/<date>/short.mp4
       python engine/render.py runs/2026-09-30 --stills 0.5 3 7.2  -> runs/<date>/qa/*.png
"""
import argparse
import importlib.util
import os
import subprocess
import sys
from multiprocessing import Pool

ENGINE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ENGINE)
from gfx import W, H, FPS  # noqa: E402

MAX_DURATION = 59.0
_TL = {}


def load_timeline(run_dir):
    run_dir = os.path.abspath(run_dir)
    if run_dir not in sys.path:
        sys.path.insert(0, run_dir)
    spec = importlib.util.spec_from_file_location("timeline", os.path.join(run_dir, "timeline.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not 0 < mod.DURATION <= MAX_DURATION:
        raise SystemExit("DURATION must be in (0, %.0f], got %s" % (MAX_DURATION, mod.DURATION))
    return mod


def _init(run_dir):
    _TL["m"] = load_timeline(run_dir)


def _frame(i):
    return bytes(_TL["m"].render_frame(i / FPS).get_data())


def stills(run_dir, times):
    tl = load_timeline(run_dir)
    out = os.path.join(run_dir, "qa")
    os.makedirs(out, exist_ok=True)
    for t in times:
        path = os.path.join(out, "still_%05.2f.png" % t)
        tl.render_frame(t).write_to_png(path)
        print(path)


def video(run_dir):
    tl = load_timeline(run_dir)
    n = int(round(tl.DURATION * FPS))
    silent = os.path.join(run_dir, "video_silent.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
           "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-maxrate", "2500k", "-bufsize", "5000k", "-pix_fmt", "yuv420p", silent]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(max(1, (os.cpu_count() or 2) - 1), _init, (run_dir,)) as pool:
        for k, data in enumerate(pool.imap(_frame, range(n), chunksize=3)):
            proc.stdin.write(data)
            if k % 150 == 0:
                print("frame %d/%d" % (k, n), flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg video encode failed")
    out = os.path.join(run_dir, "short.mp4")
    audio = os.path.join(run_dir, "audio.wav")
    if os.path.exists(audio):
        mux = ["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", audio,
               "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000",
               "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out]
    else:
        mux = ["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-c", "copy",
               "-movflags", "+faststart", out]
    subprocess.run(mux, check=True)
    os.remove(silent)
    print(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--stills", nargs="*", type=float)
    a = ap.parse_args()
    if a.stills:
        stills(a.run_dir, a.stills)
    else:
        video(a.run_dir)
