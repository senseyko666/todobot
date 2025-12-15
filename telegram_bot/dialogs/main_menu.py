"""
Главное меню бота.
"""
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Column, Start
from aiogram.types import CallbackQuery

from states import MainMenuSG, TaskListSG, CreateTaskSG


async def on_tasks_list(callback: CallbackQuery, button: Button, manager: DialogManager):
    """Переход к списку задач."""
    await manager.start(TaskListSG.list)


async def on_create_task(callback: CallbackQuery, button: Button, manager: DialogManager):
    """Переход к созданию задачи."""
    await manager.start(CreateTaskSG.title)


async def get_main_menu_data(dialog_manager: DialogManager, **kwargs):
    """Получает данные для главного меню."""
    return {
        'user_name': dialog_manager.event.from_user.first_name or 'Пользователь'
    }


main_menu_dialog = Dialog(
    Window(
        Format("👋 Привет, {user_name}!\n\n"
               "Это ToDo бот для управления задачами.\n"
               "Выберите действие:"),
        Column(
            Start(
                Const("📋 Мои задачи"),
                id="tasks_list",
                state=TaskListSG.list
            ),
            Start(
                Const("➕ Создать задачу"),
                id="create_task", 
                state=CreateTaskSG.title
            ),
        ),
        getter=get_main_menu_data,
        state=MainMenuSG.main,
    ),
)