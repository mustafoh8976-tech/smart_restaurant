import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from database.tables import init_tables
from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.cart import router as cart_router
from handlers.orders import router as orders_router
from handlers.reservations import router as reservations_router
from handlers.favorites import router as favorites_router
from handlers.order_history import router as order_history_router
from handlers.search import router as search_router
from handlers.staff import router as staff_router
from handlers.admin import router as admin_router
from handlers.ai_assistant import router as ai_router


load_dotenv()
bot = Bot(os.getenv('BOT_TOKEN'))
dp = Dispatcher()


async def main():
    await init_tables()
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(cart_router)
    dp.include_router(orders_router)
    dp.include_router(reservations_router)
    dp.include_router(favorites_router)
    dp.include_router(order_history_router)
    dp.include_router(search_router)
    dp.include_router(staff_router)
    dp.include_router(admin_router)
    dp.include_router(ai_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
