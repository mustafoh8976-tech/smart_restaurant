from database.db_connect import get_connect


async def add_category(name):
    conn = await get_connect()
    try:
        return await conn.fetchval('''
        insert into categories(name) values($1)
        on conflict(name) do nothing
        returning id
        ''', name)
    finally:
        await conn.close()


async def add_dish(category_id, name, description, price, ingredients, image):
    conn = await get_connect()
    try:
        return await conn.fetchval('''
        insert into dishes(category_id, name, description, price, ingredients, image)
        values($1, $2, $3, $4, $5, $6)
        returning id
        ''', category_id, name, description, price, ingredients, image)
    finally:
        await conn.close()


async def add_table(table_number, capacity):
    conn = await get_connect()
    try:
        return await conn.fetchval('''
        insert into restaurant_tables(table_number, capacity)
        values($1, $2)
        on conflict(table_number) do nothing
        returning id
        ''', table_number, capacity)
    finally:
        await conn.close()
