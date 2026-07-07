"""
Create more reaction bots. Sends /cancel first to reset BotFather state.
Then creates bots one by one with proper delays.
"""
import asyncio
import os
import re
import random
from telethon import TelegramClient
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
from dotenv import load_dotenv
import aiohttp

load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "")

TARGET_BOTS = 10


async def main():
    client = TelegramClient('eec_session', API_ID, API_HASH)
    await client.start(phone=PHONE_NUMBER)
    me = await client.get_me()
    print(f"✅ Logged in as: {me.first_name}")

    # Load existing tokens
    tokens = []
    if os.path.exists("data/reaction_bot_tokens.txt"):
        with open("data/reaction_bot_tokens.txt", "r") as f:
            tokens = [line.strip() for line in f if line.strip()]
    print(f"📋 Existing bots: {len(tokens)}")

    needed = TARGET_BOTS - len(tokens)
    if needed <= 0:
        print(f"✅ Already have {len(tokens)} bots. No more needed.")
    else:
        print(f"🔨 Creating {needed} more bots...")

        botfather = await client.get_entity("@BotFather")

        # Reset BotFather state
        await client.send_message(botfather, "/cancel")
        await asyncio.sleep(2)

        for i in range(needed):
            bot_num = len(tokens) + 1
            suffix = random.randint(100, 999)
            bot_username = f"eec_r{bot_num}_{suffix}_bot"
            bot_name = f"Empire Member {bot_num}"

            print(f"\n━━━ Bot {bot_num}: {bot_username}")

            # Send /newbot
            await client.send_message(botfather, "/newbot")
            await asyncio.sleep(3)

            # Check response
            msgs = await client.get_messages(botfather, limit=1)
            resp = msgs[0].text
            if "Alright" not in resp and "name" not in resp.lower():
                print(f"   ⚠️ Unexpected response: {resp[:80]}")
                await client.send_message(botfather, "/cancel")
                await asyncio.sleep(2)
                continue

            # Send name
            await client.send_message(botfather, bot_name)
            await asyncio.sleep(3)

            # Check response
            msgs = await client.get_messages(botfather, limit=1)
            resp = msgs[0].text
            if "username" not in resp.lower() and "pick" not in resp.lower():
                print(f"   ⚠️ Name step unexpected: {resp[:80]}")
                await client.send_message(botfather, "/cancel")
                await asyncio.sleep(2)
                continue

            # Send username
            await client.send_message(botfather, bot_username)
            await asyncio.sleep(4)

            # Check for token
            msgs = await client.get_messages(botfather, limit=1)
            resp = msgs[0].text
            token_match = re.search(r'(\d+:[A-Za-z0-9_-]+)', resp)

            if token_match:
                token = token_match.group(1)
                tokens.append(token)
                print(f"   ✅ Created! Token: {token[:25]}...")
            else:
                print(f"   ❌ Failed: {resp[:100]}")
                await client.send_message(botfather, "/cancel")
                await asyncio.sleep(2)

            await asyncio.sleep(3)

        # Save all tokens
        with open("data/reaction_bot_tokens.txt", "w") as f:
            for token in tokens:
                f.write(f"{token}\n")
        print(f"\n✅ Total tokens saved: {len(tokens)}")

    # Add all bots as channel admins
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
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.telegram.org/bot{token}/getMe") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        bot_username = data["result"]["username"]

                        bot_entity = await client.get_entity(f"@{bot_username}")
                        await client(EditAdminRequest(
                            channel=channel,
                            user_id=bot_entity,
                            admin_rights=admin_rights,
                            rank="Member"
                        ))
                        print(f"   ✅ Bot {i+1}: @{bot_username} — admin ✓")
                    else:
                        print(f"   ⚠️ Bot {i+1}: token invalid")
        except Exception as e:
            error_msg = str(e)
            if "already" in error_msg.lower() or "admin" in error_msg.lower():
                print(f"   ✅ Bot {i+1}: already admin")
            else:
                print(f"   ⚠️ Bot {i+1}: {error_msg[:80]}")
        await asyncio.sleep(1)

    print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🏛️ DONE. {len(tokens)} reaction bots ready.")
    print(f"   Restart service: systemctl restart eec-channel-bot")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
