from aiogram import Router, types, F
from keyboards.keyboards import categories_keyboard, dishes_keyboard, dish_keyboard
from services.menu_service import get_categories, get_dishes, get_dish


router = Router()


@router.message(F.text == 'Меню')
async def menu_handler(message: types.Message):
    categories = await get_categories()
    if not categories:
        await message.answer('Меню пока не добавлено')
        return
    await message.answer('Меню', reply_markup=categories_keyboard(categories))


@router.callback_query(F.data.startswith('category:'))
async def category_handler(callback: types.CallbackQuery):
    category_id = callback.data.split(':')[1]
    dishes = await get_dishes(category_id)
    if not dishes:
        await callback.message.answer('В этой категории пока нет доступных блюд')
        await callback.answer()
        return
    await callback.message.answer('Выберите блюдо', reply_markup=dishes_keyboard(dishes, category_id))
    await callback.answer()


@router.callback_query(F.data.startswith('dish:'))
async def dish_handler(callback: types.CallbackQuery):
    dish_id = callback.data.split(':')[1]
    dish = await get_dish(dish_id)
    if not dish:
        await callback.answer('Блюдо не найдено', show_alert=True)
        return
    text = (
        f'{dish["name"]}\n\nЦена: {dish["price"]} TJS\n\n{dish["description"] or "Нет описания"}'
    )
    if dish['image']:
        await callback.message.answer_photo(dish['image'], caption=text, reply_markup=dish_keyboard(dish['id'], dish['category_id']))
    else:
        await callback.message.answer(text, reply_markup=dish_keyboard(dish['id'], dish['category_id']))
    await callback.answer()


@router.callback_query(F.data == 'back_main')
async def back_main_handler(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer('Главное меню')
    await callback.answer()


@router.callback_query(F.data == 'back_categories')
async def back_categories_handler(callback: types.CallbackQuery):
    categories = await get_categories()
    await callback.message.edit_text('Меню', reply_markup=categories_keyboard(categories))
    await callback.answer()


@router.callback_query(F.data.startswith('back_dishes:'))
async def back_dishes_handler(callback: types.CallbackQuery):
    category_id = callback.data.split(':')[1]
    dishes = await get_dishes(category_id)
    await callback.message.delete()
    await callback.message.answer('Выберите блюдо', reply_markup=dishes_keyboard(dishes, category_id))
    await callback.answer()
