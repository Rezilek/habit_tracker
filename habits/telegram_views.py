# habits/telegram_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from .models import TelegramUser
import random
import string

User = get_user_model()


class TelegramConnectView(APIView):
    """Подключение Telegram аккаунта"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Получение кода верификации для Telegram"""
        user = request.user
        
        # Генерируем случайный код
        code = ''.join(random.choices(string.digits, k=6))
        
        # Сохраняем или обновляем Telegram пользователя
        telegram_user, created = TelegramUser.objects.get_or_create(
            user=user,
            defaults={'verification_code': code}
        )
        
        if not created:
            telegram_user.verification_code = code
            telegram_user.verified = False
            telegram_user.save()
        
        return Response({
            'verification_code': code,
            'instructions': f'Отправьте код {code} боту для привязки аккаунта'
        })
    
    def post(self, request):
        """Подтверждение верификации"""
        user = request.user
        chat_id = request.data.get('chat_id')
        username = request.data.get('username')
        
        try:
            telegram_user = TelegramUser.objects.get(user=user)
            telegram_user.chat_id = chat_id
            telegram_user.username = username
            telegram_user.verified = True
            telegram_user.save()
            
            return Response({
                'status': 'success',
                'message': 'Telegram аккаунт успешно привязан'
            })
        except TelegramUser.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Сначала получите код верификации'
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def telegram_webhook(request):
    """Вебхук для получения сообщений от Telegram бота"""
    # В реальном приложении здесь будет логика обработки сообщений от Telegram
    # Для учебного проекта просто возвращаем успех
    return Response({'status': 'webhook received'})
