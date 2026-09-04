from aiogram import Router, types, F
from services.favorite_service import add_favorite, get_favorites
from services.menu_service import get_dish
from keyboards.keyboards import dish_keyboard


router = Router()


@router.message(F.text == 'Избранное')
async def favorites_handler(message: types.Message):
    dishes = await get_favorites(message.from_user.id)
    if not dishes:
        await message.answer('У вас нет избранных блюд')
        return
    for dish in dishes:
        await message.answer(dish['name'], reply_markup=dish_keyboard(dish['id'], dish['category_id']))


@router.callback_query(F.data.startswith('favorite:'))
async def favorite_handler(callback: types.CallbackQuery):
    dish_id = callback.data.split(':')[1]
    dish = await get_dish(dish_id)
    if not dish:
        await callback.answer('Блюдо не найдено', show_alert=True)
        return
    await add_favorite(callback.from_user.id, dish_id)
    await callback.answer('Добавлено в избранное')
