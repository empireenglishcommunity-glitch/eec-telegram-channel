# EEC Telegram Channel — Progress & Session Continuity

> **Purpose:** Read this file FIRST at the start of every session to restore context.
> **Last Updated:** July 8, 2026

---

## 🟢 IMAGE-GEN PIPELINE COMPLETE — resume command only needed for NEW content

```
Read PROGRESS.md in the eec-telegram-channel repo, specifically Thread 2
(MACAL Empire image generation). The full pipeline is DONE: seed generation,
curation, dataset prep, LoRA training (fixed a bad-caption bug, retrained
successfully — 1800/1800 steps, 0 crashes), and premium hi-res branded
content generation (10/10 images, real inference pipeline + watermark) are
all complete. Final LoRA is at image-gen/training/final_lora/
macalempire_style_sdxl_v2_final.safetensors and final content is at
image-gen/output/macal_empire_hires_final/ (both gitignored, download
locally if not already synced). If asked to generate MORE content, reuse
image-gen/comfyui/gen_content_hires.py on a fresh Kaggle session via the
same bridge pattern (image-gen/kaggle/remote_exec_bridge.py) — adjust
CONTENT_PROMPTS, keep architectural/interior prompts explicitly "enclosed,
no sky visible" to avoid sky-leakage, and ALWAYS verify final quality via a
real diffusers inference pass, never trust Kohya's training-time preview
sampler (it gave a false negative on the working retrained LoRA).
```

Full detail on everything done so far is in the "Thread 2" section immediately
below, and in `image-gen/dataset/CURATION-REVIEW.md` / `image-gen/RUN_GUIDE.md`.

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
- **Step 5 (train the LoRA) + Step 6 (generate real content): ✅ FULLY COMPLETE, LoRA WORKS, PREMIUM CONTENT GENERATED.**
  Full story:
  - Built `image-gen/kaggle/remote_exec_bridge.py` — a stdlib-only HTTP server + Cloudflare
    tunnel pasted into a Kaggle cell, giving the agent direct remote control (upload files,
    run commands, poll background jobs) instead of manual copy-paste. Has a self-healing
    tunnel watchdog (auto-restarts `cloudflared` if it dies, prints a fresh URL).
  - Built `image-gen/training/train_supervisor.sh` — wraps `sdxl_train_network.py` in a
    crash-recovery loop. Enabled `save_state = true` in `train_config.toml` so a crash can
    `--resume` from the last saved step instead of restarting at 0. Applies
    `NCCL_P2P_DISABLE=1 NCCL_IB_DISABLE=1` (Kaggle T4 pairs have no NVLink; this avoids a
    P2P-timeout SIGKILL seen in an earlier dual-GPU attempt that crashed at step 120 with
    no OOM error). Gives up after 8 consecutive crashes as a GPU-quota safety valve.
  - **First real training run (2026-07-09): completed all 1800/1800 steps, ZERO crashes,
    ~2h14min on Kaggle T4x2.** Infra fix fully validated — dual-GPU + NCCL fix + self-healing
    supervisor held for the entire run with no intervention needed.
  - **But the RESULT was bad.** Checked sample previews at steps 300/600/900/1200/1800
    against corrected test prompts (matched to what's actually in the training captions,
    not "crown" which was never present in any of the 76 captions). Backgrounds came out
    light grey/white/cream marble instead of dark near-black — the opposite of the "Dark
    Luxury/Imperial" brand target. Root cause: the 76 original captions DID mention
    "dark"/"black" (71 of 76 did), but worded inconsistently every time ("near-black
    backdrop", "matte black stone", "dark background", "darkness", etc.) — diluting the
    signal the trigger word needed to bind to. SDXL's strong pretrained prior toward bright
    marble/gold luxury imagery won out over an inconsistently-worded style cue.
  - **Fix applied (2026-07-09, this session):** rewrote all 76 caption `.txt` files in
    `image-gen/dataset/curated/` to append one identical fixed suffix to every single
    caption: `", dark near-black background, moody low-key lighting, imperial luxury
    aesthetic"`. Synced `manifest_template.csv` (git-tracked) and `curated/manifest.csv`
    to match. Re-zipped to `curated_dataset.zip`, verified via a fresh unzip that all 76
    captions contain the new suffix and none are placeholders.
  - **Retrained with corrected captions (2026-07-10): 1800/1800 steps, ZERO crashes,
    ~2h19min on Kaggle T4x2.** Confirmed via `supervisor.log`.
  - **IMPORTANT LESSON — the training-time preview sampler gave a false negative.**
    Checked Kohya's built-in checkpoint sample previews (DDIM, 30 steps, no negative
    prompt) at every checkpoint including the final step 1800 — they STILL looked bad
    (light backgrounds, incoherent scenes for weak concepts). This nearly led to
    concluding the caption fix had failed a second time. Before writing that off, tested
    the actual finished LoRA through a PROPER inference pipeline instead (diffusers,
    `StableDiffusionXLPipeline` + `DPMSolverMultistepScheduler` (DPM++ Karras), real
    negative prompt, 30 steps) — and the LoRA was actually excellent. **Root cause:
    Kohya's built-in preview sampler is simply low-fidelity and unreliable for judging
    final quality — always verify with a real inference pipeline, never trust the
    training-time preview alone.**
  - **Root-caused one remaining weak spot:** the "grand imperial columns" concept
    initially rendered with a light grey sky visible between columns (every OTHER
    architectural concept — throne room, staircase — was fully enclosed and came out
    perfectly dark). Fix: reworded the prompt to explicitly state "inside an enclosed dark
    hall, no sky visible, solid dark ceiling" instead of leaving room for an open-air
    colonnade interpretation. Confirmed via a 1-image test before committing to a full
    batch: fix worked completely.
  - **Built a premium hi-res generation pipeline** (`image-gen/comfyui/gen_content_hires.py`):
    base txt2img pass (1024x1024, 40 steps) → upscale 1.5x to 1536x1536 → img2img
    refinement pass (30 steps, 0.4 denoise) through the same LoRA-fused pipeline via
    diffusers' `from_pipe()` (reuses loaded weights, no reload) → real watermark
    compositing. This is standard SDXL hi-res-fix technique, not a shortcut — adds real
    fine detail (fabric weave, metal reflections, marble veining) a single low-res pass
    cannot produce.
  - **Hit and fixed a real CUDA OOM bug**: the hi-res batch script crashed on image #2
    of 10 (image #1 succeeded, ruling out "1536px doesn't fit" — it was cross-iteration
    memory fragmentation/accumulation). Fixed with `enable_vae_slicing()` +
    `enable_vae_tiling()` + explicit `gc.collect()` / `torch.cuda.empty_cache()` after
    each image, plus `PYTORCH_ALLOC_CONF=expandable_segments:True`. Also added
    resume-on-restart logic (skips already-completed images by filename) so a crash
    mid-batch doesn't waste the GPU time already spent on earlier images.
  - **Final result: 10/10 premium hi-res branded images generated successfully**,
    covering architectural/object/portrait/abstract categories, all with the real
    "EMPIRE ENGLISH" watermark composited cleanly. 9/10 are excellent; 1 (macro compass)
    has a minor cosmetic flaw (garbled pseudo-text in engraved dial markings — a known
    SDXL limitation rendering coherent glyphs, not a pipeline bug).
  - Final LoRA downloaded to `image-gen/training/final_lora/macalempire_style_sdxl_v2_final.safetensors`
    (456,486,928 bytes, byte-for-byte verified against the Kaggle source, valid
    safetensors header with 2958 tensors). Final content images in
    `image-gen/output/macal_empire_hires_final/` (10 PNGs + `content_batch_log.csv`).
    Both gitignored (large binaries) — download locally / sync to permanent storage,
    don't expect them to survive a fresh sandbox session.
- **Both Step 5 and Step 6 of `image-gen/RUN_GUIDE.md` are now complete.** The zero-budget
  Kaggle pipeline (seed generation → curation → dataset prep → LoRA training → branded
  content generation) has been proven end-to-end, with two real production-quality
  outputs: a working brand-style LoRA and a first batch of premium branded content.
- **If resuming to generate MORE content** (not required, but the pipeline is proven and
  reusable): spin up a fresh Kaggle session, use the same bridge + upload pattern, re-run
  `image-gen/comfyui/gen_content_hires.py` (adjust `CONTENT_PROMPTS` for new concepts,
  always frame architectural/interior concepts as explicitly enclosed to avoid sky leakage,
  always verify quality via a real diffusers inference pass — never trust Kohya's
  training-time preview sampler alone).
- **Known recurring issues (all worked around, but resurface with any fresh Kaggle session):**
  - Cloudflare quick tunnel (trycloudflare.com) can die silently (DNS stops resolving, no
    warning) during long sessions — the v2 bridge's watchdog auto-restarts it, but if the
    whole Kaggle session times out (not just the tunnel), everything must be re-uploaded
    from scratch (dataset re-upload takes ~5s, SDXL model re-download ~1min, so this is
    cheap to recover from — the expensive part is losing training progress, which
    `train_supervisor.sh` now also protects against via `--resume`).
  - Pasting the raw bridge script text directly into a Kaggle cell can corrupt long
    f-strings during copy/paste reflow (hit this once: `SyntaxError: unterminated f-string
    literal`) — always use the `wget` one-liner instead of pasting the full script body.

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
| **MACAL Empire zero-budget image-gen pipeline** | ✅ COMPLETE — LoRA trained successfully, premium content generated | Full pipeline proven end-to-end: 94 seed images → 76 curated → captions fixed (consistent dark-background suffix) → LoRA retrained (1800/1800 steps, 0 crashes) → verified via real diffusers inference (not Kohya's misleading preview) → 10 premium hi-res watermarked branded images generated. Final LoRA + content in `image-gen/training/final_lora/` and `image-gen/output/macal_empire_hires_final/` (gitignored, download locally). |

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
| 13 | 2026-07-09 | Image-gen: Step 5 — LoRA training, infra fixed, first run's RESULT failed, caption fix applied | Built `remote_exec_bridge.py` (agent remote-controls Kaggle directly: upload/exec/poll/download over HTTP+Cloudflare tunnel) and `train_supervisor.sh` (crash-auto-resume via `save_state`/`--resume`, `NCCL_P2P_DISABLE=1` fix for a dual-GPU SIGKILL seen on first attempt at step 120). Tested supervisor logic locally with a fake crashing script before trusting it with real GPU time — confirmed correct resume-from-checkpoint and give-up-after-N-attempts behavior. Ran full training: 1800/1800 steps, 0 crashes, ~2h14min, dual T4. Infra fully validated. But checked sample previews at every 300-step checkpoint against prompts matched to real training concepts — backgrounds stayed light/grey/cream, not dark near-black; concepts absent from training data (e.g. "crown") produced incoherent collages. Root cause: 71/76 original captions DID mention dark/black but worded inconsistently every time, diluting the trigger word's learned association. Fix: rewrote all 76 caption .txt files with one identical fixed suffix, synced both manifest CSVs, re-zipped `curated_dataset.zip`, verified via fresh unzip. NOT yet retrained with corrected captions — that's the next action. | Kiro |
| 14 | 2026-07-10 | Image-gen: retrain succeeds, false-negative preview lesson, premium content generation | Retrained with corrected dataset: 1800/1800 steps, 0 crashes, ~2h19min. Checked Kohya's training-time preview samples — STILL looked bad (light backgrounds, incoherent). Almost concluded the fix failed again. Instead tested the actual LoRA via a proper diffusers inference pipeline (DPM++ Karras, real negative prompt) — LoRA was excellent. Root cause of the false alarm: Kohya's built-in preview sampler is simply low-fidelity/unreliable, not representative of real inference quality. Root-caused and fixed one genuine remaining flaw: "columns" concept leaked a light sky between pillars (every enclosed-interior concept was already perfect) — reworded prompt to explicitly close off the sky, verified fixed via a 1-image test. Built `gen_content_hires.py`: base pass + 1.5x upscale + img2img refinement pass (hi-res fix technique) + real watermark. Hit a genuine CUDA OOM crash on image #2 of a 10-image batch (image #1 succeeded, ruling out "doesn't fit" — was cross-iteration memory accumulation); fixed with VAE slicing/tiling + explicit gc/cache-clear per iteration + resume-on-restart logic (skip already-completed images). Final batch: 10/10 images generated successfully, 9 excellent + 1 with a minor known-limitation flaw (illegible engraved text, an SDXL glyph-rendering limitation not a pipeline bug). Downloaded final LoRA (byte-verified, 456,486,928 bytes) and all 10 final images locally. Both Step 5 and Step 6 of RUN_GUIDE.md now complete. | Kiro |

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
| image-gen/kaggle/remote_exec_bridge.py | Agent remote-control bridge for Kaggle (HTTP + Cloudflare tunnel, self-healing) | ✅ Built, tested, used in a real training run |
| image-gen/training/ | Kohya SS LoRA training config + notebook | ✅ Built & validated |
| image-gen/training/train_supervisor.sh | Self-healing training loop — auto-resume on crash via save_state/--resume | ✅ Built, tested (fake-crash harness), proven on real GPU (1800/1800 steps, 0 crashes) |
| image-gen/training/corrected_sample_prompts.txt | 5 test prompts matched to real training captions (not invented concepts like "crown") | ✅ Complete |
| image-gen/comfyui/gen_content.py | First-pass real content generation (single 1024px, diffusers pipeline) | ✅ Built, tested, superseded by gen_content_hires.py |
| image-gen/comfyui/gen_content_hires.py | Premium content generation: hi-res fix (1024→1536 img2img refine), OOM-safe (VAE slicing/tiling + explicit cleanup), resume-on-crash | ✅ Built, tested, fixed a real OOM bug, produced 10/10 final images |
| image-gen/training/inference_test.py | Diffusers-based LoRA quality verification script (proved the trained LoRA works when Kohya's preview sampler misleadingly suggested it didn't) | ✅ Complete |
| image-gen/training/final_lora/macalempire_style_sdxl_v2_final.safetensors | The final, working, corrected LoRA (456,486,928 bytes, verified) | ✅ Complete (gitignored — large binary) |
| image-gen/output/macal_empire_hires_final/ | 10 final premium branded content images + batch log | ✅ Complete (gitignored — large binaries) |
| image-gen/comfyui/ | Generation workflow, batch runner, watermark generator | ✅ Built & tested, not yet run on Kaggle |

---

*Last checkpoint: July 8, 2026 — MACAL v3 Phase 1 deployed (paused before Phase 2);
MACAL Empire image-gen pipeline: seed generation, curation (76/94 approved), and dataset
prep all complete. `curated_dataset.zip` ready for Kaggle upload. Next action is Step 5
(LoRA training) in `image-gen/RUN_GUIDE.md` (see Thread 2 above).*
