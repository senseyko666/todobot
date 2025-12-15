"""
Модели для ToDo приложения.
"""
import time
import hashlib
from django.db import models
from django.contrib.auth.models import User


def generate_custom_id():
    """Генерирует кастомный ID на основе времени и хеша."""
    timestamp = str(int(time.time() * 1000000))  # микросекунды
    hash_obj = hashlib.md5(timestamp.encode())
    return hash_obj.hexdigest()[:12]  # 12 символов


class Category(models.Model):
    """Модель категории задач."""
    id = models.CharField(
        max_length=12, 
        primary_key=True, 
        default=generate_custom_id,
        editable=False
    )
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    color = models.CharField(max_length=7, default="#007bff", verbose_name="Цвет")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Task(models.Model):
    """Модель задачи."""
    
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('in_progress', 'В процессе'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
        ('urgent', 'Срочный'),
    ]
    
    id = models.CharField(
        max_length=12, 
        primary_key=True, 
        default=generate_custom_id,
        editable=False
    )
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(blank=True, verbose_name="Описание")
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name="Статус"
    )
    priority = models.CharField(
        max_length=20, 
        choices=PRIORITY_CHOICES, 
        default='medium',
        verbose_name="Приоритет"
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Категория"
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    telegram_user_id = models.BigIntegerField(
        null=True, 
        blank=True,
        verbose_name="Telegram ID"
    )
    due_date = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Срок выполнения"
    )
    completed_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Завершено"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    
    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['telegram_user_id']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    @property
    def is_overdue(self):
        """Проверяет, просрочена ли задача."""
        if not self.due_date or self.status == 'completed':
            return False
        from django.utils import timezone
        return timezone.now() > self.due_date