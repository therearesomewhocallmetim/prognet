from contextlib import asynccontextmanager

from _root.db import close_mysql, init_mysql


async def select(conn, sql_statement, args=None):
    async with conn.cursor() as cur:
        await cur.execute(sql_statement, args)
        records = await cur.fetchall()
        col_names = [x[0] for x in cur.description]
        return [dict(zip(col_names, q)) for q in records]


@asynccontextmanager
async def database(app):
    await init_mysql(app)
    yield
    await close_mysql(app)


async def last_id(cur):
    await cur.execute('SELECT LAST_INSERT_ID();')
    return (await cur.fetchone())[0]
