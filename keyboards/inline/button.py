import asyncio
from typing import List

from aiogram.utils.keyboard import InlineKeyboardBuilder


def keyboard_builder(keyboards: List, adjust: tuple):
    builder = InlineKeyboardBuilder()
    for text, id in keyboards:
        builder.button(text=text, callback_data=str(id))

    builder.adjust(*adjust)
    keyboards = builder.as_markup()
    return keyboards


keyboards_lang = [("🇺🇿 Uzbek", "uz"), ("🇷🇺 Russian", "ru"), ("🇺🇸 English", "en")]
keyboards_one_confirm = [("⬅️ Ortga", "back")]

btn_langs = keyboard_builder(keyboards_lang, (3,))
btn_one_confirm = keyboard_builder(keyboards_one_confirm, (1,))