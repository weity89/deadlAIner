import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.config import TELEGRAM_TOKEN
from app.services.scheduler import scheduler
from app.handlers import user_commands, task_flow

from aiogram.client.telegram import TelegramAPIServer
from aiogram.client.session.aiohttp import AiohttpSession
from andro_cfw import CFWSession

# 1. Загружаем сохраненную сессию (файл cfw.session)
cfw_session = CFWSession.load()

# 2. Получаем адрес твоего Worker'а для aiogram
api_server = TelegramAPIServer(**cfw_session.aiogram_server_url())

# 3. Создаем бота с явным указанием сервера
bot = Bot(
    token=TELEGRAM_TOKEN,
    session=AiohttpSession(api=api_server),
)

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