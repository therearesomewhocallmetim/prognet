import asyncio
from importlib import import_module

import aiohttp_jinja2
import click
import jinja2
from aiohttp import web
from aiohttp_security import SessionIdentityPolicy
from aiohttp_security import setup as setup_security
from aiohttp_session import SimpleCookieStorage, session_middleware

from _root import init_db
from _root.db import close_mysql, close_queue, init_mysql, init_queue
from _root.settings import get_real_config
from auth.policies import SimpleAuthPolicy
from fake_data.gen import generate


# thing
def plugin_app(app, prefix, nested):
    async def set_db(a):
        nested['db'] = a['db']
        nested['queue'] = a['queue']
    app.on_startup.append(set_db)
    app.add_subapp(prefix, nested)
# / end of thing


plugins = [
    ('auth', '/auth/'),
    ('polls', '/profiles/')
]


def load_plugins(root):
    for application_name, prefix in plugins:
        application_module = import_module(f'{application_name}.app')
        application = application_module.get_app(root['config'])
        plugin_app(root, prefix, application)


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
    app.on_startup.append(init_queue)

    app.on_cleanup.append(close_mysql)
    app.on_cleanup.append(close_queue)

    load_plugins(app)

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
@click.pass_context
def generate_fake_data(ctx):
    app = ctx.obj['APP']
    loop = asyncio.get_event_loop()
    loop.run_until_complete(generate(app))


@cli.command()
@click.option('--port', type=click.INT, default=3000)
@click.pass_context
def run(ctx, port):
    web.run_app(ctx.obj['APP'], port=port)


if __name__ == "__main__":
    cli()
