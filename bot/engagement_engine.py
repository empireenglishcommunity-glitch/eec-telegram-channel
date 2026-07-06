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
        "💬 إيه أصعب صوت بالنسبالك لحد دلوقتي؟",
        "💬 لو عندك كلمة تانية فيها نفس الصوت — اكتبها هنا",
    ],
    "myth_destroyer": [
        "💬 كنت مصدّق الكلام ده قبل كده؟",
        "💬 إيه أكبر كدبة انت شخصيًا كنت مصدقها عن الإنجليزي؟",
        "💬 مين قالك الكلام ده وانت صغير؟",
    ],
    "system_reveal": [
        "💬 إيه الجزء اللي لفت نظرك أكتر؟",
        "💬 لو عندك سؤال عن النظام — اكتبه هنا",
        "💬 إيه أكتر حاجة عايز تعرف عنها جوه Empire؟",
    ],
    "social_proof": [
        "💬 إيه اللي ناقصك عشان تبدأ؟",
        "💬 لو بدأت — إيه أول حاجة هتركّز عليها؟",
        "🗳 أنت فين دلوقتي؟\n🅰️ مبتدئ تمامًا\n🅱️ بعرف شوية بس\n🅲️ متوسط\n🅳️ كويس بس عايز نطق",
    ],
    "brand_story": [
        "💬 إيه اللي خلّاك تفكر تتعلم إنجليزي أصلًا؟",
        "💬 لو حققت هدفك — إيه أول حاجة هتعملها؟",
    ],
    "invitation": [
        "💬 مين جرّب الامتحان؟ إيه كانت النتيجة؟",
        "💬 إيه اللي مانعك تبدأ؟",
    ],
}

BONUS_TIPS = [
    "💡 سجّل نفسك كل يوم ٣٠ ثانية بس. بعد أسبوع هتسمع الفرق.",
    "💡 مش لازم تفهم كل كلمة — لازم تفهم المعنى العام. ده الهدف.",
    "💡 أحسن وقت تتمرّن هو أول ٢٠ دقيقة لما تصحى.",
    "💡 لو خايف تغلط — ده بالظبط اللي هيوقّفك. الغلط هو الطريق.",
    "💡 ١٥ دقيقة تقليد يومي أقوى من كورس ساعتين في الأسبوع.",
    "💡 اسمع نفس المقطع ٥ مرات. المرة الخامسة هتلاحظ حاجات ما لاحظتهاش.",
    "💡 أكبر عدو للتعلم مش الصعوبة — ده التأجيل.",
    "💡 لو مش عارف تبدأ منين — ابدأ بامتحان تحديد المستوى. ٢٠ دقيقة وهتعرف.",
    "💡 النطق مش موهبة. ده عضلات. والعضلات بتتبني بالتمرين.",
    "💡 الفرق بين حد \"بيعرف\" إنجليزي وحد \"بيتكلم\" إنجليزي = ممارسة يومية.",
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
