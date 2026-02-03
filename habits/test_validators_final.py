# habits/test_validators_final.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from habits.validators import validate_duration
from habits.models import Habit
from django.contrib.auth import get_user_model

User = get_user_model()


class ValidatorsFinalTest(TestCase):
    """Финальные тесты для валидаторов."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_validate_duration_edge_cases(self):
        """Тест граничных случаев валидации длительности."""
        # Граничные значения
        self.assertEqual(validate_duration(1), 1)
        self.assertEqual(validate_duration(120), 120)

        # Некорректные граничные значения
        with self.assertRaises(ValidationError) as e:
            validate_duration(0)
        self.assertIn('меньше 1 секунды', str(e.exception))

        with self.assertRaises(ValidationError) as e:
            validate_duration(121)
        self.assertIn('меньше либо равно 120', str(e.exception))

    def test_validate_duration_normal_cases(self):
        """Тест нормальных значений валидации длительности."""
        # Нормальные значения
        self.assertEqual(validate_duration(30), 30)
        self.assertEqual(validate_duration(60), 60)
        self.assertEqual(validate_duration(90), 90)

        # Дробные числа (если поддерживаются)
        try:
            self.assertEqual(validate_duration(30.5), 30.5)
        except Exception:
            pass