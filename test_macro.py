import asyncio
import logging
from services.macro_data import macro_data

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_macro():
    try:
        print("Getting macro metrics...")
        metrics = await macro_data.get_macro_metrics()
        print("\nMacro metrics:")
        print(f"DXY: {metrics['dxy']:.2f}")
        print(f"Gold: ${metrics['gold']:,.2f}")
        print(f"S&P 500: {metrics['sp500']:,.2f}")
        print(f"VIX: {metrics['vix']:.2f}")
        
        print("\nGetting rates...")
        rates = await macro_data.get_rates()
        print("\nRates:")
        print(f"FED: {rates['fed']}%")
        print(f"ECB: {rates['ecb']}%")
        print(f"BOE: {rates['boe']}%")
        print(f"BOJ: {rates['boj']}%")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await macro_data.close()

if __name__ == '__main__':
    asyncio.run(test_macro()) 