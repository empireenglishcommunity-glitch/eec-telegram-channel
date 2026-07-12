# EEC Telegram Channel — AI Agent Rules

## Session Protocol
Full session commands (`/start`, `/status`, `/sync`, `/sync dry`,
`/checkpoint`) and standing ecosystem-wide rules live in
`empireenglishcommunity-glitch/Kiro-Master-Index/.kiro/steering/AI-AGENT-PROTOCOL.md`.
Read that file at the start of every session before anything below.

## Project Context
This repository contains the content operating system for the Empire English Club Telegram Announcement Channel. It is a trust-building content machine that funnels subscribers toward the EEC assessment and paid community.

## Rules for Any Agent Working on This Repo

### Before Starting
1. Read `PROGRESS.md` FIRST — it tells you exactly where we left off
2. Read `docs/05-DECISIONS.md` — locked decisions that must NOT be changed
3. Check which phase we're in and what tasks remain

### Content Writing Rules
1. ALL channel content is in **Egyptian Arabic (masri dialect)** — NEVER formal Arabic
2. English technical terms stay in English (stress, shadowing, linking, etc.)
3. Follow templates in `docs/03-BRAND-VOICE.md` — don't invent new formats without discussion
4. Every post file must include: pillar code, format type, full post text, and voice note script (if applicable)
5. Max post length: ~300 words (Telegram mobile readability)
6. NEVER include hashtags
7. NEVER write hard-sell copy — the channel builds trust, the bot sells

### File Organization Rules
1. Content goes in `content/[pillar-folder]/[CODE-##-slug].md`
2. Always update `PROGRESS.md` after completing any task
3. Always update `calendar/MASTER-CALENDAR.md` when adding content to the schedule
4. Commit with clear messages: "Add AL-03 Dark L accent lesson post"

### What NOT to Do
- Don't change locked decisions in `docs/05-DECISIONS.md`
- Don't restructure the repo folder layout
- Don't write content in formal Arabic (فصحى)
- Don't add promotional/sales language to value posts
- Don't create posts longer than 300 words
- Don't skip updating PROGRESS.md after work is done

### Connected Systems (Reference)
- Full EEC blueprint: `empireenglishcommunity-glitch/EEC-REPO/docs/strategy/Empire English Community Learning System.md`
- Assessment system: `empireenglishcommunity-glitch/zai-placement-test`
- Telegram sales bot (n8n-based, current per Kiro-Master-Index): `@EmpireEnglishBot` — see `Kiro-Master-Index/README.md` infrastructure table. (Note: `Claude/telegram-assistant/worker.js` is a separate, older, standalone Worker-based bot of unconfirmed live status — do not assume it's the same system.)
- Discord bots (canonical): `empireenglishcommunity-glitch/EEC-REPO/bots/discord-learning-bot/` — NOT `Claude/empire-english-bot/`, which is a confirmed-stale duplicate removed from `Claude` in the 2026-07-12 cleanup.
- Session continuity: `empireenglishcommunity-glitch/Kiro-Master-Index/SESSION_CONTINUITY.md`
