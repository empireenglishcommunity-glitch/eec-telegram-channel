# 05 — Locked Design Decisions

> **Document:** Decisions made and LOCKED. Do not revisit unless explicitly asked by the owner.
> **Purpose:** Prevents decision fatigue and scope creep across sessions.

---

## Locked Decisions

These were debated, decided, and should NOT be changed by any future agent or session without the owner's explicit request:

| # | Decision | Choice | Rationale | Date Locked |
|---|----------|--------|-----------|:-----------:|
| 1 | Primary language | Egyptian Arabic (masri) | Audience is Egyptian/Gulf. English is the subject, not the interface. | 2026-07-06 |
| 2 | Posting frequency | 5x/week (Sat-Thu) | Consistent but sustainable for a solo operator. Quality > quantity. | 2026-07-06 |
| 3 | Friday | OFF (no post) | Cultural respect + creates anticipation + prevents burnout. | 2026-07-06 |
| 4 | Posting time | 9:00 AM Dubai (7:00 AM Cairo) | Morning phone check window for target audience. | 2026-07-06 |
| 5 | Content ratio | 80% value / 10% brand / 10% CTA | Trust-first. Channel must never feel like an ad feed. | 2026-07-06 |
| 6 | Voice notes | Yes, weekly (Saturday) | This IS the product demo. Voice = proof of expertise. | 2026-07-06 |
| 7 | Hard selling | NEVER in the channel | Bot does sales. Channel does trust. Separate concerns. | 2026-07-06 |
| 8 | Reposting | Allowed every 6-8 weeks | New subscribers didn't see old posts. No shame in replaying hits. | 2026-07-06 |
| 9 | Discussion group | Linked, moderated, Arabic | Two-way engagement without cluttering the one-way channel. | 2026-07-06 |
| 10 | Email capture | Start at 250 subscribers | Insurance against platform risk. Non-negotiable long-term. | 2026-07-06 |
| 11 | Content pillars | 6 fixed pillars (AL/SP/MD/SR/BS/IN) | Structure prevents "what should I post today?" paralysis. | 2026-07-06 |
| 12 | Channel role | NURTURE only | Not discovery (TikTok), not conversion (bot), not delivery (Discord). | 2026-07-06 |
| 13 | Hashtags | Never | Look amateur in Telegram. Not a discovery mechanism here. | 2026-07-06 |
| 14 | Post length | Max ~300 words | Telegram mobile readability. Arabic text walls are unreadable. | 2026-07-06 |
| 15 | Metrics tracking | Weekly review, monthly optimize | Don't obsess daily. Look at 4-week trends. | 2026-07-06 |
| 16 | Brand posts signed | `ℳ` footer on brand stories only | Subtle brand mark without cluttering every post. | 2026-07-06 |
| 17 | Formal Arabic | NEVER | Creates distance. We speak masri. We ARE the audience. | 2026-07-06 |
| 18 | Content bank size | 30 posts minimum | 6 weeks of content ready before launch. Buffer against burnout. | 2026-07-06 |

---

## Decision-Making Framework (For Future Decisions)

When a new decision needs to be made:

1. **Does it affect the channel's role?** → If yes, check Decision #12. The channel only does NURTURE.
2. **Does it change the posting rhythm?** → If yes, think hard. Consistency is the #1 trust builder.
3. **Does it require daily creative effort?** → If yes, find a way to batch/template it instead.
4. **Does it make the channel feel like a sales channel?** → If yes, it goes in the BOT, not here.
5. **Will a future agent understand why this choice was made?** → If not, document the rationale here.

---

## Decisions NOT Yet Made (Pending)

These will be decided during Phase A execution:

| Decision | Options | Decide By |
|----------|---------|-----------|
| Channel username | @empireengclub / @empireenglishclub / @eec_official / other | Phase A |
| Image template tool | Canva / Figma / AI-generated / simple text only | Phase B |
| Scheduling tool | Manual Telegram scheduled messages / n8n workflow / third-party bot | Phase C |
| Analytics tracking | Google Sheet / Notion / in-repo markdown table | Phase C |

---

*This file is append-only. New decisions are added at the bottom. Existing decisions are never removed — only marked as "superseded" with a date and reason if overridden by the owner.*



---

## Automation Decisions (Locked July 6, 2026)

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| 19 | Human involvement | Zero (fully autonomous) | Owner's explicit requirement — focus on other projects |
| 20 | Content generation | 100% AI-generated (bank as fallback) | Long-term sustainability without human writing |
| 21 | Approval flow | None — auto-approve with quality filter | Zero involvement requirement |
| 22 | Quality guarantee | Multi-layer validation + template-constrained prompts + few-shot examples | Prevents off-brand output without human review |
| 23 | Voice content | Kokoro TTS (not human voice) | Can't automate human recordings; Kokoro is professional |
| 24 | Engagement | Bot reactions (natural pattern) + discussion group seeding | Channel looks active throughout the day |
| 25 | Reaction pattern | 8-12 bots, staggered delays, random emoji, random selection per post | Mimics natural human behavior |
| 26 | AI provider | Groq ONLY (no Gemini ever) | Gemini has limits, rate issues, unreliable free tier |
| 27 | Image generation | Cloudflare Workers AI (FLUX.1 Schnell) | Free (10K neurons/day), already have account, great quality |
| 28 | Failure mode | Evergreen bank fallback → channel NEVER goes silent | Reliability over perfection |
| 29 | Monitoring | Passive alerts only (alert if broken, otherwise silent) | Zero-involvement design |
| 30 | Event triggers | Assessment completion → auto social proof post | Makes channel feel alive with real activity |
| 31 | Scaling reactions | Proportional to subscriber count (never disproportionate) | Avoids detection; looks natural at any scale |
