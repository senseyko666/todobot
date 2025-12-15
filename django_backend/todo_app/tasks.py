"""
Celery задачи для уведомлений о задачах.
"""
from celery import shared_task
from django.utils import timezone
from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_task_notification(task_id):
    """Отправляет уведомление о наступлении срока задачи."""
    try:
        from .models import Task
        
        task = Task.objects.get(id=task_id)
        
        # Проверяем, что задача еще не завершена
        if task.status == 'completed':
            logger.info(f"Task {task_id} already completed, skipping notification")
            return
        
        # Отправляем уведомление в Telegram бот
        if task.telegram_user_id:
            send_telegram_notification.delay(
                task.telegram_user_id,
                f"⏰ Напоминание о задаче!\n\n"
                f"📝 {task.title}\n"
                f"📅 Срок: {task.due_date.strftime('%d.%m.%Y %H:%M')}\n"
                f"🏷️ Категория: {task.category.name if task.category else 'Без категории'}"
            )
        
        logger.info(f"Notification sent for task {task_id}")
        
    except Exception as e:
        logger.error(f"Error sending task notification for {task_id}: {e}")


@shared_task
def send_telegram_notification(telegram_user_id, message):
    """Отправляет уведомление в Telegram."""
    try:
        # URL для отправки сообщения через бота
        bot_api_url = getattr(settings, 'TELEGRAM_BOT_API_URL', None)
        
        if not bot_api_url:
            logger.warning("TELEGRAM_BOT_API_URL not configured")
            return
        
        response = requests.post(
            f"{bot_api_url}/send_notification",
            json={
                'user_id': telegram_user_id,
                'message': message
            },
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"Telegram notification sent to {telegram_user_id}")
        else:
            logger.error(f"Failed to send Telegram notification: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error sending Telegram notification: {e}")


@shared_task
def check_overdue_tasks():
    """Проверяет просроченные задачи и отправляет уведомления."""
    try:
        from .models import Task
        
        now = timezone.now()
        
        # Находим просроченные задачи, по которым еще не отправлялись уведомления
        overdue_tasks = Task.objects.filter(
            due_date__lt=now,
            status__in=['pending', 'in_progress']
        )
        
        for task in overdue_tasks:
            if task.telegram_user_id:
                send_telegram_notification.delay(
                    task.telegram_user_id,
                    f"🚨 Задача просрочена!\n\n"
                    f"📝 {task.title}\n"
                    f"📅 Должна была быть выполнена: {task.due_date.strftime('%d.%m.%Y %H:%M')}\n"
                    f"🏷️ Категория: {task.category.name if task.category else 'Без категории'}"
                )
        
        logger.info(f"Checked {overdue_tasks.count()} overdue tasks")
        
    except Exception as e:
        logger.error(f"Error checking overdue tasks: {e}")


@shared_task
def schedule_task_notification(task_id, notification_time):
    """Планирует уведомление о задаче."""
    try:
        from celery import current_app
        
        # Планируем задачу на определенное время
        current_app.send_task(
            'todo_app.tasks.send_task_notification',
            args=[task_id],
            eta=notification_time
        )
        
        logger.info(f"Scheduled notification for task {task_id} at {notification_time}")
        
    except Exception as e:
        logger.error(f"Error scheduling task notification: {e}")