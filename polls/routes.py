from polls.views import index, login_get, login_post


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/login', login_get)
    app.router.add_post('/login', login_post)