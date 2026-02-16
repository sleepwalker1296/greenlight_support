"""
Сервис экспорта данных в CSV
"""
import csv
import os
from datetime import datetime
from typing import Optional

from app.db import get_all_logs


def format_datetime(iso_string: str) -> tuple:
    """Форматировать ISO дату в русский формат (дата, время)"""
    if not iso_string:
        return "", ""
    try:
        dt = datetime.fromisoformat(iso_string)
        date_str = dt.strftime("%d.%m.%Y")
        time_str = dt.strftime("%H:%M")
        return date_str, time_str
    except:
        return "", ""


async def export_logs_to_csv() -> Optional[str]:
    """
    Экспорт логов в CSV файл.
    Возвращает путь к файлу или None, если нет данных.
    """
    logs = await get_all_logs()
    
    if not logs:
        return None
    
    # Создаём папку для экспорта, если её нет
    export_dir = "exports"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    # Генерируем имя файла с датой
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"training_results_{timestamp}.csv"
    filepath = os.path.join(export_dir, filename)
    
    # Определяем столбцы (на русском)
    fieldnames = [
        '№',
        'ID пользователя',
        'Ник Telegram',
        'Имя',
        '№ сообщения',
        'Текст сообщения',
        'Дата отправки',
        'Время отправки',
        'Ответ пользователя',
        'Дата ответа',
        'Время ответа',
        'Время реакции (сек)',
        'Время реакции'
    ]
    
    # Записываем в CSV
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(fieldnames)
        
        for log in logs:
            # Форматируем время ответа
            response_time = log.get('response_time_sec')
            if response_time:
                if response_time < 60:
                    formatted_time = f"{response_time} сек"
                elif response_time < 3600:
                    formatted_time = f"{response_time // 60} мин {response_time % 60} сек"
                else:
                    hours = response_time // 3600
                    minutes = (response_time % 3600) // 60
                    formatted_time = f"{hours} ч {minutes} мин"
            else:
                formatted_time = ""
            
            # Форматируем даты
            sent_date, sent_time = format_datetime(log.get('sent_at', ''))
            answered_date, answered_time = format_datetime(log.get('answered_at', ''))
            
            # Добавляем @ к нику если его нет
            username = log.get('username', '')
            if username and not username.startswith('@'):
                username = f"@{username}"
            
            row = [
                log['id'],
                log['user_id'],
                username,
                log.get('full_name', ''),
                log['message_index'],
                log.get('message_text', ''),
                sent_date,
                sent_time,
                log.get('answer_text', ''),
                answered_date,
                answered_time,
                response_time or '',
                formatted_time
            ]
            writer.writerow(row)
    
    print(f"✅ Экспортировано {len(logs)} записей в {filepath}")
    return filepath


async def export_user_report(user_id: int, username: str = "", full_name: str = "") -> Optional[str]:
    """Экспорт отчёта по конкретному пользователю"""
    logs = await get_all_logs()
    user_logs = [log for log in logs if log['user_id'] == user_id]
    
    if not user_logs:
        return None
    
    export_dir = "exports"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Используем username или ID для имени файла
    safe_name = username.replace('@', '') if username else str(user_id)
    filename = f"user_{safe_name}_{timestamp}.csv"
    filepath = os.path.join(export_dir, filename)
    
    # Заголовки на русском
    fieldnames = [
        '№ сообщения',
        'Текст сообщения',
        'Дата отправки',
        'Время отправки',
        'Ответ пользователя',
        'Дата ответа',
        'Время ответа',
        'Время реакции (сек)',
        'Время реакции'
    ]
    
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(fieldnames)
        
        for log in user_logs:
            # Форматируем время ответа
            response_time = log.get('response_time_sec')
            if response_time:
                if response_time < 60:
                    formatted_time = f"{response_time} сек"
                elif response_time < 3600:
                    formatted_time = f"{response_time // 60} мин {response_time % 60} сек"
                else:
                    hours = response_time // 3600
                    minutes = (response_time % 3600) // 60
                    formatted_time = f"{hours} ч {minutes} мин"
            else:
                formatted_time = ""
            
            # Форматируем даты
            sent_date, sent_time = format_datetime(log.get('sent_at', ''))
            answered_date, answered_time = format_datetime(log.get('answered_at', ''))
            
            row = [
                log['message_index'],
                log.get('message_text', ''),
                sent_date,
                sent_time,
                log.get('answer_text', ''),
                answered_date,
                answered_time,
                response_time or '',
                formatted_time
            ]
            writer.writerow(row)
    
    print(f"✅ Экспортировано {len(user_logs)} записей пользователя {user_id} в {filepath}")
    return filepath
