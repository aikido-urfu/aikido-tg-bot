from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command, CommandObject, CommandStart
from aiogram.utils.formatting import Text, Bold, TextLink
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config_reader import config
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
    try:
        res = requests.post(url + 'start', data={'tgid': message.chat.id, 'token': command_args})

        if res.ok:
            await message.answer('Вы подписаны на уведомления')
        elif res.status_code == 400:
            await message.answer('Вы уже подписаны на уведомления')
        else:
            raise Exception
    except:
        await message.answer('Произошла ошибка при подписке на уведомления')
        return


# /mail handler
@dp.message(Command('mail'))
async def mail(message: types.Message) -> None:
    try:
        res = requests.get(url + 'mail', data={'tgid': message.chat.id})
        if res.ok:
            answer = res.json()
            if not answer:
                await message.answer('Нет новых писем')
                return
            for letter in answer['data']:
                sender_name: str = letter['name']
                # receive_date: datetime = datetime.strptime(letter['date'], "%Y-%m-%dT%H:%M:%S.%f%z")  # '2012-11-04T14:51:06.157Z'
                receive_date: datetime = datetime.strptime('2012-11-04T14:51:06.157Z', "%Y-%m-%dT%H:%M:%S.%f%z")
                link: str = 'https://aikido.ru/mail/'
                content = Text(
                    'Вам пришло письмо от ', Bold(sender_name), '\n',
                    'В ', receive_date.strftime("%H:%M %d.%m.%Y"), '\n',  # 14:30 07.12.2012
                    TextLink('Перейти на сайт', url=link)
                )
                await message.answer(**content.as_kwargs())
        else:
            raise Exception
    except:
        await message.answer('Произошла ошибка при проверке почты')


# /votes handler
@dp.message(Command('votes'))
async def votes(message: types.Message):
    try:
        res = requests.get(url + 'mail', data={'tgid': message.chat.id})
        if res.ok:
            answer = res.json()
            if not answer:
                await message.answer('Нет активных голосований')
                return
            for vote in answer:
                vote_name: str = vote['title']
                start_date: datetime = datetime.strptime(vote['dateOfStart'], "%Y-%m-%dT%H:%M:%S.%f%z")
                end_date: datetime = datetime.strptime(vote['dateOfEnd'], "%Y-%m-%dT%H:%M:%S.%f%z")
                link: str = vote['url']
                content = Text(
                    'Вы участвуете в голосовании: ', Bold(vote_name), '\n',
                    'Сроки голосования: ', start_date.strftime("%H:%M %d.%m.%Y"), '\-',
                    end_date.strftime("%H:%M %d.%m.%Y"), '\n',
                    TextLink('Перейти к голосованию', url=link)
                )
                await message.answer(**content.as_kwargs())
        else:
            raise Exception
    except:
        await message.answer('Произошла ошибка при проверке активных голосований')


@dp.callback_query(F.data == "not_unsubscribe")
async def not_unsubscribe(callback: types.CallbackQuery):
    await callback.message.edit_text(**Text('Вы не будете отписаны.').as_kwargs())
    await callback.answer()


@dp.callback_query(F.data == "unsubscribe")
async def unsubscribe(callback: types.CallbackQuery):
    try:
        res = requests.delete(url + 'unsubscribe', data={'tgid': callback.from_user.id})
        answer: Text
        if res.ok:
            answer = Text('Вы отписаны от уведомлений')
        elif res.status_code == 400:
            answer = Text('Вы не были подписаны на уведомления')
        else:
            raise Exception
        await callback.message.edit_text(**answer.as_kwargs())
        await callback.answer()
    except:
        await callback.message.answer(**Text('Произошла ошибка при отписке от уведомлений.\nПопробуйте позже.').as_kwargs())
        await callback.answer()


# /unsubscribe handler
@dp.message(Command('unsubscribe'))
async def unsubscribe_handler(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Да",
        callback_data="unsubscribe")
    )
    builder.add(types.InlineKeyboardButton(
        text="Нет",
        callback_data="not_unsubscribe")
    )

    await message.answer(
        'Вы уверены, что хотите отписаться?',
        reply_markup=builder.as_markup(),
    )


async def main():
    global bot, dp
    bot = Bot(config.bot_token.get_secret_value(), parse_mode=ParseMode.MARKDOWN_V2)
    await dp.start_polling(bot)

if __name__ == '__main__':
    load_settings()
    asyncio.run(main())
