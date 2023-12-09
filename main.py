from datetime import date
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command, CommandObject, CommandStart
from aiogram.utils.formatting import Text, Bold, as_numbered_list, Code, TextLink
from aiogram.enums import ParseMode
import asyncio
import logging
import json
import requests


bot_token = ''
bot: Bot
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)
url = 'localhost:123/telegram/'
url = "https://reqres.in/api/"


def load_settings():
    global bot_token
    with open('./settings.json', 'r', encoding='utf-8') as f:
        settings = json.loads(f.read())
        bot_token = settings['bot_token']


# /start handler
@dp.message(CommandStart(deep_link=True))
async def start(message: types.Message, command: CommandObject):
    command_args: str = command.args
    res = requests.post(url + 'start', data={'tgid': message.chat.id, 'token': command_args})
    if res.ok:
        await message.answer('Вы подписаны на уведомления')
    else:
        await message.answer('Произошла ошибка при подписке на уведомления')


# /unsubscribe handler
@dp.message(Command('unsubscribe'))
async def unsubscribe(message: types.Message):
    res = requests.delete(url + 'unsubscribe', data={'tgid': message.chat.id})
    if res.ok:
        await message.answer('Вы отписаны от уведомлений')
    elif res.status_code == 400:
        await message.answer('Вы не были подписаны на уведомления')
    else:
        await message.answer('Произошла ошибка при отписке от уведомлений.\nПопробуйте позже.')


# /mail handler
@dp.message(Command('mail'))
async def mail(message: types.Message) -> None:
    res = requests.get(url + 'mail', data={'tgid': message.chat.id})
    if res.ok:
        answer = res.json()
        if not answer:
            await message.answer('Нет новых писем')
            return
        for letter in answer:
            sender_name: str = letter['sender']
            receive_date: date = date.fromisoformat(letter['date'])  # '2012-11-04T14:51:06.157Z'
            link: str = 'https://aikido.ru/mail/'
            content = Text(
                'Вам пришло письмо от ', Bold(sender_name), '\n',
                'В ', receive_date.strftime("%H:%M %d.%m.%Y"), '\n',  # 14:30 07.12.2012
                TextLink('Перейти на сайт', url=link)
            )
            await message.answer(**content.as_kwargs())
    else:
        await message.answer('Ошибка при проверке почты')


# /votes handler
@dp.message(Command('votes'))
async def votes(message: types.Message, command: CommandObject):
    res = requests.get(url + 'mail', data={'tgid': message.chat.id})
    if res.ok:
        answer = res.json()
        if not answer:
            await message.answer('Нет активных голосований')
            return
        for vote in answer:
            vote_name: str = vote['title']
            start_date: date = date.fromisoformat(vote['dateOfStart'])
            end_date: date = date.fromisoformat(vote['dateOfEnd'])
            link: str = vote['url']
            content = Text(
                'Вы участвуете в голосовании: ', Bold(vote_name), '\n',
                'Сроки голосования: ', start_date.strftime("%H:%M %d.%m.%Y"), '\-',
                end_date.strftime("%H:%M %d.%m.%Y"), '\n',
                TextLink('Перейти к голосованию', url=link)
            )
            await message.answer(**content.as_kwargs())
    else:
        await message.answer('Ошибка при проверке активных голосований')


async def main():
    global bot, dp
    bot = Bot(bot_token, parse_mode=ParseMode.MARKDOWN_V2)
    await dp.start_polling(bot)

if __name__ == '__main__':
    load_settings()
    asyncio.run(main())
