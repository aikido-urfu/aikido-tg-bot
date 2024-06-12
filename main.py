import logs
import asyncio
import logging
import settings as st
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from config_reader import config
from settings import dp, cmd_router, commands
from func import results_notifier, expiring_notifier
from utils import repeat, load_notif_settings
import webhook
import handlers


async def webhook_setup():
    app = web.Application()
    app.add_routes(webhook.routes)
    app.middlewares.append(webhook.auth)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, config.base_host.get_secret_value(), 3007)
    return site


# 10800 - 3h
async def periodic_task_setup():
    asyncio.create_task(repeat(10800, results_notifier))
    asyncio.create_task(repeat(21600, expiring_notifier))


async def setup_bot_commands():
    result: bool = await st.bot.set_my_commands(commands)
    if not result:
        logging.error(f'setup_bot_commands is not succeeded')


async def main():
    st.bot = Bot(config.bot_token.get_secret_value(), parse_mode=ParseMode.MARKDOWN_V2)
    site = await webhook_setup()
    dp.include_router(cmd_router)

    load_notif_settings()
    await setup_bot_commands()
    await site.start()
    await periodic_task_setup()
    await dp.start_polling(st.bot)


if __name__ == '__main__':
    asyncio.run(main())
