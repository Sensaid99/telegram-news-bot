import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env файл
load_dotenv()

# Базовые настройки
BASE_DIR = Path(__file__).resolve().parent
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_IDS = [int(id_str) for id_str in os.getenv("ADMIN_IDS", "").split(",") if id_str.strip()]

# APIs
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# Blockchain APIs
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY")
SOLSCAN_API_KEY = os.getenv("SOLSCAN_API_KEY")
TRONGRID_API_KEY = os.getenv("TRONGRID_API_KEY")

# Other Services
INVESTING_API_KEY = os.getenv("INVESTING_API_KEY")
COINMARKETCAP_API_KEY = os.getenv("COINMARKETCAP_API_KEY")
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db/quantnews.db")

# Cache
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 минут
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "True").lower() == "true"

# Market Data
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "300"))  # 5 минут
NOTIFICATION_DELAY = int(os.getenv("NOTIFICATION_DELAY", "60"))  # 1 минута
CALENDAR_UPDATE_INTERVAL = int(os.getenv("CALENDAR_UPDATE_INTERVAL", "3600"))  # 1 час

SUPPORTED_CURRENCIES = [
    "BTC", "ETH", "BNB", "SOL", "XRP", "TRX", "TON", "SUI",
    "USDT", "USDC", "BUSD", "DAI"
]
SUPPORTED_NETWORKS = ["BTC", "ETH", "BSC", "SOL", "XRP", "TRON"]

# Technical Analysis
TA_TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"]
TA_INDICATORS = ["MA", "EMA", "RSI", "MACD", "BB"]
TA_UPDATE_INTERVAL = int(os.getenv("TA_UPDATE_INTERVAL", "900"))  # 15 минут

# Whale Tracking
WHALE_THRESHOLD = {
    "BTC": float(os.getenv("WHALE_BTC", "100")),     # 100 BTC
    "ETH": float(os.getenv("WHALE_ETH", "1000")),    # 1000 ETH
    "BNB": float(os.getenv("WHALE_BNB", "5000")),    # 5000 BNB
    "SOL": float(os.getenv("WHALE_SOL", "50000")),   # 50000 SOL
    "XRP": float(os.getenv("WHALE_XRP", "1000000")), # 1M XRP
    "TRX": float(os.getenv("WHALE_TRX", "5000000"))  # 5M TRX
}

# Economic Calendar
CALENDAR_REGIONS = ["US", "EU", "CN", "JP", "GB"]
CALENDAR_IMPORTANCE = ["high", "medium", "low"]

# User Settings
DEFAULT_CURRENCY = "USD"
DEFAULT_TIMEZONE = "UTC"
DEFAULT_TIME_FORMAT = "24h"
DEFAULT_THEME = "light"

# Error Messages
ERROR_MESSAGES = {
    "general": "⚠️ Произошла ошибка. Попробуйте позже.",
    "api_error": "⚠️ Ошибка API. Попробуйте позже.",
    "not_found": "⚠️ Данные не найдены.",
    "invalid_input": "⚠️ Неверный формат ввода.",
    "rate_limit": "⚠️ Превышен лимит запросов. Попробуйте позже.",
    "maintenance": "🛠 Ведутся технические работы. Попробуйте позже."
}

# Success Messages
SUCCESS_MESSAGES = {
    "alert_set": "✅ Уведомление установлено",
    "alert_removed": "✅ Уведомление удалено",
    "settings_updated": "✅ Настройки обновлены",
    "subscription_success": "✅ Подписка оформлена"
}

# Subscription Settings
SUBSCRIPTION_PRICE = float(os.getenv('SUBSCRIPTION_PRICE', '10.0'))  # USD
FREE_ALERTS_LIMIT = int(os.getenv('FREE_ALERTS_LIMIT', '3'))

# Alert Settings
ALERT_CHECK_INTERVAL = int(os.getenv('ALERT_CHECK_INTERVAL', '300'))  # seconds
DAILY_REPORT_TIME = os.getenv('DAILY_REPORT_TIME', '08:00')  # UTC

# Content Generation
MIN_POSTS_PER_DAY = int(os.getenv('MIN_POSTS_PER_DAY', '3'))
MAX_POSTS_PER_DAY = int(os.getenv('MAX_POSTS_PER_DAY', '5'))

# Supported Cryptocurrencies
SUPPORTED_COINS = [
    'BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 
    'AVAX', 'MATIC', 'DOT', 'LINK'
] 