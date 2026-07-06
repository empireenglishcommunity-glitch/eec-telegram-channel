"""Update the pinned message (delete old, post new, pin it)."""
import asyncio
import os
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "")

NEW_PINNED = """🏛️ Empire English Community

اتكلم إنجليزي — بنطق أمريكي — من غير كورسات فاشلة.

━━━━━━━━━━━━━━━━━━━

إيه ده؟

نظام تعليم إنجليزي كامل مبني للعرب.
مش مدرس بيقرّي. ده نظام بيخلّيك تتكلم.

• ٤ مستويات (من صفر لمستوى أهل اللغة)
• نطق أمريكي من أول يوم
• مجتمع على Discord (محادثات صوتية يومية)
• ذكاء اصطناعي بيقيّم نطقك + كتابتك
• امتحان تحديد مستوى مجاني (مستوى عالمي)

━━━━━━━━━━━━━━━━━━━

ليه تفضل هنا؟

كل يوم هتلاقي:
🎯 درس نطق قصير (صوت أمريكي واحد)
💣 كدبة بنكسرها (حاجة كنت فاكرها صح وهي غلط)
🔥 نتائج حقيقية (ناس زيك بدأت من صفر)
🏛️ إزاي النظام شغال من جوه

━━━━━━━━━━━━━━━━━━━

تعمل إيه دلوقتي؟

١. 🔗 امتحان تحديد المستوى — قريبًا
٢. 🤖 بوت التفاصيل والباقات — قريبًا
٣. 💬 مجتمع Discord — قريبًا

⚡ تابع القناة دي — هنعلن هنا أول ما كل حاجة تبقى جاهزة.

━━━━━━━━━━━━━━━━━━━

📢 القناة دي بتنزّل محتوى كل يوم سبت←خميس الساعة ٩ الصبح (توقيت دبي).
الجمعة راحة.

ℳ MACAL Empire — المنطق أولًا"""


async def main():
    client = TelegramClient('eec_session', API_ID, API_HASH)
    await client.start(phone=PHONE_NUMBER)
    print("✅ Logged in")

    channel = await client.get_entity("@Empire_English_Community")

    # Delete old pinned message (msg_id 78)
    try:
        await client.delete_messages(channel, [78])
        print("🗑️ Old pinned message deleted")
    except Exception as e:
        print(f"⚠️ Could not delete old pin: {e}")

    # Post new one and pin
    msg = await client.send_message(channel, NEW_PINNED)
    await client.pin_message(channel, msg.id)
    print(f"✅ New pinned message posted + pinned (msg_id: {msg.id})")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
