from database.db_connect import get_connect


async def add_favorite(user_id, dish_id):
    conn = await get_connect()
    try:
        await conn.execute('''
        insert into favorites(user_id, dish_id)
        values($1, $2)
        on conflict(user_id, dish_id) do nothing
        ''', user_id, int(dish_id))
    finally:
        await conn.close()


async def get_favorites(user_id):
    conn = await get_connect()
    try:
        return await conn.fetch('''
        select dishes.* from favorites
        join dishes on dishes.id=favorites.dish_id
        where favorites.user_id=$1
        order by dishes.name
        ''', user_id)
    finally:
        await conn.close()
