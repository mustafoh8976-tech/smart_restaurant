from database.db_connect import get_connect


ORDER_STATUSES = {'new', 'accepted', 'preparing', 'ready', 'delivering', 'completed', 'cancelled'}


async def get_new_orders():
    conn = await get_connect()
    try:
        return await conn.fetch("select * from orders where status='new' order by created_at")
    finally:
        await conn.close()


async def get_client_orders():
    conn = await get_connect()
    try:
        return await conn.fetch('''
        select orders.*, users.first_name, users.username
        from orders
        join users on users.telegram_id=orders.user_id
        order by orders.created_at desc
        ''')
    finally:
        await conn.close()


async def update_order_status(order_id, status):
    if status not in ORDER_STATUSES:
        return None
    conn = await get_connect()
    try:
        return await conn.fetchrow('''
        update orders set status=$1 where id=$2
        returning user_id, status
        ''', status, int(order_id))
    finally:
        await conn.close()


async def get_statistics():
    conn = await get_connect()
    try:
        return await conn.fetchrow('''
        select count(*) as orders,
        coalesce(sum(total_price) filter(where status='completed'), 0) as revenue,
        coalesce(avg(total_price) filter(where status='completed'), 0) as average_order
        from orders where created_at::date=current_date
        ''')
    finally:
        await conn.close()
