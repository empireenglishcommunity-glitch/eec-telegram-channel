"""
One-time channel setup script.
Creates the channel, sets username/description, links discussion group, pins welcome message.

Usage:
    python setup_channel.py

This only needs to run ONCE. After that, the main bot handles everything.
"""
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import (
    CreateChannelRequest,
    CheckUsernameRequest,
    UpdateUsernameRequest,
    EditPhotoRequest,
)
from telethon.tl.functions.messages import (
    EditChatAboutRequest,
    ExportChatInviteRequest,
)
from telethon.tl.types import InputPeerChannel
import config

# The pinned message content
PINNED_MESSAGE = """🏛️ Empire English Community

اتكلم إنجليزي — بـ American Accent — من غير courses فاشلة.

━━━━━━━━━━━━━━━━━━━

إيه ده؟

نظام تعليم إنجليزي كامل مبني للعرب.
مش مدرس بيقرّي. ده system بيخليك تتكلم.

• ٤ مستويات (من صفر لـ native-like)
• Accent أمريكي من أول يوم
• Community على Discord (voice lounges يومية)
• AI بيقيّم نطقك + كتابتك
• امتحان تحديد مستوى مجاني (TOEFL-equivalent)

━━━━━━━━━━━━━━━━━━━

ليه تفضل هنا؟

كل يوم هتلاقي:
🎯 درس accent قصير (صوت أمريكي واحد)
💣 myth بنكسره (حاجة كنت فاكرها صح وهي غلط)
🔥 نتائج حقيقية (ناس زيك بدأت من صفر)
🏛️ إزاي النظام شغال من جوه

━━━━━━━━━━━━━━━━━━━

تعمل إيه دلوقتي؟

١. اعرف مستواك الحقيقي (مجاني، ٢٠ دقيقة):
🔗 assessment.empireenglish.online

٢. عايز تفاصيل عن الباقات والأسعار؟ كلّم الـ bot:
🤖 @EmpireEnglishBot

٣. عايز تبدأ فورًا؟ ادخل الـ Discord:
💬 https://discord.gg/empireenglish

━━━━━━━━━━━━━━━━━━━

📢 القناة دي بتنزّل محتوى كل يوم سبت→خميس الساعة ٩ الصبح (توقيت دبي).
الجمعة راحة.

ℳ MACAL Empire — Common Sense First"""

# Discussion group rules
GROUP_RULES = """🏛️ قوانين المجموعة — Empire English Community

━━━━━━━━━━━━━━━━━━━

أهلًا بيك. المجموعة دي مكان للناس اللي عايزة تتكلم إنجليزي بجد.
عشان المكان يفضل مفيد — فيه قوانين بسيطة:

━━━━━━━━━━━━━━━━━━━

✅ المسموح:

• اسأل أي سؤال عن الإنجليزي (نطق، grammar، vocabulary، أي حاجة)
• شارك progress بتاعك (recording، score، إنجاز)
• ساعد حد تاني (لو عارف الإجابة — قول)
• ناقش بوستات القناة (وده الهدف الأساسي)
• اكتب بالعربي أو الإنجليزي أو الاتنين — محدش هيحكم عليك

━━━━━━━━━━━━━━━━━━━

❌ الممنوع:

• Spam أو إعلانات (هتتشال فورًا — مفيش إنذار)
• روابط لقنوات تانية أو courses تانية
• إهانة أو تنمّر على حد (ولا حتى "بهزار")
• Voice notes أطول من دقيقتين
• محتوى مش له علاقة بالإنجليزي أو التعلم
• شحاتة members ("ادخلوا قناتي" ← ban فوري)

━━━━━━━━━━━━━━━━━━━

⚡ الأسلوب:

• كن direct. اسأل سؤالك من غير مقدمات.
• مفيش سؤال غبي — فيه ناس مش بتسأل وده أغبى.
• لو حد غلط — صححه باحترام.
• لو مش عارف — قول "مش عارف."

━━━━━━━━━━━━━━━━━━━

🏛️ Empire English Community
Common Sense First"""


async def main():
    """Create and configure the EEC announcement channel."""
    client = TelegramClient("eec_session", config.API_ID, config.API_HASH)
    await client.start(phone=config.PHONE_NUMBER)

    print("✅ Logged in successfully")
    me = await client.get_me()
    print(f"   Account: {me.first_name} ({me.phone})")

    # Step 1: Create the channel
    print("\n🏛️ Step 1: Creating channel...")
    try:
        result = await client(CreateChannelRequest(
            title=config.CHANNEL_TITLE,
            about=config.CHANNEL_DESCRIPTION,
            megagroup=False  # False = channel (not group)
        ))
        channel = result.chats[0]
        channel_id = channel.id
        access_hash = channel.access_hash
        print(f"   ✅ Channel created: {config.CHANNEL_TITLE} (ID: {channel_id})")
    except Exception as e:
        if "CHANNELS_TOO_MUCH" in str(e):
            print("   ⚠️ You've hit Telegram's channel limit. Delete unused channels first.")
            return
        raise e

    # Step 2: Set public username
    print("\n🔗 Step 2: Setting username...")
    input_channel = InputPeerChannel(channel_id=channel_id, access_hash=access_hash)
    try:
        # Check if username is available
        available = await client(CheckUsernameRequest(
            channel=input_channel,
            username=config.CHANNEL_USERNAME
        ))
        if available:
            await client(UpdateUsernameRequest(
                channel=input_channel,
                username=config.CHANNEL_USERNAME
            ))
            print(f"   ✅ Username set: @{config.CHANNEL_USERNAME}")
        else:
            print(f"   ❌ Username @{config.CHANNEL_USERNAME} is taken!")
            print("   Try a different one in .env (CHANNEL_USERNAME)")
            # Continue anyway — channel works without public username
    except Exception as e:
        print(f"   ⚠️ Could not set username: {e}")

    # Step 3: Pin the welcome message
    print("\n📌 Step 3: Posting and pinning welcome message...")
    channel_entity = await client.get_entity(input_channel)
    msg = await client.send_message(channel_entity, PINNED_MESSAGE)
    await client.pin_message(channel_entity, msg.id)
    print(f"   ✅ Welcome message posted and pinned (msg_id: {msg.id})")

    # Step 4: Link discussion group (if it exists)
    print("\n💬 Step 4: Linking discussion group...")
    try:
        group = await client.get_entity(config.DISCUSSION_GROUP_USERNAME)
        # Note: Linking discussion group requires specific API call
        # For now, print instructions
        print(f"   ℹ️ Discussion group found: @{config.DISCUSSION_GROUP_USERNAME}")
        print(f"   ℹ️ To link: Channel Settings → Discussion → Select the group")
        print(f"   (Telegram requires this to be done via the app UI)")

        # Post rules in the discussion group
        print("\n📋 Step 5: Posting rules in discussion group...")
        rules_msg = await client.send_message(group, GROUP_RULES)
        await client.pin_message(group, rules_msg.id)
        print(f"   ✅ Rules posted and pinned in discussion group")
    except Exception as e:
        print(f"   ⚠️ Could not find discussion group: {e}")
        print(f"   Create @{config.DISCUSSION_GROUP_USERNAME} first, then re-run this step")

    # Summary
    print("\n" + "=" * 50)
    print("🏛️ CHANNEL SETUP COMPLETE")
    print("=" * 50)
    print(f"\n   Channel: https://t.me/{config.CHANNEL_USERNAME}")
    print(f"   Channel ID: {channel_id}")
    print(f"   Welcome message: Pinned ✅")
    print(f"\n   ⚡ Next: Run the main bot (python main.py)")
    print(f"   It will handle daily posting, reactions, and engagement automatically.")

    # Save channel ID for the main bot
    with open("data/channel_id.txt", "w") as f:
        f.write(f"{channel_id}\n{access_hash}")
    print(f"\n   Channel ID saved to data/channel_id.txt")

    await client.disconnect()


if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)
    asyncio.run(main())
