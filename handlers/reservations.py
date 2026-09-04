from datetime import date, time
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from keyboards.reservation_keyboards import reservation_confirm_keyboard, reservation_tables_keyboard
from services.reservation_service import get_tables_status, get_table, create_reservation
from states.reservation_states import ReservationState


router = Router()


@router.message(F.text == 'Бронирование')
async def reservations_handler(message: types.Message, state: FSMContext):
    await state.set_state(ReservationState.date)
    await message.answer('Введите дату бронирования в формате ГГГГ-ММ-ДД')


@router.message(ReservationState.date)
async def set_reservation_date(message: types.Message, state: FSMContext):
    try:
        reservation_date = date.fromisoformat(message.text)
        if reservation_date < date.today():
            raise ValueError
    except ValueError:
        await message.answer('Введите правильную будущую дату')
        return
    await state.update_data(date=reservation_date)
    await state.set_state(ReservationState.time)
    await message.answer('Введите время в формате ЧЧ:ММ')


@router.message(ReservationState.time)
async def set_reservation_time(message: types.Message, state: FSMContext):
    try:
        reservation_time = time.fromisoformat(message.text)
        if reservation_time.second != 0:
            raise ValueError
    except ValueError:
        await message.answer('Введите правильное время')
        return
    await state.update_data(time=reservation_time)
    data = await state.get_data()
    tables = await get_tables_status(data['date'], reservation_time)
    if not tables:
        await message.answer('Столики пока не добавлены')
        await state.clear()
        return
    await state.set_state(ReservationState.table)
    await message.answer('Выберите свободный столик. Занятые столики выбрать нельзя:', reply_markup=reservation_tables_keyboard(tables))


@router.callback_query(ReservationState.table, F.data.startswith('reservation_table:'))
async def set_reservation_table(callback: types.CallbackQuery, state: FSMContext):
    table_id = callback.data.split(':')[1]
    table = await get_table(table_id)
    if not table:
        await callback.answer('Столик не найден', show_alert=True)
        return
    data = await state.get_data()
    tables = await get_tables_status(data['date'], data['time'])
    selected = next((item for item in tables if item['id'] == table['id']), None)
    if not selected or not selected['is_available']:
        await callback.answer('Этот столик уже занят', show_alert=True)
        return
    await state.update_data(table_id=table['id'], table_number=table['table_number'], table_capacity=table['capacity'])
    await state.set_state(ReservationState.guests)
    await callback.message.answer(f'Сколько будет гостей? Максимум: {table["capacity"]}')
    await callback.answer()


@router.callback_query(ReservationState.table, F.data == 'reservation_busy')
async def reservation_busy_handler(callback: types.CallbackQuery):
    await callback.answer('Этот столик уже занят', show_alert=True)


@router.message(ReservationState.guests)
async def set_reservation_guests(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        guests = int(message.text)
        if guests < 1 or guests > data['table_capacity']:
            raise ValueError
    except (ValueError, TypeError):
        await message.answer(f'Введите число от 1 до {data["table_capacity"]}')
        return
    await state.update_data(guests=guests)
    await state.set_state(ReservationState.phone)
    await message.answer('Введите номер телефона')


@router.message(ReservationState.phone)
async def set_reservation_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(ReservationState.comment)
    await message.answer('Добавьте комментарий или напишите -')


@router.message(ReservationState.comment)
async def set_reservation_comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)
    data = await state.get_data()
    await state.set_state(ReservationState.confirmation)
    await message.answer(
        f'Бронирование\n\nДата: {data["date"]}\nВремя: {data["time"].strftime("%H:%M")}\nГостей: {data["guests"]}\nСтолик: {data["table_number"]}',
        reply_markup=reservation_confirm_keyboard()
    )


@router.callback_query(ReservationState.confirmation, F.data == 'reservation_confirm')
async def confirm_reservation(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    reservation_id = await create_reservation(callback.from_user.id, data, data['table_id'])
    await state.clear()
    await callback.message.answer(f'Бронирование №{reservation_id} создано')
    await callback.answer()


@router.callback_query(ReservationState.confirmation, F.data == 'reservation_cancel')
async def cancel_reservation(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer('Бронирование отменено')
    await callback.answer()
