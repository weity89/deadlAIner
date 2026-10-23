from aiogram import types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta
from app.services.ai_service import ask_gigachat
from app.services.scheduler import scheduler, send_reminder
from app.database import load_tasks, save_tasks
import json

# Временная память для активных задач (в будущем заменим на БД)
user_active_tasks = {}


async def handle_task(message: types.Message, bot):
    msg = await message.answer("🧠 Анализирую задачу...")

    ai_data = await ask_gigachat(message.text)

    if not ai_data:
        await msg.edit_text("😔 Не смог распарсить. Попробуй написать проще.")
        return

    task_name = ai_data.get("task_name", "Задача")
    hours = ai_data.get("estimated_hours", 2)
    steps = ai_data.get("steps", ["Сделать задачу"])
    reminder_text = ai_data.get("reminder_text", "Погнали!")

    # === СОХРАНЕНИЕ ЗАДАЧИ В БАЗУ ===
    user_id = str(message.from_user.id)
    all_tasks = load_tasks()
    if user_id not in all_tasks:
        all_tasks[user_id] = []

    all_tasks[user_id].append({
        "name": task_name,
        "hours": hours,
        "deadline": ai_data.get("deadline", "Не указан"),  # <-- ДОБАВИЛИ ДАТУ
        "steps": steps,
        "details": ""
    })
    save_tasks(all_tasks)
    # =================================

    steps_formatted = "\n".join([f"  {i + 1}. {s}" for i, s in enumerate(steps)])

    task_name = ai_data.get("task_name", "Задача")
    hours = ai_data.get("estimated_hours", 2)
    steps = ai_data.get("steps", ["Сделать задачу"])
    reminder_text = ai_data.get("reminder_text", "Погнали!")

    # Сохраняем задачу в память
    user_active_tasks[message.from_user.id] = {"name": task_name, "est_hours": hours}

    steps_formatted = "\n".join([f"  {i + 1}. {s}" for i, s in enumerate(steps)])

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Задача выполнена", callback_data="task_done")

    response = (
        f"✅ **Задача:** {task_name}\n"
        f"⏱ **Оценка:** ~{hours} часов\n\n"
        f"📋 **План:**\n{steps_formatted}\n\n"
        f"💬 *{reminder_text}*"
    )

    await msg.edit_text(response, parse_mode="Markdown", reply_markup=builder.as_markup())

    # Тестовое напоминание через 10 секунд
    run_date = datetime.now() + timedelta(seconds=10)
    scheduler.add_job(
        send_reminder, 'date', run_date=run_date,
        args=[bot, message.from_user.id, task_name, reminder_text]
    )

async def handle_done(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    task = user_active_tasks.get(user_id)

    if task:
        # Здесь в будущем будет запись реального времени
        await callback.message.edit_text(
            f"🎉 Отлично! Задача «{task['name']}» выполнена.\n"
            f"Я запомнил, что на неё ушло [X] часов. В следующий раз я точнее оценю время!\n\n"
            f"*(В MVP мы только собираем данные для обучения)*"
        )
        del user_active_tasks[user_id]
    else:
        await callback.answer("Задача не найдена.", show_alert=True)

    await callback.answer()

def register_handlers(dp):
    dp.message.register(handle_task)
    dp.callback_query.register(handle_done, F.data == "task_done")