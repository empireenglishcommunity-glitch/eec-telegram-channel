"""
Fix: Add existing reaction bots as channel admins.
Resolves bots by username (not ID) to fix the entity lookup error.

Also creates any remaining bots if less than 8 exist.
"""
import asyncio
import os
import re
from telethon import TelegramClient
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "")


async def main():
    client = TelegramClient('eec_session', API_ID, API_HASH)
    await client.start(phone=PHONE_NUMBER)
    me = await client.get_me()
    print(f"✅ Logged in as: {me.first_name}")

    # Read existing tokens
    tokens = []
    if os.path.exists("data/reaction_bot_tokens.txt"):
        with open("data/reaction_bot_tokens.txt", "r") as f:
            tokens = [line.strip() for line in f if line.strip()]
    print(f"📋 Found {len(tokens)} existing bot tokens")

    # If we have less than 8, create more
    botfather = await client.get_entity("@BotFather")
    while len(tokens) < 8:
        i = len(tokens) + 1
        bot_username = f"eec_react_{i}_bot"
        print(f"\n━━━ Creating bot {i}: {bot_username}")

        await client.send_message(botfather, "/newbot")
        await asyncio.sleep(3)

        await client.send_message(botfather, f"EEC React {i}")
        await asyncio.sleep(3)

        await client.send_message(botfather, bot_username)
        await asyncio.sleep(4)

        messages = await client.get_messages(botfather, limit=1)
        response_text = messages[0].text

        token_match = re.search(r'(\d+:[A-Za-z0-9_-]+)', response_text)
        if token_match:
            token = token_match.group(1)
            tokens.append(token)
            print(f"   ✅ Created: {bot_username} — token: {token[:20]}...")
        else:
            print(f"   ⚠️ Failed: {response_text[:150]}")
            # Try alternate username
            import random
            alt = f"eec_r{i}_{random.randint(100,999)}_bot"
            await client.send_message(botfather, alt)
            await asyncio.sleep(4)
            messages = await client.get_messages(botfather, limit=1)
            response_text = messages[0].text
            token_match = re.search(r'(\d+:[A-Za-z0-9_-]+)', response_text)
            if token_match:
                token = token_match.group(1)
                tokens.append(token)
                print(f"   ✅ Created (alt): {alt} — token: {token[:20]}...")
            else:
                print(f"   ❌ Skipping bot {i}")
                break

        await asyncio.sleep(2)

    # Save all tokens
    with open("data/reaction_bot_tokens.txt", "w") as f:
        for token in tokens:
            f.write(f"{token}\n")
    print(f"\n✅ Total tokens saved: {len(tokens)}")

    # Now add each bot as admin — resolve by sending /start to each first
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
            # Get bot username from BotFather using getMe equivalent
            # We need to resolve the entity — try by ID with InputPeerUser
            from telethon.tl.types import InputPeerUser, InputUser
            from telethon.tl.functions.users import GetUsersRequest
            from telethon.tl.types import InputUser

            # Try to get the bot entity by messaging it first (creates the entity cache)
            # Use the Bot API to get bot info
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.telegram.org/bot{token}/getMe") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        bot_username = data["result"]["username"]
                        print(f"   Bot {i+1}: @{bot_username}")

                        # Resolve by username
                        bot_entity = await client.get_entity(f"@{bot_username}")

                        # Add as admin
                        await client(EditAdminRequest(
                            channel=channel,
                            user_id=bot_entity,
                            admin_rights=admin_rights,
                            rank=f"Member"
                        ))
                        print(f"   ✅ Bot {i+1} (@{bot_username}) added as admin")
                    else:
                        print(f"   ⚠️ Bot {i+1} token invalid")
        except Exception as e:
            print(f"   ⚠️ Bot {i+1} error: {e}")
        await asyncio.sleep(2)

    print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🏛️ DONE.")
    print(f"   {len(tokens)} bots ready for reactions")
    print(f"   Restart the main bot: systemctl restart eec-channel-bot")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
