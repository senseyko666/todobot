"""
Диалоги для работы с задачами.
"""
from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Column, Back, Start, Select, Group
from aiogram_dialog.widgets.input import TextInput

from states import TaskListSG, CreateTaskSG, MainMenuSG
from api_client import APIClient


# Список задач
async def get_tasks_data(dialog_manager: DialogManager, **kwargs):
    """Получает данные о задачах пользователя."""
    user_id = dialog_manager.event.from_user.id
    
    async with APIClient() as api:
        tasks = await api.get_tasks(user_id)
        stats = await api.get_task_stats(user_id)
    
    return {
        'tasks': tasks,
        'has_tasks': len(tasks) > 0,
        'stats': stats
    }


async def on_task_selected(callback: CallbackQuery, widget, manager: DialogManager, task_id: str):
    """Обработка выбора задачи."""
    manager.dialog_data['selected_task_id'] = task_id
    await manager.switch_to(TaskListSG.task_detail)


async def get_task_detail_data(dialog_manager: DialogManager, **kwargs):
    """Получает детальную информацию о задаче."""
    task_id = dialog_manager.dialog_data.get('selected_task_id')
    user_id = dialog_manager.event.from_user.id
    
    if not task_id:
        return {'task': None}
    
    async with APIClient() as api:
        tasks = await api.get_tasks(user_id)
    
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    return {
        'task': task,
        'task_title': task['title'] if task else 'Задача не найдена',
        'task_description': task['description'] if task else '',
        'task_status': task['status'] if task else '',
        'task_priority': task['priority'] if task else '',
        'task_category': task['category_name'] if task and task.get('category_name') else 'Без категории',
        'task_created': task['created_at'][:10] if task else '',  # Только дата
        'is_completed': task['status'] == 'completed' if task else False
    }


async def on_complete_task(callback: CallbackQuery, button: Button, manager: DialogManager):
    """Отмечает задачу как завершенную."""
    task_id = manager.dialog_data.get('selected_task_id')
    
    if task_id:
        async with APIClient() as api:
            await api.mark_task_completed(task_id)
        
        await callback.answer("✅ Задача отмечена как завершенная!")
        await manager.switch_to(TaskListSG.list)


task_list_dialog = Dialog(
    Window(
        Format("📋 Ваши задачи\n\n"
               "📊 Статистика:\n"
               "• Всего: {stats[total]}\n"
               "• В ожидании: {stats[pending]}\n"
               "• Завершено: {stats[completed]}\n"
               "• Просрочено: {stats[overdue]}"),
        Select(
            Format("📝 {item[title]} ({item[status]})"),
            items="tasks",
            item_id_getter=lambda item: item['id'],
            id="task_list",
            on_click=on_task_selected,
        ),
        Format("\n📝 У вас пока нет задач", when=~F["has_tasks"]),
        Column(
            Start(
                Const("➕ Создать задачу"),
                id="create_new_task",
                state=CreateTaskSG.title
            ),
            Start(
                Const("🏠 Главное меню"),
                id="main_menu",
                state=MainMenuSG.main
            ),
        ),
        getter=get_tasks_data,
        state=TaskListSG.list,
    ),
    Window(
        Format("📝 {task_title}\n\n"
               "📄 Описание: {task_description}\n"
               "📊 Статус: {task_status}\n"
               "⚡ Приоритет: {task_priority}\n"
               "🏷️ Категория: {task_category}\n"
               "📅 Создано: {task_created}"),
        Column(
            Button(
                Const("✅ Отметить выполненной"),
                id="complete_task",
                on_click=on_complete_task,
                when=~F["is_completed"]
            ),
            Back(Const("⬅️ Назад к списку")),
        ),
        getter=get_task_detail_data,
        state=TaskListSG.task_detail,
    ),
)


# Создание задачи
async def on_title_input(message: Message, widget, dialog_manager: DialogManager, text: str):
    """Обработка ввода заголовка задачи."""
    dialog_manager.dialog_data['task_title'] = text
    await dialog_manager.switch_to(CreateTaskSG.description)


async def on_description_input(message: Message, widget, dialog_manager: DialogManager, text: str):
    """Обработка ввода описания задачи."""
    dialog_manager.dialog_data['task_description'] = text
    await dialog_manager.switch_to(CreateTaskSG.category)


async def get_categories_data(dialog_manager: DialogManager, **kwargs):
    """Получает список категорий."""
    async with APIClient() as api:
        categories = await api.get_categories()
    
    return {
        'categories': categories,
        'has_categories': len(categories) > 0
    }


async def on_category_selected(callback: CallbackQuery, widget, manager: DialogManager, category_id: str):
    """Обработка выбора категории."""
    manager.dialog_data['task_category'] = category_id
    await manager.switch_to(CreateTaskSG.priority)


async def on_skip_category(callback: CallbackQuery, button: Button, manager: DialogManager):
    """Пропуск выбора категории."""
    manager.dialog_data['task_category'] = None
    await manager.switch_to(CreateTaskSG.priority)


async def on_priority_selected(callback: CallbackQuery, widget, manager: DialogManager, priority: str):
    """Обработка выбора приоритета."""
    manager.dialog_data['task_priority'] = priority
    await manager.switch_to(CreateTaskSG.confirm)


async def get_task_preview_data(dialog_manager: DialogManager, **kwargs):
    """Получает данные для предпросмотра задачи."""
    data = dialog_manager.dialog_data
    
    # Получаем название категории
    category_name = "Без категории"
    if data.get('task_category'):
        async with APIClient() as api:
            categories = await api.get_categories()
        category = next((c for c in categories if c['id'] == data['task_category']), None)
        if category:
            category_name = category['name']
    
    return {
        'title': data.get('task_title', ''),
        'description': data.get('task_description', ''),
        'category': category_name,
        'priority': data.get('task_priority', 'medium')
    }


async def on_create_task_confirm(callback: CallbackQuery, button: Button, manager: DialogManager):
    """Создает задачу."""
    data = manager.dialog_data
    user_id = manager.event.from_user.id
    
    async with APIClient() as api:
        task = await api.create_task(
            telegram_user_id=user_id,
            title=data.get('task_title', ''),
            description=data.get('task_description', ''),
            category_id=data.get('task_category'),
            priority=data.get('task_priority', 'medium')
        )
    
    if task:
        await callback.answer("✅ Задача создана!")
        await manager.start(TaskListSG.list)
    else:
        await callback.answer("❌ Ошибка при создании задачи")


create_task_dialog = Dialog(
    Window(
        Const("📝 Создание новой задачи\n\n"
              "Введите заголовок задачи:"),
        TextInput(
            id="title_input",
            on_success=on_title_input,
        ),
        Back(Const("⬅️ Отмена")),
        state=CreateTaskSG.title,
    ),
    Window(
        Format("📝 Заголовок: {dialog_data[task_title]}\n\n"
               "Введите описание задачи (или отправьте /skip для пропуска):"),
        TextInput(
            id="description_input",
            on_success=on_description_input,
        ),
        Button(
            Const("⏭️ Пропустить"),
            id="skip_description",
            on_click=lambda c, b, m: m.switch_to(CreateTaskSG.category)
        ),
        Back(Const("⬅️ Назад")),
        state=CreateTaskSG.description,
    ),
    Window(
        Const("🏷️ Выберите категорию:"),
        Group(
            Select(
                Format("{item[name]}"),
                id="category_select",
                item_id_getter=lambda item: item['id'],
                items="categories",
                on_click=on_category_selected,
            ),
            width=2,
        ),
        Button(
            Const("⏭️ Без категории"),
            id="skip_category",
            on_click=on_skip_category
        ),
        Back(Const("⬅️ Назад")),
        getter=get_categories_data,
        state=CreateTaskSG.category,
    ),
    Window(
        Const("⚡ Выберите приоритет:"),
        Column(
            Select(
                Format("{item[1]}"),
                id="priority_select",
                item_id_getter=lambda item: item[0],
                items=[
                    ('low', '🟢 Низкий'),
                    ('medium', '🟡 Средний'),
                    ('high', '🟠 Высокий'),
                    ('urgent', '🔴 Срочный'),
                ],
                on_click=on_priority_selected,
            ),
        ),
        Back(Const("⬅️ Назад")),
        state=CreateTaskSG.priority,
    ),
    Window(
        Format("📋 Подтверждение создания задачи:\n\n"
               "📝 Заголовок: {title}\n"
               "📄 Описание: {description}\n"
               "🏷️ Категория: {category}\n"
               "⚡ Приоритет: {priority}\n\n"
               "Создать задачу?"),
        Column(
            Button(
                Const("✅ Создать"),
                id="confirm_create",
                on_click=on_create_task_confirm
            ),
            Back(Const("⬅️ Изменить")),
        ),
        getter=get_task_preview_data,
        state=CreateTaskSG.confirm,
    ),
)