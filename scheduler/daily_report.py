import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core import bot
from database import get_session, User
from services.report_generator import generate_report

logger = logging.getLogger(__name__)

# Глобальная переменная для хранения экземпляра планировщика
scheduler = AsyncIOScheduler()

def setup(bot_instance):
    """Инициализация планировщика с экземпляром бота."""
    global bot
    bot = bot_instance
    schedule_daily_reports(scheduler)

async def send_daily_report():
    """Отправка ежедневного отчета подписчикам."""
    try:
        logger.info("Generating daily report...")
        report = await generate_report()
        
        session = get_session()
        try:
            # Получаем всех активных подписчиков
            subscribers = session.query(User).filter(User.is_subscribed == True).all()
            
            if not subscribers:
                logger.info("No active subscribers found")
                return
                
            logger.info(f"Sending daily report to {len(subscribers)} subscribers")
            
            # Отправляем отчет каждому подписчику
            for user in subscribers:
                try:
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=report,
                        disable_web_page_preview=True
                    )
                    logger.info(f"Report sent to user {user.telegram_id}")
                    
                except Exception as e:
                    logger.error(f"Error sending report to user {user.telegram_id}: {e}")
                    continue
                    
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error sending daily report: {e}")

def schedule_daily_reports(scheduler):
    """Настройка расписания ежедневных отчетов."""
    try:
        logger.info("Setting up daily report scheduler...")
        
        # Отправляем отчет каждый день в 09:00 UTC
        scheduler.add_job(
            send_daily_report,
            'cron',
            hour=9,
            minute=0,
            id='daily_report'
        )
        
        logger.info("Daily report scheduled for 09:00 UTC")
        
    except Exception as e:
        logger.error(f"Error configuring daily report scheduler: {e}")
        raise

async def start_scheduler():
    """Запуск планировщика."""
    scheduler.start() 