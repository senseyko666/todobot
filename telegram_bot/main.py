"""
Основной файл Telegram бота.
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode, setup_dialogs

from config import BOT_TOKEN, REDIS_URL
from states import MainMenuSG
from dialogs import main_menu_dialog, create_task_dialog, task_list_dialog

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создание бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def start_command(message: Message, dialog_manager: DialogManager):
    """Обработчик команды /start."""
    await dialog_manager.start(MainMenuSG.main, mode=StartMode.RESET_STACK)


async def main():
    """Главная функция запуска бота."""
    logger.info("Запуск ToDo бота...")
    
    # Регистрация диалогов
    dp.include_router(main_menu_dialog)
    dp.include_router(create_task_dialog)
    dp.include_router(task_list_dialog)
    
    # Настройка диалогов
    setup_dialogs(dp)
    
    # Регистрация обработчиков
    dp.message.register(start_command, CommandStart())
    
    try:
        # Удаление вебхука и запуск polling
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Бот запущен и готов к работе!")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())