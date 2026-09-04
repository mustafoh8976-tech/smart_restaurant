from aiogram.fsm.state import State, StatesGroup


class RegistrationState(StatesGroup):
    phone = State()
    email = State()
    password = State()


class SearchState(StatesGroup):
    text = State()


class FeedbackState(StatesGroup):
    comment = State()


class AssistantState(StatesGroup):
    question = State()
