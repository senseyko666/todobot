"""
API views для ToDo приложения.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Category, Task
from .serializers import CategorySerializer, TaskSerializer, TaskCreateSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet для категорий."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet для задач."""
    queryset = Task.objects.select_related('category', 'user').all()
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'category', 'user']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'due_date', 'priority']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Возвращает соответствующий сериализатор."""
        if self.action == 'create_for_telegram':
            return TaskCreateSerializer
        return TaskSerializer
    
    def get_queryset(self):
        """Фильтрует задачи по параметрам запроса."""
        queryset = super().get_queryset()
        
        # Фильтр по Telegram ID
        telegram_user_id = self.request.query_params.get('telegram_user_id')
        if telegram_user_id:
            queryset = queryset.filter(telegram_user_id=telegram_user_id)
        
        # Фильтр по просроченным задачам
        overdue = self.request.query_params.get('overdue')
        if overdue == 'true':
            from django.utils import timezone
            queryset = queryset.filter(
                due_date__lt=timezone.now(),
                status__in=['pending', 'in_progress']
            )
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def create_for_telegram(self, request):
        """Создает задачу для пользователя Telegram."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save()
            response_serializer = TaskSerializer(task)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_telegram_user(self, request):
        """Получает задачи пользователя по Telegram ID."""
        telegram_user_id = request.query_params.get('telegram_user_id')
        if not telegram_user_id:
            return Response(
                {'error': 'telegram_user_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tasks = self.get_queryset().filter(telegram_user_id=telegram_user_id)
        
        # Дополнительные фильтры
        status_filter = request.query_params.get('status')
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        
        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def mark_completed(self, request, pk=None):
        """Отмечает задачу как завершенную."""
        task = self.get_object()
        task.status = 'completed'
        from django.utils import timezone
        task.completed_at = timezone.now()
        task.save()
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Возвращает статистику задач."""
        telegram_user_id = request.query_params.get('telegram_user_id')
        queryset = self.get_queryset()
        
        if telegram_user_id:
            queryset = queryset.filter(telegram_user_id=telegram_user_id)
        
        stats = {
            'total': queryset.count(),
            'pending': queryset.filter(status='pending').count(),
            'in_progress': queryset.filter(status='in_progress').count(),
            'completed': queryset.filter(status='completed').count(),
            'cancelled': queryset.filter(status='cancelled').count(),
        }
        
        # Просроченные задачи
        from django.utils import timezone
        overdue_count = queryset.filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).count()
        stats['overdue'] = overdue_count
        
        return Response(stats)