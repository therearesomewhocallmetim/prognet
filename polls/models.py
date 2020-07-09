from utils import select


class Profile:
    @staticmethod
    async def get_by_user_id(conn, user_id):
        profiles = await select(
            conn, "SELECT * FROM profiles WHERE user_id=%s", int(user_id))
        if profiles:
            return profiles[0]
        return None


    @staticmethod
    async def get_all_names(conn):
        q = "SELECT first_name, last_name, user_id FROM profiles LIMIT 100;"
        return await select(conn, q)


    @staticmethod
    async def save(conn, data):
        statement = """
            INSERT INTO profiles 
                (user_id, first_name, last_name, sex, interests, city) 
            values 
                (%(user_id)s, %(first_name)s, %(last_name)s, %(sex)s, %(interests)s, %(city)s)
            ON DUPLICATE KEY UPDATE
                user_id=%(user_id)s, first_name=%(first_name)s, last_name=%(last_name)s,
                sex=%(sex)s, interests=%(interests)s, city=%(city)s;
            """

        async with conn.cursor() as cur:
            await cur.execute(
                statement, args=dict(
                    user_id=data['user_id'], first_name=data['first_name'],
                    last_name=data['last_name'], sex=data['gender'],
                    interests=data['interests'], city=data['city']))
            await conn.commit()
