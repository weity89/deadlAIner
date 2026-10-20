import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.config import TELEGRAM_TOKEN
from app.services.scheduler import scheduler
from app.handlers import user_commands, task_flow

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

async def main():
    logging.basicConfig(level=logging.INFO)
    user_commands.register_handlers(dp)
    task_flow.register_handlers(dp)
    scheduler.start()
    print("🚀 deadlAIner запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())