import logs
import asyncio
import re
import shutil
import signal
import subprocess
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command, CommandObject, CommandStart
from aiogram.utils.formatting import Text, Bold, TextLink, Italic, as_list, BotCommand
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config_reader import config
import asyncio
import logging
import requests
import sys
import os
import psutil

bot: Bot
dp = Dispatcher()
url = config.api_url.get_secret_value()


def rus_month(input_string):
    months_translation = {
        "January": "Января",
        "February": "Февраля",
        "March": "Марта",
        "April": "Апреля",
        "May": "Мая",
        "June": "Июня",
        "July": "Июля",
        "August": "Августа",
        "September": "Сентября",
        "October": "Октября",
        "November": "Ноября",
        "December": "Декабря"
    }
    for english_month, russian_translation in months_translation.items():
        if english_month in input_string:
            input_string = input_string.replace(english_month, russian_translation)
            break
    return input_string


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


# /votes handler
@dp.message(Command('votes'))
async def votes(message: types.Message):
    try:
        res = requests.get(url + 'votes', data={'tgid': message.chat.id})
        if res.ok:
            answer = res.json()
            if not answer:
                await message.answer('Нет активных голосований')
                return
            for vote in answer['votes']:
                vote_name: str = vote['text']
                # start_date: datetime = datetime.strptime(vote['dateOfStart'], "%Y-%m-%dT%H:%M:%S.%f%z")
                # end_date: datetime = datetime.strptime(vote['dateOfEnd'], "%Y-%m-%dT%H:%M:%S.%f%z")
                link: str = vote['url']
                date_format: str = "%H:%M, %d.%m.%Y"

                # vote_name = 'Выбор названия клуба'
                start_date = datetime.strptime('2012-11-04T14:51:06.157Z', "%Y-%m-%dT%H:%M:%S.%f%z")
                end_date = datetime.strptime('2012-12-05T18:51:06.157Z', "%Y-%m-%dT%H:%M:%S.%f%z")
                # link = 'https://aikido.ru/votes/1/'

                content = Text(
                    '🗳 ', Bold(f'Голосование: {vote_name}'), '\n',
                    Italic('Сроки голосования: '), start_date.strftime(date_format), ' - ',
                    end_date.strftime(date_format), '\n\n',
                    TextLink('🔗 Перейти к голосованию', url=link)
                )
                await message.answer(**content.as_kwargs())
        else:
            raise Exception
    except Exception as err:
        await message.answer('Произошла ошибка при проверке активных голосований')
        logging.error(err)


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
        await callback.message.answer(
            **Text('Произошла ошибка при отписке от уведомлений.\nПопробуйте позже.').as_kwargs())
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


async def kill_proc(server_type: str = None):
    if server_type is None:
        return

    cur_proc: asyncio.subprocess.Process | None = dp.get(server_type)

    if cur_proc:
        try:
            for child in psutil.Process(cur_proc.pid).children(recursive=True):
                child.terminate()
            cur_proc.terminate()
            await cur_proc.wait()
        except:
            dp[server_type] = None
        dp[server_type] = None
        # if cur_proc.returncode == 1:
        #     dp[server_type] = None
        # else:
        #     raise Exception()
        logging.info(f'kill_proc of {server_type}')
        # cur_proc.send_signal(signal.CTRL_C_EVENT)
        # cur_proc.send_signal(signal.SIGINT)
        # await cur_proc.wait()


# @dp.message(Command('kill'))
@dp.message(Command(re.compile(r'^kill_(web|server|files|all)$')))
async def kill(message: types.Message, command: CommandObject):
    picked_upd_type = message.text.replace('/kill_', '')
    try:
        await kill_proc(picked_upd_type)
        await message.answer(f'Процесс {picked_upd_type} завершен')
    except Exception as err:
        await message.answer('Произошла ошибка во время завершения процесса')
        logging.error(f'app_kill: {err}')


def copy_and_replace(source_path, destination_path):
    if os.path.exists(destination_path):
        os.remove(destination_path)
    shutil.copy2(source_path, destination_path)


# @dp.message(Command('update'))
@dp.message(Command(re.compile(r'^update_(web|server|files|all)$')))
async def update(message: types.Message):
    upd_type = {
        'web': 'aikido-web-core',
        'server': 'aikido-server-core',
        'files': 'aikido-server-files',
        'all': 'all'
    }
    commands = [
        ['git', 'fetch'],
        ['git', 'stash', '-u'],
        ['git', 'pull', '--force'],
        ['npm', 'i'],
    ]
    run_commands = {
        'web': 'npx webpack serve --config webpack.config.dev.js --port 3004',
        'server': 'npm start',
        'files': '',
        'all': 'all',
    }
    picked_upd_type = message.text.replace('/update_', '')

    if picked_upd_type == 'all':
        return

    if picked_upd_type == 'files':
        return
    try:
        await kill_proc(picked_upd_type)

        folder = f"{config.git_path.get_secret_value()}/{upd_type[picked_upd_type]}/"
        for cmd in commands:
            result = subprocess.run(cmd,
                                    capture_output=True,
                                    text=True,
                                    cwd=folder,
                                    shell=True)
            logging.info(f'Start of {picked_upd_type}: {result}')

        if picked_upd_type == 'server':
            copy_and_replace('./API_URL.ts', folder + 'API_URL.ts')

        proc = await asyncio.create_subprocess_shell(cmd=run_commands[picked_upd_type],
                                                     cwd=folder,
                                                     shell=True,
                                                     stdout=asyncio.subprocess.PIPE,
                                                     stderr=asyncio.subprocess.PIPE)
        dp[picked_upd_type] = proc
        await message.answer(f'{picked_upd_type} был успешно обновлен')
    except Exception as err:
        await message.answer('Произошла ошибка во время обновления приложения')
        logging.error(f'app_update: {err}')


@dp.message(Command(re.compile(r'^start_(web|server|files|all)$')))
async def start(message: types.Message):
    upd_type = {
        'web': 'aikido-web-core',
        'server': 'aikido-server-core',
        'files': 'aikido-server-files',
        'all': 'all'
    }
    run_commands = {
        'web': 'npx webpack serve --config webpack.config.dev.js --port 3004',
        'server': 'npm start',
        'files': '',
        'all': 'all',
    }
    try:
        picked_upd_type = message.text.replace('/start_', '')
        folder = f"{config.git_path.get_secret_value()}/{upd_type[picked_upd_type]}/"
        if picked_upd_type in ['files', 'all']:
            return
        if dp.get(picked_upd_type):
            await kill_proc(picked_upd_type)
        if picked_upd_type == 'server':
            copy_and_replace('./API_URL.ts', folder + 'API_URL.ts')
        proc = await asyncio.create_subprocess_shell(cmd=run_commands[picked_upd_type],
                                                     cwd=folder,
                                                     shell=True,
                                                     stdout=asyncio.subprocess.PIPE,
                                                     stderr=asyncio.subprocess.PIPE)
        dp[picked_upd_type] = proc
        await message.answer(f'{picked_upd_type} успешно запущен')
    except Exception as err:
        await message.answer('Произошла ошибка при старте приложения')
        logging.error(f'app_start: {err}')


@dp.message(Command('hosting'))
async def server_cmd(message: types.Message):
    content = Text(
        as_list(
            BotCommand('/start_', 'web'),
            BotCommand('/start_', 'server'),
            BotCommand('/start_', 'files'),
            BotCommand('/start_', 'all'),
            BotCommand('/update_', 'web'),
            BotCommand('/update_', 'server'),
            BotCommand('/update_', 'files'),
            BotCommand('/update_', 'all'),
            BotCommand('/kill_', 'web'),
            BotCommand('/kill_', 'server'),
            BotCommand('/kill_', 'files'),
            BotCommand('/kill_', 'all'),
        )
    )
    await message.answer(**content.as_kwargs())


async def main():
    global bot, dp
    bot = Bot(config.bot_token.get_secret_value(), parse_mode=ParseMode.MARKDOWN_V2)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
