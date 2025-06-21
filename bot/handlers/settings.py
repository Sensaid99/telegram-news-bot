from aiogram import Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.user_settings import UserSettings
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(lambda c: c.data == "menu_settings")
async def show_settings_menu(callback: types.CallbackQuery):
    """Показывает меню настроек."""
    try:
        settings = UserSettings()
        user_settings = await settings.get_user_settings(callback.from_user.id)
        
        text = "⚙️ Настройки\n\n"
        
        # Уведомления
        text += "🔔 Уведомления:\n"
        text += f"• Цена: {'✅' if user_settings['notifications']['price'] else '❌'}\n"
        text += f"• Объем: {'✅' if user_settings['notifications']['volume'] else '❌'}\n"
        text += f"• Новости: {'✅' if user_settings['notifications']['news'] else '❌'}\n"
        text += f"• Киты: {'✅' if user_settings['notifications']['whales'] else '❌'}\n\n"
        
        # Отображение
        text += "📱 Отображение:\n"
        text += f"• Валюта: {user_settings['display']['currency']}\n"
        text += f"• Таймзона: {user_settings['display']['timezone']}\n"
        text += f"• Формат времени: {user_settings['display']['time_format']}\n\n"
        
        # Фильтры
        text += "🔍 Фильтры:\n"
        text += f"• Мин. объем: ${user_settings['filters']['min_volume']:,.0f}\n"
        text += f"• Мин. изменение: {user_settings['filters']['min_change']}%\n"
        text += f"• Мин. сумма кита: ${user_settings['filters']['min_whale']:,.0f}\n"
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🔔 Уведомления", callback_data="settings_notifications")
        builder.button(text="📱 Отображение", callback_data="settings_display")
        builder.button(text="🔍 Фильтры", callback_data="settings_filters")
        builder.button(text="↩️ В главное меню", callback_data="menu_main")
        builder.adjust(2, 2)
        
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error in settings menu: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка при загрузке настроек. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ В главное меню", callback_data="menu_main")
            .as_markup()
        )

@router.callback_query(lambda c: c.data == "settings_notifications")
async def show_notifications_settings(callback: types.CallbackQuery):
    """Показывает настройки уведомлений."""
    try:
        settings = UserSettings()
        notifications = await settings.get_notifications_settings(callback.from_user.id)
        
        text = "🔔 Настройки уведомлений\n\n"
        
        # Цена
        text += "💰 Уведомления о цене:\n"
        text += f"• Активно: {'✅' if notifications['price']['enabled'] else '❌'}\n"
        text += f"• Изменение: {notifications['price']['change']}%\n"
        text += f"• Интервал: {notifications['price']['interval']} мин\n\n"
        
        # Объем
        text += "📊 Уведомления об объеме:\n"
        text += f"• Активно: {'✅' if notifications['volume']['enabled'] else '❌'}\n"
        text += f"• Мин. объем: ${notifications['volume']['min']:,.0f}\n"
        text += f"• Изменение: {notifications['volume']['change']}%\n\n"
        
        # Новости
        text += "📰 Уведомления о новостях:\n"
        text += f"• Активно: {'✅' if notifications['news']['enabled'] else '❌'}\n"
        text += f"• Важность: {notifications['news']['importance']}\n"
        text += f"• Категории: {', '.join(notifications['news']['categories'])}\n\n"
        
        # Киты
        text += "🐋 Уведомления о китах:\n"
        text += f"• Активно: {'✅' if notifications['whales']['enabled'] else '❌'}\n"
        text += f"• Мин. сумма: ${notifications['whales']['min']:,.0f}\n"
        text += f"• Сети: {', '.join(notifications['whales']['networks'])}"
        
        builder = InlineKeyboardBuilder()
        builder.button(text="💰 Цена", callback_data="notif_price")
        builder.button(text="📊 Объем", callback_data="notif_volume")
        builder.button(text="📰 Новости", callback_data="notif_news")
        builder.button(text="🐋 Киты", callback_data="notif_whales")
        builder.button(text="↩️ Назад", callback_data="menu_settings")
        builder.adjust(2, 2, 1)
        
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error in notifications settings: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка при загрузке настроек уведомлений. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ Назад", callback_data="menu_settings")
            .as_markup()
        )

@router.callback_query(lambda c: c.data == "settings_display")
async def show_display_settings(callback: types.CallbackQuery):
    """Показывает настройки отображения."""
    try:
        settings = UserSettings()
        display = await settings.get_display_settings(callback.from_user.id)
        
        text = "📱 Настройки отображения\n\n"
        
        # Валюта
        text += "💵 Валюта:\n"
        text += f"• Основная: {display['currency']['main']}\n"
        text += f"• Дополнительная: {display['currency']['secondary']}\n\n"
        
        # Время
        text += "🕒 Время:\n"
        text += f"• Таймзона: {display['time']['timezone']}\n"
        text += f"• Формат: {display['time']['format']}\n\n"
        
        # Формат чисел
        text += "🔢 Формат чисел:\n"
        text += f"• Разделитель: {display['numbers']['separator']}\n"
        text += f"• Десятичные: {display['numbers']['decimals']}\n\n"
        
        # Тема
        text += "🎨 Тема:\n"
        text += f"• Режим: {display['theme']['mode']}\n"
        text += f"• Эмодзи: {'✅' if display['theme']['emoji'] else '❌'}"
        
        builder = InlineKeyboardBuilder()
        builder.button(text="💵 Валюта", callback_data="display_currency")
        builder.button(text="🕒 Время", callback_data="display_time")
        builder.button(text="🔢 Числа", callback_data="display_numbers")
        builder.button(text="🎨 Тема", callback_data="display_theme")
        builder.button(text="↩️ Назад", callback_data="menu_settings")
        builder.adjust(2, 2, 1)
        
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error in display settings: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка при загрузке настроек отображения. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ Назад", callback_data="menu_settings")
            .as_markup()
        )

@router.callback_query(lambda c: c.data == "settings_filters")
async def show_filter_settings(callback: types.CallbackQuery):
    """Показывает настройки фильтров."""
    try:
        settings = UserSettings()
        filters = await settings.get_filter_settings(callback.from_user.id)
        
        text = "🔍 Настройки фильтров\n\n"
        
        # Объем
        text += "💎 Фильтры объема:\n"
        text += f"• Мин. объем: ${filters['volume']['min']:,.0f}\n"
        text += f"• Мин. изменение: {filters['volume']['change']}%\n\n"
        
        # Цена
        text += "💰 Фильтры цены:\n"
        text += f"• Мин. изменение: {filters['price']['change']}%\n"
        text += f"• Волатильность: {filters['price']['volatility']}\n\n"
        
        # Киты
        text += "🐋 Фильтры китов:\n"
        text += f"• Мин. сумма: ${filters['whales']['min']:,.0f}\n"
        text += f"• Тип транзакций: {filters['whales']['types']}\n\n"
        
        # Новости
        text += "📰 Фильтры новостей:\n"
        text += f"• Важность: {filters['news']['importance']}\n"
        text += f"• Категории: {', '.join(filters['news']['categories'])}"
        
        builder = InlineKeyboardBuilder()
        builder.button(text="💎 Объем", callback_data="filter_volume")
        builder.button(text="💰 Цена", callback_data="filter_price")
        builder.button(text="🐋 Киты", callback_data="filter_whales")
        builder.button(text="📰 Новости", callback_data="filter_news")
        builder.button(text="↩️ Назад", callback_data="menu_settings")
        builder.adjust(2, 2, 1)
        
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error in filter settings: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка при загрузке настроек фильтров. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ Назад", callback_data="menu_settings")
            .as_markup()
        ) 