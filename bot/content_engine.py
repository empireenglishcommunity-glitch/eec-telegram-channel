"""
Content generation engine — uses Groq AI to generate channel posts.
Falls back to evergreen bank if AI fails.
"""
import json
import random
import aiohttp
import config

# Few-shot examples for each pillar (the AI mimics these)
PILLAR_PROMPTS = {
    "accent_lesson": {
        "system": """أنت كاتب محتوى لـ Empire English Club — مجتمع تعليم إنجليزي للعرب.
بتكتب بالعامية المصرية. الكلمات التقنية بالإنجليزي (stress, shadowing, linking).

قواعد:
- العامية المصرية فقط — ممنوع الفصحى
- أول سطر hook قوي يوقّف القارئ
- ممنوع hashtags
- ممنوع "تابعونا" أو "شير"
- ممنوع يزيد عن ٢٥٠ كلمة
- الأسلوب: واثق، ساخر بخفة، أبوي
- آخر سطر: breadcrumb خفيف ناحية Empire (مش بيع)
- ابدأ بالمشكلة/الغلطة اللي المصريين بيعملوها
- بعدها اشرح الصوت الصح
- بعدها أمثلة (كلمات)
- بعدها "اسمع" أو "جرّب"
- اختم بـ breadcrumb

اكتب البوست بالظبط — من غير أي كلام إضافي.""",
        "topics": [
            "Glottal Stop T (mountain, kitten, button)",
            "Nasal sounds /m/ /n/ /ŋ/ differences",
            "Consonant clusters (strengths, asks, texts)",
            "Weak forms of function words (to, for, of, and)",
            "Sentence stress and emphasis patterns",
            "The American O sound (/ɑ/ vs /oʊ/)",
            "Silent letters (knife, psychology, Wednesday)",
            "Diphthongs /aɪ/ /aʊ/ /ɔɪ/ in American English",
            "Dropped syllables in fast speech (probably, basically, actually)",
            "Word-final consonant release (stop, but, back)",
        ],
    },
    "myth_destroyer": {
        "system": """أنت كاتب محتوى لـ Empire English Club.
بتكتب بالعامية المصرية. أسلوبك: واثق، ساخر، أبوي.

قواعد:
- ابدأ بالـ myth (اكتبه كأنه حقيقة — provocative)
- سطر فاضي
- ٢-٣ سطور بتكسر الـ myth بمنطق أو مثال
- سطر "الحقيقة هي..." 
- breadcrumb خفيف لـ Empire (اختياري)
- ممنوع hashtags أو "تابعونا"
- Max ١٥٠ كلمة""",
        "topics": [
            "لازم تتعلم الإنجليزي من صغرك (critical period myth)",
            "لو عايز تتعلم لازم تاخد course غالي",
            "الأفلام والأغاني كفاية تتعلم منها",
            "لازم تحفظ قواعد كتير قبل ما تتكلم",
            "Accent مش مهم — المهم الناس تفهمك",
            "لو مش عايش في بلد إنجليزي مش هتتعلم صح",
            "الكبار مش بيتعلموا languages بسهولة",
            "Online learning مش بيجيب نتيجة",
            "التعليم الذاتي مستحيل من غير مدرس",
            "لو بتغلط كتير يبقى مش هتتعلم",
        ],
    },
    "system_reveal": {
        "system": """أنت كاتب محتوى لـ Empire English Club.
بتكتب بالعامية المصرية. بتشرح جزء من النظام التعليمي.

قواعد:
- ابدأ بسؤال أو statement بيخلّي القارئ curious
- اشرح جانب واحد من النظام (bullet points)
- كن specific (أرقام، أدوات، methods)
- اختم بـ "عايز تجربه؟" + breadcrumb
- ممنوع hashtags
- Max ٢٥٠ كلمة""",
        "topics": [
            "The 7-task daily loop (what and why this order)",
            "How we use AI to evaluate your pronunciation",
            "The streak system and accountability",
            "How voice lounges work (daily sessions, level-gated)",
            "The advancement exam (when and how you level up)",
            "How we track your progress (dashboard, weekly scores)",
            "The buddy system (how new members are paired)",
            "Content factory (how 25 AI prompts generate infinite content)",
            "Why we chose Discord over WhatsApp or Telegram for delivery",
            "The 44 phonemes system (what it is, why it works)",
        ],
    },
    "social_proof": {
        "system": """أنت كاتب محتوى لـ Empire English Club.
بتكتب بالعامية المصرية. بتكتب بوست social proof.

قواعد:
- ابدأ بنتيجة (رقم أو إنجاز محدد)
- مين الشخص + من فين بدأ + قد إيه وقت
- إيه اللي عمله (specific)
- breadcrumb: "ده اللي النظام بينتجه"
- ممنوع hashtags
- Max ١٥٠ كلمة
- لو مفيش data حقيقي — اكتب بوست عن stats النظام نفسه (عدد الأسئلة، عدد التمارين، إلخ)""",
        "topics": [
            "Assessment system stats (399 questions, 624 reading combinations, IRT adaptive)",
            "Community activity (voice lounge hours, tasks completed this week)",
            "First student to hit Level 1 from Level 0",
            "The 56-day L0 curriculum (448 vocab, 56 speaking missions, 56 writing prompts)",
            "Kokoro TTS (professional AI voice for pronunciation demos — free, self-hosted)",
            "Number of unique test paths (impossible to memorize)",
            "Discord server structure (42 channels, 9 roles, 3 bots working 24/7)",
        ],
    },
    "brand_story": {
        "system": """أنت كاتب محتوى لـ Empire English Club.
بتكتب بالعامية المصرية. بتكتب brand story.

قواعد:
- ابدأ بجملة شخصية أو visionary
- احكي قصة (ليه بنينا EEC، أو فلسفة، أو moment مهم)
- اختم بجملة punchy تتحفظ
- ختام: ℳ
- ممنوع hashtags
- Max ٢٥٠ كلمة""",
        "topics": [
            "Why 'system over instructor' is the future",
            "The moment I realized courses don't work",
            "Common Sense First — what it means and why",
            "Building in public — $8/month runs everything",
            "Why we chose American accent specifically",
            "The 10,000 member vision — where this is going",
            "Why free pilot first (prove the system, then charge)",
            "Empire = not for everyone (exclusive by design)",
        ],
    },
}


async def generate_post(pillar: str) -> str | None:
    """Generate a post using Groq AI."""
    pillar_config = PILLAR_PROMPTS.get(pillar)
    if not pillar_config:
        return None

    topic = random.choice(pillar_config["topics"])

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": pillar_config["system"]},
            {"role": "user", "content": f"اكتب بوست عن: {topic}\n\nاكتب البوست فقط — من غير أي كلام تاني."},
        ],
        "temperature": 0.8,
        "max_tokens": 1000,
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
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status != 200:
                    print(f"  ⚠️ Groq returned {resp.status}")
                    # Try fallback model
                    return await _generate_fallback(pillar_config, topic)

                data = await resp.json()
                text = data["choices"][0]["message"]["content"].strip()

                # Validate
                if _validate_post(text):
                    return text
                else:
                    print("  ⚠️ Post failed validation — regenerating")
                    return await _generate_fallback(pillar_config, topic)

    except Exception as e:
        print(f"  ⚠️ Groq error: {e}")
        return None


async def _generate_fallback(pillar_config: dict, topic: str) -> str | None:
    """Fallback to 8b model."""
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": pillar_config["system"]},
            {"role": "user", "content": f"اكتب بوست عن: {topic}\n\nاكتب البوست فقط."},
        ],
        "temperature": 0.7,
        "max_tokens": 800,
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
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"].strip()
    except:
        pass
    return None


def _validate_post(text: str) -> bool:
    """Validate a generated post meets quality standards."""
    if not text or len(text) < 50:
        return False
    if len(text) > 2000:  # ~300 Arabic words
        return False
    if "#" in text:
        return False
    if "تابعونا" in text or "شير" in text:
        return False
    # Must contain some Arabic
    arabic_chars = sum(1 for c in text if "\u0600" <= c <= "\u06FF")
    if arabic_chars < 20:
        return False
    return True


async def get_bank_post(pillar: str) -> str | None:
    """Get a post from the evergreen bank (fallback)."""
    bank_path = f"data/bank/{pillar}.json"
    try:
        with open(bank_path, "r", encoding="utf-8") as f:
            posts = json.load(f)
        if posts:
            return random.choice(posts)["text"]
    except FileNotFoundError:
        pass
    return None


async def generate_weekly_batch():
    """Pre-generate 6 posts for the coming week."""
    # This populates the queue for the week
    # For now, posts are generated on-the-fly in daily_post
    # This function can be expanded to pre-generate and queue
    print("  Weekly batch: generating on-the-fly (per-day generation active)")
    pass
