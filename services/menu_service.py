from database.db_connect import get_connect


async def get_categories():
    conn = await get_connect()
    try:
        return await conn.fetch('select * from categories order by name')
    finally:
        await conn.close()


async def get_dishes(category_id):
    conn = await get_connect()
    try:
        return await conn.fetch('''
        select * from dishes
        where category_id=$1 and is_available=true
        order by name
        ''', int(category_id))
    finally:
        await conn.close()


async def get_dish(dish_id):
    conn = await get_connect()
    try:
        return await conn.fetchrow('select * from dishes where id=$1', int(dish_id))
    finally:
        await conn.close()


async def search_dishes(text):
    conn = await get_connect()
    try:
        return await conn.fetch('''
        select * from dishes
        where is_available=true and (
            name ilike $1 or description ilike $1 or ingredients ilike $1
            or id::text=$2
        )
        order by name
        ''', f'%{text}%', text.strip())
    finally:
        await conn.close()


async def get_available_dishes():
    conn = await get_connect()
    try:
        return await conn.fetch('select * from dishes where is_available=true order by name')
    finally:
        await conn.close()
