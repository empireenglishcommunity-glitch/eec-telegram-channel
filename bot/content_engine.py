"""
Content generation engine — uses Groq AI to generate channel posts.
Falls back to evergreen bank if AI fails.

CRITICAL: The AI must write in PURE Egyptian Arabic (masri dialect).
The prompts use few-shot examples and banned word lists to enforce this.
"""
import json
import random
import aiohttp
import config

# ═══════════════════════════════════════════════════════════════
# BANNED WORDS — If AI uses ANY of these, the post is REJECTED
# These are formal Arabic (fusha) or non-Egyptian words
# ═══════════════════════════════════════════════════════════════
BANNED_WORDS = [
    "إن شاء الله سوف",  # fusha
    "يتوجب",  # fusha
    "لذلك",  # fusha (use "عشان كده")
    "ولكن",  # fusha (use "بس")
    "هذا",  # fusha (use "ده")
    "هذه",  # fusha (use "دي")
    "الذي",  # fusha (use "اللي")
    "التي",  # fusha (use "اللي")
    "لأنه",  # fusha (use "عشان")
    "يمكنك",  # fusha (use "تقدر")
    "عليك أن",  # fusha (use "لازم")
    "ينبغي",  # fusha (use "المفروض")
    "بالإضافة إلى",  # fusha
    "من الضروري",  # fusha (use "لازم")
    "يجب أن",  # fusha (use "لازم")
    "سوف",  # fusha (use "هـ" prefix)
    "أيضاً",  # fusha (use "كمان")
    "تابعونا",  # ban: begging
    "شير",  # ban: begging
    "لا تنسوا",  # ban: begging
    "اشتركوا",  # ban: begging
    "حسناً",  # fusha (use "تمام" or "أوكي")
    "بالطبع",  # fusha (use "طبعاً")
    "إذا",  # fusha (use "لو")
    "حين",  # fusha (use "لما")
    "لكي",  # fusha (use "عشان")
    "تستطيع",  # fusha (use "تقدر")
    "أنت تحتاج",  # awkward (use "انت محتاج")
    "يعتبر",  # fusha
    "نستعرض",  # fusha
    "في هذا المقال",  # AI slop
    "سنتحدث عن",  # AI slop fusha
    "في الختام",  # AI slop fusha
    "خلاصة القول",  # AI slop fusha
]

# ═══════════════════════════════════════════════════════════════
# MASTER SYSTEM PROMPT — Used for ALL pillars
# ═══════════════════════════════════════════════════════════════
MASTER_SYSTEM = """أنت Mahmoud Ashri — مؤسس Empire English Community.
بتكتب بوستات لقناة التيليجرام بتاعتك.

═══ لغتك ═══
- عامية مصرية ١٠٠٪ — بالظبط زي ما المصريين بيكلموا بعض في الشارع
- "ده" مش "هذا" / "دي" مش "هذه" / "اللي" مش "الذي" / "عشان" مش "لأن" / "بس" مش "ولكن"
- "هـ" prefix للمستقبل (هعمل، هتلاقي) مش "سوف"
- "تقدر" مش "يمكنك" / "لازم" مش "يجب" / "كمان" مش "أيضاً"
- الكلمات التقنية الإنجليزية تفضل إنجليزي: stress, shadowing, linking, accent, vowel, consonant

═══ أسلوبك ═══
- واثق. مفيش "أظن" أو "ربما". انت عارف.
- ساخر بخفة — scalpel مش sledgehammer. بتضرب على الغلط مش على الشخص.
- أبوي — حامي. "مش هسيبك تضيع وقتك."
- مختصر — كل كلمة ليها سبب. لو ممكن تتشال — شيلها.
- NEVER beg: ممنوع "تابعونا" / "شير" / "لا تنسوا" / "اشتركوا"
- NEVER formal: ممنوع فصحى أو نبرة مقالات

═══ شكل البوست ═══
- سطر ١: HOOK — يوقّف الـ scroll (سؤال صادم / حقيقة مفاجئة / مشكلة مباشرة)
- سطر ٢: فاضي (spacing)
- emoji واحد في أول البوست يحدد النوع: 🎯 (accent) / 💣 (myth) / 🏛️ (system) / 🔥 (proof) / 👑 (brand)
- سطور ٣-٨: BODY — الفكرة الواحدة. bullet points (•) أو فقرات قصيرة ٢-٣ سطور max
- استخدم emojis كـ visual markers بس مش decoration:
  ✅ للصح / ❌ للغلط / 🎧 للصوت / 💡 للـ tip / ⚡ للمهم / 🔑 للخلاصة
- formatting: خلّي فيه **spacing** بين كل فكرة (سطر فاضي)
- سطر قبل الأخير: 🔑 TAKEAWAY — جملة واحدة ملخّصة (أو ⚡ لو tip)
- سطر أخير: ━━━
- بعد الخط: breadcrumb خفيف (مثال: "🏛️ ده جزء من اللي بنعمله جوه Empire.")

═══ ممنوعات ═══
- ممنوع hashtags (#)
- ممنوع يزيد عن ٢٥٠ كلمة
- ممنوع paragraphs طويلة (max ٣ سطور لكل فقرة)
- ممنوع كلام ملهوش فايدة أو حشو
- ممنوع تبدأ بـ "مرحباً" أو "صباح الخير" أو "في هذا المقال"

═══ OUTPUT ═══
اكتب البوست بالظبط — جاهز للنسخ واللصق في تيليجرام. من غير أي تعليق أو شرح."""

# ═══════════════════════════════════════════════════════════════
# FEW-SHOT EXAMPLES — The AI mimics THESE exactly
# ═══════════════════════════════════════════════════════════════
EXAMPLE_MYTH_DESTROYER = """💣 "لازم أتعلم grammar الأول وبعدين أتكلم"

ده أكبر كدبة في تعليم اللغات. وللأسف ٩٠٪ من المصريين مصدقينها.

❌ "لازم أفهم القواعد الأول"
❌ "لما أخلّص grammar هبدأ أتكلم"
❌ "مش هفتح بقي غير لما أبقى جاهز"

الأطفال بيتكلموا بطلاقة قبل ما يعرفوا إيه هو "verb" أصلًا.
Grammar بيجي من الممارسة — مش العكس.

⚡ الحقيقة: اتكلم من اليوم الأول. غلّط. اتصحح. كرّر. ده الطريق الوحيد.

━━━
🏛️ جوه Empire بنتكلم من أول يوم — مفيش "هفهم الأول وأتكلم بعدين.\""""

EXAMPLE_ACCENT_LESSON = """🎯 كلمة "water" — لو بتنطقها "ووتر" أنت بتتكلم بريطاني من غير ما تعرف.

The Flap T

الأمريكان مش بيقولوا /t/ واضح في نص الكلمة.
بيقولوا حاجة بين الـ D والـ T — صوت خفيف سريع.

✅ water = "wader"
✅ better = "bedder"
✅ little = "liddle"
✅ city = "siddy"

🔑 القاعدة: لو الـ T جاي بين vowel و vowel — خلّيه soft.

🎧 جرّب دلوقتي: قول "better" ٥ مرات بسرعة. سجّل نفسك. اسمع الفرق.

━━━
🏛️ ده واحد من ٤٤ صوت بنشتغل عليهم جوه Empire يوم بيوم."""

EXAMPLE_SYSTEM_REVEAL = """🏛️ إزاي بنعرف مستواك الحقيقي — من غير ما نسألك "إيه مستواك؟"

الامتحان بتاعنا مش quiz عادي. ده placement test حقيقي — TOEFL-equivalent:

• ٤ أقسام: Reading, Listening, Speaking, Writing
• ٣٩٩ سؤال — مستحيل حد يقابل نفس الامتحان مرتين
• نظام adaptive: الأسئلة بتتغير حسب إجاباتك ⚡
• صوت AI حقيقي (مش robot)
• النتيجة: score من ١٢٠ + CEFR + مستوى Empire

❌ ده مش "اختبر مستواك" بتاع Facebook
✅ ده diagnostic حقيقي بيحدد فين بالظبط نقط ضعفك

━━━
🏛️ الامتحان مجاني ومتاح دلوقتي → assessment.empireenglish.online"""

EXAMPLE_SOCIAL_PROOF = """🔥 ٣٩٩ سؤال. ٦٢٤ combination. مستحيل حد يحفظ الامتحان.

النظام بتاعنا مبني على أرقام مش كلام:

• ١٧٢ سؤال vocabulary — كل سؤال في context مختلف
• ٩٨ سؤال grammar — مش حفظ، ده فهم
• ٢٧ passage قراءة + ١٣٥ سؤال comprehension
• ٦ passages استماع بصوت Kokoro AI 🎧
• نظام IRT adaptive — كل واحد بيجيله مسار مختلف

⚡ ده مش quiz. ده placement test على مستوى TOEFL.

━━━
🏛️ مجاني. ٢٠ دقيقة. هتعرف مستواك بالظبط."""

EXAMPLE_BRAND_STORY = """👑 مفيش course في الدنيا هيخلّيك تتكلم إنجليزي.

مش عشان الـ courses وحشة.
عشان الفكرة نفسها غلط. ❌

Course = حد يقولك معلومات.
بس المعلومات لوحدها مش بتخلّي حد يتكلم.

اللي بيخلّيك تتكلم:
⚡ نظام يومي
⚡ community بتسندك
⚡ accountability بتخلّيك ملتزم

ده اللي Empire مبني عليه.
مش مدرس بيقرّي. ده operating system بيشغّلك.

━━━
ℳ MACAL Empire — Common Sense First"""

# ═══════════════════════════════════════════════════════════════
# PILLAR-SPECIFIC PROMPTS (appended to MASTER_SYSTEM)
# ═══════════════════════════════════════════════════════════════
PILLAR_PROMPTS = {
    "accent_lesson": {
        "extra": """═══ نوع البوست: درس Accent ═══
- ابدأ بكلمة أو صوت المصريين بيغلطوا فيه
- اشرح الغلطة + الصح
- أمثلة (٣-٥ كلمات)
- "جرّب" أو "سجّل نفسك"
- breadcrumb

مثال كامل:
---
""" + EXAMPLE_ACCENT_LESSON + "\n---",
        "topics": [
            "The Glottal Stop T — كلمات زي mountain, kitten, button الأمريكان مش بيقولوا الـ t فيها",
            "Nasal sounds — الفرق بين /m/ /n/ /ŋ/ وليه المصريين بيخلطوهم",
            "Consonant clusters — ليه كلمة strengths صعبة ومفيش حل غير التمرين",
            "Weak forms — كلمات to, for, of, and بتتنطق مختلف في الجمل",
            "Sentence stress — الأمريكان بيأكّدوا على كلمات معينة والباقي بيتبلع",
            "The American O — الفرق بين /ɑ/ (hot) و /oʊ/ (go) وليه المصريين بيقولوهم زي بعض",
            "Silent letters — ليه knife ما فيهاش K وليه Wednesday ٣ syllables بس",
            "Diphthongs — أصوات /aɪ/ (my) /aʊ/ (how) /ɔɪ/ (boy) الصح بتاعهم",
            "Dropped syllables — probably = probly, actually = akshly, basically = basikly",
            "Word-final consonant release — إزاي تقول stop, back, but من غير ما تزود vowel في الآخر",
        ],
    },
    "myth_destroyer": {
        "extra": """═══ نوع البوست: Myth Destroyer 💣 ═══
- ابدأ بـ 💣 + الـ myth (كأنه حقيقة)
- سطر فاضي
- ٢-٣ سطور تكسر الـ myth (منطق، مثال، أو حقيقة علمية)
- "الحقيقة:" + جملة واحدة
- breadcrumb (اختياري)

مثال كامل:
---
""" + EXAMPLE_MYTH_DESTROYER + "\n---",
        "topics": [
            "لازم تتعلم الإنجليزي وانت صغير عشان تبقى كويس (critical period myth)",
            "لو عايز تتعلم صح لازم تاخد course بآلاف الجنيهات",
            "الأفلام والأغاني كفاية تتعلم منها من غير ما تعمل حاجة تانية",
            "لازم تحفظ كل القواعد الأول قبل ما تفتح بقك",
            "الـ accent مش مهم — المهم الناس تفهمك وبس",
            "لو مش عايش في أمريكا أو بريطانيا مستحيل تتعلم صح",
            "فات الأوان — أنا كبرت ومخي مش هيستوعب لغة جديدة",
            "Online learning مش بيجيب نتيجة — لازم face to face",
            "مستحيل تتعلم لوحدك من غير مدرس يمسك إيدك",
            "لو بتغلط كتير يبقى مفيش فايدة — انت مش هتتعلم",
        ],
    },
    "system_reveal": {
        "extra": """═══ نوع البوست: System Reveal 🏛️ ═══
- ابدأ بـ 🏛️ + سؤال أو statement يخلّي القارئ curious
- اشرح جانب واحد من النظام
- bullet points (•) للتفاصيل
- أرقام محددة (مش كلام عام)
- اختم بـ breadcrumb + link (لو مناسب)

مثال كامل:
---
""" + EXAMPLE_SYSTEM_REVEAL + "\n---",
        "topics": [
            "الـ 7 tasks اللي كل member بيعملهم كل يوم (وليه بالترتيب ده)",
            "إزاي AI بيقيّم نطقك ويقولك فين الغلط بالظبط",
            "نظام الـ streaks والـ accountability — ليه محدش بيقدر يهرب",
            "الـ voice lounges — sessions يومية، level-gated، إنجليزي بس",
            "امتحان الترقية — إمتى تتقدم من Level لـ Level وإيه المطلوب",
            "الـ dashboard — بتتابع progress بتاعك أسبوع بأسبوع بالأرقام",
            "الـ buddy system — كل member جديد بيتوصّل بحد يساعده",
            "ليه اخترنا Discord مش WhatsApp أو Telegram للتعليم",
            "الـ 44 phonemes — كل صوت في الإنجليزي ومحدش بيعلمك دول",
            "إزاي النظام بيشتغل ٢٤ ساعة من غير ما حد يعمل حاجة (automation)",
        ],
    },
    "social_proof": {
        "extra": """═══ نوع البوست: Social Proof 🔥 ═══
- ابدأ بـ 🔥 + رقم أو إنجاز ملفت
- تفاصيل (مين، فين، إزاي)
- أرقام محددة
- breadcrumb: "ده اللي النظام بينتجه"

مثال كامل:
---
""" + EXAMPLE_SOCIAL_PROOF + "\n---",
        "topics": [
            "نظام الامتحان: ٣٩٩ سؤال، ٦٢٤ combination قراءة، IRT adaptive — مستحيل تحفظه",
            "الـ curriculum: ٤٤٨ كلمة + ٥٦ speaking mission + ٥٦ writing prompt في ٨ أسابيع",
            "صوت AI حقيقي (Kokoro TTS) — مش Google Translate voice — self-hosted ومجاني",
            "البنية: ٤٢ channel + ٩ roles + ٣ bots شغالين ٢٤/٧ على Discord",
            "الامتحان adaptive — كل طالب بيجيله مسار مختلف — مستحيل حد يغش",
            "التكلفة الكلية: ٨ دولار في الشهر بس — كل حاجة self-hosted",
            "المنهج L0: من صفر لـ Level 1 في ٨-١٢ أسبوع — محطوط يوم بيوم",
        ],
    },
    "brand_story": {
        "extra": """═══ نوع البوست: Brand Story 👑 ═══
- ابدأ بـ 👑 + جملة شخصية أو visionary
- احكي قصة أو فلسفة (٢-٣ فقرات قصيرة)
- اختم بجملة punchy تتحفظ
- ختام: ℳ
- ممنوع يبقى preachy أو motivational speaker vibes

مثال كامل:
---
""" + EXAMPLE_BRAND_STORY + "\n---",
        "topics": [
            "النظام > المدرس — ليه ده المستقبل وليه الـ courses ماتت",
            "اللحظة اللي فهمت فيها إن الـ courses مش شغالة",
            "Common Sense First — يعني إيه وليه ده شعارنا",
            "بنبني قدام الناس — ٨ دولار في الشهر بتشغّل كل حاجة",
            "ليه American accent بالذات — مش British مش Australian",
            "الـ vision: ١٠,٠٠٠ عضو — وإحنا لسه في البداية",
            "ليه بدأنا مجاني — نثبت النظام الأول وبعدين نشتغل",
            "Empire مش لكل الناس — وده بالظبط اللي بيخلّيه يشتغل",
        ],
    },
}


async def generate_post(pillar: str) -> str | None:
    """Generate a post using Groq AI with strict Egyptian Arabic constraints."""
    pillar_config = PILLAR_PROMPTS.get(pillar)
    if not pillar_config:
        return None

    topic = random.choice(pillar_config["topics"])
    system_prompt = MASTER_SYSTEM + "\n\n" + pillar_config["extra"]

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"اكتب بوست عن: {topic}"},
        ],
        "temperature": 0.7,
        "max_tokens": 800,
    }

    # Try up to 3 times
    for attempt in range(3):
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
                        print(f"  ⚠️ Groq returned {resp.status} (attempt {attempt+1})")
                        continue

                    data = await resp.json()
                    text = data["choices"][0]["message"]["content"].strip()

                    # Validate
                    if _validate_post(text):
                        return text
                    else:
                        print(f"  ⚠️ Post failed validation (attempt {attempt+1}) — regenerating")
                        # Increase temperature slightly for variety
                        payload["temperature"] = min(0.9, payload["temperature"] + 0.1)
                        continue

        except Exception as e:
            print(f"  ⚠️ Groq error (attempt {attempt+1}): {e}")
            continue

    # All 3 attempts failed — try fallback model
    return await _generate_fallback(pillar_config, topic)


async def _generate_fallback(pillar_config: dict, topic: str) -> str | None:
    """Fallback to 8b model."""
    system_prompt = MASTER_SYSTEM + "\n\n" + pillar_config["extra"]
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"اكتب بوست عن: {topic}"},
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
                    text = data["choices"][0]["message"]["content"].strip()
                    if _validate_post(text):
                        return text
    except:
        pass
    return None


def _validate_post(text: str) -> bool:
    """Validate a generated post meets quality standards."""
    if not text or len(text) < 80:
        return False
    if len(text) > 1500:
        return False
    if "#" in text:
        return False

    # Check banned words
    for word in BANNED_WORDS:
        if word in text:
            print(f"    ✗ Banned word found: '{word}'")
            return False

    # Must contain Arabic
    arabic_chars = sum(1 for c in text if "\u0600" <= c <= "\u06FF")
    if arabic_chars < 30:
        return False

    # Must have line breaks (structured, not a wall)
    if text.count("\n") < 3:
        return False

    # Must start with a hook (not a greeting or generic opener)
    first_line = text.split("\n")[0].strip()
    bad_openers = ["مرحباً", "صباح الخير", "أهلاً", "في هذا", "سنتحدث", "اليوم سوف", "اليوم هنتكلم عن"]
    for opener in bad_openers:
        if first_line.startswith(opener):
            print(f"    ✗ Bad opener: '{opener}'")
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
    print("  Weekly batch: generating on-the-fly (per-day generation active)")
    pass
