import logging
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message
from database import get_session, PriceAlert, User

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("alerts"))
async def cmd_alerts(message: Message):
    """Показывает меню управления алертами."""
    builder = InlineKeyboardBuilder()
    
    # Добавляем кнопки для управления алертами
    builder.button(text="➕ Создать алерт", callback_data="alert_create")
    builder.button(text="📋 Мои алерты", callback_data="alert_list")
    builder.button(text="❌ Удалить алерт", callback_data="alert_delete")
    builder.button(text="↩️ Назад", callback_data="menu_main")
    
    # Выравниваем по 2 кнопки в ряд
    builder.adjust(2)
    
    await message.answer(
        "🔔 Управление ценовыми алертами\n\n"
        "Выберите действие:",
        reply_markup=builder.as_markup()
    )

@router.callback_query(lambda c: c.data == "alert_create")
async def create_alert(callback: types.CallbackQuery):
    """Создание нового алерта."""
    builder = InlineKeyboardBuilder()
    
    # Добавляем основные криптовалюты
    builder.button(text="Bitcoin (BTC)", callback_data="alert_coin_btc")
    builder.button(text="Ethereum (ETH)", callback_data="alert_coin_eth")
    builder.button(text="Solana (SOL)", callback_data="alert_coin_sol")
    builder.button(text="BNB", callback_data="alert_coin_bnb")
    builder.button(text="↩️ Назад", callback_data="menu_alerts")
    
    # Выравниваем по 2 кнопки в ряд
    builder.adjust(2)
    
    await callback.message.edit_text(
        "Выберите криптовалюту для алерта:",
        reply_markup=builder.as_markup()
    )

@router.callback_query(lambda c: c.data.startswith("alert_coin_"))
async def select_condition(callback: types.CallbackQuery):
    """Выбор условия для алерта."""
    coin = callback.data.split("_")[-1].upper()
    
    builder = InlineKeyboardBuilder()
    builder.button(text="Выше цены", callback_data=f"alert_condition_above_{coin}")
    builder.button(text="Ниже цены", callback_data=f"alert_condition_below_{coin}")
    builder.button(text="↩️ Назад", callback_data="alert_create")
    
    # Выравниваем по 2 кнопки в ряд
    builder.adjust(2)
    
    await callback.message.edit_text(
        f"Выберите условие для {coin}:",
        reply_markup=builder.as_markup()
    )

@router.callback_query(lambda c: c.data.startswith("alert_condition_"))
async def enter_price(callback: types.CallbackQuery):
    """Ввод цены для алерта."""
    parts = callback.data.split("_")
    condition = parts[2]
    coin = parts[3].upper()
    
    # Сохраняем временные данные
    user_data = {
        "coin": coin,
        "condition": condition
    }
    
    await callback.message.edit_text(
        f"Введите цену для {coin} (в USD):\n"
        f"Алерт сработает когда цена будет {'выше' if condition == 'above' else 'ниже'} указанного значения."
    )

@router.message(lambda message: message.text and message.text.replace(".", "").isdigit())
async def save_alert(message: Message):
    """Сохранение алерта."""
    try:
        price = float(message.text)
        session = get_session()
        
        try:
            user = session.query(User).filter(User.telegram_id == message.from_user.id).first()
            if not user:
                await message.reply("Ошибка: пользователь не найден.")
                return
                
            # Создаем новый алерт
            alert = PriceAlert(
                user_id=user.id,
                symbol="BTC",  # Здесь нужно сохранять выбранную монету
                condition="above",  # И выбранное условие
                price=price,
                is_active=True
            )
            
            session.add(alert)
            session.commit()
            
            await message.reply(
                f"✅ Алерт создан!\n\n"
                f"Монета: {alert.symbol}\n"
                f"Условие: {'выше' if alert.condition == 'above' else 'ниже'} ${alert.price:,.2f}"
            )
            
        finally:
            session.close()
            
    except ValueError:
        await message.reply("Ошибка: введите корректное число.")
    except Exception as e:
        logger.error(f"Error saving alert: {e}")
        await message.reply("Произошла ошибка при сохранении алерта.") 