"""
Engagement engine — seeds discussion group with follow-up content.
Makes the channel ecosystem feel alive throughout the day.
"""
import random
import asyncio
import config


# Follow-up prompts per pillar (posted in discussion group after channel post)
FOLLOW_UP_PROMPTS = {
    "accent_lesson": [
        "💬 مين فيكم بيقع في الغلطة دي؟",
        "💬 جرّبت تسجّل نفسك؟ إيه اللي لاحظته؟",
        "💬 إيه أصعب sound بالنسبالك لحد دلوقتي؟",
        "💬 لو عندك كلمة تانية فيها نفس الصوت — اكتبها هنا",
    ],
    "myth_destroyer": [
        "💬 كنت مصدّق الكلام ده قبل كده؟",
        "💬 إيه أكبر myth انت شخصيًا كنت مصدقه عن الإنجليزي؟",
        "💬 مين قالك الكلام ده وانت صغير؟",
    ],
    "system_reveal": [
        "💬 إيه الجزء ده اللي لفت نظرك أكتر؟",
        "💬 لو عندك سؤال عن النظام — اكتبه هنا وهنجاوبك",
        "💬 إيه أكتر حاجة عايز تعرف عنها جوه Empire؟",
    ],
    "social_proof": [
        "💬 إيه اللي ناقصك عشان تبدأ؟",
        "💬 لو بدأت — إيه أول حاجة هتركّز عليها؟",
        "🗳 أنت فين دلوقتي؟\n🅰️ مبتدئ تمامًا\n🅱️ بعرف شوية بس\n🅲️ متوسط\n🅳️ كويس بس عايز accent",
    ],
    "brand_story": [
        "💬 إيه اللي خلّاك تفكر تتعلم إنجليزي أصلًا؟",
        "💬 لو حققت هدفك — إيه أول حاجة هتعملها؟",
    ],
}

BONUS_TIPS = [
    "💡 Tip: سجّل نفسك كل يوم ٣٠ ثانية بس. بعد أسبوع هتسمع الفرق.",
    "💡 Tip: مش لازم تفهم كل كلمة — لازم تفهم المعنى العام. ده الهدف.",
    "💡 Tip: أحسن وقت تتمرّن هو أول ٢٠ دقيقة لما تصحى.",
    "💡 Tip: لو خايف تغلط — ده بالظبط اللي هيوقّفك. الغلط هو الطريق.",
    "💡 Tip: Shadowing ١٥ دقيقة يومي > course ساعتين في الأسبوع.",
    "💡 Tip: اسمع نفس الـ clip ٥ مرات. المرة الخامسة هتبدأ تلاحظ حاجات ما لاحظتهاش.",
]


async def seed_discussion_group(client, post_text: str, pillar: str):
    """Post follow-up content in the discussion group after a channel post."""
    try:
        group = await client.get_entity(f"@{config.DISCUSSION_GROUP_USERNAME}")
    except Exception as e:
        print(f"  ⚠️ Could not find discussion group: {e}")
        return

    # 1. Immediate: forward prompt (1-2 min after post)
    await asyncio.sleep(random.randint(60, 120))
    prompts = FOLLOW_UP_PROMPTS.get(pillar, FOLLOW_UP_PROMPTS["accent_lesson"])
    prompt = random.choice(prompts)
    await client.send_message(group, prompt)
    print(f"  💬 Discussion prompt sent: {prompt[:40]}...")

    # 2. Delayed: bonus tip (2-4 hours later)
    # Schedule this as a background task
    asyncio.create_task(_delayed_tip(client, group))


async def _delayed_tip(client, group):
    """Send a bonus tip after a random delay (2-4 hours)."""
    delay = random.randint(7200, 14400)  # 2-4 hours
    await asyncio.sleep(delay)
    tip = random.choice(BONUS_TIPS)
    try:
        await client.send_message(group, tip)
        print(f"  💡 Bonus tip sent after {delay//3600}h")
    except Exception as e:
        print(f"  ⚠️ Bonus tip failed: {e}")
