"""Test a single post to verify everything works."""
import asyncio
import os
from telethon import TelegramClient
from telethon.tl.types import ReactionEmoji
from telethon.tl.functions.messages import SendReactionRequest
import config
from content_engine import generate_post, get_bank_post
from image_engine import generate_image


async def main():
    client = TelegramClient('eec_session', config.API_ID, config.API_HASH)
    await client.start(phone=config.PHONE_NUMBER)
    me = await client.get_me()
    print(f"Logged in as: {me.first_name}")

    # Get channel
    with open("data/channel_id.txt", "r") as f:
        lines = f.read().strip().split("\n")
        channel_id = int(lines[0])
    channel = await client.get_entity(channel_id)
    print(f"Channel: {channel.title}")

    # Determine pillar
    from datetime import datetime
    today = datetime.now().weekday()
    pillar = config.PILLAR_SCHEDULE.get(today, "accent_lesson")
    print(f"Today's pillar: {pillar}")

    # Generate content
    print("Generating post...")
    post_text, metadata = await generate_post(pillar)
    if not post_text:
        print("No content available! Make sure data/bank/ has JSON files.")
        await client.disconnect()
        return

    print(f"Post generated ({len(post_text)} chars)")
    print("---")
    print(post_text[:200] + "...")
    print("---")

    # Generate image
    print("Generating image...")
    image_path = await generate_image(pillar, post_text, metadata)

    # Post to channel
    print("Posting to channel...")
    if image_path and os.path.exists(image_path):
        msg = await client.send_file(channel, image_path, caption=post_text)
        os.remove(image_path)
    else:
        msg = await client.send_message(channel, post_text)

    print(f"✅ Posted! Message ID: {msg.id}")
    print(f"Check your channel: https://t.me/Empire_English_Community")

    await client.disconnect()


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    asyncio.run(main())
