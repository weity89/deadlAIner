import re
from aiogram import types
from aiogram.filters import Command
from app.database import load_tasks, save_tasks, load_busy, save_busy
from app.services.ai_service import ask_gigachat


async def cmd_start(message: types.Message):
    welcome_text = (
        "✈️ **Добро пожаловать в deadlAIner!**\n\n"
        "Я твой личный AI-штурман.\n"
        "Напиши задачу как думаешь (например: «Лаба по ООП до пятницы»), "
        "а я оценю время и разобью на этапы! 🚀\n\n"
        "**Доступные команды:**\n"
        "/list — посмотреть все задачи\n"
        "/busy — указать время, когда ты занят (сон/учеба)"
    )
    await message.answer(welcome_text, parse_mode="Markdown")

async def cmd_info(message: types.Message):
    user_id = str(message.from_user.id)
    text = message.text.replace("/info", "").strip()

    # Ищем номер задачи в начале текста
    match = re.match(r'^(\d+)\s*(.*)', text, re.DOTALL)
    if not match:
        await message.answer("Напиши так: `/info 1 Текст условия задачи...`", parse_mode="Markdown")
        return

    task_index = int(match.group(1)) - 1  # Вычитаем 1, т.к. индексы с 0
    task_details = match.group(2).strip()

    all_tasks = load_tasks()
    user_tasks = all_tasks.get(user_id, [])

    if task_index < 0 or task_index >= len(user_tasks):
        await message.answer("❌ Задачи с таким номером нет. Проверь `/list`.")
        return

    task = user_tasks[task_index]

    await message.answer(f"🧠 Анализирую условие для задачи «{task['name']}»...")

    # Отправляем в GigaChat: Название задачи + Условие
    prompt = f"Задача: {task['name']}. Условие: {task_details}"
    ai_data = await ask_gigachat(prompt)

    if ai_data:
        # Обновляем данные задачи
        task['hours'] = ai_data.get("estimated_hours", task['hours'])
        task['steps'] = ai_data.get("steps", task['steps'])
        task['details'] = task_details
        task['deadline'] = ai_data.get("deadline", task['deadline'])

        save_tasks(all_tasks)

        steps_formatted = "\n".join([f"  {i + 1}. {s}" for i, s in enumerate(task['steps'])])
        await message.answer(
            f"✅ **Оценка обновлена!**\n"
            f"⏱ Новое время: ~{task['hours']} часов.\n"
            f"📅 Дедлайн: {task['deadline']}\n\n"
            f"📋 **Новый план:**\n{steps_formatted}",
            parse_mode="Markdown"
        )
    else:
        await message.answer("😔 Не смог проанализировать условие.")


async def cmd_list(message: types.Message):
    user_id = str(message.from_user.id)
    tasks = load_tasks().get(user_id, [])

    if not tasks:
        await message.answer("📭 У тебя пока нет задач. Напиши что-нибудь!")
        return

    text = "📋 **Твои задачи:**\n\n"
    for i, t in enumerate(tasks):
        deadline = t.get('deadline', 'Без срока')
        text += f"**{i + 1}.** {t['name']} (до {deadline})\n   ⏱ ~{t['hours']} ч.\n\n"

    text += "💡 *Напиши `/info НОМЕР`, чтобы добавить описание к задаче и уточнить оценку.*"
    await message.answer(text, parse_mode="Markdown")


async def cmd_busy(message: types.Message):
    user_id = str(message.from_user.id)
    # Убираем саму команду /busy из текста
    text = message.text.replace("/busy", "").strip()

    if not text:
        await message.answer(
            "Напиши, когда ты занят, чтобы я не беспокоил тебя.\n"
            "Например: `/busy с 9 до 18 учеба, с 23 до 8 сон`",
            parse_mode="Markdown"
        )
        return

    busy_data = load_busy()
    busy_data[user_id] = text
    save_busy(busy_data)

    await message.answer(
        f"✅ Я запомнил, что ты занят:\n*{text}*\n\nТеперь я буду подстраивать напоминания под это расписание!",
        parse_mode="Markdown"
    )


def register_handlers(dp):
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_list, Command("list"))
    dp.message.register(cmd_busy, Command("busy"))
    dp.message.register(cmd_info, Command("info"))