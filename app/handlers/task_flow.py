from aiogram import types
from datetime import datetime, timedelta
from app.services.ai_service import ask_yandex_gpt
from app.services.scheduler import scheduler, send_reminder

async def handle_task(message: types.Message, bot):
    msg = await message.answer("🧠 Анализирую задачу...")
    ai_data = await ask_yandex_gpt(message.text)
    if not ai_data:
        await msg.edit_text("😔 Не смог распарсить. Попробуй иначе.")
        return
    task_name = ai_data.get("task_name", "Задача")
    hours = ai_data.get("estimated_hours", 2)
    steps = ai_data.get("steps", ["Сделать задачу"])
    reminder_text = ai_data.get("reminder_text", "Погнали!")
    steps_formatted = "\n".join([f"  {i+1}. {s}" for i, s in enumerate(steps)])
    response = (
        f"✅ **Задача:** {task_name}\n"
        f"⏱ **Оценка:** ~{hours} часов\n\n"
        f"📋 **План:**\n{steps_formatted}\n\n"
        f"💬 *{reminder_text}*"
    )
    await msg.edit_text(response, parse_mode="Markdown")
    run_date = datetime.now() + timedelta(seconds=10)
    scheduler.add_job(
        send_reminder, 'date', run_date=run_date,
        args=[bot, message.from_user.id, task_name, reminder_text]
    )

def register_handlers(dp):
    dp.message.register(handle_task)