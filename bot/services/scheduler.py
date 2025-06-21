import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from ..config import UPDATE_INTERVAL, NOTIFICATION_DELAY, CALENDAR_UPDATE_INTERVAL

logger = logging.getLogger(__name__)

class TaskScheduler:
    """Планировщик задач."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._setup_jobs()
        
    def _setup_jobs(self):
        """Настраивает регулярные задачи."""
        try:
            # Обновление рыночных данных
            self.scheduler.add_job(
                self._update_market_data,
                IntervalTrigger(seconds=UPDATE_INTERVAL),
                id="market_data_update",
                replace_existing=True
            )
            
            # Проверка уведомлений
            self.scheduler.add_job(
                self._check_alerts,
                IntervalTrigger(seconds=NOTIFICATION_DELAY),
                id="alerts_check",
                replace_existing=True
            )
            
            # Обновление календаря
            self.scheduler.add_job(
                self._update_calendar,
                IntervalTrigger(seconds=CALENDAR_UPDATE_INTERVAL),
                id="calendar_update",
                replace_existing=True
            )
            
            # Ежедневный отчет (утро)
            self.scheduler.add_job(
                self._daily_morning_report,
                CronTrigger(hour=8, minute=0),
                id="morning_report",
                replace_existing=True
            )
            
            # Ежедневный отчет (вечер)
            self.scheduler.add_job(
                self._daily_evening_report,
                CronTrigger(hour=20, minute=0),
                id="evening_report",
                replace_existing=True
            )
            
            # Очистка кэша
            self.scheduler.add_job(
                self._cleanup_cache,
                IntervalTrigger(hours=1),
                id="cache_cleanup",
                replace_existing=True
            )
            
            logger.info("Scheduled jobs setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up jobs: {e}")
            
    async def _update_market_data(self):
        """Обновляет рыночные данные."""
        from services.market_data import MarketData
        try:
            market = MarketData()
            await market.update_all()
            logger.info("Market data updated")
            
        except Exception as e:
            logger.error(f"Error updating market data: {e}")
            
    async def _check_alerts(self):
        """Проверяет и отправляет уведомления."""
        from services.alerts import AlertService
        try:
            alerts = AlertService()
            await alerts.check_all()
            logger.debug("Alerts checked")
            
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
            
    async def _update_calendar(self):
        """Обновляет экономический календарь."""
        from services.macro_calendar import MacroCalendar
        try:
            calendar = MacroCalendar()
            await calendar.update_events()
            logger.info("Calendar updated")
            
        except Exception as e:
            logger.error(f"Error updating calendar: {e}")
            
    async def _daily_morning_report(self):
        """Формирует и отправляет утренний отчет."""
        from services.reports import ReportService
        try:
            reports = ReportService()
            await reports.send_morning_report()
            logger.info("Morning report sent")
            
        except Exception as e:
            logger.error(f"Error sending morning report: {e}")
            
    async def _daily_evening_report(self):
        """Формирует и отправляет вечерний отчет."""
        from services.reports import ReportService
        try:
            reports = ReportService()
            await reports.send_evening_report()
            logger.info("Evening report sent")
            
        except Exception as e:
            logger.error(f"Error sending evening report: {e}")
            
    async def _cleanup_cache(self):
        """Очищает устаревшие данные из кэша."""
        from services.cache import cache
        try:
            cleaned = cache.cleanup()
            logger.info(f"Cache cleanup completed: {cleaned} items removed")
            
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
            
    def start(self):
        """Запускает планировщик."""
        try:
            self.scheduler.start()
            logger.info("Scheduler started")
            
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
            
    def stop(self):
        """Останавливает планировщик."""
        try:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
            
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
            
    def add_job(self, func, trigger, **kwargs):
        """Добавляет новую задачу."""
        try:
            self.scheduler.add_job(func, trigger, **kwargs)
            logger.info(f"Added new job: {kwargs.get('id', 'unnamed')}")
            
        except Exception as e:
            logger.error(f"Error adding job: {e}")
            
    def remove_job(self, job_id):
        """Удаляет задачу."""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed job: {job_id}")
            
        except Exception as e:
            logger.error(f"Error removing job: {e}")
            
    def get_jobs(self):
        """Возвращает список активных задач."""
        try:
            jobs = []
            for job in self.scheduler.get_jobs():
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time,
                    "trigger": str(job.trigger)
                })
            return jobs
            
        except Exception as e:
            logger.error(f"Error getting jobs: {e}")
            return []
            
# Создаем глобальный экземпляр планировщика
scheduler = TaskScheduler() 