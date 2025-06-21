from typing import Dict
from services.market_data import MarketData
from services.cache_manager import cache
from services.blockchain_stats import BlockchainStats
from services.macro_data import MacroData
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def generate_report() -> str:
    """Генерирует краткий отчет о рынке."""
    try:
        # Проверяем кэш
        cache_key = f"daily_report_{datetime.utcnow().strftime('%Y-%m-%d_%H')}"
        cached_report = cache.get(cache_key)
        if cached_report:
            return cached_report
        
        market = MarketData()
        
        # Получаем данные о объемах
        volumes = await market.get_market_volume()
        
        # Получаем тренды
        trends = await market.get_trending_coins()
        
        # Формируем отчет
        report = "📊 Ежедневный отчет\n\n"
        
        # Добавляем информацию об объемах
        report += "💰 Топ по объему торгов (24ч):\n"
        for coin_id, data in volumes.items():
            report += f"• {data['symbol']}: ${data['volume']:,.0f}\n"
            report += f"  Изменение: {data['change']:+.1f}%\n"
        
        report += "\n🔥 Тренды:\n"
        report += trends
        
        # Сохраняем в кэш на 1 час
        cache.set(cache_key, report, expire_minutes=60)
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return "❌ Ошибка при генерации отчета. Попробуйте позже."

async def generate_detailed_report() -> str:
    """Генерирует подробный отчет о рынке с блокчейн-метриками и макроданными."""
    try:
        cache_key = f"detailed_report_{datetime.utcnow().strftime('%Y-%m-%d_%H')}"
        cached_report = cache.get(cache_key)
        if cached_report:
            return cached_report
            
        market = MarketData()
        blockchain = BlockchainStats()
        macro = MacroData()
        
        # Получаем все необходимые данные
        volumes = await market.get_market_volume()
        trends = await market.get_trending_coins()
        chain_stats = await blockchain.get_network_stats()
        macro_data = await macro.get_market_indicators()
        
        # Формируем подробный отчет
        report = "📊 Подробный рыночный отчет\n\n"
        
        # Объемы торгов
        report += "💰 Топ по объему торгов (24ч):\n"
        for coin_id, data in volumes.items():
            report += f"• {data['symbol']}: ${data['volume']:,.0f}\n"
            report += f"  Изменение: {data['change']:+.1f}%\n"
        
        # Тренды
        report += "\n🔥 Тренды:\n"
        report += trends
        
        # Блокчейн-метрики
        report += "\n⛓ Сетевая активность:\n"
        report += chain_stats
        
        # Макроэкономические показатели
        report += "\n🌍 Макроэкономика:\n"
        report += macro_data
        
        # Сохраняем в кэш на 1 час
        cache.set(cache_key, report, expire_minutes=60)
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating detailed report: {e}")
        return "❌ Ошибка при генерации подробного отчета. Попробуйте позже." 