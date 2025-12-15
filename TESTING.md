# 🧪 Тестирование ToDo Bot

## Быстрая проверка работоспособности

### 1. Запуск проекта
```bash
# Linux/Mac
./start_todo_project.sh

# Windows
start_todo_project.bat
```

### 2. Проверка сервисов
```bash
# Статус всех контейнеров
docker-compose ps

# Логи Django
docker-compose logs django

# Логи бота
docker-compose logs telegram-bot

# Логи Celery
docker-compose logs celery
```

### 3. Тестирование Django API

**Проверка категорий:**
```bash
curl http://localhost:8000/api/categories/
```

**Создание задачи через API:**
```bash
curl -X POST http://localhost:8000/api/tasks/create_for_telegram/ \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_user_id": 123456789,
    "title": "Тестовая задача",
    "description": "Описание тестовой задачи",
    "priority": "high"
  }'
```

**Получение задач пользователя:**
```bash
curl "http://localhost:8000/api/tasks/by_telegram_user/?telegram_user_id=123456789"
```

**Статистика задач:**
```bash
curl "http://localhost:8000/api/tasks/stats/?telegram_user_id=123456789"
```

### 4. Тестирование Telegram бота

1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Проверьте основные функции:
   - Просмотр списка задач
   - Создание новой задачи
   - Отметка задачи как выполненной

### 5. Тестирование Django Admin

1. Откройте http://localhost:8000/admin/
2. Войдите с созданными учетными данными
3. Проверьте:
   - Список категорий
   - Список задач
   - Возможность редактирования

## Проверка требований тестового задания

### ✅ Django Backend
- [x] Сервис для управления задачами ToDo List
- [x] Задачи поддерживают категории (теги)
- [x] Привязка к пользователям
- [x] Кастомные PK (не UUID, не random, не автоинкременты)
- [x] CRUD API для задач и категорий
- [x] Административный интерфейс
- [x] Часовой пояс America/Adak

### ✅ Aiogram и Aiogram-Dialog
- [x] Телеграм-бот для работы с ToDo List
- [x] Просмотр списка задач с категориями
- [x] Показ даты создания задач
- [x] Добавление задач через диалоговое взаимодействие
- [x] Связь с Django через REST API

### ✅ Celery
- [x] Уведомления при наступлении даты исполнения
- [x] Celery Worker для фоновых задач
- [x] Celery Beat для планировщика

### ✅ Docker
- [x] Docker-compose для всех сервисов
- [x] Django, PostgreSQL, Redis, Telegram-бот
- [x] Корректный запуск и взаимодействие

## Отладка проблем

### Проблема: Бот не отвечает
```bash
# Проверьте логи бота
docker-compose logs telegram-bot

# Проверьте переменную BOT_TOKEN в .env
cat .env | grep BOT_TOKEN

# Перезапустите бота
docker-compose restart telegram-bot
```

### Проблема: Django API недоступен
```bash
# Проверьте статус Django
docker-compose ps django

# Проверьте логи
docker-compose logs django

# Проверьте миграции
docker-compose exec django python manage.py showmigrations
```

### Проблема: База данных недоступна
```bash
# Проверьте PostgreSQL
docker-compose ps postgres

# Подключитесь к базе
docker-compose exec postgres psql -U postgres -d todo_db
```

### Проблема: Celery не работает
```bash
# Проверьте Celery worker
docker-compose logs celery

# Проверьте Redis
docker-compose exec redis redis-cli ping

# Проверьте задачи в очереди
docker-compose exec django python manage.py shell
>>> from celery import current_app
>>> current_app.control.inspect().active()
```

## Полезные команды

```bash
# Полная перезагрузка
docker-compose down && docker-compose up -d

# Пересборка образов
docker-compose build --no-cache

# Очистка Docker
docker system prune -a

# Создание суперпользователя
docker-compose exec django python manage.py createsuperuser

# Выполнение миграций
docker-compose exec django python manage.py migrate

# Создание начальных данных
docker-compose exec django python manage.py create_initial_data
```