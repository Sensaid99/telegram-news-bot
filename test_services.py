import logging
from services.binance import binance_api
from services.whale_watch import WhaleWatch
from services.coinmarketcap import CoinMarketCapAPI

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_binance():
    logger.info("Testing Binance API...")
    try:
        # Проверка получения глубины рынка
        depth = binance_api.get_market_depth("BTCUSDT")
        logger.info(f"Market depth received: {len(depth.get('bids', []))} bids, {len(depth.get('asks', []))} asks")
        
        # Проверка получения фандинг рейтов
        rates = binance_api.get_funding_rates(["BTCUSDT", "ETHUSDT"])
        logger.info(f"Funding rates received: {rates}")
        
        return True
    except Exception as e:
        logger.error(f"Binance API test failed: {e}")
        return False

def test_whale_watch():
    logger.info("Testing WhaleWatch...")
    try:
        whale_watch = WhaleWatch()
        # Проверим инициализацию и доступ к API ключам
        logger.info(f"Available networks: {list(whale_watch.apis.keys())}")
        return True
    except Exception as e:
        logger.error(f"WhaleWatch test failed: {e}")
        return False

def test_coinmarketcap():
    logger.info("Testing CoinMarketCap API...")
    try:
        cmc = CoinMarketCapAPI()
        data = cmc.get_latest_prices(['BTC', 'ETH'])
        logger.info(f"Price data received: {data}")
        return True
    except Exception as e:
        logger.error(f"CoinMarketCap API test failed: {e}")
        return False

if __name__ == "__main__":
    services_status = {
        "Binance": test_binance(),
        "WhaleWatch": test_whale_watch(),
        "CoinMarketCap": test_coinmarketcap()
    }
    
    logger.info("\nServices Status Summary:")
    for service, status in services_status.items():
        logger.info(f"{service}: {'✅ Working' if status else '❌ Failed'}") 