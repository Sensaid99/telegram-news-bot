import json
import os
import time
from typing import Any, Dict, Optional

class CacheManager:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def _get_cache_path(self, key: str) -> str:
        """Получает путь к файлу кэша."""
        # Заменяем недопустимые символы в имени файла
        safe_key = key.replace('/', '_').replace('\\', '_')
        return os.path.join(self.cache_dir, f"{safe_key}.json")
    
    def get(self, key: str) -> Optional[Any]:
        """Получает данные из кэша."""
        try:
            cache_path = self._get_cache_path(key)
            if not os.path.exists(cache_path):
                return None
                
            with open(cache_path, 'r') as f:
                data = json.load(f)
                
            # Проверяем срок действия кэша
            if time.time() > data.get('expires_at', 0):
                os.remove(cache_path)
                return None
                
            return data.get('value')
            
        except Exception:
            return None
    
    def set(self, key: str, value: Any, expire_minutes: int = 5) -> None:
        """Сохраняет данные в кэш."""
        try:
            cache_path = self._get_cache_path(key)
            data = {
                'value': value,
                'expires_at': time.time() + (expire_minutes * 60)
            }
            
            with open(cache_path, 'w') as f:
                json.dump(data, f)
                
        except Exception:
            pass
    
    def clear(self) -> None:
        """Очищает весь кэш."""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, filename))
        except Exception:
            pass

# Создаем глобальный экземпляр кэш-менеджера
cache = CacheManager() 