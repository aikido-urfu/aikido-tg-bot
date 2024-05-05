import asyncio
import signal
import sys
import logging
import psutil
import settings as st
from config_reader import config
from aiogram.utils.formatting import Text
from settings import dp


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


# DEBUG
async def send_msg(msg: str):
    await st.bot.send_message(int(config.debug_chat_id.get_secret_value()), **Text(msg).as_kwargs())


async def handle_new_vote(data):
    await send_msg(data)
