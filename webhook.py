import logging
from aiohttp import web
from pydantic import ValidationError

from func import handle_notification, get_vote_msg,get_reminder_msg,get_results_msg,get_answer_msg
from config_reader import config
from settings import routes, NewVoteStructure, VoteResultsStructure, VoteReminderStructure, DiscussionAnswerStructure


@web.middleware
async def auth(request: web.Request, handler: web.Callable):
    if request.headers.get('Authorization').replace('Bearer ', '') == config.tg_auth_token.get_secret_value():
        return await handler(request)
    else:
        return web.Response(status=401)


# WebHook for new votes
@routes.post('/votes/new')
async def new_vote(request: web.Request):
    try:
        data = NewVoteStructure.model_validate(await request.json())
        await handle_notification(data, get_vote_msg)
        return web.Response(status=200)
    except ValidationError as val_err:
        logging.error(f'new_vote: {val_err}')
        return web.Response(status=400, reason='Data validation error')
    except Exception as err:
        logging.error(f'new_vote: {err}')
        return web.Response(status=500)


# WebHook for vote results / vote end
@routes.post('/votes/results')
async def vote_results(request: web.Request):
    try:
        data = VoteResultsStructure.model_validate(await request.json())
        await handle_notification(data, get_results_msg)
        return web.Response(status=200)
    except ValidationError as val_err:
        logging.error(f'vote_results: {val_err}')
        return web.Response(status=400, reason='Data validation error')
    except Exception as err:
        logging.error(f'vote_results: {err}')
        return web.Response(status=500)


# WebHook for vote expiration
@routes.post('/votes/reminder')
async def vote_expire(request: web.Request):
    try:
        data = VoteReminderStructure.model_validate(await request.json())
        await handle_notification(data, get_reminder_msg)
        return web.Response(status=200)
    except ValidationError as val_err:
        logging.error(f'vote_expire: {val_err}')
        return web.Response(status=400, reason='Data validation error')
    except Exception as err:
        logging.error(f'vote_expire: {err}')
        return web.Response(status=500)


# WebHook for answer in discussion
@routes.post('/discussion/answer')
async def discussion_answer(request: web.Request):
    try:
        data = DiscussionAnswerStructure.model_validate(await request.json())
        await handle_notification(data, get_answer_msg)
        return web.Response(status=200)
    except ValidationError as val_err:
        logging.error(f'discussion_answer: {val_err}')
        return web.Response(status=400, reason='Data validation error')
    except Exception as err:
        logging.error(f'discussion_answer: {err}')
        return web.Response(status=500)


# Hello server response
@routes.get('/')
async def hello(request: web.Request):
    return web.Response(status=200, body='Telegram bot is running!')
