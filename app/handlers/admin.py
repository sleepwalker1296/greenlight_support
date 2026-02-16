"""
Админские команды
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import Command

from app.config import ADMIN_ID
from app.db import get_all_users, reset_training, get_all_logs, get_user
from app.services.export import export_logs_to_csv, export_user_report

router = Router()


def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь админом"""
    return user_id == ADMIN_ID


def get_admin_keyboard():
    """Создать админскую клавиатуру"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Экспорт", callback_data="admin_export")],
        [InlineKeyboardButton(text="📈 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📤 Отправить сейчас", callback_data="admin_send_now")],
        [InlineKeyboardButton(text="🔄 Сбросить тренировку", callback_data="admin_reset")],
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="admin_close")]
    ])
    return keyboard


async def get_export_keyboard():
    """Создать клавиатуру для экспорта"""
    users = await get_all_users()
    
    buttons = []
    
    # Кнопка "Скачать всё"
    buttons.append([InlineKeyboardButton(text="📥 Скачать всё", callback_data="export_all")])
    
    # Кнопки для каждого пользователя
    for user in users:
        username = f"@{user['username']}" if user.get('username') else ""
        name = user.get('full_name', 'Пользователь')
        display = f"{name} {username}".strip()
        
        buttons.append([
            InlineKeyboardButton(
                text=f"👤 {display}",
                callback_data=f"export_user_{user['user_id']}"
            )
        ])
    
    # Кнопки навигации
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="admin_back")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(Command("export"))
async def cmd_export(message: Message):
    """Экспорт логов в CSV - показать меню выбора"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Эта команда доступна только администратору.")
        return
    
    users = await get_all_users()
    if not users:
        await message.answer("👤 Пользователей пока нет.")
        return
    
    keyboard = await get_export_keyboard()
    await message.answer(
        "📊 Выберите что экспортировать:",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "export_all")
async def callback_export_all(callback: CallbackQuery):
    """Экспорт всех логов"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    await callback.message.edit_text("📊 Формирую полный отчёт...")
    
    try:
        file_path = await export_logs_to_csv()
        
        if file_path:
            document = FSInputFile(file_path)
            await callback.message.answer_document(
                document=document,
                caption="📊 Экспорт всех результатов тренировки"
            )
            await callback.message.delete()
        else:
            await callback.message.edit_text("📭 Нет данных для экспорта.")
            
    except Exception as e:
        await callback.message.edit_text(f"❌ Ошибка экспорта: {e}")
    
    await callback.answer()


@router.callback_query(F.data.startswith("export_user_"))
async def callback_export_user(callback: CallbackQuery):
    """Экспорт логов конкретного пользователя"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    user_id = int(callback.data.replace("export_user_", ""))
    user = await get_user(user_id)
    
    if not user:
        await callback.message.edit_text(f"❌ Пользователь не найден.")
        await callback.answer()
        return
    
    await callback.message.edit_text(f"📊 Формирую отчёт для {user.get('full_name', 'пользователя')}...")
    
    try:
        file_path = await export_user_report(
            user_id=user_id,
            username=user.get('username', ''),
            full_name=user.get('full_name', '')
        )
        
        if file_path:
            document = FSInputFile(file_path)
            name = user.get('full_name', '')
            await callback.message.answer_document(
                document=document,
                caption=f"📊 Диалог с {name}"
            )
            await callback.message.delete()
        else:
            await callback.message.edit_text(f"📭 Нет данных для этого пользователя.")
            
    except Exception as e:
        await callback.message.edit_text(f"❌ Ошибка экспорта: {e}")
    
    await callback.answer()


@router.callback_query(F.data == "export_cancel")
async def callback_export_cancel(callback: CallbackQuery):
    """Отмена экспорта"""
    await callback.message.delete()
    await callback.answer("Отменено")


# ===== Админ-панель с кнопками =====

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Показать админ-панель"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Эта команда доступна только администратору.")
        return
    
    await message.answer(
        "🔧 Панель администратора",
        reply_markup=get_admin_keyboard()
    )


@router.callback_query(F.data == "admin_export")
async def callback_admin_export(callback: CallbackQuery):
    """Открыть меню экспорта"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    users = await get_all_users()
    if not users:
        await callback.message.edit_text("👤 Пользователей пока нет.")
        await callback.answer()
        return
    
    keyboard = await get_export_keyboard()
    await callback.message.edit_text(
        "📊 Выберите что экспортировать:",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "admin_stats")
async def callback_admin_stats(callback: CallbackQuery):
    """Показать статистику"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    logs = await get_all_logs()
    users = await get_all_users()
    
    total_sent = len(logs)
    total_answered = sum(1 for log in logs if log.get('answer_text'))
    
    response_times = [log['response_time_sec'] for log in logs if log.get('response_time_sec')]
    avg_time = sum(response_times) // len(response_times) if response_times else 0
    
    if avg_time < 60:
        avg_time_str = f"{avg_time} сек"
    else:
        avg_time_str = f"{avg_time // 60} мин {avg_time % 60} сек"
    
    text = (
        "📊 Статистика тренировки:\n\n"
        f"👥 Пользователей: {len(users)}\n"
        f"🟢 Активных: {sum(1 for u in users if u.get('is_active'))}\n\n"
        f"📨 Отправлено сообщений: {total_sent}\n"
        f"✅ Получено ответов: {total_answered}\n"
        f"📝 Без ответа: {total_sent - total_answered}\n\n"
        f"⏱ Среднее время ответа: {avg_time_str}"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_back")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "admin_send_now")
async def callback_admin_send_now(callback: CallbackQuery):
    """Отправить сообщение сейчас"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    from app.scheduler import send_training_messages
    
    await callback.message.edit_text("📤 Отправляю сообщение...")
    await send_training_messages()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_back")]
    ])
    
    await callback.message.edit_text("✅ Сообщение отправлено!", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "admin_reset")
async def callback_admin_reset(callback: CallbackQuery):
    """Подтверждение сброса"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, сбросить", callback_data="admin_reset_confirm")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_back")]
    ])
    
    await callback.message.edit_text(
        "⚠️ Вы уверены?\n\n"
        "Это действие:\n"
        "• Деактивирует всех пользователей\n"
        "• Очистит все логи\n"
        "• Сценарий начнётся сначала",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "admin_reset_confirm")
async def callback_admin_reset_confirm(callback: CallbackQuery):
    """Подтверждённый сброс"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    await reset_training()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_back")]
    ])
    
    await callback.message.edit_text(
        "🔄 Тренировка сброшена!\n\n"
        "• Все пользователи деактивированы\n"
        "• Логи очищены\n"
        "• Сценарий начнётся с начала",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "admin_back")
async def callback_admin_back(callback: CallbackQuery):
    """Вернуться в админ-панель"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🔧 Панель администратора",
        reply_markup=get_admin_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_close")
async def callback_admin_close(callback: CallbackQuery):
    """Закрыть админ-панель"""
    await callback.message.delete()
    await callback.answer()


@router.message(Command("export_user"))
async def cmd_export_user(message: Message):
    """Экспорт логов конкретного пользователя"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Эта команда доступна только администратору.")
        return
    
    # Получаем аргумент команды (user_id)
    args = message.text.split()
    if len(args) < 2:
        # Показываем список пользователей для выбора
        users = await get_all_users()
        if not users:
            await message.answer("👤 Пользователей пока нет.")
            return
        
        text = "📤 Экспорт по пользователю\n\n"
        text += "Используйте: /export_user <ID>\n\n"
        text += "Доступные пользователи:\n"
        
        for user in users:
            username = f"@{user['username']}" if user.get('username') else "—"
            text += f"• {user['full_name']} ({username})\n"
            text += f"  ID: {user['user_id']}\n"
        
        await message.answer(text)
        return
    
    try:
        user_id = int(args[1])
    except ValueError:
        await message.answer("❌ Неверный формат ID. Используйте число.")
        return
    
    # Проверяем существование пользователя
    user = await get_user(user_id)
    if not user:
        await message.answer(f"❌ Пользователь с ID {user_id} не найден.")
        return
    
    await message.answer(f"📊 Формирую отчёт для {user.get('full_name', 'пользователя')}...")
    
    try:
        file_path = await export_user_report(
            user_id=user_id,
            username=user.get('username', ''),
            full_name=user.get('full_name', '')
        )
        
        if file_path:
            from aiogram.types import FSInputFile
            document = FSInputFile(file_path)
            
            username_display = f"@{user['username']}" if user.get('username') else str(user_id)
            await message.answer_document(
                document=document,
                caption=f"📊 Диалог с {user.get('full_name', '')} ({username_display})"
            )
        else:
            await message.answer(f"📭 Нет данных для пользователя {user_id}.")
            
    except Exception as e:
        await message.answer(f"❌ Ошибка экспорта: {e}")


@router.message(Command("reset"))
async def cmd_reset(message: Message):
    """Сброс тренировки"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Эта команда доступна только администратору.")
        return
    
    await reset_training()
    await message.answer(
        "🔄 *Тренировка сброшена!*\n\n"
        "• Все пользователи деактивированы\n"
        "• Логи очищены\n"
        "• Сценарий начнётся с начала",
        parse_mode="Markdown"
    )


@router.message(Command("users"))
async def cmd_users(message: Message):
    """Список пользователей"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Эта команда доступна только администратору.")
        return
    
    users = await get_all_users()
    
    if not users:
        await message.answer("👤 Пользователей пока нет.")
        return
    
    text = "👥 *Пользователи:*\n\n"
    
    for user in users:
        status = "🟢" if user.get('is_active') else "⚪"
        username = f"@{user['username']}" if user.get('username') else "—"
        text += f"{status} {user['full_name']} ({username})\n"
        text += f"   ID: `{user['user_id']}`\n\n"
    
    active_count = sum(1 for u in users if u.get('is_active'))
    text += f"_Всего: {len(users)} | Активных: {active_count}_"
    
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Статистика тренировки"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Эта команда доступна только администратору.")
        return
    
    logs = await get_all_logs()
    users = await get_all_users()
    
    total_sent = len(logs)
    total_answered = sum(1 for log in logs if log.get('answer_text'))
    
    # Среднее время ответа
    response_times = [log['response_time_sec'] for log in logs if log.get('response_time_sec')]
    avg_time = sum(response_times) // len(response_times) if response_times else 0
    
    if avg_time < 60:
        avg_time_str = f"{avg_time} сек"
    else:
        avg_time_str = f"{avg_time // 60} мин {avg_time % 60} сек"
    
    text = (
        "📊 *Статистика тренировки:*\n\n"
        f"👥 Пользователей: {len(users)}\n"
        f"🟢 Активных: {sum(1 for u in users if u.get('is_active'))}\n\n"
        f"📨 Отправлено сообщений: {total_sent}\n"
        f"✅ Получено ответов: {total_answered}\n"
        f"📝 Без ответа: {total_sent - total_answered}\n\n"
        f"⏱ Среднее время ответа: {avg_time_str}"
    )
    
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("send_now"))
async def cmd_send_now(message: Message):
    """Отправить сообщение прямо сейчас (для тестирования)"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Эта команда доступна только администратору.")
        return
    
    from app.scheduler import send_training_messages
    
    await message.answer("📤 Отправляю сообщение...")
    await send_training_messages()
    await message.answer("✅ Готово!")


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Помощь по командам"""
    if not is_admin(message.from_user.id):
        await message.answer(
            "ℹ️ *Доступные команды:*\n\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать это сообщение",
            parse_mode="Markdown"
        )
        return
    
    await message.answer(
        "🔧 *Админ-команды:*\n\n"
        "/export - Экспорт всех логов в CSV\n"
        "/export\_user - Экспорт диалога с пользователем\n"
        "/reset - Сброс тренировки\n"
        "/users - Список пользователей\n"
        "/stats - Статистика\n"
        "/send\_now - Отправить сообщение сейчас\n"
        "/help - Это сообщение",
        parse_mode="Markdown"
    )
