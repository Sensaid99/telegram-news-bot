import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import ADMIN_IDS, CHANNEL_ID
from core import bot
from services.report_generator import generate_report

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("test_report"))
async def test_report_command(message: Message):
    """Обработчик команды /test_report для администраторов."""
    try:
        # Проверяем, является ли пользователь администратором
        if message.from_user.id not in ADMIN_IDS:
            logger.warning(f"Unauthorized access attempt from user {message.from_user.id}")
            await message.reply("⛔️ У вас нет доступа к этой команде.")
            return
            
        # Отправляем сообщение о начале генерации
        status_msg = await message.reply("⏳ Генерирую тестовый отчет...")
            
        logger.info(f"Generating test report for admin {message.from_user.id}")
        report = await generate_report()
        
        # Отправляем отчет в личку
        logger.info(f"Sending test report to admin {message.from_user.id}")
        await message.reply(report)
        
        # Отправляем отчет в канал
        try:
            logger.info(f"Sending test report to channel {CHANNEL_ID}")
            await bot.send_message(CHANNEL_ID, report)
            await message.reply(f"✅ Отчет успешно отправлен в канал {CHANNEL_ID}")
        except Exception as e:
            logger.error(f"Error sending report to channel: {e}")
            await message.reply(f"❌ Ошибка отправки в канал: {str(e)}")
        
        # Удаляем статусное сообщение
        await status_msg.delete()
        
    except Exception as e:
        logger.error(f"Error in test_report_command: {e}")
        await message.reply("Извините, произошла ошибка при генерации тестового отчета.") 