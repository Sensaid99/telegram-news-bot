import logging
from typing import Dict, List
import aiohttp
from datetime import datetime, timedelta
from config import (
    ETHERSCAN_API_KEY,
    BSCSCAN_API_KEY,
    SOLSCAN_API_KEY,
    TRONGRID_API_KEY
)

logger = logging.getLogger(__name__)

class WhaleWatch:
    def __init__(self):
        self.apis = {
            'ETH': {
                'url': 'https://api.etherscan.io/api',
                'key': ETHERSCAN_API_KEY
            },
            'BNB': {
                'url': 'https://api.bscscan.com/api',
                'key': BSCSCAN_API_KEY
            },
            'SOL': {
                'url': 'https://public-api.solscan.io',
                'key': SOLSCAN_API_KEY
            },
            'TRX': {
                'url': 'https://api.trongrid.io',
                'key': TRONGRID_API_KEY
            }
        }
        
        # Минимальные суммы для определения крупных транзакций (в USD)
        self.whale_thresholds = {
            'BTC': 1000000,  # $1M
            'ETH': 500000,   # $500K
            'BNB': 200000,   # $200K
            'SOL': 100000,   # $100K
            'TRX': 100000,   # $100K
            'SUI': 50000,    # $50K
            'TON': 50000,    # $50K
            'XRP': 100000    # $100K
        }
    
    async def track_address(self, address: str, network: str) -> Dict:
        """Отслеживает активность конкретного адреса."""
        try:
            api_config = self.apis.get(network.upper())
            if not api_config:
                raise ValueError(f"Unsupported network: {network}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    api_config['url'],
                    params={
                        'module': 'account',
                        'action': 'txlist',
                        'address': address,
                        'apikey': api_config['key'],
                        'sort': 'desc'
                    }
                ) as response:
                    data = await response.json()
                    
            return self._process_transactions(data, network)
            
        except Exception as e:
            logger.error(f"Error tracking address {address} on {network}: {e}")
            return {}
    
    async def get_whale_movements(self, network: str, hours: int = 24) -> List[Dict]:
        """Получает крупные движения средств в сети."""
        try:
            api_config = self.apis.get(network.upper())
            if not api_config:
                raise ValueError(f"Unsupported network: {network}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{api_config['url']}/api/v2/transactions",
                    params={
                        'from': int((datetime.now() - timedelta(hours=hours)).timestamp()),
                        'apikey': api_config['key']
                    }
                ) as response:
                    data = await response.json()
                    
            return self._filter_whale_transactions(data, network)
            
        except Exception as e:
            logger.error(f"Error getting whale movements for {network}: {e}")
            return []
    
    def _process_transactions(self, data: Dict, network: str) -> Dict:
        """Обрабатывает транзакции адреса."""
        try:
            if not data.get('result'):
                return {}
            
            processed = {
                'total_sent': 0,
                'total_received': 0,
                'transactions': []
            }
            
            for tx in data['result'][:100]:  # Последние 100 транзакций
                amount = float(tx['value']) / 1e18  # Конвертация из wei/satoshi
                if tx['from'].lower() == address.lower():
                    processed['total_sent'] += amount
                else:
                    processed['total_received'] += amount
                    
                processed['transactions'].append({
                    'hash': tx['hash'],
                    'timestamp': datetime.fromtimestamp(int(tx['timeStamp'])),
                    'from': tx['from'],
                    'to': tx['to'],
                    'amount': amount,
                    'type': 'out' if tx['from'].lower() == address.lower() else 'in'
                })
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing transactions: {e}")
            return {}
    
    def _filter_whale_transactions(self, data: List[Dict], network: str) -> List[Dict]:
        """Фильтрует крупные транзакции."""
        try:
            whale_txs = []
            threshold = self.whale_thresholds.get(network.upper(), 100000)
            
            for tx in data:
                amount_usd = float(tx.get('value_usd', 0))
                if amount_usd >= threshold:
                    whale_txs.append({
                        'hash': tx['hash'],
                        'from': tx['from'],
                        'to': tx['to'],
                        'amount': float(tx['value']),
                        'amount_usd': amount_usd,
                        'timestamp': datetime.fromtimestamp(int(tx['timestamp']))
                    })
            
            return whale_txs
            
        except Exception as e:
            logger.error(f"Error filtering whale transactions: {e}")
            return []
    
    async def analyze_movements(self, network: str) -> str:
        """Анализирует движения китов и их возможное влияние."""
        try:
            movements = await self.get_whale_movements(network)
            if not movements:
                return f"Нет крупных движений в сети {network}"
            
            analysis = f"🐋 Анализ движений китов в сети {network}:\n\n"
            
            # Группировка по направлению (на биржу/с биржи)
            exchange_inflow = 0
            exchange_outflow = 0
            
            for tx in movements:
                if self._is_exchange_address(tx['to']):
                    exchange_inflow += tx['amount_usd']
                elif self._is_exchange_address(tx['from']):
                    exchange_outflow += tx['amount_usd']
            
            # Анализ тренда
            analysis += "📊 Общая статистика за 24 часа:\n"
            analysis += f"• Приток на биржи: ${exchange_inflow:,.2f}\n"
            analysis += f"• Отток с бирж: ${exchange_outflow:,.2f}\n\n"
            
            # Определение настроения
            if exchange_outflow > exchange_inflow * 1.5:
                analysis += "📈 Киты активно выводят средства с бирж - возможен рост\n"
            elif exchange_inflow > exchange_outflow * 1.5:
                analysis += "📉 Киты переводят средства на биржи - возможна коррекция\n"
            else:
                analysis += "➡️ Нет явного тренда в движениях китов\n"
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing whale movements: {e}")
            return "Ошибка при анализе движений"
    
    def _is_exchange_address(self, address: str) -> bool:
        """Проверяет, является ли адрес биржевым."""
        # Здесь должен быть список известных адресов бирж
        exchange_addresses = {
            'binance': ['0x28C6c06298d514Db089934071355E5743bf21d60'],
            'coinbase': ['0x71660c4005BA85c37ccec55d0C4493E66Fe775d3'],
            'ftx': ['0x2FAF487A4414Fe77e2327F0bf4AE2a264a776AD2'],
            'kucoin': ['0x0681d8Db095565Fe8A346fA0277bFfdE9C0eDBBF']
        }
        
        return any(
            address.lower() == ex_addr.lower()
            for exchange in exchange_addresses.values()
            for ex_addr in exchange
        ) 