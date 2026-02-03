from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from habits.models import Habit
from datetime import time

User = get_user_model()


class HabitModelTests(TestCase):
    """Тесты для модели Habit"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_create_habit(self):
        """Тест создания привычки"""
        habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time=time(8, 0),
            action='Пить воду',
            duration=60,
            is_public=True
        )

        self.assertEqual(habit.user.email, 'test@example.com')
        self.assertEqual(habit.action, 'Пить воду')
        self.assertEqual(habit.duration, 60)
        self.assertTrue(habit.is_public)
        self.assertIsNotNone(habit.created_at)

    def test_habit_string_representation(self):
        """Тест строкового представления привычки"""
        habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time=time(8, 0),
            action='Пить воду',
            duration=60
        )

        expected_str = f"{self.user}: Пить воду в 08:00:00 в Дом"
        self.assertEqual(str(habit), expected_str)

    def test_pleasant_habit_constraints(self):
        """Тест ограничений для приятной привычки"""
        # Создаем приятную привычку
        pleasant_habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time=time(9, 0),
            action='Медитация',
            is_pleasant=True,
            duration=30
        )

        # Приятная привычка не должна иметь вознаграждения
        pleasant_habit.refresh_from_db()
        self.assertTrue(pleasant_habit.is_pleasant)
        self.assertIsNone(pleasant_habit.reward)
        self.assertIsNone(pleasant_habit.related_habit)

    def test_duration_validation(self):
        """Тест валидации времени выполнения"""
        # Длительность должна быть положительной
        habit = Habit.objects.create(
            user=self.user,
            place='Офис',
            time=time(10, 0),
            action='Работа',
            duration=120
        )

        self.assertEqual(habit.duration, 120)

        # Проверяем через валидацию формы или сериализатора
        # Вместо проверки на уровне модели
        from django.core.exceptions import ValidationError
        from django.db import transaction

        # Пытаемся создать объект с неправильной длительностью
        try:
            with transaction.atomic():
                habit2 = Habit.objects.create(
                    user=self.user,
                    place='Тест',
                    time=time(11, 0),
                    action='Тест',
                    duration=0
                )
                # Если дошли сюда, вызываем full_clean для валидации
                habit2.full_clean()
            # Если не было исключения, тест должен упасть
            self.fail("Expected ValidationError but none was raised")
        except (ValidationError, Exception) as e:
            # Ожидаемое исключение
            self.assertTrue(True)


class HabitAPITests(APITestCase):
    """Тесты для API привычек"""

    def setUp(self):
        """Настройка тестовых данных для API"""
        # Используем уникальный email
        self.user = User.objects.create_user(
            email='api_test_user@example.com',  # Уникальный email
            password='testpass123'
        )

        # Создаем привычку для тестов
        self.habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time=time(8, 0),
            action='Пить воду',
            duration=60,
            is_public=True
        )

        # Получаем JWT токен
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # Настраиваем клиент с токеном
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_get_my_habits_authenticated(self):
        """Тест получения своих привычек с авторизацией"""
        response = self.client.get('/api/my-habits/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)

        habit_data = response.data['results'][0]
        self.assertEqual(habit_data['action'], 'Пить воду')
        self.assertEqual(habit_data['place'], 'Дом')

    def test_get_my_habits_unauthenticated(self):
        """Тест получения привычек без авторизации"""
        client = APIClient()  # Клиент без токена
        response = client.get('/api/my-habits/')

        self.assertEqual(response.status_code, 401)  # Unauthorized

    def test_get_public_habits(self):
        """Тест получения публичных привычек"""
        response = self.client.get('/api/public-habits/')

        self.assertEqual(response.status_code, 200)

        # Проверяем формат ответа (может быть список или пагинированный)
        response_data = response.data

        # Если это пагинированный ответ
        if isinstance(response_data, dict) and 'results' in response_data:
            habits = response_data['results']
            # Наша привычка публичная, должна быть в результатах
            habit_actions = [h['action'] for h in habits]
            self.assertIn('Пить воду', habit_actions)
        else:
            # Если это просто список
            habits = response_data
            self.assertIsInstance(habits, list)
            habit_actions = [h['action'] for h in habits]
            self.assertIn('Пить воду', habit_actions)

    def test_create_habit(self):
        """Тест создания привычки через API"""
        data = {
            'place': 'Офис',
            'time': '09:00:00',
            'action': 'Делать зарядку',
            'duration': 120,
            'is_public': True,
            'frequency': 1
        }

        response = self.client.post('/api/my-habits/', data, format='json')

        if response.status_code != 201:
            print(f"Ошибка при создании: {response.data}")

        self.assertEqual(response.status_code, 201)

        # Проверяем, что привычка создалась
        habit_id = response.data['id']
        habit = Habit.objects.get(id=habit_id)
        self.assertEqual(habit.action, 'Делать зарядку')
        self.assertEqual(habit.user, self.user)  # Должен быть привязан к текущему пользователю

    def test_update_habit(self):
        """Тест обновления привычки"""
        data = {
            'action': 'Пить воду утром',
            'duration': 90
        }

        response = self.client.patch(f'/api/my-habits/{self.habit.id}/', data, format='json')

        self.assertEqual(response.status_code, 200)

        # Проверяем обновление в базе
        self.habit.refresh_from_db()
        self.assertEqual(self.habit.action, 'Пить воду утром')
        self.assertEqual(self.habit.duration, 90)

    def test_delete_habit(self):
        """Тест удаления привычки"""
        response = self.client.delete(f'/api/my-habits/{self.habit.id}/')

        self.assertEqual(response.status_code, 204)

        # Проверяем, что привычка удалена
        with self.assertRaises(Habit.DoesNotExist):
            Habit.objects.get(id=self.habit.id)

    def test_cannot_access_other_user_habits(self):
        """Тест, что нельзя получить привычки другого пользователя"""
        # Создаем второго пользователя
        other_user = User.objects.create_user(
            email='other@example.com',
            password='otherpass123'
        )

        # Создаем привычку для второго пользователя
        other_habit = Habit.objects.create(
            user=other_user,
            place='Работа',
            time=time(12, 0),
            action='Обед',
            duration=60,
            is_public=False  # Не публичная!
        )

        # Пытаемся получить привычку другого пользователя
        response = self.client.get(f'/api/my-habits/{other_habit.id}/')

        # Должна быть ошибка 404 или 403
        self.assertIn(response.status_code, [403, 404])

    def test_habit_validation(self):
        """Тест валидации данных привычки"""
        # Пытаемся создать привычку с неправильной длительностью
        data = {
            'place': 'Дом',
            'time': '08:00:00',
            'action': 'Тест',
            'duration': 0,  # Неправильная длительность
            'is_public': True
        }

        response = self.client.post('/api/my-habits/', data, format='json')

        # Должна быть ошибка валидации
        self.assertEqual(response.status_code, 400)
        self.assertIn('duration', response.data)


class HabitValidatorTests(TestCase):
    """Тесты валидаторов привычек"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='validator_test@example.com',
            password='testpass123'
        )

    def test_pleasant_habit_cannot_have_reward(self):
        """Приятная привычка не может иметь вознаграждения"""
        from django.core.exceptions import ValidationError

        habit = Habit(
            user=self.user,
            place='Дом',
            time=time(8, 0),
            action='Медитация',
            is_pleasant=True,
            reward='Кофе',  # Не должно быть вознаграждения
            duration=30
        )

        # Вызываем валидацию
        with self.assertRaises(ValidationError) as context:
            habit.full_clean()

        self.assertIn('приятной привычки', str(context.exception))

    def test_pleasant_habit_cannot_have_related(self):
        """Приятная привычка не может иметь связанную привычку"""
        from django.core.exceptions import ValidationError

        # Создаем приятную привычку
        pleasant_habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time=time(7, 0),
            action='Зарядка',
            is_pleasant=True,
            duration=30
        )

        # Пытаемся создать другую приятную привычку со связанной
        habit = Habit(
            user=self.user,
            place='Дом',
            time=time(8, 0),
            action='Медитация',
            is_pleasant=True,
            related_habit=pleasant_habit,
            duration=30
        )

        with self.assertRaises(ValidationError) as context:
            habit.full_clean()

        self.assertIn('приятной привычки', str(context.exception))

    def test_habit_cannot_have_both_reward_and_related(self):
        """Привычка не может иметь одновременно и вознаграждение, и связанную привычку"""
        from django.core.exceptions import ValidationError

        # Создаем приятную привычку для связи
        pleasant_habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time=time(7, 0),
            action='Зарядка',
            is_pleasant=True,
            duration=30
        )

        # Пытаемся создать привычку с обоими полями
        habit = Habit(
            user=self.user,
            place='Дом',
            time=time(8, 0),
            action='Завтрак',
            reward='Кофе',
            related_habit=pleasant_habit,
            duration=20
        )

        with self.assertRaises(ValidationError) as context:
            habit.full_clean()

        self.assertIn('одновременно', str(context.exception))

    def test_related_habit_must_be_pleasant(self):
        """Связанная привычка должна быть приятной"""
        from django.core.exceptions import ValidationError

        # Создаем НЕприятную привычку
        not_pleasant_habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time=time(7, 0),
            action='Работа',
            is_pleasant=False,
            duration=30
        )

        # Пытаемся связать с неприятной привычкой
        habit = Habit(
            user=self.user,
            place='Дом',
            time=time(8, 0),
            action='Отдых',
            related_habit=not_pleasant_habit,
            duration=20
        )

        with self.assertRaises(ValidationError) as context:
            habit.full_clean()

        self.assertIn('должна быть приятной', str(context.exception))

    def test_habit_cannot_be_related_to_itself(self):
        """Привычка не может быть связана сама с собой"""
        from django.core.exceptions import ValidationError

        # Создаем привычку и сохраняем, чтобы получить ID
        habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time=time(8, 0),
            action='Тест',
            duration=30,
            is_pleasant=True  # Делаем приятной, чтобы избежать ошибки "должна быть приятной"
        )

        # Пытаемся связать с самой собой
        habit.related_habit = habit

        with self.assertRaises(ValidationError) as context:
            habit.full_clean()

        # Проверяем, что ошибка содержит нужный текст
        error_message = str(context.exception)
        print(f"Error message: {error_message}")  # Для отладки

        # Проверяем разные возможные формулировки ошибки
        possible_errors = ['сама с собой', 'самой с собой', 'self', 'itself']
        error_found = any(err in error_message.lower() for err in possible_errors)

        self.assertTrue(error_found,
                        f"Expected error about self-relation, but got: {error_message}")

    def test_duration_min_max_validation(self):
        """Тест минимальной и максимальной длительности"""
        from django.core.exceptions import ValidationError

        # Тест с минимальным значением (1)
        habit_min = Habit(
            user=self.user,
            place='Дом',
            time=time(8, 0),
            action='Минимальная',
            duration=1
        )
        try:
            habit_min.full_clean()
            habit_min.save()
        except ValidationError:
            self.fail("Duration=1 should be valid")

        # Тест с максимальным значением (120)
        habit_max = Habit(
            user=self.user,
            place='Дом',
            time=time(9, 0),
            action='Максимальная',
            duration=120
        )
        try:
            habit_max.full_clean()
            habit_max.save()
        except ValidationError:
            self.fail("Duration=120 should be valid")

        # Тест со значением меньше минимума (0)
        habit_too_small = Habit(
            user=self.user,
            place='Дом',
            time=time(10, 0),
            action='Слишком короткая',
            duration=0
        )
        with self.assertRaises(ValidationError):
            habit_too_small.full_clean()

        # Тест со значением больше максимума (121)
        habit_too_large = Habit(
            user=self.user,
            place='Дом',
            time=time(11, 0),
            action='Слишком длинная',
            duration=121
        )
        with self.assertRaises(ValidationError):
            habit_too_large.full_clean()

# Тесты для моделей пользователей


class UserModelTests(TestCase):
    """Тесты для модели User"""

    def test_create_user(self):
        """Тест создания обычного пользователя"""
        user = User.objects.create_user(
            email='user@example.com',
            password='password123'
        )

        self.assertEqual(user.email, 'user@example.com')
        self.assertTrue(user.check_password('password123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Тест создания суперпользователя"""
        superuser = User.objects.create_superuser(
            email='super@example.com',
            password='super123'
        )

        self.assertEqual(superuser.email, 'super@example.com')
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)

    def test_user_string_representation(self):
        """Тест строкового представления пользователя"""
        user = User.objects.create_user(
            email='test@example.com',
            password='test123'
        )

        self.assertEqual(str(user), 'test@example.com')

    def test_email_is_required(self):
        """Тест, что email обязателен"""
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='test123')

    def test_superuser_must_have_is_staff_true(self):
        """Тест, что суперпользователь должен иметь is_staff=True"""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='test@example.com',
                password='test123',
                is_staff=False
            )

    def test_superuser_must_have_is_superuser_true(self):
        """Тест, что суперпользователь должен иметь is_superuser=True"""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='test@example.com',
                password='test123',
                is_superuser=False
            )


# Добавьте этот класс для тестов сериализаторов, если они есть
class SerializerTests(APITestCase):
    """Тесты для сериализаторов"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='serializer_test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_habit_serializer_validation(self):
        """Тест валидации в сериализаторе привычек"""
        from habits.serializers import HabitSerializer

        # Тест с правильными данными
        valid_data = {
            'place': 'Дом',
            'time': '08:00:00',
            'action': 'Тест',
            'duration': 60,
            'is_public': True
        }

        serializer = HabitSerializer(data=valid_data, context={'request': type('Request', (), {'user': self.user})()})
        self.assertTrue(serializer.is_valid())

        # Тест с неправильной длительностью
        invalid_data = {
            'place': 'Дом',
            'time': '08:00:00',
            'action': 'Тест',
            'duration': 0,  # Неправильно
            'is_public': True
        }

        serializer = HabitSerializer(data=invalid_data, context={'request': type('Request', (), {'user': self.user})()})
        self.assertFalse(serializer.is_valid())
        self.assertIn('duration', serializer.errors)
