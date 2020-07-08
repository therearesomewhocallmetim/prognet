import aiohttp_jinja2
from aiohttp import web
from aiohttp_security import authorized_userid, check_authorized

from utils import select


@aiohttp_jinja2.template('index.html')
async def index(request):
    try:
        await check_authorized(request)
    except web.HTTPUnauthorized:
        raise web.HTTPFound('/login')
    user = await authorized_userid(request)

    q = "SELECT login FROM users;"

    async with request.app['db'].acquire() as conn:
        users = await select(conn, q)
    return {'users': users}
