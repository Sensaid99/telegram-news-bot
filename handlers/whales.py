import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.whale_watch import WhaleWatch
from services.macro_calendar import MacroCalendar
from services.blockchain_stats import BlockchainStats
from services.whale_tracker import WhaleTracker

logger = logging.getLogger(__name__)
router = Router()

whale_watcher = WhaleWatch()
macro_calendar = MacroCalendar()

def get_network_keyboard():
    """Возвращает клавиатуру выбора сети."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Bitcoin (BTC)", callback_data="whales_btc")
    builder.button(text="Ethereum (ETH)", callback_data="whales_eth")
    builder.button(text="Solana (SOL)", callback_data="whales_sol")
    builder.button(text="BNB Chain", callback_data="whales_bnb")
    builder.button(text="TRON (TRX)", callback_data="whales_trx")
    builder.button(text="TON", callback_data="whales_ton")
    builder.button(text="Ripple (XRP)", callback_data="whales_xrp")
    builder.button(text="SUI", callback_data="whales_sui")
    builder.button(text="USDT", callback_data="whales_usdt")
    builder.button(text="USDC", callback_data="whales_usdc")
    builder.button(text="↩️ В главное меню", callback_data="menu_main")
    builder.adjust(2)
    return builder.as_markup()

def get_whale_menu_keyboard(network: str):
    """Возвращает клавиатуру меню китов для конкретной сети."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 Крупные транзакции", callback_data=f"whale_tx_{network}")
    builder.button(text="📊 Анализ движений", callback_data=f"whale_analysis_{network}")
    builder.button(text="🔄 Корреляции", callback_data=f"whale_correlation_{network}")
    builder.button(text="⚡️ Отслеживать", callback_data=f"whale_track_{network}")
    builder.button(text="↩️ Назад к сетям", callback_data="menu_whales")
    builder.adjust(2)
    return builder.as_markup()

@router.message(Command("whales"))
async def cmd_whales(message: Message):
    """Показывает меню отслеживания китов."""
    await message.answer(
        "🐋 Отслеживание крупных игроков\n\n"
        "Выберите сеть или тип анализа:",
        reply_markup=get_network_keyboard()
    )

@router.callback_query(lambda c: c.data == "menu_whales")
async def show_whales_menu(callback: types.CallbackQuery):
    """Показывает меню отслеживания китов."""
    try:
        builder = InlineKeyboardBuilder()
        builder.button(text="Bitcoin", callback_data="whales_btc")
        builder.button(text="Ethereum", callback_data="whales_eth")
        builder.button(text="BNB Chain", callback_data="whales_bnb")
        builder.button(text="Solana", callback_data="whales_sol")
        builder.button(text="TRON", callback_data="whales_trx")
        builder.button(text="↩️ В главное меню", callback_data="menu_main")
        builder.adjust(2, 2, 2)
        
        await callback.message.edit_text(
            "🐋 Отслеживание китов\n\n"
            "Выберите сеть для мониторинга:",
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error in whales menu: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ В главное меню", callback_data="menu_main")
            .as_markup()
        )

@router.callback_query(lambda c: c.data.startswith("whales_"))
async def show_whale_activity(callback: types.CallbackQuery):
    """Показывает активность китов в выбранной сети."""
    try:
        network = callback.data.split("_")[1].upper()
        await callback.answer(f"Получаю данные {network}...")
        
        tracker = WhaleTracker()
        data = await tracker.get_whale_activity(network)
        
        text = f"🐋 Активность китов | {network}\n\n"
        
        # Крупные транзакции
        text += "💰 Крупные транзакции (24ч):\n"
        for tx in data['transactions'][:5]:  # Топ-5 транзакций
            text += (
                f"• ${tx['amount']:,.0f} | "
                f"{tx['from'][:8]}...{tx['from'][-8:]} ➜ "
                f"{tx['to'][:8]}...{tx['to'][-8:]}\n"
                f"  {tx['time']} | {tx['type']}\n\n"
            )
        
        # Активность бирж
        text += "📊 Активность бирж:\n"
        text += f"• Приток: ${data['exchange_flow']['inflow']:,.0f}\n"
        text += f"• Отток: ${data['exchange_flow']['outflow']:,.0f}\n"
        text += f"• Нетто: ${data['exchange_flow']['net']:,.0f}\n\n"
        
        # Топ китов
        text += "🔝 Топ китов:\n"
        for whale in data['top_whales'][:3]:  # Топ-3 кита
            text += (
                f"• {whale['address'][:8]}...{whale['address'][-8:]}\n"
                f"  Баланс: ${whale['balance']:,.0f}\n"
                f"  Изменение (24ч): {whale['change_24h']:+.1f}%\n\n"
            )
        
        # Метрики
        text += "📈 Метрики:\n"
        text += f"• Средний размер транзакции: ${data['metrics']['avg_tx_size']:,.0f}\n"
        text += f"• Активные киты: {data['metrics']['active_whales']}\n"
        text += f"• Концентрация: {data['metrics']['concentration']}%\n"
        
        # Кнопки фильтров
        builder = InlineKeyboardBuilder()
        builder.button(text="🔄 Обновить", callback_data=f"whales_{network.lower()}")
        builder.button(text="📊 Графики", callback_data=f"whales_chart_{network.lower()}")
        builder.button(text="⚡️ Уведомления", callback_data=f"whales_alert_{network.lower()}")
        builder.button(text="↩️ Назад", callback_data="menu_whales")
        builder.adjust(2, 2)
        
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error showing whale activity: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка при получении данных. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ Назад", callback_data="menu_whales")
            .as_markup()
        )

@router.callback_query(lambda c: c.data.startswith("whales_alert_"))
async def setup_whale_alerts(callback: types.CallbackQuery):
    """Настройка уведомлений о крупных транзакциях."""
    try:
        network = callback.data.split("_")[2].upper()
        
        builder = InlineKeyboardBuilder()
        builder.button(text="💰 Сумма транзакции", callback_data=f"whale_alert_amount_{network.lower()}")
        builder.button(text="📊 Объем сети", callback_data=f"whale_alert_volume_{network.lower()}")
        builder.button(text="🏦 Активность бирж", callback_data=f"whale_alert_exchange_{network.lower()}")
        builder.button(text="👥 Конкретный адрес", callback_data=f"whale_alert_address_{network.lower()}")
        builder.button(text="↩️ Назад", callback_data=f"whales_{network.lower()}")
        builder.adjust(2, 2, 1)
        
        await callback.message.edit_text(
            f"⚡️ Настройка уведомлений | {network}\n\n"
            "Выберите тип уведомления:",
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error setting up whale alerts: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка при настройке уведомлений. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ Назад", callback_data=f"whales_{network.lower()}")
            .as_markup()
        )

@router.message(F.text.contains(":"))
async def handle_address_tracking(message: Message):
    """Обрабатывает запросы на отслеживание адресов."""
    try:
        network, address = message.text.split(":")
        network = network.strip().upper()
        address = address.strip()
        
        if network not in ["BTC", "ETH", "BNB", "SOL", "TRX", "SUI", "TON", "XRP"]:
            await message.answer(
                "❌ Неподдерживаемая сеть. Используйте одну из: BTC, ETH, BNB, SOL, TRX, SUI, TON, XRP",
                reply_markup=get_network_keyboard()
            )
            return
        
        # Получаем данные по адресу
        data = await whale_watcher.track_address(address, network)
        if not data:
            await message.answer(
                "❌ Не удалось получить данные по адресу",
                reply_markup=get_network_keyboard()
            )
            return
        
        # Формируем отчет
        report = f"📊 Анализ адреса в сети {network}:\n"
        report += f"Адрес: `{address}`\n\n"
        report += f"💸 Всего отправлено: {data['total_sent']:.2f}\n"
        report += f"📥 Всего получено: {data['total_received']:.2f}\n\n"
        
        # Последние транзакции
        report += "📝 Последние транзакции:\n"
        for tx in data['transactions'][:5]:  # Показываем только 5 последних
            report += f"{'⬆️' if tx['type'] == 'out' else '⬇️'} "
            report += f"{tx['amount']:.4f} {network}\n"
            report += f"🕒 {tx['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        await message.answer(
            report,
            reply_markup=get_network_keyboard()
        )
        
    except ValueError:
        await message.answer(
            "❌ Неверный формат. Используйте: СЕТЬ:АДРЕС",
            reply_markup=get_network_keyboard()
        )
    except Exception as e:
        logger.error(f"Error tracking address: {e}")
        await message.answer(
            "❌ Произошла ошибка при отслеживании адреса",
            reply_markup=get_network_keyboard()
        ) 