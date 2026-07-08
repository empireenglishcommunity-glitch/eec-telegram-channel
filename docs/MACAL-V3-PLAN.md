# MACAL v3 — Full Enhancement Plan

> **Status:** ✅ Phase 1 COMPLETE & DEPLOYED | 🔲 Phase 2 NEXT (paused — resume here)
> **Last Updated:** July 8, 2026
> **Owner:** @macal_emperor (Empire English Community)
> **Repo:** empireenglishcommunity-glitch/eec-telegram-channel
> **Server:** Hetzner 77.42.43.250 at /opt/eec-channel-bot/
> **Service:** systemd `eec-channel-bot`
> **Deploy:** `cd /opt/eec-channel-bot && git pull && systemctl restart eec-channel-bot`

## ⏸️ RESUME POINT (read this first if continuing)

**Phase 1 is DONE and LIVE on the server.** The user paused here intentionally to work
on something else. When they come back, **start directly on Phase 2 (Image Library)**
— do not redo Phase 1.

Latest commit: `ceef45a` — "feat: MACAL v3 — full phonics knowledge + brand + sales psychology"
Pushed to: `main` branch, already deployed to Hetzner server (confirmed via git pull output).

Before starting Phase 2, quickly verify Phase 1 is still healthy:
```bash
systemctl status eec-channel-bot
journalctl -u eec-channel-bot --no-pager -n 10
```
Should show the service active and recent "🏛️ MACAL replied" log lines with no errors.

---

## Context — What's Already Done

### MACAL v1 (original):
- Groq AI (llama-3.3-70b) with system prompt
- Only 6 pronunciation rules (P/B, V/F, G/J, CH/SH, TH, R)
- Basic question detection in Telegram discussion group
- Replies to questions, ignores greetings/noise

### MACAL v2 (current — live on server):
- AI-first (NO keyword bank, NO static matching)
- System prompt v2 with personality + 6 rules + format rules + CTA
- Short replies (80-120 words)
- Arabic RTL-safe CTAs
- 3 example responses in prompt
- File: `bot/group_reply_engine.py` (147 lines, clean)

### What was REMOVED (broken, don't bring back):
- `bot/phonics_bank_engine.py` — keyword matching engine (caused false positives)
- `bot/data/bank/phonics_bank.json` — 50 static answers (gave wrong answers)
- The bank approach is DEAD. AI-only is the way forward.

---

## The Vision — MACAL v3

MACAL becomes the **most helpful English pronunciation assistant** for Arabs on Telegram. He knows ALL sounds, ALL common mistakes, and every reply subtly drives toward booking a free call with Empire English.

**Funnel:** Free value in group → Trust → Student feels the gap → Book free 30-min call → Membership

---

## Brand Guidelines

| Element | Value |
|---------|-------|
| Bot personality name | MACAL |
| Brand | Empire English (short) / Empire English Community - EEC (full) |
| Signature | 🏛️ EEC |
| Colors (for images) | Gold (#D4AF37) + Black (#1A1A1A) + White text |
| Tone | Egyptian masri, encouraging friend, knowledgeable |
| Target audience | Arabic speakers (Egyptian + Gulf) learning English |
| CTA target | Book free 30-min call with @macal_emperor |

### The Free Call (30 minutes):
- Free, no obligation
- Assessment of current pronunciation level
- Identify exact weak points
- Personal development roadmap
- Book via @macal_emperor on Telegram

---

## Phase 1: Enhanced AI Prompt — ✅ COMPLETE (July 8, 2026)

### Goal:
Expand MACAL's knowledge from 6 sounds to FULL pronunciation coverage, add sales psychology, integrate Empire brand.

### What was actually built (matches plan below):
- ✅ Identity/brand: MACAL introduced as "الصوت الرسمي لـ Empire English Community (EEC)"
- ✅ Core 6 rules kept STRICT and unchanged (P/B, V/F, G/J, CH/SH, TH, R)
- ✅ Added 9 extended sound rules: W vs V, NG, Dark/Light L, Schwa /ə/, short/long vowel
  pairs (ship/sheep, full/fool, cat/bed), -ED endings (3 forms), -S endings (3 forms),
  D vs T at word end, silent letters, word stress
- ✅ Added 20-word "commonly mispronounced" list (comfortable, vegetable, Wednesday, etc.)
- ✅ Added VALIDATE → VALUE → GAP → CTA response strategy explicitly in the prompt
- ✅ Added 30-minute free call description (bullet points) in the prompt
- ✅ Expanded CTA variations from 3 → 5, all Arabic RTL-safe
- ✅ Expanded example responses from 3 → 5 (core sound, extended/schwa sound,
  difficult word, general FAQ, About Empire/EEC)
- ✅ Fixed `_is_question()` signal gaps found during testing: added "ليه/why", "مين/who",
  "احجز/اشترك/انضم", "كام/سعر/تكلفة", "كبير/خايف/بخاف" — tested 21 cases (13 match / 8 no-match), all pass
- ✅ Deployed to Hetzner and confirmed live via `git pull` + `systemctl restart`

### File modified: `bot/group_reply_engine.py`
Only the `MACAL_SYSTEM_PROMPT` variable + `QUESTION_SIGNALS` list were changed.
Rest of the code (rate limiting, `_is_question`, `generate_reply`, `setup_group_listener`) unchanged from v2.

### File to modify: `bot/group_reply_engine.py`
Only the `MACAL_SYSTEM_PROMPT` variable needs rewriting. The rest of the code stays the same.

### New System Prompt v3 Structure:

```
1. IDENTITY & BRAND
   - "أنا MACAL من Empire English (EEC)"
   - Personality: Egyptian masri, encouraging, knowledgeable friend
   - Brand mention in every reply naturally

2. EXPANDED KNOWLEDGE BASE

   A) Core 6 Rules (STRICT — use exact physical descriptions):
      - P vs B (plosives, tissue test)
      - V vs F (fricatives, vibration test)
      - G vs J (Egyptian vs Standard Arabic ج)
      - CH vs SH (stop vs continuant)
      - TH /θ/ vs /ð/ (tongue between teeth)
      - English R (tongue never touches roof)

   B) Additional Sound Rules (12 more):
      - W vs V (lips rounded vs teeth on lip)
      - NG /ŋ/ (back of tongue, nasal)
      - Dark L vs Light L (back vs front tongue position)
      - Schwa /ə/ (most common English sound, relaxed mouth)
      - Short vowels: /ɪ/ ship vs /iː/ sheep
      - Short vowels: /ʊ/ full vs /uː/ fool
      - Short vowels: /æ/ cat vs /e/ bed
      - -ED endings: /t/ (walked), /d/ (played), /ɪd/ (wanted)
      - Plural -S: /s/ (cats), /z/ (dogs), /ɪz/ (buses)
      - D vs T (voiced vs voiceless at word end)
      - H (when it's silent: hour, honest)
      - Silent letters (knife, write, psychology, Wednesday)

   C) Word Stress & Rhythm:
      - English is stress-timed (not syllable-timed like Arabic)
      - Wrong stress = not understood (e.g., PHOto vs phoTO)
      - Common stress mistakes Arabs make

   D) 20 Most Mispronounced Words (Arabs):
      - comfortable, vegetable, Wednesday, February
      - world, girl, work, word
      - clothes, months, fifths (consonant clusters)
      - beach, sheet, focus (embarrassing mix-ups)
      - ask, three, think, author
      - development, environment, temperature
      - determine, executive

3. RESPONSE STRATEGY (Hidden sales psychology)

   Every response follows:
   a) VALIDATE: Make them feel good for asking ("سؤال ممتاز!")
   b) VALUE: Give real, useful information (builds trust)
   c) GAP: Hint at what they can't do alone:
      - "بس أذنك متعودة على النطق القديم — محتاج حد يسمعك"
      - "التمرين ده كويس بس محتاج feedback من متخصص"
      - "لوحدك صعب تعرف لو الصوت طالع صح"
   d) CTA: Natural next step (book the free call)

4. CTA RULES
   - End EVERY reply with a CTA
   - Choose the most natural one based on context
   - All Arabic, RTL-safe
   - Always mention @macal_emperor
   - Variations:
     • 🔥 كلّم @macal_emperor واحجز مكالمتك المجانية مع Empire English!
     • 🏛️ احجز 30 دقيقة مجانية مع Empire — كلّم @macal_emperor
     • 💡 عايز خطة شخصية؟ كلّم @macal_emperor — أول مكالمة مجانية!
     • 📱 ابدأ مع Empire English — كلّم @macal_emperor واحجز مكالمتك!
     • 🎯 خطوتك الجاية؟ كلّم @macal_emperor — 30 دقيقة تقييم مجاني!

5. FORMAT RULES
   - 80-150 words max (5-10 lines on Telegram)
   - 2-4 emojis (natural, not forced)
   - Short lines (phone-friendly)
   - Arabic RTL (minimize English words in CTA line)
   - Structure: problem → explanation → gap → CTA

6. BOOKING INFO (use when relevant)
   "المكالمة المجانية 30 دقيقة:
    - بنقيّم مستواك الحقيقي في النطق
    - بنحدد نقاط الضعف بالظبط
    - بنعملك خطة تطوير شخصية
    - مجانية ومفيش أي التزام"

7. EXAMPLE RESPONSES (5 different types for AI to mimic)

   Example 1 — Core sound question (P vs B)
   Example 2 — Non-core sound question (D or W)
   Example 3 — Word pronunciation (world, comfortable)
   Example 4 — General FAQ (where to start, how long)
   Example 5 — About Empire / booking
```

### Technical Details:
- Model: `llama-3.3-70b-versatile` (Groq)
- Temperature: 0.7
- Max tokens: 350
- Timeout: 15 seconds
- Rate limit: 15 replies/hour
- Fallback: if AI fails, don't reply (better than wrong answer)

---

## Phase 2: Image Library — 🔲 NEXT UP (start here on resume)

### Goal:
Attach branded Empire infographic images to relevant replies. Premium visual identity.

### Status: Not started. Nothing built yet for this phase.

### Architecture:
- Pre-made HTML templates → rendered to PNG via html2img (already in bot)
- Stored in `bot/data/images/` as PNG files
- Topic detection in reply engine: if AI mentions certain sounds → attach matching image
- NOT on every reply — only when there's a relevant infographic

### Image List (15 images):

| # | Filename | Topic | When to attach |
|---|----------|-------|----------------|
| 1 | `p_vs_b.png` | P vs B | AI reply about P or B |
| 2 | `v_vs_f.png` | V vs F | AI reply about V or F |
| 3 | `g_vs_j.png` | G vs J | AI reply about G or J |
| 4 | `ch_vs_sh.png` | CH vs SH | AI reply about CH or SH |
| 5 | `th_sounds.png` | TH /θ/ and /ð/ | AI reply about TH |
| 6 | `english_r.png` | English R | AI reply about R |
| 7 | `w_vs_v.png` | W vs V | AI reply about W |
| 8 | `ed_endings.png` | -ED pronunciation | AI reply about past tense |
| 9 | `word_stress.png` | Stress rules | AI reply about stress |
| 10 | `schwa.png` | Schwa /ə/ | AI reply about vowels |
| 11 | `short_long_vowels.png` | Ship/Sheep etc. | AI reply about vowel pairs |
| 12 | `silent_letters.png` | Silent letters | AI reply about silent letters |
| 13 | `6_missing_sounds.png` | "Where to start" | AI reply about starting |
| 14 | `empire_system.png` | What is Empire | AI reply about Empire/EEC |
| 15 | `free_call.png` | Book a call | AI reply about booking |

### Image Style:
- Gold (#D4AF37) header bar
- Black (#1A1A1A) background
- White text, Arabic-friendly font
- RTL layout
- 🏛️ Empire English Community logo/watermark
- Phone-optimized (1080x1350 or similar vertical)
- Clean, minimalist, premium

### Implementation:
1. Create HTML templates in `bot/templates/phonics/` (one per image)
2. Render once to PNG and store in `bot/data/images/`
3. In `group_reply_engine.py` after AI generates reply:
   - Check reply content for topic keywords
   - If match → `await event.reply(text, file=image_path)`
   - If no match → text only
4. Simple topic → image mapping dict (not the old bank matching!)

---

## Important Rules (Learned from mistakes):

1. **NEVER use keyword bank matching** — it causes false positives and gives wrong answers
2. **AI generates ALL replies** — it understands context, banks don't
3. **If AI can't answer well → don't reply** — silence is better than wrong answer
4. **Test on server with real questions** — sandbox can't call Groq API
5. **RTL matters** — every CTA line must be Arabic-first, @username only exception
6. **Short > long** — Telegram is mobile-first, people don't read walls of text
7. **The "gap" sells** — give value but make them realize they need a coach

---

## Deploy Checklist:

```bash
# On Hetzner server (77.42.43.250):
cd /opt/eec-channel-bot && git pull && systemctl restart eec-channel-bot

# Verify:
systemctl status eec-channel-bot
journalctl -u eec-channel-bot --no-pager -n 10

# Test (send in discussion group from non-bot account):
# - "الفرق بين p و b"
# - "إزاي أنطق حرف d"
# - "ابدأ منين"
# - Check logs show "🏛️ MACAL replied"
```

---

## File Map:

| File | Purpose | Status |
|------|---------|--------|
| `bot/group_reply_engine.py` | Main engine (AI prompt + listener) | ✅ v3 live on server |
| `bot/config.py` | Environment loader | ✅ No changes needed |
| `bot/main.py` | 24/7 autopilot (imports group_reply_engine) | ✅ No changes needed |
| `bot/templates/phonics/` | HTML templates for infographics | 🔲 Phase 2 — not created yet |
| `bot/data/images/` | Rendered PNG infographics | 🔲 Phase 2 — not created yet |
| `docs/MACAL-V3-PLAN.md` | This file | ✅ |

---

## Session Log

| Date | What happened | Agent |
|------|---------------|-------|
| Jul 8, 2026 | MACAL v1 built (basic 6-sound AI system) | Kiro |
| Jul 8, 2026 | Attempted "Option C" hybrid bank+AI system — built, deployed | Kiro |
| Jul 8, 2026 | Bank caused false positive (asked about D, got P answer) — user flagged as broken/embarrassing | Kiro |
| Jul 8, 2026 | Full renovation to MACAL v2: deleted bank entirely, AI-only system, tested, deployed | Kiro |
| Jul 8, 2026 | Brainstormed MACAL v3 (full phonics + brand + images), user approved plan, documented in this file | Kiro |
| Jul 8, 2026 | **Phase 1 built, tested (21 cases), committed (`ceef45a`), pushed, deployed to Hetzner** | Kiro |
| Jul 8, 2026 | User pausing to work on something else — checkpoint updated, will resume at Phase 2 | Kiro |

---

*Last checkpoint: July 8, 2026 — Session with Kiro — PAUSED after Phase 1, resume at Phase 2*
