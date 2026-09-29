# Video styles — Subatomic Secrets

Every style: 1080×1920, 30 fps, **30–59 s** (hard cap 59 s), a hook in the first 2 s, no title card.
Burned-in captions of the voiceover (max 2 lines, 64–80 px, white on a black/yellow pill,
inside y 250–1650), `brand.watermark(ctx)` on every frame, and `brand.end_card(ctx, t, DURATION - 1.2)`.
Palette: yellow `#FDCB04`, black `#111111`, white, plus accents teal/orange.
Draw everything with cairo via `engine/gfx.py`. No real company logos or real people. Names only as text.

Timeline contract (`runs/<date>/timeline.py`): export `DURATION` and `render_frame(t)`.
Use `gfx.Track` for keyframes and `sfx.envelope()` for lip-sync and caption pulse.
Worked example: `examples/arjun_fan/` (story style, 30 s, full SFX mix).

## story — Arjun & Nimi cartoon (AI/tech in everyday life)
Reuse `characters.py` (Arjun full body with IK arms, Nimi bust) and `props.py` / `backgrounds.py`.
Structure: everyday problem (0–8 s) → Arjun tries the new tech comically (8–30 s) →
Nimi explains the real fact in one line (30–45 s) → punchline (45–55 s) → end card.
Two voices: `voice.arjun` and `voice.nimi`. Speech bubbles mirror the lines.

## newsflash — launches and announcements
Black background with a diagonal yellow "BREAKING" band that slides in (0–1.5 s).
4–6 cards, each 6–9 s: a big headline word (kinetic scale-in) plus a simple vector icon
(chip, phone, robot, rocket, brain) plus a 1-line fact. Card swaps use a yellow wipe with a `sfx.swish()`.
Last card: "Why it matters" with 2 bullets.

## cosmic — space & physics
Deep navy-to-black gradient, parallax starfield (3 layers), glowing planets or black holes made from
radial gradients, slow camera drift, `sfx.pad()` bed plus `sfx.riser()` into each reveal.
Captions in white with a yellow keyword highlight.

## lab — science explainers (biology, chemistry, physics)
Cream background, grid lines, animated diagrams: atoms (orbiting electrons), DNA helix
(two sine strands with rungs), cells, molecules, arrows and labels that draw on progressively.
Step-by-step build-up. Each step gets a `sfx.bloop()`.

## countdown — "3 facts about X"
Big yellow numbers 3 → 2 → 1 that slam in (`ease_back` plus `sfx.thud()`), each fact 12–16 s
with its own icon animation. The last fact is the most surprising.

## mythfact — misconceptions
Split screen. The top half "MYTH" is red-tinted with the claim, then stamped ✗ (`sfx.pop()`).
The bottom half "FACT" is teal-tinted with the truth, revealed with ✓ (`sfx.ting()`), plus a simple diagram.
Up to 2 myths per video.
