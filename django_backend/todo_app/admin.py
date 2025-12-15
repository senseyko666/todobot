"""
Административный интерфейс для ToDo приложения.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Task


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админка для категорий."""
    list_display = ['name', 'description', 'color_display', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at']
    
    def color_display(self, obj):
        """Отображает цвет категории."""
        return format_html(
            '<span style="background-color: {}; padding: 5px 10px; color: white; border-radius: 3px;">{}</span>',
            obj.color,
            obj.color
        )
    color_display.short_description = 'Цвет'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Админка для задач."""
    list_display = [
        'title', 'user', 'category', 'status', 'priority', 
        'due_date', 'is_overdue_display', 'created_at'
    ]
    list_filter = [
        'status', 'priority', 'category', 'created_at', 'due_date'
    ]
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('id', 'title', 'description', 'user', 'telegram_user_id')
        }),
        ('Параметры задачи', {
            'fields': ('status', 'priority', 'category', 'due_date')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_overdue_display(self, obj):
        """Отображает статус просрочки."""
        if obj.is_overdue:
            return format_html(
                '<span style="color: red; font-weight: bold;">Просрочена</span>'
            )
        return format_html(
            '<span style="color: green;">В срок</span>'
        )
    is_overdue_display.short_description = 'Просрочка'
    
    actions = ['mark_completed', 'mark_pending']
    
    def mark_completed(self, request, queryset):
        """Отмечает задачи как завершенные."""
        from django.utils import timezone
        updated = queryset.update(
            status='completed',
            completed_at=timezone.now()
        )
        self.message_user(
            request,
            f'{updated} задач отмечено как завершенные.'
        )
    mark_completed.short_description = 'Отметить как завершенные'
    
    def mark_pending(self, request, queryset):
        """Отмечает задачи как ожидающие."""
        updated = queryset.update(
            status='pending',
            completed_at=None
        )
        self.message_user(
            request,
            f'{updated} задач отмечено как ожидающие.'
        )
    mark_pending.short_description = 'Отметить как ожидающие'