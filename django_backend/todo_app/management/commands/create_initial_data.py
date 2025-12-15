"""
Команда для создания начальных данных.
"""
from django.core.management.base import BaseCommand
from todo_app.models import Category


class Command(BaseCommand):
    help = 'Создает начальные категории для задач'

    def handle(self, *args, **options):
        categories = [
            {'name': 'Работа', 'description': 'Рабочие задачи', 'color': '#007bff'},
            {'name': 'Личное', 'description': 'Личные дела', 'color': '#28a745'},
            {'name': 'Покупки', 'description': 'Список покупок', 'color': '#ffc107'},
            {'name': 'Здоровье', 'description': 'Здоровье и спорт', 'color': '#dc3545'},
            {'name': 'Обучение', 'description': 'Образование и развитие', 'color': '#6f42c1'},
            {'name': 'Дом', 'description': 'Домашние дела', 'color': '#fd7e14'},
        ]

        created_count = 0
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'color': cat_data['color']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Создана категория: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Создано {created_count} новых категорий')
        )