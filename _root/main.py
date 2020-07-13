import sys

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp_security import SessionIdentityPolicy
from aiohttp_security import setup as setup_security
from aiohttp_session import SimpleCookieStorage, session_middleware

from auth import app as auth
from auth.policies import SimpleAuthPolicy
from polls import app as polls
from _root.db import close_mysql, init_mysql
from _root.settings import get_real_config

# thing
def plugin_app(app, prefix, nested):
    async def set_db(a):
        nested['db'] = a['db']
    app.on_startup.append(set_db)
    app.add_subapp(prefix, nested)
# / end of thing


config_files = sys.argv[1:]

middleware = session_middleware(SimpleCookieStorage())

app = web.Application(middlewares=[middleware])
app.name = 'main'

app['config'] = get_real_config('polls.yaml', *config_files)
app.on_startup.append(init_mysql)
app.on_cleanup.append(close_mysql)


plugin_app(app, '/profiles/', polls.get_app(app['config']))
plugin_app(app, '/auth/', auth.get_app(app['config']))

aiohttp_jinja2.setup(
    app, loader=jinja2.FileSystemLoader(map(str, app['config']['template_dirs'])))


# security
policy = SessionIdentityPolicy()
setup_security(app, policy, SimpleAuthPolicy())

web.run_app(app, port=3000)
