# EEC Telegram Announcement Channel — Content Operating System

> **Project:** Empire English Club — Telegram Channel System
> **Owner:** empireenglishcommunity-glitch
> **Status:** Phase A (Foundation) — IN PROGRESS
> **Created:** July 6, 2026

---

## What This Repository Is

This is the **complete content operating system** for the EEC Telegram Announcement Channel — the public-facing trust engine that converts cold audiences into paying community members.

This repo contains:
- The full strategic blueprint (why, how, what)
- Content bank (30+ pre-written evergreen posts)
- Content calendar and posting schedule
- Templates and brand voice guidelines
- Progress tracking and session continuity
- Operational workflows

---

## Repository Structure

```
eec-telegram-channel/
├── README.md                          ← This file (project index)
├── PROGRESS.md                        ← Session continuity & checkpoint tracking
│
├── docs/
│   ├── 01-STRATEGY.md                 ← Strategic analysis & ecosystem positioning
│   ├── 02-CONTENT-ARCHITECTURE.md     ← 6 pillars, formats, calendar, metrics
│   ├── 03-BRAND-VOICE.md             ← Writing system, tone, templates
│   ├── 04-IMPLEMENTATION-PLAN.md     ← Phase A→E breakdown with tasks
│   └── 05-DECISIONS.md               ← Locked design decisions (don't revisit)
│
├── content/
│   ├── pinned-message.md              ← The channel "homepage" (pinned post)
│   ├── channel-description.md         ← Channel bio/about text
│   ├── accent-lessons/               ← 🎯 AL posts (voice note scripts + captions)
│   │   ├── AL-01-flap-t.md
│   │   ├── AL-02-schwa.md
│   │   └── ...
│   ├── myth-destroyers/              ← 💣 MD posts
│   │   ├── MD-01-grammar-first.md
│   │   └── ...
│   ├── system-reveals/               ← 🏛️ SR posts
│   │   ├── SR-01-four-levels.md
│   │   └── ...
│   ├── social-proof/                 ← 🔥 SP posts
│   │   ├── SP-01-before-after.md
│   │   └── ...
│   ├── brand-stories/                ← 👑 BS posts
│   │   ├── BS-01-why-i-built-eec.md
│   │   └── ...
│   └── invitations/                  ← 📢 IN posts (CTAs)
│       ├── IN-01-assessment-invite.md
│       └── ...
│
├── calendar/
│   ├── MASTER-CALENDAR.md            ← Full posting schedule (weeks mapped)
│   └── weekly-templates/             ← Reusable week structures
│
├── assets/
│   ├── voice-notes/                  ← Audio file references or scripts
│   └── images/                       ← Image templates or references
│
└── .kiro/
    └── steering/
        └── project-rules.md          ← AI agent rules for this project
```

---

## How to Use This Repo

### For Continuing Work (New Session / New Agent)

1. Read `PROGRESS.md` — shows exactly where we left off
2. Read `docs/02-CONTENT-ARCHITECTURE.md` — the content system
3. Read `docs/05-DECISIONS.md` — locked decisions (don't change these)
4. Check `calendar/MASTER-CALENDAR.md` — what's scheduled vs. what's written

### For Posting Content

1. Go to `content/` folder
2. Find the post for today's pillar
3. Copy the text, record the voice note (if applicable)
4. Post to Telegram at 9:00 AM Dubai time

### For Writing New Content

1. Follow templates in `docs/03-BRAND-VOICE.md`
2. Save in the correct `content/` subfolder
3. Update `PROGRESS.md` with what was added
4. Add to `calendar/MASTER-CALENDAR.md`

---

## Quick Reference

| Item | Value |
|------|-------|
| Channel | @[TBD — set during Phase A] |
| Discussion Group | @empireenglishcommunity |
| Posting Schedule | Sat-Thu, 9:00 AM Dubai (7:00 AM Cairo) |
| Friday | OFF (silence day) |
| Language | Egyptian Arabic (masri) — English is the subject, not the medium |
| Content Ratio | 80% value / 10% brand / 10% CTA |
| Voice Notes | Weekly (Saturday — Accent Lessons) |
| Pillar Rotation | AL → SP → MD → AL → SR → BS/IN |

---

## Connected Systems

| System | Purpose | Link |
|--------|---------|------|
| Telegram Sales Bot | Conversion (packages, quiz, payment) | @EmpireEnglishBot |
| Assessment | Placement test (TOEFL-equivalent) | assessment.empireenglish.online |
| Discord | Product delivery (learning system) | Server ID: 1519797013565280446 |
| Landing Page | SEO + email capture | empireenglish.online |
| LinkedIn Engine | Personal brand (Cloudflare Worker) | Auto-posting daily |
| Goals Form | Student intake | goals.empireenglish.online |

---

## Design Principles (Non-Negotiable)

1. **Value First, Always** — 80% teaches or inspires. Worth following even if they never pay.
2. **System Over Inspiration** — Content is planned, templated, batched. Never depends on daily motivation.
3. **One Post, One Purpose** — Every post does exactly ONE thing.
4. **Brand Voice Consistency** — Authoritative, slightly sarcastic, paternal, Egyptian Arabic.
5. **Silent Funnel** — Even value posts leave breadcrumbs toward assessment/bot.
6. **Compound, Don't Expire** — Evergreen content stays valuable forever.
7. **Rhythm Creates Trust** — Same days, same times, same formats.

---

*Empire English Club — Common Sense First*
