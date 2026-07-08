"""
Auto-reply engine for the discussion group.
Listens to messages and replies to English-learning questions.
Uses Groq AI to understand and respond in Egyptian Arabic.

Rules:
- Only replies to questions (not every message)
- Max 5 replies per hour (rate limit)
- Responds in Egyptian masri (MACAL brand voice)
- Short, helpful, authoritative
- Doesn't reply to its own messages
- Doesn't reply to forwarded posts from channel
"""
import asyncio
import time
import aiohttp
from datetime import datetime
from telethon import events
import config

# Rate limiting
REPLY_TIMESTAMPS = []
MAX_REPLIES_PER_HOUR = 5

# Keywords that signal a question about English
QUESTION_SIGNALS = [
    "؟",  # Arabic question mark
    "?",  # English question mark
    "إزاي", "ازاي",  # how
    "يعني إيه", "يعني ايه",  # what does it mean
    "الفرق بين", "الفرق ما بين",  # difference between
    "إيه معنى", "ايه معنى",  # what's the meaning
    "بتتنطق", "بينطق", "نطق",  # pronunciation
    "ينفع أقول", "ينفع اقول",  # can I say
    "صح ولا غلط",  # right or wrong
    "مش فاهم", "مش فاهمة",  # I don't understand
    "حد يشرح", "حد يفهمني",  # someone explain
    "ممكن حد", "ممكن أسأل",  # can someone / can I ask
]

# Ignore these patterns (not real questions)
IGNORE_PATTERNS = [
    "صباح الخير", "مساء الخير",  # greetings
    "تمام", "شكرا", "شكرًا",  # thanks
    "😂", "🤣", "هههه",  # laughter
]

SYSTEM_PROMPT = """أنت المساعد الرسمي لـ Empire English Community.
بتجاوب على أسئلة الأعضاء عن تعلم الإنجليزي وعن النظام بتاع Empire.

═══ شخصيتك ═══
- اسمك: مساعد Empire
- أسلوبك: واثق، مباشر، مختصر، مفيد
- لغتك: عامية مصرية ١٠٠٪
- ممنوع: كلام فاضي، مقدمات، "أهلًا بيك"، "تحت أمرك"

═══ تعرف إيه عن Empire ═══
- نظام تعليم إنجليزي للعرب — نطق أمريكي من أول يوم
- ٤ مستويات (٠ → ٣)
- ٧ مهام يومية (نطق، كلمات، تقليد، كلام، استماع، كتابة، مجتمع)
- امتحان تحديد مستوى مجاني: assessment.empireenglish.online
- مجتمع Discord فيه محادثات صوتية يومية
- بوت التفاصيل: @EmpireEnglishBot
- مفيش معلم — فيه نظام + ذكاء اصطناعي + مجتمع

═══ لما حد يسأل عن الإنجليزي ═══
- اشرح بإيجاز (٢-٤ سطور max)
- لو سؤال نطق: اشرح الصوت + ادي مثال
- لو سؤال معنى: المعنى + جملة
- لو سؤال قواعد: القاعدة + مثال

═══ لما حد يسأل عن Empire ═══
- جاوب عن النظام بثقة
- وجّهه للامتحان المجاني أو البوت

═══ ممنوع ═══
- إجابات أطول من ٥ سطور
- "أهلًا وسهلًا" أو "تحت أمرك" أو "أنا هنا عشان اساعدك"
- كلام عام من غير فايدة
- الرد بـ "ده مش تخصصي" على أي سؤال عن الإنجليزي أو عن Empire

═══ شكل الإجابة ═══
[الإجابة المباشرة في ٢-٤ سطور]

🏛️"""


def _is_question(text: str) -> bool:
    """Check if a message is likely a question about English or Empire."""
    if not text or len(text) < 10:
        return False

    # Check ignore patterns first
    for pattern in IGNORE_PATTERNS:
        if text.strip() == pattern or text.strip().startswith(pattern):
            return False

    # Ignore messages that are the bot's own seeded prompts
    if text.startswith("💬") or text.startswith("💡") or text.startswith("🗳"):
        return False

    # Check for question signals
    for signal in QUESTION_SIGNALS:
        if signal in text:
            return True

    return False


def _can_reply() -> bool:
    """Rate limit: max 5 replies per hour."""
    global REPLY_TIMESTAMPS
    now = time.time()
    # Remove timestamps older than 1 hour
    REPLY_TIMESTAMPS = [t for t in REPLY_TIMESTAMPS if now - t < 3600]
    return len(REPLY_TIMESTAMPS) < MAX_REPLIES_PER_HOUR


async def generate_reply(question: str) -> str | None:
    """Generate a reply using Groq AI."""
    if not config.GROQ_API_KEY:
        return None

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        "temperature": 0.7,
        "max_tokens": 300,
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
                    # Ensure it ends with brand mark
                    if "🏛️" not in reply:
                        reply += "\n\n🏛️"
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

        # Don't reply to forwarded messages (channel posts)
        if event.message.fwd_from:
            return

        # Don't reply to bot messages
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

        # Add a small random delay (20-45 sec) — looks human but fast
        delay = __import__('random').randint(20, 45)
        await asyncio.sleep(delay)

        # Generate reply
        reply = await generate_reply(text)
        if reply:
            try:
                await event.reply(reply)
                REPLY_TIMESTAMPS.append(time.time())
                print(f"  💬 Auto-reply sent ({len(reply)} chars)")
            except Exception as e:
                print(f"  ⚠️ Auto-reply send error: {e}")
