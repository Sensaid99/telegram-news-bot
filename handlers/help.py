from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from database import get_session, User
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("help"))
async def help_command(message: Message):
    """Обработчик команды /help."""
    help_text = """
📚 Справка по командам:

/today - Получить текущую сводку рынка
• Цены основных криптовалют
• On-chain метрики
• Настроение рынка
• Топ движения за 24ч

/alerts - Управление ценовыми алертами
• Создание новых алертов
• Просмотр активных алертов
• Удаление алертов

/test_report - Тестовый отчет (только для админов)
• Проверка форматирования
• Тест новых метрик

🔔 Канал: @Ev_Hor
По вопросам и предложениям: @admin

💡 Совет: Используйте команду /today для быстрого получения актуальной информации о рынке.
"""
    await message.reply(help_text)

@router.message(Command("today"))
async def cmd_today(message: Message):
    # Get user's subscription status
    session = get_session()
    user = session.query(User).filter(User.telegram_id == message.from_user.id).first()
    is_premium = user and user.is_premium
    
    help_text = """
📚 Команды бота:

/start - Начать работу с ботом
/today - Получить сводку за сегодня
/alerts - Настроить ценовые уведомления
/help - Это сообщение

⚡️ Возможности:
• Ежедневные сводки рынка (утро/вечер)
• Уведомления о движении цен
• On-chain метрики
• Анализ активности крупных игроков

"""
    
    if is_premium:
        help_text += """
💎 Ваш премиум статус активен:
• Увеличенный лимит алертов (10)
• Приоритетные уведомления
• Доступ к закрытому чату
"""
    else:
        help_text += """
💎 Преимущества премиум:
• Больше алертов (до 10)
• Приоритетные уведомления
• Закрытый чат

Используйте /subscribe для подключения премиум.
"""
    
    await message.answer(help_text)

@router.callback_query(lambda c: c.data == "menu_help")
async def show_help_menu(callback: types.CallbackQuery):
    """Показывает меню помощи."""
    try:
        builder = InlineKeyboardBuilder()
        builder.button(text="📚 Руководство", callback_data="help_guide")
        builder.button(text="❓ FAQ", callback_data="help_faq")
        builder.button(text="🔧 Команды", callback_data="help_commands")
        builder.button(text="📱 Функции", callback_data="help_features")
        builder.button(text="↩️ В главное меню", callback_data="menu_main")
        builder.adjust(2, 2, 1)
        
        await callback.message.edit_text(
            "ℹ️ Помощь и поддержка\n\n"
            "Выберите раздел помощи:",
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error in help menu: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ В главное меню", callback_data="menu_main")
            .as_markup()
        )

@router.callback_query(lambda c: c.data == "help_guide")
async def show_guide(callback: types.CallbackQuery):
    """Показывает руководство пользователя."""
    try:
        text = (
            "📚 Руководство пользователя\n\n"
            "🔹 Начало работы:\n"
            "1. Выберите интересующий раздел в главном меню\n"
            "2. Настройте уведомления в разделе Настройки\n"
            "3. Добавьте избранные монеты для быстрого доступа\n\n"
            
            "🔹 Основные разделы:\n"
            "• Криптовалюты - информация о монетах\n"
            "• Рыночный анализ - обзор рынка\n"
            "• Макроэкономика - влияние новостей\n"
            "• Технический анализ - графики и индикаторы\n"
            "• Киты - крупные транзакции\n\n"
            
            "🔹 Дополнительные функции:\n"
            "• Уведомления о движении цены\n"
            "• Отслеживание объемов торгов\n"
            "• Мониторинг китов\n"
            "• Важные новости\n\n"
            
            "🔹 Настройка бота:\n"
            "• Выберите предпочитаемую валюту\n"
            "• Установите часовой пояс\n"
            "• Настройте фильтры уведомлений\n"
            "• Выберите формат отображения"
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="↩️ Назад", callback_data="menu_help")
        
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error showing guide: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка при загрузке руководства. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ Назад", callback_data="menu_help")
            .as_markup()
        )

@router.callback_query(lambda c: c.data == "help_faq")
async def show_faq(callback: types.CallbackQuery):
    """Показывает часто задаваемые вопросы."""
    try:
        text = (
            "❓ Часто задаваемые вопросы\n\n"
            
            "В: Как настроить уведомления?\n"
            "О: Перейдите в Настройки → Уведомления и выберите нужные параметры.\n\n"
            
            "В: Как добавить монету в избранное?\n"
            "О: Нажмите на звездочку рядом с монетой в разделе Криптовалюты.\n\n"
            
            "В: Как изменить валюту отображения?\n"
            "О: Перейдите в Настройки → Отображение → Валюта.\n\n"
            
            "В: Как работает отслеживание китов?\n"
            "О: Бот отслеживает крупные транзакции выше установленного порога.\n\n"
            
            "В: Как часто обновляются данные?\n"
            "О: Рыночные данные - каждую минуту, on-chain метрики - каждые 5 минут.\n\n"
            
            "В: Как настроить фильтры для уведомлений?\n"
            "О: Перейдите в Настройки → Фильтры и установите пороговые значения.\n\n"
            
            "В: Откуда берутся данные?\n"
            "О: Используются API ведущих бирж и блокчейн-эксплореров."
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="↩️ Назад", callback_data="menu_help")
        
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error showing FAQ: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка при загрузке FAQ. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ Назад", callback_data="menu_help")
            .as_markup()
        )

@router.callback_query(lambda c: c.data == "help_commands")
async def show_commands(callback: types.CallbackQuery):
    """Показывает список команд."""
    try:
        text = (
            "🔧 Команды бота\n\n"
            
            "Основные команды:\n"
            "/start - Запуск бота\n"
            "/help - Помощь\n"
            "/settings - Настройки\n\n"
            
            "Криптовалюты:\n"
            "/p <символ> - Цена монеты\n"
            "/v <символ> - Объем торгов\n"
            "/c <символ> - График\n"
            "/i <символ> - Информация\n\n"
            
            "Уведомления:\n"
            "/alert_price <символ> <цена> - Уведомление о цене\n"
            "/alert_volume <символ> <объем> - Уведомление об объеме\n"
            "/alert_whale <сеть> <сумма> - Уведомление о ките\n"
            "/alerts_list - Список уведомлений\n"
            "/alerts_clear - Очистить уведомления\n\n"
            
            "Анализ:\n"
            "/market - Рыночный анализ\n"
            "/macro - Макроэкономика\n"
            "/ta <символ> - Технический анализ\n"
            "/whales <сеть> - Активность китов\n\n"
            
            "Настройки:\n"
            "/currency <код> - Изменить валюту\n"
            "/timezone <зона> - Изменить часовой пояс\n"
            "/format <формат> - Формат времени\n"
            "/theme <тема> - Сменить тему"
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="↩️ Назад", callback_data="menu_help")
        
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error showing commands: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка при загрузке команд. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ Назад", callback_data="menu_help")
            .as_markup()
        )

@router.callback_query(lambda c: c.data == "help_features")
async def show_features(callback: types.CallbackQuery):
    """Показывает описание функций."""
    try:
        text = (
            "📱 Функции бота\n\n"
            
            "🔹 Криптовалюты:\n"
            "• Актуальные цены и объемы\n"
            "• On-chain метрики\n"
            "• Графики и индикаторы\n"
            "• Уведомления об изменениях\n\n"
            
            "🔹 Рыночный анализ:\n"
            "• Обзор состояния рынка\n"
            "• Тренды и корреляции\n"
            "• Объемы торгов\n"
            "• Рыночные настроения\n\n"
            
            "🔹 Макроэкономика:\n"
            "• Важные новости\n"
            "• Экономический календарь\n"
            "• Влияние на крипторынок\n"
            "• Индикаторы рынка\n\n"
            
            "🔹 Технический анализ:\n"
            "• Графики разных таймфреймов\n"
            "• Технические индикаторы\n"
            "• Уровни поддержки/сопротивления\n"
            "• Паттерны и сигналы\n\n"
            
            "🔹 Отслеживание китов:\n"
            "• Крупные транзакции\n"
            "• Активность бирж\n"
            "• Концентрация токенов\n"
            "• Уведомления о движениях\n\n"
            
            "🔹 Настройки:\n"
            "• Персонализация уведомлений\n"
            "• Выбор валюты и формата\n"
            "• Фильтры и пороги\n"
            "• Тема интерфейса"
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="↩️ Назад", callback_data="menu_help")
        
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error showing features: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка при загрузке функций. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ Назад", callback_data="menu_help")
            .as_markup()
        ) 