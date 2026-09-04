from database.db_connect import get_connect


async def get_user_orders(user_id):
    conn = await get_connect()
    try:
        return await conn.fetch('''
        select * from orders where user_id=$1 order by created_at desc
        ''', user_id)
    finally:
        await conn.close()


async def get_order_items(order_id):
    conn = await get_connect()
    try:
        return await conn.fetch('''
        select order_items.*, dishes.name
        from order_items join dishes on dishes.id=order_items.dish_id
        where order_id=$1
        ''', int(order_id))
    finally:
        await conn.close()
