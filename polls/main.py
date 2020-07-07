import sys

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp_security import SessionIdentityPolicy
from aiohttp_security import setup as setup_security
from aiohttp_session import SimpleCookieStorage, session_middleware

from auth.policies import SimpleAuthPolicy
from polls.db import close_pg, init_pg
from polls.routes import setup_routes
from polls.settings import BASE_DIR, get_real_config

config_files = sys.argv[1:]

middleware = session_middleware(SimpleCookieStorage())

app = web.Application(middlewares=[middleware])
app['config'] = get_real_config('polls.yaml', *config_files)

aiohttp_jinja2.setup(
    app, loader=jinja2.FileSystemLoader([
        str(BASE_DIR / 'polls' / 'templates'),
        str(BASE_DIR / 'auth' / 'templates')]))

setup_routes(app)

app.on_startup.append(init_pg)
app.on_cleanup.append(close_pg)

# security
policy = SessionIdentityPolicy()
setup_security(app, policy, SimpleAuthPolicy())

web.run_app(app, port=3000)
