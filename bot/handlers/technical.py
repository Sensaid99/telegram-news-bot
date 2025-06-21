from aiogram import Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ..services.technical_analysis import TechnicalAnalysis
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(lambda c: c.data == "menu_technical")
async def show_technical_menu(callback: types.CallbackQuery):
    """Показывает меню технического анализа."""
    try:
        builder = InlineKeyboardBuilder()
        builder.button(text="BTC/USDT", callback_data="ta_btc")
        builder.button(text="ETH/USDT", callback_data="ta_eth")
        builder.button(text="BNB/USDT", callback_data="ta_bnb")
        builder.button(text="SOL/USDT", callback_data="ta_sol")
        builder.button(text="XRP/USDT", callback_data="ta_xrp")
        builder.button(text="↩️ В главное меню", callback_data="menu_main")
        builder.adjust(2, 2, 2)
        
        await callback.message.edit_text(
            "📊 Технический анализ\n\n"
            "Выберите торговую пару для анализа:",
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error in technical menu: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ В главное меню", callback_data="menu_main")
            .as_markup()
        )

@router.callback_query(lambda c: c.data.startswith("ta_"))
async def show_technical_analysis(callback: types.CallbackQuery):
    """Показывает технический анализ для выбранной пары."""
    try:
        symbol = callback.data.split("_")[1].upper()
        await callback.answer(f"Анализирую {symbol}...")
        
        ta = TechnicalAnalysis()
        analysis = await ta.get_analysis(f"{symbol}/USDT")
        
        text = f"📊 Технический анализ {symbol}/USDT\n\n"
        
        # Тренды
        text += "📈 Тренды:\n"
        text += f"• Краткосрочный (H4): {analysis['trends']['short']}\n"
        text += f"• Среднесрочный (D): {analysis['trends']['medium']}\n"
        text += f"• Долгосрочный (W): {analysis['trends']['long']}\n\n"
        
        # Уровни
        text += "🎯 Ключевые уровни:\n"
        text += f"• Сопротивление: ${analysis['levels']['resistance']:,.2f}\n"
        text += f"• Поддержка: ${analysis['levels']['support']:,.2f}\n\n"
        
        # Индикаторы
        text += "📊 Технические индикаторы:\n"
        text += f"• RSI (14): {analysis['indicators']['rsi']}\n"
        text += f"• MACD: {analysis['indicators']['macd']}\n"
        text += f"• MA (50/200): {analysis['indicators']['moving_averages']}\n"
        text += f"• Bollinger: {analysis['indicators']['bollinger']}\n\n"
        
        # Паттерны
        text += "🔍 Паттерны:\n"
        for pattern in analysis['patterns']:
            text += f"• {pattern}\n"
        text += "\n"
        
        # Объемы
        text += "📊 Анализ объемов:\n"
        text += f"• OBV: {analysis['volume']['obv']}\n"
        text += f"• Volume Profile: {analysis['volume']['profile']}\n\n"
        
        # Рекомендация
        text += f"📝 Рекомендация: {analysis['recommendation']}\n"
        text += f"⚠️ Риск: {analysis['risk']}"
        
        # Кнопки таймфреймов
        builder = InlineKeyboardBuilder()
        builder.button(text="5m", callback_data=f"timeframe_{symbol.lower()}_5m")
        builder.button(text="15m", callback_data=f"timeframe_{symbol.lower()}_15m")
        builder.button(text="1H", callback_data=f"timeframe_{symbol.lower()}_1h")
        builder.button(text="4H", callback_data=f"timeframe_{symbol.lower()}_4h")
        builder.button(text="1D", callback_data=f"timeframe_{symbol.lower()}_1d")
        builder.button(text="↩️ Назад", callback_data="menu_technical")
        builder.adjust(5, 1)
        
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error in technical analysis: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка при получении анализа. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ Назад", callback_data="menu_technical")
            .as_markup()
        )

@router.callback_query(lambda c: c.data.startswith("timeframe_"))
async def change_timeframe(callback: types.CallbackQuery):
    """Меняет таймфрейм анализа."""
    try:
        _, symbol, timeframe = callback.data.split("_")
        await callback.answer(f"Обновляю для {timeframe}...")
        
        ta = TechnicalAnalysis()
        analysis = await ta.get_analysis(f"{symbol.upper()}/USDT", timeframe)
        
        # Обновляем анализ с новым таймфреймом
        text = f"📊 Технический анализ {symbol.upper()}/USDT ({timeframe})\n\n"
        
        # Добавляем тот же анализ, но для выбранного таймфрейма
        text += "📈 Тренды:\n"
        text += f"• Текущий тренд: {analysis['trends']['current']}\n"
        text += f"• Сила тренда: {analysis['trends']['strength']}\n\n"
        
        text += "🎯 Ключевые уровни:\n"
        text += f"• Сопротивление: ${analysis['levels']['resistance']:,.2f}\n"
        text += f"• Поддержка: ${analysis['levels']['support']:,.2f}\n\n"
        
        text += "📊 Технические индикаторы:\n"
        text += f"• RSI (14): {analysis['indicators']['rsi']}\n"
        text += f"• MACD: {analysis['indicators']['macd']}\n"
        text += f"• MA (50/200): {analysis['indicators']['moving_averages']}\n"
        text += f"• Bollinger: {analysis['indicators']['bollinger']}\n\n"
        
        text += "🔍 Активные паттерны:\n"
        for pattern in analysis['patterns']:
            text += f"• {pattern}\n"
        text += "\n"
        
        text += f"📝 Рекомендация: {analysis['recommendation']}\n"
        text += f"⚠️ Риск: {analysis['risk']}"
        
        # Те же кнопки таймфреймов
        builder = InlineKeyboardBuilder()
        builder.button(text="5m", callback_data=f"timeframe_{symbol}_5m")
        builder.button(text="15m", callback_data=f"timeframe_{symbol}_15m")
        builder.button(text="1H", callback_data=f"timeframe_{symbol}_1h")
        builder.button(text="4H", callback_data=f"timeframe_{symbol}_4h")
        builder.button(text="1D", callback_data=f"timeframe_{symbol}_1d")
        builder.button(text="↩️ Назад", callback_data=f"ta_{symbol}")
        builder.adjust(5, 1)
        
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error changing timeframe: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка при смене таймфрейма. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ Назад", callback_data=f"ta_{symbol}")
            .as_markup()
        ) 