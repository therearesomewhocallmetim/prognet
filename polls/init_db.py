import asyncio
import hashlib

import aiomysql

from polls.settings import get_real_config

conf = get_real_config('polls_local.yaml')['db']


async def create_tables(conn):
    async with conn.cursor() as cur:
        await cur.execute(
            """CREATE TABLE IF NOT EXISTS users (
               id BIGINT PRIMARY KEY AUTO_INCREMENT,
               login VARCHAR(255) UNIQUE KEY not null, 
               password VARCHAR(255) NOT NULL
            );""")


async def sample_data(conn):
    async with conn.cursor() as cur:
        await cur.execute(
            f"""INSERT INTO users (login, password) 
                values ('admin', '{hashlib.sha3_256('password'.encode()).hexdigest()}');""")
        await conn.commit()


async def main():
    conn = await aiomysql.connect(
        host=conf['host'], port=conf['port'], user=conf['user'],
        password=conf['password'], db=conf['database'])

    await create_tables(conn)
    await sample_data(conn)
    conn.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
