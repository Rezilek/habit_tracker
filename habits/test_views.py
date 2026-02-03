# habits/test_views.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Habit
from .views import HabitViewSet, PublicHabitViewSet, HabitPagination

User = get_user_model()


class TestPagination(TestCase):
    """Тесты пагинации."""
    
    def test_pagination_class(self):
        """Тест класса пагинации."""
        pagination = HabitPagination()
        self.assertEqual(pagination.page_size, 5)
        self.assertEqual(pagination.page_size_query_param, 'page_size')
        self.assertEqual(pagination.max_page_size, 100)


class TestViewSets(TestCase):
    """Тесты viewset'ов."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        # Создаем несколько привычек
        for i in range(3):
            Habit.objects.create(
                user=self.user,
                place=f'Место {i}',
                time=f'{8 + i}:00:00',
                action=f'Действие {i}',
                duration=30,
                is_public=(i % 2 == 0)  # Каждая вторая публичная
            )
    
    def test_habit_viewset_get_queryset(self):
        """Тест get_queryset HabitViewSet."""
        viewset = HabitViewSet()
        viewset.request = type('Request', (), {'user': self.user})()
        
        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 3)
        
        # Проверяем, что все привычки принадлежат пользователю
        for habit in queryset:
            self.assertEqual(habit.user, self.user)
    
    def test_habit_viewset_perform_create(self):
        """Тест perform_create HabitViewSet."""
        viewset = HabitViewSet()
        
        # Мокаем serializer
        class MockSerializer:
            def __init__(self):
                self.validated_data = {}
            
            def save(self, **kwargs):
                self.saved_with = kwargs
        
        serializer = MockSerializer()
        viewset.request = type('Request', (), {'user': self.user})()
        
        viewset.perform_create(serializer)
        
        self.assertIn('user', serializer.saved_with)
        self.assertEqual(serializer.saved_with['user'], self.user)
    
    def test_public_habit_viewset_queryset(self):
        """Тест queryset PublicHabitViewSet."""
        viewset = PublicHabitViewSet()
        queryset = viewset.get_queryset()
        
        # Должны быть только публичные привычки
        public_count = Habit.objects.filter(is_public=True).count()
        self.assertEqual(queryset.count(), public_count)
        
        # Проверяем, что все привычки публичные
        for habit in queryset:
            self.assertTrue(habit.is_public)


class TestTelegramViews(TestCase):
    """Тесты Telegram views."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_telegram_connect_view_import(self):
        """Тест импорта Telegram views."""
        try:
            from habits.telegram_views import TelegramConnectView, telegram_webhook
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Не удалось импортировать Telegram views: {e}")

