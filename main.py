from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command, CommandObject, CommandStart
from aiogram.enums import ParseMode
import asyncio
import logging
import json


bot_token = ''
bot: Bot
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)


def load_settings():
    global bot_token
    with open('./settings.json', 'r', encoding='utf-8') as f:
        settings = json.loads(f.read())
        bot_token = settings['bot_token']


# /start handler
@dp.message(CommandStart(deep_link=True))  # , magic=F.args.regexp(re.compile(r'Regex   token'))
async def start(message: types.Message, command: CommandObject):
    command_args: str = command.args
    await message.answer(f'StartToken \= {command_args}')
    await message.answer('Вы подписаны на уведомления')


# /disable handler
@dp.message(Command('disable'))
async def disable(message: types.Message, command: CommandObject):
    await message.answer('Уведомления отключены')


# /mail handler
@dp.message(Command('mail'))
async def mail(message: types.Message, command: CommandObject):
    sender_name: str = 'Max'
    link: str = 'https://aikido.ru/mail/'
    await message.answer(f'Вам пришло письмо от *{sender_name}*\n\n'
                         f'[Перейти на сайт]({link})')


# /votes handler
@dp.message(Command('votes'))
async def votes(message: types.Message, command: CommandObject):
    vote_name: str = 'Выбор названия клуба'
    start, end = '11\.11\.2011', '12\.12\.2022'
    link: str = 'https://aikido.ru/votes/1/'
    await message.answer(f'Вы участвуете в голосовании: *{vote_name}*\n'
                         f'Сроки голосования: {start} \- {end}\n\n'
                         f'[Перейти к голосованию]({link})')


async def main():
    global bot, dp
    bot = Bot(bot_token, parse_mode=ParseMode.MARKDOWN_V2)
    await dp.start_polling(bot)

if __name__ == '__main__':
    load_settings()
    asyncio.run(main())
