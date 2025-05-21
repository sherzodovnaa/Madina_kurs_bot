from aiogram.fsm.state import StatesGroup, State


class QuizState(StatesGroup):
    confirm = State()
    quession = State()