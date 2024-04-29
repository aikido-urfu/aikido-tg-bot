from aiogram import Bot, Dispatcher, Router
from config_reader import config

dp: Dispatcher = Dispatcher()
cmd_router: Router = Router()
bot: Bot
url = config.api_url.get_secret_value()
