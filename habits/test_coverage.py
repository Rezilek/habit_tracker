# habits/test_coverage.py
from datetime import time
from django.test import TestCase
from django.core.exceptions import ValidationError
from habits.models import Habit, TelegramUser
from users.models import User


class TestModels(TestCase):

    def setUp(self):
        """Настройка тестовых данных."""
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )

    def test_habit_clean_method_invalid_self_reference(self):
        """Тест метода clean для привычки, связанной с самой собой."""
        # Создаем привычку с правильными полями согласно вашей модели
        habit = Habit.objects.create(
            user=self.user,
            place="Дома",
            time=time(hour=12, minute=0),  # Используем time вместо строки
            action="Читать книгу",
            is_pleasant=False,
            frequency=1,
            duration=120,  # В секундах
            is_public=False
        )

        # Пытаемся связать привычку саму с собой
        habit.related_habit = habit

        # Должно вызвать ValidationError
        with self.assertRaises(ValidationError) as context:
            habit.clean()  # Вызываем clean() напрямую

        # Проверяем сообщение об ошибке
        self.assertIn('не может быть связана сама с собой', str(context.exception))

    def test_habit_clean_method_valid(self):
        """Тест метода clean для валидной привычки."""
        # Проверяем разные валидные сценарии

        # 1. Приятная привычка
        nice_habit = Habit(
            user=self.user,
            place="Диван",
            time=time(hour=19, minute=30),
            action="Слушать музыку",
            is_pleasant=True,
            frequency=1,
            duration=60,  # 1 минута
            is_public=True
        )

        # Должно пройти без ошибок
        try:
            nice_habit.full_clean()  # Используем full_clean для полной валидации
        except ValidationError as e:
            self.fail(f"Приятная привычка вызвала ValidationError: {e}")
        else:
            nice_habit.save()

        # 2. Обычная привычка с вознаграждением
        regular_habit = Habit(
            user=self.user,
            place="Спортзал",
            time=time(hour=8, minute=0),
            action="Делать зарядку",
            is_pleasant=False,
            frequency=1,
            reward="Чашка кофе",
            duration=120,  # 2 минуты (максимум)
            is_public=False
        )

        # Должно пройти без ошибок
        try:
            regular_habit.full_clean()
        except ValidationError as e:
            self.fail(f"Обычная привычка с вознаграждением вызвала ValidationError: {e}")
        else:
            regular_habit.save()

        # 3. Обычная привычка со связанной приятной привычкой
        habit_with_related = Habit(
            user=self.user,
            place="Кухня",
            time=time(hour=9, minute=0),
            action="Пить воду",
            is_pleasant=False,
            frequency=1,
            related_habit=nice_habit,
            duration=30,  # 30 секунд
            is_public=False
        )

        # Должно пройти без ошибок
        try:
            habit_with_related.full_clean()
        except ValidationError as e:
            self.fail(f"Привычка со связанной приятной привычкой вызвала ValidationError: {e}")
        else:
            habit_with_related.save()

        # Проверяем, что все привычки сохранены
        self.assertEqual(Habit.objects.count(), 3)

def test_habit_clean_pleasant_with_reward(self):
    """Тест: приятная привычка не может иметь вознаграждения."""
    habit = Habit(
        user=self.user,
        place="Дома",
        time=time(hour=12, minute=0),
        action="Медитировать",
        is_pleasant=True,
        frequency=1,
        reward="Конфета",  # Нельзя для приятной привычки
        duration=300,
        is_public=False
    )

    with self.assertRaises(ValidationError) as context:
        habit.clean()

    self.assertIn('У приятной привычки не может быть вознаграждения', str(context.exception))


def test_habit_clean_pleasant_with_related(self):
    """Тест: приятная привычка не может иметь связанной привычки."""
    # Создаем другую привычку для связи
    other_habit = Habit.objects.create(
        user=self.user,
        place="Парк",
        time=time(hour=7, minute=0),
        action="Бегать",
        is_pleasant=False,
        frequency=1,
        duration=1800,
        is_public=True
    )

    habit = Habit(
        user=self.user,
        place="Дома",
        time=time(hour=12, minute=0),
        action="Медитировать",
        is_pleasant=True,
        frequency=1,
        related_habit=other_habit,  # Нельзя для приятной привычки
        duration=300,
        is_public=False
    )

    with self.assertRaises(ValidationError) as context:
        habit.clean()

    self.assertIn('У приятной привычки не может быть связанной привычки', str(context.exception))


def test_habit_clean_both_reward_and_related(self):
    """Тест: нельзя одновременно указывать и вознаграждение, и связанную привычку."""
    # Создаем приятную привычку для связи
    nice_habit = Habit.objects.create(
        user=self.user,
        place="Диван",
        time=time(hour=19, minute=30),
        action="Слушать музыку",
        is_pleasant=True,
        frequency=1,
        duration=300,
        is_public=True
    )

    habit = Habit(
        user=self.user,
        place="Спортзал",
        time=time(hour=8, minute=0),
        action="Делать зарядку",
        is_pleasant=False,
        frequency=1,
        related_habit=nice_habit,
        reward="Чашка кофе",  # Нельзя одновременно с related_habit
        duration=600,
        is_public=False
    )

    with self.assertRaises(ValidationError) as context:
        habit.clean()

    self.assertIn('Нельзя одновременно указывать связанную привычку и вознаграждение', str(context.exception))


def test_habit_clean_related_not_pleasant(self):
    """Тест: связанная привычка должна быть приятной."""
    # Создаем НЕприятную привычку для связи
    not_nice_habit = Habit.objects.create(
        user=self.user,
        place="Спортзал",
        time=time(hour=8, minute=0),
        action="Поднимать тяжести",
        is_pleasant=False,  # НЕ приятная привычка!
        frequency=7,
        reward="Белок",
        duration=1800,
        is_public=True
    )

    habit = Habit(
        user=self.user,
        place="Кухня",
        time=time(hour=9, minute=0),
        action="Пить воду",
        is_pleasant=False,
        frequency=1,
        related_habit=not_nice_habit,  # Связываем с НЕприятной привычкой - должно быть ошибкой
        duration=60,
        is_public=False
    )

    with self.assertRaises(ValidationError) as context:
        habit.clean()

    self.assertIn('Связанная привычка должна быть приятной', str(context.exception))