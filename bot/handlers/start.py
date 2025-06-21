import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from database import get_session, User

# Настройка логирования
logger = logging.getLogger(__name__)

router = Router()

def get_main_menu() -> types.InlineKeyboardMarkup:
    """Создает главное меню бота."""
    builder = InlineKeyboardBuilder()
    
    # Первый ряд - Основные разделы
    builder.button(text="📊 Рыночный анализ", callback_data="menu_market")
    builder.button(text="⚡️ Криптовалюты", callback_data="menu_crypto")
    
    # Второй ряд - Макро и Технический анализ
    builder.button(text="🌍 Макроэкономика", callback_data="menu_macro")
    builder.button(text="📈 Технический анализ", callback_data="menu_technical")
    
    # Третий ряд - Новые разделы
    builder.button(text="🐋 Киты", callback_data="menu_whales")
    builder.button(text="📅 Экономический календарь", callback_data="menu_calendar")
    
    # Четвертый ряд - Настройки и помощь
    builder.button(text="⚙️ Настройки", callback_data="menu_settings")
    builder.button(text="ℹ️ Помощь", callback_data="menu_help")
    
    # Выравнивание кнопок
    builder.adjust(2, 2, 2, 2)
    return builder.as_markup()

def get_market_menu() -> InlineKeyboardBuilder:
    """Создает меню рыночного анализа."""
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Дневной отчет", callback_data="market_daily")
    builder.button(text="💰 Объемы торгов", callback_data="market_volume")
    builder.button(text="🔄 Тренды", callback_data="market_trends")
    builder.button(text="↩️ Назад", callback_data="menu_main")
    builder.adjust(2)
    return builder

def get_whale_menu() -> InlineKeyboardBuilder:
    """Создает меню отслеживания китов."""
    builder = InlineKeyboardBuilder()
    builder.button(text="₿ Bitcoin", callback_data="whale_btc")
    builder.button(text="Ξ Ethereum", callback_data="whale_eth")
    builder.button(text="⚡️ Solana", callback_data="whale_sol")
    builder.button(text="🟡 BNB", callback_data="whale_bnb")
    builder.button(text="🔍 Другие сети", callback_data="whale_other")
    builder.button(text="↩️ Назад", callback_data="menu_main")
    builder.adjust(2)
    return builder

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обрабатывает команду /start."""
    try:
        # Логируем получение команды
        logger.info(f"Received /start command from user {message.from_user.id}")
        
        # Получаем или создаем пользователя
        session = get_session()
        user = session.query(User).filter(User.telegram_id == message.from_user.id).first()
        
        if user:
            logger.info(f"Existing user returned: {message.from_user.id}")
        else:
            # Создаем нового пользователя
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )
            session.add(user)
            session.commit()
            logger.info(f"New user registered: {message.from_user.id}")
        
        # Отправляем приветственное сообщение
        logger.info(f"Sending welcome message to user {message.from_user.id}")
        await message.answer(
            f"👋 Привет, {message.from_user.first_name}!\n\n"
            "Я - QuantNews Bot, ваш помощник в анализе криптовалютного рынка.\n\n"
            "🔥 Что нового:\n"
            "• 🐋 Отслеживание крупных игроков\n"
            "• 📅 Экономический календарь\n"
            "• 📊 Расширенная аналитика\n\n"
            "Выберите интересующий раздел:",
            reply_markup=get_main_menu()
        )
        
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await message.answer(
            "❌ Произошла ошибка при запуске бота. Попробуйте позже или обратитесь в поддержку."
        )

@router.callback_query(F.data.startswith("menu_"))
async def handle_menu(callback: types.CallbackQuery):
    """Обрабатывает нажатия кнопок главного меню."""
    section = callback.data.split("_")[1]
    
    try:
        if section == "whales":
            # Переходим в раздел отслеживания китов
            await callback.message.edit_text(
                "🐋 Отслеживание крупных игроков\n\n"
                "Выберите сеть или тип анализа:",
                reply_markup=get_whale_menu().as_markup()
            )
            
        elif section == "calendar":
            # Получаем данные календаря
            calendar = await macro_calendar.get_daily_summary()
            await callback.message.edit_text(
                calendar,
                reply_markup=get_main_menu()
            )
            
        elif section == "market":
            # Остальные разделы остаются без изменений
            await callback.message.edit_text(
                "📊 Рыночный анализ\n\n"
                "Выберите тип анализа:",
                reply_markup=get_market_menu().as_markup()
            )
            
        # ... остальные обработчики меню ...
        
    except Exception as e:
        logger.error(f"Error in menu handler: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при обработке запроса",
            reply_markup=get_main_menu()
        )

# Обработчики для подменю рыночного анализа
@router.callback_query(lambda c: c.data == "menu_market")
async def market_menu(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Дневной отчет", callback_data="market_daily")
    builder.button(text="💰 Объемы торгов", callback_data="market_volume")
    builder.button(text="🔄 Тренды", callback_data="market_trends")
    builder.button(text="↩️ Назад", callback_data="menu_main")
    builder.adjust(2)
    
    await callback.message.edit_text(
        "📊 Рыночный анализ\n\nВыберите тип отчета:",
        reply_markup=builder.as_markup()
    )

# Обработчики для подменю криптовалют
@router.callback_query(lambda c: c.data == "menu_crypto")
async def crypto_menu(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="₿ Bitcoin", callback_data="crypto_btc")
    builder.button(text="Ξ Ethereum", callback_data="crypto_eth")
    builder.button(text="⚡️ Solana", callback_data="crypto_sol")
    builder.button(text="🟡 BNB", callback_data="crypto_bnb")
    builder.button(text="🔍 Другие", callback_data="crypto_other")
    builder.button(text="↩️ Назад", callback_data="menu_main")
    builder.adjust(2)
    
    await callback.message.edit_text(
        "⚡️ Криптовалюты\n\nВыберите актив для анализа:",
        reply_markup=builder.as_markup()
    )

# Обработчики для подменю макроэкономики
@router.callback_query(lambda c: c.data == "menu_macro")
async def macro_menu(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="💵 DXY", callback_data="macro_dxy")
    builder.button(text="📈 S&P 500", callback_data="macro_sp500")
    builder.button(text="📉 VIX", callback_data="macro_vix")
    builder.button(text="🔸 Gold", callback_data="macro_gold")
    builder.button(text="↩️ Назад", callback_data="menu_main")
    builder.adjust(2)
    
    await callback.message.edit_text(
        "🌍 Макроэкономика\n\nВыберите индикатор:",
        reply_markup=builder.as_markup()
    )

# Обработчик возврата в главное меню
@router.callback_query(lambda c: c.data == "menu_main")
async def return_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Выберите интересующий вас раздел:",
        reply_markup=get_main_menu()
    )

def get_start_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Сегодняшняя сводка")],
            [KeyboardButton(text="⚡️ Настроить алерты")],
            [KeyboardButton(text="💎 Премиум подписка")],
            [KeyboardButton(text="❓ Помощь")]
        ],
        resize_keyboard=True
    )
    return keyboard 