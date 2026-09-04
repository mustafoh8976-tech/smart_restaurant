from aiogram.fsm.state import State, StatesGroup


class ReservationState(StatesGroup):
    date = State()
    time = State()
    table = State()
    guests = State()
    phone = State()
    comment = State()
    confirmation = State()
