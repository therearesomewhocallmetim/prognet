from pathlib import Path

from aiohttp import web

from .routes import setup_routes


def get_app(config):
    parent = Path(__file__).parent
    app = web.Application()
    app['config'] = {}
    app.name = parent.name
    config['template_dirs'].append(parent / 'templates')
    app['config'].update(config)
    setup_routes(app)
    return app
