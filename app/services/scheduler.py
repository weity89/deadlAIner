from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

scheduler = AsyncIOScheduler()

async def send_reminder(bot: Bot, user_id: int, task_name: str, text: str):
    await bot.send_message(user_id, f"⏰ **НАПОМИНАНИЕ: {task_name}**\n\n{text}", parse_mode="Markdown")