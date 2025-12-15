"""
Сериализаторы для API ToDo приложения.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Task


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'color', 'created_at']
        read_only_fields = ['id', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    """Сериализатор для задач."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'category', 'category_name', 'user', 'user_username',
            'telegram_user_id', 'due_date', 'completed_at',
            'created_at', 'updated_at', 'is_overdue'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Создает новую задачу."""
        # Если статус завершен, устанавливаем время завершения
        if validated_data.get('status') == 'completed':
            from django.utils import timezone
            validated_data['completed_at'] = timezone.now()
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Обновляет задачу."""
        # Если статус изменился на завершен, устанавливаем время завершения
        if (validated_data.get('status') == 'completed' and 
            instance.status != 'completed'):
            from django.utils import timezone
            validated_data['completed_at'] = timezone.now()
        
        # Если статус изменился с завершенного, убираем время завершения
        elif (validated_data.get('status') != 'completed' and 
              instance.status == 'completed'):
            validated_data['completed_at'] = None
        
        return super().update(instance, validated_data)


class TaskCreateSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор для создания задач через бота."""
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'category', 'priority', 'due_date', 'telegram_user_id']
    
    def create(self, validated_data):
        """Создает задачу с автоматическим созданием пользователя."""
        telegram_user_id = validated_data.get('telegram_user_id')
        
        if telegram_user_id:
            # Пытаемся найти или создать пользователя по Telegram ID
            user, created = User.objects.get_or_create(
                username=f'tg_{telegram_user_id}',
                defaults={
                    'first_name': f'User_{telegram_user_id}',
                    'is_active': True
                }
            )
            validated_data['user'] = user
        
        return super().create(validated_data)