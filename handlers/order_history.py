from aiogram import Router, types, F
from services.order_history_service import get_user_orders, get_order_items
from keyboards.keyboards import order_keyboard


router = Router()


@router.message(F.text == 'Мои заказы')
async def orders_history_handler(message: types.Message):
    orders = await get_user_orders(message.from_user.id)
    if not orders:
        await message.answer('У вас пока нет заказов')
        return
    for order in orders:
        status_names = {
            'new': 'новый',
            'accepted': 'принят',
            'preparing': 'готовится',
            'ready': 'готов',
            'delivering': 'доставляется',
            'completed': 'завершен',
            'cancelled': 'отменен'
        }
        await message.answer(
            f'Заказ №{order["id"]}\nСтатус: {status_names.get(order["status"], order["status"])}\nСумма: {order["total_price"]} TJS',
            reply_markup=order_keyboard(order['id'])
        )


@router.callback_query(F.data.startswith('order_items:'))
async def order_items_handler(callback: types.CallbackQuery):
    order_id = callback.data.split(':')[1]
    items = await get_order_items(order_id)
    text = f'Заказ №{order_id}\n\n'
    for item in items:
        text += f'{item["quantity"]} x {item["name"]}\n'
    await callback.message.answer(text)
    await callback.answer()
