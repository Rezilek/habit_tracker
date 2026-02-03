from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserTests(TestCase):
    """Тесты для кастомной модели пользователя"""

    def setUp(self):
        """Очищаем базу перед каждым тестом"""
        User.objects.all().delete()

    def test_create_user_with_email_successful(self):
        """Тест создания пользователя с email"""
        email = 'test@example.com'
        password = 'Testpass123'
        user = User.objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Тест нормализации email при создании пользователя"""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected in sample_emails:
            user = User.objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Тест, что создание пользователя без email вызывает ошибку"""
        with self.assertRaises(ValueError):
            User.objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Тест создания суперпользователя"""
        email = 'admin_test@example.com'  # Уникальный email для теста
        password = 'admin123'
        user = User.objects.create_superuser(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
