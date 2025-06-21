import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import ADMIN_IDS
from services.macro_data import macro_data
from services.market_analysis import market_analysis
import asyncio

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("test_macro"))
async def test_macro_command(message: Message):
    """Тестовый обработчик для проверки макроэкономических данных."""
    try:
        logger.info(f"Received test_macro command from user {message.from_user.id}")
        
        if message.from_user.id not in ADMIN_IDS:
            logger.warning(f"Unauthorized access attempt from user {message.from_user.id}")
            await message.reply("⛔️ У вас нет доступа к этой команде.")
            return
            
        logger.info("User is admin, proceeding with macro data")
        
        # Получаем макроэкономические данные
        metrics = await macro_data.get_macro_metrics()
        rates = await macro_data.get_rates()
        
        logger.info(f"Got metrics: {metrics}")
        logger.info(f"Got rates: {rates}")
        
        # Анализируем состояние рынка
        market_state = market_analysis.get_market_state(metrics, rates)
        
        # Формируем отчет
        report = f"""📊 *Макроэкономический анализ*

🌍 *Общее состояние рынка:* {market_state['indicator']}
• Бычьи факторы: {market_state['bullish_factors']}
• Медвежьи факторы: {market_state['bearish_factors']}

💵 *DXY (Индекс доллара):* {metrics.get('dxy', 'N/A')} {market_state['analysis']['dxy']['trend']}
• {market_state['analysis']['dxy']['strength']}
• Изменение: {market_state['analysis']['dxy']['change']:.2f}%

📈 *S&P 500:* {metrics.get('sp500', 'N/A')} {market_state['analysis']['sp500']['trend']}
• {market_state['analysis']['sp500']['state']}
• Изменение: {market_state['analysis']['sp500']['change']:.2f}%

📊 *NASDAQ:* {metrics.get('nasdaq', 'N/A')} {market_state['analysis']['nasdaq']['trend']}
• Изменение: {market_state['analysis']['nasdaq']['change']:.2f}%

📉 *VIX (Волатильность):* {metrics.get('vix', 'N/A')} {market_state['analysis']['vix']['trend']}
• {market_state['analysis']['vix']['risk_level']} риск
• Изменение: {market_state['analysis']['vix']['change']:.2f}%

🏦 *Ставки ЦБ:*
• ФРС: {rates.get('fed', 'N/A')}%
• ЕЦБ: {rates.get('ecb', 'N/A')}%
• БА: {rates.get('boe', 'N/A')}%
• БЯ: {rates.get('boj', 'N/A')}%

📈 *Доходность трежерис:*
• 10Y: {metrics.get('treasury_10y', 'N/A')}% {market_state['analysis']['treasuries']['trend']}
• 2Y: {metrics.get('treasury_2y', 'N/A')}%
• Спред: {market_state['analysis']['treasuries']['spread']:.2f}%
• Кривая: {market_state['analysis']['treasuries']['state']}

🪙 *Золото:* ${metrics.get('gold', 'N/A')} {market_state['analysis']['gold']['trend']}
• Изменение: {market_state['analysis']['gold']['change']:.2f}%

🛢 *Нефть:* ${metrics.get('crude_oil', 'N/A')} {market_state['analysis']['crude_oil']['trend']}
• Изменение: {market_state['analysis']['crude_oil']['change']:.2f}%

*Анализ рынка:*
{market_state['analysis']['dxy']['impact']}

{market_state['analysis']['vix']['interpretation']}

{market_state['analysis']['treasuries']['interpretation']}
"""
        
        logger.info("Sending report...")
        await message.answer(report, parse_mode="Markdown")
        logger.info("Report sent successfully")
        
    except Exception as e:
        logger.error(f"Error in test_macro command: {e}")
        await message.answer("❌ Произошла ошибка при получении макроэкономических данных.") 