import logging

from aiohttp import web
import func
from config_reader import config

routes = web.RouteTableDef()


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
        data = await request.json()
        await func.handle_new_vote(data)
        return web.Response(status=200)
    except Exception as err:
        logging.error(f'new_vote: {err}')
        return web.Response(status=500)


# WebHook for vote results / vote end
@routes.post('/votes/results')
async def vote_results(request: web.Request):
    data = await request.json()
    pass
    return web.Response(status=200)


# WebHook for vote expiration
@routes.post('/votes/reminder')
async def vote_expire(request: web.Request):
    data = await request.json()
    pass
    return web.Response(status=200)


# WebHook for answer in discussion
@routes.post('/discussion/answer')
async def discussion_answer(request: web.Request):
    data = await request.json()
    pass
    return web.Response(status=200)
