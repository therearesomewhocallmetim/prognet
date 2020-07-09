async def select(conn, sql_statement, *args):
    async with conn.cursor() as cur:
        await cur.execute(sql_statement, *args)
        records = await cur.fetchall()
        col_names = [x[0] for x in cur.description]
        return [dict(zip(col_names, q)) for q in records]
