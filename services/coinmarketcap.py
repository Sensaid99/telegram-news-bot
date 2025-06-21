import requests
from typing import Dict, List, Optional
from config import COINMARKETCAP_API_KEY
import logging

logger = logging.getLogger(__name__)

class CoinMarketCapAPI:
    def __init__(self):
        self.api_key = COINMARKETCAP_API_KEY
        self.base_url = "https://pro-api.coinmarketcap.com/v1"
        self.headers = {
            'X-CMC_PRO_API_KEY': self.api_key,
            'Accept': 'application/json'
        }
    
    def get_latest_prices(self, symbols: List[str]) -> Dict:
        """Get latest prices for given cryptocurrency symbols."""
        endpoint = f"{self.base_url}/cryptocurrency/quotes/latest"
        params = {
            'symbol': ','.join(symbols),
            'convert': 'USD'
        }
        
        response = requests.get(endpoint, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()['data']
    
    def get_market_metrics(self, symbol: str) -> Dict:
        """Get market metrics for a specific coin."""
        try:
            # Игнорируем команды бота
            if symbol.startswith('/'):
                raise ValueError(f"Invalid symbol: {symbol}")
                
            url = f"{self.base_url}/cryptocurrency/quotes/latest"
            params = {
                'symbol': symbol,
                'convert': 'USD'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()['data'][symbol]
            quote = data['quote']['USD']
            
            return {
                'price': quote['price'],
                'volume_24h': quote['volume_24h'],
                'percent_change_24h': quote['percent_change_24h'],
                'market_cap': quote['market_cap']
            }
            
        except Exception as e:
            logger.error(f"Error getting market metrics for {symbol}: {e}")
            return {
                'price': 0,
                'volume_24h': 0,
                'percent_change_24h': 0,
                'market_cap': 0
            }
    
    def get_trending_coins(self, limit: int = 5) -> List[Dict]:
        """Get trending coins by 24h volume."""
        try:
            url = f"{self.base_url}/cryptocurrency/listings/latest"
            params = {
                'sort': 'volume_24h',
                'limit': limit,
                'convert': 'USD'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            return response.json()['data']
            
        except Exception as e:
            print(f"Error getting trending coins: {e}")
            return []

# Create API instance
cmc_api = CoinMarketCapAPI() 