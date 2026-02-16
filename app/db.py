"""
Модуль работы с базой данных SQLite
"""
import aiosqlite
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.config import DATABASE_PATH


async def get_connection():
    """Получить соединение с БД"""
    return await aiosqlite.connect(DATABASE_PATH)


async def init_db():
    """Инициализация базы данных - создание таблиц"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Таблица пользователей
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                is_active INTEGER DEFAULT 0,
                training_start_time TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица сообщений сценария
        await db.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_index INTEGER UNIQUE,
                text TEXT NOT NULL,
                category TEXT,
                difficulty TEXT
            )
        ''')
        
        # Таблица логов (отправленные сообщения и ответы)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message_index INTEGER,
                message_text TEXT,
                sent_at TEXT,
                answer_text TEXT,
                answered_at TEXT,
                response_time_sec INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (message_index) REFERENCES messages(message_index)
            )
        ''')
        
        await db.commit()
        print("✅ База данных инициализирована")


async def load_messages_to_db(messages: List[Dict]):
    """Загрузка сценария сообщений в БД"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Очистка таблицы сообщений
        await db.execute('DELETE FROM messages')
        
        # Загрузка новых сообщений
        for msg in messages:
            await db.execute('''
                INSERT INTO messages (message_index, text, category, difficulty)
                VALUES (?, ?, ?, ?)
            ''', (msg['index'], msg['text'], msg.get('category', ''), msg.get('difficulty', '')))
        
        await db.commit()
        print(f"✅ Загружено {len(messages)} сообщений в БД")


# ===== Функции для работы с пользователями =====

async def add_user(user_id: int, username: str, full_name: str):
    """Добавить или обновить пользователя"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''
            INSERT OR REPLACE INTO users (user_id, username, full_name, created_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, full_name, datetime.now().isoformat()))
        await db.commit()


async def set_user_active(user_id: int, is_active: bool):
    """Установить статус активности пользователя"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        training_start = datetime.now().isoformat() if is_active else None
        await db.execute('''
            UPDATE users 
            SET is_active = ?, training_start_time = ?
            WHERE user_id = ?
        ''', (1 if is_active else 0, training_start, user_id))
        await db.commit()


async def get_active_users() -> List[Dict]:
    """Получить всех активных пользователей"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('''
            SELECT user_id, username, full_name, training_start_time
            FROM users WHERE is_active = 1
        ''')
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_all_users() -> List[Dict]:
    """Получить всех пользователей"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('''
            SELECT user_id, username, full_name, is_active, training_start_time, created_at
            FROM users
        ''')
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_user(user_id: int) -> Optional[Dict]:
    """Получить пользователя по ID"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            'SELECT * FROM users WHERE user_id = ?', (user_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


# ===== Функции для работы с сообщениями =====

async def get_message_by_index(index: int) -> Optional[Dict]:
    """Получить сообщение по индексу"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            'SELECT * FROM messages WHERE message_index = ?', (index,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_total_messages() -> int:
    """Получить общее количество сообщений"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute('SELECT COUNT(*) FROM messages')
        row = await cursor.fetchone()
        return row[0] if row else 0


async def get_all_messages_from_db() -> List[Dict]:
    """Получить все сообщения из БД"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            'SELECT * FROM messages ORDER BY message_index'
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


# ===== Функции для работы с логами =====

async def log_sent_message(user_id: int, message_index: int, message_text: str, sent_at: str):
    """Записать отправленное сообщение в лог"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''
            INSERT INTO logs (user_id, message_index, message_text, sent_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, message_index, message_text, sent_at))
        await db.commit()


async def get_last_unanswered_log(user_id: int) -> Optional[Dict]:
    """Получить последний лог без ответа для пользователя"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('''
            SELECT * FROM logs 
            WHERE user_id = ? AND answer_text IS NULL
            ORDER BY sent_at DESC
            LIMIT 1
        ''', (user_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def save_answer(log_id: int, answer_text: str, answered_at: str, response_time_sec: int):
    """Сохранить ответ пользователя"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''
            UPDATE logs 
            SET answer_text = ?, answered_at = ?, response_time_sec = ?
            WHERE id = ?
        ''', (answer_text, answered_at, response_time_sec, log_id))
        await db.commit()


async def get_all_logs() -> List[Dict]:
    """Получить все логи"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('''
            SELECT l.*, u.username, u.full_name
            FROM logs l
            LEFT JOIN users u ON l.user_id = u.user_id
            ORDER BY l.sent_at
        ''')
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_current_message_index() -> int:
    """Получить текущий индекс сообщения (последний отправленный + 1)"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute('''
            SELECT MAX(message_index) FROM logs
        ''')
        row = await cursor.fetchone()
        if row and row[0]:
            return row[0] + 1
        return 1  # Начинаем с первого сообщения


async def reset_training():
    """Сбросить всю тренировку"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Деактивировать всех пользователей
        await db.execute('UPDATE users SET is_active = 0, training_start_time = NULL')
        # Очистить логи
        await db.execute('DELETE FROM logs')
        await db.commit()
        print("✅ Тренировка сброшена")
