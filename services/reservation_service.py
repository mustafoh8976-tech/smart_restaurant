from database.db_connect import get_connect


async def get_available_table(guests, date, time):
    conn = await get_connect()
    try:
        return await conn.fetchrow('''
        select t.* from restaurant_tables t
        where t.capacity >= $1 and t.is_active=true
        and not exists(
            select 1 from reservations r
            where r.table_id=t.id and r.reservation_date=$2 and r.reservation_time=$3
            and r.status in ('pending', 'confirmed')
        )
        order by t.capacity
        limit 1
        ''', guests, date, time)
    finally:
        await conn.close()


async def get_tables_status(date, time):
    conn = await get_connect()
    try:
        return await conn.fetch('''
        select t.*, not exists(
            select 1 from reservations r
            where r.table_id=t.id and r.reservation_date=$1 and r.reservation_time=$2
            and r.status in ('pending', 'confirmed')
        ) as is_available
        from restaurant_tables t
        where t.is_active=true
        order by t.table_number
        ''', date, time)
    finally:
        await conn.close()


async def get_table(table_id):
    conn = await get_connect()
    try:
        return await conn.fetchrow('select * from restaurant_tables where id=$1 and is_active=true', int(table_id))
    finally:
        await conn.close()


async def create_reservation(user_id, data, table_id):
    conn = await get_connect()
    try:
        return await conn.fetchval('''
        insert into reservations(user_id, table_id, reservation_date, reservation_time, guests, phone, comment)
        values($1, $2, $3, $4, $5, $6, $7)
        returning id
        ''', user_id, table_id, data['date'], data['time'], data['guests'], data['phone'], data.get('comment'))
    finally:
        await conn.close()
