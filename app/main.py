"""
Главный файл бота - точка входа
"""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from app.config import BOT_TOKEN
from app.db import init_db, load_messages_to_db
from app.data.messages import get_all_messages
from app.scheduler import set_bot, start_scheduler, stop_scheduler

# Импорт роутеров
from app.handlers import start, answers, admin

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    logger.info("🚀 Бот запускается...")
    
    # Инициализация БД
    await init_db()
    
    # Загрузка сценария сообщений
    messages = get_all_messages()
    await load_messages_to_db(messages)
    
    # Установка бота для планировщика
    set_bot(bot)
    
    # Запуск планировщика
    start_scheduler()
    
    logger.info("✅ Бот успешно запущен!")


async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    logger.info("⏹️ Бот останавливается...")
    
    # Остановка планировщика
    stop_scheduler()
    
    logger.info("👋 Бот остановлен")


async def main():
    """Главная функция запуска"""
    
    # Проверка токена
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ Укажите BOT_TOKEN в config.py или переменных окружения!")
        sys.exit(1)
    
    # Создание бота
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    
    # Создание диспетчера
    dp = Dispatcher()
    
    # Регистрация роутеров
    # Важно: admin должен быть перед answers, чтобы команды обрабатывались первыми
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(answers.router)  # Должен быть последним (ловит все текстовые сообщения)
    
    # Регистрация обработчиков жизненного цикла
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Запуск поллинга
    try:
        logger.info("🤖 Запуск polling...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен пользователем")
