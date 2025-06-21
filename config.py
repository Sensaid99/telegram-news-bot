import os
import logging
from dotenv import load_dotenv
import importlib.util
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config():
    """Загружает конфигурацию из .env или env_example.py"""
    # Сначала пробуем загрузить из .env
    logger.info("Trying to load configuration from .env...")
    load_dotenv(verbose=True)
    
    # Если не все переменные загружены, пробуем загрузить из env_example.py
    if not all(os.getenv(key) for key in ['BOT_TOKEN', 'CHANNEL_ID']):
        logger.info("Some variables missing in .env, trying env_example.py...")
        try:
            spec = importlib.util.spec_from_file_location("env_example", "env_example.py")
            env_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(env_module)
            
            # Загружаем переменные из модуля в os.environ
            for key in dir(env_module):
                if not key.startswith('__'):
                    value = getattr(env_module, key)
                    if isinstance(value, str):
                        os.environ[key] = value
            logger.info("✅ Configuration loaded from env_example.py")
        except Exception as e:
            logger.error(f"❌ Failed to load env_example.py: {e}")

# Загружаем конфигурацию
load_config()

# Проверка всех переменных окружения
required_keys = [
    'BOT_TOKEN',
    'CHANNEL_ID',
    'ETHERSCAN_API_KEY',
    'BSCSCAN_API_KEY',
    'SOLSCAN_API_KEY',
    'TRONGRID_API_KEY',
    'INVESTING_API_KEY',
    'BINANCE_API_KEY',
    'BINANCE_API_SECRET',
    'TWELVEDATA_API_KEY'
]

for key in required_keys:
    if os.getenv(key):
        logger.info(f"✅ {key} loaded successfully")
    else:
        logger.warning(f"⚠️ {key} not found")

# Основные настройки бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("BOT_TOKEN not found in environment variables")

# Admin Configuration
admin_ids_str = os.getenv('ADMIN_IDS', '')
ADMIN_IDS = [int(id_str) for id_str in admin_ids_str.split(',') if id_str.strip()]
logger.info(f"Admin IDs configured: {ADMIN_IDS}")

# Channel Configuration
CHANNEL_ID = os.getenv('CHANNEL_ID')
logger.info(f"Channel ID configured: {CHANNEL_ID}")

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///db/quantnews.db')
logger.info(f"Using database: {DATABASE_URL}")

# API Keys
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
BSCSCAN_API_KEY = os.getenv('BSCSCAN_API_KEY')
SOLSCAN_API_KEY = os.getenv('SOLSCAN_API_KEY')
TRONGRID_API_KEY = os.getenv('TRONGRID_API_KEY')
INVESTING_API_KEY = os.getenv('INVESTING_API_KEY')
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
TWELVEDATA_API_KEY = os.getenv('TWELVEDATA_API_KEY')

# Scheduler Configuration
DAILY_REPORT_TIME = "09:00"  # Время отправки ежедневного отчета (UTC)
MAX_DAILY_POSTS = 6

# Alert Configuration
DEFAULT_ALERT_CHECK_INTERVAL = 5  # minutes
MAX_ALERTS_FREE_TIER = 3
MAX_ALERTS_PREMIUM_TIER = 10

# Content Generation
MIN_POST_INTERVAL = 14400  # 4 часа в секундах

# Subscription prices (in RUB)
SUBSCRIPTION_PRICES = {
    'monthly': 990,
    'quarterly': 2490,
    'yearly': 9990
}

# Настройки логирования
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'bot.log')

# Whale Tracking
WHALE_THRESHOLD = {
    "BTC": 1000000,  # $1M
    "ETH": 500000,   # $500K
    "BNB": 200000,   # $200K
    "SOL": 100000,   # $100K
    "TRX": 100000,   # $100K
    "SUI": 50000,    # $50K
    "TON": 50000,    # $50K
    "XRP": 100000    # $100K
}

# Загружаем переменные окружения
load_dotenv()

# Базовые настройки
BASE_DIR = Path(__file__).resolve().parent
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# APIs
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# Blockchain APIs
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY")
SOLSCAN_API_KEY = os.getenv("SOLSCAN_API_KEY")
TRONGRID_API_KEY = os.getenv("TRONGRID_API_KEY")

# Other Services
FOREX_FACTORY_API_KEY = os.getenv("FOREX_FACTORY_API_KEY")
CRYPTOPANIC_API_KEY = os.getenv("CRYPTOPANIC_API_KEY")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bot.db")

# Cache
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 минут
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "True").lower() == "true"

# Notifications
NOTIFICATION_DELAY = int(os.getenv("NOTIFICATION_DELAY", "60"))  # 1 минута
MAX_ALERTS_PER_USER = int(os.getenv("MAX_ALERTS_PER_USER", "10"))

# Market Data
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "300"))  # 5 минут
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
CALENDAR_UPDATE_INTERVAL = int(os.getenv("CALENDAR_UPDATE_INTERVAL", "3600"))  # 1 час
CALENDAR_REGIONS = ["US", "EU", "CN", "JP", "GB"]
CALENDAR_IMPORTANCE = ["high", "medium", "low"]

# User Settings
DEFAULT_CURRENCY = "USD"
DEFAULT_TIMEZONE = "UTC"
DEFAULT_TIME_FORMAT = "24h"
DEFAULT_THEME = "light"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = os.path.join(BASE_DIR, "bot.log")

# Security
MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60"))
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))  # 30 секунд

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

# Help Messages
HELP_MESSAGES = {
    "start": """
🤖 Добро пожаловать в Crypto Market Bot!

Этот бот поможет вам:
• Отслеживать цены криптовалют
• Анализировать рыночные тренды
• Получать технический анализ
• Следить за активностью китов
• Быть в курсе важных событий

Используйте меню для навигации или команды:
/help - Эта справка
/settings - Настройки
    """,
    "crypto": """
💰 Команды для работы с криптовалютами:

/p <символ> - Текущая цена
/v <символ> - Объем торгов
/c <символ> - График цены
/i <символ> - Полная информация

Пример: /p BTC
    """,
    "alerts": """
🔔 Команды для уведомлений:

/alert_price <символ> <цена> - Уведомление о цене
/alert_volume <символ> <объем> - Уведомление об объеме
/alert_whale <сеть> <сумма> - Уведомление о ките
/alerts_list - Список уведомлений
/alerts_clear - Очистить уведомления

Пример: /alert_price BTC 50000
    """,
    "analysis": """
📊 Команды для анализа:

/market - Рыночный анализ
/macro - Макроэкономика
/ta <символ> - Технический анализ
/whales <сеть> - Активность китов

Пример: /ta ETH
    """,
    "settings": """
⚙️ Команды настроек:

/currency <код> - Изменить валюту
/timezone <зона> - Изменить часовой пояс
/format <формат> - Формат времени
/theme <тема> - Сменить тему

Пример: /currency EUR
    """
} 