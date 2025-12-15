"""
Клиент для работы с Django API.
"""
import aiohttp
import logging
from typing import List, Dict, Optional
from config import DJANGO_API_URL

logger = logging.getLogger(__name__)


class APIClient:
    """Клиент для работы с Django API."""
    
    def __init__(self):
        self.base_url = DJANGO_API_URL
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Выполняет HTTP запрос к API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 201:
                    return await response.json()
                else:
                    logger.error(f"API request failed: {response.status} - {await response.text()}")
                    return {}
        except Exception as e:
            logger.error(f"API request error: {e}")
            return {}
    
    # Категории
    async def get_categories(self) -> List[Dict]:
        """Получает список категорий."""
        result = await self._request('GET', 'categories/')
        return result.get('results', []) if 'results' in result else result
    
    async def create_category(self, name: str, description: str = "", color: str = "#007bff") -> Dict:
        """Создает новую категорию."""
        data = {
            'name': name,
            'description': description,
            'color': color
        }
        return await self._request('POST', 'categories/', json=data)
    
    # Задачи
    async def get_tasks(self, telegram_user_id: int, status: Optional[str] = None) -> List[Dict]:
        """Получает задачи пользователя."""
        params = {'telegram_user_id': telegram_user_id}
        if status:
            params['status'] = status
        
        result = await self._request('GET', 'tasks/by_telegram_user/', params=params)
        return result.get('results', []) if 'results' in result else result
    
    async def create_task(self, telegram_user_id: int, title: str, 
                         description: str = "", category_id: Optional[str] = None,
                         priority: str = "medium", due_date: Optional[str] = None) -> Dict:
        """Создает новую задачу."""
        data = {
            'telegram_user_id': telegram_user_id,
            'title': title,
            'description': description,
            'priority': priority
        }
        
        if category_id:
            data['category'] = category_id
        
        if due_date:
            data['due_date'] = due_date
        
        return await self._request('POST', 'tasks/create_for_telegram/', json=data)
    
    async def update_task(self, task_id: str, **kwargs) -> Dict:
        """Обновляет задачу."""
        return await self._request('PATCH', f'tasks/{task_id}/', json=kwargs)
    
    async def mark_task_completed(self, task_id: str) -> Dict:
        """Отмечает задачу как завершенную."""
        return await self._request('PATCH', f'tasks/{task_id}/mark_completed/')
    
    async def delete_task(self, task_id: str) -> bool:
        """Удаляет задачу."""
        result = await self._request('DELETE', f'tasks/{task_id}/')
        return result is not None
    
    async def get_task_stats(self, telegram_user_id: int) -> Dict:
        """Получает статистику задач пользователя."""
        params = {'telegram_user_id': telegram_user_id}
        return await self._request('GET', 'tasks/stats/', params=params)


# Глобальный экземпляр клиента
api_client = APIClient()