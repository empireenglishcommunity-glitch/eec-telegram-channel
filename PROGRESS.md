# EEC Telegram Channel — Progress & Session Continuity

> **Purpose:** Read this file FIRST at the start of every session to restore context.
> **Last Updated:** July 8, 2026

---

## 🟢 RESUME COMMAND — paste this to continue exactly where we left off

```
Read PROGRESS.md in the eec-telegram-channel repo, specifically Thread 2
(MACAL Empire image generation). Steps 0-4 of image-gen/RUN_GUIDE.md are done:
94 seed images generated, curated down to 76 (approved via PR #2), real
captions written, dataset prepped and zipped to
image-gen/dataset/curated_dataset.zip. Walk me through Step 5 — uploading
that curated dataset to a new Kaggle session and running
image-gen/training/MACAL_Empire_Train_LoRA.ipynb to train the brand LoRA.
```

Just paste the block above into a new session (any agent) and it will pick up
exactly at Step 5 of the image-gen pipeline. Full detail on everything done so
far is in the "Thread 2" section immediately below, and in
`image-gen/dataset/CURATION-REVIEW.md` / `image-gen/RUN_GUIDE.md`.

---

## ⏸️ ACTIVE WORK IN PROGRESS — READ THIS FIRST

**Two parallel threads are mid-flight.** Read both before continuing:

### Thread 1: MACAL (discussion group AI reply bot) — see `docs/MACAL-V3-PLAN.md`

- MACAL v1/v2/v3 all live in `bot/group_reply_engine.py`
- Current live version: **v3, Phase 1 complete and deployed** (full phonics knowledge,
  Empire brand integration, sales psychology, 5 CTA variations)
- **Phase 2 (branded infographic image library) is next but NOT started** — user paused
  intentionally to work on something else and will resume Phase 2 later
- Do NOT rebuild the keyword-matching bank system (`phonics_bank_engine.py` /
  `phonics_bank.json`) — it was tried, caused false positives (wrong answers), and was
  deleted. AI-only is the correct architecture for MACAL.
- **When resuming:** read `docs/MACAL-V3-PLAN.md` in full, verify the service is healthy,
  then start Phase 2 (image library).

### Thread 2: MACAL Empire brand image generation — see `image-gen/RUN_GUIDE.md`

- Full research report at `docs/MACAL-EMPIRE-IMAGE-GEN-INFRASTRUCTURE.md` (self-hosted
  SDXL/FLUX + ComfyUI, hardware options, LoRA training strategy, cost estimates)
- A complete **zero-budget implementation** (Kaggle-based) has been built in `image-gen/`
- **Steps 0-4 of RUN_GUIDE.md are DONE:**
  - Kaggle GPU (T4x2) set up, ComfyUI + SDXL base model installed and running (via
    Cloudflare quick tunnel — URL changes every restart, tunnel drops every 5-10 min)
  - **Seed generation complete:** 94/105 unique seed images generated to
    `image-gen/dataset/raw_seed/` (gitignored, 132MB) — 11 prompts failed after retries
    (indices 1,12,37,60-65,76,97), acceptable loss
  - **Curation complete (agent-reviewed via 5 thumbnail contact sheets, pushed to PR #2
    for user visual review, user approved):** 76 KEEP / 18 REJECT. Full breakdown in
    `image-gen/dataset/CURATION-REVIEW.md`. Rejects were off-palette (grey/white studio
    backgrounds, green damask) or off-concept (storm clouds, hourglasses on light bg).
  - **Dataset prep complete:** real captions written for all 76 images (pulled from the
    actual generation prompt in `seed_batch_log.csv`, NOT auto-caption placeholders) into
    `manifest_template.csv` (tracked in git). Ran `prepare_dataset.py` →
    `image-gen/dataset/curated/` (gitignored, 76 image+caption pairs, 1024x1024, 0 rejected
    by validation). Zipped to `image-gen/dataset/curated_dataset.zip` (~106MB, gitignored)
    ready for Kaggle upload.
- **NOT yet done: Step 5 (train the LoRA) and Step 6 (generate real branded content)**
  — no trained LoRA exists yet.
- **When resuming:** read `image-gen/RUN_GUIDE.md` Step 5. User needs to upload
  `curated_dataset.zip` contents to a **new** Kaggle session (as a Kaggle Dataset, ideally)
  and run `training/MACAL_Empire_Train_LoRA.ipynb` (1-3 hrs GPU time). Compare checkpoint
  samples every 300 steps, pick best (not necessarily last). Then load LoRA into ComfyUI
  and generate real content via `batch_runner.py` with `--watermark`.
- **Known recurring issue:** Kaggle's Cloudflare quick tunnel (trycloudflare.com) drops
  every 5-10 min in long sessions — requires the 3-cell restart sequence (kill processes →
  start ComfyUI alone, verify locally → start tunnel separately with a short delay to avoid
  "Text file busy" race condition).

---

## Current State

| Phase | Status | Notes |
|-------|:------:|-------|
| Phase A — Foundation | ✅ COMPLETE | Channel description, pinned message (coming soon links), group rules |
| Phase B — Content Bank | ✅ COMPLETE | 100 premium posts + 10 Empire Word + 15 evening tips + 10 polls + 10 quizzes + 9 series parts |
| Phase C — Automation Engine | ✅ COMPLETE | Telethon userbot, systemd service, daily posting ~9AM Dubai |
| Phase D — Bank-Only + Images | ✅ COMPLETE | Hand-crafted content + HTML2IMG branded images |
| Phase E — Reactions | ✅ COMPLETE | 4 bot accounts, staggered 10min-7hrs, random emoji |
| Phase F — Engagement Engine | ✅ COMPLETE | Discussion group seeding + bonus tips |
| Phase G — Event Triggers | ✅ COMPLETE | Assessment completion → auto social proof (30min poll) |
| Phase H — Launch | ✅ COMPLETE | Pinned message, description, rules deployed, burn-in passed |
| **Enhancement Phase 1 — Fixes** | ✅ COMPLETE | Dedup, Thursday alternation, time jitter, Tuesday empire_word pillar |
| **Enhancement Phase 2 — Voice + Engagement** | ✅ COMPLETE | Kokoro voice notes, evening tips (7PM), weekly polls, weekly quizzes |
| **Enhancement Phase 3 — Growth** | ✅ COMPLETE | Series posts, milestones, analytics, monthly report, best-of recycling |
| **Enhancement Phase 4 — Innovation** | ✅ COMPLETE | Voice challenges, secret codes, audio room, email capture, referral |
| **Stress Test** | ✅ COMPLETE | 3 bugs found and fixed |
| **MACAL v1 — Basic AI reply bot** | ✅ COMPLETE | Groq AI, 6 pronunciation rules, question detection |
| **MACAL "Option C" hybrid bank** | ❌ BUILT & REVERTED | Keyword bank caused false positives (wrong-sound answers) — fully deleted |
| **MACAL v2 — AI-only renovation** | ✅ COMPLETE | Deleted broken bank, AI-first architecture, clean & tested |
| **MACAL v3 Phase 1 — Full phonics + brand + sales** | ✅ COMPLETE & DEPLOYED | See `docs/MACAL-V3-PLAN.md` |
| **MACAL v3 Phase 2 — Branded image library** | 🔲 PLANNED, NOT STARTED | Resume point — see `docs/MACAL-V3-PLAN.md` |
| **MACAL Empire self-hosted image-gen infrastructure report** | ✅ COMPLETE | Full research + implementation plan, see `docs/MACAL-EMPIRE-IMAGE-GEN-INFRASTRUCTURE.md` |
| **MACAL Empire zero-budget image-gen pipeline** | 🟡 IN PROGRESS — Steps 0-4 done, Step 5 (LoRA training) next | Kaggle GPU set up, 94 seed images generated, curated to 76, captioned, dataset prepped & zipped (`curated_dataset.zip`). See `image-gen/RUN_GUIDE.md` — Step 5 (train LoRA on Kaggle) is the next action |

**Content/posting automation (Phases A-H + Enhancements 1-4) is 100% complete.**
**MACAL discussion-group bot is mid-enhancement — Phase 2 pending.**

**DEFERRED (not blocking):**
- Cross-promotion links (bot, assessment, Discord) — update pinned message when services fully ready
- 5 more reaction bots — run `create_more_bots.py` after rate limit clears (~2.5 hours from last attempt)

---

## What's Been Done

### Session 1 — July 6, 2026
**Focus:** Strategic analysis + system design + repo creation + full automation architecture

**Completed:**
- [x] Full strategic analysis (Telegram vs alternatives, ecosystem positioning)
- [x] Content architecture designed (6 pillars, formats, weekly calendar)
- [x] Brand voice system defined (MACAL tone, templates, rules)
- [x] Implementation plan created (Phases A→H)
- [x] 30-post evergreen bank outlined (topics + hooks for all 30)
- [x] Success metrics defined
- [x] Risk mitigations documented
- [x] Design decisions locked (18 + 9 automation decisions = 27 total)
- [x] Repository created with full structure
- [x] All documentation files written
- [x] **FULL AUTOMATION ENGINE DESIGNED** (`docs/06-AUTOMATION-ENGINE.md`)
  - Content generation: Groq AI (no Gemini) — auto-generates weekly
  - Image generation: Cloudflare Workers AI (FLUX.1 Schnell) — free, per-post visuals
  - Reaction engine: 8-12 bot accounts with staggered natural-looking reactions
  - Engagement engine: Discussion group auto-seeding throughout the day
  - Voice content: Kokoro TTS (already on server) — pronunciation demos
  - Event triggers: Assessment completion → auto social proof posts
  - Health monitoring: Passive alerts, auto-recovery, never goes silent
  - Total cost: $0/month additional

**Also Completed This Session:**
- [x] Phase A execution: channel description, pinned message, branding copy ✅
- [x] Phase B: 50 premium posts written (Option A — minimal English, perfect masri) ✅
- [x] Full Telethon userbot developed (setup_channel.py, main.py, content_engine.py, image_engine.py, engagement_engine.py, config.py) ✅
- [x] HTML image templates built (6 pillars, gold/black Empire brand, RTL-safe) ✅
- [x] Server deployment: cloned, venv, deps installed, .env configured ✅
- [x] Telegram API credentials obtained (api_id + api_hash from my.telegram.org) ✅
- [x] Groq API key retrieved from existing server config ✅
- [x] Cloudflare Account ID + API Token created ✅
- [x] setup_channel.py executed — new channel created ✅
- [x] Bot reconfigured to use EXISTING channel (@Empire_English_Community) ✅
- [x] Test post verified — premium quality with branded image (message #77) ✅
- [x] AI content generation tested — rejected (quality not Empire-level) ✅
- [x] Switched to bank-only mode (hand-written posts, no AI generation) ✅
- [x] HTML2IMG service integration working (branded image per post) ✅
- [x] systemd service running — bot on full autopilot ✅

**System is LIVE. Zero human involvement required.**

---

## Next Session Priority

1. **Resume MACAL v3 Phase 2 (image library)** — read `docs/MACAL-V3-PLAN.md` first, this is the active work
2. **Create 5 more reaction bots** — run `create_more_bots.py` (rate limit should be cleared)
3. **Update pinned message** — when bot/assessment/Discord are ready, replace "coming soon" with live links

---

## Session Log

| # | Date | Focus | Key Outcomes | Agent |
|---|------|-------|-------------|-------|
| 1 | 2026-07-06 | Strategy + Design + Build + Deploy + Content | Full plan, automation engine, Telethon bot, 50 premium posts, deployed to server, channel LIVE on autopilot | Kiro |
| 2 | 2026-07-06 | Reactions + Engagement + Content + Events | Doubled to 100 posts (20 weeks), reactions engine, engagement engine, event triggers — all deployed | Kiro |
| 3 | 2026-07-06 | Phase H Launch + Burn-in | Pinned message deployed, description set, group rules posted, burn-in test passed (post #82), cross-promo deferred (coming soon) | Kiro |
| 4 | 2026-07-06 | Enhancement Phases 1-4 + Stress Test | ALL enhancements built: fixes (dedup, jitter, alternation, empire_word), voice notes, polls, quizzes, evening tips, series posts, milestones, analytics, best-of, voice challenges, secret codes, audio rooms, email capture, referral. 3 bugs found and fixed. System 100% complete. | Kiro |
| 5 | 2026-07-08 | Monitor + Verify + Create Bots | Verified bot working in production (posts, reactions, milestones, engagement all confirmed). Created 5th reaction bot. Discussion group confirmed linked. System 100% operational. | Kiro |
| 6 | 2026-07-08 | MACAL Option C hybrid bank — built, broke, reverted | Built keyword-bank + AI hybrid system, deployed. User found false positive (asked about letter D, got letter P answer) — flagged as damaging to credibility. Fully deleted bank files. | Kiro |
| 7 | 2026-07-08 | MACAL v2 — full AI-only renovation | Rewrote `group_reply_engine.py` from scratch, AI-only (Groq), tested 19+ question-detection cases, deployed and confirmed working live. | Kiro |
| 8 | 2026-07-08 | MACAL v3 planning + Phase 1 build | Brainstormed full phonics + brand + image plan with user, documented in `docs/MACAL-V3-PLAN.md`. Built & deployed Phase 1: expanded knowledge (14+ sounds, 20 hard words), Empire/EEC brand integration, VALIDATE→VALUE→GAP→CTA sales strategy, 5 CTA variations, 5 examples. Tested 21 question-detection cases, all pass. Committed `ceef45a`, deployed to Hetzner. | Kiro |
| 9 | TBD | **RESUME: MACAL v3 Phase 2** — image library | Build branded HTML→PNG infographics (gold/black Empire style) for ~15 topics, wire up topic-detection + image attachment in `group_reply_engine.py`. See `docs/MACAL-V3-PLAN.md` for full spec. | TBD |
| 10 | 2026-07-08 | MACAL Empire image-gen research + zero-budget pipeline build | User asked for a full self-hosted image-gen infra plan for the "MACAL Empire" brand (Dark Luxury/Imperial/Cinematic). Researched and wrote full technical report (`docs/MACAL-EMPIRE-IMAGE-GEN-INFRASTRUCTURE.md`): confirmed zero GPU exists in current infra, compared FLUX vs SDXL vs ComfyUI vs A1111, LoRA training strategy, recommended reusing existing n8n as orchestrator. User then said they can't spend anything — added a Zero-Budget Path section (Kaggle free GPU, 30hrs/week). Then built the ENTIRE pipeline as working, tested code in `image-gen/`: seed prompt generator (105 prompts), dataset prep script, Kaggle setup notebook (ComfyUI), Kohya SS LoRA training config + notebook, ComfyUI generation workflow + batch runner + watermark generator, and a master `RUN_GUIDE.md`. Every script was actually executed and tested (not just written) — see commit `ed09230`. **Not yet run on actual Kaggle by the user.** | Kiro |
| 11 | TBD | Create 5 more bots + update pinned links | Run create_more_bots.py after rate limit clears. Update pinned message when services ready. | TBD |
| 12 | 2026-07-08 | Image-gen: seed generation + curation + dataset prep | Ran seed batch on Kaggle T4x2 (with tunnel-drop recovery logic added to `run_seed_batch.py`), got 94/105 images. Built thumbnail contact sheets (5 sheets, ~200KB each) to review all 94 without exceeding message size limits — pushed to PR #2 for user visual review on GitHub. User approved. Corrected an initial recount error (68→76 keep after re-verifying against `seed_batch_log.csv`, added missed #066). Wrote real captions from actual generation prompts (not placeholders) into `manifest_template.csv`. Ran `prepare_dataset.py`: 76/76 accepted, 0 rejected, all 1024x1024, all captions verified. Zipped `curated_dataset.zip` for Kaggle upload. Next: Step 5, LoRA training. | Kiro |

---

## Important Context for New Agents

- This project is part of **Empire English Club** (EEC), an English learning community for Arabic speakers
- The Telegram channel is the **trust engine** — it does NOT sell. The Telegram bot does sales.
- All content is in **Egyptian Arabic** (masri dialect). English is the subject, not the medium.
- The channel connects to an existing ecosystem: Sales Bot, Assessment, Discord, Landing Page, LinkedIn Engine
- Read `docs/05-DECISIONS.md` for locked decisions that should NOT be changed
- Read `docs/03-BRAND-VOICE.md` for how posts should sound
- The full EEC system blueprint lives in: `empireenglishcommunity-glitch/EEC-REPO/docs/strategy/Empire English Community Learning System.md`

---

## Files in This Repo

| File | Purpose | Status |
|------|---------|:------:|
| README.md | Project index | ✅ Complete |
| PROGRESS.md | This file — session continuity | ✅ Active |
| docs/01-STRATEGY.md | Strategic analysis & positioning | ✅ Complete |
| docs/02-CONTENT-ARCHITECTURE.md | Pillars, formats, calendar, metrics | ✅ Complete |
| docs/03-BRAND-VOICE.md | Writing system, tone, templates | ✅ Complete |
| docs/04-IMPLEMENTATION-PLAN.md | Phase breakdown with tasks | ✅ Complete |
| docs/05-DECISIONS.md | Locked design decisions | ✅ Complete |
| docs/06-AUTOMATION-ENGINE.md | Full autopilot technical architecture | ✅ Complete |
| content/pinned-message.md | Channel pinned post | ✅ Complete |
| content/channel-description.md | Channel bio/about | ✅ Complete |
| content/channel-username.md | Username options (ranked) | ✅ Complete |
| content/discussion-group-rules.md | Discussion group rules | ✅ Complete |
| content/accent-lessons/ | 9 accent lesson posts (legacy, replaced by bank) | ✅ Superseded by JSON bank |
| content/myth-destroyers/ | 6 myth destroyer posts (legacy) | ✅ Superseded by JSON bank |
| content/system-reveals/ | 6 system reveal posts (legacy) | ✅ Superseded by JSON bank |
| content/social-proof/ | 5 social proof posts (legacy) | ✅ Superseded by JSON bank |
| content/brand-stories/ | 4 brand story posts (legacy) | ✅ Superseded by JSON bank |
| content/invitations/ | 3 invitation/CTA posts (legacy) | ✅ Superseded by JSON bank |
| bot/data/bank/accent_lesson.json | 10 premium accent posts | ✅ Complete |
| bot/data/bank/myth_destroyer.json | 10 premium myth posts | ✅ Complete |
| bot/data/bank/system_reveal.json | 10 premium system posts | ✅ Complete |
| bot/data/bank/social_proof.json | 10 premium proof posts | ✅ Complete |
| bot/data/bank/brand_story.json | 5 premium brand posts | ✅ Complete |
| bot/data/bank/invitation.json | 5 premium invitation posts | ✅ Complete |
| bot/templates/base.py | HTML base template (gold/black, RTL) | ✅ Complete |
| bot/templates/pillars.py | 6 pillar-specific HTML templates | ✅ Complete |
| bot/setup_channel.py | One-time channel creation script | ✅ Complete (executed on server) |
| bot/main.py | 24/7 autopilot engine | ✅ Complete (not yet running as service) |
| bot/content_engine.py | Groq AI content generation | ✅ Complete |
| bot/image_engine.py | Cloudflare Workers AI images | ✅ Complete |
| bot/engagement_engine.py | Discussion group auto-seeding | ✅ Complete |
| bot/config.py | Environment loader | ✅ Complete |
| bot/DEPLOY.md | Deployment guide | ✅ Complete |
| bot/.env.example | Credentials template | ✅ Complete |
| calendar/MASTER-CALENDAR.md | Posting schedule | ⬜ Not written |
| bot/group_reply_engine.py | MACAL — AI discussion-group reply bot (v3, Phase 1) | ✅ Live on server |
| docs/MACAL-V3-PLAN.md | MACAL v3 full plan + resume point (Phase 2 next) | ✅ Active — READ BEFORE MACAL WORK |
| ~~bot/phonics_bank_engine.py~~ | ~~Keyword bank matching~~ | ❌ Deleted — caused false positives, do not recreate |
| ~~bot/data/bank/phonics_bank.json~~ | ~~Static answer bank~~ | ❌ Deleted — do not recreate |
| docs/MACAL-EMPIRE-IMAGE-GEN-INFRASTRUCTURE.md | Full self-hosted image-gen research report | ✅ Complete |
| image-gen/RUN_GUIDE.md | Master step-by-step guide for the zero-budget pipeline | ✅ Active — READ BEFORE IMAGE-GEN WORK |
| image-gen/dataset/ | Seed prompts, dataset spec, prep script | ✅ Built & tested |
| image-gen/dataset/CURATION-REVIEW.md | Curation decision record — 76 keep / 18 reject, approved by user | ✅ Complete |
| image-gen/dataset/manifest_template.csv | Real captions for all 76 curated images | ✅ Complete, tracked in git |
| image-gen/dataset/curated/ (gitignored) | 76 training-ready 1024x1024 images + captions | ✅ Complete, ready for Kaggle upload |
| image-gen/dataset/curated_dataset.zip (gitignored) | Zipped curated/ for Kaggle upload | ✅ Complete |
| image-gen/kaggle/MACAL_Empire_Setup.ipynb | ComfyUI + SDXL environment setup notebook | ✅ Built & validated, not yet run on Kaggle |
| image-gen/training/ | Kohya SS LoRA training config + notebook | ✅ Built & validated, not yet run on Kaggle |
| image-gen/comfyui/ | Generation workflow, batch runner, watermark generator | ✅ Built & tested, not yet run on Kaggle |

---

*Last checkpoint: July 8, 2026 — MACAL v3 Phase 1 deployed (paused before Phase 2);
MACAL Empire image-gen pipeline: seed generation, curation (76/94 approved), and dataset
prep all complete. `curated_dataset.zip` ready for Kaggle upload. Next action is Step 5
(LoRA training) in `image-gen/RUN_GUIDE.md` (see Thread 2 above).*
