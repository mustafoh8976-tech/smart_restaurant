from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from services.cart_service import get_cart, clear_cart
from services.order_service import create_order
from states.order_states import CheckoutState
from keyboards.keyboards import confirm_keyboard


router = Router()


@router.message(CheckoutState.delivery_type)
async def set_delivery_type(message: types.Message, state: FSMContext):
    if message.text not in ['Доставка', 'Самовывоз']:
        await message.answer('Выберите доставку или самовывоз')
        return
    await state.update_data(delivery_type=message.text)
    if message.text == 'Доставка':
        await state.set_state(CheckoutState.address)
        await message.answer('Введите адрес доставки')
    else:
        await state.set_state(CheckoutState.phone)
        await message.answer('Введите номер телефона')


@router.message(CheckoutState.address)
async def set_address(message: types.Message, state: FSMContext):
    if not message.text or len(message.text) < 5:
        await message.answer('Введите правильный адрес')
        return
    await state.update_data(address=message.text)
    await state.set_state(CheckoutState.phone)
    await message.answer('Введите номер телефона')


@router.message(CheckoutState.phone)
async def set_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(CheckoutState.comment)
    await message.answer('Добавьте комментарий или напишите -')


@router.message(CheckoutState.comment)
async def set_comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)
    data = await state.get_data()
    items = await get_cart(message.from_user.id)
    total = sum(item['quantity'] * item['price'] for item in items)
    text = f'Ваш заказ\n\nСумма: {total} TJS\nСпособ получения: {data.get("delivery_type")}\n'
    if data.get('address'):
        text += f'Адрес: {data["address"]}\n'
    await state.set_state(CheckoutState.confirmation)
    await message.answer(text, reply_markup=confirm_keyboard())


@router.callback_query(CheckoutState.confirmation, F.data == 'order_confirm')
async def confirm_order(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_id = await create_order(callback.from_user.id, data)
    await clear_cart(callback.from_user.id)
    await state.clear()
    await callback.message.answer(f'Заказ №{order_id} создан')
    await callback.answer()


@router.callback_query(CheckoutState.confirmation, F.data == 'order_cancel')
async def cancel_order(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer('Заказ отменен')
    await callback.answer()
