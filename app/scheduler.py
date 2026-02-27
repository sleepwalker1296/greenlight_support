"""
Планировщик для автоматической рассылки сообщений
"""
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import pytz

logger = logging.getLogger(__name__)

from app.config import (
    MESSAGE_INTERVAL_MINUTES, 
    WORK_HOURS_START, 
    WORK_HOURS_END,
    TIMEZONE
)
from app.db import (
    get_active_users,
    get_message_by_index,
    log_sent_message,
    get_total_messages,
    get_user_last_message_time,
    get_user_next_message_index,
)

# Глобальная переменная для бота (будет установлена из main.py)
bot = None
scheduler = None


def set_bot(bot_instance):
    """Установить экземпляр бота для отправки сообщений"""
    global bot
    bot = bot_instance


def get_scheduler():
    """Получить экземпляр планировщика"""
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    return scheduler


def is_work_time() -> bool:
    """Проверить, находимся ли мы в рабочем окне"""
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    current_hour = now.hour
    return WORK_HOURS_START <= current_hour < WORK_HOURS_END


async def send_training_messages():
    """
    Основная функция рассылки сообщений.
    Вызывается каждую минуту, отправляет каждому пользователю
    следующее сообщение если прошло >= MESSAGE_INTERVAL_MINUTES с последнего.
    """
    global bot

    if bot is None:
        logger.warning("Бот не инициализирован")
        return

    # Проверка рабочего времени
    if not is_work_time():
        logger.info(f"Вне рабочего времени ({WORK_HOURS_START}:00 - {WORK_HOURS_END}:00)")
        return

    active_users = await get_active_users()
    if not active_users:
        return

    total_messages = await get_total_messages()
    now = datetime.now()

    for user in active_users:
        user_id = user['user_id']

        # Проверяем, прошло ли достаточно времени с последнего сообщения
        last_time = await get_user_last_message_time(user_id)
        if last_time is None:
            # Первое сообщение отправляет обработчик кнопки — пропускаем
            continue
        elapsed_minutes = (now - last_time).total_seconds() / 60
        if elapsed_minutes < MESSAGE_INTERVAL_MINUTES:
            continue

        # Определяем следующий индекс для этого пользователя
        next_index = await get_user_next_message_index(user_id)
        if next_index > total_messages:
            logger.info(f"Все сообщения отправлены пользователю {user_id}")
            continue

        message_data = await get_message_by_index(next_index)
        if not message_data:
            logger.warning(f"Сообщение {next_index} не найдено")
            continue

        message_text = f"📨 *Сообщение #{next_index}*\n\n"
        message_text += f"_{message_data.get('category', 'Общее')}_\n\n"
        message_text += message_data['text']

        sent_at = now.isoformat()
        try:
            await bot.send_message(
                chat_id=user_id,
                text=message_text,
                parse_mode="Markdown"
            )
            await log_sent_message(
                user_id=user_id,
                message_index=next_index,
                message_text=message_data['text'],
                sent_at=sent_at
            )
            logger.info(f"Сообщение #{next_index} отправлено пользователю {user_id}")
        except Exception as e:
            logger.error(f"Ошибка отправки пользователю {user_id}: {e}")


def start_scheduler():
    """Запустить планировщик"""
    global scheduler
    scheduler = get_scheduler()
    
    # Добавляем задачу рассылки
    scheduler.add_job(
        send_training_messages,
        trigger=IntervalTrigger(minutes=1),
        id='training_messages',
        name='Рассылка тренировочных сообщений',
        replace_existing=True
    )

    scheduler.start()
    logger.info(f"Планировщик запущен (проверка каждую минуту, интервал между сообщениями: {MESSAGE_INTERVAL_MINUTES} мин)")


def stop_scheduler():
    """Остановить планировщик"""
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown()
        print("⏹️ Планировщик остановлен")


async def send_first_message_now():
    """Отправить первое сообщение немедленно (для тестирования)"""
    await send_training_messages()
