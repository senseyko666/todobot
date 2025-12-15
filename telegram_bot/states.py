"""
Состояния для диалогов бота.
"""
from aiogram.fsm.state import State, StatesGroup


class MainMenuSG(StatesGroup):
    """Состояния главного меню."""
    main = State()


class TaskListSG(StatesGroup):
    """Состояния списка задач."""
    list = State()
    task_detail = State()


class CreateTaskSG(StatesGroup):
    """Состояния создания задачи."""
    title = State()
    description = State()
    category = State()
    priority = State()
    confirm = State()