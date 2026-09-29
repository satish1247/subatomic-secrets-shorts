# Subatomic Secrets — daily Shorts engine

Code-only animated YouTube Shorts (1080x1920, <=59 s) for the **Subatomic Secrets** channel.
A Claude Code cloud routine runs `ROUTINE_PROMPT.md` daily at 05:30 IST: research -> topic -> script ->
render (`engine/`) -> QA -> upload to YouTube via Zapier.

- `engine/` gfx, characters, props, backgrounds, brand, sfx, tts, render, qa
- `examples/` newsflash_demo (end-to-end smoke test), arjun_fan (story style reference)
- `STYLES.md` the 6 video styles, `SPEC.md` requirements, `brand/` logo + channel config

Smoke test: `python examples/newsflash_demo/make_audio.py && python engine/render.py examples/newsflash_demo && python engine/qa.py examples/newsflash_demo`
