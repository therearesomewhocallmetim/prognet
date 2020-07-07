import aiohttp_jinja2
from aiohttp import web
from aiohttp_security import authorized_userid, check_authorized

from . import db


@aiohttp_jinja2.template('index.html')
async def index(request):
    try:
        await check_authorized(request)
    except web.HTTPUnauthorized:
        raise web.HTTPFound('/login')
    user = await authorized_userid(request)
    async with request.app['db'].acquire() as conn:
        cursor = await conn.execute(db.question.select())
        records = await cursor.fetchall()
        questions = [dict(q) for q in records]

    return {'questions': questions}
