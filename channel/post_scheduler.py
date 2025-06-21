import asyncio
from datetime import datetime, timedelta
from typing import Optional
import random
from services.coinmarketcap import cmc_api
from services.binance import binance_api
from core import bot
from config import CHANNEL_ID, MIN_POST_INTERVAL, MAX_DAILY_POSTS
from services.blockchain_stats import blockchain_stats
from services.report_generator import generate_report
import logging

logger = logging.getLogger(__name__)

async def generate_market_update() -> str:
    """Generate market update post."""
    btc = cmc_api.get_market_metrics('BTC')
    eth = cmc_api.get_market_metrics('ETH')
    
    post = f"""
🔥 Обновление рынка | {datetime.now().strftime('%H:%M МСК')}

BTC: ${btc['price']:,.2f} ({btc['percent_change_24h']:+.1f}%)
ETH: ${eth['price']:,.2f} ({eth['percent_change_24h']:+.1f}%)

Объёмы за 24ч:
• BTC: ${btc['volume_24h']:,.0f}
• ETH: ${eth['volume_24h']:,.0f}

#Market #BTC #ETH
"""
    return post

async def generate_trending_post() -> str:
    """Generate post about trending coins."""
    trending = cmc_api.get_trending_coins(limit=5)
    
    post = "🔥 Топ движения за 4 часа:\n\n"
    
    for coin in trending:
        quote = coin['quote']['USD']
        post += f"• {coin['symbol']}: {quote['percent_change_24h']:+.1f}%\n"
        post += f"  ${quote['price']:,.4f} | Vol: ${quote['volume_24h']:,.0f}\n\n"
    
    post += "#Trading #Crypto"
    return post

async def generate_onchain_post() -> Optional[str]:
    """Generate on-chain metrics post."""
    try:
        metrics = glassnode_api.get_btc_metrics()
        
        post = f"""
⛓ On-chain метрики BTC:

• Активные адреса: {metrics['active_addresses']:,}
• Транзакции: {metrics['transactions']:,}
• Средний размер TX: {metrics['avg_transaction_size']:,.2f} BTC
• Хэшрейт: {metrics['hashrate']:.1f} EH/s

#Bitcoin #OnChain
"""
        return post
    except Exception:
        return None

async def generate_channel_post() -> str:
    """Генерация поста для канала."""
    # Получаем данные о рынке
    btc_data = cmc_api.get_market_metrics('BTC')
    eth_data = cmc_api.get_market_metrics('ETH')
    trending = cmc_api.get_trending_coins(limit=3)
    
    # Получаем on-chain метрики
    btc_metrics = blockchain_stats.get_btc_metrics()
    eth_metrics = blockchain_stats.get_eth_metrics()
    
    # Форматируем топ монеты
    top_coins = ""
    for coin in trending:
        quote = coin['quote']['USD']
        top_coins += f"• {coin['symbol']}: {quote['percent_change_24h']:.1f}% (${quote['price']:,.2f})\n"
    
    post = f"""
📊 Обновление рынка

#BTC ${btc_data['price']:,.0f} ({btc_data['percent_change_24h']:.1f}%)
Активные адреса: {btc_metrics['active_addresses']:,}
Транзакции: {btc_metrics['transactions']:,}

#ETH ${eth_data['price']:.0f} ({eth_data['percent_change_24h']:.1f}%)
Gas: {eth_metrics['gas_price']} gwei
Supply: {eth_metrics['total_supply']:,.0f} ETH

🔥 Топ движения за 24ч:
{top_coins}
"""
    return post.strip()

async def post_to_channel():
    """Публикация отчета в канал."""
    try:
        logger.info(f"Generating report for channel {CHANNEL_ID}")
        report = await generate_report()
        
        logger.info(f"Posting report to channel {CHANNEL_ID}")
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=report,
            disable_web_page_preview=True
        )
        logger.info("Channel post sent successfully")
        
    except Exception as e:
        logger.error(f"Error posting to channel: {e}")

def schedule_channel_posts(scheduler):
    """Настройка расписания постов в канал."""
    try:
        logger.info("Setting up channel post scheduler...")
        
        # Планируем посты с интервалом MIN_POST_INTERVAL
        scheduler.add_job(
            post_to_channel,
            'interval',
            hours=MIN_POST_INTERVAL // 3600,  # Конвертируем секунды в часы
            id='channel_posts',
            max_instances=MAX_DAILY_POSTS
        )
        
        logger.info(f"Channel posts scheduled every {MIN_POST_INTERVAL // 3600} hours")
        
    except Exception as e:
        logger.error(f"Error configuring channel post scheduler: {e}")
        raise 