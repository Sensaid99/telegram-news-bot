from aiogram import Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.macro_data import MacroData
from services.news_service import NewsService
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(lambda c: c.data == "menu_macro")
async def show_macro_analysis(callback: types.CallbackQuery):
    """Показывает макроэкономический анализ."""
    try:
        macro = MacroData()
        news = NewsService()
        
        # Получаем данные
        indicators = await macro.get_indicators()
        market_impact = await macro.get_market_impact()
        news_data = await news.get_market_news()
        
        # Формируем отчет
        text = "📊 Макроэкономический анализ\n\n"
        
        # Ключевые индикаторы
        text += "📈 Ключевые индикаторы:\n"
        text += f"• S&P 500: {indicators['sp500']}\n"
        text += f"• DXY: {indicators['dxy']}\n"
        text += f"• Gold: {indicators['gold']}\n"
        text += f"• Oil: {indicators['oil']}\n\n"
        
        # Влияние на рынок
        text += "🎯 Влияние на крипторынок:\n"
        for factor, impact in market_impact.items():
            text += f"• {factor}: {impact}\n"
        text += "\n"
        
        # Важные новости
        text += "📰 Ключевые новости:\n"
        for news_item in news_data[:3]:  # Топ-3 новости
            text += f"• {news_item['title']}\n"
            text += f"  Влияние: {news_item['impact']}\n\n"
        
        # Кнопки
        builder = InlineKeyboardBuilder()
        builder.button(text="📰 Все новости", callback_data="macro_news")
        builder.button(text="📊 Индикаторы", callback_data="macro_indicators")
        builder.button(text="📅 Календарь", callback_data="macro_calendar")
        builder.button(text="↩️ В главное меню", callback_data="menu_main")
        builder.adjust(2, 2)
        
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error in macro analysis: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка при получении макроэкономических данных. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ В главное меню", callback_data="menu_main")
            .as_markup()
        )

@router.callback_query(lambda c: c.data == "macro_news")
async def show_macro_news(callback: types.CallbackQuery):
    """Показывает все макроэкономические новости."""
    try:
        news = NewsService()
        news_data = await news.get_market_news()
        
        text = "📰 Макроэкономические новости\n\n"
        
        for news_item in news_data:
            text += f"📌 {news_item['title']}\n"
            text += f"📊 Влияние: {news_item['impact']}\n"
            text += f"📝 {news_item['summary']}\n\n"
        
        builder = InlineKeyboardBuilder()
        builder.button(text="↩️ Назад", callback_data="menu_macro")
        
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error showing macro news: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка при получении новостей. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ Назад", callback_data="menu_macro")
            .as_markup()
        )

@router.callback_query(lambda c: c.data == "macro_calendar")
async def show_economic_calendar(callback: types.CallbackQuery):
    """Показывает экономический календарь."""
    try:
        macro = MacroData()
        calendar = await macro.get_economic_calendar()
        
        text = "📅 Экономический календарь\n\n"
        
        for event in calendar:
            text += f"🕒 {event['time']}\n"
            text += f"📊 {event['event']}\n"
            text += f"🌍 {event['country']}\n"
            text += f"⚡️ Важность: {event['importance']}\n"
            text += f"📈 Прогноз: {event['forecast']}\n"
            text += f"📊 Предыдущее: {event['previous']}\n\n"
        
        builder = InlineKeyboardBuilder()
        builder.button(text="↩️ Назад", callback_data="menu_macro")
        
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error showing economic calendar: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка при получении календаря. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ Назад", callback_data="menu_macro")
            .as_markup()
        ) 