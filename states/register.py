from aiogram.fsm.state import StatesGroup, State


class RegisterState(StatesGroup):
    lang = State()
    fullname = State()
    phone = State()