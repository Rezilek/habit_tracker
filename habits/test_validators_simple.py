# habits/test_validators_simple.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from habits.validators import validate_duration


class SimpleValidatorsTest(TestCase):
    """Простой тест для валидаторов."""

    def test_validate_duration(self):
        """Тест валидации длительности."""
        # Корректные значения
        self.assertEqual(validate_duration(1), 1)
        self.assertEqual(validate_duration(120), 120)
        self.assertEqual(validate_duration(60), 60)

        # Некорректные значения
        with self.assertRaises(ValidationError):
            validate_duration(0)

        with self.assertRaises(ValidationError):
            validate_duration(121)
