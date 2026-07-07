"""
EEC Channel Bot — Full Autopilot Engine.
Handles daily posting, AI content generation, reactions, and engagement.

This script runs 24/7 on the server as a systemd service.
"""
import asyncio
import random
import json
import os
from datetime import datetime, timedelta

from telethon import TelegramClient
from telethon.tl.types import ReactionEmoji
from telethon.tl.functions.messages import SendReactionRequest
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import config
from content_engine import generate_post, get_bank_post
from image_engine import generate_image
from engagement_engine import seed_discussion_group
from event_triggers import check_new_assessments

# Global client
client: TelegramClient = None
scheduler: AsyncIOScheduler = None


async def get_channel():
    """Get the channel entity."""
    try:
        with open("data/channel_id.txt", "r") as f:
            lines = f.read().strip().split("\n")
            channel_id = int(lines[0])
        return await client.get_entity(channel_id)
    except FileNotFoundError:
        # Fallback: get by username
        return await client.get_entity(f"@{config.CHANNEL_USERNAME}")


async def daily_post_with_jitter():
    """Adds random 0-20 min delay before posting (makes timing look human)."""
    jitter = random.randint(0, 1200)  # 0 to 20 minutes
    print(f"[{datetime.now()}] Post jitter: waiting {jitter//60} min...")
    await asyncio.sleep(jitter)
    await daily_post()


async def daily_post():
    """Main daily posting routine — fires at 9 AM Dubai (±10 min jitter)."""
    today = datetime.now().weekday()

    # Friday = OFF
    if today == 4:
        print(f"[{datetime.now()}] Friday — no post today")
        return

    # Deduplication: check if we already posted today
    today_str = datetime.now().strftime("%Y-%m-%d")
    dedup_file = "data/last_post_date.txt"
    if os.path.exists(dedup_file):
        with open(dedup_file, "r") as f:
            last_date = f.read().strip()
        if last_date == today_str:
            print(f"[{datetime.now()}] Already posted today — skipping")
            return

    # Thursday alternation: even weeks = brand_story, odd weeks = invitation
    pillar = config.PILLAR_SCHEDULE.get(today, "accent_lesson")
    if pillar == "alternating":
        week_number = datetime.now().isocalendar()[1]
        pillar = "brand_story" if week_number % 2 == 0 else "invitation"

    print(f"[{datetime.now()}] Daily post — pillar: {pillar}")

    try:
        # 1. Generate content (from bank)
        post_text, metadata = await generate_post(pillar)
        if not post_text:
            post_text, metadata = await get_bank_post(pillar)

        if not post_text:
            print("  ❌ No content available — skipping today")
            return

        # 2. Generate image (using HTML templates)
        image_path = await generate_image(pillar, post_text, metadata)

        # 3. Post to channel
        channel = await get_channel()
        if image_path and os.path.exists(image_path):
            msg = await client.send_file(
                channel,
                image_path,
                caption=post_text,
            )
            # Clean up temp image
            os.remove(image_path)
        else:
            msg = await client.send_message(channel, post_text)

        print(f"  ✅ Posted (msg_id: {msg.id})")

        # Mark today as posted (deduplication)
        with open("data/last_post_date.txt", "w") as f:
            f.write(datetime.now().strftime("%Y-%m-%d"))

        # 4. Schedule reactions (staggered throughout the day)
        await schedule_reactions(channel, msg.id)

        # 5. Seed discussion group
        await seed_discussion_group(client, post_text, pillar)

        print(f"  ✅ Reactions scheduled + group seeded")

    except Exception as e:
        print(f"  ❌ Error in daily_post: {e}")
        # Send alert to your personal chat
        try:
            await client.send_message(
                "me",
                f"⚠️ EEC Channel Bot Error:\n{str(e)[:500]}"
            )
        except:
            pass


async def schedule_reactions(channel, message_id):
    """Schedule staggered reactions using reaction bot tokens."""
    # Load reaction bot tokens
    token_file = "data/reaction_bot_tokens.txt"
    if not os.path.exists(token_file):
        print("  ⚠️ No reaction bot tokens found")
        return

    with open(token_file, "r") as f:
        tokens = [line.strip() for line in f if line.strip()]

    if not tokens:
        print("  ⚠️ No reaction bot tokens")
        return

    # Get channel ID for Bot API (needs -100 prefix)
    with open("data/channel_id.txt", "r") as f:
        channel_id = int(f.read().strip().split("\n")[0])
    chat_id = int(f"-100{channel_id}")

    # Each bot reacts once, with staggered timing
    # For 100 members: 8-12 reactions looks natural
    # Randomly skip some bots (not all react every time = more natural)
    selected_tokens = tokens if len(tokens) <= 5 else random.sample(tokens, random.randint(min(6, len(tokens)), len(tokens)))

    for i, token in enumerate(selected_tokens):
        # Stagger: earlier bots react sooner, later ones spread out
        if i < 2:
            delay = random.randint(600, 2400)     # 10-40 min
        elif i < 5:
            delay = random.randint(2400, 7200)    # 40 min - 2 hours
        elif i < 8:
            delay = random.randint(7200, 14400)   # 2-4 hours
        else:
            delay = random.randint(14400, 25200)  # 4-7 hours

        delay += random.randint(-120, 120)  # Jitter
        delay = max(300, delay)

        emoji = random.choice(config.REACTION_EMOJIS)

        asyncio.create_task(_bot_reaction(token, chat_id, message_id, emoji, delay, i))

    print(f"  ⏱️ {len(selected_tokens)} reactions scheduled (staggered over hours)")


async def _bot_reaction(token: str, chat_id: int, message_id: int, emoji: str, delay: int, index: int):
    """Wait and then react using Bot API."""
    await asyncio.sleep(delay)
    try:
        import aiohttp
        url = f"https://api.telegram.org/bot{token}/setMessageReaction"
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "reaction": [{"type": "emoji", "emoji": emoji}],
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    mins = delay // 60
                    print(f"  👍 Bot {index+1} reacted {emoji} (after {mins}min)")
                else:
                    error = await resp.text()
                    print(f"  ⚠️ Bot {index+1} reaction failed: {error[:100]}")
    except Exception as e:
        print(f"  ⚠️ Bot {index+1} reaction error: {e}")


async def weekly_generate():
    """Generate next week's content (runs Sunday 2 AM Dubai = Saturday 10 PM UTC)."""
    print(f"[{datetime.now()}] Weekly generation — creating 6 posts...")
    from content_engine import generate_weekly_batch
    await generate_weekly_batch()
    print(f"  ✅ Weekly batch generated")


async def health_check():
    """Daily health check (runs 11 PM Dubai)."""
    print(f"[{datetime.now()}] Health check")
    try:
        channel = await get_channel()
        full = await client.get_entity(channel)
        print(f"  Channel: {full.title}")
        print(f"  Health: OK")
    except Exception as e:
        print(f"  ❌ Health check failed: {e}")
        await client.send_message("me", f"⚠️ EEC Bot health check failed: {e}")


async def event_check():
    """Check for new events (assessments, milestones) every 30 min."""
    try:
        await check_new_assessments(client)
    except Exception as e:
        print(f"  ⚠️ Event check error: {e}")


async def start():
    """Start the bot."""
    global client, scheduler

    print("=" * 50)
    print("🏛️ EEC Channel Bot — Starting")
    print("=" * 50)

    # Connect to Telegram
    client = TelegramClient("eec_session", config.API_ID, config.API_HASH)
    await client.start(phone=config.PHONE_NUMBER)
    me = await client.get_me()
    print(f"✅ Logged in as: {me.first_name} ({me.phone})")

    # Setup scheduler
    scheduler = AsyncIOScheduler(timezone="Asia/Dubai")

    # Daily post at 9:00 AM Dubai (with jitter added inside daily_post)
    scheduler.add_job(
        daily_post_with_jitter,
        CronTrigger(hour=8, minute=50, timezone="Asia/Dubai"),
        id="daily_post",
        replace_existing=True,
    )

    # Weekly generation: Sunday 2:00 AM Dubai
    scheduler.add_job(
        weekly_generate,
        CronTrigger(day_of_week="sun", hour=2, minute=0, timezone="Asia/Dubai"),
        id="weekly_generate",
        replace_existing=True,
    )

    # Daily health check: 11:00 PM Dubai
    scheduler.add_job(
        health_check,
        CronTrigger(hour=23, minute=0, timezone="Asia/Dubai"),
        id="health_check",
        replace_existing=True,
    )

    # Event triggers: check every 30 minutes for new assessments
    scheduler.add_job(
        event_check,
        "interval",
        minutes=30,
        id="event_check",
        replace_existing=True,
    )

    scheduler.start()
    print(f"\n📅 Scheduled:")
    print(f"   • Daily post: 9:00 AM Dubai (Sat-Thu)")
    print(f"   • Weekly generation: Sunday 2:00 AM Dubai")
    print(f"   • Health check: 11:00 PM Dubai")
    print(f"   • Event triggers: every 30 minutes")
    print(f"\n🏛️ Bot is running. Press Ctrl+C to stop.\n")

    # Keep running
    await client.run_until_disconnected()


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    asyncio.run(start())
