# habits/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import telegram_views
from .views import HabitViewSet, PublicHabitViewSet
from .telegram_views import TelegramConnectView, telegram_webhook

router = DefaultRouter()
router.register(r'my-habits', HabitViewSet, basename='my-habits')
router.register(r'public-habits', PublicHabitViewSet, basename='public-habits')

urlpatterns = [
    path('telegram/connect/', TelegramConnectView.as_view(), name='telegram-connect'),
    path('telegram/webhook/', telegram_views.telegram_webhook, name='telegram-webhook'),
    path('', include(router.urls)),
]

