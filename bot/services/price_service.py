import logging
import aiohttp
from typing import Dict, Optional
from services.cache_manager import cache
from config import BINANCE_API_KEY, BINANCE_API_SECRET

logger = logging.getLogger(__name__)

class PriceService:
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.headers = {
            "X-MBX-APIKEY": BINANCE_API_KEY
        }
    
    async def _make_request(self, endpoint: str) -> Dict:
        """Делает запрос к API с кэшированием."""
        cache_key = f"price_service_{endpoint}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
            
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/{endpoint}", headers=self.headers) as response:
                data = await response.json()
                cache.set(cache_key, data, expire_minutes=1)  # Кэшируем на 1 минуту
                return data
    
    async def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Получает текущую цену криптовалюты.
        
        Args:
            symbol: Тикер криптовалюты (например, 'BTC', 'ETH')
            
        Returns:
            float: Текущая цена в USD или None в случае ошибки
        """
        try:
            # Добавляем USDT к символу
            symbol_pair = f"{symbol}USDT"
            
            # Получаем текущую цену
            data = await self._make_request(f"ticker/price?symbol={symbol_pair}")
            price = float(data['price'])
            
            logger.info(f"Got price for {symbol}: ${price:,.2f}")
            return price
            
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None
    
    async def get_24h_stats(self, symbol: str) -> Optional[Dict]:
        """
        Получает статистику за 24 часа.
        
        Args:
            symbol: Тикер криптовалюты
            
        Returns:
            Dict: Статистика или None в случае ошибки
        """
        try:
            symbol_pair = f"{symbol}USDT"
            data = await self._make_request(f"ticker/24hr?symbol={symbol_pair}")
            
            return {
                'price': float(data['lastPrice']),
                'change_24h': float(data['priceChangePercent']),
                'volume_24h': float(data['volume']),
                'high_24h': float(data['highPrice']),
                'low_24h': float(data['lowPrice'])
            }
            
        except Exception as e:
            logger.error(f"Error getting 24h stats for {symbol}: {e}")
            return None

# Create service instance
price_service = PriceService() 