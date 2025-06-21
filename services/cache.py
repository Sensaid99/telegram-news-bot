import logging
from typing import Any, Optional
from datetime import datetime, timedelta
from config import CACHE_TTL, CACHE_ENABLED

logger = logging.getLogger(__name__)

class Cache:
    """Простой in-memory кэш."""
    
    def __init__(self):
        self._cache = {}
        self._ttl = {}
        
    def get(self, key: str) -> Optional[Any]:
        """Получает значение из кэша."""
        if not CACHE_ENABLED:
            return None
            
        try:
            if key in self._cache:
                # Проверяем TTL
                if datetime.now() < self._ttl[key]:
                    return self._cache[key]
                else:
                    # Удаляем просроченные данные
                    del self._cache[key]
                    del self._ttl[key]
                    
            return None
            
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None
            
    def set(self, key: str, value: Any, ttl: int = CACHE_TTL) -> bool:
        """Сохраняет значение в кэш."""
        if not CACHE_ENABLED:
            return False
            
        try:
            self._cache[key] = value
            self._ttl[key] = datetime.now() + timedelta(seconds=ttl)
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
            
    def delete(self, key: str) -> bool:
        """Удаляет значение из кэша."""
        try:
            if key in self._cache:
                del self._cache[key]
                del self._ttl[key]
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False
            
    def clear(self) -> bool:
        """Очищает весь кэш."""
        try:
            self._cache.clear()
            self._ttl.clear()
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
            
    def cleanup(self) -> int:
        """Удаляет просроченные данные из кэша."""
        try:
            expired = []
            now = datetime.now()
            
            # Находим просроченные ключи
            for key, ttl in self._ttl.items():
                if now > ttl:
                    expired.append(key)
                    
            # Удаляем просроченные данные
            for key in expired:
                del self._cache[key]
                del self._ttl[key]
                
            return len(expired)
            
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
            return 0
            
    def get_stats(self) -> dict:
        """Возвращает статистику кэша."""
        try:
            total = len(self._cache)
            expired = sum(1 for ttl in self._ttl.values() if datetime.now() > ttl)
            
            return {
                "total": total,
                "active": total - expired,
                "expired": expired,
                "enabled": CACHE_ENABLED
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {
                "total": 0,
                "active": 0,
                "expired": 0,
                "enabled": CACHE_ENABLED
            }
            
# Создаем глобальный экземпляр кэша
cache = Cache() 