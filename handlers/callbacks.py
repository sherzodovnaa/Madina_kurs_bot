from enum import Enum
from typing import Optional

from aiogram.filters.callback_data import CallbackData


class Level(Enum):
    CATEGORY = 'category'
    SUBCATEGORY = 'subcategory'
    QUIZ_START = 'quiz_start'
    QUIZ = 'quiz'


class CategoryCallback(CallbackData, prefix='cat'):
    id: int


class SubcategoryCallback(CallbackData, prefix='sub'):
    id: int
    category: int


class QuizCallback(CallbackData, prefix='quiz'):
    id: int
    subcategory: int
    category: int


class OptionCallback(CallbackData, prefix='option'):
    id: int
    quiz: int
    subcategory: int
    category: int


class BackCallback(CallbackData, prefix='back'):
    level: str
    category: Optional[int] = None
    subcategory: Optional[int] = None
    quiz: Optional[int] = None