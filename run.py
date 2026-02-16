"""
Скрипт запуска бота
"""
import sys
import os

# Добавляем корневую папку в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Запускаем бота
from app.main import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
