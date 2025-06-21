import logging
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_session, User
from config import SUBSCRIPTION_PRICES

logger = logging.getLogger(__name__)

router = Router()

def get_subscription_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"Месяц - {SUBSCRIPTION_PRICES['monthly']} ₽",
                    callback_data="subscribe_monthly"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"3 месяца - {SUBSCRIPTION_PRICES['quarterly']} ₽",
                    callback_data="subscribe_quarterly"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"Год - {SUBSCRIPTION_PRICES['yearly']} ₽",
                    callback_data="subscribe_yearly"
                )
            ]
        ]
    )
    return keyboard

@router.message(Command("subscribe"))
async def subscribe_command(message: Message):
    """Обработчик команды /subscribe."""
    try:
        subscription_text = """
💎 Премиум подписка QuantNews

Получите доступ ко всем функциям бота:
• Неограниченное количество алертов
• Приоритетная поддержка
• Расширенная аналитика
• Эксклюзивные отчеты

Выберите период подписки:
"""
        await message.reply(
            subscription_text,
            reply_markup=get_subscription_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in subscribe_command: {e}")
        await message.reply("Извините, произошла ошибка. Попробуйте позже.")

@router.callback_query(F.data.startswith("subscribe_"))
async def process_subscription(callback: CallbackQuery):
    """Обработчик выбора периода подписки."""
    try:
        period = callback.data.split("_")[1]
        price = SUBSCRIPTION_PRICES.get(period)
        
        if not price:
            await callback.answer("Неверный период подписки")
            return
            
        payment_text = f"""
💳 Оплата подписки

Период: {period}
Стоимость: {price} ₽

Для оплаты переведите указанную сумму на счет:
XXXX XXXX XXXX XXXX

В комментарии укажите ваш Telegram ID: {callback.from_user.id}
"""
        await callback.message.edit_text(
            payment_text,
            reply_markup=None
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in process_subscription: {e}")
        await callback.answer("Произошла ошибка. Попробуйте позже.")

# Webhook handler for payment confirmation
async def process_payment_webhook(user_id: int, plan: str):
    session = get_session()
    user = session.query(User).filter(User.telegram_id == user_id).first()
    
    if user:
        duration = 365 if plan == "yearly" else 30
        user.is_premium = True
        user.subscription_end = datetime.utcnow() + timedelta(days=duration)
        session.commit()
        
        await bot.send_message(
            user_id,
            "🎉 Премиум подписка активирована!\n"
            f"Действует до: {user.subscription_end.strftime('%d.%m.%Y')}"
        ) 