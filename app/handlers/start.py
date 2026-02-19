"""
Обработчик команды /start и основных кнопок
"""
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

from app.db import add_user, set_user_active, get_user, get_all_messages_from_db

router = Router()


def get_main_keyboard():
    """Создать основную клавиатуру"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="▶️ Начать тренировку")],
            [KeyboardButton(text="📄 Скрипты")],
            [KeyboardButton(text="⛔ Завершить")]
        ],
        resize_keyboard=True
    )
    return keyboard


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    user = message.from_user
    
    # Добавляем/обновляем пользователя в БД
    await add_user(
        user_id=user.id,
        username=user.username or "",
        full_name=user.full_name or ""
    )
    
    welcome_text = (
        f"👋 Привет, *{user.first_name}*!\n\n"
        "Я бот-тренажёр для отработки навыков поддержки клиентов.\n\n"
        "🎯 *Как это работает:*\n"
        "1. Нажми «▶️ Начать тренировку»\n"
        "2. Тебе будут приходить сообщения от «клиентов»\n"
        "3. Отвечай на них как настоящий специалист поддержки\n"
        "4. Твои ответы и время реакции будут записаны\n\n"
        "📊 Результаты можно экспортировать для анализа.\n\n"
        "Готов начать?"
    )
    
    await message.answer(
        welcome_text, 
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )


@router.message(F.text == "▶️ Начать тренировку")
async def start_training(message: Message):
    """Начало тренировки"""
    user_id = message.from_user.id
    
    # Проверяем, не активна ли уже тренировка
    user = await get_user(user_id)
    if user and user.get('is_active'):
        await message.answer(
            "⚠️ Тренировка уже активна!\n"
            "Сообщения будут приходить автоматически.\n\n"
            "Для завершения нажми «⛔ Завершить»"
        )
        return
    
    # Активируем пользователя
    await set_user_active(user_id, True)
    
    await message.answer(
        "✅ *Тренировка началась!*\n\n"
        "📨 Сообщения от «клиентов» будут приходить автоматически.\n"
        "⏰ Интервал между сообщениями: ~ 32 минуты\n"
        "🕐 Рабочее время: 10:00 - 22:00 (45 вопросов за 2 дня)\n\n"
        "Отвечай на каждое сообщение текстом - "
        "я запишу твой ответ и время реакции.\n\n"
        "Удачи! 💪",
        parse_mode="Markdown"
    )


@router.message(F.text == "📄 Скрипты")
async def show_scripts(message: Message):
    """Показать все скрипты/сообщения"""
    messages = await get_all_messages_from_db()
    
    if not messages:
        await message.answer("📭 Сценарий пока не загружен.")
        return
    
    # Формируем список сообщений
    text = "📄 *Сценарий тренировки:*\n\n"
    
    for msg in messages[:10]:  # Показываем первые 10
        text += f"*{msg['message_index']}.* _{msg.get('category', 'Общее')}_\n"
        # Обрезаем длинные сообщения
        preview = msg['text'][:100] + "..." if len(msg['text']) > 100 else msg['text']
        text += f"{preview}\n\n"
    
    if len(messages) > 10:
        text += f"_...и ещё {len(messages) - 10} сообщений_"
    
    await message.answer(text, parse_mode="Markdown")


@router.message(F.text == "⛔ Завершить")
async def stop_training(message: Message):
    """Завершение тренировки"""
    user_id = message.from_user.id
    
    # Проверяем статус
    user = await get_user(user_id)
    if not user or not user.get('is_active'):
        await message.answer(
            "ℹ️ Тренировка не активна.\n"
            "Нажми «▶️ Начать тренировку» для старта."
        )
        return
    
    # Деактивируем пользователя
    await set_user_active(user_id, False)
    
    await message.answer(
        "⛔ *Тренировка завершена!*\n\n"
        "Спасибо за участие! 👏\n"
        "Твои результаты сохранены.\n\n"
        "Хочешь начать заново? Нажми «▶️ Начать тренировку»",
        parse_mode="Markdown"
    )
