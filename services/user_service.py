from database.db_connect import get_connect


async def get_user(telegram_id):
    conn = await get_connect()
    try:
        return await conn.fetchrow('select * from users where telegram_id=$1', telegram_id)
    finally:
        await conn.close()


async def add_user(telegram_id, first_name, username, phone, email, password_hash):
    conn = await get_connect()
    try:
        await conn.execute('''
        insert into users(telegram_id, first_name, username, phone, email, password_hash)
        values($1, $2, $3, $4, $5, $6)
        on conflict(telegram_id) do update set
        first_name=$2, username=$3, phone=$4, email=$5, password_hash=$6
        ''', telegram_id, first_name, username, phone, email, password_hash)
    finally:
        await conn.close()
