from auth.views import login_get, login_post, logout, register
from polls.views import index


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/login', login_get)
    app.router.add_post('/login', login_post)
    app.router.add_get('/logout', logout)
    app.router.add_post('/register', register)
