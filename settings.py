import pydantic
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
    title: str = Field(...)
    tgUserIds: list[int]

    class Config:
        extra = 'allow'


class NewVoteStructure(VoteRoot):
    startDate: str
    endDate: str


class DiscussionAnswerStructure(VoteRoot):
    message: str = None
    messageAuthor: str = None
    messageDate: str = None


class VoteReminderStructure(BaseModel):
    _EXT_VoteRoot = pydantic.create_model('_EXT_Vote_model', endDate=(str, ...), __base__=VoteRoot, )
    votes: list[_EXT_VoteRoot]


class VoteResultsStructure(BaseModel):
    votes: list[VoteRoot]


class UserStartStructure(BaseModel):
    token: str
    telegramUserID: str = None
