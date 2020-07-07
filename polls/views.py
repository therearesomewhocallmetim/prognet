import hashlib
import logging

import aiohttp_jinja2
from aiohttp import web
from aiohttp_security import authorized_userid, check_authorized, remember
from sqlalchemy import text

from . import db


@aiohttp_jinja2.template('index.html')
async def index(request):
    await check_authorized(request)
    user = await authorized_userid(request)
    async with request.app['db'].acquire() as conn:
        cursor = await conn.execute(db.question.select())
        records = await cursor.fetchall()
        questions = [dict(q) for q in records]

    return {'questions': questions}


async def login_post(request):
    async with request.app['db'].acquire() as conn:
        data = await request.post()
        login = data['login']
        password = hashlib.sha3_256(data['password'].encode()).hexdigest()
        statement = text(
            """SELECT * from users where login=:login and password=:password;""")
        cursor = await conn.execute(statement, login=login, password=password)
        records = [dict(u) for u in await cursor.fetchall()]
        logging.error(f'user: {records}')
        redirect_response = web.HTTPFound('/')
        await remember(request, redirect_response, records[0]['login'])
        raise redirect_response


@aiohttp_jinja2.template('login.html')
async def login_get(request):
    return {}