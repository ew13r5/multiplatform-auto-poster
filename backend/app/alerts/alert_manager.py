import json
import logging
from datetime import datetime
from typing import Optional

import redis as sync_redis
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.alert_log import AlertLog, AlertChannel, AlertSeverity

logger = logging.getLogger(__name__)

# Alert type constants
EMPTY_QUEUE = "empty_queue"
LOW_QUEUE = "low_queue"
ERROR_SPIKE = "error_spike"
MISSED_SLOT = "missed_slot"
TOKEN_EXPIRY = "token_expiry"
SCHEDULER_DOWN = "scheduler_down"
PUBLISH_FAILED = "publish_failed"
TOKEN_UNHEALTHY = "token_unhealthy"

# Severity emojis
_SEVERITY_EMOJI = {
    "critical": "🔴",
    "warning": "🟡",
    "info": "🔵",
}


def _get_redis():
    settings = get_settings()
    return sync_redis.from_url(settings.REDIS_URL, decode_responses=True)


def _get_alert_config(page_id: Optional[str]) -> dict:
    """Load alert config for a page from Redis."""
    if not page_id:
        return {"telegram_enabled": True, "email_enabled": False, "telegram_chat_ids": [], "email_recipients": [], "dedup_window_minutes": 30}
    try:
        r = _get_redis()
        config_str = r.get(f"alert_config:{page_id}")
        if config_str:
            return json.loads(config_str)
    except Exception:
        pass
    return {"telegram_enabled": False, "email_enabled": False, "telegram_chat_ids": [], "email_recipients": [], "dedup_window_minutes": 30}


def format_alert_message(alert_type: str, message: str, severity: str, page_name: str = "") -> str:
    """Format alert message with emoji and structure."""
    emoji = _SEVERITY_EMOJI.get(severity, "ℹ️")
    title = alert_type.replace("_", " ").title()
    lines = [f"{emoji} {severity.upper()}: {title}"]
    if page_name:
        lines.append(f"Page: {page_name}")
    lines.append(f"Details: {message}")
    lines.append(f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    return "\n".join(lines)


def send_alert(
    alert_type: str,
    message: str,
    page_id: Optional[str],
    severity: str,
    db: Optional[Session] = None,
    page_name: str = "",
) -> bool:
    """Route alert to configured channels with deduplication.

    Returns True if alert was sent, False if deduplicated/skipped.
    """
    # Dedup check
    dedup_key = f"alert_dedup:{alert_type}:{page_id or 'global'}"
    try:
        r = _get_redis()
        if r.exists(dedup_key):
            logger.debug("Alert deduplicated: %s for page %s", alert_type, page_id)
            return False
    except Exception:
        r = None

    # Load config
    config = _get_alert_config(page_id)
    formatted = format_alert_message(alert_type, message, severity, page_name)

    # Route to Telegram
    if config.get("telegram_enabled") and config.get("telegram_chat_ids"):
        try:
            from app.alerts.telegram_sender import send_telegram_sync
            settings = get_settings()
            if settings.TELEGRAM_BOT_TOKEN:
                send_telegram_sync(
                    settings.TELEGRAM_BOT_TOKEN,
                    config["telegram_chat_ids"],
                    formatted,
                )
        except Exception as e:
            logger.warning("Telegram send failed: %s", e)

    # Route to Email
    if config.get("email_enabled") and config.get("email_recipients"):
        try:
            from app.alerts.email_sender import send_email_sync
            title = f"{_SEVERITY_EMOJI.get(severity, '')} {alert_type.replace('_', ' ').title()}"
            send_email_sync(config["email_recipients"], title, formatted)
        except Exception as e:
            logger.warning("Email send failed: %s", e)

    # Always broadcast via WebSocket
    try:
        from app.api.websocket import manager
        import asyncio
        asyncio.get_event_loop().create_task(manager.broadcast({
            "event": "alert",
            "type": alert_type,
            "message": message,
            "severity": severity,
            "page_id": str(page_id) if page_id else None,
        }))
    except Exception:
        pass  # No event loop in sync context (Celery)

    # Set dedup key
    dedup_window = config.get("dedup_window_minutes", 30) * 60
    try:
        if r:
            r.setex(dedup_key, dedup_window, "1")
    except Exception:
        pass

    # Log to DB
    if db:
        try:
            log = AlertLog(
                type=alert_type,
                message=message,
                page_id=page_id,
                channel=AlertChannel.in_app,
                severity=AlertSeverity(severity) if severity in [s.value for s in AlertSeverity] else AlertSeverity.info,
            )
            db.add(log)
            db.commit()
        except Exception as e:
            logger.warning("Failed to log alert: %s", e)

    logger.info("Alert sent: %s %s for page %s", severity, alert_type, page_id)
    return True
