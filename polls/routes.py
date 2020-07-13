from polls.views import index, profile_detail, profile_get, profile_post


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/{user_id:\d+}', profile_detail)
    app.router.add_get('/me', profile_get)
    app.router.add_post('/me', profile_post)

