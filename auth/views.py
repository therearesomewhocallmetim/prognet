import hashlib

import aiohttp_jinja2
from aiohttp import web
from aiohttp_security import (
    authorized_userid, check_authorized, forget, remember)
from pymysql import IntegrityError

from utils import select


async def check_unauthed(request):
    try:
        await check_authorized(request)
        raise web.HTTPFound('/')
    except web.HTTPUnauthorized:
        pass


async def login_post(request):
    async with request.app['db'].acquire() as conn:
        await check_unauthed(request)
        data = await request.post()
        login = data['login']
        password = hashlib.sha3_256(data['password'].encode()).hexdigest()
        statement = f"""SELECT id from users where login='{login}' and password='{password}';"""
        records = await select(conn, statement)
        if records:
            redirect_response = web.HTTPFound('/')
            await remember(request, redirect_response, str(records[0]['id']))
        redirect_response = web.HTTPFound('/login')
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


async def register(request):
    await check_unauthed(request)
    data = await request.post()
    login = data['login']
    password = data['password']
    password2 = data['password2']
    if password != password2:
        raise web.HTTPFound('/login')
    password = hashlib.sha3_256(password.encode()).hexdigest()

    statement = f"""INSERT INTO users (login, password) values (%s, %s);"""
    async with request.app['db'].acquire() as conn:
        async with conn.cursor() as cur:
            try:
                await cur.execute(statement, (login, password))
                await cur.execute('SELECT LAST_INSERT_ID();')
                last_id = (await cur.fetchone())[0]
                await conn.commit()
                redirect_response = web.HTTPFound('/')
                await remember(request, redirect_response, str(last_id))
                raise redirect_response
            except IntegrityError:
                raise web.HTTPFound('/login')
