from database.db_connect import get_connect


async def add_feedback(user_id, order_id, rating, comment):
    conn = await get_connect()
    try:
        await conn.execute('''
        insert into feedback(user_id, order_id, rating, comment)
        values($1, $2, $3, $4)
        on conflict(user_id, order_id) do update set rating=$3, comment=$4
        ''', user_id, int(order_id), int(rating), comment)
    finally:
        await conn.close()


async def get_average_rating():
    conn = await get_connect()
    try:
        return await conn.fetchval('select coalesce(avg(rating), 0) from feedback')
    finally:
        await conn.close()
