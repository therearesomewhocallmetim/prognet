from datetime import date, datetime

import aiohttp_jinja2
from aiohttp import web
from aiohttp_security import authorized_userid, check_authorized

from polls.models import Profile


async def login_required(request):
    try:
        await check_authorized(request)
    except web.HTTPUnauthorized:
        raise web.HTTPFound('/auth/login')
    user_id = await authorized_userid(request)
    return user_id


@aiohttp_jinja2.template('index.html')
async def index(request):
    async with request.app['db'].acquire() as conn:
        # user_id = await login_required(request)
        # await check_has_profile(user_id, conn)
        profiles = await Profile.get_all_names(conn)
        return {'profiles': profiles}


async def check_has_profile(user_id, conn):
    profile = await Profile.get_by_user_id(conn, user_id)
    if not profile:
        raise web.HTTPFound('/profiles/me')


@aiohttp_jinja2.template('profile_form.html')
async def profile_get(request):
    async with request.app['db'].acquire() as conn:
        user_id = await login_required(request)
        profile = await Profile.get_by_user_id(conn, user_id)
        if profile:
            return {'profile': profile}
        return {'profile': None}


async def profile_post(request):
    data = await request.post()
    user_id = await login_required(request)
    data = dict(data.items())
    try:
        data['birth'] = datetime.strptime(data['birth'], '%Y-%m-%d').date()
    except ValueError:
        data['birth'] = None

    data['user_id'] = user_id
    async with request.app['db'].acquire() as conn:
        await Profile.save(conn, data)
        await conn.commit()
    raise web.HTTPFound('/profiles/')


@aiohttp_jinja2.template('profile_detail.html')
async def profile_detail(request):
    try:
        user_id = int(request.match_info['user_id'])
        async with request.app['db'].acquire() as conn:
            profile = await Profile.get_by_user_id(conn, user_id)
            if not profile:
                raise web.HTTPNotFound()
            if profile['date_of_birth']:
                age = (date.today() - profile['date_of_birth']).days // 365
                profile['age'] = age
            return {'profile': profile}

    except ValueError:
        raise web.HTTPNotFound()
