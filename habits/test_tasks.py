# habits/test_tasks.py
from django.test import TestCase
from unittest.mock import patch, MagicMock
from habits.tasks import send_daily_reminders, test_celery_task
from habits.models import Habit, TelegramUser
from users.models import User
from datetime import datetime, time
from django.utils import timezone
import pytest
from django.core.exceptions import ValidationError


class CeleryTasksTests(TestCase):
    """Тесты для Celery задач."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

        # Создаем TelegramUser для пользователя
        self.telegram_user = TelegramUser.objects.create(
            user=self.user,
            chat_id='123456',
            verified=True
        )

    @patch('habits.tasks.send_telegram_reminder')
    @patch('habits.tasks.timezone.now')
    def test_send_daily_reminders_daily_habit(self, mock_now, mock_send):
        """Тест задачи отправки ежедневных напоминаний для ежедневной привычки."""
        # Настраиваем моки
        test_time = time(12, 0, 0)
        mock_datetime = datetime(2024, 1, 1, 12, 0, 0)
        mock_now.return_value = timezone.make_aware(mock_datetime)
        mock_send.return_value = True

        try:
            # Создаем ежедневную привычку (frequency=1)
            habit = Habit.objects.create(
                user=self.user,
                place='Дома',
                time=test_time,
                action='Тестовая привычка',
                frequency=1,  # Ежедневно
                duration=120,
                is_public=False,
                created_at=timezone.make_aware(datetime(2023, 12, 31))  # Создана вчера
            )
        except ValidationError as e:
            self.fail(f"Ошибка валидации при создании привычки: {e}")

        # Вызываем задачу
        result = send_daily_reminders()

        # Проверяем результат
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['sent_count'], 1)
        self.assertEqual(result['errors_count'], 0)
        self.assertIn('Отправлено напоминаний:', result['message'])

        # Проверяем, что функция отправки была вызвана
        mock_send.assert_called_once()

    @patch('habits.tasks.send_telegram_reminder')
    @patch('habits.tasks.timezone.now')
    def test_send_daily_reminders_periodic_habit(self, mock_now, mock_send):
        """Тест задачи для привычки с периодичностью > 1 день."""
        # Настраиваем моки
        test_time = time(12, 0, 0)
        mock_datetime = datetime(2024, 1, 1, 12, 0, 0)
        mock_now.return_value = timezone.make_aware(mock_datetime)
        mock_send.return_value = True

        try:
            # Создаем привычку с периодичностью 3 дня
            # Она была создана 3 дня назад (2023-12-29)
            created_date = timezone.make_aware(datetime(2023, 12, 29))

            habit = Habit.objects.create(
                user=self.user,
                place='Дома',
                time=test_time,
                action='Тестовая периодическая привычка',
                frequency=3,  # Раз в 3 дня
                duration=60,
                is_public=False,
                created_at=created_date
            )
        except ValidationError as e:
            self.fail(f"Ошибка валидации при создании привычки: {e}")

        # Вызываем задачу (должна отправиться, т.к. прошло 3 дня)
        result = send_daily_reminders()

        # Проверяем результат
        self.assertEqual(result['sent_count'], 1)
        mock_send.assert_called_once()

    @patch('habits.tasks.send_telegram_reminder')
    @patch('habits.tasks.timezone.now')
    def test_send_daily_reminders_wrong_time(self, mock_now, mock_send):
        """Тест задачи, когда время привычки не совпадает с текущим."""
        # Настраиваем моки - текущее время 15:00
        mock_datetime = datetime(2024, 1, 1, 15, 0, 0)
        mock_now.return_value = timezone.make_aware(mock_datetime)
        mock_send.return_value = True

        try:
            # Создаем привычку на 12:00
            habit_time = time(12, 0, 0)

            habit = Habit.objects.create(
                user=self.user,
                place='Дома',
                time=habit_time,
                action='Тестовая привычка',
                frequency=1,
                duration=60,
                is_public=False
            )
        except ValidationError as e:
            self.fail(f"Ошибка валидации при создании привычки: {e}")

        # Вызываем задачу
        result = send_daily_reminders()

        # Проверяем результат - не должно быть отправок (разница во времени > 30 мин)
        self.assertEqual(result['sent_count'], 0)
        mock_send.assert_not_called()

    @patch('habits.tasks.send_telegram_reminder')
    @patch('habits.tasks.timezone.now')
    def test_send_daily_reminders_telegram_error(self, mock_now, mock_send):
        """Тест задачи с ошибкой при отправке в Telegram."""
        # Настраиваем моки
        test_time = time(12, 0, 0)
        mock_datetime = datetime(2024, 1, 1, 12, 0, 0)
        mock_now.return_value = timezone.make_aware(mock_datetime)
        mock_send.return_value = False  # Имитация ошибки

        try:
            # Создаем привычку
            habit = Habit.objects.create(
                user=self.user,
                place='Дома',
                time=test_time,
                action='Тестовая привычка',
                frequency=1,
                duration=60,
                is_public=False
            )
        except ValidationError as e:
            self.fail(f"Ошибка валидации при создании привычки: {e}")

        # Вызываем задачу
        result = send_daily_reminders()

        # Проверяем результат
        self.assertEqual(result['sent_count'], 0)
        self.assertEqual(result['errors_count'], 1)
        mock_send.assert_called_once()

    @patch('habits.tasks.send_telegram_reminder')
    @patch('habits.tasks.timezone.now')
    def test_send_daily_reminders_no_telegram_user(self, mock_now, mock_send):
        """Тест задачи, когда у пользователя нет Telegram."""
        # Создаем нового пользователя без Telegram
        user_without_telegram = User.objects.create_user(
            email='no_telegram@example.com',
            password='testpass123'
        )

        # Настраиваем моки
        test_time = time(12, 0, 0)
        mock_datetime = datetime(2024, 1, 1, 12, 0, 0)
        mock_now.return_value = timezone.make_aware(mock_datetime)
        mock_send.return_value = True

        try:
            # Создаем привычку для пользователя без Telegram
            habit = Habit.objects.create(
                user=user_without_telegram,
                place='Дома',
                time=test_time,
                action='Тестовая привычка',
                frequency=1,
                duration=60,
                is_public=False
            )
        except ValidationError as e:
            self.fail(f"Ошибка валидации при создании привычки: {e}")

        # Вызываем задачу
        result = send_daily_reminders()

        # Проверяем результат - не должно быть отправок
        self.assertEqual(result['sent_count'], 0)
        mock_send.assert_not_called()

    @patch('habits.tasks.send_telegram_reminder')
    @patch('habits.tasks.timezone.now')
    def test_send_daily_reminders_with_reward(self, mock_now, mock_send):
        """Тест задачи для привычки с вознаграждением."""
        # Настраиваем моки
        test_time = time(12, 0, 0)
        mock_datetime = datetime(2024, 1, 1, 12, 0, 0)
        mock_now.return_value = timezone.make_aware(mock_datetime)
        mock_send.return_value = True

        try:
            # Создаем привычку с вознаграждением
            habit = Habit.objects.create(
                user=self.user,
                place='Дома',
                time=test_time,
                action='Тестовая привычка с наградой',
                frequency=1,
                duration=60,
                reward='Выпить кофе',
                is_public=False
            )
        except ValidationError as e:
            self.fail(f"Ошибка валидации при создании привычки: {e}")

        # Вызываем задачу
        result = send_daily_reminders()

        # Проверяем результат
        self.assertEqual(result['sent_count'], 1)
        mock_send.assert_called_once()

        # Проверяем, что в сообщении есть информация о награде
        args, kwargs = mock_send.call_args
        message = args[1] if args else kwargs.get('message')
        if message:
            self.assertIn('Выпить кофе', message)

    @patch('habits.tasks.send_telegram_reminder')
    @patch('habits.tasks.timezone.now')
    def test_send_daily_reminders_with_related_habit(self, mock_now, mock_send):
        """Тест задачи для привычки со связанной привычкой."""
        # Настраиваем моки
        test_time = time(12, 0, 0)
        mock_datetime = datetime(2024, 1, 1, 12, 0, 0)
        mock_now.return_value = timezone.make_aware(mock_datetime)
        mock_send.return_value = True

        try:
            # Создаем приятную привычку в ДРУГОЕ время (не в пределах 30 минут от текущего)
            pleasant_habit = Habit.objects.create(
                user=self.user,
                place='Диван',
                time=time(15, 30, 0),  # Время отличается более чем на 30 минут от 12:00
                action='Отдохнуть',
                is_pleasant=True,
                frequency=1,
                duration=120,
                is_public=False
            )

            # Создаем привычку со связанной привычкой в ТЕКУЩЕЕ время
            habit = Habit.objects.create(
                user=self.user,
                place='Дома',
                time=test_time,  # Текущее время (12:00)
                action='Тестовая привычка со связанной',
                frequency=1,
                duration=60,
                related_habit=pleasant_habit,
                is_public=False
            )
        except ValidationError as e:
            self.fail(f"Ошибка валидации при создании привычки: {e}")

        # Вызываем задачу
        result = send_daily_reminders()

        # Проверяем результат - должна отправиться только ОДНА привычка (основная)
        self.assertEqual(result['sent_count'], 1)
        mock_send.assert_called_once()

        # Проверяем, что в сообщении есть информация о связанной привычке
        args, kwargs = mock_send.call_args
        message = args[1] if args else kwargs.get('message')
        if message:
            self.assertIn('Отдохнуть', message)

    def test_test_celery_task(self):
        """Тест тестовой Celery задачи."""
        # Вызываем задачу
        result = test_celery_task()

        # Проверяем результат
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Celery работает корректно!")
        self.assertIn("timestamp", result)

    @patch('habits.tasks.send_telegram_reminder')
    @patch('habits.tasks.timezone.now')
    def test_send_daily_reminders_multiple_habits(self, mock_now, mock_send):
        """Тест задачи с несколькими привычками."""
        # Настраиваем моки
        test_time = time(12, 0, 0)
        mock_datetime = datetime(2024, 1, 1, 12, 0, 0)
        mock_now.return_value = timezone.make_aware(mock_datetime)
        mock_send.return_value = True

        try:
            # Создаем несколько привычек
            habit1 = Habit.objects.create(
                user=self.user,
                place='Дома',
                time=test_time,
                action='Первая привычка',
                frequency=1,
                duration=60,
                is_public=False
            )

            habit2 = Habit.objects.create(
                user=self.user,
                place='Офис',
                time=time(11, 50, 0),  # В пределах 30 минут
                action='Вторая привычка',
                frequency=1,
                duration=45,
                is_public=False
            )

            # Эта привычка не должна быть отправлена (время отличается более чем на 30 минут)
            habit3 = Habit.objects.create(
                user=self.user,
                place='Парк',
                time=time(10, 0, 0),  # Более чем за 2 часа
                action='Третья привычка',
                frequency=1,
                duration=90,
                is_public=False
            )
        except ValidationError as e:
            self.fail(f"Ошибка валидации при создании привычки: {e}")

        # Вызываем задачу
        result = send_daily_reminders()

        # Проверяем результат - должно быть отправлено 2 напоминания
        self.assertEqual(result['sent_count'], 2)
        self.assertEqual(result['errors_count'], 0)
        self.assertEqual(mock_send.call_count, 2)

    @patch('habits.tasks.send_telegram_reminder')
    @patch('habits.tasks.timezone.now')
    def test_send_daily_reminders_pleasant_habit(self, mock_now, mock_send):
        """Тест задачи для приятной привычки."""
        # Настраиваем моки
        test_time = time(12, 0, 0)
        mock_datetime = datetime(2024, 1, 1, 12, 0, 0)
        mock_now.return_value = timezone.make_aware(mock_datetime)
        mock_send.return_value = True

        try:
            # Создаем приятную привычку
            pleasant_habit = Habit.objects.create(
                user=self.user,
                place='Дома',
                time=test_time,
                action='Послушать музыку',
                is_pleasant=True,
                frequency=1,
                duration=120,
                is_public=False
            )
        except ValidationError as e:
            self.fail(f"Ошибка валидации при создании привычки: {e}")

        # Вызываем задачу
        result = send_daily_reminders()

        # Проверяем результат - приятные привычки тоже отправляются
        self.assertEqual(result['sent_count'], 1)
        mock_send.assert_called_once()