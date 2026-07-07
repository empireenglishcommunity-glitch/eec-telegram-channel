"""
Best-of recycling — after 8 weeks, re-post top performers for new subscribers.
Checks analytics data for posts with highest views and re-posts them.
"""
import json
import os
from datetime import datetime, timedelta

ANALYTICS_FILE = "data/analytics.json"
BESTOF_FILE = "data/last_bestof.txt"


async def check_bestof(client) -> tuple[str | None, int | None]:
    """
    Check if it's time for a 'best of' re-post.
    Runs once per month (first Sunday after 8 weeks of data).
    Returns (post_text, original_msg_id) or (None, None).
    """
    # Only run on first Sunday of the month
    today = datetime.now()
    if today.weekday() != 6 or today.day > 7:
        return None, None

    # Check if we already did best-of this month
    if os.path.exists(BESTOF_FILE):
        with open(BESTOF_FILE, "r") as f:
            last_month = f.read().strip()
        if last_month == today.strftime("%Y-%m"):
            return None, None

    # Check if we have 8 weeks of data
    if not os.path.exists(ANALYTICS_FILE):
        return None, None

    with open(ANALYTICS_FILE, "r", encoding="utf-8") as f:
        analytics = json.load(f)

    # Filter entries with views data
    with_views = [a for a in analytics if a.get("views_24h") is not None and a["views_24h"] > 0]

    if len(with_views) < 20:  # Need at least 20 posts with view data
        return None, None

    # Sort by views (highest first)
    with_views.sort(key=lambda a: a["views_24h"], reverse=True)

    # Pick the top post
    best = with_views[0]

    # Mark as done this month
    with open(BESTOF_FILE, "w") as f:
        f.write(today.strftime("%Y-%m"))

    return best, best.get("msg_id")


async def post_bestof(client, channel):
    """Check and post best-of if conditions are met."""
    result, msg_id = await check_bestof(client)

    if not result:
        return

    views = result.get("views_24h", 0)
    pillar = result.get("pillar", "")

    bestof_text = f"""🔥 الأكتر مشاهدة الشهر ده — {views} مشاهدة

ده البوست اللي الناس حبته أكتر الشهر اللي فات.
لو فاتك — اقرأه دلوقتي.

━━━━━━━━━
🏛️ Empire English Community"""

    try:
        # Forward the original message
        if msg_id:
            await client.forward_messages(channel, msg_id, channel)
        # Then post the "best of" label
        await client.send_message(channel, bestof_text)
        print(f"  🔥 Best-of posted (msg {msg_id}, {views} views)")
    except Exception as e:
        print(f"  ⚠️ Best-of error: {e}")
