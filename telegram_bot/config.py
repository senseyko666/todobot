"""
Конфигурация для Telegram бота.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

# Django API
DJANGO_API_URL = os.getenv('DJANGO_API_URL', 'http://localhost:8000/api')

# Redis для состояний диалогов
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/1')

# Логирование
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')