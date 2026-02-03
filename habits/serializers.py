from rest_framework import serializers
from .models import Habit

class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = [
            'id', 'place', 'time', 'action', 'is_pleasant',
            'related_habit', 'frequency', 'reward', 'duration',
            'is_public', 'created_at'
        ]
        read_only_fields = ['created_at', 'user']

    def validate(self, data):
        """Дополнительная валидация"""
        # Проверка, что пользователь не указал и reward и related_habit
        if data.get('related_habit') and data.get('reward'):
            raise serializers.ValidationError(
                "Нельзя одновременно указывать связанную привычку и вознаграждение."
            )

        # Проверка для приятных привычек
        if data.get('is_pleasant') and (data.get('reward') or data.get('related_habit')):
            raise serializers.ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки."
            )

        return data

class PublicHabitSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Habit
        fields = [
            'id', 'user_email', 'place', 'time', 'action',
            'frequency', 'duration', 'created_at'
        ]
        read_only_fields = fields
