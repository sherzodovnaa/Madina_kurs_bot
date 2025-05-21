from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from app import ADMINS


def study_menu(chat_id):
    keybords = ['📚 Darsliklar', '👨‍🏫 Kurslar', '🧑‍💻 Testlar', '📊 Statistika', "🌐 Tilni o'zgartirish"]
    if chat_id == int(ADMINS):
        keybords.append('⚙️ Sozlamalar')

    builder = ReplyKeyboardBuilder()

    builder.add(
        *[KeyboardButton(text=keyboard) for keyboard in keybords])

    builder = builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)


def share_contact():
    contact = KeyboardButton(text='📲 Raqamni ulashish', request_contact=True)

    btn = ReplyKeyboardMarkup(keyboard=[
        [contact]
    ])

    return btn


def settings_kb():
    builder = ReplyKeyboardBuilder()
    kbs = ['Shablon', 'Savollarni yuklab olish', 'O`chirish', '⬅️ Ortga']
    builder.add(*[KeyboardButton(text=kb) for kb in kbs])
    builder.adjust(2)
    return builder.as_markup()


