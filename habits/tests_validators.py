# habits/tests_validators.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from habits.models import Habit
from django.contrib.auth import get_user_model

User = get_user_model()


class HabitValidatorsCompleteTests(TestCase):
    """Полные тесты валидаторов привычек."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_habit_validators_complete(self):
        """Комплексный тест всех валидаторов."""
        # 1. Тест на связанную привычку саму с собой
        # Создаем привычку
        habit = Habit(
            user=self.user,
            place='Дома',
            time='12:00:00',
            action='Тестовая привычка',
            frequency=1,
            duration=120
        )

        # Сохраняем привычку сначала (чтобы у нее был ID)
        habit.save()

        # Теперь пытаемся связать привычку саму с собой
        habit.related_habit = habit

        # Должно вызвать ValidationError при full_clean()
        with self.assertRaises(ValidationError) as context:
            habit.full_clean()

        self.assertIn('Привычка не может быть связана сама с собой.', str(context.exception))

        # Проверяем, что нельзя сохранить
        with self.assertRaises(ValidationError):
            habit.save()

        # Обновляем объект из базы данных
        habit.refresh_from_db()

        # Проверяем, что related_habit не установлен
        self.assertIsNone(habit.related_habit)

        # 2. Тест, что приятная привычка не может иметь награды
        pleasant_habit = Habit(
            user=self.user,
            place='Парк',
            time='18:00:00',
            action='Прогулка',
            is_pleasant=True,
            frequency=1,
            duration=30,
            reward='Кофе'  # Не должно быть для приятной привычки
        )

        with self.assertRaises(ValidationError) as context:
            pleasant_habit.full_clean()
        self.assertIn('приятной привычки не может быть вознаграждения', str(context.exception).lower())