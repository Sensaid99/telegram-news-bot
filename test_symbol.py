import asyncio
import aiohttp
from config import TWELVEDATA_API_KEY

async def test_symbol(symbol: str):
    async with aiohttp.ClientSession() as session:
        url = f'https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&outputsize=1&apikey={TWELVEDATA_API_KEY}'
        print(f"Testing URL: {url}")
        
        async with session.get(url) as response:
            data = await response.json()
            print(f"\nResponse for {symbol}:")
            print(data)

if __name__ == '__main__':
    # Тестируем каждый символ
    symbols = ['EUR/USD', 'XAU/USD', 'SPY', 'UVXY']
    for symbol in symbols:
        print(f"\nTesting {symbol}...")
        asyncio.run(test_symbol(symbol)) 