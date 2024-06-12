import logging
import re
import subprocess
import requests
import asyncio

import settings as st
from aiogram import types, F
from aiogram.filters.command import Command, CommandObject, CommandStart
from aiogram.utils.formatting import Text, Bold, TextLink, Italic, as_list, BotCommand
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from datetime import datetime
from pathlib import Path

from settings import cmd_router, dp, UserStartStructure, upd_type
from config_reader import config
from func import link_telegram, unlink_telegram, get_settings_inline_kb
from utils import restart_task, kill_task, save_notif_settings


# /start handler
@cmd_router.message(CommandStart(deep_link=True))
async def start(message: types.Message, command: CommandObject):
    command_args: str = command.args
    try:
        user = UserStartStructure(token=command_args, telegramUserID=str(message.chat.id))
        res = await link_telegram(user)

        if res.ok:
            await message.answer('Вы подписаны на уведомления')
        elif res.status_code == 409:
            await message.answer('Вы уже подписаны на уведомления')
        else:
            raise Exception("Internal error")
    except:
        await message.answer('Произошла ошибка при подписке на уведомления')
        return


# /votes handler
@cmd_router.message(Command('votes'))
async def votes(message: types.Message):
    try:
        res = requests.get(st.url + 'votes', data={'tgid': message.chat.id})
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


@cmd_router.callback_query(F.data == "not_unsubscribe")
async def not_unsubscribe(callback: types.CallbackQuery):
    await callback.message.edit_text(**Text('Вы не будете отписаны.').as_kwargs())
    await callback.answer()


@cmd_router.callback_query(F.data == "unsubscribe")
async def unsubscribe(callback: types.CallbackQuery):
    try:
        res = await unlink_telegram(callback.from_user.id)

        answer: Text
        if res.ok:
            answer = Text('Вы отписаны от уведомлений')
        elif res.status_code == 409:
            answer = Text('Вы не были подписаны на уведомления')
        else:
            raise Exception("Internal error")
        await callback.message.edit_text(**answer.as_kwargs())
        await callback.answer()
    except:
        await callback.message.answer(
            **Text('Произошла ошибка при отписке от уведомлений.\nПопробуйте позже.').as_kwargs())
        await callback.answer()


# /unsubscribe handler
@cmd_router.message(Command('unsubscribe'))
async def unsubscribe_handler(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Да",
            callback_data="unsubscribe"),
        InlineKeyboardButton(
            text="Нет",
            callback_data="not_unsubscribe")
    )
    await message.answer(
        'Вы уверены, что хотите отписаться?',
        reply_markup=builder.as_markup(),
    )


@cmd_router.callback_query(F.data.startswith('settings_inline_'))
async def settings_inline(callback: types.CallbackQuery):
    try:
        setting = callback.data.replace('settings_inline_', '')

        if setting == 'close':
            await callback.message.edit_text(**Text('Настройки уведомлений сохранены').as_kwargs())
            await callback.answer()
            return

        settings = st.notif_settings.get(callback.from_user.id, st.notif_settings[0])
        cur_setting: bool | None = getattr(settings, setting, None)
        if cur_setting is None:
            raise Exception(f'Setting with name {setting} not found')

        setattr(settings, setting, not cur_setting)
        st.notif_settings[callback.from_user.id] = settings
        save_notif_settings()

        builder = await get_settings_inline_kb(settings)

        await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
        await callback.answer()
    except Exception as err:
        logging.error(f'settings_inline: {err}')
        await callback.message.answer(**Text('Произошла ошибка при изменении настроек.').as_kwargs())
        await callback.answer()


# /settings
@cmd_router.message(Command('settings'))
async def settings_handler(message: types.Message):
    try:
        settings = st.notif_settings.get(message.from_user.id, st.notif_settings[0])
        builder = await get_settings_inline_kb(settings)

        await message.answer('Выберите уведомления, которые хотите получать', reply_markup=builder.as_markup())
    except Exception as err:
        await message.answer('Произошла непредвиденная ошибка')
        logging.error(f'settings_handler: {err}')


# @dp.message(Command('kill'))
@cmd_router.message(Command(re.compile(r'^kill_(web|server|files|all)$')))
async def kill(message: types.Message, command: CommandObject):
    try:
        if str(message.from_user.id) != config.debug_chat_id.get_secret_value():
            await message.answer(**Text('Unauthorized').as_kwargs())

        picked_upd_type = message.text.replace('/kill_', '')

        if picked_upd_type == 'all':
            for app in upd_type.values():
                kill_task(app)
        else:
            kill_task(upd_type[picked_upd_type])

        await message.answer(f'Процесс {picked_upd_type} завершен')
    except Exception as err:
        await message.answer('Произошла ошибка во время завершения процесса')
        logging.error(f'app_kill: {err}')


@cmd_router.message(Command(re.compile(r'^restart_(web|server|files|all)$')))
async def restart(message: types.Message):
    try:
        if str(message.from_user.id) != config.debug_chat_id.get_secret_value():
            await message.answer(**Text('Unauthorized').as_kwargs())

        picked_upd_type = message.text.replace('/restart_', '')

        if picked_upd_type == 'all':
            for app in upd_type.values():
                restart_task(app)
        else:
            restart_task(upd_type[picked_upd_type])

        await message.answer(f'{picked_upd_type} успешно запущен')
    except Exception as err:
        await message.answer('Произошла ошибка при рестарте приложения')
        logging.error(f'app_restart: {err}')


@cmd_router.message(Command('hosting'))
async def server_cmd(message: types.Message):
    content = Text(
        as_list(
            BotCommand('/restart_', 'web'),
            BotCommand('/restart_', 'server'),
            BotCommand('/restart_', 'files'),
            BotCommand('/restart_', 'all'),
            BotCommand('/kill_', 'web'),
            BotCommand('/kill_', 'server'),
            BotCommand('/kill_', 'files'),
            BotCommand('/kill_', 'all'),
        )
    )
    await message.answer(**content.as_kwargs())
