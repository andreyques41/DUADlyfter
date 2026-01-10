"""Compatibility shim for email service.

Historically the codebase imported `EmailService` from this module.
The implementation lives in `app.core.services.email_service`.
"""

from app.core.services.email_service import EmailAttachment, EmailService

__all__ = ["EmailService", "EmailAttachment"]
