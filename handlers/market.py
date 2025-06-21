from aiogram import Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.market_data import MarketData
from services.macro_data import MacroData
import logging

logger = logging.getLogger(__name__)
router = Router()

def format_price_change(change: float) -> str:
    """Форматирует изменение цены с эмодзи."""
    if change > 0:
        return f"🟢 +{change:.2f}%"
    elif change < 0:
        return f"🔴 {change:.2f}%"
    return f"⚪️ {change:.2f}%"

def format_volume_change(change: float) -> str:
    """Форматирует изменение объема с эмодзи."""
    if change > 0:
        return f"📈 +{change:.2f}%"
    elif change < 0:
        return f"📉 {change:.2f}%"
    return f"➡️ {change:.2f}%"

def format_volume_share(share: float) -> str:
    """Форматирует долю объема с эмодзи."""
    if share > 20:
        return f"🔥 {share:.1f}%"
    elif share > 10:
        return f"💫 {share:.1f}%"
    elif share > 5:
        return f"✨ {share:.1f}%"
    return f"💧 {share:.1f}%"

@router.callback_query(lambda c: c.data == "menu_market")
async def show_market_analysis(callback: types.CallbackQuery):
    """Показывает рыночный анализ."""
    try:
        market = MarketData()
        macro = MacroData()
        
        # Получаем данные
        volume_data = await market.get_market_volume()
        trends = await market.get_trending_coins()
        market_state = await macro.get_market_state()
        
        # Формируем сокращенный отчет
        text = "📊 Рыночный анализ\n\n"
        
        # Состояние рынка
        text += f"🌍 Рынок: {market_state['state']}\n"
        text += f"📈 Тренд: {market_state['trend']}\n"
        text += f"⚡️ Волатильность: {market_state['volatility']}\n\n"
        
        # Топ-5 по объему
        text += "💎 Топ объемов (24ч):\n"
        for i, (symbol, data) in enumerate(list(volume_data.items())[:5], 1):
            price_usdt = data['price']
            price_change = data['price_change']
            volume_change = data['volume_change']
            volume_share = data['volume_share']
            high_24h = data['high_24h']
            low_24h = data['low_24h']
            network = data['network']
            
            text += (
                f"{i}. {symbol}/USDT ({network})\n"
                f"   💰 Цена: ${price_usdt:,.2f}\n"
                f"   📊 24ч: {format_price_change(price_change)}\n"
                f"   📈 Объем: ${data['volume']:,.0f}\n"
                f"   💫 Доля объема: {format_volume_share(volume_share)}\n"
                f"   📊 24ч High/Low: ${high_24h:,.2f} / ${low_24h:,.2f}\n\n"
            )
        
        # Тренды (топ-3)
        text += "🔥 Тренды:\n"
        trend_lines = trends.split('\n\n')[:3]
        text += '\n\n'.join(trend_lines)
        
        # Кнопки
        builder = InlineKeyboardBuilder()
        builder.button(text="📊 Подробный анализ", callback_data="market_detailed")
        builder.button(text="📈 Графики", callback_data="market_charts")
        builder.button(text="↩️ В главное меню", callback_data="menu_main")
        builder.adjust(2, 1)
        
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error in market analysis: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка при получении рыночных данных. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ В главное меню", callback_data="menu_main")
            .as_markup()
        )

@router.callback_query(lambda c: c.data == "market_detailed")
async def show_detailed_analysis(callback: types.CallbackQuery):
    """Показывает подробный рыночный анализ."""
    try:
        market = MarketData()
        macro = MacroData()
        
        # Получаем расширенные данные
        volume_data = await market.get_market_volume()
        market_state = await macro.get_market_state()
        correlations = await macro.get_correlations()
        
        text = "📊 Подробный анализ рынка\n\n"
        
        # Состояние рынка
        text += f"🌍 Состояние: {market_state['state']}\n"
        text += f"📈 Тренд: {market_state['trend']}\n"
        text += f"⚡️ Волатильность: {market_state['volatility']}\n"
        text += f"💰 Ликвидность: {market_state['liquidity']}\n\n"
        
        # Объемы всех монет
        text += "💎 Объемы торгов (24ч):\n"
        for symbol, data in volume_data.items():
            price_usdt = data['price']
            price_change = data['price_change']
            volume_change = data['volume_change']
            volume_share = data['volume_share']
            high_24h = data['high_24h']
            low_24h = data['low_24h']
            network = data['network']
            
            text += (
                f"• {symbol}/USDT ({network})\n"
                f"  💰 Цена: ${price_usdt:,.2f}\n"
                f"  📊 24ч: {format_price_change(price_change)}\n"
                f"  📈 Объем: ${data['volume']:,.0f}\n"
                f"  💫 Доля объема: {format_volume_share(volume_share)}\n"
                f"  📊 24ч High/Low: ${high_24h:,.2f} / ${low_24h:,.2f}\n\n"
            )
        
        # Корреляции
        text += "📊 Корреляции:\n"
        text += f"• BTC-ETH: {correlations['btc_eth']}\n"
        text += f"• Крипто-S&P500: {correlations['crypto_sp500']}\n"
        text += f"• Крипто-Gold: {correlations['crypto_gold']}\n"
        
        # Кнопки
        builder = InlineKeyboardBuilder()
        builder.button(text="↩️ Назад", callback_data="menu_market")
        builder.button(text="📈 Графики", callback_data="market_charts")
        builder.adjust(2)
        
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error in detailed market analysis: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка при получении данных. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ Назад", callback_data="menu_market")
            .as_markup()
        )

@router.callback_query(lambda c: c.data == "market_charts")
async def show_market_charts(callback: types.CallbackQuery):
    """Показывает графики рынка."""
    try:
        # Кнопки для выбора графика
        builder = InlineKeyboardBuilder()
        builder.button(text="BTC/USDT", callback_data="chart_BTCUSDT")
        builder.button(text="ETH/USDT", callback_data="chart_ETHUSDT")
        builder.button(text="SOL/USDT", callback_data="chart_SOLUSDT")
        builder.button(text="BNB/USDT", callback_data="chart_BNBUSDT")
        builder.button(text="TRX/USDT", callback_data="chart_TRXUSDT")
        builder.button(text="TON/USDT", callback_data="chart_TONUSDT")
        builder.button(text="XRP/USDT", callback_data="chart_XRPUSDT")
        builder.button(text="SUI/USDT", callback_data="chart_SUIUSDT")
        builder.button(text="↩️ Назад", callback_data="menu_market")
        builder.adjust(2, 2, 2, 2, 1)
        
        await callback.message.edit_text(
            "📈 Выберите график для просмотра:",
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error showing market charts: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка при загрузке графиков. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ Назад", callback_data="menu_market")
            .as_markup()
        ) 