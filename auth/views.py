import hashlib

import aiohttp_jinja2
from aiohttp import web
from aiohttp_security import (
    authorized_userid, check_authorized, forget, remember)

from utils import select


async def login_post(request):
    async with request.app['db'].acquire() as conn:
        try:
            await check_authorized(request)
            raise web.HTTPFound('/')
        except web.HTTPUnauthorized:
            pass

        data = await request.post()
        login = data['login']
        password = hashlib.sha3_256(data['password'].encode()).hexdigest()
        statement = f"""SELECT login from users where login='{login}' and password='{password}';"""
        records = await select(conn, statement)
        redirect_response = web.HTTPFound('/')
        await remember(request, redirect_response, records[0]['login'])
        raise redirect_response


@aiohttp_jinja2.template('login.html')
async def login_get(request):
    try:
        await check_authorized(request)
        raise web.HTTPFound('/')
    except web.HTTPUnauthorized:
        return {}


async def logout(request):
    user = await authorized_userid(request)
    await forget(request, user)
    raise web.HTTPFound('/')
