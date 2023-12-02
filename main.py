from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command, CommandObject, CommandStart
from aiogram.enums import ParseMode
import asyncio
import logging
import json
import requests


bot_token = ''
bot: Bot
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)
url = 'http://aikido.ru/tg/'


def load_settings():
    global bot_token
    with open('./settings.json', 'r', encoding='utf-8') as f:
        settings = json.loads(f.read())
        bot_token = settings['bot_token']


# /start handler
@dp.message(CommandStart(deep_link=True))  # , magic=F.args.regexp(re.compile(r'Regex   token'))
async def start(message: types.Message, command: CommandObject):
    command_args: str = command.args
    res = requests.post(url + 'start', data={'tgID': message.chat.id, 'token': command_args})
    if res.ok:
        await message.answer('Вы подписаны на уведомления')
    else:
        await message.answer('Произошла ошибка при подписке на уведомления')


# /unsubscribe handler
@dp.message(Command('unsubscribe'))
async def unsubscribe(message: types.Message):
    res = requests.post(url + 'unsubscribe', data={'tgID': message.chat.id})
    if res.ok:
        await message.answer('Вы отписаны от уведомлений')
    else:
        await message.answer('Ошибка при отписке')


# /mail handler
@dp.message(Command('mail'))
async def mail(message: types.Message, command: CommandObject):
    res = requests.get(url + 'mail', data={'tgID': message.chat.id})
    if res.ok:
        ans = res.json()
        sender_name: str = ans['sender_name']
        link: str = 'https://aikido.ru/mail/'
        await message.answer(f'Вам пришло письмо от *{sender_name}*\n\n'
                             f'[Перейти на сайт]({link})')
    else:
        await message.answer('Ошибка при проверке почты')


# /votes handler
@dp.message(Command('votes'))
async def votes(message: types.Message, command: CommandObject):
    res = requests.get(url + 'mail', data={'tgID': message.chat.id})
    if res.ok:
        ans = res.json()
        vote_name: str = ans['vote_name']
        start, end = ['start'], ['end']
        link: str = f'https://aikido.ru/votes/{ans["vote_id"]}'
        await message.answer(f'Вы участвуете в голосовании: *{vote_name}*\n'
                             f'Сроки голосования: {start} \- {end}\n\n'
                             f'[Перейти к голосованию]({link})')
    else:
        await message.answer('Ошибка при проверке голосований')


async def main():
    global bot, dp
    bot = Bot(bot_token, parse_mode=ParseMode.MARKDOWN_V2)
    await dp.start_polling(bot)

if __name__ == '__main__':
    load_settings()
    asyncio.run(main())
