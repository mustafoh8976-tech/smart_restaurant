from decimal import Decimal, InvalidOperation
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config import ADMIN_IDS
from keyboards.admin_keyboards import admin_keyboard, admin_categories_keyboard, admin_confirm_keyboard
from services.admin_service import add_category, add_dish, add_table
from services.menu_service import get_categories
from services.staff_service import get_client_orders
from states.admin_states import CategoryState, DishState, TableState


router = Router()


def is_admin(user_id):
    return user_id in ADMIN_IDS


@router.message(Command('admin'))
async def admin_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer('У вас нет доступа')
        return
    await message.answer(
        'Добро пожаловать в панель администратора онлайн-ресторана!\n\n'
        'Доступные команды:',
        reply_markup=admin_keyboard()
    )


@router.callback_query(F.data == 'admin_client_orders')
async def admin_client_orders_handler(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer('У вас нет доступа', show_alert=True)
        return
    orders = await get_client_orders()
    if not orders:
        await callback.message.answer('Заказов клиентов пока нет')
        await callback.answer()
        return
    for order in orders:
        customer = order['first_name'] or order['username'] or 'Без имени'
        await callback.message.answer(
            f'Заказ №{order["id"]}\n'
            f'Клиент: {customer}\n'
            f'Статус: {order["status"]}\n'
            f'Сумма: {order["total_price"]} TJS'
        )
    await callback.answer()


@router.callback_query(F.data == 'admin_statistics')
async def admin_statistics_handler(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer('У вас нет доступа', show_alert=True)
        return
    await callback.message.answer('Для просмотра статистики используйте команду: Статистика')
    await callback.answer()


@router.callback_query(F.data == 'admin_add_category')
async def admin_add_category_handler(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer('У вас нет доступа', show_alert=True)
        return
    await state.set_state(CategoryState.name)
    await callback.message.answer('Введите название категории')
    await callback.answer()


@router.message(CategoryState.name)
async def admin_category_name_handler(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        await message.answer('У вас нет доступа')
        return
    name = message.text.strip()
    if not name:
        await message.answer('Название не может быть пустым')
        return
    category_id = await add_category(name)
    await state.clear()
    if category_id:
        await message.answer('Категория добавлена')
    else:
        await message.answer('Такая категория уже существует')


@router.callback_query(F.data == 'admin_add_dish')
async def admin_add_dish_handler(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer('У вас нет доступа', show_alert=True)
        return
    categories = await get_categories()
    if not categories:
        await callback.message.answer('Сначала добавьте категорию')
        await callback.answer()
        return
    await state.set_state(DishState.category)
    await callback.message.answer(
        'Выберите категорию для блюда:',
        reply_markup=admin_categories_keyboard(categories)
    )
    await callback.answer()


@router.callback_query(F.data == 'admin_add_table')
async def admin_add_table_handler(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer('У вас нет доступа', show_alert=True)
        return
    await state.set_state(TableState.number)
    await callback.message.answer('Введите номер столика')
    await callback.answer()


@router.message(TableState.number)
async def admin_table_number_handler(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) < 1:
        await message.answer('Введите правильный номер столика')
        return
    await state.update_data(table_number=int(message.text))
    await state.set_state(TableState.capacity)
    await message.answer('Введите количество мест')


@router.message(TableState.capacity)
async def admin_table_capacity_handler(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) < 1:
        await message.answer('Введите правильное количество мест')
        return
    data = await state.get_data()
    table_id = await add_table(data['table_number'], int(message.text))
    await state.clear()
    if table_id:
        await message.answer(f'Столик №{data["table_number"]} добавлен')
    else:
        await message.answer('Столик с таким номером уже существует')


@router.callback_query(F.data == 'admin_back')
async def admin_back_handler(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer('У вас нет доступа', show_alert=True)
        return
    await state.clear()
    await callback.message.edit_text(
        'Панель администратора\n\nДоступные команды:',
        reply_markup=admin_keyboard()
    )
    await callback.answer()


@router.callback_query(DishState.category, F.data.startswith('admin_category:'))
async def admin_dish_category_handler(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer('У вас нет доступа', show_alert=True)
        return
    category_id = callback.data.split(':')[1]
    if not category_id.isdigit():
        await callback.answer('Неверная категория', show_alert=True)
        return
    await state.update_data(category_id=int(category_id))
    await state.set_state(DishState.name)
    await callback.message.answer('Введите название блюда')
    await callback.answer()


@router.message(DishState.name)
async def admin_dish_name_handler(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(DishState.description)
    await message.answer('Введите описание блюда')


@router.message(DishState.description)
async def admin_dish_description_handler(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(DishState.price)
    await message.answer('Введите цену блюда')


@router.message(DishState.price)
async def admin_dish_price_handler(message: types.Message, state: FSMContext):
    try:
        price = Decimal(message.text.replace(',', '.'))
        if price < 0:
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        await message.answer('Введите правильную цену')
        return
    await state.update_data(price=price)
    await state.set_state(DishState.ingredients)
    await message.answer('Введите ингредиенты')


@router.message(DishState.ingredients)
async def admin_dish_ingredients_handler(message: types.Message, state: FSMContext):
    await state.update_data(ingredients=message.text.strip())
    await state.set_state(DishState.image)
    await message.answer('Отправьте фото блюда или напишите -')


@router.message(DishState.image, F.photo)
async def admin_dish_photo_handler(message: types.Message, state: FSMContext):
    await state.update_data(image=message.photo[-1].file_id)
    await show_dish_confirmation(message, state)


@router.message(DishState.image, F.text)
async def admin_dish_no_photo_handler(message: types.Message, state: FSMContext):
    if message.text != '-':
        await message.answer('Отправьте фото или напишите -')
        return
    await state.update_data(image=None)
    await show_dish_confirmation(message, state)


async def show_dish_confirmation(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.set_state(DishState.confirmation)
    text = (
        f'Проверьте блюдо:\n\n{data["name"]}\nЦена: {data["price"]} TJS\n'
        f'{data["description"]}\nИнгредиенты: {data["ingredients"]}'
    )
    if data.get('image'):
        await message.answer_photo(data['image'], caption=text, reply_markup=admin_confirm_keyboard())
    else:
        await message.answer(text, reply_markup=admin_confirm_keyboard())


@router.callback_query(DishState.confirmation, F.data == 'admin_save_dish')
async def admin_save_dish_handler(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer('У вас нет доступа', show_alert=True)
        return
    data = await state.get_data()
    dish_id = await add_dish(
        data['category_id'], data['name'], data['description'], data['price'], data['ingredients'], data['image']
    )
    await state.clear()
    await callback.message.answer(f'Блюдо добавлено. Номер блюда: {dish_id}')
    await callback.answer()


@router.callback_query(DishState.confirmation, F.data == 'admin_cancel')
async def admin_cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer('Добавление отменено')
    await callback.answer()
