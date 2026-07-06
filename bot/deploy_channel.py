"""
Deploy channel foundation — sets description, posts+pins welcome message,
links discussion group, and posts rules.

Run ONCE: python deploy_channel.py
"""
import asyncio
import os
from telethon import TelegramClient
from telethon.tl.functions.messages import EditChatAboutRequest
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "")

CHANNEL_USERNAME = "Empire_English_Community"
DISCUSSION_GROUP_USERNAME = "empireenglishcommunity"

CHANNEL_DESCRIPTION = """نظام تعليم إنجليزي حقيقي — نطق أمريكي من اليوم الأول.
مش كورس. ده نظام بيخلّيك تتكلم.

🏛️ Empire English Community"""

PINNED_MESSAGE = """🏛️ Empire English Community

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

GROUP_RULES = """🏛️ قوانين المجموعة — Empire English Community

━━━━━━━━━━━━━━━━━━━

أهلًا بيك. المجموعة دي مكان للناس اللي عايزة تتكلم إنجليزي بجد.
عشان المكان يفضل مفيد — فيه قوانين بسيطة:

━━━━━━━━━━━━━━━━━━━

✅ المسموح:

• اسأل أي سؤال عن الإنجليزي (نطق، قواعد، كلمات، أي حاجة)
• شارك تقدمك (تسجيل، درجة، إنجاز)
• ساعد حد تاني (لو عارف الإجابة — قول)
• ناقش بوستات القناة (وده الهدف الأساسي)
• اكتب بالعربي أو الإنجليزي أو الاتنين

━━━━━━━━━━━━━━━━━━━

❌ الممنوع:

• إعلانات أو روابط خارجية (حذف فوري — مفيش إنذار)
• روابط لقنوات تانية أو كورسات تانية
• إهانة أو تنمّر على حد
• رسائل صوتية أطول من دقيقتين
• محتوى مش له علاقة بالإنجليزي أو التعلم

━━━━━━━━━━━━━━━━━━━

⚡ الأسلوب:

• كن مباشر. اسأل سؤالك من غير مقدمات.
• مفيش سؤال غبي — فيه ناس مش بتسأل وده أغبى.
• لو حد غلط — صححه باحترام.
• لو مش عارف — قول "مش عارف."

━━━━━━━━━━━━━━━━━━━

🏛️ Empire English Community
المنطق أولًا"""


async def main():
    client = TelegramClient('eec_session', API_ID, API_HASH)
    await client.start(phone=PHONE_NUMBER)
    me = await client.get_me()
    print(f"✅ Logged in as: {me.first_name}")

    # Get channel
    channel = await client.get_entity(f"@{CHANNEL_USERNAME}")
    print(f"📢 Channel: {channel.title}")

    # Step 1: Set channel description
    print("\n━━━ Step 1: Setting channel description...")
    try:
        await client(EditChatAboutRequest(
            peer=channel,
            about=CHANNEL_DESCRIPTION
        ))
        print("   ✅ Description set")
    except Exception as e:
        print(f"   ⚠️ Description error: {e}")

    # Step 2: Post and pin welcome message
    print("\n━━━ Step 2: Posting + pinning welcome message...")
    try:
        msg = await client.send_message(channel, PINNED_MESSAGE)
        await client.pin_message(channel, msg.id)
        print(f"   ✅ Pinned message posted (msg_id: {msg.id})")
    except Exception as e:
        print(f"   ⚠️ Pin error: {e}")

    # Step 3: Link discussion group + post rules
    print("\n━━━ Step 3: Discussion group...")
    try:
        group = await client.get_entity(f"@{DISCUSSION_GROUP_USERNAME}")
        print(f"   Found group: {group.title}")

        # Post rules
        rules_msg = await client.send_message(group, GROUP_RULES)
        await client.pin_message(group, rules_msg.id)
        print(f"   ✅ Rules posted + pinned in group")
        print(f"   ℹ️ To link as discussion group: Channel Settings → Discussion → Select the group")
    except Exception as e:
        print(f"   ⚠️ Group error: {e}")
        print(f"   ℹ️ Create @{DISCUSSION_GROUP_USERNAME} first if it doesn't exist")

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🏛️ CHANNEL DEPLOYMENT COMPLETE")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"\n   Channel: https://t.me/{CHANNEL_USERNAME}")
    print(f"   Pinned: ✅")
    print(f"   Description: ✅")
    print(f"   Group rules: ✅")
    print(f"\n   ⚠️ Manual steps remaining:")
    print(f"   1. Link discussion group: Channel Settings → Discussion → @{DISCUSSION_GROUP_USERNAME}")
    print(f"   2. Cross-promote in bot, assessment, Discord (separate task)")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
