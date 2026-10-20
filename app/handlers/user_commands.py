from aiogram import types
from aiogram.filters import Command

async def cmd_start(message: types.Message):
    welcome_text = (
        "✈️ **Добро пожаловать в deadlAIner!**\n\n"
        "Я твой личный AI-штурман.\n"
        "Напиши задачу как думаешь (например: «Лаба по ООП до пятницы»), "
        "а я оценю время и разобью на этапы! 🚀"
    )
    await message.answer(welcome_text, parse_mode="Markdown")

def register_handlers(dp):
    dp.message.register(cmd_start, Command("start"))