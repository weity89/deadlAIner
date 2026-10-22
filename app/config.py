import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
# YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
# YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")

# Новые ключи GigaChat
GIGACHAT_CREDENTIALS = os.getenv("GIGACHAT_CREDENTIALS")
GIGACHAT_SCOPE = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")