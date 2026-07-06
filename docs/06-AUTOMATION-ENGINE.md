# 06 — Full Automation Engine

> **Document:** Complete technical architecture for 100% autonomous channel operation.
> **Requirement:** Zero human involvement. Best quality. Visual content. Active engagement.
> **AI Provider:** Groq ONLY (no Gemini — limits and reliability issues).
> **Image Provider:** Cloudflare Workers AI (free, 10K neurons/day = dozens of images).

---

## 1. System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              EEC TELEGRAM CHANNEL — FULL AUTOPILOT ENGINE                     │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │ 1. CONTENT GENERATION (Weekly — Sunday 2 AM Dubai)                    │   │
│  │                                                                        │   │
│  │  Calendar logic → Groq AI (6 posts) → Quality filter → Image gen →    │   │
│  │  → Content queue (SQLite)                                              │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │ 2. POSTING ENGINE (Daily — 9:00 AM Dubai)                             │   │
│  │                                                                        │   │
│  │  Queue → Format post → Attach image → Send to channel → Log           │   │
│  │  Fallback: evergreen bank if queue empty                               │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │ 3. REACTION ENGINE (Staggered — 15 min to 8 hours after post)         │   │
│  │                                                                        │   │
│  │  Multiple bots react with randomized delays + emoji variety            │   │
│  │  Pattern: fast early reactions → slow trickle throughout day           │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │ 4. ENGAGEMENT ENGINE (Throughout the day)                             │   │
│  │                                                                        │   │
│  │  Discussion group seeding → Follow-up prompts → Polls → CTAs          │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │ 5. VISUAL ENGINE (Attached to generation)                             │   │
│  │                                                                        │   │
│  │  Cloudflare Workers AI (FLUX.1 Schnell) → branded images per post     │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │ 6. HEALTH MONITOR (Daily — 11 PM Dubai)                               │   │
│  │                                                                        │   │
│  │  Verify post sent → Check queue depth → Growth stats → Alert if broken│   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. AI Content Generation (Groq)

### Why Groq Only

| Factor | Groq | Gemini (rejected) |
|--------|------|:----------------:|
| Reliability | 99.9% uptime | Frequent rate limits, random failures |
| Speed | 500+ tokens/sec | Slow, unpredictable |
| Free tier | 14,400 req/day (8b), 1,000/day (70b) | 50 req/day on free |
| Quality | Excellent with good prompts | Good but unreliable delivery |
| Already deployed | ✅ GROQ_API_KEY on server | Would need separate setup |

### Generation Strategy

**Primary model:** `llama-3.3-70b-versatile` (best quality, 1000 req/day)
**Fallback:** `llama-3.1-8b-instant` (good quality, 14,400 req/day)

**Weekly generation batch (Sunday 2 AM):**
1. Determine next week's pillar rotation (Sat→Thu)
2. For each day: select topic from the rotation pool
3. Generate post using pillar-specific prompt + 3 few-shot examples
4. Validate: length, Arabic content, no banned phrases, has hook
5. If validation fails → regenerate (max 3 attempts) → fallback to bank
6. Generate image prompt for each post
7. Call Cloudflare Workers AI for image
8. Store text + image in queue

### Master Prompt Structure

```
SYSTEM:
أنت كاتب محتوى لـ Empire English Club — مجتمع تعليم إنجليزي للعرب.
بتكتب بالعامية المصرية. الكلمات التقنية بالإنجليزي (stress, shadowing, linking).

قواعد ثابتة:
- العامية المصرية فقط — ممنوع الفصحى
- أول سطر لازم يوقّف القارئ (hook)
- ممنوع hashtags
- ممنوع "تابعونا" أو "شير"
- ممنوع يزيد عن ٢٥٠ كلمة
- الأسلوب: واثق، ساخر بخفة (scalpel not sledgehammer)، أبوي
- آخر سطر: breadcrumb خفيف ناحية EEC (مش بيع)

USER:
اكتب بوست {pillar_type} عن: {topic}

اتبع القالب ده بالظبط:
{template}

أمثلة على بوستات سابقة ناجحة:
---
{example_1}
---
{example_2}
---
{example_3}
---

اكتب البوست الآن. Output البوست بس — من غير أي كلام تاني.
```

### Topic Pools (50+ Per Pillar — Never Runs Out)

**Accent Lessons:** Flap T, Schwa, Dark L, R sound, Word stress, Linking, TH sounds, Vowel reduction, Intonation, Glottal stop, Dropped H, Yod dropping, NG coalescence, Consonant clusters, Weak forms, Sentence stress, Rhythm, Nasal sounds, Diphthongs, Connected speech... (50+)

**Myth Destroyers:** Grammar first myth, Travel myth, Age myth, App myth, Vocabulary myth, Native teacher myth, Perfect pronunciation myth, Immersion myth, Talent myth, Fear of mistakes myth, Textbook myth, Watching movies myth... (30+)

**System Reveals:** 4 levels, Placement test, Daily loop, Shadowing, AI+Human, Discord, Kokoro TTS, IRT adaptive, 399 questions, CEFR mapping, Certification, Accountability, Voice lounges, Streak system, Bot features... (30+)

### Validation Rules (Auto-Check Before Queuing)

```javascript
function validatePost(text) {
  const checks = {
    hasContent: text.length > 50,
    notTooLong: text.length < 1500, // ~300 Arabic words
    hasArabic: /[\u0600-\u06FF]/.test(text),
    noHashtags: !text.includes('#'),
    noFollowUs: !text.includes('تابعونا') && !text.includes('شير'),
    noFormal: !text.includes('إن شاء الله سوف') && !text.includes('نود أن'),
    hasHook: text.split('\n')[0].length > 10, // First line exists and has substance
    hasBreakcrumb: text.includes('Empire') || text.includes('النظام') || text.includes('pinned'),
  };
  return Object.values(checks).every(v => v);
}
```

---

## 3. Visual Content (Cloudflare Workers AI)

### Why Cloudflare Workers AI

| Factor | Value |
|--------|-------|
| Cost | FREE (10,000 neurons/day) |
| Model | FLUX.1 Schnell (12B params, high quality) |
| Speed | ~5 seconds per image |
| API | OpenAI-compatible, works with n8n HTTP node |
| Already have | Cloudflare account (Workers already deployed) |
| Daily capacity | ~20-30 images/day on free tier (we need 1/day) |

### Image Strategy

Not every post needs an image. Here's the visual plan:

| Pillar | Visual Type | When |
|--------|-------------|------|
| 🎯 Accent Lesson (Saturday) | Branded graphic: the sound + mouth position | Always |
| 🔥 Social Proof (Sunday) | Stats graphic or progress visualization | Always |
| 💣 Myth Destroyer (Monday) | Bold text on branded background (myth crossed out) | Always |
| 🎯 Empire Word (Tuesday) | Word card: word + pronunciation + Arabic meaning | Always |
| 🏛️ System Reveal (Wednesday) | Diagram or system visualization | Sometimes |
| 👑/📢 Thursday | Brand image or CTA graphic | Sometimes |

### Image Generation Prompt Template

```
Generate a Telegram channel post image for an English learning brand.

Style: Dark background (#0A0A0F), gold accent (#D4AF37), modern, minimal, professional.
No text in the image (text will be in the Telegram caption).
Theme: {image_theme}
Mood: Authoritative, premium, educational.
Elements: {specific_elements}
Aspect ratio: Square (1024x1024)
```

### Image Types by Pillar

| Pillar | Image Prompt Pattern |
|--------|---------------------|
| AL | "Abstract visualization of sound waves and mouth anatomy, gold particles on dark background, professional educational" |
| SP | "Upward arrow chart showing progress, gold gradient on dark background, achievement celebration, premium feel" |
| MD | "Shattered glass or broken chains concept, gold shards on dark background, freedom from wrong beliefs" |
| SR | "Clean system diagram or network visualization, gold nodes connected on dark background, technology meets education" |
| BS | "Crown or empire pillars, gold on matte black, premium brand identity, powerful" |
| IN | "Open golden gate or doorway with light streaming in, invitation concept, dark surroundings, premium" |

### Fallback Strategy

If Cloudflare Workers AI fails:
1. Use a set of 10 pre-generated brand images (stored on server)
2. Rotate them based on pillar (each pillar has 2 fallback images)
3. Channel never posts without visuals — just uses a stock branded image

---

## 4. Reaction Engine (Natural-Looking)

### Technical Approach: Multiple Bot Accounts

The Telegram Bot API supports `setMessageReaction` — a bot that is admin in the channel can add reactions to posts. By using multiple bots, each adding one reaction with staggered timing, it looks natural.

### Architecture

```
┌─────────────────────────────────────────────────────┐
│  REACTION POOL: 8-12 Bot Accounts                    │
│                                                      │
│  Bot 1: @eec_helper_1   (react after 15-45 min)     │
│  Bot 2: @eec_helper_2   (react after 30-90 min)     │
│  Bot 3: @eec_helper_3   (react after 1-2 hours)     │
│  Bot 4: @eec_helper_4   (react after 1.5-3 hours)   │
│  Bot 5: @eec_helper_5   (react after 2-4 hours)     │
│  Bot 6: @eec_helper_6   (react after 3-5 hours)     │
│  Bot 7: @eec_helper_7   (react after 4-6 hours)     │
│  Bot 8: @eec_helper_8   (react after 5-8 hours)     │
│  ...                                                 │
└─────────────────────────────────────────────────────┘
```

### Natural Behavior Patterns

To avoid detection, the system mimics real human reaction patterns:

| Rule | Implementation |
|------|---------------|
| **Randomized delays** | Each bot reacts within a window, not at exact times. E.g., Bot 1 reacts between 15-45 min (random). |
| **Not all bots react every time** | Only 60-80% of bots react to each post (random selection). |
| **Varied emojis** | Each bot picks from a weighted set: 🔥(40%), ❤️(25%), 👍(20%), 😍(10%), 🎯(5%) |
| **Emoji matches content** | AI suggests 2-3 appropriate emojis per post. System picks from those. |
| **Fast burst + slow trickle** | 3-4 reactions in first hour (the "early engagers"), then 1 every 1-2 hours (the "throughout the day" people) |
| **Skip some days** | 1-2 bots "take a day off" randomly (real people don't react to EVERY post) |
| **Weekend variance** | Slightly fewer reactions on certain days (mimics real engagement patterns) |

### Setup Requirements

1. Create 8-12 bots via @BotFather (takes 5 minutes)
2. Add all bots as admins in the channel (with "Post Messages" permission)
3. Store all bot tokens in a config on the server
4. n8n workflow iterates through them with randomized delays

### n8n Workflow Logic (Pseudo-code)

```
TRIGGER: After main post is sent (gets message_id)

FOR each bot IN selected_bots (random 60-80% of pool):
    delay = random_delay_in_window(bot.min_delay, bot.max_delay)
    emoji = select_weighted_emoji(post_theme)
    
    SCHEDULE at (now + delay):
        HTTP POST: https://api.telegram.org/bot{token}/setMessageReaction
        Body: {
            chat_id: CHANNEL_ID,
            message_id: POST_MESSAGE_ID,
            reaction: [{ type: "emoji", emoji: emoji }]
        }
```

### Reaction Count Targets (Realistic for Channel Size)

| Subscriber Count | Target Reactions/Post | Looks Natural Because |
|:----------------:|:---------------------:|----------------------|
| 0-100 | 5-8 | Small community, engaged early adopters |
| 100-500 | 8-15 | Growing, loyal audience |
| 500-1000 | 15-25 | Established, good engagement rate |
| 1000+ | 20-40 | Scale up gradually (NEVER jump suddenly) |

**Critical rule:** Scale reactions UP gradually as real subscribers grow. If channel has 50 subscribers and posts get 30 reactions, it looks fake. Start low, scale with growth.

---

## 5. Engagement Engine (Discussion Group Activity)

Makes the channel ecosystem feel busy and alive WITHOUT fake reactions in the main channel.

### Auto-Seeded Discussion Group Activity

| Time After Post | Action | What It Looks Like |
|:---------------:|--------|-------------------|
| +1 min | Forward post to discussion group with prompt | "💬 إيه رأيكم في البوست ده؟" |
| +2 hours | Bot asks follow-up question related to today's topic | "سؤال: مين فيكم بيقع في الغلطة دي؟" |
| +4 hours | Bot shares a "bonus tip" related to the post | "💡 tip إضافي: لو عايز تتمرن على ده..." |
| +6 hours | Bot posts a mini-poll or question | "🗳 إيه أصعب sound بالنسبالك؟" |

### The Discussion Group Bot Personality

The bot that posts in the discussion group should feel like a **community manager**, not a robot:

- Uses Egyptian Arabic
- Asks genuine questions
- References today's channel post
- Responds to messages (using Groq AI for dynamic replies)
- Posts at varied times (not exactly on the hour)

---

## 6. Kokoro TTS Integration (Voice Content)

Since you want zero involvement, voice notes will use **Kokoro TTS** (already on your server):

### How It Works

1. AI generates accent lesson text
2. Text includes a "demonstration section" in English
3. Kokoro generates audio of the English pronunciation demo
4. Audio attached to the channel post as a voice note

### Voice Note Format

The post says: "🎧 اسمع النطق الصح:" + Kokoro-generated audio of the example words/sentences.

This gives the channel audio content without you recording anything.

**Voice:** `af_heart` (already configured — professional, clear, American English)

---

## 7. Event-Triggered Posts (Always-On)

These fire automatically when things happen in the EEC ecosystem:

| Trigger Source | Event | Auto-Generated Post |
|---------------|-------|-------------------|
| Assessment API | Student completes assessment | 🔥 Social proof: "عضو جديد أكمل الامتحان — Score X/120" |
| Assessment API | Score > 90 | 🏆 "أول حد يجيب ٩٠+ في الامتحان!" |
| Channel stats | Subscriber milestone | 📊 "وصلنا X عضو في القناة!" |
| Challenge bot | Day 7/15/30 milestone | ⚔️ "Day X في التحدي — اللي لسه ماشيين..." |
| Calendar | 1st of month | 🏛️ "State of the Empire — شهر X" (auto-generated stats summary) |

---

## 8. Health Monitoring (Passive — No Action Needed)

| Check | Frequency | Alert If |
|-------|-----------|----------|
| Post sent today? | Daily 11 PM | No post went out |
| Queue depth | Daily | < 3 posts remaining |
| Reaction bots healthy | Daily | Any bot token invalid |
| Image generation working | Weekly | Cloudflare returning errors |
| Groq API accessible | At generation time | All models failing |
| Subscriber count | Weekly | Sudden drop (> 10% in a week) |

**Alerts go to:** Your Telegram (@macal_emperor) — you read only if you want. No action needed unless something breaks.

---

## 9. Complete Daily Timeline (What Happens Automatically)

| Time (Dubai) | Action | System |
|:------------:|--------|--------|
| 2:00 AM (Sun only) | Generate 6 posts + images for the week | n8n → Groq → Cloudflare AI |
| 8:55 AM | Prepare today's post from queue | n8n |
| 9:00 AM | **Post goes live** (text + image) | n8n → Telegram API |
| 9:01 AM | Forward to discussion group with prompt | n8n |
| 9:15-9:45 AM | First 2-3 reactions appear | Reaction engine (fast bots) |
| 10:00-11:00 AM | 2-3 more reactions | Reaction engine (medium bots) |
| 11:00 AM | Discussion group follow-up question | Engagement engine |
| 12:00-2:00 PM | 1-2 more reactions trickle in | Reaction engine (slow bots) |
| 1:00 PM | Discussion group bonus tip | Engagement engine |
| 3:00-5:00 PM | Final 1-2 reactions | Reaction engine (late bots) |
| 5:00 PM | Discussion group poll/question | Engagement engine |
| 11:00 PM | Health check + log | Monitor |

**From the subscriber's perspective:** They see a post at 9 AM with a beautiful image. Throughout the day, reactions build up naturally. The discussion group is active with related conversation. The channel feels alive, professional, and engaged.

---

## 10. Technology Stack Summary

| Component | Technology | Cost | Status |
|-----------|-----------|:----:|:------:|
| Workflow engine | n8n (self-hosted) | $0 | ✅ Running |
| Text generation | Groq (llama-3.3-70b) | $0 | ✅ Key on server |
| Image generation | Cloudflare Workers AI (FLUX.1) | $0 | ✅ Account exists |
| Voice generation | Kokoro TTS (self-hosted) | $0 | ✅ Running on-demand |
| Reaction bots | 8-12 Telegram bots (BotFather) | $0 | 🔨 Need to create |
| Content queue | SQLite on Hetzner | $0 | 🔨 Need to create |
| Posting | Telegram Bot API | $0 | ✅ Token exists |
| Monitoring | n8n + Telegram alerts | $0 | ✅ Pattern exists |
| **Total new cost** | | **$0** | |

---

## 11. Failure Modes & Recovery

| Failure | Impact | Auto-Recovery |
|---------|--------|---------------|
| Groq down during generation | No new posts generated | Use evergreen bank (30 posts always available) |
| Cloudflare AI down | No image | Send text-only post (still better than silence) |
| Single reaction bot token invalid | Fewer reactions | Other bots still react. Alert sent for manual token refresh. |
| n8n crashes | Everything stops | Watchdog auto-restarts (already running, 60s checks) |
| Queue empty | No post for today | Trigger emergency generation from bank + alert |
| Post sent but reactions fail | Post looks less engaged | Not critical — real subscribers still react |

**The golden rule:** The channel NEVER goes silent. There's always a fallback.

---

## 12. Security & Anti-Detection (Reactions)

| Measure | Purpose |
|---------|---------|
| Random delays (range, not fixed) | No two posts get reactions at the same time pattern |
| Random emoji selection (weighted) | Not always the same emoji combination |
| Random bot subset each day | Different "people" react to different posts |
| Gradual scaling with subscriber count | Reactions grow proportionally (not 50 reactions on a 20-subscriber channel) |
| Some bots skip days | Mimics real human behavior (not everyone reacts daily) |
| Weekend variance | Slightly different patterns on weekends |
| Never react to other channel's posts | Bots ONLY interact with EEC channel (clean accounts) |
| Bot profiles have names + avatars | Look like real accounts if someone checks |

---

## 13. Your Involvement After Launch

| Task | Frequency | Time |
|------|-----------|:----:|
| Nothing | Daily | 0 min |
| Glance at weekly report (optional) | Weekly | 1 min |
| Top up content bank (optional — AI handles it) | Never (unless you want to) | 0 min |
| Record voice notes | Never (Kokoro handles it) | 0 min |
| Fix broken bot token (rare) | If alert fires | 5 min |
| **Monthly total** | | **~5 min** |

---

*This document supersedes the manual workflow described in `04-IMPLEMENTATION-PLAN.md`.
The implementation plan phases remain the same, but Phase C-G now build this automation engine.*
