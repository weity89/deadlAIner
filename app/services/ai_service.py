import json
import logging
import re
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
from app.config import GIGACHAT_CREDENTIALS, GIGACHAT_SCOPE


async def ask_gigachat(prompt: str, context: str = "") -> dict:
    system_prompt = (
        "Ты — умный помощник-планировщик. Проанализируй текст задачи, "
        "оцени сложность и разбей на этапы. "
        "Верни СТРОГО JSON с ключами:\n"
        "task_name: краткое название (строка)\n"
        "estimated_hours: число часов (число)\n"
        "deadline: дата сдачи в формате YYYY-MM-DD (если дата не указана, верни null)\n"
        "steps: массив из 2-3 подзадач (строки)\n"
        "reminder_text: мотивационная фраза (строка)\n"
        "Сегодняшняя дата: 2026-10-21. Если пишут 'до пятницы', посчитай дату этой пятницы.\n"
        "НИКАКОГО текста до или после JSON. Только фигурные скобки."
        f"\nДОПОЛНИТЕЛЬНЫЙ КОНТЕКСТ ОТ ПОЛЬЗОВАТЕЛЯ: {context}"
    )

    giga = GigaChat(
        credentials=GIGACHAT_CREDENTIALS,
        scope=GIGACHAT_SCOPE,
        model="GigaChat-2",
        verify_ssl_certs=False
    )

    try:
        response = giga.chat(
            Chat(messages=[
                Messages(role=MessagesRole.SYSTEM, content=system_prompt),
                Messages(role=MessagesRole.USER, content=prompt)
            ])
        )

        # --- ОТЛАДКА ---
        print("=== СЫРОЙ ОТВЕТ ОТ GIGACHAT ===")
        print(response)
        print("================================")
        # ---------------

        text_response = response.choices[0].message.content
        print(f"=== ТЕКСТ ОТВЕТА: {repr(text_response)} ===")  # покажет скрытые символы

        match = re.search(r'\{.*\}', text_response, re.DOTALL)
        if match:
            clean_json = match.group(0)
            return json.loads(clean_json)
        else:
            logging.error(f"GigaChat вернул текст без JSON: {text_response}")
            return None

    except Exception as e:
        logging.error(f"Ошибка GigaChat: {e}")
        return None
    finally:
        giga.close()