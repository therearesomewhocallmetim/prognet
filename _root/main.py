import sys

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp_security import SessionIdentityPolicy
from aiohttp_security import setup as setup_security
from aiohttp_session import SimpleCookieStorage, session_middleware

from auth.policies import SimpleAuthPolicy
from polls import app as polls
from polls.db import close_mysql, init_mysql
from polls.settings import BASE_DIR, get_real_config

# thing
def plugin_app(app, prefix, nested):
    async def set_db(a):
        print(a.name)
        nested['db'] = a['db']

    app.on_startup.append(set_db)
    app.add_subapp(prefix, nested)

# / end of thing


config_files = sys.argv[1:]

middleware = session_middleware(SimpleCookieStorage())

app = web.Application(middlewares=[middleware])
app.name='main'

app['config'] = get_real_config('polls.yaml', *config_files)
app.on_startup.append(init_mysql)
app.on_cleanup.append(close_mysql)


polls_subapp = polls.get_app(app['config'])
# polls_subapp['db'] = app['db']

# app.add_subapp('/polls/', polls_subapp)
plugin_app(app, '/polls/', polls_subapp)

aiohttp_jinja2.setup(
    app, loader=jinja2.FileSystemLoader([
        str(BASE_DIR / 'polls' / 'templates'),
        str(BASE_DIR / 'auth' / 'templates')]))



# security
policy = SessionIdentityPolicy()
setup_security(app, policy, SimpleAuthPolicy())

web.run_app(app, port=3000)
