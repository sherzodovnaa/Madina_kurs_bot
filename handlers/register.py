from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.types import ReplyKeyboardRemove

from keyboards.default.button import share_contact, study_menu
from utils.helper.user_helper import save_language_to_database, register

from states.register import RegisterState

register_router = Router()


@register_router.callback_query(lambda call: call.data in ['uz', 'ru', 'en'])
async def save_lang(call: CallbackQuery, state: FSMContext):
    til = call.data
    chat_id = call.message.chat.id
    await save_language_to_database(chat_id, til)
    username = call.from_user.username
    current_state = await state.get_state()
    if current_state == RegisterState.lang.state:
        await state.update_data(lang=til, username=username)
        await state.set_state(RegisterState.fullname)
        await call.message.answer("To'liq ismingiz kiriting: ", reply_markup=ReplyKeyboardRemove())
    else:
        await call.message.edit_text(f"<b>{til}</b> tiliga o'zgardi!")


@register_router.message(RegisterState.fullname)
async def save_fullname(message: Message, state: FSMContext):
    fullname = message.text
    await state.update_data(fullname=fullname)
    await state.set_state(RegisterState.phone)
    await message.answer("Telefon raqamingizni kiriting yoki ulashing: ", reply_markup=share_contact())


@register_router.message(F.text == '📲 Raqamni ulashish')
@register_router.message(RegisterState.phone)
async def save_fullname(message: Message, state: FSMContext):
    chat_id = message.chat.id

    phone = message.text
    if message.contact:
        phone = message.contact.phone_number

    data = await state.get_data()

    await register(chat_id=chat_id, fullname=data['fullname'], username=data['username'], phone=phone, lang=data['lang'])
    await message.answer('Quyidagi tugmalardan birini tanlang!', reply_markup=study_menu(chat_id))
    await state.clear()