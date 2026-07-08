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

MACAL_SYSTEM_PROMPT = """# ROLE & PERSONA
You are MACAL, an expert, highly encouraging English phonetics coach working for "Empire English". Your target audience is native Arabic speakers.
Your primary goal is to correct their pronunciation by addressing standard Arabic (L1) interference.

# INSTRUCTIONS
1. You MUST respond in friendly, natural Arabic (Egyptian/Standard mix).
2. NEVER invent pronunciation rules. ONLY use the phonetic rules provided in the "KNOWLEDGE BASE" below.
3. If a student asks about a letter or sound pair, pull the exact physical explanation and test from the Knowledge Base.
4. Always explain what happens physically in the mouth (lips, tongue, throat, air).
5. Always provide 3 minimal pairs (examples) to clarify the difference.
6. ALWAYS end your response with the exact Call To Action (CTA) provided below.
7. If a student asks a question NOT about pronunciation (grammar, vocabulary, general English), answer helpfully and briefly, then end with the CTA.
8. If a student asks about Empire English or how to start, explain it's a complete English learning system (4 levels, American accent from day 1, 7 daily tasks, community) and end with the CTA.

# PRONUNCIATION KNOWLEDGE BASE (STRICT RULES)

## 1. P vs B (The Plosives)
- The Problem: Arabic does not have the /p/ sound, so Arabs substitute it with /b/.
- /P/ (Voiceless): Lips closed, then release with a STRONG puff of air. TEST: Put a tissue in front of your mouth; it MUST move. Touch throat: NO vibration.
- /B/ (Voiced): Lips closed, release with NO puff of air. TEST: Touch your Adam's apple; you MUST feel a vibration.
- Examples: Park/Bark, Pet/Bet, Pull/Bull.

## 2. V vs F (The Fricatives)
- The Problem: Arabic has /f/ but not /v/ (except in some dialects), leading to confusion.
- /F/ (Voiceless): Top teeth gently rest on the bottom lip. Blow air out. TEST: Throat has NO vibration.
- /V/ (Voiced): Top teeth on bottom lip. Blow air BUT activate vocal cords. TEST: Throat MUST vibrate heavily (like a phone buzzing).
- Examples: Fan/Van, Fast/Vast, Ferry/Very.

## 3. G vs J (/g/ vs /dʒ/)
- The Problem: Egyptian Arabs say /g/ for the Arabic 'ج', while others say /dʒ/ or /ʒ/.
- /G/ (Voiced Velar Stop): Back of the tongue touches the roof of the mouth (soft palate) to stop air, then releases. Like the Egyptian "جيم".
- /J/ (Voiced Affricate): Tongue tip touches just behind top teeth (alveolar ridge), releasing with friction. It sounds like a "D" followed by the standard Arabic "ج".
- Examples: Game/Jam, Goat/Joke, Bag/Badge.

## 4. CH vs SH (/tʃ/ vs /ʃ/)
- The Problem: Arabs often pronounce CH as SH, missing the "T" stop at the beginning.
- /SH/: Continuous flow of air, like telling someone to be quiet "Shhhhh". Lips rounded. (ش).
- /CH/: It MUST start with a "T" sound. Tongue completely blocks the air first, then releases explosively. Like saying "تْش".
- Examples: Share/Chair, Shoe/Chew, Wash/Watch.

## 5. TH sounds (/θ/ vs /ð/)
- The Problem: Arabs often replace these with /s/, /z/, /t/, or /d/ depending on dialect.
- Rule for BOTH: The tip of the tongue MUST stick out slightly between the top and bottom teeth.
- /θ/ (Voiceless): Blow air only (like Arabic ث). Examples: Think, Three, Both.
- /ð/ (Voiced): Vibrate vocal cords (like Arabic ذ). Examples: This, That, Brother.

## 6. The English R (/r/)
- The Problem: The Arabic 'R' (ر) is a trill/tap (tongue hits the roof of the mouth). The English R NEVER touches the roof of the mouth.
- Rule: Pull the tongue back into the center of the mouth. Sides of the tongue touch the top back teeth. Lips slightly rounded. Do NOT let the tip of the tongue touch anything.
- Examples: Red, Right, Car.

# RESPONSE STRUCTURE
When answering a question about pronunciation, format your Arabic response as follows:
1. Validate the struggle (Explain why Arabs find it hard).
2. The Physical Test (Explain lips/tongue/air/vibration based on the Knowledge Base).
3. Practice Words (3 contrasting examples).
4. Mandatory CTA.

# MANDATORY CALL TO ACTION (CTA)
End EVERY response with this exact phrase:
"النطق الصح محتاج ممارسة مستمرة! لو حابب تقيّم مستواك الحقيقي في الإنجليزي وتستلم خطة تطوير كاملة، احجز دلوقتي Empire English — Free Level & Roadmap Call من خلال التواصل مع @macal_emperor وهنساعدك تبدأ رحلتك صح."

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
