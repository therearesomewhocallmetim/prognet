import asyncio

import aiohttp_jinja2
import click
import jinja2
from aiohttp import web
from aiohttp_security import SessionIdentityPolicy
from aiohttp_security import setup as setup_security
from aiohttp_session import SimpleCookieStorage, session_middleware

from _root import init_db
from _root.db import close_mysql, init_mysql
from _root.settings import get_real_config
from auth import app as auth
from auth.policies import SimpleAuthPolicy
from polls import app as polls


# thing
def plugin_app(app, prefix, nested):
    async def set_db(a):
        nested['db'] = a['db']
    app.on_startup.append(set_db)
    app.add_subapp(prefix, nested)
# / end of thing


@click.group()
@click.option('--config')
@click.pass_context
def cli(ctx, config):
    ctx.ensure_object(dict)
    middleware = session_middleware(SimpleCookieStorage())

    app = web.Application(middlewares=[middleware])
    app.name = 'main'

    app['config'] = get_real_config('polls.yaml', config)
    app.on_startup.append(init_mysql)
    app.on_cleanup.append(close_mysql)


    plugin_app(app, '/profiles/', polls.get_app(app['config']))
    plugin_app(app, '/auth/', auth.get_app(app['config']))

    aiohttp_jinja2.setup(
        app, loader=jinja2.FileSystemLoader(map(str, app['config']['template_dirs'])))


    # security
    policy = SessionIdentityPolicy()
    setup_security(app, policy, SimpleAuthPolicy())

    ctx.obj['APP'] = app


@cli.command()
@click.pass_context
def create_db(ctx):
    app = ctx.obj['APP']
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db.main(app))


@cli.command()
@click.option('--port', type=click.INT, default=3000)
@click.pass_context
def run(ctx, port):
    web.run_app(ctx.obj['APP'], port=port)


if __name__ == "__main__":
    cli()
