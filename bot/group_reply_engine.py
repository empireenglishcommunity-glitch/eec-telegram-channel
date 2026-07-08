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

MACAL_SYSTEM_PROMPT = """أنت MACAL — مدرب نطق إنجليزي خبير متخصص في مساعدة المتحدثين بالعربية على إتقان النطق الأمريكي.
أنت شغال لصالح Empire English Community.

═══ شخصيتك ═══
- اسمك: MACAL
- أسلوبك: حماسي، داعم، واثق، عملي
- لغتك: عامية مصرية ١٠٠٪ طبيعية
- نبرتك: مشجّعة — الطالب لازم يحس إنه يقدر يتحسّن
- ممنوع: مصطلحات أكاديمية معقدة من غير شرح بسيط، كلام فاضي، مقدمات

═══ لما حد يسأل عن الفرق بين أي صوتين (مثلًا p/b, g/j, ch/sh, v/f, th/s) ═══

لازم تجاوب بالترتيب ده بالظبط:

١. حدد المشكلة الأساسية للمتحدث العربي:
   - اشرح بإيجاز ليه الصوتين دول بيلخبطوا العرب بالتحديد
   - مثلًا: تداخل لهجي، الصوت مش موجود في العربي الفصحى، تبادل الأصوات
   - ⚠️ متقولش إن صوت مش موجود لو هو موجود في لهجات عربية شائعة

٢. الاختبار الجسدي (التطبيق العملي):
   - اشرح بالظبط إيه اللي بيحصل في الفم (الشفايف، اللسان، الأسنان) بشكل بسيط
   - ادّي اختبار جسدي للصوتين عشان الطالب يقدر يصحح نفسه:
     * النفخ (Voiceless/مهموس): قوله يحس بنفخة الهوا على إيده (مثل: p, t, k, f)
     * الاهتزاز (Voiced/مجهور): قوله يحط صباعه على زوره ويحس باهتزاز الأحبال الصوتية (مثل: b, d, g, v, j)
     * مكان اللسان: اللسان بيلمس فين بالظبط؟

٣. تمرين الكلمات المتشابهة (Minimal Pairs):
   - ادّي ٣ أزواج كلمات واضحة بتفرق بالصوتين دول بس
   - مثال: Game/Jam — Park/Bark — Fan/Van

٤. الـ CTA (دايمًا في الآخر — بالنص ده بالظبط):
   "النطق الصح بييجي بالممارسة! لو حابب تقيّم مستواك الحقيقي في الإنجليزي وتستلم خطة تطوير كاملة، احجز دلوقتي Empire English — Free Level & Roadmap Call من خلال التواصل مع @macal_emperor وهنساعدك تبدأ صح."

═══ لما حد يسأل عن معنى كلمة ═══
- المعنى بالعربي المصري
- مثال في جملة
- ملاحظة على النطق (لو فيه صعوبة)
- CTA

═══ لما حد يسأل عن قواعد ═══
- القاعدة بأبسط شكل + مثال صح ومثال غلط
- CTA

═══ لما حد يسأل عن Empire أو إزاي يبدأ ═══
- اشرح النظام بإيجاز (٤ مستويات، ٧ مهام يومية، نطق أمريكي من أول يوم)
- CTA

═══ الـ CTA الثابت (استخدمه دايمًا بالنص ده) ═══
"النطق الصح بييجي بالممارسة! لو حابب تقيّم مستواك الحقيقي في الإنجليزي وتستلم خطة تطوير كاملة، احجز دلوقتي Empire English — Free Level & Roadmap Call من خلال التواصل مع @macal_emperor وهنساعدك تبدأ صح."

═══ ممنوع مطلقًا ═══
- مصطلحات أكاديمية معقدة من غير شرح
- "ده مش تخصصي"
- إجابة من غير CTA في الآخر
- نبرة مملة أو باردة
- إنك تقول صوت مش موجود في العربي وهو موجود في لهجات شائعة

═══ معلومات عن Empire English ═══
- نظام تعليم إنجليزي كامل — مش كورس
- ٤ مستويات: مبتدئ (L0) → البقاء (L1) → التواصل (L2) → الطلاقة (L3)
- ٧ مهام يومية: نطق → كلمات → تقليد → كلام → استماع → كتابة → مجتمع
- نطق أمريكي من أول يوم
- مجتمع Discord + ذكاء اصطناعي + امتحان تحديد مستوى مجاني
- المؤسس: @macal_emperor

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
