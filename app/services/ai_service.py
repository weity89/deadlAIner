import aiohttp
import json
import logging
from app.config import YANDEX_API_KEY, YANDEX_FOLDER_ID

async def ask_yandex_gpt(prompt: str) -> dict:
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json"
    }
    system_prompt = (
        "Ты — умный помощник-планировщик. Проанализируй текст задачи, "
        "оцени сложность и разбей на этапы. "
        "Верни СТРОГО JSON (без ```json) с ключами:\n"
        "task_name: краткое название\n"
        "estimated_hours: число часов\n"
        "steps: массив из 2-3 подзадач\n"
        "reminder_text: мотивационная фраза\n"
        f"Текст: {prompt}"
    )
    data = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite/latest",
        "completionOptions": {"stream": False, "temperature": 0.3, "maxTokens": "1000"},
        "messages": [
            {"role": "system", "text": system_prompt},
            {"role": "user", "text": prompt}
        ]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                text = result['result']['alternatives'][0]['message']['text']
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    logging.error(f"Ошибка JSON: {text}")
                    return None
            else:
                logging.error(f"Ошибка API: {await response.text()}")
                return None