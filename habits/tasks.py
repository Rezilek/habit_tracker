from celery import shared_task
from datetime import datetime, time
from django.utils import timezone
from django.db.models import Q
from .models import Habit, TelegramUser
from .services import send_telegram_reminder
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_daily_reminders():
    """
    Отправка ежедневных напоминаний о привычках.
    Проверяет привычки, которые нужно выполнить сегодня.
    """
    now = timezone.now()
    current_time = now.time()
    current_date = now.date()

    # Определяем день недели (0=понедельник, 6=воскресенье)
    current_weekday = now.weekday()  # 0-6

    # Логи для отладки
    logger.info(f"Запуск отправки напоминаний: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Текущий день недели: {current_weekday}")

    # Получаем все привычки, у пользователей которых есть Telegram
    habits = Habit.objects.filter(
        user__telegram__isnull=False
    ).select_related('user__telegram')

    logger.info(f"Найдено привычек с Telegram: {habits.count()}")

    sent_count = 0
    errors_count = 0

    for habit in habits:
        try:
            # Проверяем, нужно ли выполнять привычку сегодня
            # frequency = 1 (ежедневно) или проверка по дню недели для frequency > 1
            should_send_today = False

            if habit.frequency == 1:  # Ежедневно
                should_send_today = True
            elif habit.frequency > 1:  # Раз в несколько дней
                # Простая логика: отправляем если прошло достаточно дней с создания
                days_since_creation = (current_date - habit.created_at.date()).days
                if days_since_creation % habit.frequency == 0:
                    should_send_today = True

            if not should_send_today:
                continue

            # Проверяем время привычки (±30 минут)
            habit_time = habit.time
            current_minutes = current_time.hour * 60 + current_time.minute
            habit_minutes = habit_time.hour * 60 + habit_time.minute
            time_diff = abs(current_minutes - habit_minutes)

            if time_diff <= 30:  # Напоминание за 30 минут до или после
                telegram_user = habit.user.telegram

                # Формируем сообщение
                message = (
                    "🔔 *Напоминание о привычке!*\n\n"
                    f"*Действие:* {habit.action}\n"
                    f"*Место:* {habit.place}\n"
                    f"*Время:* {habit_time.strftime('%H:%M')}\n"
                    f"*Длительность:* {habit.duration} секунд\n"
                )

                # Добавляем информацию о вознаграждении или связанной привычке
                if habit.reward:
                    message += f"*Вознаграждение:* {habit.reward}\n"
                elif habit.related_habit:
                    message += f"*Следом выполнить:* {habit.related_habit.action}\n"

                # Отправляем напоминание
                success = send_telegram_reminder(telegram_user.chat_id, message)

                if success:
                    logger.info(f"✓ Отправлено напоминание пользователю {habit.user.email}")
                    sent_count += 1
                else:
                    logger.warning(f"✗ Не удалось отправить пользователю {habit.user.email}")
                    errors_count += 1

        except TelegramUser.DoesNotExist:
            logger.warning(f"У пользователя {habit.user.email} нет телеграм аккаунта")
            errors_count += 1
        except Exception as e:
            logger.error(f"Ошибка обработки привычки {habit.id}: {str(e)}")
            errors_count += 1

    logger.info(f"Итог: отправлено {sent_count}, ошибок: {errors_count}")
    return {
        "status": "success",
        "sent_count": sent_count,
        "errors_count": errors_count,
        "message": f"Отправлено напоминаний: {sent_count}, ошибок: {errors_count}"
    }


@shared_task
def test_celery_task():
    """Тестовая задача для проверки работы Celery."""
    logger.info("Тестовая задача Celery выполнена успешно")
    return {
        "status": "success",
        "message": "Celery работает корректно!",
        "timestamp": timezone.now().isoformat()
    }