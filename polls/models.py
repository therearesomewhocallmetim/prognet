from utils import select


class Profile:
    @staticmethod
    async def get_by_user_id(conn, user_id):
        return await select(
            conn, "SELECT * FROM profiles WHERE user_id=%s", int(user_id))
