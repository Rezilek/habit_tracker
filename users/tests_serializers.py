import pytest
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.mark.django_db
class TestUserSerializers:
    """Тесты для сериализаторов пользователей."""

    def test_user_serializer(self):
        """Тест сериализатора пользователя."""
        user = User.objects.create_user(
            email='serializer@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )

        serializer = UserSerializer(user)
        data = serializer.data

        assert data['email'] == 'serializer@example.com'
        assert data['first_name'] == 'John'
        assert data['last_name'] == 'Doe'
        assert 'password' not in data  # Пароль не должен быть в выводе
        assert 'id' in data

    def test_user_serializer_create(self):
        """Тест создания пользователя через сериализатор."""
        serializer = UserSerializer(data={
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'first_name': 'Jane',
            'last_name': 'Smith'
        })

        assert serializer.is_valid()
        user = serializer.save()

        assert user.email == 'newuser@example.com'
        assert user.first_name == 'Jane'
        assert user.check_password('newpass123')

    def test_custom_token_serializer(self):
        """Тест кастомного сериализатора токена."""
        user = User.objects.create_user(
            email='token@example.com',
            password='testpass123'
        )

        serializer = CustomTokenObtainPairSerializer()
        token = serializer.get_token(user)

        assert token is not None
        assert 'user_id' in token
        assert token['user_id'] == user.id
