"""
Конфигурация бота
"""
import os

# Токен бота от @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "8564179994:AAEoFdu78Tcll0rgtwWah_Kcx-R_Zyx-5gc")

# ID администратора (можно получить через @userinfobot)
ADMIN_ID = int(os.getenv("ADMIN_ID", "1015433406"))

# Интервал между сообщениями в минутах
MESSAGE_INTERVAL_MINUTES = 40

# Рабочее окно (часы, когда бот отправляет сообщения)
WORK_HOURS_START = 10  # С 10:00
WORK_HOURS_END = 20    # До 20:00

# Путь к базе данных
DATABASE_PATH = "trainer.db"

# Часовой пояс
TIMEZONE = "Europe/Moscow"
