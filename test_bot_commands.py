import asyncio
import logging
import sys
from datetime import datetime
from typing import Dict, Any, List

from config import *
from services.market_data import MarketData
from services.price_service import price_service
from services.blockchain_stats import BlockchainStats
from services.macro_data import MacroData
from database import get_session, User, PriceAlert
from handlers.crypto import get_crypto_info
from database import init_db

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,  # Изменяем уровень на DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout  # Добавляем вывод в stdout
)
logger = logging.getLogger(__name__)

def handle_exception(loop, context):
    """Обработчик необработанных исключений в событийном цикле."""
    msg = context.get('exception', context['message'])
    logger.error(f"Caught exception: {msg}", exc_info=context.get('exception'))

class TestRunner:
    def __init__(self):
        """Инициализация тестового окружения."""
        logger.debug("Starting test environment initialization")
        self.success_count = 0
        self.error_count = 0
        
        try:
            # Инициализация базы данных
            logger.debug("Initializing database")
            self.Session = init_db()
            self.session = self.Session()
            logger.debug("Database initialized successfully")
            
            # Инициализация сервисов
            logger.debug("Initializing services")
            self.market_data = MarketData()
            logger.info("✅ MarketData service initialized")
            
            self.blockchain_stats = BlockchainStats()
            logger.info("✅ BlockchainStats service initialized")
            
            self.macro_data = MacroData()
            logger.info("✅ MacroData service initialized")
            
            logger.info("✅ Database session initialized")
            logger.info("✅ All services initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize services: {e}", exc_info=True)
            raise
    
    async def setup(self):
        """Подготовка тестового окружения."""
        logger.debug("Starting test setup")
        try:
            # Тест получения объемов
            logger.info("\nTesting market volumes...")
            volumes = await self.market_data.get_market_volume()
            if volumes:
                logger.info(f"✅ Market volumes received: {len(volumes)} pairs")
                for symbol, data in volumes.items():
                    logger.info(f"  • {symbol}: ${data['volume']:,.2f} ({data['change']:+.2f}%)")
                self.success_count += 1
            else:
                logger.error("❌ Failed to get market volumes")
                self.error_count += 1
            
            # Тест получения трендов
            logger.info("\nTesting market trends...")
            trends = await self.market_data.get_trending_coins()
            if trends and trends != "Ошибка получения данных о трендах":
                logger.info("✅ Market trends received:")
                logger.info(trends)
                self.success_count += 1
            else:
                logger.error("❌ Failed to get market trends")
                self.error_count += 1
            
            # Тест получения данных по BTC
            logger.info("\nTesting BTC data...")
            btc_data = await self.market_data.get_bitcoin_data()
            if btc_data['price'] > 0:
                logger.info(f"✅ BTC data received: ${btc_data['price']:,.2f} ({btc_data['change_24h']:+.2f}%)")
                self.success_count += 1
            else:
                logger.error("❌ Failed to get BTC data")
                self.error_count += 1
            
            # Тест получения данных по ETH
            logger.info("\nTesting ETH data...")
            eth_data = await self.market_data.get_ethereum_data()
            if eth_data['price'] > 0:
                logger.info(f"✅ ETH data received: ${eth_data['price']:,.2f} ({eth_data['change_24h']:+.2f}%)")
                self.success_count += 1
            else:
                logger.error("❌ Failed to get ETH data")
                self.error_count += 1
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}", exc_info=True)
            self.error_count += 1
    
    async def test_blockchain_commands(self):
        """Тестирование команд блокчейн-данных."""
        logger.debug("Starting blockchain commands tests")
        logger.info("\n=== Testing Blockchain Commands ===")
        try:
            # Тест получения сетевой статистики
            logger.info("\nTesting network stats...")
            stats = await self.blockchain_stats.get_network_stats()
            if stats and "Данные временно недоступны" not in stats:
                logger.info("✅ Network stats received:")
                logger.info(stats)
                self.success_count += 1
            else:
                logger.error("❌ Failed to get network stats")
                self.error_count += 1
            
            # Тест получения метрик Bitcoin
            logger.info("\nTesting BTC metrics...")
            btc_metrics = await self.blockchain_stats.get_bitcoin_metrics()
            if btc_metrics['transactions'] > 0:
                logger.info("✅ BTC metrics received:")
                for key, value in btc_metrics.items():
                    logger.info(f"  • {key}: {value}")
                self.success_count += 1
            else:
                logger.error("❌ Failed to get BTC metrics")
                self.error_count += 1
            
            # Тест получения метрик Ethereum
            logger.info("\nTesting ETH metrics...")
            eth_metrics = await self.blockchain_stats.get_ethereum_metrics()
            if eth_metrics['gas'] > 0:
                logger.info("✅ ETH metrics received:")
                for key, value in eth_metrics.items():
                    logger.info(f"  • {key}: {value}")
                self.success_count += 1
            else:
                logger.error("❌ Failed to get ETH metrics")
                self.error_count += 1
            
        except Exception as e:
            logger.error(f"❌ Blockchain commands test failed: {e}", exc_info=True)
            self.error_count += 1
    
    async def test_macro_commands(self):
        """Тестирование макроэкономических команд."""
        logger.debug("Starting macro commands tests")
        logger.info("\n=== Testing Macro Commands ===")
        try:
            # Тест получения индикаторов
            logger.info("\nTesting market indicators...")
            indicators = await self.macro_data.get_market_indicators()
            if indicators and "Данные временно недоступны" not in indicators:
                logger.info("✅ Macro indicators received:")
                logger.info(indicators)
                self.success_count += 1
            else:
                logger.error("❌ Failed to get macro indicators")
                self.error_count += 1
            
            # Тест получения детального отчета
            logger.info("\nTesting detailed report...")
            report = await self.macro_data.get_detailed_report()
            if report and "Данные временно недоступны" not in report:
                logger.info("✅ Detailed report received:")
                logger.info(report)
                self.success_count += 1
            else:
                logger.error("❌ Failed to get detailed report")
                self.error_count += 1
            
        except Exception as e:
            logger.error(f"❌ Macro commands test failed: {e}", exc_info=True)
            self.error_count += 1
    
    async def test_database(self):
        """Тестирование работы с базой данных."""
        logger.debug("Starting database tests")
        logger.info("\n=== Testing Database Operations ===")
        try:
            # Проверяем, существует ли тестовый пользователь
            test_telegram_id = 123456789
            logger.debug(f"Checking for existing user with telegram_id {test_telegram_id}")
            existing_user = self.session.query(User).filter_by(telegram_id=test_telegram_id).first()
            if existing_user:
                logger.debug("Found existing test user, deleting")
                self.session.delete(existing_user)
                self.session.commit()
                logger.info("✅ Cleaned up existing test user")
            
            # Тест создания пользователя
            logger.debug("Creating test user")
            test_user = User(
                telegram_id=test_telegram_id,
                username="test_user",
                first_name="Test",
                last_name="User"
            )
            self.session.add(test_user)
            self.session.commit()
            logger.info("✅ Test user created")
            self.success_count += 1
            
            # Тест создания алертов
            logger.debug("Creating test alerts")
            test_alerts = [
                PriceAlert(
                    user_id=test_user.id,
                    symbol="BTC",
                    condition="above",
                    price=50000.0
                ),
                PriceAlert(
                    user_id=test_user.id,
                    symbol="ETH",
                    condition="below",
                    price=2000.0
                )
            ]
            
            for alert in test_alerts:
                self.session.add(alert)
            self.session.commit()
            logger.info("✅ Test alerts created")
            self.success_count += 1
            
            # Тест получения алертов
            logger.debug("Retrieving test alerts")
            alerts = self.session.query(PriceAlert).filter_by(user_id=test_user.id).all()
            if len(alerts) == 2:
                logger.info(f"✅ Found {len(alerts)} alerts")
                for alert in alerts:
                    logger.info(f"  • Alert: {alert.symbol} {alert.condition} {alert.price}")
                self.success_count += 1
            else:
                logger.error("❌ Failed to retrieve alerts")
                self.error_count += 1
            
            # Очистка тестовых данных
            logger.debug("Cleaning up test data")
            for alert in test_alerts:
                self.session.delete(alert)
            self.session.delete(test_user)
            self.session.commit()
            logger.info("✅ Test data cleaned up")
            self.success_count += 1
            
        except Exception as e:
            logger.error(f"❌ Database test failed: {e}", exc_info=True)
            self.error_count += 1
    
    async def cleanup(self):
        """Очистка тестового окружения."""
        logger.debug("Starting test environment cleanup")
        try:
            if hasattr(self, 'market_data'):
                await self.market_data.close()
            if hasattr(self, 'blockchain_stats'):
                await self.blockchain_stats.close()
            if hasattr(self, 'macro_data'):
                await self.macro_data.close()
            if hasattr(self, 'session'):
                self.session.close()
            logger.info("✅ Test environment cleaned up successfully")
        except Exception as e:
            logger.error(f"❌ Failed to cleanup test environment: {e}", exc_info=True)

async def main():
    """Основная функция для запуска тестов."""
    logger.debug("Starting main test function")
    runner = TestRunner()
    
    try:
        # Запуск тестов
        await runner.setup()
        await runner.test_blockchain_commands()
        await runner.test_macro_commands()
        await runner.test_database()
        
        # Вывод результатов
        logger.info("\n=== Test Summary ===")
        logger.info(f"Total tests: {runner.success_count + runner.error_count}")
        logger.info(f"Successful: {runner.success_count}")
        logger.info(f"Failed: {runner.error_count}")
        
        if runner.error_count > 0:
            logger.error(f"❌ {runner.error_count} test(s) failed")
        else:
            logger.info("✅ All tests passed")
            
    except Exception as e:
        logger.error(f"❌ Tests failed: {e}", exc_info=True)
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    try:
        logger.debug("Starting test script")
        asyncio.run(main())
        logger.debug("Test script completed")
    except KeyboardInterrupt:
        logger.info("Test script interrupted by user")
    except Exception as e:
        logger.error(f"Test script failed: {str(e)}", exc_info=True) 