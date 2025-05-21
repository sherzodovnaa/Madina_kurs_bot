import random  # new

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.callbacks import CategoryCallback, SubcategoryCallback, BackCallback, Level, QuizCallback, OptionCallback
from utils.helper.user_helper import get_categories, get_subcategories, get_quizzes, get_options, get_question_text, \
    save_answer, find_id_by_chat_id

router = Router()

user_quiz_data = {}


@router.message(F.text == "🧑‍💻 Testlar")
async def show_categories(msg: Message):
    categories = get_categories()

    builder = InlineKeyboardBuilder()
    for name, cat_id in categories:
        builder.button(text=name, callback_data=CategoryCallback(id=cat_id))
    builder.adjust(2)
    await msg.answer("Bo'limni tanlang:", reply_markup=builder.as_markup())


@router.callback_query(CategoryCallback.filter())
async def show_subcategories(callback: CallbackQuery, callback_data: CategoryCallback):
    subcategories = get_subcategories(callback_data.id)
    builder = InlineKeyboardBuilder()
    for name, sub_id in subcategories:
        builder.button(
            text=name,
            callback_data=SubcategoryCallback(id=sub_id, category=callback_data.id)
        )
    builder.button(
        text="⬅️ Ortga",
        callback_data=BackCallback(level=Level.CATEGORY.value)
    )
    builder.adjust(2)
    await callback.message.edit_text("Bo'lim ichidagi mavzular:", reply_markup=builder.as_markup())


@router.callback_query(SubcategoryCallback.filter())
async def show_quiz_start(callback: CallbackQuery, callback_data: SubcategoryCallback):
    quizzes = get_quizzes(callback_data.id)
    quizzes = random.sample(quizzes, min(5, len(quizzes)))  # new
    if not quizzes:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="⬅️ Ortga",
            callback_data=BackCallback(
                level=Level.SUBCATEGORY.value,
                category=callback_data.category
            )
        )
        await callback.message.edit_text(
            "Test topilmadi.",
            reply_markup=builder.as_markup()
        )
        return

    user_id = callback.from_user.id
    user_quiz_data[user_id] = {
        'subcategory': callback_data.id,
        'category': callback_data.category,
        'quizzes': quizzes,
        'current_index': 0,
        'correct_answers': 0,
        'user_answers': {}
    }

    builder = InlineKeyboardBuilder()
    builder.button(
        text="Testni boshlash 🚀",
        callback_data=QuizCallback(
            id=quizzes[0][1],
            subcategory=callback_data.id,
            category=callback_data.category
        )
    )
    builder.button(
        text="⬅️ Ortga",
        callback_data=BackCallback(
            level=Level.SUBCATEGORY.value,
            category=callback_data.category
        )
    )
    builder.adjust(1)
    await callback.message.edit_text(
        f"Test {len(quizzes)} ta savoldan iborat. Boshlaymizmi?",
        reply_markup=builder.as_markup()
    )


@router.callback_query(QuizCallback.filter())
async def show_question(callback: CallbackQuery, callback_data: QuizCallback):
    user_id = callback.from_user.id
    if user_id not in user_quiz_data:
        await callback.message.edit_text("Xatolik yuz berdi. Iltimos, testni qayta boshlang.")
        return

    quiz_data = user_quiz_data[user_id]
    quizzes = quiz_data['quizzes']
    current_index = quiz_data['current_index']

    # Agar yangi test boshlanayotgan bo'lsa
    if callback_data.id != quizzes[current_index][1]:
        current_index = next((i for i, (_, q_id) in enumerate(quizzes) if q_id == callback_data.id), 0)
        quiz_data['current_index'] = current_index

    question_text = get_question_text(callback_data.id)
    options = get_options(callback_data.id)
    options = random.sample(options, min(4, len(options)))  # new

    builder = InlineKeyboardBuilder()
    for text, option_id in options:  # new
        builder.button(
            text=text,
            callback_data=OptionCallback(
                id=option_id,  # new
                quiz=callback_data.id,
                subcategory=callback_data.subcategory,
                category=callback_data.category
            )
        )

    # Navigatsiya tugmalari
    if current_index == 0:
        builder.button(
            text="⬅️ Ortga",
            callback_data=BackCallback(
                level=Level.QUIZ_START.value,
                subcategory=callback_data.subcategory,
                category=callback_data.category
            )
        )
    else:
        builder.button(
            text="⬅️ Oldingi savol",
            callback_data=QuizCallback(
                id=quizzes[current_index - 1][1],
                subcategory=callback_data.subcategory,
                category=callback_data.category
            )
        )

    builder.adjust(2)
    await callback.message.edit_text(
        f"Savol {current_index + 1}/{len(quizzes)}:\n\n{question_text}",
        reply_markup=builder.as_markup()
    )


@router.callback_query(OptionCallback.filter())
async def process_answer(callback: CallbackQuery, callback_data: OptionCallback):
    user_chat_id = callback.from_user.id
    if user_chat_id not in user_quiz_data:
        await callback.message.edit_text("Xatolik yuz berdi. Iltimos, testni qayta boshlang.")
        return

    quiz_data = user_quiz_data[user_chat_id]
    quizzes = quiz_data['quizzes']
    current_index = quiz_data['current_index']
    quiz_id = quizzes[current_index][1]

    # Javobni tekshirish
    selected_option = get_options(quiz_id, callback_data.id)  # new
    is_correct = selected_option[1]

    # Javobni saqlash
    quiz_data['user_answers'][quiz_id] = callback_data.id
    user_id = find_id_by_chat_id(chat_id=user_chat_id)
    save_answer(user_id=user_id, quiz_id=quiz_id, option_id=callback_data.id)
    if is_correct:
        quiz_data['correct_answers'] += 1

    # Keyingi savolga o'tish
    if current_index + 1 < len(quizzes):
        quiz_data['current_index'] += 1
        next_quiz_id = quizzes[current_index + 1][1]
        await show_question(
            callback,
            QuizCallback(
                id=next_quiz_id,
                subcategory=callback_data.subcategory,
                category=callback_data.category
            )
        )
    else:
        # Test yakunlandi
        total_questions = len(quizzes)
        correct_answers = quiz_data['correct_answers']
        score = f"{correct_answers}/{total_questions}"

        builder = InlineKeyboardBuilder()
        builder.button(
            text="Testni qayta boshlash 🔄",
            callback_data=SubcategoryCallback(
                id=quiz_data['subcategory'],
                category=quiz_data['category']
            )
        )
        builder.button(
            text="Bosh menyu 🏠",
            callback_data=BackCallback(level=Level.CATEGORY.value)
        )
        builder.adjust(1)
        await callback.message.edit_text(
            f"Test yakunlandi! Natijangiz: {score}\n\nYana test yechmoqchimisiz?",
            reply_markup=builder.as_markup()
        )
        # Foydalanuvchi ma'lumotlarini tozalash
        del user_quiz_data[user_chat_id]


@router.callback_query(BackCallback.filter())
async def handle_back(callback: CallbackQuery, callback_data: BackCallback):
    level = Level(callback_data.level)

    if level == Level.CATEGORY:
        categories = get_categories()
        builder = InlineKeyboardBuilder()
        for name, cat_id in categories:
            builder.button(text=name, callback_data=CategoryCallback(id=cat_id))
        builder.adjust(2)
        await callback.message.edit_text("Bo'limni tanlang:", reply_markup=builder.as_markup())

    elif level == Level.SUBCATEGORY:
        subcategories = get_subcategories(callback_data.category)
        builder = InlineKeyboardBuilder()
        for name, sub_id in subcategories:
            builder.button(
                text=name,
                callback_data=SubcategoryCallback(id=sub_id, category=callback_data.category)
            )
        builder.button(
            text="⬅️ Ortga",
            callback_data=BackCallback(level=Level.CATEGORY.value)
        )
        builder.adjust(2)
        await callback.message.edit_text("Bo'lim ichidagi mavzular:", reply_markup=builder.as_markup())

    elif level == Level.QUIZ_START:
        user_id = callback.from_user.id
        if user_id in user_quiz_data:
            del user_quiz_data[user_id]
        quizzes = get_quizzes(callback_data.subcategory)
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Testni boshlash 🚀",
            callback_data=QuizCallback(
                id=quizzes[0][1],
                subcategory=callback_data.subcategory,
                category=callback_data.category
            )
        )
        builder.button(
            text="⬅️ Ortga",
            callback_data=BackCallback(
                level=Level.SUBCATEGORY.value,
                category=callback_data.category
            )
        )
        builder.adjust(1)
        await callback.message.edit_text(
            f"Test: {quizzes[0][0]}\n\nTest {len(quizzes)} ta savoldan iborat. Boshlaymizmi?",
            reply_markup=builder.as_markup()
        )