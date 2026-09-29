"""Render driver: stills for QA, or the full video piped into ffmpeg.

usage: python render.py stills 1.0 3.2 ...   -> qa/frame_XX.XX.png
       python render.py video                -> build/video_silent.mp4
"""
import os
import subprocess
import sys
from multiprocessing import Pool
from gfx import W, H, FPS, DURATION

HERE = os.path.dirname(os.path.abspath(__file__))


def _frame_bytes(i):
    from compose import render_frame
    return bytes(render_frame(i / FPS).get_data())


def stills(times):
    from compose import render_frame
    os.makedirs(os.path.join(HERE, "qa"), exist_ok=True)
    for t in times:
        path = os.path.join(HERE, "qa", "frame_%05.2f.png" % t)
        render_frame(t).write_to_png(path)
        print(path)


def video():
    os.makedirs(os.path.join(HERE, "build"), exist_ok=True)
    out = os.path.join(HERE, "build", "video_silent.mp4")
    n = int(round(DURATION * FPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
           "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "slow", "-crf", "17",
           "-pix_fmt", "yuv420p", "-r", str(FPS), out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(max(1, os.cpu_count() - 1)) as pool:
        for k, data in enumerate(pool.imap(_frame_bytes, range(n), chunksize=3)):
            proc.stdin.write(data)
            if k % 60 == 0:
                print("frame %d/%d" % (k, n), flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print(out)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills([float(a) for a in sys.argv[2:]])
    else:
        video()
