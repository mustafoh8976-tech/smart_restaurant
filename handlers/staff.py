from aiogram import Router, types, F
from config import STAFF_IDS, ADMIN_IDS
from services.staff_service import get_new_orders, update_order_status, get_statistics
from keyboards.staff_keyboards import order_status_keyboard


router = Router()


@router.message(F.text == 'Сотрудник')
async def staff_handler(message: types.Message):
    if message.from_user.id not in STAFF_IDS + ADMIN_IDS:
        await message.answer('У вас нет доступа')
        return
    orders = await get_new_orders()
    if not orders:
        await message.answer('Новых заказов нет')
        return
    for order in orders:
        await message.answer(
            f'Заказ №{order["id"]} - {order["total_price"]} TJS',
            reply_markup=order_status_keyboard(order['id'])
        )


@router.callback_query(F.data.startswith('status:'))
async def status_handler(callback: types.CallbackQuery):
    if callback.from_user.id not in STAFF_IDS + ADMIN_IDS:
        await callback.answer('У вас нет доступа', show_alert=True)
        return
    parts = callback.data.split(':')
    if len(parts) != 3:
        await callback.answer('Неверная команда', show_alert=True)
        return
    if not parts[1].isdigit():
        await callback.answer('Неверный номер заказа', show_alert=True)
        return
    order = await update_order_status(parts[1], parts[2])
    if not order:
        await callback.answer('Заказ не найден', show_alert=True)
        return
    status_names = {
        'accepted': 'принят',
        'preparing': 'готовится',
        'ready': 'готов',
        'delivering': 'доставляется',
        'completed': 'завершен',
        'cancelled': 'отменен'
    }
    status_name = status_names.get(parts[2], parts[2])
    await callback.message.answer(f'У заказа №{parts[1]} новый статус: {status_name}')
    await callback.bot.send_message(order['user_id'], f'Ваш заказ №{parts[1]}. Новый статус: {status_name}')
    await callback.answer()


@router.message(F.text == 'Статистика')
async def statistics_handler(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer('У вас нет доступа')
        return
    statistics = await get_statistics()
    await message.answer(
        f'Сегодня\nЗаказы: {statistics["orders"]}\nВыручка: {statistics["revenue"]} TJS\nСредний чек: {statistics["average_order"]} TJS'
    )
