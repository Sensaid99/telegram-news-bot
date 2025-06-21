import asyncio
import aiohttp
from config import TWELVEDATA_API_KEY

async def test_symbols():
    async with aiohttp.ClientSession() as session:
        # Проверяем доступные символы
        async with session.get(f'https://api.twelvedata.com/stocks?apikey={TWELVEDATA_API_KEY}') as response:
            stocks = await response.json()
            print("Доступные акции:")
            for symbol in stocks.get('data', [])[:5]:  # Показываем первые 5
                print(f"- {symbol['symbol']}: {symbol['name']}")
                
        # Проверяем форекс пары
        async with session.get(f'https://api.twelvedata.com/forex_pairs?apikey={TWELVEDATA_API_KEY}') as response:
            forex = await response.json()
            print("\nДоступные форекс пары:")
            for pair in forex.get('data', [])[:5]:  # Показываем первые 5
                print(f"- {pair['symbol']}: {pair['name']}")
                
        # Проверяем индексы
        async with session.get(f'https://api.twelvedata.com/indices?apikey={TWELVEDATA_API_KEY}') as response:
            indices = await response.json()
            print("\nДоступные индексы:")
            for index in indices.get('data', [])[:5]:  # Показываем первые 5
                print(f"- {index['symbol']}: {index['name']}")

if __name__ == '__main__':
    asyncio.run(test_symbols()) 