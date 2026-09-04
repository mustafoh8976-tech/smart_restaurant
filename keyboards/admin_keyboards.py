import re
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Добавить блюдо', callback_data='admin_add_dish')],
        [InlineKeyboardButton(text='Добавить столик', callback_data='admin_add_table')],
        [InlineKeyboardButton(text='Заказы клиентов', callback_data='admin_client_orders')],
        [InlineKeyboardButton(text='Статистика', callback_data='admin_statistics')]
    ])


def admin_categories_keyboard(categories):
    buttons = []
    for category in categories:
        category_name = re.sub(r'^\s*\d+(?:\.|\)|-)\s*', '', category['name'])
        buttons.append([
            InlineKeyboardButton(
                text=category_name,
                callback_data=f'admin_category:{category["id"]}'
            )
        ])
    buttons.append([InlineKeyboardButton(text='Назад', callback_data='admin_back')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_confirm_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Сохранить', callback_data='admin_save_dish'),
            InlineKeyboardButton(text='Отменить', callback_data='admin_cancel')
        ]
    ])
