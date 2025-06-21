import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core import bot
from database import get_session, PriceAlert
from services.price_service import price_service
from sqlalchemy import select

logger = logging.getLogger(__name__)

# Глобальная переменная для хранения экземпляра планировщика
scheduler = AsyncIOScheduler()

def setup(bot_instance):
    """Инициализация планировщика с экземпляром бота."""
    global bot
    bot = bot_instance
    schedule_alerts_check(scheduler)

async def check_alerts():
    """Проверяет все активные алерты."""
    try:
        logger.info("Checking alerts...")
        session = get_session()
        try:
            # Получаем все активные алерты
            alerts = session.query(PriceAlert).filter(PriceAlert.is_active == True).all()
            
            for alert in alerts:
                try:
                    # Получаем текущую цену
                    current_price = await price_service.get_current_price(alert.symbol)
                    
                    if current_price is None:
                        logger.warning(f"Could not get price for {alert.symbol}")
                        continue
                    
                    # Проверяем условия
                    if alert.condition == "above" and current_price >= alert.price:
                        message = f"🔔 Цена {alert.symbol} поднялась выше {alert.price:.2f}! Текущая цена: {current_price:.2f}"
                        alert.is_active = False
                        
                    elif alert.condition == "below" and current_price <= alert.price:
                        message = f"🔔 Цена {alert.symbol} опустилась ниже {alert.price:.2f}! Текущая цена: {current_price:.2f}"
                        alert.is_active = False
                    
                    # Если алерт сработал
                    if not alert.is_active:
                        alert.triggered_at = datetime.utcnow()
                        session.commit()
                        
                        # Отправляем уведомление пользователю
                        await bot.send_message(
                            chat_id=alert.user.telegram_id,
                            text=message
                        )
                        logger.info(f"Alert triggered and notification sent: {message}")
                        
                except Exception as e:
                    logger.error(f"Error processing alert {alert.id}: {e}")
                    continue
                    
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error checking alerts: {e}")

def schedule_alerts_check(scheduler):
    """Планирует проверку алертов."""
    try:
        # Проверяем алерты каждые 5 минут
        scheduler.add_job(
            check_alerts,
            'interval',
            minutes=5,
            id='check_alerts'
        )
        logger.info("Alerts check scheduled")
        
    except Exception as e:
        logger.error(f"Error scheduling alerts check: {e}")

async def start_scheduler():
    """Запуск планировщика."""
    scheduler.start() 