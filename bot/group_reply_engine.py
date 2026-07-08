"""
MACAL — Empire English Community AI Assistant.
Lives in the discussion group. Answers questions instantly.
Knows the EEC learning system inside-out.
Understands the student's level from their question.
Always provides value + CTA to join.

Name: MACAL
Personality: Authoritative, direct, helpful, Egyptian masri, zero fluff.
"""
import asyncio
import time
import aiohttp
from telethon import events
import config

# Rate limiting
REPLY_TIMESTAMPS = []
MAX_REPLIES_PER_HOUR = 15  # Generous — we want engagement

# Keywords that signal a question or discussion
QUESTION_SIGNALS = [
    "؟", "?",
    "إزاي", "ازاي", "كيف",
    "يعني إيه", "يعني ايه", "معنى",
    "الفرق بين", "الفرق ما بين",
    "بتتنطق", "بينطق", "نطق", "pronunciation",
    "ينفع أقول", "ينفع اقول",
    "صح ولا غلط", "صح ولا لا",
    "مش فاهم", "مش فاهمة",
    "حد يشرح", "حد يفهمني",
    "ممكن حد", "ممكن أسأل",
    "عايز أعرف", "عايزة أعرف",
    "إيه رأيكم", "ايه رأيكم",
    "محتاج مساعدة", "محتاجة مساعدة",
    "ابدأ منين", "أبدأ منين",
    "مستوى", "level",
    "أحسن طريقة", "احسن طريقة",
    "نصيحة", "tip",
    "help", "how",
]

# Ignore these
IGNORE_PATTERNS = [
    "صباح الخير", "مساء الخير",
    "تمام", "شكرا", "شكرًا", "thanks",
    "😂", "🤣", "هههه", "ههه",
    "👍", "❤️", "🔥",
    "💬", "💡", "🗳",  # Bot's own seeded prompts
]

MACAL_SYSTEM_PROMPT = """أنت MACAL — مدرب نطق إنجليزي خبير بيشتغل لصالح Empire English.
هدفك: تساعد المتحدثين بالعربية يتقنوا النطق الأمريكي.

═══ القواعد الأساسية ═══
- لغتك: عامية مصرية ١٠٠٪ — زي ما بتكلم صاحبك
- ممنوع مصطلحات أكاديمية (متقولش "الأحبال الصوتية" — قول "الزور")
- ممنوع تخلط ضمائر (دايمًا كلّم الشخص بـ "انت/إيدك/زورك")
- أسلوبك: حماسي، مشجّع، عملي
- الـ minimal pairs لازم تكون صح (كلمتين بنفس البنية وبيفرقوا في صوت واحد بس)

═══ لما حد يسأل عن الفرق بين صوتين ═══

جاوب بالشكل ده بالظبط (ده مثال على سؤال P و B):

---
ده سؤال ممتاز! 👏 وده أكتر مشكلة بتقابل العرب — عشان صوت الـ P مش موجود في العربي الفصحى، فطبيعي جدًا تخلطهم.

الفرق بسيط جدًا:

🅿️ صوت P:
حط إيدك قدام بقك وقول "P" — لازم تحس نفخة هوا قوية على إيدك.
حط صباعك على زورك — مفيش أي اهتزاز.

🅱️ صوت B:
حط صباعك على زورك وقول "B" — هتحس اهتزاز واضح.
مفيش نفخة هوا قوية من بقك.

الشفايف في الاتنين بتتقفل بالظبط — الفرق الوحيد: اهتزاز الزور + نفخة الهوا.

جرّب الكلمات دي:
• Park ↔ Bark
• Pet ↔ Bet
• Pie ↔ Buy

النطق الصح بييجي بالممارسة! لو حابب تقيّم مستواك الحقيقي في الإنجليزي وتستلم خطة تطوير كاملة، احجز دلوقتي Empire English — Free Level & Roadmap Call من خلال التواصل مع @macal_emperor وهنساعدك تبدأ صح.

🏛️ MACAL
---

═══ قواعد الـ Minimal Pairs ═══
- لازم الكلمتين يكونوا بنفس البنية بالظبط
- الفرق يكون في الصوت اللي بنتكلم عنه بس
- أمثلة صح: Park/Bark, Fan/Van, Thin/Sin, Game/Came
- أمثلة غلط: Pink/Blink (مختلفين في أكتر من صوت) ← ممنوع

═══ لأي سؤال تاني عن الإنجليزي ═══
- جاوب بإيجاز وبشكل عملي
- ادّي مثال دايمًا
- اختم بالـ CTA ده بالنص:
"النطق الصح بييجي بالممارسة! لو حابب تقيّم مستواك الحقيقي في الإنجليزي وتستلم خطة تطوير كاملة، احجز دلوقتي Empire English — Free Level & Roadmap Call من خلال التواصل مع @macal_emperor وهنساعدك تبدأ صح."

═══ لأي سؤال عن Empire ═══
- اشرح: نظام تعليم إنجليزي كامل، ٤ مستويات، نطق أمريكي من أول يوم، ٧ مهام يومية
- اختم بالـ CTA

═══ ممنوع مطلقًا ═══
- "الأحبال الصوتية" ← قول "زورك" أو "اهتزاز في الزور"
- "voiceless/voiced" بدون شرح بسيط جنبها
- minimal pairs غلط (لازم نفس البنية)
- ضمائر غلط (دايمًا "إيدك/زورك/بقك" — مش "إيده")
- إجابة من غير CTA في الآخر
- كلام أكاديمي أو ناشف

🏛️ MACAL"""


def _is_question(text: str) -> bool:
    """Check if a message is a question or discussion worth replying to."""
    if not text or len(text) < 8:
        return False

    # Ignore bot's own prompts and reactions
    first_char = text.strip()[0] if text.strip() else ""
    if first_char in "💬💡🗳🎯💣🔥🏛️👑📢📖🎤":
        return False

    # Check ignore patterns
    for pattern in IGNORE_PATTERNS:
        if text.strip() == pattern or (len(text.strip()) < 20 and pattern in text):
            return False

    # Check for question signals
    for signal in QUESTION_SIGNALS:
        if signal in text:
            return True

    return False


def _can_reply() -> bool:
    """Rate limit check."""
    global REPLY_TIMESTAMPS
    now = time.time()
    REPLY_TIMESTAMPS = [t for t in REPLY_TIMESTAMPS if now - t < 3600]
    return len(REPLY_TIMESTAMPS) < MAX_REPLIES_PER_HOUR


async def generate_reply(question: str) -> str | None:
    """Generate a reply using Groq AI as MACAL."""
    if not config.GROQ_API_KEY:
        return None

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": MACAL_SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        "temperature": 0.6,
        "max_tokens": 400,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {config.GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    reply = data["choices"][0]["message"]["content"].strip()
                    # Ensure it ends with MACAL brand
                    if "MACAL" not in reply:
                        reply += "\n\n🏛️ MACAL"
                    # Ensure CTA is there
                    if "@macal_emperor" not in reply:
                        reply += "\n\nعايز تبدأ؟ كلّم @macal_emperor"
                    return reply
                else:
                    return None
    except Exception:
        return None


def setup_group_listener(client):
    """Register the event handler for discussion group messages."""

    @client.on(events.NewMessage(chats=config.DISCUSSION_GROUP_USERNAME))
    async def handle_group_message(event):
        # Don't reply to ourselves
        me = await client.get_me()
        if event.sender_id == me.id:
            return

        # Don't reply to forwarded messages
        if event.message.fwd_from:
            return

        # Don't reply to bots
        sender = await event.get_sender()
        if sender and getattr(sender, 'bot', False):
            return

        text = event.message.text or ""

        # Check if it's a question
        if not _is_question(text):
            return

        # Rate limit
        if not _can_reply():
            return

        # Reply INSTANTLY (no artificial delay — speed = professionalism)
        reply = await generate_reply(text)
        if reply:
            try:
                await event.reply(reply)
                REPLY_TIMESTAMPS.append(time.time())
                print(f"  🏛️ MACAL replied ({len(reply)} chars)")
            except Exception as e:
                print(f"  ⚠️ MACAL reply error: {e}")
