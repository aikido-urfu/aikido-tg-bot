from aiogram import Bot, Dispatcher, Router
from config_reader import config
from aiohttp import web
from pydantic import BaseModel, Field
from typing import Optional

dp: Dispatcher = Dispatcher()
cmd_router: Router = Router()
bot: Bot
url = config.server_url.get_secret_value()
routes = web.RouteTableDef()


class VoteRoot(BaseModel):
    voteId: int = Field(..., alias='id')
    title: str = Field(..., serialization_alias='voteName', description='Vote name')
    tgUserIds: list[int]

    class Config:
        extra = 'allow'


class NewVoteStructure(VoteRoot):
    startDate: str
    endDate: str


class DiscussionAnswerStructure(VoteRoot):
    messageAuthor: str
    message: str
    messageDate: str


class VoteReminderStructure(VoteRoot):
    endDate: str


class VoteResultsStructure(VoteRoot):
    results: None


class UserStartStructure(BaseModel):
    token: str
    telegramUserID: str = None
