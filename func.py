import asyncio
from datetime import datetime
import logging
import psutil
import settings as st
from config_reader import config
from aiogram.utils.formatting import Text, Bold, Italic, TextLink
from settings import dp


# DEBUG int(config.debug_chat_id.get_secret_value())
async def send_msg(user_id: int, content: Text):
    await st.bot.send_message(user_id, **content.as_kwargs())


async def send_vote(user_id: int, vote: dict):
    try:
        vote_name: str = vote['voteName']
        start_date: datetime = datetime.strptime(vote['voteStartDate'], "%Y-%m-%dT%H:%M:%S.%f%z")
        end_date: datetime = datetime.strptime(vote['voteEndDate'], "%Y-%m-%dT%H:%M:%S.%f%z")
        # link: str = vote['url']
        date_format: str = "%H:%M, %d.%m.%Y"
        link = 'http://aikido.sytes.net/vote'

        content = Text(
            '🗳 ', Bold(f'Голосование: {vote_name}'), '\n',
            Italic('Сроки голосования: '), start_date.strftime(date_format), ' - ',
            end_date.strftime(date_format), '\n\n',
            TextLink('🔗 Перейти к голосованию', url=link)
        )
        await send_msg(int(user_id), content)
    except Exception as err:
        error = Exception(f'send_vote: {err}')
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


async def handle_new_vote(data):
    for user in data['userIds']:
        await send_vote(user, data)
