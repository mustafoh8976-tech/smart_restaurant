from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from keyboards.keyboards import dishes_keyboard
from services.menu_service import search_dishes
from states.states import SearchState


router = Router()


@router.message(F.text == 'Поиск')
async def search_handler(message: types.Message, state: FSMContext):
    await state.set_state(SearchState.text)
    await message.answer('Введите название или номер блюда')


@router.message(SearchState.text)
async def search_result_handler(message: types.Message, state: FSMContext):
    dishes = await search_dishes(message.text)
    await state.clear()
    if not dishes:
        await message.answer('Блюда не найдены')
        return
    await message.answer('Результаты поиска', reply_markup=dishes_keyboard(dishes, None))
