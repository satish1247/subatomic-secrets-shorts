# SPEC — Subatomic Secrets: Daily Shorts Routine

> **v3 (2026-09-29, supersedes conflicting lines below):** single trigger **05:30 IST** (cron `0 0 * * *` UTC);
> Shorts only, **max 59 s** (target 35-55 s + 1.4 s end card); **no Google Drive**: the MP4 is hosted on a
> `claude/video-<date>` branch of the public GitHub repo and uploaded to YouTube by Zapier from its raw URL;
> run history lives on the `claude/history` branch. Authoritative steps: ROUTINE_PROMPT.md.


Status: DRAFT v2, awaiting approval · Owner: dronicsacademy@gmail.com · 2026-09-27

## 1. Goal
A Claude Code cloud **routine** on **claude-opus-5-5** makes one YouTube Short a day for
**Subatomic Secrets** ("EVERY FACT. EVERYWHERE.") and publishes it **public** via the Zapier MCP connector.

| Run | Time (IST) | Job |
|---|---|---|
| Main | **06:00** | research → pick topic → script → render → upload to YouTube |
| Safety net | **09:00** | only if the 06:00 run did not publish: retry once. Otherwise stop immediately |

Cron (UTC): `30 0,3 * * *`. The duplicate guard in `history/published.json` guarantees at most one video per day.
This replaces the old 11 am automation.

## 2. Brand
- Name: Subatomic Secrets · Tagline: EVERY FACT. EVERYWHERE.
- Colours: yellow `#FDCB04` (primary), near-black `#111111`, white; accent glass highlights.
- Icon set (from the logo): planet, flask, DNA, brain, globe, leaf, magnifier, lightbulb, galaxy, atom.
- Logo: `brand/logo.png`. It appears as a small top-right watermark and on a 1 s end-card with the tagline.
- Topics: **70% AI & technology, 30% science** (space, physics, biology, chemistry, mind-blowing facts), balanced over the last 10 videos.
- Language: **English only**.

## 3. Topic research (100+ parameters)
Every run sweeps web search (at least 25 queries) for:
- **Fresh news (≤48 h):** AI model/product launches, open-source AI, big-tech, gadgets, chips,
  EV, robotics, cybersecurity, dev tools, India tech, space missions, new research papers or discoveries.
- **Evergreen science facts:** physics, space, biology, chemistry, human body, earth and nature.
  These are used when no strong news topic exists.

Collect ≥100 candidates. Score each 0–10 on 12 attributes: recency, source credibility, novelty
versus the last 30 days, audience interest, explainable in 45 s, visual potential, wow factor,
factual certainty, search interest, evergreen value, India relevance, and safety/controversy risk (inverted).
Then: **classify → validate (≥2 independent credible sources, no rumours or leaks) → score → pick top 1**,
keeping a runner-up. Everything is logged to `runs/<date>/research.json`.

## 4. Video styles (the agent picks per topic)
| Style | Best for | Look |
|---|---|---|
| **Story** | tech/AI in everyday life | Arjun and Nimi 2.5D cartoon comedy (as in `arjun_fan`) |
| **News flash** | launches and announcements | bold yellow and black headline cards, icons, kinetic text |
| **Cosmic** | space and physics | dark starfield, glowing planets and particles, slow camera drift |
| **Lab explainer** | science, biology, chemistry | animated diagrams (atoms, DNA, cells), labels, arrows |
| **Countdown** | "3 facts about X" | numbered cards 3 → 2 → 1 with icon animations |
| **Myth vs Fact** | misconceptions | split screen, ✗/✓ reveal |

All styles share: 1080×1920, 30 fps, **30–45 s**, a hook in the first 2 s, no title card,
the brand palette and watermark, an end-card, and on-screen captions synced to the voice.
Voice comes from `edge-tts` (an en-IN neural voice), with `piper` as an offline fallback.
Sound effects are synthesized, and loudness is about −14 LUFS. The file is H.264 + AAC and under 20 MB.
No real company logos or real-person likenesses; names appear as text only.

## 5. QA gate (max 3 rounds, then runner-up topic, then FAIL)
Stills every ~1.5 s plus contact sheets, inspected by the agent. Checks:
- consistency, clipping, and text legibility inside the safe area (y 250–1650)
- clean cuts
- captions match the voice
- `ffprobe` duration, size and resolution

## 6. Publishing
- Title ≤70 chars, a description with summary and sources, `#Shorts` plus 3 hashtags, 10–15 tags,
  category Science & Technology, not made for kids, and the disclosure "Animated and voiced with AI tools."
- MP4 → Google Drive folder (anyone-with-link) → Zapier YouTube "Upload Video", **public**.
- Record the result in `history/published.json` and `history/topics.json`, then commit and push.

## 7. Failure policy
Never publish an unverified fact or a video that failed QA. On failure, write `runs/<date>/FAILED.md`
and upload nothing. Zapier or Drive errors are retried once. Never post twice in a day.

## 8. Repo layout (GitHub, required for cloud routines)
```
engine/     gfx, compose, audio, tts, render, qa, drive_upload (generalised from arjun_fan)
styles/     story/ newsflash/ cosmic/ lab/ countdown/ mythfact/   (reusable templates)
brand/      logo.png, channel.json (name, colours, fonts, scoring weights)
fonts/      bundled OFL fonts
history/    published.json, topics.json
runs/<date>/ research.json, script.md, timeline.py, qa/, metadata.json
ROUTINE_PROMPT.md, requirements.txt
```

## 9. Still needed from you
1. **GitHub** private repo URL. The cloud agent can only run code it clones from git.
2. **Google Drive** folder link, and a service-account JSON (saved as a routine secret) with
   that folder shared to the service account.
3. **Zapier** connected on claude.ai with YouTube "Upload Video" enabled for the Subatomic Secrets channel.
4. ~~Language~~ decided: English only.

## 10. Acceptance criteria
- [ ] A manual run publishes a 30–45 s, 1080×1920 Short publicly and logs the URL
- [ ] `research.json` has ≥100 scored candidates; the chosen topic has ≥2 sources
- [ ] At least 4 different styles are produced across test topics (story, news flash, cosmic, lab)
- [ ] The 09:00 run exits without posting when 06:00 already succeeded
- [ ] A forced failure produces `FAILED.md` and no upload
- [ ] 3 consecutive scheduled days succeed

## 11. Risks
- Zapier may not set YouTube's synthetic-content flag; the disclosure goes in the description.
- The Drive virus-scan page breaks downloads above ~25 MB, so output stays under 20 MB.
- The cloud sandbox may block edge-tts network access, so piper is the fallback.
- Automated daily uploads can be judged "repetitive content" for monetisation. Rotating styles and topics mitigates this.
- Opus 5.5 every day, with rendering and visual QA, is a heavy daily token cost.
