from aiogram import Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(lambda c: c.data == "menu_main")
async def show_main_menu(callback: types.CallbackQuery):
    """Показывает главное меню."""
    try:
        builder = InlineKeyboardBuilder()
        
        # Основные разделы
        builder.button(text="💰 Криптовалюты", callback_data="menu_crypto")
        builder.button(text="📊 Рыночный анализ", callback_data="menu_market")
        builder.button(text="🌍 Макроэкономика", callback_data="menu_macro")
        builder.button(text="📈 Технический анализ", callback_data="menu_technical")
        builder.button(text="🐋 Киты", callback_data="menu_whales")
        builder.button(text="📅 Экономический календарь", callback_data="menu_calendar")
        builder.button(text="⚙️ Настройки", callback_data="menu_settings")
        builder.button(text="❓ Помощь", callback_data="menu_help")
        
        # Выравниваем по 2 кнопки в ряд
        builder.adjust(2)
        
        await callback.message.edit_text(
            "🤖 Главное меню\n\n"
            "Выберите интересующий раздел:",
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error in main menu: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="🔄 Обновить", callback_data="menu_main")
            .as_markup()
        )

@router.callback_query(lambda c: c.data == "menu_crypto")
async def show_crypto_menu(callback: types.CallbackQuery):
    """Показывает меню криптовалют."""
    try:
        builder = InlineKeyboardBuilder()
        
        # Основные монеты
        builder.button(text="Bitcoin", callback_data="crypto_btc")
        builder.button(text="Ethereum", callback_data="crypto_eth")
        builder.button(text="BNB", callback_data="crypto_bnb")
        builder.button(text="Solana", callback_data="crypto_sol")
        builder.button(text="XRP", callback_data="crypto_xrp")
        builder.button(text="TRON", callback_data="crypto_trx")
        builder.button(text="TON", callback_data="crypto_ton")
        builder.button(text="SUI", callback_data="crypto_sui")
        builder.button(text="↩️ В главное меню", callback_data="menu_main")
        
        # Выравниваем по 2 кнопки в ряд
        builder.adjust(2)
        
        await callback.message.edit_text(
            "💰 Криптовалюты\n\n"
            "Выберите монету для анализа:",
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error in crypto menu: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ В главное меню", callback_data="menu_main")
            .as_markup()
        )

@router.callback_query(lambda c: c.data == "menu_calendar")
async def show_calendar_menu(callback: types.CallbackQuery):
    """Показывает экономический календарь."""
    try:
        builder = InlineKeyboardBuilder()
        
        # Фильтры календаря
        builder.button(text="🔥 Важные события", callback_data="calendar_important")
        builder.button(text="📊 Все события", callback_data="calendar_all")
        builder.button(text="📅 По дате", callback_data="calendar_date")
        builder.button(text="🌍 По региону", callback_data="calendar_region")
        builder.button(text="↩️ В главное меню", callback_data="menu_main")
        
        # Выравниваем по 2 кнопки в ряд
        builder.adjust(2)
        
        await callback.message.edit_text(
            "📅 Экономический календарь\n\n"
            "Выберите фильтр событий:",
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error in calendar menu: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ В главное меню", callback_data="menu_main")
            .as_markup()
        ) 