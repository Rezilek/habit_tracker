# habits/test_services.py
from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock
from habits.services import send_telegram_reminder
import requests


class TelegramServiceTests(TestCase):
    """Тесты для сервиса отправки Telegram сообщений."""

    @override_settings(TELEGRAM_BOT_TOKEN='test_token')
    @patch('habits.services.requests.post')
    def test_send_telegram_reminder_success(self, mock_post):
        """Тест успешной отправки сообщения."""
        # Настраиваем mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()  # Мокаем метод raise_for_status
        mock_post.return_value = mock_response

        # Вызываем функцию
        result = send_telegram_reminder('123456', 'Тестовое сообщение')

        # Проверяем результат
        self.assertTrue(result)
        mock_post.assert_called_once()

    @override_settings(TELEGRAM_BOT_TOKEN='test_token')
    @patch('habits.services.requests.post')
    def test_send_telegram_reminder_failure(self, mock_post):
        """Тест неудачной отправки сообщения."""
        # Настраиваем mock для выброса исключения
        mock_post.side_effect = requests.exceptions.RequestException('Ошибка сети')

        # Вызываем функцию
        result = send_telegram_reminder('123456', 'Тестовое сообщение')

        # Проверяем результат
        self.assertFalse(result)
        mock_post.assert_called_once()

    @override_settings(TELEGRAM_BOT_TOKEN='')
    def test_send_telegram_reminder_no_token(self):
        """Тест отправки без токена."""
        # Вызываем функцию
        result = send_telegram_reminder('123456', 'Тестовое сообщение')

        # Проверяем результат
        self.assertFalse(result)

    @override_settings(TELEGRAM_BOT_TOKEN='test_token')
    @patch('habits.services.requests.post')
    def test_send_telegram_reminder_http_error(self, mock_post):
        """Тест HTTP ошибки при отправке."""
        # Настраиваем mock для выброса HTTPError
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.raise_for_status = MagicMock(side_effect=requests.exceptions.HTTPError("HTTP ошибка"))
        mock_post.return_value = mock_response

        # Вызываем функцию
        result = send_telegram_reminder('123456', 'Тестовое сообщение')

        # Проверяем результат
        self.assertFalse(result)
        mock_post.assert_called_once()