# habits/services.py
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def send_telegram_reminder(chat_id, message):
    """
    Отправка сообщения в Telegram.
    Возвращает True при успехе, False при ошибке.
    """
    bot_token = settings.TELEGRAM_BOT_TOKEN

    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN не настроен")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'  # Для форматирования текста
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Сообщение отправлено в чат {chat_id}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка отправки в Telegram: {e}")
        return False