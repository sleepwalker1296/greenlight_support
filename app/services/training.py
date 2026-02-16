"""
Сервис управления тренировкой
"""
from typing import List, Dict, Optional
from datetime import datetime

from app.db import (
    get_active_users,
    get_current_message_index,
    get_total_messages,
    get_all_logs
)


async def get_training_status() -> Dict:
    """Получить текущий статус тренировки"""
    active_users = await get_active_users()
    current_index = await get_current_message_index()
    total_messages = await get_total_messages()
    
    return {
        "active_users_count": len(active_users),
        "active_users": active_users,
        "current_message_index": current_index,
        "total_messages": total_messages,
        "is_completed": current_index > total_messages,
        "progress_percent": min(100, round((current_index - 1) / total_messages * 100)) if total_messages > 0 else 0
    }


async def get_user_statistics(user_id: int) -> Dict:
    """Получить статистику конкретного пользователя"""
    logs = await get_all_logs()
    user_logs = [log for log in logs if log['user_id'] == user_id]
    
    total_received = len(user_logs)
    total_answered = sum(1 for log in user_logs if log.get('answer_text'))
    
    # Время ответов
    response_times = [log['response_time_sec'] for log in user_logs if log.get('response_time_sec')]
    
    avg_response_time = sum(response_times) // len(response_times) if response_times else 0
    min_response_time = min(response_times) if response_times else 0
    max_response_time = max(response_times) if response_times else 0
    
    return {
        "user_id": user_id,
        "total_received": total_received,
        "total_answered": total_answered,
        "unanswered": total_received - total_answered,
        "answer_rate": round(total_answered / total_received * 100) if total_received > 0 else 0,
        "avg_response_time_sec": avg_response_time,
        "min_response_time_sec": min_response_time,
        "max_response_time_sec": max_response_time
    }


async def get_overall_statistics() -> Dict:
    """Получить общую статистику по всем пользователям"""
    logs = await get_all_logs()
    active_users = await get_active_users()
    
    total_sent = len(logs)
    total_answered = sum(1 for log in logs if log.get('answer_text'))
    
    response_times = [log['response_time_sec'] for log in logs if log.get('response_time_sec')]
    avg_time = sum(response_times) // len(response_times) if response_times else 0
    
    # Группировка по пользователям
    users_stats = {}
    for log in logs:
        uid = log['user_id']
        if uid not in users_stats:
            users_stats[uid] = {"received": 0, "answered": 0, "times": []}
        users_stats[uid]["received"] += 1
        if log.get('answer_text'):
            users_stats[uid]["answered"] += 1
        if log.get('response_time_sec'):
            users_stats[uid]["times"].append(log['response_time_sec'])
    
    return {
        "active_users_count": len(active_users),
        "total_participants": len(users_stats),
        "total_messages_sent": total_sent,
        "total_answers": total_answered,
        "unanswered": total_sent - total_answered,
        "avg_response_time_sec": avg_time,
        "answer_rate": round(total_answered / total_sent * 100) if total_sent > 0 else 0
    }


def format_time(seconds: int) -> str:
    """Форматировать секунды в читаемый вид"""
    if seconds < 60:
        return f"{seconds} сек"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes} мин {secs} сек"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours} ч {minutes} мин"
