"""
Growth engine — subscriber milestones, analytics logging, monthly report.
"""
import asyncio
import json
import os
import random
from datetime import datetime, timedelta

import config


# Milestone thresholds
MILESTONES = [50, 100, 250, 500, 1000, 2500, 5000, 10000]
MILESTONE_FILE = "data/last_milestone.txt"
ANALYTICS_FILE = "data/analytics.json"

MILESTONE_TEMPLATES = [
    "🏛️ وصلنا {count} عضو في القناة.\n\nمش رقم كبير لسه — بس كل واحد فيكم هنا عشان عايز يتغيّر فعلًا.\n\n⚡ ده مش مجتمع أرقام. ده مجتمع ناس جادة.\n\nشكرًا إنك هنا. والأحسن لسه جاي.\n\n━━━━━━━━━\n🏛️ Empire English Community",
    "🔥 {count} عضو.\n\nكل واحد فيكم اختار يبقى هنا — مش بالصدفة.\n\n⚡ واحنا لسه في البداية.\nاللي جاي أكبر.\n\n━━━━━━━━━\n🏛️ Empire English Community",
]


async def check_subscriber_milestone(client):
    """Check if we hit a new subscriber milestone."""
    try:
        with open("data/channel_id.txt", "r") as f:
            channel_id = int(f.read().strip().split("\n")[0])
        channel = await client.get_entity(channel_id)

        # Get subscriber count
        from telethon.tl.functions.channels import GetFullChannelRequest
        full = await client(GetFullChannelRequest(channel))
        count = full.full_chat.participants_count

        # Check what milestone we last celebrated
        last_milestone = 0
        if os.path.exists(MILESTONE_FILE):
            with open(MILESTONE_FILE, "r") as f:
                last_milestone = int(f.read().strip() or "0")

        # Did we pass a new milestone?
        for milestone in MILESTONES:
            if count >= milestone and milestone > last_milestone:
                # Celebrate!
                template = random.choice(MILESTONE_TEMPLATES)
                post_text = template.format(count=milestone)
                await client.send_message(channel, post_text)
                print(f"  🎉 Milestone: {milestone} subscribers!")

                # Save
                with open(MILESTONE_FILE, "w") as f:
                    f.write(str(milestone))
                break

    except Exception as e:
        print(f"  ⚠️ Milestone check error: {e}")


async def log_analytics(client, post_msg_id: int, pillar: str):
    """Log a post for analytics tracking. Views checked 24h later."""
    analytics = []
    if os.path.exists(ANALYTICS_FILE):
        with open(ANALYTICS_FILE, "r", encoding="utf-8") as f:
            analytics = json.load(f)

    analytics.append({
        "msg_id": post_msg_id,
        "pillar": pillar,
        "date": datetime.now().isoformat(),
        "views_24h": None,  # Filled later
    })

    # Keep only last 100 entries
    analytics = analytics[-100:]

    with open(ANALYTICS_FILE, "w", encoding="utf-8") as f:
        json.dump(analytics, f, ensure_ascii=False, indent=2)


async def check_post_views(client):
    """Check views for posts from 24h ago and update analytics."""
    if not os.path.exists(ANALYTICS_FILE):
        return

    with open(ANALYTICS_FILE, "r", encoding="utf-8") as f:
        analytics = json.load(f)

    updated = False
    now = datetime.now()

    with open("data/channel_id.txt", "r") as f:
        channel_id = int(f.read().strip().split("\n")[0])
    channel = await client.get_entity(channel_id)

    for entry in analytics:
        if entry["views_24h"] is not None:
            continue

        post_date = datetime.fromisoformat(entry["date"])
        if now - post_date < timedelta(hours=23):
            continue

        # Get views for this message
        try:
            msgs = await client.get_messages(channel, ids=entry["msg_id"])
            if msgs and msgs.views:
                entry["views_24h"] = msgs.views
                updated = True
                print(f"  📊 Post {entry['msg_id']} ({entry['pillar']}): {msgs.views} views")
        except:
            pass

    if updated:
        with open(ANALYTICS_FILE, "w", encoding="utf-8") as f:
            json.dump(analytics, f, ensure_ascii=False, indent=2)


async def monthly_state_of_empire(client):
    """Generate and post monthly stats summary (1st Saturday of each month)."""
    now = datetime.now()

    # Only run on first Saturday of the month (day 1-7 + Saturday)
    if now.day > 7 or now.weekday() != 5:
        return

    # Check if we already posted this month
    state_file = "data/last_state_of_empire.txt"
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            last_month = f.read().strip()
        if last_month == now.strftime("%Y-%m"):
            return

    # Get subscriber count
    try:
        with open("data/channel_id.txt", "r") as f:
            channel_id = int(f.read().strip().split("\n")[0])
        channel = await client.get_entity(channel_id)

        from telethon.tl.functions.channels import GetFullChannelRequest
        full = await client(GetFullChannelRequest(channel))
        count = full.full_chat.participants_count

        # Count posts this month from analytics
        posts_this_month = 0
        if os.path.exists(ANALYTICS_FILE):
            with open(ANALYTICS_FILE, "r", encoding="utf-8") as f:
                analytics = json.load(f)
            month_str = now.strftime("%Y-%m")
            posts_this_month = sum(1 for a in analytics if a["date"].startswith(month_str))

        month_name = now.strftime("%B %Y")
        post_text = f"""🏛️ حالة الإمبراطورية — {month_name}

⚡ أرقام الشهر:
• عدد الأعضاء: {count}
• عدد البوستات: {posts_this_month}+
• محتوى يومي: سبت←خميس
• نظام ٢٤/٧: شغال

الشهر الجاي — أكبر.

━━━━━━━━━
🏛️ Empire English Community"""

        await client.send_message(channel, post_text)
        print(f"  🏛️ State of the Empire posted ({month_name})")

        with open(state_file, "w") as f:
            f.write(now.strftime("%Y-%m"))

    except Exception as e:
        print(f"  ⚠️ State of Empire error: {e}")
