from auth.views import login_get, login_post, logout, register
from polls.views import index, profile_get, profile_post, profile_detail


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/login', login_get)
    app.router.add_post('/login', login_post)
    app.router.add_get('/logout', logout)
    app.router.add_post('/register', register)

    app.router.add_get('/profiles/{user_id:\d+}', profile_detail)
    app.router.add_get('/profile', profile_get)
    app.router.add_post('/profile', profile_post)

