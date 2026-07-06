"""Get existing channel ID and save it."""
import asyncio
import os
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()

async def main():
    client = TelegramClient('eec_session', int(os.getenv('API_ID')), os.getenv('API_HASH'))
    await client.start(phone=os.getenv('PHONE_NUMBER'))
    entity = await client.get_entity('@Empire_English_Community')
    print(f'Channel ID: {entity.id}')
    print(f'Access Hash: {entity.access_hash}')
    os.makedirs('data', exist_ok=True)
    with open('data/channel_id.txt', 'w') as f:
        f.write(str(entity.id))
        f.write('\n')
        f.write(str(entity.access_hash))
    print('Saved to data/channel_id.txt')
    await client.disconnect()

asyncio.run(main())
