import aiomysql


async def init_mysql(app):
    conf = app['config']['db']

    conn = await aiomysql.create_pool(
        host=conf['host'], port=conf['port'], user=conf['user'],
        password=conf['password'], db=conf['database'])
    app['db'] = conn


async def close_mysql(app):
    app['db'].close()
