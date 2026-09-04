from aiogram.fsm.state import State, StatesGroup


class CategoryState(StatesGroup):
    name = State()


class DishState(StatesGroup):
    category = State()
    name = State()
    description = State()
    price = State()
    ingredients = State()
    image = State()
    confirmation = State()


class TableState(StatesGroup):
    number = State()
    capacity = State()
