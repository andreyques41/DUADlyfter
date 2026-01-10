"""Email sending service (Mailtrap SMTP only).

This service is best-effort: failures are logged and should not break core flows.

Configuration is sourced from `config.settings`:
- EMAIL_ENABLED
- MAILTRAP_HOST, MAILTRAP_PORT
- MAILTRAP_USERNAME, MAILTRAP_PASSWORD
- MAILTRAP_USE_TLS
- MAILTRAP_FROM_EMAIL, MAILTRAP_FROM_NAME
"""

from __future__ import annotations

import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path
from typing import Optional, Sequence

from config import settings
from config.logging import get_logger


logger = get_logger(__name__)


@dataclass(frozen=True)
class EmailAttachment:
    filename: str
    content_bytes: bytes
    mime_type: str = "application/octet-stream"


class EmailService:
    """Simple wrapper for outbound email."""

    @staticmethod
    def enabled() -> bool:
        if not bool(getattr(settings, "EMAIL_ENABLED", False)):
            return False

        username = (getattr(settings, "MAILTRAP_USERNAME", "") or "").strip()
        password = (getattr(settings, "MAILTRAP_PASSWORD", "") or "").strip()
        return bool(username and password)

    @staticmethod
    def send_email(
        *,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[Sequence[EmailAttachment]] = None,
    ) -> bool:
        """Send an email.

        Returns:
            bool: True if provider accepted the request.
        """
        if not EmailService.enabled():
            return False

        from_email = (getattr(settings, "MAILTRAP_FROM_EMAIL", "") or "").strip()
        from_name = (getattr(settings, "MAILTRAP_FROM_NAME", "") or "").strip()
        from_header = f"{from_name} <{from_email}>" if from_name else from_email

        host = getattr(settings, "MAILTRAP_HOST", "sandbox.smtp.mailtrap.io")
        port = int(getattr(settings, "MAILTRAP_PORT", 2525))
        username = (getattr(settings, "MAILTRAP_USERNAME", "") or "").strip()
        password = (getattr(settings, "MAILTRAP_PASSWORD", "") or "").strip()
        use_tls = bool(getattr(settings, "MAILTRAP_USE_TLS", True))

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_header
        msg["To"] = to_email

        msg.set_content(text_content or "")
        msg.add_alternative(html_content, subtype="html")

        if attachments:
            for attachment in attachments:
                mime = (attachment.mime_type or "application/octet-stream").strip()
                if "/" in mime:
                    maintype, subtype = mime.split("/", 1)
                else:
                    maintype, subtype = "application", "octet-stream"

                msg.add_attachment(
                    attachment.content_bytes,
                    maintype=maintype,
                    subtype=subtype,
                    filename=attachment.filename,
                )

        try:
            timeout = 15
            context = ssl.create_default_context()
            with smtplib.SMTP(host=host, port=port, timeout=timeout) as smtp:
                smtp.ehlo()
                if use_tls:
                    smtp.starttls(context=context)
                    smtp.ehlo()
                smtp.login(username, password)
                smtp.send_message(msg)

            logger.info(f"Email sent via Mailtrap SMTP to {to_email}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email via Mailtrap SMTP to {to_email}: {e}", exc_info=True)
            return False

    @staticmethod
    def _templates_dir() -> Path:
        # .../app/core/services/email_service.py -> .../app/core/templates
        return Path(__file__).resolve().parents[1] / "templates"

    @staticmethod
    def _render_template(template_name: str, **context: object) -> str:
        from jinja2 import Environment, FileSystemLoader, select_autoescape

        env = Environment(
            loader=FileSystemLoader(str(EmailService._templates_dir())),
            autoescape=select_autoescape(["html", "xml"]),
        )
        template = env.get_template(template_name)
        return template.render(**context)

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

    @staticmethod
    def send_quotation_email(
        *,
        to_email: str,
        chef_name: str,
        quotation_number: str,
        pdf_bytes: bytes,
        client_name: str = "",
        custom_message: Optional[str] = None,
    ) -> bool:
        html_body = EmailService._render_template(
            "quotation_email.html",
            client_name=client_name,
            chef_name=chef_name,
            quotation_number=quotation_number,
            custom_message=custom_message,
        )
        text_body = (
            f"Quotation {quotation_number} from {chef_name}. "
            "The PDF is attached. "
            + (f"Message: {custom_message}" if custom_message else "")
        ).strip()

        filename = f"quotation-{quotation_number}.pdf"
        return EmailService.send_email(
            to_email=to_email,
            subject=f"Quotation {quotation_number}",
            html_content=html_body,
            text_content=text_body,
            attachments=[EmailAttachment(filename=filename, content_bytes=pdf_bytes, mime_type="application/pdf")],
        )

    @staticmethod
    def send_contact_notification(
        *,
        chef_email: str,
        visitor_name: str,
        visitor_email: str,
        message: str,
        visitor_phone: Optional[str] = None,
        chef_name: str = "",
    ) -> bool:
        html_body = EmailService._render_template(
            "contact_notification.html",
            chef_name=chef_name,
            visitor_name=visitor_name,
            visitor_email=visitor_email,
            visitor_phone=visitor_phone,
            message=message,
        )
        text_body = (
            f"New contact request from {visitor_name} ({visitor_email})"
            + (f" Phone: {visitor_phone}." if visitor_phone else ".")
            + f" Message: {message}"
        )
        return EmailService.send_email(
            to_email=chef_email,
            subject=f"New contact request from {visitor_name}",
            html_content=html_body,
            text_content=text_body,
        )
