from aiohttp import web

from polls.routes import setup_routes



def get_app(config):
    polls = web.Application()
    polls.name = 'polls'
    polls['config'] = {}
    polls['config'].update(config)
    setup_routes(polls)
    return polls
