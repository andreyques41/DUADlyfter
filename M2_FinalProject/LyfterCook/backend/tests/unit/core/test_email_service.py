"""Unit tests for EmailService (ADR-003 P0).

Tests email sending logic with mocked SMTP for Mailtrap/SendGrid.
"""

from __future__ import annotations

import smtplib
from unittest.mock import MagicMock, patch

import pytest

from app.core.services.email_service import EmailService, EmailAttachment


class TestEmailServiceEnabled:
    """Test enabled() configuration toggle."""

    def test_email_disabled_by_config(self, monkeypatch):
        """EMAIL_ENABLED=false → disabled."""
        from config import settings

        monkeypatch.setattr(settings, "EMAIL_ENABLED", False)
        assert EmailService.enabled() is False

    def test_email_enabled_no_username(self, monkeypatch):
        """EMAIL_ENABLED=true but no username → disabled."""
        from config import settings

        monkeypatch.setattr(settings, "EMAIL_ENABLED", True)
        monkeypatch.setattr(settings, "MAILTRAP_USERNAME", "")
        monkeypatch.setattr(settings, "MAILTRAP_PASSWORD", "pass123")
        assert EmailService.enabled() is False

    def test_email_enabled_no_password(self, monkeypatch):
        """EMAIL_ENABLED=true but no password → disabled."""
        from config import settings

        monkeypatch.setattr(settings, "EMAIL_ENABLED", True)
        monkeypatch.setattr(settings, "MAILTRAP_USERNAME", "user123")
        monkeypatch.setattr(settings, "MAILTRAP_PASSWORD", "")
        assert EmailService.enabled() is False

    def test_email_enabled_with_credentials(self, monkeypatch):
        """EMAIL_ENABLED=true + credentials → enabled."""
        from config import settings

        monkeypatch.setattr(settings, "EMAIL_ENABLED", True)
        monkeypatch.setattr(settings, "MAILTRAP_USERNAME", "user123")
        monkeypatch.setattr(settings, "MAILTRAP_PASSWORD", "pass123")
        assert EmailService.enabled() is True


class TestEmailServiceSend:
    """Test send_email() method with SMTP mocking."""

    def test_send_email_when_disabled_returns_false(self, monkeypatch):
        """send_email() returns False if enabled() is False."""
        from config import settings

        monkeypatch.setattr(settings, "EMAIL_ENABLED", False)

        result = EmailService.send_email(
            to_email="test@example.com",
            subject="Test",
            html_content="<p>Test</p>",
        )

        assert result is False

    def test_send_email_success(self, monkeypatch):
        """SMTP connection succeeds and email is sent."""
        from config import settings

        monkeypatch.setattr(settings, "EMAIL_ENABLED", True)
        monkeypatch.setattr(settings, "MAILTRAP_USERNAME", "user")
        monkeypatch.setattr(settings, "MAILTRAP_PASSWORD", "pass")
        monkeypatch.setattr(settings, "MAILTRAP_HOST", "smtp.test.com")
        monkeypatch.setattr(settings, "MAILTRAP_PORT", 2525)
        monkeypatch.setattr(settings, "MAILTRAP_USE_TLS", True)
        monkeypatch.setattr(settings, "MAILTRAP_FROM_EMAIL", "from@test.com")
        monkeypatch.setattr(settings, "MAILTRAP_FROM_NAME", "Test Sender")

        mock_smtp_instance = MagicMock()
        mock_smtp_class = MagicMock(return_value=mock_smtp_instance)
        # Make context manager work
        mock_smtp_instance.__enter__ = MagicMock(return_value=mock_smtp_instance)
        mock_smtp_instance.__exit__ = MagicMock(return_value=False)

        with patch("app.core.services.email_service.smtplib.SMTP", mock_smtp_class):
            result = EmailService.send_email(
                to_email="recipient@example.com",
                subject="Test Subject",
                html_content="<p>Test HTML</p>",
                text_content="Test text",
            )

        assert result is True
        mock_smtp_class.assert_called_once()
        # ehlo() is called at least once (possibly twice: before and after STARTTLS)
        assert mock_smtp_instance.ehlo.call_count >= 1
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with("user", "pass")
        mock_smtp_instance.send_message.assert_called_once()

    def test_send_email_smtp_connection_fails(self, monkeypatch):
        """SMTP connection exception → returns False."""
        from config import settings

        monkeypatch.setattr(settings, "EMAIL_ENABLED", True)
        monkeypatch.setattr(settings, "MAILTRAP_USERNAME", "user")
        monkeypatch.setattr(settings, "MAILTRAP_PASSWORD", "pass")

        with patch("app.core.services.email_service.smtplib.SMTP", side_effect=smtplib.SMTPException("Connection failed")):
            result = EmailService.send_email(
                to_email="test@example.com",
                subject="Test",
                html_content="<p>Test</p>",
            )

        assert result is False

    def test_send_email_login_fails(self, monkeypatch):
        """Login failure returns False."""
        from config import settings

        monkeypatch.setattr(settings, "EMAIL_ENABLED", True)
        monkeypatch.setattr(settings, "MAILTRAP_USERNAME", "user")
        monkeypatch.setattr(settings, "MAILTRAP_PASSWORD", "wrongpass")

        mock_smtp_instance = MagicMock()
        mock_smtp_class = MagicMock(return_value=mock_smtp_instance)
        mock_smtp_instance.__enter__ = MagicMock(return_value=mock_smtp_instance)
        mock_smtp_instance.__exit__ = MagicMock(return_value=False)
        # Make login fail
        mock_smtp_instance.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Auth failed")

        with patch("app.core.services.email_service.smtplib.SMTP", mock_smtp_class):
            result = EmailService.send_email(
                to_email="test@example.com",
                subject="Test",
                html_content="<p>Test</p>",
            )

        assert result is False

    def test_send_email_send_message_fails(self, monkeypatch):
        """Send message failure returns False."""
        from config import settings

        monkeypatch.setattr(settings, "EMAIL_ENABLED", True)
        monkeypatch.setattr(settings, "MAILTRAP_USERNAME", "user")
        monkeypatch.setattr(settings, "MAILTRAP_PASSWORD", "pass")

        mock_smtp_instance = MagicMock()
        mock_smtp_class = MagicMock(return_value=mock_smtp_instance)
        mock_smtp_instance.__enter__ = MagicMock(return_value=mock_smtp_instance)
        mock_smtp_instance.__exit__ = MagicMock(return_value=False)
        # Make send_message fail
        mock_smtp_instance.send_message.side_effect = smtplib.SMTPException("Send failed")

        with patch("app.core.services.email_service.smtplib.SMTP", mock_smtp_class):
            result = EmailService.send_email(
                to_email="test@example.com",
                subject="Test",
                html_content="<p>Test</p>",
            )

        assert result is False


class TestEmailServiceAttachments:
    """Test attachment handling."""

    def test_send_email_with_attachment(self, monkeypatch):
        """Email with attachment is properly constructed."""
        from config import settings

        monkeypatch.setattr(settings, "EMAIL_ENABLED", True)
        monkeypatch.setattr(settings, "MAILTRAP_USERNAME", "user")
        monkeypatch.setattr(settings, "MAILTRAP_PASSWORD", "pass")

        attachment = EmailAttachment(
            filename="report.pdf",
            content_bytes=b"%PDF fake",
            mime_type="application/pdf",
        )

        mock_smtp_instance = MagicMock()
        mock_smtp_class = MagicMock(return_value=mock_smtp_instance)
        mock_smtp_instance.__enter__ = MagicMock(return_value=mock_smtp_instance)
        mock_smtp_instance.__exit__ = MagicMock(return_value=False)

        with patch("app.core.services.email_service.smtplib.SMTP", mock_smtp_class):
            result = EmailService.send_email(
                to_email="test@example.com",
                subject="Report",
                html_content="<p>See attached report</p>",
                attachments=[attachment],
            )

        assert result is True
        # Verify send_message was called
        mock_smtp_instance.send_message.assert_called_once()
        # Get the EmailMessage that was sent
        call_args = mock_smtp_instance.send_message.call_args
        msg = call_args[0][0] if call_args and call_args[0] else None
        assert msg is not None
        # Verify it's an email.message.EmailMessage with correct headers
        assert msg["Subject"] == "Report"
        assert msg["To"] == "test@example.com"


class TestEmailServiceWelcomeEmail:
    """Test send_welcome_email() helper."""

    def test_send_welcome_email(self, monkeypatch):
        """Welcome email is sent with correct parameters."""
        from config import settings

        monkeypatch.setattr(settings, "EMAIL_ENABLED", True)
        monkeypatch.setattr(settings, "MAILTRAP_USERNAME", "user")
        monkeypatch.setattr(settings, "MAILTRAP_PASSWORD", "pass")

        mock_smtp_instance = MagicMock()
        mock_smtp_class = MagicMock(return_value=mock_smtp_instance)
        mock_smtp_instance.__enter__ = MagicMock(return_value=mock_smtp_instance)
        mock_smtp_instance.__exit__ = MagicMock(return_value=False)

        with patch("app.core.services.email_service.smtplib.SMTP", mock_smtp_class):
            result = EmailService.send_welcome_email(
                to_email="newuser@example.com",
                username="johndoe",
            )

        assert result is True
        # Verify email was sent
        mock_smtp_instance.send_message.assert_called_once()
        call_args = mock_smtp_instance.send_message.call_args
        msg = call_args[0][0] if call_args and call_args[0] else None
        assert msg is not None
        assert msg["Subject"] == "Welcome to LyfterCook"
        assert msg["To"] == "newuser@example.com"
