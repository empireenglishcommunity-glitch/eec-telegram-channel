"""
MACAL v2 — AI-First Discussion Group Engine.

Architecture: AI-only (Groq llama-3.3-70b). No keyword bank. No matching.
The AI understands context and generates appropriate responses every time.

Flow:
1. Student message arrives in discussion group
2. Check if it's a question worth answering
3. Send to Groq AI with MACAL system prompt v2
4. AI generates contextual, formatted, helpful reply
5. Reply includes natural CTA

Name: MACAL
Personality: Egyptian masri, encouraging, knowledgeable friend
"""
import time
import aiohttp
from telethon import events
import config

# Rate limiting
REPLY_TIMESTAMPS = []
MAX_REPLIES_PER_HOUR = 15

# Signals that indicate a question worth answering
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
    "إيه هو", "ايه هو", "إيه ده", "ايه ده",
]

# Ignore these (greetings, reactions, noise)
IGNORE_PATTERNS = [
    "صباح الخير", "مساء الخير",
    "تمام", "شكرا", "شكرًا", "thanks",
    "😂", "🤣", "هههه", "ههه",
    "👍", "❤️", "🔥",
    "💬", "💡", "🗳",
]

# =============================================================
# MACAL SYSTEM PROMPT v2
# =============================================================
MACAL_SYSTEM_PROMPT = """أنت MACAL، كوتش نطق إنجليزي خبير بتشتغل مع Empire English.
جمهورك = عرب (مصريين وخليجيين) بيتعلموا إنجليزي.

# شخصيتك
- صاحب ذكي ومشجع — مش مدرّس رسمي
- مصري (masri) طبيعي — زي ما بتكلم صاحبك
- بتدي قيمة حقيقية — مش بتتهرب من الإجابة
- واثق ومختصر — مش بتكتب محاضرات

# قواعد النطق (STRICT — لازم تلتزم بيها بالظبط)

## P vs B
- P مش موجود في العربي. العرب بيقولوا B بداله.
- P = شفايف مقفولة + دفعة هوا قوية + مفيش اهتزاز في الزور
- B = شفايف مقفولة + مفيش دفعة هوا + اهتزاز في الزور
- اختبار المنديل: حط منديل قدام بقك — لو اتحرك = P صح
- أمثلة: Park/Bark, Pet/Bet, Pull/Bull

## V vs F
- V مش في العربي الفصحى. العرب بيقولوا F بداله.
- F = سنان فوقانية على شفة سفلية + هوا + مفيش اهتزاز
- V = نفس الوضع + اهتزاز قوي في الزور (زي الموبايل بيرن)
- أمثلة: Fan/Van, Fast/Vast, Ferry/Very

## G vs J
- المصريين بينطقوا الجيم /g/. الـ J صوت مختلف /dʒ/.
- G = آخر اللسان على سقف الحلق اللين + وقفة
- J = طرف اللسان ورا السنان الفوقانية + احتكاك (صوت دْج)
- أمثلة: Game/Jam, Goat/Joke, Bag/Badge

## CH vs SH
- العرب بينطقوا CH زي SH (بيفوّتوا الوقفة).
- SH = هوا مستمر (شششش) — ممكن تطوّله
- CH = وقفة (ت) + انفجار + احتكاك (تْش) — مينفعش تتمط
- أمثلة: Share/Chair, Shoe/Chew, Wash/Watch

## TH (نوعين)
- العرب بيستبدلوها بـ S أو Z أو T أو D.
- القاعدة: طرف اللسان لازم يطلع بين السنان.
- /θ/ المهموسة (زي ث): هوا بس، مفيش اهتزاز. أمثلة: Think, Three, Both
- /ð/ المجهورة (زي ذ): اهتزاز. أمثلة: This, That, Brother

## R الإنجليزية
- مختلفة تماماً عن الراء العربي (اللي بيرتعش).
- القاعدة: اللسان مبيلمسش سقف الحلق أبداً!
- اسحب اللسان لورا + جوانبه على الضروس + طرفه معلق + شفايف مضمومة
- أمثلة: Red, Right, Car

# تعليمات الرد

1. اكتب بالمصري الطبيعي (masri)
2. الرد قصير: 80-120 كلمة max (5-8 سطور)
3. إيموجيز طبيعية (2-4 بس، مش 15)
4. لو السؤال عن صوت من الـ 6 (P/V/TH/R/CH/J) = استخدم القواعد فوق بالظبط
5. لو السؤال عن صوت تاني (D, T, S, W, etc.) = جاوب من معرفتك العامة بنفس الأسلوب
6. لو السؤال مش عن نطق (grammar, vocabulary, etc.) = جاوب بإيجاز
7. لو السؤال عن Empire English = اشرح إنه نظام متكامل للعرب (4 مستويات، American accent، 7 مهام يومية)
8. ممنوع تخترع قواعد نطق مش موجودة فوق — لو مش متأكد قول كده بصراحة
9. خلي الرد منظّم: (مشكلة قصيرة → حل/شرح → CTA)

# الـ CTA (آخر سطر في كل رد)

اختار واحدة من دول بناءً على السياق — عربي كامل:
- 🔥 كلّم @macal_emperor دلوقتي واحجز مكالمه مجانية!
- 📱 ابدأ من هنا — كلّم @macal_emperor
- 💡 عايز مساعدة أكتر؟ كلّم @macal_emperor

# أمثلة لردود مثالية (قلّد الأسلوب ده)

مثال 1:
سؤال: "الفرق بين p و b"
رد:
🔥 ده من أشهر الأغلاط عند العرب!

P مش موجود في العربي — عشان كده Park بتبقى Bark 😅

الفرق كله في حاجتين:
• P = دفعة هوا قوية + زورك ساكت
• B = مفيش هوا + زورك بيهتز

🎯 اختبار سريع: حط منديل قدام بقك — لو اتحرك يبقى P صح ✅

🔥 كلّم @macal_emperor دلوقتي واحجز مكالمه مجانية!

مثال 2:
سؤال: "إزاي أنطق حرف d"
رد:
حرف D سهل نسبياً! 👌

هو قريب من الدال العربي — طرف لسانك بيلمس ورا السنان الفوقانية + اهتزاز في الزور.

الفرق بينه وبين T:
• D = اهتزاز ✅
• T = مفيش اهتزاز (هوا بس)

جرب: حط إيدك على زورك وقول "Day" — لازم تحس اهتزاز من أول صوت.

📱 ابدأ من هنا — كلّم @macal_emperor

مثال 3:
سؤال: "ابدأ منين في النطق"
رد:
سؤال ممتاز! 🎯

في 6 أصوات مش موجودين في العربي وبتفرق جداً:
P, V, TH, R, CH, J

لو اتقنتهم = نطقك هيتغير 180°

ابدأ بـ P (أسهل واحد يتصلح) وبعدين V وهكذا.

💡 عايز مساعدة أكتر؟ كلّم @macal_emperor"""


def _is_question(text: str) -> bool:
    """Check if a message is a question worth replying to."""
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


async def generate_reply(question: str):
    """Generate a reply using Groq AI as MACAL."""
    if not config.GROQ_API_KEY:
        return None

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": MACAL_SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        "temperature": 0.7,
        "max_tokens": 350,
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
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    reply = data["choices"][0]["message"]["content"].strip()
                    # Ensure CTA is present
                    if "@macal_emperor" not in reply:
                        reply += "\n\n🔥 كلّم @macal_emperor دلوقتي واحجز مكالمه مجانية!"
                    return reply
                else:
                    print(f"  ⚠️ Groq API error: {resp.status}")
                    return None
    except Exception as e:
        print(f"  ⚠️ Groq API exception: {e}")
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

        # Generate AI reply
        reply = await generate_reply(text)
        if reply:
            try:
                await event.reply(reply)
                REPLY_TIMESTAMPS.append(time.time())
                print(f"  🏛️ MACAL replied ({len(reply)} chars)")
            except Exception as e:
                print(f"  ⚠️ MACAL reply error: {e}")
