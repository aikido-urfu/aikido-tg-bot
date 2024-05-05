import logs
import asyncio
import settings as st
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from config_reader import config
from settings import dp, cmd_router
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


async def main():
    st.bot = Bot(config.bot_token.get_secret_value(), parse_mode=ParseMode.MARKDOWN_V2)
    site = await webhook_setup()
    dp.include_router(cmd_router)

    await site.start()
    await dp.start_polling(st.bot)


if __name__ == '__main__':
    asyncio.run(main())
