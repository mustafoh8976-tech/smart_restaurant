from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from keyboards.keyboards import cart_keyboard, delivery_keyboard
from services.cart_service import get_cart, add_cart_item, change_cart_item, clear_cart
from services.menu_service import get_dish
from states.order_states import CheckoutState


router = Router()


async def show_cart(message: types.Message):
    items = await get_cart(message.from_user.id)
    if not items:
        await message.answer('Ваша корзина пуста')
        return False

    text = 'Ваша корзина\n\n'
    total = 0
    for item in items:
        item_total = item['quantity'] * item['price']
        total += item_total
        text += f'{item["quantity"]} x {item["name"]} = {item_total} TJS\n'
    text += f'\nИтого: {total} TJS'
    await message.answer(text, reply_markup=cart_keyboard(items))
    return True


@router.message(F.text == 'Корзина')
async def cart_handler(message: types.Message):
    await show_cart(message)


@router.callback_query(F.data.startswith('add_cart:'))
async def add_cart_handler(callback: types.CallbackQuery):
    dish_id = callback.data.split(':')[1]
    dish = await get_dish(dish_id)
    if not dish or not dish['is_available']:
        await callback.answer('Блюдо недоступно', show_alert=True)
        return
    await add_cart_item(callback.from_user.id, dish_id)
    await callback.answer('Добавлено в корзину')


@router.callback_query(F.data.startswith('cart_plus:'))
async def cart_plus_handler(callback: types.CallbackQuery):
    dish_id = callback.data.split(':')[1]
    items = await get_cart(callback.from_user.id)
    for item in items:
        if item['dish_id'] == int(dish_id):
            await change_cart_item(callback.from_user.id, dish_id, item['quantity'] + 1)
    await callback.message.delete()
    await show_cart(callback.message)
    await callback.answer()


@router.callback_query(F.data.startswith('cart_minus:'))
async def cart_minus_handler(callback: types.CallbackQuery):
    dish_id = callback.data.split(':')[1]
    items = await get_cart(callback.from_user.id)
    for item in items:
        if item['dish_id'] == int(dish_id):
            await change_cart_item(callback.from_user.id, dish_id, item['quantity'] - 1)
    await callback.message.delete()
    await show_cart(callback.message)
    await callback.answer()


@router.callback_query(F.data == 'cart_noop')
async def cart_noop_handler(callback: types.CallbackQuery):
    await callback.answer()


@router.callback_query(F.data == 'cart_clear')
async def cart_clear_handler(callback: types.CallbackQuery):
    await clear_cart(callback.from_user.id)
    await callback.message.edit_text('Ваша корзина пуста')
    await callback.answer()


@router.callback_query(F.data == 'checkout')
async def checkout_handler(callback: types.CallbackQuery, state: FSMContext):
    items = await get_cart(callback.from_user.id)
    if not items:
        await callback.answer('Ваша корзина пуста', show_alert=True)
        return
    await state.set_state(CheckoutState.delivery_type)
    await callback.message.answer('Выберите способ получения', reply_markup=delivery_keyboard())
    await callback.answer()
