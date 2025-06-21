import logging
from typing import Dict, Any
from database import get_session, User

logger = logging.getLogger(__name__)

class UserSettings:
    """Сервис управления настройками пользователя."""
    
    async def get_user_settings(self, user_id: int) -> Dict[str, Any]:
        """Получает все настройки пользователя."""
        try:
            async with get_session() as session:
                user = await session.get(User, user_id)
                if not user:
                    return self._get_default_settings()
                return user.settings
                
        except Exception as e:
            logger.error(f"Error getting user settings: {e}")
            return self._get_default_settings()
            
    async def get_notifications_settings(self, user_id: int) -> Dict[str, Any]:
        """Получает настройки уведомлений."""
        try:
            settings = await self.get_user_settings(user_id)
            return settings.get('notifications', self._get_default_notifications())
            
        except Exception as e:
            logger.error(f"Error getting notifications settings: {e}")
            return self._get_default_notifications()
            
    async def get_display_settings(self, user_id: int) -> Dict[str, Any]:
        """Получает настройки отображения."""
        try:
            settings = await self.get_user_settings(user_id)
            return settings.get('display', self._get_default_display())
            
        except Exception as e:
            logger.error(f"Error getting display settings: {e}")
            return self._get_default_display()
            
    async def get_filter_settings(self, user_id: int) -> Dict[str, Any]:
        """Получает настройки фильтров."""
        try:
            settings = await self.get_user_settings(user_id)
            return settings.get('filters', self._get_default_filters())
            
        except Exception as e:
            logger.error(f"Error getting filter settings: {e}")
            return self._get_default_filters()
            
    async def update_settings(self, user_id: int, settings: Dict[str, Any]) -> bool:
        """Обновляет настройки пользователя."""
        try:
            async with get_session() as session:
                user = await session.get(User, user_id)
                if not user:
                    user = User(id=user_id, settings=settings)
                    session.add(user)
                else:
                    user.settings.update(settings)
                await session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            return False
            
    def _get_default_settings(self) -> Dict[str, Any]:
        """Возвращает настройки по умолчанию."""
        return {
            "notifications": self._get_default_notifications(),
            "display": self._get_default_display(),
            "filters": self._get_default_filters()
        }
        
    def _get_default_notifications(self) -> Dict[str, Any]:
        """Возвращает настройки уведомлений по умолчанию."""
        return {
            "price": {
                "enabled": True,
                "change": 5.0,  # % изменения
                "interval": 5  # минуты
            },
            "volume": {
                "enabled": True,
                "min": 1000000,  # мин. объем в USD
                "change": 50.0  # % изменения
            },
            "news": {
                "enabled": True,
                "importance": "high",
                "categories": ["market", "regulation", "technology"]
            },
            "whales": {
                "enabled": True,
                "min": 5000000,  # мин. сумма в USD
                "networks": ["BTC", "ETH", "BNB"]
            }
        }
        
    def _get_default_display(self) -> Dict[str, Any]:
        """Возвращает настройки отображения по умолчанию."""
        return {
            "currency": {
                "main": "USD",
                "secondary": "BTC"
            },
            "time": {
                "timezone": "UTC",
                "format": "24h"
            },
            "numbers": {
                "separator": ",",
                "decimals": 2
            },
            "theme": {
                "mode": "light",
                "emoji": True
            }
        }
        
    def _get_default_filters(self) -> Dict[str, Any]:
        """Возвращает настройки фильтров по умолчанию."""
        return {
            "volume": {
                "min": 1000000,  # мин. объем в USD
                "change": 20.0  # % изменения
            },
            "price": {
                "change": 3.0,  # % изменения
                "volatility": "medium"  # low/medium/high
            },
            "whales": {
                "min": 1000000,  # мин. сумма в USD
                "types": ["transfer", "exchange"]  # типы транзакций
            },
            "news": {
                "importance": "medium",  # low/medium/high
                "categories": ["market", "regulation", "technology", "adoption"]
            }
        } 