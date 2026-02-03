# habits/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone  # ✅ Правильный импорт

User = get_user_model()

class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    place = models.CharField(max_length=255, verbose_name='Место')
    time = models.TimeField(verbose_name='Время')
    action = models.CharField(max_length=500, verbose_name='Действие')
    is_pleasant = models.BooleanField(default=False, verbose_name='Признак приятной привычки')
    related_habit = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                      verbose_name='Связанная привычка', related_name='related_to')

    frequency = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        verbose_name='Периодичность (дни)'
    )

    reward = models.CharField(max_length=255, blank=True, null=True, verbose_name='Вознаграждение')
    duration = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(120)],
                                           verbose_name='Время на выполнение (в секундах)')
    is_public = models.BooleanField(default=False, verbose_name='Признак публичности')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    last_completed = models.DateTimeField(null=True, blank=True,
                                          verbose_name='Последнее выполнение')  # Добавьте если нужно

    def clean(self):
        """Валидация на уровне модели"""
        super().clean()

        # 1. Привычка не может быть связана сама с собой
        if self.related_habit == self:
            raise ValidationError("Привычка не может быть связана сама с собой.")

        # 2. Приятная привычка не может иметь вознаграждения или связанной привычки
        if self.is_pleasant and (self.reward or self.related_habit):
            raise ValidationError("У приятной привычки не может быть вознаграждения или связанной привычки.")

        # 3. Нельзя одновременно указывать связанную привычку и вознаграждение
        if self.related_habit and self.reward:
            raise ValidationError("Нельзя одновременно указывать связанную привычку и вознаграждение.")

        # 4. Связанная привычка должна быть приятной
        if self.related_habit and not self.related_habit.is_pleasant:
            raise ValidationError("Связанная привычка должна быть приятной.")

        # 5. Проверка периодичности
        if self.frequency < 1 or self.frequency > 7:
            raise ValidationError("Периодичность должна быть от 1 до 7 дней")

        ("Нельзя пропускать привычку более 7 дней")

    def save(self, *args, **kwargs):
        """Вызываем clean при сохранении"""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user}: {self.action} в {self.time} в {self.place}"

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
        ordering = ['-created_at']

class TelegramUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='telegram')
    chat_id = models.CharField(max_length=50, unique=True, verbose_name='ID чата в Telegram')
    username = models.CharField(max_length=100, blank=True, null=True, verbose_name='Username в Telegram')
    verified = models.BooleanField(default=False, verbose_name='Верифицирован')
    verification_code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} -> {self.chat_id}"

    class Meta:
        verbose_name = 'Telegram пользователь'
        verbose_name_plural = 'Telegram пользователи'