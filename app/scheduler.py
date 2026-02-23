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
    get_current_message_index,
    get_total_messages
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
    Вызывается планировщиком каждые N минут.
    """
    global bot
    
    if bot is None:
        logger.warning("Бот не инициализирован")
        return

    # Проверка рабочего времени
    if not is_work_time():
        logger.info(f"Вне рабочего времени ({WORK_HOURS_START}:00 - {WORK_HOURS_END}:00)")
        return

    # Получаем текущий индекс сообщения
    current_index = await get_current_message_index()
    total_messages = await get_total_messages()

    logger.info(f"Текущий индекс: {current_index}, всего сообщений: {total_messages}")

    # Проверяем, есть ли ещё сообщения
    if current_index > total_messages:
        logger.info("Все сообщения сценария уже отправлены")
        return

    # Получаем сообщение
    message_data = await get_message_by_index(current_index)
    if not message_data:
        logger.warning(f"Сообщение с индексом {current_index} не найдено")
        return

    # Получаем активных пользователей
    active_users = await get_active_users()
    if not active_users:
        logger.warning("Нет активных пользователей")
        return
    
    # Время отправки (одинаковое для всех)
    sent_at = datetime.now().isoformat()
    
    # Формируем текст сообщения
    message_text = f"📨 *Сообщение #{current_index}*\n\n"
    message_text += f"_{message_data.get('category', 'Общее')}_\n\n"
    message_text += message_data['text']
    
    # Отправляем всем активным пользователям
    sent_count = 0
    for user in active_users:
        try:
            await bot.send_message(
                chat_id=user['user_id'],
                text=message_text,
                parse_mode="Markdown"
            )
            
            # Логируем отправку
            await log_sent_message(
                user_id=user['user_id'],
                message_index=current_index,
                message_text=message_data['text'],
                sent_at=sent_at
            )
            sent_count += 1
            
        except Exception as e:
            logger.error(f"Ошибка отправки пользователю {user['user_id']}: {e}")

    logger.info(f"Сообщение #{current_index} отправлено {sent_count} пользователям")


def start_scheduler():
    """Запустить планировщик"""
    global scheduler
    scheduler = get_scheduler()
    
    # Добавляем задачу рассылки
    scheduler.add_job(
        send_training_messages,
        trigger=IntervalTrigger(minutes=MESSAGE_INTERVAL_MINUTES),
        id='training_messages',
        name='Рассылка тренировочных сообщений',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info(f"Планировщик запущен (интервал: {MESSAGE_INTERVAL_MINUTES} мин)")


def stop_scheduler():
    """Остановить планировщик"""
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown()
        print("⏹️ Планировщик остановлен")


async def send_first_message_now():
    """Отправить первое сообщение немедленно (для тестирования)"""
    await send_training_messages()
