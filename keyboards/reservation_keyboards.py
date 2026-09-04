from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def reservation_confirm_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Подтвердить', callback_data='reservation_confirm'),
            InlineKeyboardButton(text='Отменить', callback_data='reservation_cancel')
        ]
    ])


def reservation_tables_keyboard(tables):
    buttons = []
    for table in tables:
        status = 'свободен' if table['is_available'] else 'занят'
        if table['is_available']:
            buttons.append([
                InlineKeyboardButton(
                    text=f'Столик №{table["table_number"]} - {table["capacity"]} мест - {status}',
                    callback_data=f'reservation_table:{table["id"]}'
                )
            ])
        else:
            buttons.append([InlineKeyboardButton(
                text=f'Столик №{table["table_number"]} - {table["capacity"]} мест - {status}',
                callback_data='reservation_busy'
            )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
