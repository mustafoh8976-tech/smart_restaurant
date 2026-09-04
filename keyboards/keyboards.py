import re
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


def main_keyboard():
    buttons = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Меню'), KeyboardButton(text='Корзина')],
            [KeyboardButton(text='Мои заказы'), KeyboardButton(text='Бронирование')],
            [KeyboardButton(text='Избранное'), KeyboardButton(text='Поиск')],
            [KeyboardButton(text='AI-помощник')]
        ],
        resize_keyboard=True
    )
    return buttons


def phone_keyboard():
    buttons = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Отправить номер', request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return buttons


def categories_keyboard(categories):
    buttons = []
    for category in categories:
        category_name = re.sub(r'^\s*\d+(?:\.|\)|-)\s*', '', category['name'])
        buttons.append([InlineKeyboardButton(text=category_name, callback_data=f'category:{category["id"]}')])
    buttons.append([InlineKeyboardButton(text='Назад', callback_data='back_main')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def dishes_keyboard(dishes, category_id):
    buttons = []
    for dish in dishes:
        buttons.append([InlineKeyboardButton(text=f'{dish["name"]} - {dish["price"]} TJS', callback_data=f'dish:{dish["id"]}')])
    buttons.append([InlineKeyboardButton(text='Назад', callback_data='back_categories')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def dish_keyboard(dish_id, category_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Добавить в корзину', callback_data=f'add_cart:{dish_id}')],
        [InlineKeyboardButton(text='Добавить в избранное', callback_data=f'favorite:{dish_id}')],
        [InlineKeyboardButton(text='Назад', callback_data=f'back_dishes:{category_id}')]
    ])


def cart_keyboard(items):
    buttons = []
    for item in items:
        buttons.append([
            InlineKeyboardButton(text='-', callback_data=f'cart_minus:{item["dish_id"]}'),
            InlineKeyboardButton(text=str(item['quantity']), callback_data='cart_noop'),
            InlineKeyboardButton(text='+', callback_data=f'cart_plus:{item["dish_id"]}')
        ])
    buttons.append([InlineKeyboardButton(text='Оформить заказ', callback_data='checkout')])
    buttons.append([InlineKeyboardButton(text='Очистить корзину', callback_data='cart_clear')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def order_keyboard(order_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Товары заказа', callback_data=f'order_items:{order_id}')]
    ])


def delivery_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Доставка'), KeyboardButton(text='Самовывоз')]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def confirm_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Подтвердить', callback_data='order_confirm'),
            InlineKeyboardButton(text='Отменить', callback_data='order_cancel')
        ]
    ])
