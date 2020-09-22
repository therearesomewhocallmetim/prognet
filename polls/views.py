from datetime import date, datetime
from functools import wraps

import aiohttp
import aiohttp_jinja2
from aiohttp import web
from aiohttp.web_ws import WebSocketResponse
from aiohttp_security import authorized_userid, check_authorized

from auth.policies import identity_from_token
from polls.models import Following, Post, Profile


def db(fn):
    @wraps(fn)
    async def wrapper(request, *args, **kwargs):
        async with request.app['db'].acquire() as conn:
            request['conn'] = conn
            res = await fn(request, *args, **kwargs)
            await conn.commit()
            return res
    return wrapper


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
        user_id = await login_required(request)
        my_profile = await Profile.get_by_user_id(conn, user_id)
        if not my_profile:
            raise web.HTTPFound('/profiles/me')
        profiles = await Profile.get_all_names(conn, my_profile['id'])
        followed = await followed_profiles(conn, my_profile['id'])
        for profile in profiles:
            profile['is_followed'] = profile['id'] in followed
    await request.app['queue'].send(f'{datetime.now().timestamp()}')

    return {
        'profiles': profiles,
        'my_profile': {
            'first_name': my_profile['first_name'], 'last_name': my_profile['last_name']}}


async def check_has_profile(user_id, conn):
    profile = await Profile.get_by_user_id(conn, user_id)
    if not profile:
        raise web.HTTPFound('/profiles/me')
    return profile['id']


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


@aiohttp_jinja2.template('index.html')
async def search_profiles(request):
    async with request.app['db'].acquire() as conn:
        params = dict(request.query)
        profiles = await Profile.search(conn, params)
        return {'profiles': profiles}


@aiohttp_jinja2.template('posts_form.html')
async def posts_form(request):
    user_id = await login_required(request)
    async with request.app['db'].acquire() as conn:
        await check_has_profile(user_id, conn)


async def posts_post(request):
    data = await request.post()
    user_id = await login_required(request)
    async with request.app['db'].acquire() as conn:
        profile = await Profile.get_by_user_id(conn, user_id)
        data = {'text': data['text'], 'author_id': profile['id'], }
        pk = await Post.save(conn, data)

        await conn.commit()
    await request.app['queue'].send(
        {
            'text': data['text'],
            'id': pk,
            'profile': {
                'id': profile['id'],
                'first_name': profile['first_name'],
                'last_name': profile['last_name']
            }
        })

    raise web.HTTPFound('/profiles/posts')


@aiohttp_jinja2.template('posts.html')
@db
async def list_posts(request):
    conn = request['conn']
    user_id = await login_required(request)
    if (profile_id_str := request.match_info.get('prof_id')) is not None:
        profile_id = int(profile_id_str)
    else:
        profile_id = await check_has_profile(user_id, conn)
    posts = await Post.get_by_author_id(conn, profile_id)
    return {'posts': posts, 'profile_id': profile_id}


@aiohttp_jinja2.template('post.html')
@db
async def get_post(request):
    conn = request['conn']
    post_id = request.match_info.get('post_id')
    post = await Post.get_by_id(conn, post_id)
    return {'post': post[0]}


@db
async def follow(request):
    conn = request['conn']
    my_profile_id, profile_to_follow = await _follow_params(request, conn)
    await Following.follow(conn, who=my_profile_id, whom=profile_to_follow)
    await conn.commit()
    raise web.HTTPFound(f'/profiles/posts/{profile_to_follow}')


@db
async def unfollow(request):
    conn = request['conn']
    my_profile_id, profile_to_follow = await _follow_params(request, conn)
    await Following.unfollow(conn, who=my_profile_id, whom=profile_to_follow)
    await conn.commit()
    raise web.HTTPFound(f'/profiles/posts/{profile_to_follow}')


async def _follow_params(request, conn):
    user_id = await login_required(request)
    my_profile_id = await check_has_profile(user_id, conn)
    profile_to_follow = int(request.match_info.get('prof_id'))
    return my_profile_id, profile_to_follow


@db
async def news_websocket_handler(request):
    ws = WebSocketResponse()
    await ws.prepare(request)
    profile_id = 0
    async for ws_msg in ws:
        if ws_msg.type == aiohttp.WSMsgType.TEXT:
            token = ws_msg.data
            identity = await identity_from_token(token)
            profile_id = await check_has_profile(identity, request['conn'])
        break

    queue = request.app['queue']
    async for msg in queue.receive():
        if msg['profile']['id'] in await followed_profiles(request['conn'], profile_id):
            name = f'{msg["profile"]["first_name"]} {msg["profile"]["last_name"]}'
            await ws.send_str(f'''
                <p>
                    <a href="/profiles/post/{msg["id"]}">{msg["text"][:50]}...</a> by
                    <a href="{msg["profile"]["id"]}">{name}</a></p>''')
    return ws


async def followed_profiles(conn, profile_id):
    followed = await Following.followed_by(conn, profile_id)
    return [x['follows'] for x in followed]


@db
@aiohttp_jinja2.template('message.html')
async def message(request):
    user_id = await login_required(request)
    profile = await Profile.get_by_user_id(request['conn'], user_id)
    if not profile:
        raise web.HTTPFound('/profiles/me')

    to = request.query
    to = to.get('to')
    to = await Profile.get_by_user_id(request['conn'], to)

    return {'my_profile': profile, 'to': to}
