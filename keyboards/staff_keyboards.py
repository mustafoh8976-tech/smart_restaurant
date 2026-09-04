from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def order_status_keyboard(order_id):
    statuses = ['accepted', 'preparing', 'ready', 'delivering', 'completed', 'cancelled']
    buttons = []
    for status in statuses:
        status_names = {
            'accepted': 'Принять',
            'preparing': 'Готовится',
            'ready': 'Готов',
            'delivering': 'Доставляется',
            'completed': 'Завершить',
            'cancelled': 'Отменить'
        }
        buttons.append([InlineKeyboardButton(text=status_names[status], callback_data=f'status:{order_id}:{status}')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)