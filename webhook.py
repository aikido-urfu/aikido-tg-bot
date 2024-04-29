from aiohttp import web
import func

routes = web.RouteTableDef()


# WebHook for new votes
@routes.post('/votes/new')
async def new_vote(request):
    data = await request.json()
    await func.handle_new_vote(data)
    return web.Response(status=200)


# WebHook for vote results / vote end
@routes.post('/votes/results')
async def vote_results(request):
    data = await request.json()
    pass
    return web.Response(status=200)


# WebHook for vote expiration
@routes.post('/votes/reminder')
async def vote_expire(request):
    data = await request.json()
    pass
    return web.Response(status=200)


# WebHook for answer in discussion
@routes.post('/discussion/answer')
async def discussion_answer(request):
    data = await request.json()
    pass
    return web.Response(status=200)
