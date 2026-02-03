# users/test_coverage.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .serializers import UserSerializer, RegisterSerializer

User = get_user_model()


class TestUserModel(TestCase):
    """Тесты модели пользователя."""
    
    def test_create_user(self):
        """Тест создания обычного пользователя."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        """Тест создания суперпользователя."""
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
    
    def test_user_str_representation(self):
        """Тест строкового представления пользователя."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(str(user), 'test@example.com')


class TestUserSerializer(TestCase):
    """Тесты сериализатора пользователя."""

    def test_user_serializer_valid(self):
        """Тест валидного UserSerializer."""
        # Создаем пользователя через модель
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

        # Тестируем сериализатор
        serializer = UserSerializer(user)
        data = serializer.data

        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['first_name'], 'Test')
        self.assertEqual(data['last_name'], 'User')
        # Пароль не должен быть в выводе
        self.assertNotIn('password', data)

    def test_user_serializer_update(self):
        """Тест обновления через UserSerializer."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'password': 'newpassword123'
        }

        serializer = UserSerializer(user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'Name')
        self.assertTrue(updated_user.check_password('newpassword123'))

    def test_user_serializer_invalid_email(self):
        """Тест сериализатора с невалидным email."""
        data = {
            'email': 'invalid-email',
            'password': 'testpass123',
            'password2': 'testpass123'
        }

        # Используем RegisterSerializer
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)


class TestRegistrationAPI(APITestCase):
    """Тесты API регистрации."""

    def test_user_registration_success(self):
        """Тест успешной регистрации пользователя."""
        data = {
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }

        # Исправьте путь на '/api/register/' вместо '/api/users/register/'
        response = self.client.post('/api/register/', data, format='json')
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('message', response.data)

        # Проверяем, что пользователь создан
        user_exists = User.objects.filter(email='newuser@example.com').exists()
        self.assertTrue(user_exists)

    def test_user_registration_password_mismatch(self):
        """Тест регистрации с несовпадающими паролями."""
        data = {
            'email': 'newuser@example.com',
            'password': 'pass123',
            'password2': 'differentpass',
            'first_name': 'New',
            'last_name': 'User'
        }

        # Исправьте путь на '/api/register/' вместо '/api/users/register/'
        response = self.client.post('/api/register/', data, format='json')
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)


class TestRegisterSerializer(TestCase):
    """Тесты сериализатора регистрации (RegisterSerializer)."""

    def test_register_serializer_valid(self):
        """Тест валидного RegisterSerializer."""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }

        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))

    def test_register_serializer_password_mismatch(self):
        """Тест RegisterSerializer с несовпадающими паролями."""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'different',
            'first_name': 'Test',
            'last_name': 'User'
        }

        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
