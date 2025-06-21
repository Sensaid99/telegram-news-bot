import requests
from typing import List, Dict
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from utils import load_from_cache, save_to_cache

class LookOnChainParser:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_whale_moves(self) -> List[Dict]:
        """Получить последние крупные движения с LookOnChain."""
        cache_key = 'whale_moves'
        cached_data = load_from_cache(cache_key)
        if cached_data:
            return cached_data
            
        try:
            # В реальном проекте здесь будет парсинг Twitter API или Telegram API
            # Для демонстрации возвращаем тестовые данные
            moves = [
                {
                    'time': datetime.now() - timedelta(hours=1),
                    'type': 'transfer',
                    'amount': 1000,
                    'token': 'BTC',
                    'from_address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
                    'to_address': '3D2oetdNuZUqQHPJmcMDDHYoqkyNVsFk9r',
                    'source': 'Binance'
                },
                {
                    'time': datetime.now() - timedelta(hours=2),
                    'type': 'deposit',
                    'amount': 5000,
                    'token': 'ETH',
                    'from_address': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
                    'to_address': 'Binance',
                    'source': 'Unknown Wallet'
                }
            ]
            
            # Сохраняем в кэш на 5 минут
            save_to_cache(cache_key, moves, expire_minutes=5)
            return moves
            
        except Exception as e:
            print(f"Ошибка получения китовых движений: {e}")
            return []
    
    def format_whale_alert(self, move: Dict) -> str:
        """Форматировать сообщение о движении китов."""
        if move['type'] == 'transfer':
            return (
                f"🐋 Перемещение {move['amount']} {move['token']}\n"
                f"От: {move['from_address'][:8]}...\n"
                f"К: {move['to_address'][:8]}...\n"
                f"Источник: {move['source']}"
            )
        elif move['type'] == 'deposit':
            return (
                f"📥 Депозит {move['amount']} {move['token']}\n"
                f"От: {move['from_address'][:8]}...\n"
                f"На биржу: {move['to_address']}"
            )
        else:
            return (
                f"💰 Движение {move['amount']} {move['token']}\n"
                f"Детали: {move['from_address']} → {move['to_address']}"
            )

# Создаем единственный экземпляр
lookonchain_parser = LookOnChainParser() 