import aiohttp_jinja2
from aiohttp import web
from aiohttp_security import authorized_userid, check_authorized

from utils import select


async def login_required(request):
    try:
        await check_authorized(request)
    except web.HTTPUnauthorized:
        raise web.HTTPFound('/login')
    user_id = await authorized_userid(request)
    return user_id


@aiohttp_jinja2.template('index.html')
async def index(request):
    async with request.app['db'].acquire() as conn:
        user_id = await login_required(request)
        await check_has_profile(user_id, conn)

        q = "SELECT login FROM users;"

        users = await select(conn, q)
        return {'users': users}


async def check_has_profile(user_id, conn):
    user = await select(conn, "SELECT * FROM profiles WHERE user_id=%s", int(user_id))
    if not user:
        raise web.HTTPFound('/profile')


@aiohttp_jinja2.template('profile_form.html')
async def profile_get(request):
    pass


async def profile_post(request):
    data = await request.post()
    user_id = await login_required(request)
    statement = """
        INSERT INTO profiles 
            (user_id, first_name, last_name, sex, interests, city) 
        values 
            (%(user_id)s, %(first_name)s, %(last_name)s, %(sex)s, %(interests)s, %(city)s)
        ON DUPLICATE KEY UPDATE
            user_id=%(user_id)s, first_name=%(first_name)s, last_name=%(last_name)s,
            sex=%(sex)s, interests=%(interests)s, city=%(city)s;
        """
    async with request.app['db'].acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                statement, args=dict(
                    user_id=user_id, first_name=data['first_name'],
                    last_name=data['last_name'], sex=data['gender'],
                    interests=data['interests'], city=data['city']))
            await conn.commit()

    raise web.HTTPFound('/')
