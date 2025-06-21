import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from services.report_generator import generate_report

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("today"))
async def today_command(message: Message):
    """Обработчик команды /today."""
    try:
        logger.info(f"Generating report for user {message.from_user.id}")
        report = await generate_report()
        
        logger.info(f"Sending report to user {message.from_user.id}")
        await message.reply(report)
        
    except Exception as e:
        logger.error(f"Error in today_command: {e}")
        await message.reply("Извините, произошла ошибка при генерации отчета. Попробуйте позже.") 