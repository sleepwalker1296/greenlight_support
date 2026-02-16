"""
Обработчик ответов пользователей
"""
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message

from app.db import get_user, get_last_unanswered_log, save_answer

router = Router()


@router.message(F.text)
async def handle_user_answer(message: Message):
    """
    Обработка любого текстового сообщения как ответа на тренировочный вопрос
    """
    user_id = message.from_user.id
    answer_text = message.text
    
    # Игнорируем команды и кнопки меню
    if answer_text.startswith('/'):
        return
    if answer_text in ["▶️ Начать тренировку", "📄 Скрипты", "⛔ Завершить"]:
        return
    
    # Проверяем, активна ли тренировка у пользователя
    user = await get_user(user_id)
    if not user or not user.get('is_active'):
        await message.answer(
            "ℹ️ Сначала начни тренировку!\n"
            "Нажми «▶️ Начать тренировку»"
        )
        return
    
    # Ищем последний неотвеченный вопрос
    last_log = await get_last_unanswered_log(user_id)
    
    if not last_log:
        await message.answer(
            "⏳ Пока нет новых сообщений для ответа.\n"
            "Жди следующего сообщения от «клиента»!"
        )
        return
    
    # Вычисляем время ответа
    sent_at = datetime.fromisoformat(last_log['sent_at'])
    answered_at = datetime.now()
    response_time_sec = int((answered_at - sent_at).total_seconds())
    
    # Сохраняем ответ
    await save_answer(
        log_id=last_log['id'],
        answer_text=answer_text,
        answered_at=answered_at.isoformat(),
        response_time_sec=response_time_sec
    )
    
    # Форматируем время для отображения
    if response_time_sec < 60:
        time_str = f"{response_time_sec} сек"
    elif response_time_sec < 3600:
        minutes = response_time_sec // 60
        seconds = response_time_sec % 60
        time_str = f"{minutes} мин {seconds} сек"
    else:
        hours = response_time_sec // 3600
        minutes = (response_time_sec % 3600) // 60
        time_str = f"{hours} ч {minutes} мин"
    
    # Подтверждаем получение ответа
    await message.answer(
        f"✅ Ответ записан!\n\n"
        f"⏱ Время ответа: *{time_str}*\n\n"
        f"Жди следующего сообщения от «клиента» 📨",
        parse_mode="Markdown"
    )
