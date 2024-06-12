import asyncio
import logging
import psutil
import requests
import settings as st
from datetime import datetime
from collections.abc import Callable
from aiogram.utils.formatting import Text, Bold, Italic, TextLink
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from settings import dp, NewVoteStructure, VoteResultsStructure, VoteReminderStructure, DiscussionAnswerStructure, \
    VoteRoot, UserStartStructure, NotificationSettingsRoot, NotificationType
from utils import parse_date
from config_reader import config


def get_bell_icon(state: bool) -> str:
    return st.bell_on if state else st.bell_off


# DEBUG int(config.debug_chat_id.get_secret_value())
async def send_msg(user_id: int, content: Text):
    await st.bot.send_message(user_id, **content.as_kwargs())


async def get_settings_inline_kb(settings: NotificationSettingsRoot):
    builder = InlineKeyboardBuilder()
    builder.max_width = 1
    builder.adjust()
    builder.add(
        InlineKeyboardButton(
            text=f"{get_bell_icon(settings.newVote)} Новые голосования",
            callback_data="settings_inline_newVote"),
        InlineKeyboardButton(
            text=f"{get_bell_icon(settings.expiringVotes)} Истекающие голосования",
            callback_data="settings_inline_expiringVotes"),
        InlineKeyboardButton(
            text=f"{get_bell_icon(settings.expiredVotes)} Истёкшие голосования",
            callback_data="settings_inline_expiredVotes"),
        InlineKeyboardButton(
            text=f"{get_bell_icon(settings.discussAnswer)} Ответы в обсуждениях",
            callback_data="settings_inline_discussAnswer"),
        InlineKeyboardButton(
            text="Закрыть",
            callback_data="settings_inline_close"))
    return builder


def get_vote_msg(vote: NewVoteStructure) -> Text:
    try:
        start_date = parse_date(vote.startDate)
        end_date = parse_date(vote.endDate)
        date_format: str = "%H:%M, %d.%m.%Y"
        link = f'http://aikido.sytes.net/vote/{vote.voteId}'

        content = Text(
            '🗳 ', Bold(f'Голосование: {vote.title}'), '\n',
            Italic('Сроки голосования: '), start_date.strftime(date_format), ' - ',
            end_date.strftime(date_format), '\n\n',
            TextLink('🔗 Перейти к голосованию', url=link)
        )
        return content
    except Exception as err:
        error = Exception(f'get_vote_msg: {err}')
        logging.error(error)
        raise error


def get_results_msg(vote: VoteResultsStructure) -> Text:
    try:
        link = f'http://aikido.sytes.net/vote/{vote.voteId}/results'

        content = Text(
            '🗳 ', Bold(f'Голосование: {vote.title} завершилось'), '\n',
            TextLink('🔗 Посмотреть результаты', url=link)
        )
        return content
    except Exception as err:
        error = Exception(f'get_results_msg: {err}')
        logging.error(error)
        raise error


def get_reminder_msg(vote: VoteRoot.__subclasses__()) -> Text:
    try:
        date_format: str = "%H:%M, %d.%m.%Y"
        end_date: datetime = parse_date(vote.endDate)
        link = f'http://aikido.sytes.net/vote/{vote.voteId}'

        content = Text(
            '🗳 ', Bold(f'Голосование {vote.title} скоро закончится!'), '\n',
            '⌛️ Успейте проголосовать до ', end_date.strftime(date_format), '\n',
            TextLink('🔗 Перейти к голосованию', url=link)
        )
        return content
    except Exception as err:
        error = Exception(f'get_reminder_msg: {err}')
        logging.error(error)
        raise error


def get_answer_msg(discussion: DiscussionAnswerStructure) -> Text:
    try:
        link = f'http://aikido.sytes.net/vote/{discussion.voteId}/discussion'

        content = Text(
            '🗳 ', Bold(f'Вам ответили в обсуждении: {discussion.title}'), '\n',
            TextLink('🔗 Посмотреть ответ', url=link)
        )
        return content
    except Exception as err:
        error = Exception(f'get_answer_msg: {err}')
        logging.error(error)
        raise error


async def link_telegram(user: UserStartStructure):
    try:
        header = {"Authorization": f'Bearer {config.server_auth_token.get_secret_value()}'}
        res = requests.post(f"{st.url}telegram/start", json=user.model_dump(), headers=header)
        return res
    except Exception as err:
        error = Exception(f'link_telegram: {err}')
        logging.error(error)
        raise error


async def unlink_telegram(tgUserId: int):
    try:
        header = {"Authorization": f'Bearer {config.server_auth_token.get_secret_value()}'}
        res = requests.delete(f"{st.url}telegram/unsubscribe", json={'telegramUserID': str(tgUserId)}, headers=header)
        return res
    except Exception as err:
        error = Exception(f'unlink_telegram: {err}')
        logging.error(error)
        raise error


# TODO: Последовательная рассылка для упреждения ограничений телеграм
async def handle_notification(notif_type: NotificationType, data: VoteRoot,
                              send_func: Callable[[VoteRoot.__subclasses__()], Text]):
    for user in data.tgUserIds:
        settings = st.notif_settings.get(user, st.notif_settings[0])
        if getattr(settings, notif_type.value, True):
            content = send_func(data)
            await send_msg(user, content)


# Check every 12 hours
async def get_expiring_votes(period: int):
    try:
        header = {"Authorization": f'Bearer {config.server_auth_token.get_secret_value()}'}
        res = requests.get(f"{st.url}telegram/expiringVotes", params={'period': period}, headers=header)
        return res
    except Exception as err:
        error = Exception(f'get_expiring_votes: {err}')
        logging.error(error)
        raise error


async def get_expired_votes(period: int):
    try:
        header = {"Authorization": f'Bearer {config.server_auth_token.get_secret_value()}'}
        res = requests.get(f"{st.url}telegram/expiredVotes", params={'period': period}, headers=header)
        return res
    except Exception as err:
        error = Exception(f'get_expired_votes: {err}')
        logging.error(error)
        raise error


async def results_notifier():
    try:
        logging.info(f'results_notifier: called')
        period = 10800
        res = await get_expired_votes(period)

        if not res.ok:
            raise Exception

        data = res.json()
        expired_votes = VoteResultsStructure.model_validate(data)
        pass
        for vote in expired_votes.votes:
            await handle_notification(NotificationType.EXPIRED_VOTE, vote, get_results_msg)
        logging.info(f'results_notifier: {len(expired_votes.votes)} votes ended')
    except Exception as err:
        logging.error(err)


async def expiring_notifier():
    try:
        logging.info(f'expiring_notifier: called')
        period = 21600
        res = await get_expiring_votes(period)

        if not res.ok:
            raise Exception

        data = res.json()
        expiring_votes = VoteReminderStructure.model_validate(data)
        pass
        for vote in expiring_votes.votes:
            await handle_notification(NotificationType.EXPIRING_VOTE, vote, get_reminder_msg)
        logging.info(f'expiring_notifier: {len(expiring_votes.votes)} votes will end soon')
    except Exception as err:
        logging.error(err)
