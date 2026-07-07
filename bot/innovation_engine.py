"""
Innovation engine — Phase 4 features.
These activate automatically based on subscriber count or time triggers.
Built now, runs when ready.
"""
import asyncio
import json
import os
import random
from datetime import datetime, timedelta

import config


# ══════════════════════════════════════════════════════════════
# 4.1 — VOICE CHALLENGES
# Posts a pronunciation challenge every 2 weeks.
# Subscribers record themselves and send to the discussion group.
# ══════════════════════════════════════════════════════════════

VOICE_CHALLENGES = [
    {
        "word": "entrepreneurship",
        "text": "🎤 تحدي الأسبوع\n\nالكلمة: entrepreneurship\n\nسجّل نفسك بتقولها.\nابعت التسجيل في المجموعة.\n\nأحسن نطق هياخد mention في بوست بكره.\n\n⚡ النطق الصح: on-truh-pruh-NUR-ship\n\nجرّب. سجّل. ابعت.\n\n━━━━━━━━━\n🏛️ Empire English Community"
    },
    {
        "word": "comfortable",
        "text": "🎤 تحدي الأسبوع\n\nالكلمة: comfortable\n\nسجّل نفسك بتقولها.\nابعت التسجيل في المجموعة.\n\n⚡ تلميح: ٣ مقاطع بس — مش ٤.\nCOMF-ter-bl.\n\nمين هيقولها صح؟\n\n━━━━━━━━━\n🏛️ Empire English Community"
    },
    {
        "word": "world",
        "text": "🎤 تحدي الأسبوع\n\nالكلمة: world\n\nأصعب كلمة على المصريين.\nسجّل نفسك بتقولها.\nابعت في المجموعة.\n\n⚡ تلميح: مقطع واحد — werld.\nلسانك بيتلف لورا — مش بيلمس حاجة.\n\nيلا شوف مين يقدر.\n\n━━━━━━━━━\n🏛️ Empire English Community"
    },
    {
        "word": "three things I think",
        "text": "🎤 تحدي الأسبوع\n\nالجملة: \"Three things I think about\"\n\nفيها TH مرتين + الـ R + ربط.\nسجّل نفسك بتقولها بسرعة طبيعية.\n\n⚡ لو قدرت تقولها من غير ما تقف — أنت ماشي صح.\n\nابعت التسجيل في المجموعة.\n\n━━━━━━━━━\n🏛️ Empire English Community"
    },
    {
        "word": "I want to get a cup of coffee",
        "text": "🎤 تحدي الأسبوع\n\nالجملة: \"I want to get a cup of coffee\"\n\nلو قولتها كلمة كلمة — غلط.\nلازم تبقى: \"I wanna gedda cuppa coffee\"\n\nسجّل نفسك.\nابعت في المجموعة.\n\n⚡ اللي يقولها طبيعي — هياخد mention.\n\n━━━━━━━━━\n🏛️ Empire English Community"
    },
]

CHALLENGE_STATE_FILE = "data/last_challenge.json"


async def post_voice_challenge(client, channel):
    """Post a voice challenge every 2 weeks (Thursday)."""
    today = datetime.now()

    # Only Thursday
    if today.weekday() != 3:
        return

    # Only every 2 weeks (odd weeks)
    week_num = today.isocalendar()[1]
    if week_num % 2 == 0:
        return

    # Check if already posted this week
    if os.path.exists(CHALLENGE_STATE_FILE):
        with open(CHALLENGE_STATE_FILE, "r") as f:
            state = json.load(f)
        if state.get("last_week") == week_num:
            return
    else:
        state = {}

    # Pick a challenge
    used = state.get("used_indices", [])
    available = [i for i in range(len(VOICE_CHALLENGES)) if i not in used]
    if not available:
        available = list(range(len(VOICE_CHALLENGES)))
        used = []

    idx = random.choice(available)
    challenge = VOICE_CHALLENGES[idx]

    try:
        await client.send_message(channel, challenge["text"])
        used.append(idx)
        state["last_week"] = week_num
        state["used_indices"] = used
        with open(CHALLENGE_STATE_FILE, "w") as f:
            json.dump(state, f)
        print(f"  🎤 Voice challenge posted: {challenge['word']}")
    except Exception as e:
        print(f"  ⚠️ Voice challenge error: {e}")


# ══════════════════════════════════════════════════════════════
# 4.3 — SECRET CODES
# Randomly adds a secret code to ~10% of posts.
# First person to DM the bot with the code gets mentioned.
# ══════════════════════════════════════════════════════════════

SECRET_CODES = [
    "EMPIRE2026", "GOLDEN", "PHONEME44", "ACCENT", "SHADOW",
    "LINK", "STRESS", "RHYTHM", "SCHWA", "FLUENT",
]

SECRET_CODE_FILE = "data/secret_code_active.json"


def maybe_add_secret_code(post_text: str) -> str:
    """10% chance to add a hidden code to a post."""
    if random.random() > 0.10:  # 90% of the time, don't add
        return post_text

    code = random.choice(SECRET_CODES)

    secret_line = f"\n\n🔑 كود سري: {code}\nأول واحد يبعت الكود ده للبوت @EmpireEnglishBot — هياخد surprise."

    # Save active code
    with open(SECRET_CODE_FILE, "w") as f:
        json.dump({"code": code, "date": datetime.now().isoformat(), "claimed": False}, f)

    return post_text + secret_line


# ══════════════════════════════════════════════════════════════
# 4.5 — AUDIO ROOM ANNOUNCEMENTS
# Announces weekly voice chat schedule every Saturday morning.
# ══════════════════════════════════════════════════════════════

AUDIO_ROOM_TEXT = """🎧 محادثات صوتية هالأسبوع — Empire English

⚡ كل يوم الساعة ٨ مساءً (توقيت دبي)
⚡ إنجليزي بس
⚡ كل المستويات

المكان: مجتمع Discord بتاعنا.
مش محتاج تكون كويس. محتاج تكون موجود.

لو خايف تتكلم — اسمع بس. ده كمان تمرين.

━━━━━━━━━
🏛️ Empire English Community"""


async def announce_audio_room(client, channel):
    """Announce weekly audio room (Saturday morning, after main post)."""
    today = datetime.now()
    if today.weekday() != 5:  # Saturday only
        return

    # Check if already announced this week
    announce_file = "data/last_audio_announce.txt"
    week_str = today.strftime("%Y-W%W")
    if os.path.exists(announce_file):
        with open(announce_file, "r") as f:
            if f.read().strip() == week_str:
                return

    try:
        # Wait 4-6 hours after morning post
        delay = random.randint(14400, 21600)
        await asyncio.sleep(delay)
        await client.send_message(channel, AUDIO_ROOM_TEXT)
        with open(announce_file, "w") as f:
            f.write(week_str)
        print(f"  🎧 Audio room announced")
    except Exception as e:
        print(f"  ⚠️ Audio room announce error: {e}")


# ══════════════════════════════════════════════════════════════
# 4.7 — EMAIL CAPTURE (via channel post with CTA)
# Posts an email capture CTA once per month.
# Directs people to bot or form for email collection.
# ══════════════════════════════════════════════════════════════

EMAIL_CAPTURE_TEXT = """📧 عايز تفضل متابع — حتى لو تيليجرام حصلها حاجة؟

سجّل إيميلك وهنبعتلك:
⚡ ملخص أسبوعي بأهم المحتوى
⚡ نصايح حصرية مش بتنزل هنا
⚡ إشعار لو فيه حاجة جديدة كبيرة

🔗 ابعت إيميلك للبوت: @EmpireEnglishBot
(اكتب: email ثم الإيميل بتاعك)

━━━━━━━━━
🏛️ Empire English Community"""

EMAIL_STATE_FILE = "data/last_email_capture.txt"


async def post_email_capture(client, channel):
    """Post email capture CTA once per month."""
    today = datetime.now()
    month_str = today.strftime("%Y-%m")

    if os.path.exists(EMAIL_STATE_FILE):
        with open(EMAIL_STATE_FILE, "r") as f:
            if f.read().strip() == month_str:
                return

    # Only post on the 15th (mid-month)
    if today.day != 15:
        return

    try:
        await client.send_message(channel, EMAIL_CAPTURE_TEXT)
        with open(EMAIL_STATE_FILE, "w") as f:
            f.write(month_str)
        print(f"  📧 Email capture CTA posted")
    except Exception as e:
        print(f"  ⚠️ Email capture error: {e}")


# ══════════════════════════════════════════════════════════════
# 4.8 — REFERRAL POST
# Posts referral CTA once per month (different week from email).
# ══════════════════════════════════════════════════════════════

REFERRAL_TEXT = """🔗 شارك القناة — ساعد حد يبدأ.

لو عندك صاحب/صاحبة عايز/عايزة يتعلم إنجليزي — ابعتله القناة.

مش عشاننا. عشانه.
عشان ممكن ده يبقى أول خطوة بتغيّر حياته.

🔗 https://t.me/Empire_English_Community

━━━━━━━━━
🏛️ Empire English Community"""

REFERRAL_STATE_FILE = "data/last_referral.txt"


async def post_referral(client, channel):
    """Post referral CTA once per month (22nd)."""
    today = datetime.now()
    month_str = today.strftime("%Y-%m")

    if os.path.exists(REFERRAL_STATE_FILE):
        with open(REFERRAL_STATE_FILE, "r") as f:
            if f.read().strip() == month_str:
                return

    # Only post on the 22nd
    if today.day != 22:
        return

    try:
        await client.send_message(channel, REFERRAL_TEXT)
        with open(REFERRAL_STATE_FILE, "w") as f:
            f.write(month_str)
        print(f"  🔗 Referral CTA posted")
    except Exception as e:
        print(f"  ⚠️ Referral error: {e}")
