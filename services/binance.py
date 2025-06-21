import requests
from typing import Dict, List
from config import BINANCE_API_KEY, BINANCE_API_SECRET
import hmac
import hashlib
import time

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

# Create API instance
binance_api = BinanceAPI() 