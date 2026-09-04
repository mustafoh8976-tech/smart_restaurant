from database.db_connect import get_connect
from services.cart_service import get_cart


async def create_order(user_id, data):
    conn = await get_connect()
    try:
        items = await get_cart(user_id)
        total = sum(item['quantity'] * item['price'] for item in items)
        order_id = await conn.fetchval('''
        insert into orders(user_id, delivery_type, address, phone, comment, total_price)
        values($1, $2, $3, $4, $5, $6)
        returning id
        ''', user_id, data.get('delivery_type'), data.get('address'), data.get('phone'), data.get('comment'), total)
        for item in items:
            await conn.execute('''
            insert into order_items(order_id, dish_id, quantity, price)
            values($1, $2, $3, $4)
            ''', order_id, item['dish_id'], item['quantity'], item['price'])
        return order_id
    finally:
        await conn.close()
