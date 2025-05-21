from aiogram import Router, F
from aiogram.types import Message

statistics_router = Router()


@statistics_router.message(F.text == '📊 Statistika')
async def get_statistics(message: Message):
    pass