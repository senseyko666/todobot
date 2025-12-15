@echo off
echo 🚀 Запуск ToDo Bot проекта
echo ==========================

REM Проверяем наличие Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker не установлен. Установите Docker Desktop.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose не установлен.
    pause
    exit /b 1
)

REM Проверяем наличие .env файла
if not exist .env (
    echo 📝 Создаем .env файл из шаблона...
    copy .env.todo .env
    echo ⚠️  ВАЖНО: Отредактируйте .env файл и укажите BOT_TOKEN!
    echo    Получите токен у @BotFather в Telegram
    pause
)

REM Останавливаем существующие контейнеры
echo 🛑 Останавливаем существующие контейнеры...
docker-compose down

REM Собираем образы
echo 🔨 Собираем Docker образы...
docker-compose build

REM Запускаем сервисы
echo 🚀 Запускаем сервисы...
docker-compose up -d postgres redis

REM Ждем готовности базы данных
echo ⏳ Ждем готовности PostgreSQL...
timeout /t 10 /nobreak >nul

REM Запускаем Django
echo 🌐 Запускаем Django...
docker-compose up -d django

REM Ждем готовности Django
echo ⏳ Ждем готовности Django...
timeout /t 15 /nobreak >nul

REM Выполняем миграции
echo 📊 Выполняем миграции базы данных...
docker-compose exec django python manage.py makemigrations
docker-compose exec django python manage.py migrate

REM Создаем начальные данные
echo 📋 Создаем начальные категории...
docker-compose exec django python manage.py create_initial_data

REM Создаем суперпользователя
echo 👤 Создание суперпользователя для Django Admin...
docker-compose exec django python manage.py createsuperuser

REM Запускаем остальные сервисы
echo 🔄 Запускаем Celery и Telegram Bot...
docker-compose up -d

REM Показываем статус
echo.
echo ✅ Проект запущен!
echo.
echo 📊 Статус сервисов:
docker-compose ps

echo.
echo 🌐 Доступные сервисы:
echo   • Django Admin: http://localhost:8000/admin/
echo   • Django API: http://localhost:8000/api/
echo   • Telegram Bot: найдите вашего бота в Telegram
echo.
echo 📝 Для просмотра логов:
echo   docker-compose logs -f telegram-bot
echo   docker-compose logs -f django
echo.
echo 🛑 Для остановки:
echo   docker-compose down

pause