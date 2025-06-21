import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from .config import BOT_TOKEN, CHANNEL_ID
from .handlers.menu import router as menu_router
from .handlers.crypto import router as crypto_router
from .handlers.market import router as market_router
from .handlers.macro import router as macro_router
from .handlers.technical import router as technical_router
from .handlers.whales import router as whales_router
from .handlers.settings import router as settings_router
from .handlers.help import router as help_router
from .services.scheduler import TaskScheduler
from .services.market_data import MarketData
from .services.blockchain_stats import BlockchainStats
from .services.macro_data import MacroData
from .services.cache import cache

# Настройка логирования
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bot.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Глобальные сервисы
market_data = None
blockchain_stats = None
macro_data = None
scheduler = None

async def init_services():
    """Асинхронная инициализация сервисов."""
    global market_data, blockchain_stats, macro_data, scheduler
    
    logger.info("Initializing services...")
    try:
        # Инициализируем сервисы
        market_data = MarketData()
        blockchain_stats = BlockchainStats()
        macro_data = MacroData()
        scheduler = TaskScheduler()
        scheduler.start()
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
        raise

async def main():
    """Основная функция бота."""
    try:
        # Инициализируем сервисы
        await init_services()
        
        # Инициализируем бота
        bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
        dp = Dispatcher(storage=MemoryStorage())
        
        # Регистрируем обработчики
        dp.include_router(menu_router)
        dp.include_router(crypto_router)
        dp.include_router(market_router)
        dp.include_router(macro_router)
        dp.include_router(technical_router)
        dp.include_router(whales_router)
        dp.include_router(settings_router)
        dp.include_router(help_router)
        
        # Запускаем бота
        logger.info("Starting bot...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        # Очищаем кэш при выключении
        cache.clear()
        if scheduler:
            scheduler.stop()
    except Exception as e:
        logger.error(f"Bot stopped with error: {e}")
        raise 