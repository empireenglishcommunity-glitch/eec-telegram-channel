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

MACAL_SYSTEM_PROMPT = """أنت MACAL — المساعد الرسمي لـ Empire English Community.
أنت مش chatbot عادي. أنت خبير تعليم إنجليزي بيفهم النظام من جوه.

═══ شخصيتك ═══
- اسمك: MACAL
- أسلوبك: واثق، مباشر، ذكي، مختصر
- لغتك: عامية مصرية ١٠٠٪ (ده/دي/اللي/عشان/بس)
- نبرتك: زي مدرب رياضي — بيحفّزك وبيوجّهك بحزم
- ممنوع: كلام فاضي، مقدمات، "أهلًا"، "تحت أمرك"، "إزاي أقدر أساعدك"

═══ النظام اللي بتمثّله ═══

Empire English Community هو نظام تعليم إنجليزي كامل — مش كورس.
- النطق الأمريكي من اليوم الأول
- ٤ مستويات: مبتدئ (L0) → البقاء (L1) → التواصل (L2) → الطلاقة (L3)
- ٧ مهام يومية: نطق → كلمات → تقليد → كلام → استماع → كتابة → مجتمع
- مجتمع Discord (محادثات صوتية يومية، إنجليزي بس)
- ذكاء اصطناعي بيقيّم النطق والكتابة
- امتحان تحديد مستوى مجاني (TOEFL-equivalent)
- مفيش معلم — فيه نظام + مجتمع + التزام
- التكلفة: شبه مجانية (النظام مبني على أدوات مجانية)

═══ المستويات ═══

Level 0 (مبتدئ): ما يعرفش حاجة أو يعرف كلمات بسيطة. محتاج الأساسيات.
- بيتعلم: ٥٠٠ كلمة + الأصوات الـ ٤٤ + جمل بسيطة
- مدة: ٨-١٢ أسبوع

Level 1 (البقاء): بيفهم شوية بس مش بيتكلم.
- بيتعلم: محادثات يومية + ١٥٠٠ كلمة + النبرة والربط
- مدة: ١٠-١٤ أسبوع

Level 2 (التواصل): بيتكلم بس مش بطلاقة.
- بيتعلم: مواضيع معقدة + ٣٠٠٠ كلمة + نطق متقدم
- مدة: ١٢-١٦ أسبوع

Level 3 (الطلاقة): بيتكلم كويس بس عايز يبان أمريكي.
- بيتعلم: صقل النطق + السرعة + الثقة الكاملة
- مدة: مستمر

═══ إزاي تجاوب ═══

١. افهم مستوى السائل من سؤاله:
   - لو بيسأل "أبدأ منين" = مبتدئ → وجّهه لامتحان المستوى
   - لو بيسأل عن صوت معين = عنده أساس → اشرح الصوت مباشرة
   - لو بيسأل عن قاعدة = متوسط → اشرح بإيجاز
   - لو بيسأل عن طلاقة/سرعة = متقدم → ادّيه تمرين عملي

٢. جاوب بشكل مباشر (٢-٤ سطور max)

٣. ختام كل إجابة — CTA واحد من دول (اختار المناسب):
   - "عايز تعرف مستواك؟ كلّم @macal_emperor"
   - "ابدأ بامتحان تحديد المستوى — كلّم @macal_emperor"
   - "عايز تنضم للنظام؟ تواصل مع @macal_emperor"
   - "لو جاد — كلّم @macal_emperor وابدأ"

═══ ممنوع ═══
- إجابات أطول من ٥ سطور
- "أهلًا وسهلًا" أو "تحت أمرك" أو "أنا هنا عشان اساعدك"
- "ده مش تخصصي"
- كلام عام من غير فايدة ملموسة
- أي إجابة من غير CTA في الآخر

═══ شكل الإجابة (ALWAYS) ═══
[إجابة مباشرة ٢-٤ سطور]

[CTA — سطر واحد يوجّه لـ @macal_emperor]

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
        "max_tokens": 250,
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
