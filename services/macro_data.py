import aiohttp
import logging
from typing import Dict, Optional
from services.cache_manager import cache
from config import TWELVEDATA_API_KEY

logger = logging.getLogger(__name__)

class MacroData:
    def __init__(self):
        if not TWELVEDATA_API_KEY:
            logger.error("TwelveData API key is not configured")
            raise ValueError("TwelveData API key is required")
            
        self.base_url = "https://api.twelvedata.com"
        self.api_key = TWELVEDATA_API_KEY
        self._session = None
        self.symbols = {
            'DXY': 'USD/EUR',    # US Dollar Index (через EUR/USD)
            'SPX': 'SPY',        # S&P 500 (используем ETF SPY)
            'VIX': 'UVXY',       # Volatility Index (используем ETF UVXY)
            'GC': 'GLD'          # Gold (используем ETF GLD)
        }
    
    @property
    async def session(self) -> aiohttp.ClientSession:
        """Получение сессии для HTTP-запросов."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Делает запрос к API с кэшированием."""
        if params is None:
            params = {}
        params['apikey'] = self.api_key
        
        cache_key = f"macro_data_{endpoint}_{str(params)}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
            
        session = await self.session
            
        try:
            async with session.get(f"{self.base_url}/{endpoint}", params=params) as response:
                if response.status != 200:
                    raise Exception(f"API request failed with status {response.status}")
                data = await response.json()
                if data.get('status') == 'error':
                    raise Exception(f"API error: {data.get('message')}")
                cache.set(cache_key, data, expire_minutes=60)
                return data
        except Exception as e:
            logger.error(f"Error making request to {endpoint}: {e}")
            raise
    
    async def get_indicator_data(self, symbol: str) -> Optional[Dict]:
        """Получает данные по конкретному индикатору."""
        try:
            # Получаем цены
            price_params = {
                'symbol': self.symbols[symbol],
                'interval': '1day',
                'outputsize': '1'  # Запрашиваем только последнее значение
            }
            price_data = await self._make_request('time_series', price_params)
            
            if 'values' not in price_data or not price_data['values']:
                return None
                
            latest = price_data['values'][0]
            
            # Получаем объем торгов из того же запроса
            volume = float(latest.get('volume', 0))
            
            return {
                'price': float(latest['close']),
                'change': float(latest.get('percent_change', '0')),
                'high': float(latest['high']),
                'low': float(latest['low']),
                'volume': volume
            }
        except Exception as e:
            logger.error(f"Error getting data for {symbol}: {e}")
            return None
    
    def _get_trend_emoji(self, change: float) -> str:
        """Возвращает эмодзи тренда."""
        if change > 0:
            return "📈"
        elif change < 0:
            return "📉"
        return "⚪️"
    
    def _format_volume(self, volume: float) -> str:
        """Форматирует объем торгов в читаемый вид."""
        if volume >= 1_000_000_000:
            return f"{volume/1_000_000_000:.1f}B"
        elif volume >= 1_000_000:
            return f"{volume/1_000_000:.1f}M"
        elif volume >= 1_000:
            return f"{volume/1_000:.1f}K"
        return f"{volume:.0f}"
    
    async def get_market_indicators(self) -> str:
        """Получает основные макроэкономические показатели."""
        try:
            result = []
            
            # Получаем данные по каждому индикатору
            for symbol_key, symbol_name in self.symbols.items():
                data = await self.get_indicator_data(symbol_key)
                if data:
                    trend = self._get_trend_emoji(data['change'])
                    price_str = f"${data['price']:,.2f}" if symbol_key in ['SPX', 'GC'] else f"{data['price']:.3f}"
                    volume_str = f" | Vol: {self._format_volume(data['volume'])}"
                    
                    if symbol_key == 'GC':
                        result.append(f"Gold: {price_str} {trend} {data['change']:+.1f}%{volume_str}")
                    else:
                        result.append(f"{symbol_key}: {price_str} {trend} {data['change']:+.1f}%{volume_str}")
            
            return "\n".join(result) if result else "Данные временно недоступны"
            
        except Exception as e:
            logger.error(f"Error getting market indicators: {e}")
            return "Данные временно недоступны"
    
    async def get_detailed_report(self) -> str:
        """Получает детальный отчет по макроэкономическим показателям."""
        try:
            report = []
            
            # Описания индикаторов
            descriptions = {
                'DXY': 'US Dollar Index',
                'SPX': 'S&P 500 Index',
                'VIX': 'CBOE Volatility Index',
                'GC': 'Gold ETF'
            }
            
            for symbol_key, symbol_name in self.symbols.items():
                data = await self.get_indicator_data(symbol_key)
                if data:
                    trend = self._get_trend_emoji(data['change'])
                    price_str = f"${data['price']:,.2f}" if symbol_key in ['SPX', 'GC'] else f"{data['price']:.3f}"
                    
                    report.append(f"{descriptions[symbol_key]} ({symbol_key})")
                    report.append(f"• Текущая цена: {price_str}")
                    report.append(f"• Изменение: {data['change']:+.1f}% {trend}")
                    report.append(f"• Диапазон: {data['low']:.2f} - {data['high']:.2f}")
                    report.append(f"• Объем: {self._format_volume(data['volume'])}")
                    report.append("")  # Пустая строка для разделения
            
            return "\n".join(report) if report else "Данные временно недоступны"
            
        except Exception as e:
            logger.error(f"Error getting detailed report: {e}")
            return "Данные временно недоступны"

    async def close(self):
        """Закрывает все соединения."""
        try:
            if self._session:
                await self._session.close()
                self._session = None
        except Exception as e:
            logger.error(f"Error closing connections: {e}")

# Create API instance
macro_data = MacroData() 