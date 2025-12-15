#!/bin/bash

echo "🚀 Запуск ToDo Bot проекта"
echo "=========================="

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и Docker Compose."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен."
    exit 1
fi

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "📝 Создаем .env файл из шаблона..."
    cp .env.todo .env
    echo "⚠️  ВАЖНО: Отредактируйте .env файл и укажите BOT_TOKEN!"
    echo "   Получите токен у @BotFather в Telegram"
    read -p "Нажмите Enter после настройки .env файла..."
fi

# Останавливаем существующие контейнеры
echo "🛑 Останавливаем существующие контейнеры..."
docker-compose down

# Собираем образы
echo "🔨 Собираем Docker образы..."
docker-compose build

# Запускаем сервисы
echo "🚀 Запускаем сервисы..."
docker-compose up -d postgres redis

# Ждем готовности базы данных
echo "⏳ Ждем готовности PostgreSQL..."
sleep 10

# Запускаем Django
echo "🌐 Запускаем Django..."
docker-compose up -d django

# Ждем готовности Django
echo "⏳ Ждем готовности Django..."
sleep 15

# Выполняем миграции
echo "📊 Выполняем миграции базы данных..."
docker-compose exec django python manage.py makemigrations
docker-compose exec django python manage.py migrate

# Создаем начальные данные
echo "📋 Создаем начальные категории..."
docker-compose exec django python manage.py create_initial_data

# Создаем суперпользователя
echo "👤 Создание суперпользователя для Django Admin..."
docker-compose exec django python manage.py createsuperuser

# Запускаем остальные сервисы
echo "🔄 Запускаем Celery и Telegram Bot..."
docker-compose up -d

# Показываем статус
echo ""
echo "✅ Проект запущен!"
echo ""
echo "📊 Статус сервисов:"
docker-compose ps

echo ""
echo "🌐 Доступные сервисы:"
echo "  • Django Admin: http://localhost:8000/admin/"
echo "  • Django API: http://localhost:8000/api/"
echo "  • Telegram Bot: найдите вашего бота в Telegram"
echo ""
echo "📝 Для просмотра логов:"
echo "  docker-compose logs -f telegram-bot"
echo "  docker-compose logs -f django"
echo ""
echo "🛑 Для остановки:"
echo "  docker-compose down"