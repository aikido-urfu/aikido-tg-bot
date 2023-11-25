from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import asyncio
import json


bot_token = ''
chat_id = -1
logging.basicConfig(level=logging.INFO)

def load_settings():
    global bot_token, chat_id
    with open('./settings.json', 'r', encoding='utf-8') as f:
        settings = json.loads(f.read())
        bot_token = settings['bot_token']
        chat_id = settings['chat_id']


# @client.on(events)


async def main():
    bot = telegram.Bot(bot_token)

    async with bot:
        print(await bot.get_me())
        last_msgs = (await bot.get_updates())
        print(last_msgs)
        await bot.send_message(text=f'Hello ', chat_id=chat_id)

if __name__ == '__main__':
    load_settings()
    asyncio.run(main())
