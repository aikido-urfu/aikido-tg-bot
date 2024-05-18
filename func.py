import asyncio
from datetime import datetime
import logging
from collections.abc import Callable

import psutil
import requests

import settings as st
from aiogram.utils.formatting import Text, Bold, Italic, TextLink
from settings import dp, NewVoteStructure, VoteResultsStructure, VoteReminderStructure, DiscussionAnswerStructure, VoteRoot, UserStartStructure
from utils import parse_date


# DEBUG int(config.debug_chat_id.get_secret_value())
async def send_msg(user_id: int, content: Text):
    await st.bot.send_message(user_id, **content.as_kwargs())


def get_vote_msg(vote: NewVoteStructure) -> Text:
    try:
        start_date = parse_date(vote.startDate)
        end_date = parse_date(vote.endDate)
        date_format: str = "%H:%M, %d.%m.%Y"
        link = 'http://aikido.sytes.net/vote'

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


async def link_telegram(user: UserStartStructure):
    try:
        res = requests.post(f"{st.url}telegram/start", json=user.model_dump())
        return res
    except Exception as err:
        error = Exception(f'link_telegram: {err}')
        logging.error(error)
        raise error


async def unlink_telegram(tgUserId: int):
    try:
        res = requests.delete(f"{st.url}telegram/unsubscribe", json={'telegramUserID': str(tgUserId)})
        return res
    except Exception as err:
        error = Exception(f'unlink_telegram: {err}')
        logging.error(error)
        raise error


# TODO: Последовательная рассылка для упреждения ограничений телеграм
async def handle_notification(data: VoteRoot, send_func: Callable[[VoteRoot.__subclasses__()], Text]):
    for user in data.tgUserIds:
        content = send_func(data)
        await send_msg(user, content)


# Check every 12 hours
async def get_expiring_votes(period: int):
    try:
        res = requests.get(f"{st.url}telegram/expiringVotes", params={'period': period})
        return res
    except Exception as err:
        error = Exception(f'get_expiring_votes: {err}')
        logging.error(error)
        raise error


async def get_expired_votes(period: int):
    try:
        res = requests.get(f"{st.url}telegram/expiredVotes", params={'period': period})
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
            await handle_notification(vote, get_results_msg)
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
            await handle_notification(vote, get_reminder_msg)
        logging.info(f'expiring_notifier: {len(expiring_votes.votes)} votes will end soon')
    except Exception as err:
        logging.error(err)
