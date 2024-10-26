import pydantic
from enum import Enum
from aiogram import Bot, Dispatcher, Router
from aiogram.types import BotCommand
from src.config_reader import config
from aiohttp import web
from pydantic import BaseModel, Field


class NotificationSettingsRoot(BaseModel):
    newVote: bool = True
    expiringVotes: bool = True
    expiredVotes: bool = True
    discussAnswer: bool = True


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


class UserVoteStructure(BaseModel):
    voteId: int = Field(..., alias='id')
    title: str = Field(...)
    startDate: str
    endDate: str
    isVoted: bool
    isExpired: bool


class UserVotesStructure(BaseModel):
    votes: list[UserVoteStructure]


class NotificationType(Enum):
    NEW_VOTE = 'newVote'
    EXPIRING_VOTE = 'expiringVotes'
    EXPIRED_VOTE = 'expiredVotes'
    DISCUSS_ANSWER = 'discussAnswer'


upd_type = {
    'web': 'aikido-web-core',
    'server': 'aikido-server-core',
    'files': 'aikido-server-files',
}

commands: list[BotCommand] = [
    BotCommand(command='votes', description='Список голосований'),
    BotCommand(command='unsubscribe', description='Отписаться от уведомлений'),
    BotCommand(command='settings', description='Изменить настройки уведомлений'),
    BotCommand(command='hosting', description='Рестарт/стоп приложений на хосте'),
    BotCommand(command='privacy', description='Политика конфиденциальности')
]

dp: Dispatcher = Dispatcher()
cmd_router: Router = Router()
bot: Bot
url = config.server_url.get_secret_value()
routes = web.RouteTableDef()
notif_settings: dict[int, NotificationSettingsRoot] = {0: NotificationSettingsRoot()}
bell_on, bell_off = '🔔', '🔕'
