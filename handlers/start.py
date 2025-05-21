from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import html, Router

from keyboards.default.button import study_menu
from keyboards.inline.button import btn_langs
from utils.helper.user_helper import check_registration, followers_count
from states.register import RegisterState

start_router = Router()


@start_router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    chat_id = message.chat.id

    await message.answer(f"Assalomu alaykum, {html.bold(message.from_user.full_name)}!",
                         reply_markup=ReplyKeyboardRemove())

    if await check_registration(chat_id):
        await message.answer('Quyidagi tugmalardan birini tanlang!', reply_markup=study_menu(chat_id))
    else:
        await choose_language(message)
        await state.set_state(RegisterState.lang)


@start_router.message(Command('obunachilar'))
async def followers(message: Message):
    count = await followers_count()
    await message.answer(html.bold(f'🔔 Obunachilar soni {count} ta.'))


async def choose_language(message):
    text = (f"O'zingizga mos til tanlang:\n"
            f"Выберите язык, подходящий для себя:\n"
            f"Choose a language suitable for yourself: \n")

    await message.answer(text, reply_markup=btn_langs)