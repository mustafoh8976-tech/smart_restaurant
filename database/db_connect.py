import asyncpg
from config import DB_HOST, DB_PORT, DB_USER, DB_NAME, DB_PASSWORD


async def get_connect():
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        database=DB_NAME,
        password=DB_PASSWORD
    )
    return conn
