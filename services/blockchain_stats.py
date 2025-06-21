import logging
import aiohttp
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from services.cache_manager import cache
from config import (
    ETHERSCAN_API_KEY,
    BSCSCAN_API_KEY,
    SOLSCAN_API_KEY,
    TRONGRID_API_KEY
)

logger = logging.getLogger(__name__)

class BlockchainStats:
    """Класс для получения on-chain метрик из различных источников."""
    
    def __init__(self):
        # Проверяем наличие всех необходимых API ключей
        if not ETHERSCAN_API_KEY:
            logger.error("Etherscan API key is not configured")
            raise ValueError("Etherscan API key is required")
        if not BSCSCAN_API_KEY:
            logger.error("BSCScan API key is not configured")
            raise ValueError("BSCScan API key is required")
        if not SOLSCAN_API_KEY:
            logger.error("Solscan API key is not configured")
            raise ValueError("Solscan API key is required")
        if not TRONGRID_API_KEY:
            logger.error("TronGrid API key is not configured")
            raise ValueError("TronGrid API key is required")
            
        self.apis = {
            'ETH': {
                'url': 'https://api.etherscan.io/api',
                'key': ETHERSCAN_API_KEY
            },
            'BSC': {
                'url': 'https://api.bscscan.com/api',
                'key': BSCSCAN_API_KEY
            },
            'SOL': {
                'url': 'https://api.mainnet-beta.solana.com',
                'key': None
            },
            'BTC': {
                'url': 'https://api.blockchain.info/stats',
                'key': None
            },
            'TRX': {
                'url': 'https://api.trongrid.io',
                'key': TRONGRID_API_KEY
            }
        }
        self._session = None
        self.supported_networks = {
            'btc': 'Bitcoin',
            'eth': 'Ethereum',
            'sol': 'Solana',
            'bnb': 'BNB Chain',
            'trx': 'TRON',
            'ton': 'TON',
            'xrp': 'Ripple',
            'sui': 'SUI',
            'usdt': 'USDT',
            'usdc': 'USDC'
        }
        
        # Минимальные суммы для определения китов (в USD)
        self.whale_thresholds = {
            'btc': 1000000,  # $1M
            'eth': 500000,   # $500K
            'sol': 100000,   # $100K
            'bnb': 100000,   # $100K
            'trx': 50000,    # $50K
            'ton': 50000,    # $50K
            'xrp': 50000,    # $50K
            'sui': 50000,    # $50K
            'usdt': 1000000, # $1M
            'usdc': 1000000  # $1M
        }
    
    @property
    async def session(self) -> aiohttp.ClientSession:
        """Получение сессии для HTTP-запросов."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Закрывает все соединения."""
        try:
            if self._session is not None:
                await self._session.close()
                self._session = None
        except Exception as e:
            logger.error(f"Error closing connections: {e}")
    
    async def get_bitcoin_metrics(self) -> Dict[str, Any]:
        """Получение метрик сети Bitcoin."""
        try:
            cache_key = "bitcoin_metrics"
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data
                
            session = await self.session
            async with session.get(self.apis['BTC']['url']) as response:
                if response.status != 200:
                    raise Exception(f"API request failed with status {response.status}")
                data = await response.json()
                
                result = {
                    'transactions': int(data.get('n_tx', 0)),
                    'active_addresses': int(data.get('n_unique_addresses', 0)),
                    'fee': float(data.get('median_fee', 0))
                }
                
                cache.set(cache_key, result, expire_minutes=5)
                return result
                
        except Exception as e:
            logger.error(f"Error getting Bitcoin metrics: {e}")
            return {
                'transactions': 0,
                'active_addresses': 0,
                'fee': 0.0
            }
    
    async def get_ethereum_metrics(self) -> Dict[str, Any]:
        """Получение метрик сети Ethereum."""
        try:
            cache_key = "ethereum_metrics"
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data
                
            session = await self.session
            params = {
                'module': 'gastracker',
                'action': 'gasoracle',
                'apikey': ETHERSCAN_API_KEY
            }
            async with session.get(f"{self.apis['ETH']['url']}", params=params) as response:
                if response.status != 200:
                    raise Exception(f"API request failed with status {response.status}")
                data = await response.json()
                
                if data.get('status') != '1':
                    raise Exception(f"API error: {data.get('message')}")
                    
                gas_price = data.get('result', {}).get('SafeGasPrice', '0')
                result = {
                    'gas': float(gas_price),  # Преобразуем в float
                    'tvl': await self._get_eth_tvl(),
                    'active_addresses': await self._get_eth_active_addresses()
                }
                
                cache.set(cache_key, result, expire_minutes=5)
                return result
                
        except Exception as e:
            logger.error(f"Error getting Ethereum metrics: {e}")
            return {
                'gas': 0.0,  # Возвращаем float
                'tvl': 0.0,
                'active_addresses': 0
            }
    
    async def get_solana_metrics(self) -> Dict[str, Any]:
        """Получение метрик сети Solana."""
        try:
            cache_key = "solana_metrics"
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data
                
            session = await self.session
            # Получаем производительность
            perf_data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getRecentPerformanceSamples",
                "params": [1]
            }
            async with session.post(self.apis['SOL']['url'], json=perf_data) as response:
                if response.status != 200:
                    raise Exception(f"API request failed with status {response.status}")
                perf_result = await response.json()
                
                if 'result' not in perf_result or not perf_result['result']:
                    raise Exception("No performance data available")
                    
                sample = perf_result['result'][0]
                
                # Получаем информацию о последнем блоке
                block_data = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getBlockTime",
                    "params": ["latest"]
                }
                async with session.post(self.apis['SOL']['url'], json=block_data) as response:
                    if response.status != 200:
                        raise Exception(f"API request failed with status {response.status}")
                    block_result = await response.json()
                    block_time = block_result.get('result', 0)
                
                result = {
                    'tps': round(float(sample.get('numTransactions', 0)) / sample.get('samplePeriodSecs', 60), 1),
                    'fee': round(float(sample.get('numNonVoteTransactions', 0)) / sample.get('samplePeriodSecs', 60), 2),
                    'validators': await self._get_sol_validators(),
                    'block_time': block_time
                }
                
                cache.set(cache_key, result, expire_minutes=5)
                return result
                
        except Exception as e:
            logger.error(f"Error getting Solana metrics: {e}")
            return {
                'tps': 0.0,
                'fee': 0.0,
                'validators': 0,
                'block_time': 0.0
            }
    
    async def get_bnb_metrics(self) -> Dict[str, Any]:
        """Получение метрик сети BNB Chain."""
        try:
            cache_key = "bnb_metrics"
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data
                
            session = await self.session
            params = {
                'module': 'gastracker',
                'action': 'gasoracle',
                'apikey': BSCSCAN_API_KEY
            }
            async with session.get(f"{self.apis['BSC']['url']}", params=params) as response:
                if response.status != 200:
                    raise Exception(f"API request failed with status {response.status}")
                data = await response.json()
                
                if data.get('status') != '1':
                    raise Exception(f"API error: {data.get('message')}")
                    
                result = {
                    'gas': data.get('result', {}).get('SafeGasPrice', 0),
                    'tvl': await self._get_bsc_tvl(),
                    'validators': await self._get_bsc_validators()
                }
                
                cache.set(cache_key, result, expire_minutes=5)
                return result
                
        except Exception as e:
            logger.error(f"Error getting BNB Chain metrics: {e}")
            return {
                'gas': 0,
                'tvl': 0,
                'validators': 0
            }

    async def _get_eth_tvl(self) -> float:
        """Получает TVL в сети Ethereum."""
        try:
            session = await self.session
            async with session.get('https://api.llama.fi/v2/chains/ethereum') as response:
                if response.status != 200:
                    return 0
                data = await response.json()
                return float(data[0].get('tvl', 0))
        except Exception:
            return 0

    async def _get_bsc_tvl(self) -> float:
        """Получает TVL в сети BSC."""
        try:
            session = await self.session
            async with session.get('https://api.llama.fi/v2/chains/bsc') as response:
                if response.status != 200:
                    return 0
                data = await response.json()
                return float(data[0].get('tvl', 0))
        except Exception:
            return 0

    async def _get_eth_active_addresses(self) -> int:
        """Получает количество активных адресов в сети Ethereum."""
        try:
            session = await self.session
            params = {
                'module': 'stats',
                'action': 'dailyaddresscount',
                'apikey': ETHERSCAN_API_KEY
            }
            async with session.get(f"{self.apis['ETH']['url']}", params=params) as response:
                if response.status != 200:
                    return 0
                data = await response.json()
                if data.get('status') != '1':
                    return 0
                return int(data.get('result', [{'addressCount': 0}])[-1].get('addressCount', 0))
        except Exception:
            return 0

    async def _get_bsc_validators(self) -> int:
        """Получает количество валидаторов в сети BSC."""
        try:
            session = await self.session
            async with session.get('https://api.binance.org/v1/staking/chains/bsc/validators') as response:
                if response.status != 200:
                    return 0
                data = await response.json()
                return len(data) if isinstance(data, list) else 0
        except Exception:
            return 0

    async def _get_sol_validators(self) -> int:
        """Получение количества валидаторов Solana."""
        try:
            session = await self.session
            data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getVoteAccounts",
                "params": []
            }
            async with session.post(self.apis['SOL']['url'], json=data) as response:
                if response.status != 200:
                    raise Exception(f"API request failed with status {response.status}")
                result = await response.json()
                
                if 'result' not in result:
                    return 0
                    
                current = len(result['result'].get('current', []))
                delinquent = len(result['result'].get('delinquent', []))
                return current + delinquent
                
        except Exception as e:
            logger.error(f"Error getting Solana validators: {e}")
            return 0

    async def get_network_stats(self) -> str:
        """Получает статистику по основным сетям."""
        try:
            # Получаем метрики по каждой сети
            btc = await self.get_bitcoin_metrics()
            eth = await self.get_ethereum_metrics()
            bnb = await self.get_bnb_metrics()
            sol = await self.get_solana_metrics()
            
            # Форматируем вывод
            return f"""Bitcoin:
• Transactions: {btc['transactions']:,}
• Active addresses: {btc['active_addresses']:,}
• Fee: {btc['fee']:.1f} sat/vB

Ethereum:
• Gas: {eth['gas']:.2f} Gwei
• TVL: ${eth['tvl']:,.0f}
• Active addresses: {eth['active_addresses']:,}

BSC:
• Gas: {float(bnb['gas']):.1f} Gwei
• TVL: ${bnb['tvl']:,.0f}
• Validators: {bnb['validators']:,}

Solana:
• TPS: {sol['tps']:.1f}
• Fee: {sol['fee']:.2f} SOL
• Validators: {sol['validators']:,}
• Block Time: {(time.time() - sol['block_time']) / 60:.1f} min ago"""
                
        except Exception as e:
            logger.error(f"Error getting network stats: {e}")
            return "Данные временно недоступны"

    async def get_whale_movements(self, network: str) -> Optional[Dict[str, Any]]:
        """Получает информацию о движениях китов в сети."""
        try:
            network = network.lower()
            if network not in self.supported_networks:
                return None
                
            cache_key = f"whale_movements_{network}"
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data
            
            # В реальном приложении здесь будет запрос к API блокчейн-эксплорера
            # Сейчас возвращаем тестовые данные
            data = {
                'transactions_count': 15,
                'total_volume': 25000000,
                'avg_transaction': 1666666,
                'largest_transaction': 5000000,
                'timestamp': datetime.now().isoformat()
            }
            
            cache.set(cache_key, data, expire_minutes=5)
            return data
            
        except Exception as e:
            logger.error(f"Error getting whale movements for {network}: {e}")
            return None
    
    async def get_whale_transactions(self, network: str) -> Optional[List[Dict[str, Any]]]:
        """Получает список крупных транзакций в сети."""
        try:
            network = network.lower()
            if network not in self.supported_networks:
                return None
                
            cache_key = f"whale_transactions_{network}"
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data
            
            # Тестовые данные
            data = [
                {
                    'amount': 5000000,
                    'time': '2024-03-20 15:30:00',
                    'from': '0x1234...5678',
                    'to': '0x8765...4321',
                    'type': 'transfer'
                },
                {
                    'amount': 3000000,
                    'time': '2024-03-20 14:45:00',
                    'from': '0xabcd...efgh',
                    'to': '0xhgfe...dcba',
                    'type': 'transfer'
                }
            ]
            
            cache.set(cache_key, data, expire_minutes=5)
            return data
            
        except Exception as e:
            logger.error(f"Error getting whale transactions for {network}: {e}")
            return None
    
    async def get_whale_analysis(self, network: str) -> Optional[Dict[str, str]]:
        """Анализирует движения китов и их влияние на рынок."""
        try:
            network = network.lower()
            if network not in self.supported_networks:
                return None
                
            cache_key = f"whale_analysis_{network}"
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data
            
            movements = await self.get_whale_movements(network)
            if not movements:
                return None
            
            # Анализ на основе данных
            data = {
                'trend': 'Накопление',  # Накопление/Распределение
                'activity': 'Высокая активность китов',
                'recommendation': 'Возможен рост цены в ближайшее время'
            }
            
            cache.set(cache_key, data, expire_minutes=15)
            return data
            
        except Exception as e:
            logger.error(f"Error analyzing whale movements for {network}: {e}")
            return None
    
    async def get_whale_correlation(self, network: str) -> Optional[Dict[str, str]]:
        """Анализирует корреляцию движений китов с рыночными показателями."""
        try:
            network = network.lower()
            if network not in self.supported_networks:
                return None
                
            cache_key = f"whale_correlation_{network}"
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data
            
            # Тестовые данные
            data = {
                'price_correlation': 'Сильная положительная (0.85)',
                'volume_correlation': 'Умеренная (0.45)',
                'market_impact': 'Значительное влияние на цену'
            }
            
            cache.set(cache_key, data, expire_minutes=30)
            return data
            
        except Exception as e:
            logger.error(f"Error getting whale correlation for {network}: {e}")
            return None

# Create API instance
blockchain_stats = BlockchainStats() 