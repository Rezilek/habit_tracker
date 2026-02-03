# habits/validators.py
from rest_framework import serializers
from .models import Habit
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_duration(value):
    """
    Валидатор для проверки длительности выполнения привычки.
    Длительность должна быть от 1 до 120 секунд.
    """
    if value < 1:
        raise ValidationError(
            _('Длительность выполнения не может быть меньше 1 секунды.')
        )
    if value > 120:
        raise ValidationError(
            _('Убедитесь, что это значение меньше либо равно 120.')
        )
    return value


class HabitValidator:
    """Валидатор для проверки бизнес-логики привычек."""

    def __call__(self, data):
        # Проверяем, что нельзя одновременно указывать вознаграждение и связанную привычку
        if data.get('reward') and data.get('related_habit'):
            raise ValidationError(
                _('Нельзя одновременно указывать вознаграждение и связанную привычку.')
            )

        # Проверяем, что приятная привычка не может иметь вознаграждения
        if data.get('is_pleasant') and data.get('reward'):
            raise ValidationError(
                _('У приятной привычки не может быть вознаграждения.')
            )

        # Проверяем, что связанная привычка должна быть приятной
        related_habit = data.get('related_habit')
        if related_habit and not getattr(related_habit, 'is_pleasant', False):
            raise ValidationError(
                _('Связанная привычка должна быть приятной.')
            )

        # Проверяем периодичность (не реже 1 раза в 7 дней)
        if data.get('frequency', 1) > 7:
            raise ValidationError(
                _('Нельзя выполнять привычку реже, чем 1 раз в 7 дней.')
            )

        # Проверяем, что привычка не связана сама с собой
        if 'id' in data and data.get('related_habit') and data['id'] == getattr(data['related_habit'], 'id', None):
            raise ValidationError(
                _('Привычка не может быть связана сама с собой.')
            )


# Если у вас нет отдельных функций-валидаторов, используйте класс HabitValidator
# или создайте их по аналогии:

def validate_habit_not_related_to_itself(habit):
    """Валидация: привычка не может быть связана сама с собой."""
    if habit.related_habit and habit.id and habit.related_habit.id == habit.id:
        raise ValidationError(
            _('Привычка не может быть связана сама с собой.')
        )


def validate_pleasant_habit_no_reward(habit):
    """Валидация: приятная привычка не может иметь вознаграждения."""
    if habit.is_pleasant and habit.reward:
        raise ValidationError(
            _('У приятной привычки не может быть вознаграждения.')
        )


def validate_no_both_reward_and_related(habit):
    """Валидация: нельзя одновременно указывать вознаграждение и связанную привычку."""
    if habit.reward and habit.related_habit:
        raise ValidationError(
            _('Нельзя одновременно указывать вознаграждение и связанную привычку.')
        )


def validate_related_habit_must_be_pleasant(habit):
    """Валидация: связанная привычка должна быть приятной."""
    if habit.related_habit and not habit.related_habit.is_pleasant:
        raise ValidationError(
            _('Связанная привычка должна быть приятной.')
        )


def validate_periodicity(habit):
    """Валидация: периодичность не реже 1 раза в 7 дней."""
    if habit.frequency > 7:
        raise ValidationError(
            _('Нельзя выполнять привычку реже, чем 1 раз в 7 дней.')
        )
