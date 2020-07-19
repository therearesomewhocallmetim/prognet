class User:

    @staticmethod
    async def save(conn, login, password):
        statement = f"""INSERT INTO users (login, password) values (%s, %s);"""

        async with conn.cursor() as cur:
            await cur.execute(statement, (login, password))
            await cur.execute('SELECT LAST_INSERT_ID();')
            last_id = (await cur.fetchone())[0]
        return last_id
