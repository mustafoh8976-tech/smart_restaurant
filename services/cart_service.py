from database.db_connect import get_connect


async def add_cart_item(user_id, dish_id):
    conn = await get_connect()
    try:
        await conn.execute('''
        insert into cart_items(user_id, dish_id, quantity)
        values($1, $2, 1)
        on conflict(user_id, dish_id) do update set quantity=cart_items.quantity + 1
        ''', user_id, int(dish_id))
    finally:
        await conn.close()


async def get_cart(user_id):
    conn = await get_connect()
    try:
        return await conn.fetch('''
        select cart_items.*, dishes.name, dishes.price
        from cart_items
        join dishes on dishes.id=cart_items.dish_id
        where cart_items.user_id=$1
        order by cart_items.id
        ''', user_id)
    finally:
        await conn.close()


async def change_cart_item(user_id, dish_id, quantity):
    conn = await get_connect()
    try:
        if quantity <= 0:
            await conn.execute('delete from cart_items where user_id=$1 and dish_id=$2', user_id, int(dish_id))
        else:
            await conn.execute('update cart_items set quantity=$1 where user_id=$2 and dish_id=$3', quantity, user_id, int(dish_id))
    finally:
        await conn.close()


async def clear_cart(user_id):
    conn = await get_connect()
    try:
        await conn.execute('delete from cart_items where user_id=$1', user_id)
    finally:
        await conn.close()
