import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from app.config import get_settings

logger = logging.getLogger(__name__)


def send_email_sync(recipients: List[str], subject: str, body: str) -> None:
    """Send email via SMTP (synchronous)."""
    settings = get_settings()
    if not settings.SMTP_HOST:
        logger.debug("SMTP not configured, skipping email")
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM or settings.SMTP_USER
        msg["To"] = ", ".join(recipients)

        # Plain text
        msg.attach(MIMEText(body, "plain"))

        # HTML version
        html_body = f"""
        <div style="font-family: Arial, sans-serif; padding: 16px;">
            <div style="border-left: 4px solid #e53e3e; padding: 12px; background: #fff5f5;">
                <pre style="white-space: pre-wrap;">{body}</pre>
            </div>
        </div>
        """
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(msg["From"], recipients, msg.as_string())

        logger.info("Email sent to %s: %s", recipients, subject)
    except Exception as e:
        logger.warning("Email send failed: %s", e)


async def send_email(recipients: List[str], subject: str, body: str) -> None:
    """Async wrapper for email sending."""
    import asyncio
    await asyncio.to_thread(send_email_sync, recipients, subject, body)
