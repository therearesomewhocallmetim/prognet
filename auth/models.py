from utils import last_id


class User:

    @staticmethod
    async def save(conn, login, password):
        statement = f"""INSERT INTO users (login, password) values (%s, %s);"""

        async with conn.cursor() as cur:
            await cur.execute(statement, (login, password))
            return await last_id(cur)
