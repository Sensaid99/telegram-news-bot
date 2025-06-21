import requests
from typing import Dict, List, Any
from ..config import BINANCE_API_KEY, BINANCE_API_SECRET
import hmac
import hashlib
import time
import logging
import aiohttp
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class BinanceAPI:
    def __init__(self):
        self.api_key = BINANCE_API_KEY
        self.api_secret = BINANCE_API_SECRET
        self.base_url = "https://api.binance.com"
        self.headers = {
            'X-MBX-APIKEY': self.api_key
        }
    
    def _get_signature(self, params: Dict) -> str:
        """Generate signature for authenticated requests."""
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def get_funding_rates(self, symbols: List[str]) -> Dict[str, float]:
        """Get current funding rates for futures markets."""
        try:
            url = f"{self.base_url}/fapi/v1/premiumIndex"
            
            # Get funding rates for all symbols
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Filter and format results
            rates = {}
            for item in data:
                if item['symbol'] in symbols:
                    rates[item['symbol']] = float(item['lastFundingRate'])
            
            return rates
            
        except Exception as e:
            print(f"Error getting funding rates: {e}")
            return {symbol: 0.0 for symbol in symbols}
    
    def get_market_depth(self, symbol: str, limit: int = 10) -> Dict:
        """Get order book for a symbol."""
        try:
            url = f"{self.base_url}/api/v3/depth"
            params = {
                'symbol': symbol,
                'limit': limit
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error getting market depth for {symbol}: {e}")
            return {
                'bids': [],
                'asks': []
            }
    
    def get_recent_trades(self, symbol: str, limit: int = 50) -> List[Dict]:
        """Get recent trades for a symbol."""
        try:
            url = f"{self.base_url}/api/v3/trades"
            params = {
                'symbol': symbol,
                'limit': limit
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error getting recent trades for {symbol}: {e}")
            return []

class BinanceService:
    """Сервис для работы с Binance API."""
    
    def __init__(self):
        self.api = BinanceAPI()
        self.base_url = "https://api.binance.com"
        
    async def get_klines(self, symbol: str, interval: str = "1h", limit: int = 100) -> List[List[Any]]:
        """Получает исторические данные."""
        try:
            url = f"{self.base_url}/api/v3/klines"
            params = {
                'symbol': symbol.replace('/', ''),
                'interval': interval,
                'limit': limit
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Error getting klines: {await response.text()}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error in get_klines: {e}")
            return []
            
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Получает текущие данные по торговой паре."""
        try:
            url = f"{self.base_url}/api/v3/ticker/24hr"
            params = {'symbol': symbol.replace('/', '')}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Error getting ticker: {await response.text()}")
                        return {}
                        
        except Exception as e:
            logger.error(f"Error in get_ticker: {e}")
            return {}
            
    async def get_exchange_info(self, symbol: str = None) -> Dict[str, Any]:
        """Получает информацию о бирже или конкретной торговой паре."""
        try:
            url = f"{self.base_url}/api/v3/exchangeInfo"
            params = {'symbol': symbol.replace('/', '')} if symbol else {}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Error getting exchange info: {await response.text()}")
                        return {}
                        
        except Exception as e:
            logger.error(f"Error in get_exchange_info: {e}")
            return {}
            
    async def get_order_book(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Получает книгу ордеров."""
        try:
            url = f"{self.base_url}/api/v3/depth"
            params = {
                'symbol': symbol.replace('/', ''),
                'limit': limit
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Error getting order book: {await response.text()}")
                        return {'bids': [], 'asks': []}
                        
        except Exception as e:
            logger.error(f"Error in get_order_book: {e}")
            return {'bids': [], 'asks': []}

# Create API instance
binance_api = BinanceAPI() 