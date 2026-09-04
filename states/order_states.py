from aiogram.fsm.state import State, StatesGroup


class CheckoutState(StatesGroup):
    delivery_type = State()
    address = State()
    phone = State()
    comment = State()
    confirmation = State()
