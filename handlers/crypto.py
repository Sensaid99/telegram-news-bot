from aiogram import Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.market_data import MarketData
from services.blockchain_stats import BlockchainStats
import logging

logger = logging.getLogger(__name__)
router = Router()

def get_main_keyboard():
    """Возвращает основную клавиатуру."""
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Рыночный анализ", callback_data="menu_market")
    builder.button(text="💰 Криптовалюты", callback_data="menu_crypto")
    builder.button(text="📈 Макроэкономика", callback_data="menu_macro")
    builder.button(text="📊 Технический анализ", callback_data="menu_tech")
    builder.button(text="🐋 Киты", callback_data="menu_whales")
    builder.button(text="📅 Экономический календарь", callback_data="menu_calendar")
    builder.button(text="⚙️ Настройки", callback_data="menu_settings")
    builder.button(text="❓ Помощь", callback_data="menu_help")
    builder.adjust(2)
    return builder.as_markup()

def get_crypto_keyboard():
    """Возвращает клавиатуру выбора криптовалют."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Bitcoin (BTC)", callback_data="crypto_btc")
    builder.button(text="Ethereum (ETH)", callback_data="crypto_eth")
    builder.button(text="Solana (SOL)", callback_data="crypto_sol")
    builder.button(text="BNB Chain", callback_data="crypto_bnb")
    builder.button(text="TRON (TRX)", callback_data="crypto_trx")
    builder.button(text="TON", callback_data="crypto_ton")
    builder.button(text="Ripple (XRP)", callback_data="crypto_xrp")
    builder.button(text="SUI", callback_data="crypto_sui")
    builder.button(text="↩️ В главное меню", callback_data="menu_main")
    builder.adjust(2)
    return builder.as_markup()

@router.callback_query(lambda c: c.data.startswith("menu_"))
async def handle_menu(callback: types.CallbackQuery):
    """Обработчик меню."""
    menu_type = callback.data.split("_")[1]
    
    try:
        if menu_type == "main":
            await callback.message.edit_text(
                "🤖 Главное меню",
                reply_markup=get_main_keyboard()
            )
        elif menu_type == "crypto":
            await callback.message.edit_text(
                "💰 Выберите криптовалюту:",
                reply_markup=get_crypto_keyboard()
            )
        elif menu_type == "market":
            market = MarketData()
            volume_data = await market.get_market_volume()
            trends = await market.get_trending_coins()
            
            text = "📊 Рыночный анализ\n\n"
            text += "💎 Объемы торгов (24ч):\n"
            for symbol, data in volume_data.items():
                text += (
                    f"• {symbol}: ${data['volume']:,.0f}\n"
                    f"  Изменение объема: {data['volume_change']:+.1f}%\n"
                    f"  Изменение цены: {data['price_change']:+.1f}%\n"
                )
            
            text += f"\n{trends}"
            
            builder = InlineKeyboardBuilder()
            builder.button(text="↩️ В главное меню", callback_data="menu_main")
            
            await callback.message.edit_text(
                text,
                reply_markup=builder.as_markup()
            )
        else:
            # Заглушки для остальных разделов
            messages = {
                "macro": "📈 Раздел макроэкономики находится в разработке",
                "tech": "📊 Раздел технического анализа находится в разработке",
                "whales": "🐋 Раздел анализа китов находится в разработке",
                "calendar": "📅 Экономический календарь находится в разработке",
                "settings": "⚙️ Настройки находятся в разработке",
                "help": "❓ Раздел помощи находится в разработке"
            }
            
            builder = InlineKeyboardBuilder()
            builder.button(text="↩️ В главное меню", callback_data="menu_main")
            
            await callback.message.edit_text(
                messages.get(menu_type, "⚠️ Раздел находится в разработке"),
                reply_markup=builder.as_markup()
            )
            
    except Exception as e:
        logger.error(f"Error in menu handler: {e}")
        await callback.message.edit_text(
            "⚠️ Произошла ошибка. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ В главное меню", callback_data="menu_main")
            .as_markup()
        )

async def get_crypto_info(symbol: str) -> str:
    """Получает информацию о криптовалюте."""
    try:
        market = MarketData()
        blockchain = BlockchainStats()
        
        if symbol == "BTC":
            data = await market.get_bitcoin_data()
            metrics = await blockchain.get_bitcoin_metrics()
            
            return (
                f"₿ Bitcoin (BTC)\n\n"
                f"💰 Цена: ${data['price']:,.2f}\n"
                f"📈 Изменение (24ч): {data['change_24h']:+.1f}%\n"
                f"💎 Объем: ${data['volume_24h']:,.0f}\n\n"
                f"⛓ On-chain метрики:\n"
                f"• Активные адреса: {metrics['active_addresses']:,}\n"
                f"• Транзакции (24ч): {metrics['transactions']:,}\n"
                f"• Комиссия: {metrics['fee']} sat/vB (${metrics['fee_usd']:.2f})\n"
                f"• Среднее время транзакции: {metrics['avg_time']} мин\n"
                f"• Хешрейт: {metrics.get('hashrate', 'N/A')} EH/s\n"
            )
            
        elif symbol == "ETH":
            data = await market.get_ethereum_data()
            metrics = await blockchain.get_ethereum_metrics()
            
            return (
                f"Ξ Ethereum (ETH)\n\n"
                f"💰 Цена: ${data['price']:,.2f}\n"
                f"📈 Изменение (24ч): {data['change_24h']:+.1f}%\n"
                f"💎 Объем: ${data['volume_24h']:,.0f}\n\n"
                f"⛓ On-chain метрики:\n"
                f"• Gas: {metrics['gas']} gwei (${metrics['gas_usd']:.2f})\n"
                f"• TVL: ${metrics['tvl']:,.0f}\n"
                f"• Активные адреса: {metrics.get('active_addresses', 'N/A'):,}\n"
                f"• Валидаторы: {metrics.get('validators', 'N/A')}\n"
                f"• TPS: {metrics.get('tps', 'N/A')}\n"
                f"• Среднее время транзакции: {metrics['avg_time']} сек\n"
            )
            
        elif symbol == "SOL":
            data = await market.get_solana_data()
            metrics = await blockchain.get_solana_metrics()
            
            return (
                f"⚡️ Solana (SOL)\n\n"
                f"💰 Цена: ${data['price']:,.2f}\n"
                f"📈 Изменение (24ч): {data['change_24h']:+.1f}%\n"
                f"💎 Объем: ${data['volume_24h']:,.0f}\n\n"
                f"⛓ On-chain метрики:\n"
                f"• TPS: {metrics['tps']}\n"
                f"• TVL: ${metrics['tvl']:,.0f}\n"
                f"• Комиссия: {metrics['fee']} SOL (${metrics['fee_usd']:.4f})\n"
                f"• Валидаторы: {metrics.get('validators', 'N/A')}\n"
                f"• Среднее время транзакции: {metrics['avg_time']} сек\n"
            )
            
        elif symbol == "BNB":
            data = await market.get_bnb_data()
            metrics = await blockchain.get_bnb_metrics()
            
            return (
                f"🟡 BNB Chain (BNB)\n\n"
                f"💰 Цена: ${data['price']:,.2f}\n"
                f"📈 Изменение (24ч): {data['change_24h']:+.1f}%\n"
                f"💎 Объем: ${data['volume_24h']:,.0f}\n\n"
                f"⛓ On-chain метрики:\n"
                f"• Gas: {metrics['gas']} gwei (${metrics['gas_usd']:.4f})\n"
                f"• TVL: ${metrics['tvl']:,.0f}\n"
                f"• TPS: {metrics.get('tps', 'N/A')}\n"
                f"• Валидаторы: {metrics.get('validators', 'N/A')}\n"
                f"• Среднее время транзакции: {metrics['avg_time']} сек\n"
            )

        elif symbol == "TRX":
            data = await market.get_tron_data()
            metrics = await blockchain.get_tron_metrics()
            
            return (
                f"🔴 TRON (TRX)\n\n"
                f"💰 Цена: ${data['price']:,.4f}\n"
                f"📈 Изменение (24ч): {data['change_24h']:+.1f}%\n"
                f"💎 Объем: ${data['volume_24h']:,.0f}\n\n"
                f"⛓ On-chain метрики:\n"
                f"• TPS: {metrics['tps']}\n"
                f"• TVL: ${metrics['tvl']:,.0f}\n"
                f"• Комиссия: {metrics['fee']} TRX (${metrics['fee_usd']:.4f})\n"
                f"• Валидаторы: {metrics.get('validators', 'N/A')}\n"
                f"• Среднее время транзакции: {metrics['avg_time']} сек\n"
            )

        elif symbol == "TON":
            data = await market.get_ton_data()
            metrics = await blockchain.get_ton_metrics()
            
            return (
                f"💎 TON\n\n"
                f"💰 Цена: ${data['price']:,.4f}\n"
                f"📈 Изменение (24ч): {data['change_24h']:+.1f}%\n"
                f"💎 Объем: ${data['volume_24h']:,.0f}\n\n"
                f"⛓ On-chain метрики:\n"
                f"• TPS: {metrics['tps']}\n"
                f"• TVL: ${metrics['tvl']:,.0f}\n"
                f"• Комиссия: {metrics['fee']} TON (${metrics['fee_usd']:.4f})\n"
                f"• Валидаторы: {metrics.get('validators', 'N/A')}\n"
                f"• Среднее время транзакции: {metrics['avg_time']} сек\n"
            )

        elif symbol == "XRP":
            data = await market.get_xrp_data()
            metrics = await blockchain.get_xrp_metrics()
            
            return (
                f"🌊 Ripple (XRP)\n\n"
                f"💰 Цена: ${data['price']:,.4f}\n"
                f"📈 Изменение (24ч): {data['change_24h']:+.1f}%\n"
                f"💎 Объем: ${data['volume_24h']:,.0f}\n\n"
                f"⛓ On-chain метрики:\n"
                f"• TPS: {metrics['tps']}\n"
                f"• TVL: ${metrics['tvl']:,.0f}\n"
                f"• Комиссия: {metrics['fee']} XRP (${metrics['fee_usd']:.4f})\n"
                f"• Валидаторы: {metrics.get('validators', 'N/A')}\n"
                f"• Среднее время транзакции: {metrics['avg_time']} сек\n"
            )

        elif symbol == "SUI":
            data = await market.get_sui_data()
            metrics = await blockchain.get_sui_metrics()
            
            return (
                f"🔵 SUI\n\n"
                f"💰 Цена: ${data['price']:,.4f}\n"
                f"📈 Изменение (24ч): {data['change_24h']:+.1f}%\n"
                f"💎 Объем: ${data['volume_24h']:,.0f}\n\n"
                f"⛓ On-chain метрики:\n"
                f"• TPS: {metrics['tps']}\n"
                f"• TVL: ${metrics['tvl']:,.0f}\n"
                f"• Комиссия: {metrics['fee']} SUI (${metrics['fee_usd']:.4f})\n"
                f"• Валидаторы: {metrics.get('validators', 'N/A')}\n"
                f"• Среднее время транзакции: {metrics['avg_time']} сек\n"
            )

    except Exception as e:
        logger.error(f"Error getting {symbol} info: {e}")
        return f"⚠️ Ошибка при получении данных для {symbol}"

@router.callback_query(lambda c: c.data.startswith("crypto_"))
async def show_crypto_info(callback: types.CallbackQuery):
    """Показывает информацию о выбранной криптовалюте."""
    try:
        symbol = callback.data.split("_")[1].upper()
        await callback.answer(f"Получаю данные для {symbol}...")
        
        info = await get_crypto_info(symbol)
        
        # Добавляем кнопки действий
        builder = InlineKeyboardBuilder()
        builder.button(text="📊 График", callback_data=f"chart_{symbol.lower()}")
        builder.button(text="⚡️ Уведомления", callback_data=f"alert_{symbol.lower()}")
        builder.button(text="↩️ Назад", callback_data="menu_crypto")
        builder.adjust(2)
        
        await callback.message.edit_text(
            text=info,
            reply_markup=builder.as_markup()
        )
        logger.info(f"Crypto info shown to user {callback.from_user.id} for {symbol}")
        
    except Exception as e:
        logger.error(f"Error in crypto menu: {e}")
        await callback.message.edit_text(
            "⚠️ Произошла ошибка. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ Назад", callback_data="menu_crypto")
            .as_markup()
        )

@router.callback_query(lambda c: c.data.startswith("chart_"))
async def show_chart(callback: types.CallbackQuery):
    """Показывает график криптовалюты."""
    try:
        symbol = callback.data.split("_")[1].upper()
        await callback.answer("Генерирую график...")
        
        # Здесь будет логика получения и отображения графика
        chart_data = await technical.get_chart_data(symbol)
        
        builder = InlineKeyboardBuilder()
        builder.button(text="1H", callback_data=f"timeframe_{symbol.lower()}_1h")
        builder.button(text="4H", callback_data=f"timeframe_{symbol.lower()}_4h")
        builder.button(text="1D", callback_data=f"timeframe_{symbol.lower()}_1d")
        builder.button(text="1W", callback_data=f"timeframe_{symbol.lower()}_1w")
        builder.button(text="↩️ Назад", callback_data=f"crypto_{symbol.lower()}")
        builder.adjust(4, 1)
        
        await callback.message.edit_text(
            text=chart_data['description'],
            reply_markup=builder.as_markup()
        )
        
        # Отправляем изображение графика
        if chart_data.get('image'):
            await callback.message.answer_photo(
                photo=chart_data['image'],
                caption=f"График {symbol}/USDT"
            )
            
    except Exception as e:
        logger.error(f"Error showing chart: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка при генерации графика. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ Назад", callback_data=f"crypto_{symbol.lower()}")
            .as_markup()
        )

@router.callback_query(lambda c: c.data.startswith("alert_"))
async def setup_alert(callback: types.CallbackQuery):
    """Настройка уведомлений для криптовалюты."""
    try:
        symbol = callback.data.split("_")[1].upper()
        
        builder = InlineKeyboardBuilder()
        builder.button(text="📈 Цена выше", callback_data=f"alert_price_above_{symbol.lower()}")
        builder.button(text="📉 Цена ниже", callback_data=f"alert_price_below_{symbol.lower()}")
        builder.button(text="💹 Изменение %", callback_data=f"alert_change_{symbol.lower()}")
        builder.button(text="📊 Объем", callback_data=f"alert_volume_{symbol.lower()}")
        builder.button(text="↩️ Назад", callback_data=f"crypto_{symbol.lower()}")
        builder.adjust(2, 2, 1)
        
        await callback.message.edit_text(
            f"⚡️ Настройка уведомлений для {symbol}\n\n"
            "Выберите тип уведомления:",
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error setting up alert: {e}")
        await callback.message.edit_text(
            "⚠️ Ошибка при настройке уведомлений. Попробуйте позже.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ Назад", callback_data=f"crypto_{symbol.lower()}")
            .as_markup()
        ) 