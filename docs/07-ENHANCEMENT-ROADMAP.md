# 07 — Enhancement Roadmap

> **Document:** Complete roadmap for fixes, enhancements, and innovations.
> **Created:** July 6, 2026
> **Status:** Ready to execute

---

## Overview

| Phase | Focus | Priority | Sessions |
|-------|-------|:--------:|:--------:|
| **Phase 1** | Critical Fixes | 🔴 | 1 session |
| **Phase 2** | Voice + Engagement | 🟡 | 1 session |
| **Phase 3** | Growth Features | 🟢 | 1-2 sessions |
| **Phase 4** | Innovation | 🔵 | Future |

---

## Phase 1 — Critical Fixes (Do First)

These are bugs or design flaws that will cause problems if not fixed.

| # | Fix | Problem | Solution | Status |
|---|-----|---------|----------|:------:|
| 1.1 | Reaction engine | Self-reactions aren't visible to subscribers on channel posts. Userbot reacting to its own post doesn't show. | Create 8-12 bot accounts via @BotFather, add as admins, rotate tokens for reactions | ⬜ |
| 1.2 | Thursday alternation | Thursday is always `brand_story`. Should alternate weekly with `invitation`. | Add week-number logic: even weeks = brand_story, odd weeks = invitation | ⬜ |
| 1.3 | Post deduplication | If bot crashes and restarts mid-day, it could post twice. No "did I already post today?" check. | Write last_post_date to file after posting. Check before posting. | ⬜ |
| 1.4 | AL depletion imbalance | Accent lessons get 2 slots/week (Sat + Tue) but other pillars get 1. AL bank depletes 2x faster. | Change Tuesday to "empire_word" (new pillar — single word focus, different from full accent lesson) | ⬜ |
| 1.5 | Post time variance | Posting at exactly 9:00:00 AM every day looks robotic. | Add random jitter: post between 8:50-9:10 AM (±10 min) | ⬜ |

### Phase 1 Deliverables
- [ ] Create 8-12 bots via @BotFather (human task)
- [ ] Store bot tokens in `.env` (comma-separated)
- [ ] Rewrite reaction engine to use multiple bot tokens
- [ ] Add Thursday alternation logic
- [ ] Add deduplication (last_post_date check)
- [ ] Change Tuesday pillar to "empire_word"
- [ ] Write 10 "Empire Word" posts for Tuesday bank
- [ ] Add time jitter (±10 min random)
- [ ] Test all fixes
- [ ] Deploy + restart service

---

## Phase 2 — Voice + Engagement (High Impact)

Features that will dramatically increase engagement and channel quality.

| # | Enhancement | What | Impact | Status |
|---|-------------|------|:------:|:------:|
| 2.1 | Kokoro voice notes | Generate pronunciation audio via Kokoro TTS for Saturday accent posts. Send as voice note after the image+text post. | 🔥🔥🔥 | ⬜ |
| 2.2 | Weekly polls | Add a weekly poll (Sunday afternoon). Topics rotate: hardest sound, daily practice habit, level self-assessment. | 🔥🔥 | ⬜ |
| 2.3 | Smart post timing | Instead of fixed 9:00 AM, vary ±10 min randomly per day. | 🔥 | ⬜ |
| 2.4 | Second daily touch | Add a short "evening tip" post (7 PM Dubai) — just 1-2 lines. Makes channel feel more alive. | 🔥🔥 | ⬜ |
| 2.5 | Discussion group auto-reply | When someone asks a question in the group, bot responds with a relevant tip or link to a past post. Uses Groq AI to understand the question. | 🔥🔥 | ⬜ |

### Phase 2 Deliverables
- [ ] Build Kokoro TTS integration (generate MP3 from post examples)
- [ ] Add voice note sending after accent lesson posts
- [ ] Create poll bank (20 poll questions, pillar-relevant)
- [ ] Schedule weekly poll (Sunday 3 PM Dubai)
- [ ] Write 30 evening tips (short, 1-2 lines each)
- [ ] Schedule evening tip (7 PM Dubai)
- [ ] Build discussion group auto-reply (Groq AI, triggered by keywords)
- [ ] Test all features
- [ ] Deploy + restart service

---

## Phase 3 — Growth Features (Scale)

Features that accelerate subscriber growth and deepen engagement.

| # | Enhancement | What | Impact | Status |
|---|-------------|------|:------:|:------:|
| 3.1 | Subscriber milestones | Auto-celebrate when channel hits 50, 100, 250, 500, 1000 subscribers. Branded image + text. | 🔥🔥 | ⬜ |
| 3.2 | Series posts (multi-part) | 3-part series that build anticipation. "Part 1/3" → next day "Part 2/3" → "Part 3/3". Drives daily check-backs. | 🔥🔥🔥 | ⬜ |
| 3.3 | "Best of" recycling | After 8 weeks, identify top 5 posts by views. Re-post as "🔥 الأكتر مشاهدة الشهر ده" for new subscribers. | 🔥🔥 | ⬜ |
| 3.4 | Quiz of the week | Sunday quiz: "Which pronunciation is correct? A or B?" — inline Telegram poll. Gamification. | 🔥🔥 | ⬜ |
| 3.5 | Daily analytics logging | Log post ID, pillar, views (after 24h), forwards. Build data to optimize. | 🔥 | ⬜ |
| 3.6 | Automated "State of the Empire" | First Saturday of each month: auto-generated stats post (posts this month, engagement, growth). | 🔥🔥 | ⬜ |

### Phase 3 Deliverables
- [ ] Build subscriber count checker (Telethon API)
- [ ] Create milestone celebration templates (image + text)
- [ ] Write 5 series (3 posts each = 15 series posts)
- [ ] Add series scheduling logic (detect if today starts a series)
- [ ] Build "best of" recycler (track views, re-post top performers)
- [ ] Create quiz bank (20 pronunciation quizzes)
- [ ] Add quiz scheduling (Sunday 5 PM Dubai)
- [ ] Build analytics logger (post_id, pillar, date, views_24h)
- [ ] Build monthly "State of Empire" auto-generator
- [ ] Deploy + restart service

---

## Phase 4 — Innovation (Future, When Channel Grows)

For when the channel has 500+ subscribers and needs next-level features.

| # | Innovation | What | When |
|---|-----------|------|------|
| 4.1 | Voice challenges | Post a challenge: "سجّل نفسك بتقول [word]. أحسن تسجيل هياخد mention." User-generated content. | 500+ subscribers |
| 4.2 | Before/After templates | Auto-generate "Day 1 vs Day 30" visuals when students advance levels. Most powerful social proof. | When students are active |
| 4.3 | Secret codes | Hide code words in posts occasionally. First person to DM bot gets a bonus. Forces reading. | 200+ subscribers |
| 4.4 | Telegram Stories | Post 15-second daily stories (pronunciation tip). Stories get massive views. | When Telegram Stories API is stable |
| 4.5 | Audio room announcements | Schedule weekly live audio rooms + announce in channel. Bridges passive → active. | When community is active |
| 4.6 | Weekly leaderboard | Auto-generate leaderboard image (top 5 by tasks, voice hours). Public recognition. | When Discord community is active |
| 4.7 | Email capture bot | Inline bot that captures emails when people tap a button. Builds owned audience list. | 250+ subscribers |
| 4.8 | Referral system | "ابعت القناة لـ ٣ صحابك واحصل على [bonus]" — tracked via bot. Viral growth. | 500+ subscribers |

---

## Execution Timeline

| Week | Phase | Focus |
|:----:|-------|-------|
| Week 1 | Phase 1 | Critical fixes (reactions, dedup, alternation, timing) |
| Week 2 | Phase 2 | Voice notes + polls + evening tips + smart timing |
| Week 3-4 | Phase 3 | Series, milestones, quizzes, analytics, monthly report |
| Month 2+ | Phase 4 | Innovations (as subscriber count grows) |

---

## Dependencies

| Dependency | Required For | Who |
|------------|-------------|-----|
| Create 8-12 bot accounts (@BotFather) | Phase 1.1 (reaction fix) | Human (you) |
| Kokoro TTS container running | Phase 2.1 (voice notes) | Already on server (start when needed) |
| Active students in assessment | Phase 4.2 (before/after) | Needs members |
| Channel growth to 200+ | Phase 4.3-4.8 (innovations) | Organic from content |

---

## Technical Notes

### Reaction Fix Architecture
```
Current (broken):
  Userbot → SendReactionRequest → own post → NOT visible to subscribers

Fixed:
  Bot_1 → setMessageReaction → post → visible ✅
  Bot_2 → setMessageReaction → post → visible ✅
  Bot_3 → setMessageReaction → post → visible ✅
  ... (staggered, random subset, different emojis)
```

### Kokoro Voice Note Flow
```
Post goes out (accent lesson) → extract example words →
Kokoro generates MP3 (localhost:8880/v1/audio/speech) →
Bot sends voice note to channel (2-3 min after main post)
```

### Evening Tip Format
```
Short, punchy, 1-2 lines only. No image. Just text.
Example: "💡 سجّل نفسك ٣٠ ثانية كل يوم. بعد أسبوع هتسمع الفرق."
```

### Series Post Logic
```
data/bank/series/series_01.json:
[
  {"part": 1, "total": 3, "text": "...", "next_day": true},
  {"part": 2, "total": 3, "text": "...", "next_day": true},
  {"part": 3, "total": 3, "text": "...", "next_day": false}
]

When scheduler picks a series → posts Part 1 today, Part 2 tomorrow, Part 3 day after.
Normal bank posts resume after series completes.
```

---

## Success Metrics (After All Phases)

| Metric | Current | Target (8 weeks) |
|--------|:-------:|:-----------------:|
| Posts per week | 5 | 10 (main + evening tips) |
| Voice notes per week | 0 | 1-2 |
| Polls per week | 0 | 1 |
| Reactions per post | 0 (broken) | 5-10 |
| Discussion group messages/day | Unknown | 10+ |
| Subscriber growth/week | Unknown | 5-10% |
| Views per post (% of subscribers) | Unknown | 30%+ |

---

*Ready to execute. Start with Phase 1.*
