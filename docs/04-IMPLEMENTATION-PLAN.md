# 04 — Implementation Plan

> **Document:** Phase-by-phase breakdown of what to build, in what order, with clear deliverables.

---

## Overview

| Phase | Duration | Focus | Status |
|-------|----------|-------|:------:|
| **A** | Days 1-3 | Foundation (channel setup, pinned msg, branding) | 🟡 Next |
| **B** | Days 4-7 | Content Bank (write all 30 evergreen posts) | ⬜ Waiting |
| **C** | Days 8-9 | Automation (calendar, scheduling, workflow) | ⬜ Waiting |
| **D** | Day 10 | Launch (first posts live, cross-promote) | ⬜ Waiting |
| **E** | Ongoing | Operation (daily posting, weekly review, monthly optimization) | ⬜ Waiting |

---

## Phase A — Foundation (Days 1-3)

### Deliverables

| # | Task | Output File | Status |
|---|------|-------------|:------:|
| A.1 | Write channel description/bio (Arabic, brand voice) | `content/channel-description.md` | ⬜ |
| A.2 | Write pinned message (the "homepage") | `content/pinned-message.md` | ⬜ |
| A.3 | Decide channel username | Noted in PROGRESS.md | ⬜ |
| A.4 | Link discussion group (@empireenglishcommunity) | Manual action | ⬜ |
| A.5 | Write discussion group rules | `content/discussion-group-rules.md` | ⬜ |
| A.6 | Design post footer/signature convention | Noted in 03-BRAND-VOICE.md | ⬜ |

### Acceptance Criteria
- Channel description is < 200 characters, Arabic, communicates value proposition
- Pinned message answers: What is EEC? Why stay? What do I do next?
- Discussion group is linked and has clear rules posted

---

## Phase B — Content Bank (Days 4-7)

### Deliverables

| # | Task | Output Files | Count | Status |
|---|------|-------------|:-----:|:------:|
| B.1 | Write Accent Lesson posts | `content/accent-lessons/AL-01.md` → `AL-09.md` | 9 | ⬜ |
| B.2 | Write Myth Destroyer posts | `content/myth-destroyers/MD-01.md` → `MD-06.md` | 6 | ⬜ |
| B.3 | Write System Reveal posts | `content/system-reveals/SR-01.md` → `SR-06.md` | 6 | ⬜ |
| B.4 | Write Social Proof posts | `content/social-proof/SP-01.md` → `SP-05.md` | 5 | ⬜ |
| B.5 | Write Brand Story posts | `content/brand-stories/BS-01.md` → `BS-04.md` | 4 | ⬜ |
| B.6 | Write Invitation posts | `content/invitations/IN-01.md` → `IN-03.md` | 3 | ⬜ |
| B.7 | Write voice note scripts for AL posts | Included in AL files | 9 | ⬜ |
| B.8 | Record voice notes (human task) | `assets/voice-notes/` | 9 | ⬜ |

### Writing Order (recommended)
1. Accent Lessons first (these are the strongest content — lead with your best)
2. Myth Destroyers (easy to write, high engagement)
3. System Reveals (explain the system — requires knowing it well)
4. Social Proof (may need real data — use templates/placeholders where needed)
5. Brand Stories (personal — write these yourself or dictate and we format)
6. Invitations (write last — they depend on knowing what the other posts set up)

### Acceptance Criteria
- Each post file contains: the full post text (ready to paste into Telegram), format type noted, pillar code noted
- Voice note posts include the script to read when recording
- All posts follow templates from 03-BRAND-VOICE.md
- No post exceeds 300 words (Telegram readability limit for Arabic)

---

## Phase C — Automation & Workflow (Days 8-9)

### Deliverables

| # | Task | Output | Status |
|---|------|--------|:------:|
| C.1 | Create master content calendar (4 weeks mapped) | `calendar/MASTER-CALENDAR.md` | ⬜ |
| C.2 | Create reusable weekly template | `calendar/weekly-templates/standard-week.md` | ⬜ |
| C.3 | Define posting workflow (daily routine) | Documented in this file | ⬜ |
| C.4 | Set up tracking sheet (views, forwards, growth) | Google Sheet or in-repo | ⬜ |
| C.5 | (Optional) n8n scheduled posting workflow | If feasible | ⬜ |

### Daily Posting Routine (15-20 minutes)

```
9:00 AM Dubai — Posting Window

1. Open content calendar → find today's post
2. Open the post file → copy text
3. If voice note day: record (script is in the file)
4. Paste into Telegram → attach media if any → Send
5. Check discussion group briefly (2 min) — answer any direct questions

Done. Move on with your day.
```

### Weekly Routine (30 min, Sunday evening)

```
1. Review this week's posts — note view counts
2. Check: did any post get unusually high/low engagement? Note why.
3. Queue next week's posts (mark them in calendar)
4. Write one new post to replenish the bank (optional)
```

### Monthly Routine (1 hour, first Saturday)

```
1. Write "State of the Empire" monthly post
2. Review: subscriber growth, avg views, forwards
3. Identify best-performing pillar — do more of it next month
4. Replenish content bank (write 4-6 new posts to replace used ones)
5. Plan any special content (events, launches, seasonal)
6. Update PROGRESS.md with monthly checkpoint
```

---

## Phase D — Launch (Day 10)

### Deliverables

| # | Task | Status |
|---|------|:------:|
| D.1 | Post pinned message to channel | ⬜ |
| D.2 | Post first Saturday "3 American Sounds" lesson | ⬜ |
| D.3 | Announce channel in: Telegram bot flow, Discord, discussion group | ⬜ |
| D.4 | Add channel link to: website, assessment page, all touchpoints | ⬜ |
| D.5 | Update Telegram bot to mention channel in welcome/menu | ⬜ |

### Launch Checklist
- [ ] Channel description is set
- [ ] Pinned message is posted
- [ ] Discussion group is linked
- [ ] At least 7 posts are ready (first full week)
- [ ] Channel link added to bot welcome message
- [ ] Channel link added to assessment registration page
- [ ] Channel link added to Discord #announcements

---

## Phase E — Ongoing Operation

### Success Indicators (Track Weekly)

| Signal | Healthy | Concerning | Action Needed |
|--------|---------|-----------|---------------|
| Posts published this week | 5/5 | 4/5 | < 4 — something is wrong |
| Avg views per post | 30%+ of subscribers | 20-30% | < 20% — content quality issue |
| New subscribers this week | Any growth | Flat | Negative — check cross-promotion |
| Discussion group messages | Active daily | Quiet | Dead — seed with questions |
| Forwards | 3+ per post | 1-2 | 0 — posts aren't share-worthy |

### Content Bank Replenishment Schedule

| Month | New Posts to Write | Type |
|-------|:-----------------:|------|
| Month 1 | 0 (using initial bank) | — |
| Month 2 | 6 (replace used content) | Mix of all pillars |
| Month 3 | 6 | Add new topics based on audience questions |
| Month 4+ | 4-6/month | Sustainable rhythm |

### Scaling Triggers

| Subscriber Count | Action |
|:----------------:|--------|
| 100 | Celebrate publicly + invite wave |
| 250 | Start email capture (add to bot flow) |
| 500 | Evaluate: what's working best? Double down. |
| 1,000 | Consider Telegram Ads, consider paid content |
| 2,000 | Evaluate: is Telegram still primary? Or time for app/web shift? |

---

## Dependencies & Blockers

| Dependency | Required For | Who |
|------------|-------------|-----|
| Channel username decided | Phase A | Human (you) |
| Voice recordings done | Phase B completion | Human (you) |
| Real student recordings for SP posts | Social Proof posts | Requires active students |
| Canva/image template for "Empire Word" | Tuesday posts | Human or AI |

---

## Risk Mitigations Built Into the Plan

| Risk | How This Plan Mitigates It |
|------|---------------------------|
| Motivation drops after 2 weeks | 30-post bank means "just hit send" — no creative energy needed daily |
| Content feels repetitive | 6 different pillars rotate — variety built in |
| No time to create content | Batch-writing (Phase B) decouples creation from publishing |
| Channel feels dead with low subscribers | Content quality compounds — early posts attract future shares |
| Platform risk (Telegram changes) | Email capture starts at 250 subscribers |

---

*For locked decisions that should NOT be changed, see `05-DECISIONS.md`.*
