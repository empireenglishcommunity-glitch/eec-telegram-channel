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


async def daily_post():
    """Main daily posting routine — fires at 9 AM Dubai."""
    today = datetime.now().weekday()

    # Friday = OFF
    if today == 4:
        print(f"[{datetime.now()}] Friday — no post today")
        return

    pillar = config.PILLAR_SCHEDULE.get(today, "accent_lesson")
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
    """Schedule staggered reactions throughout the day."""
    # Decide how many reactions (based on randomness + realism)
    num_reactions = random.randint(4, 8)

    for i in range(num_reactions):
        # Random delay: 15 min to 8 hours, exponentially distributed
        # (more reactions early, fewer late)
        if i < 3:
            # First 3 reactions: 15 min to 2 hours
            delay = random.randint(900, 7200)
        else:
            # Later reactions: 2 to 8 hours
            delay = random.randint(7200, 28800)

        # Add some jitter
        delay += random.randint(-120, 120)
        delay = max(300, delay)  # Minimum 5 minutes

        emoji = random.choice(config.REACTION_EMOJIS)

        # Schedule the reaction
        run_time = datetime.now() + timedelta(seconds=delay)
        scheduler.add_job(
            do_react,
            "date",
            run_date=run_time,
            args=[channel, message_id, emoji],
            id=f"react_{message_id}_{i}",
            replace_existing=True,
        )


async def do_react(channel, message_id, emoji):
    """Add a reaction to a message."""
    try:
        await client(SendReactionRequest(
            peer=channel,
            msg_id=message_id,
            reaction=[ReactionEmoji(emoticon=emoji)]
        ))
        print(f"  👍 Reacted with {emoji} to msg {message_id}")
    except Exception as e:
        print(f"  ⚠️ Reaction failed: {e}")


async def weekly_generate():
    """Generate next week's content (runs Sunday 2 AM Dubai = Saturday 10 PM UTC)."""
    print(f"[{datetime.now()}] Weekly generation — creating 6 posts...")
    from content_engine import generate_weekly_batch
    await generate_weekly_batch()
    print(f"  ✅ Weekly batch generated")


async def health_check():
    """Daily health check (runs 11 PM Dubai)."""
    print(f"[{datetime.now()}] Health check")
    # TODO: Check queue depth, subscriber count, alert if issues
    try:
        channel = await get_channel()
        # Get channel info for stats
        full = await client.get_entity(channel)
        print(f"  Channel: {full.title}")
        print(f"  Health: OK")
    except Exception as e:
        print(f"  ❌ Health check failed: {e}")
        await client.send_message("me", f"⚠️ EEC Bot health check failed: {e}")


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

    # Daily post at 9:00 AM Dubai
    scheduler.add_job(
        daily_post,
        CronTrigger(hour=9, minute=0, timezone="Asia/Dubai"),
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

    scheduler.start()
    print(f"\n📅 Scheduled:")
    print(f"   • Daily post: 9:00 AM Dubai (Sat-Thu)")
    print(f"   • Weekly generation: Sunday 2:00 AM Dubai")
    print(f"   • Health check: 11:00 PM Dubai")
    print(f"\n🏛️ Bot is running. Press Ctrl+C to stop.\n")

    # Keep running
    await client.run_until_disconnected()


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    asyncio.run(start())
