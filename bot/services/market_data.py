import logging
import aiohttp
from typing import Dict, Any, List
from services.cache_manager import cache
from config import BINANCE_API_KEY, BINANCE_API_SECRET
from binance import AsyncClient

logger = logging.getLogger(__name__)

class MarketData:
    """Класс для получения рыночных данных криптовалют."""
    
    def __init__(self):
        if not BINANCE_API_KEY or not BINANCE_API_SECRET:
            logger.error("Binance API credentials are not configured")
            raise ValueError("Binance API credentials are required")
            
        self.coingecko_url = "https://api.coingecko.com/api/v3"
        self._binance_client = None
        self._session = None
        self.supported_pairs = [
            'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 
            'TRXUSDT', 'TONUSDT', 'XRPUSDT', 'SUIUSDT',
            'USDCUSDT', 'BUSDUSDT', 'DOGEUSDT', 'MATICUSDT',
            'ADAUSDT', 'DOTUSDT', 'LINKUSDT', 'AVAXUSDT'
        ]
        
        # Маппинг для имен сетей
        self.network_names = {
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum',
            'SOL': 'Solana',
            'BNB': 'BNB Chain',
            'TRX': 'TRON',
            'TON': 'TON',
            'XRP': 'Ripple',
            'SUI': 'Sui',
            'MATIC': 'Polygon',
            'AVAX': 'Avalanche'
        }
    
    async def get_binance_client(self) -> AsyncClient:
        """Получает или создает клиент Binance."""
        if self._binance_client is None:
            try:
                self._binance_client = await AsyncClient.create(BINANCE_API_KEY, BINANCE_API_SECRET)
            except Exception as e:
                logger.error(f"Failed to create Binance client: {e}")
                raise
        return self._binance_client
    
    async def _make_request(self, endpoint: str) -> Dict:
        """Делает запрос к CoinGecko API с кэшированием."""
        cache_key = f"market_data_{endpoint}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
            
        if self._session is None:
            self._session = aiohttp.ClientSession()
            
        try:
            async with self._session.get(f"{self.coingecko_url}/{endpoint}") as response:
                if response.status != 200:
                    raise Exception(f"API request failed with status {response.status}")
                data = await response.json()
                cache.set(cache_key, data, expire_minutes=5)
                return data
        except Exception as e:
            logger.error(f"Error making request to {endpoint}: {e}")
            raise
    
    async def get_market_volume(self) -> Dict:
        """Получает данные об объемах торгов с контекстом."""
        try:
            client = await self.get_binance_client()
            tickers = await client.get_ticker()
            
            # Получаем общий объем рынка
            total_volume = 0
            result = {}
            
            # Первый проход для подсчета общего объема
            for ticker in tickers:
                if ticker['symbol'] in self.supported_pairs:
                    total_volume += float(ticker['quoteVolume'])
            
            # Второй проход для сбора данных с контекстом
            for ticker in tickers:
                if ticker['symbol'] in self.supported_pairs:
                    symbol = ticker['symbol'].replace('USDT', '')
                    curr_volume = float(ticker['quoteVolume'])
                    prev_volume = float(ticker.get('prevDayVolume', 0))
                    volume_change = ((curr_volume - prev_volume) / prev_volume * 100) if prev_volume > 0 else 0
                    
                    # Добавляем контекст объема
                    volume_share = (curr_volume / total_volume * 100) if total_volume > 0 else 0
                    
                    result[symbol] = {
                        'symbol': symbol,
                        'volume': curr_volume,
                        'volume_change': volume_change,
                        'volume_share': volume_share,  # Доля в общем объеме
                        'price': float(ticker['lastPrice']),
                        'price_change': float(ticker['priceChangePercent']),
                        'prev_price': float(ticker.get('prevClosePrice', 0)),
                        'high_24h': float(ticker['highPrice']),
                        'low_24h': float(ticker['lowPrice']),
                        'network': self.network_names.get(symbol, symbol)
                    }
            
            # Сортируем по объему
            sorted_result = dict(sorted(result.items(), key=lambda x: x[1]['volume'], reverse=True))
            return sorted_result
            
        except Exception as e:
            logger.error(f"Error getting market volume: {e}")
            return {}
    
    async def get_trending_coins(self) -> str:
        """Получает информацию о трендовых монетах."""
        try:
            data = await self._make_request("search/trending")
            
            trend_text = "🔥 Тренды рынка:\n\n"
            for coin in data['coins'][:5]:  # Берем топ-5 монет
                item = coin['item']
                price_btc = float(item.get('price_btc', 0))
                btc_data = await self.get_bitcoin_data()
                price_usdt = price_btc * btc_data['price']
                
                # Добавляем больше контекста
                market_cap = item.get('market_cap', 0)
                volume_24h = item.get('volume_24h', 0)
                
                trend_text += (
                    f"🔸 {item['name']} ({item['symbol'].upper()})\n"
                    f"💰 Цена: ${price_usdt:.4f}\n"
                    f"📈 Ранг: #{item.get('market_cap_rank', 'N/A')}\n"
                    f"💎 Капитализация: ${market_cap:,.0f}\n"
                    f"📊 Объем 24ч: ${volume_24h:,.0f}\n"
                    f"🔍 Причина тренда: {self._get_trend_reason(item)}\n\n"
                )
            
            return trend_text or "Нет данных о трендах"
            
        except Exception as e:
            logger.error(f"Error getting trending coins: {e}")
            return "Ошибка получения данных о трендах"
    
    def _get_trend_reason(self, item: Dict) -> str:
        """Определяет причину тренда на основе метрик."""
        reasons = []
        
        if item.get('price_change_24h', 0) > 5:
            reasons.append("сильный рост цены")
        if item.get('volume_change_24h', 0) > 50:
            reasons.append("высокий объем торгов")
        if item.get('social_score', 0) > 1000:
            reasons.append("высокая социальная активность")
        if item.get('developer_score', 0) > 800:
            reasons.append("активная разработка")
        if item.get('community_score', 0) > 800:
            reasons.append("сильное комьюнити")
            
        return ", ".join(reasons) if reasons else "рост интереса инвесторов"
    
    async def get_coin_data(self, symbol: str) -> Dict[str, Any]:
        """Получение данных о конкретной монете."""
        try:
            client = await self.get_binance_client()
            ticker = await client.get_ticker(symbol=f'{symbol}USDT')
            
            return {
                'price': float(ticker['lastPrice']),
                'change_24h': float(ticker['priceChangePercent']),
                'volume_24h': float(ticker['quoteVolume']),
                'high_24h': float(ticker['highPrice']),
                'low_24h': float(ticker['lowPrice']),
                'network': self.network_names.get(symbol, symbol)
            }
        except Exception as e:
            logger.error(f"Error getting {symbol} data: {e}")
            return {
                'price': 0,
                'change_24h': 0,
                'volume_24h': 0,
                'high_24h': 0,
                'low_24h': 0,
                'network': self.network_names.get(symbol, symbol)
            }
    
    async def get_bitcoin_data(self) -> Dict[str, Any]:
        """Получение данных о Bitcoin."""
        return await self.get_coin_data('BTC')
    
    async def get_ethereum_data(self) -> Dict[str, Any]:
        """Получение данных о Ethereum."""
        return await self.get_coin_data('ETH')
    
    async def get_solana_data(self) -> Dict[str, Any]:
        """Получение данных о Solana."""
        return await self.get_coin_data('SOL')
    
    async def get_bnb_data(self) -> Dict[str, Any]:
        """Получение данных о BNB."""
        return await self.get_coin_data('BNB')
    
    async def get_tron_data(self) -> Dict[str, Any]:
        """Получение данных о TRON."""
        return await self.get_coin_data('TRX')
    
    async def get_ton_data(self) -> Dict[str, Any]:
        """Получение данных о TON."""
        return await self.get_coin_data('TON')
    
    async def get_xrp_data(self) -> Dict[str, Any]:
        """Получение данных о XRP."""
        return await self.get_coin_data('XRP')
    
    async def get_sui_data(self) -> Dict[str, Any]:
        """Получение данных о SUI."""
        return await self.get_coin_data('SUI')
    
    async def close(self):
        """Закрывает все соединения."""
        try:
            if self._binance_client:
                await self._binance_client.close_connection()
                self._binance_client = None
            
            if self._session:
                await self._session.close()
                self._session = None
        except Exception as e:
            logger.error(f"Error closing connections: {e}") 