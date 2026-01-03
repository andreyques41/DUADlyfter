"""Email sending via SendGrid.

This service is best-effort: failures are logged and should not break core flows.
"""

from __future__ import annotations

import os
from typing import Optional

from config import settings
from config.logging import get_logger


logger = get_logger(__name__)


class EmailService:
    """Simple wrapper around SendGrid."""

    @staticmethod
    def enabled() -> bool:
        if os.getenv("EMAIL_ENABLED", "").lower() in {"0", "false", "no"}:
            return False
        return bool(getattr(settings, "SENDGRID_API_KEY", ""))

    @staticmethod
    def send_email(
        *,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """Send an email.

        Returns:
            bool: True if SendGrid accepted the request.
        """
        if not EmailService.enabled():
            return False

        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
        except Exception as e:
            logger.warning(f"SendGrid dependencies unavailable: {e}")
            return False

        try:
            message = Mail(
                from_email=(settings.SENDGRID_FROM_EMAIL, settings.SENDGRID_FROM_NAME),
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
                plain_text_content=text_content,
            )
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            accepted = 200 <= response.status_code < 300
            if accepted:
                logger.info(f"Email sent to {to_email}: {subject}")
            else:
                logger.warning(
                    f"SendGrid rejected email to {to_email}: status={response.status_code}"
                )
            return accepted
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}", exc_info=True)
            return False

    @staticmethod
    def send_welcome_email(*, to_email: str, username: str) -> bool:
        subject = "Welcome to LyfterCook"
        html = (
            "<h2>Welcome to LyfterCook</h2>"
            f"<p>Hi <strong>{username}</strong>, your account is ready.</p>"
            "<p>You can now log in and start creating menus, quotations, and appointments.</p>"
        )
        text = f"Welcome to LyfterCook, {username}. Your account is ready."
        return EmailService.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html,
            text_content=text,
        )
