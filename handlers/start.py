import hashlib
import re
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from keyboards.keyboards import main_keyboard, phone_keyboard
from services.user_service import get_user, add_user
from states.states import RegistrationState


router = Router()


@router.message(Command('start'))
async def start_handler(message: types.Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if user and user['phone'] and user['email'] and user['password_hash']:
        await message.answer('Добро пожаловать в наш онлайн-ресторан!', reply_markup=main_keyboard())
        return

    await state.set_state(RegistrationState.phone)
    await message.answer('Отправьте свой номер телефона', reply_markup=phone_keyboard())


@router.message(RegistrationState.phone)
async def set_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    if not phone:
        await message.answer('Введите номер телефона')
        return
    await state.update_data(phone=phone)
    await state.set_state(RegistrationState.email)
    await message.answer('Введите электронную почту')


@router.message(RegistrationState.email)
async def set_email(message: types.Message, state: FSMContext):
    if not message.text or not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', message.text):
        await message.answer('Введите правильную электронную почту')
        return
    await state.update_data(email=message.text.lower())
    await state.set_state(RegistrationState.password)
    await message.answer('Придумайте пароль минимум из 6 символов')


@router.message(RegistrationState.password)
async def set_password(message: types.Message, state: FSMContext):
    if not message.text or len(message.text) < 6:
        await message.answer('Пароль должен содержать минимум 6 символов')
        return
    data = await state.get_data()
    password_hash = hashlib.sha256(message.text.encode()).hexdigest()
    await add_user(
        message.from_user.id,
        message.from_user.first_name,
        message.from_user.username,
        data['phone'],
        data['email'],
        password_hash
    )
    await state.clear()
    await message.answer('Добро пожаловать в наш онлайн-ресторан!', reply_markup=main_keyboard())
