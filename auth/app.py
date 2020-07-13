from aiohttp import web

from .routes import setup_routes


def get_app(config):
    app = web.Application()
    app.name = 'auth'
    app['config'] = {}
    app['config'].update(config)
    setup_routes(app)
    return app
