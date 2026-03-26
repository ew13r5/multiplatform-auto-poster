import logging
from typing import List

logger = logging.getLogger(__name__)


async def send_telegram(bot_token: str, chat_ids: List[str], message: str) -> None:
    """Send formatted message to multiple Telegram chats (async)."""
    try:
        from telegram import Bot
        bot = Bot(token=bot_token)
        for chat_id in chat_ids:
            try:
                await bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
            except Exception as e:
                logger.warning("Failed to send Telegram to %s: %s", chat_id, e)
    except ImportError:
        logger.warning("python-telegram-bot not installed, skipping Telegram send")
    except Exception as e:
        logger.warning("Telegram send error: %s", e)


def send_telegram_sync(bot_token: str, chat_ids: List[str], message: str) -> None:
    """Sync wrapper for Telegram sending (for use in Celery tasks)."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # In async context, can't use asyncio.run
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                pool.submit(asyncio.run, send_telegram(bot_token, chat_ids, message)).result(timeout=10)
        else:
            asyncio.run(send_telegram(bot_token, chat_ids, message))
    except Exception as e:
        logger.warning("Telegram sync send failed: %s", e)
