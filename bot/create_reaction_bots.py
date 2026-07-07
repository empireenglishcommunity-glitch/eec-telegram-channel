"""
Create 8 reaction bots via @BotFather automatically.
Uses the Telethon userbot to send commands to BotFather.

Run ONCE: python create_reaction_bots.py
Saves all tokens to data/reaction_bot_tokens.txt
"""
import asyncio
import os
import re
from telethon import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "")

NUM_BOTS = 8
BOT_NAME_PREFIX = "EEC Member"
BOT_USERNAME_PREFIX = "eec_member_"


async def main():
    client = TelegramClient('eec_session', API_ID, API_HASH)
    await client.start(phone=PHONE_NUMBER)
    me = await client.get_me()
    print(f"✅ Logged in as: {me.first_name}")

    botfather = await client.get_entity("@BotFather")
    tokens = []

    for i in range(1, NUM_BOTS + 1):
        bot_name = f"{BOT_NAME_PREFIX} {i}"
        bot_username = f"{BOT_USERNAME_PREFIX}{i}_bot"

        print(f"\n━━━ Creating bot {i}/{NUM_BOTS}: {bot_username}")

        # Send /newbot command
        await client.send_message(botfather, "/newbot")
        await asyncio.sleep(2)

        # Send bot name
        await client.send_message(botfather, bot_name)
        await asyncio.sleep(2)

        # Send username
        await client.send_message(botfather, bot_username)
        await asyncio.sleep(3)

        # Read the response to get the token
        messages = await client.get_messages(botfather, limit=1)
        response_text = messages[0].text

        # Extract token from BotFather response
        token_match = re.search(r'(\d+:[A-Za-z0-9_-]+)', response_text)

        if token_match:
            token = token_match.group(1)
            tokens.append(token)
            print(f"   ✅ Token: {token[:20]}...")
        elif "Sorry" in response_text or "already" in response_text:
            print(f"   ⚠️ Username {bot_username} might be taken. Trying with suffix...")
            # Try with random suffix
            import random
            alt_username = f"{BOT_USERNAME_PREFIX}{i}_{random.randint(10,99)}_bot"
            await client.send_message(botfather, alt_username)
            await asyncio.sleep(3)

            messages = await client.get_messages(botfather, limit=1)
            response_text = messages[0].text
            token_match = re.search(r'(\d+:[A-Za-z0-9_-]+)', response_text)
            if token_match:
                token = token_match.group(1)
                tokens.append(token)
                print(f"   ✅ Token (alt): {token[:20]}...")
            else:
                print(f"   ❌ Failed to create bot {i}")
                print(f"   Response: {response_text[:200]}")
        else:
            print(f"   ❌ No token found in response")
            print(f"   Response: {response_text[:200]}")

        await asyncio.sleep(2)  # Rate limit safety

    # Save tokens
    os.makedirs("data", exist_ok=True)
    with open("data/reaction_bot_tokens.txt", "w") as f:
        for token in tokens:
            f.write(f"{token}\n")

    print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"✅ Created {len(tokens)} bots")
    print(f"   Tokens saved to: data/reaction_bot_tokens.txt")

    if tokens:
        # Now add bots as admins to the channel
        print(f"\n━━━ Adding bots as channel admins...")
        with open("data/channel_id.txt", "r") as f:
            channel_id = int(f.read().strip().split("\n")[0])
        channel = await client.get_entity(channel_id)

        admin_rights = ChatAdminRights(
            post_messages=True,
            edit_messages=False,
            delete_messages=False,
            ban_users=False,
            invite_users=False,
            pin_messages=False,
            add_admins=False,
            manage_call=False,
        )

        for i, token in enumerate(tokens):
            bot_id = int(token.split(":")[0])
            try:
                bot_entity = await client.get_entity(bot_id)
                await client(EditAdminRequest(
                    channel=channel,
                    user_id=bot_entity,
                    admin_rights=admin_rights,
                    rank=f"Member {i+1}"
                ))
                print(f"   ✅ Bot {i+1} added as admin")
            except Exception as e:
                print(f"   ⚠️ Could not add bot {i+1} as admin: {e}")
                print(f"   (You may need to start a chat with the bot first)")
            await asyncio.sleep(1)

    print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🏛️ DONE. Next: restart the main bot service.")
    print(f"   The reaction engine will use these tokens automatically.")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
