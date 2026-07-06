"""
Event triggers — auto-post to channel when events happen in the EEC ecosystem.

Currently monitors:
- Assessment completions (student finishes all 4 trials with a score)

Polls the assessment SQLite DB every 30 minutes for new completed assessments.
"""
import asyncio
import sqlite3
import os
import random
from datetime import datetime, timedelta

import config

# Assessment DB path (same server)
ASSESSMENT_DB = "/opt/empire-assessment/db/assessment.db"

# Track what we've already posted about (avoid duplicates)
POSTED_FILE = "data/posted_assessments.txt"

# Templates for auto-generated social proof posts
COMPLETION_TEMPLATES = [
    "🔥 عضو جديد أكمل امتحان تحديد المستوى.\n\nالنتيجة: {score}/١٢٠\nالمستوى: {level}\n\n⚡ كل يوم ناس جديدة بتكتشف مستواها الحقيقي.\nالامتحان مجاني — ٢٠ دقيقة.\n\nassessment.empireenglish.online\n\n━━━━━━━━━\n🏛️ Empire English Community",
    "🔥 واحد كمان عرف مستواه الحقيقي.\n\nالامتحان: ٤ أقسام (قراءة + استماع + كلام + كتابة)\nالنتيجة: {score}/١٢٠\nالمستوى: {level}\n\n⚡ ده مش اختبار ترفيهي — ده تشخيص.\nكل واحد بيجيله مسار مختلف.\n\nمجاني. ٢٠ دقيقة. جرّب.\n\n━━━━━━━━━\n🏛️ Empire English Community",
    "🔥 نتيجة جديدة في النظام.\n\n{score}/١٢٠ — مستوى {level}\n\n⚡ الامتحان بيقولك بالظبط:\n• فين نقط قوتك\n• فين نقط ضعفك\n• إيه اللي محتاج تشتغل عليه\n\nمش \"مستواك متوسط\" وخلاص.\nده تشخيص بالأرقام.\n\nassessment.empireenglish.online\n\n━━━━━━━━━\n🏛️ Empire English Community",
]

# Map numeric level to Arabic name
LEVEL_NAMES = {
    0: "مبتدئ (المستوى ٠)",
    1: "البقاء (المستوى ١)",
    2: "التواصل (المستوى ٢)",
    3: "الطلاقة (المستوى ٣)",
}


def _get_posted_ids():
    """Get set of assessment IDs we've already posted about."""
    if not os.path.exists(POSTED_FILE):
        return set()
    with open(POSTED_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())


def _mark_as_posted(assessment_id):
    """Mark an assessment as posted."""
    os.makedirs(os.path.dirname(POSTED_FILE) if os.path.dirname(POSTED_FILE) else "data", exist_ok=True)
    with open(POSTED_FILE, "a") as f:
        f.write(f"{assessment_id}\n")


async def check_new_assessments(client):
    """Check for new completed assessments and post about them."""
    if not os.path.exists(ASSESSMENT_DB):
        return

    posted_ids = _get_posted_ids()

    try:
        conn = sqlite3.connect(ASSESSMENT_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Find completed assessments from the last 24 hours
        # that we haven't posted about yet
        yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
        cursor.execute("""
            SELECT id, totalScore, cefrLevel, createdAt
            FROM assessments
            WHERE totalScore IS NOT NULL
            AND totalScore > 0
            AND createdAt > ?
            AND status = 'completed'
            ORDER BY createdAt DESC
            LIMIT 5
        """, (yesterday,))

        rows = cursor.fetchall()
        conn.close()

        new_completions = [r for r in rows if str(r["id"]) not in posted_ids]

        if not new_completions:
            return

        # Post about the most recent one (don't spam)
        latest = new_completions[0]
        score = int(latest["totalScore"]) if latest["totalScore"] else 0
        cefr = latest["cefrLevel"] or "A1"

        # Determine Empire level from score
        if score < 32:
            level_num = 0
        elif score < 60:
            level_num = 1
        elif score < 94:
            level_num = 2
        else:
            level_num = 3

        level_name = LEVEL_NAMES.get(level_num, "مبتدئ (المستوى ٠)")

        # Pick a random template and fill it
        template = random.choice(COMPLETION_TEMPLATES)
        post_text = template.format(score=score, level=level_name)

        # Post to channel
        try:
            with open("data/channel_id.txt", "r") as f:
                channel_id = int(f.read().strip().split("\n")[0])
            channel = await client.get_entity(channel_id)
            await client.send_message(channel, post_text)
            print(f"  🎉 Event post: assessment completed (score: {score}/120)")

            # Mark as posted
            _mark_as_posted(str(latest["id"]))

        except Exception as e:
            print(f"  ⚠️ Event post failed: {e}")

    except sqlite3.OperationalError as e:
        # DB might be locked or table doesn't exist
        print(f"  ⚠️ Assessment DB error: {e}")
    except Exception as e:
        print(f"  ⚠️ Event trigger error: {e}")
