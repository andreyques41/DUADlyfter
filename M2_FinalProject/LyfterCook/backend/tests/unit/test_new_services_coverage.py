import builtins
import importlib
import sys
import types
from datetime import datetime, timezone
from types import SimpleNamespace


def test_calendar_ics_service_appointment_to_event_and_escaping():
    from app.appointments.services.calendar_ics_service import CalendarIcsService

    appointment = SimpleNamespace(
        id=123,
        scheduled_at=datetime(2026, 1, 1, 12, 0, 0),  # naive -> treated as UTC
        duration_minutes=None,
        title="Team; Sync, \\ Weekly\nMeeting",
        description="Line1\nLine2",
        meeting_url="https://meet.example.com/abc",
        location="HQ, Floor; 2",
    )

    event = CalendarIcsService.appointment_to_event(appointment, backend_url="http://localhost:5000/")
    assert event.uid == "appointment-123@lyftercook"
    assert event.dtstart_utc.tzinfo == timezone.utc
    assert event.dtend_utc.tzinfo == timezone.utc
    # Default duration is 60 when missing/falsey
    assert int((event.dtend_utc - event.dtstart_utc).total_seconds()) == 60 * 60
    assert event.url == "http://localhost:5000/appointments/123"

    ics = event.to_ics()
    assert "BEGIN:VCALENDAR" in ics
    assert "BEGIN:VEVENT" in ics
    assert "END:VCALENDAR" in ics
    # Escaping for special chars and newlines
    assert "SUMMARY:Team\\; Sync\\, \\\\ Weekly\\nMeeting" in ics
    assert "LOCATION:HQ\\, Floor\\; 2" in ics
    assert "DESCRIPTION:Line1\\nLine2\\\\n\\\\nMeeting: https://meet.example.com/abc" in ics


def test_calendar_ics_service_invalid_scheduled_at_raises():
    from app.appointments.services.calendar_ics_service import CalendarIcsService

    appointment = SimpleNamespace(id=1, scheduled_at="not-a-datetime")
    try:
        CalendarIcsService.appointment_to_event(appointment)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_quotation_pdf_service_render_html_escapes_and_renders_items():
    from app.quotations.services.quotation_pdf_service import QuotationPdfService

    client = SimpleNamespace(name="Alice & Bob")
    item1 = SimpleNamespace(
        item_name="Dish <1>",
        description="Desc & details",
        quantity=2,
        unit_price="10.00",
        subtotal="20.00",
    )
    quotation = SimpleNamespace(
        id=99,
        quotation_number="Q-<99>",
        status="PENDING",
        created_at=datetime(2026, 1, 2, 8, 30, 0),
        client=client,
        items=[item1],
        total_amount="20.00",
        notes="Note <b>bold</b>",
        terms_and_conditions="Terms & conditions",
    )

    html_str = QuotationPdfService.render_html(quotation)
    assert "Quotation Q-&lt;99&gt;" in html_str
    assert "Alice &amp; Bob" in html_str
    assert "Dish &lt;1&gt;" in html_str
    assert "Desc &amp; details" in html_str
    assert "Note &lt;b&gt;bold&lt;/b&gt;" in html_str
    assert "Terms &amp; conditions" in html_str


def test_quotation_pdf_service_render_pdf_weasyprint_unavailable(monkeypatch):
    from app.quotations.services.quotation_pdf_service import QuotationPdfService

    quotation = SimpleNamespace(id=1, quotation_number="Q-1", status="PENDING", created_at=None, items=[])

    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "weasyprint":
            raise Exception("no weasyprint")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    result = QuotationPdfService.render_pdf(quotation)
    assert result.ok is False
    assert result.error and "WeasyPrint unavailable" in result.error


def test_quotation_pdf_service_render_pdf_success_with_mocked_weasyprint(monkeypatch):
    from app.quotations.services.quotation_pdf_service import QuotationPdfService

    weasyprint = types.ModuleType("weasyprint")

    class HTML:
        def __init__(self, string):
            self.string = string

        def write_pdf(self):
            return b"%PDF-1.4\nmock"

    weasyprint.HTML = HTML
    monkeypatch.setitem(sys.modules, "weasyprint", weasyprint)

    quotation = SimpleNamespace(id=2, quotation_number="Q-2", status="PENDING", created_at=None, items=[])
    result = QuotationPdfService.render_pdf(quotation)
    assert result.ok is True
    assert result.pdf_bytes and result.pdf_bytes.startswith(b"%PDF")


def test_quotation_pdf_service_render_pdf_failure_returns_generic_error(monkeypatch):
    from app.quotations.services.quotation_pdf_service import QuotationPdfService

    weasyprint = types.ModuleType("weasyprint")

    class HTML:
        def __init__(self, string):
            self.string = string

        def write_pdf(self):
            raise RuntimeError("boom")

    weasyprint.HTML = HTML
    monkeypatch.setitem(sys.modules, "weasyprint", weasyprint)

    quotation = SimpleNamespace(id=3, quotation_number="Q-3", status="PENDING", created_at=None, items=[])
    result = QuotationPdfService.render_pdf(quotation)
    assert result.ok is False
    assert result.error == "Failed to generate PDF"


def _install_fake_sendgrid(monkeypatch, *, status_code=202, raise_on_send=False):
    sendgrid = types.ModuleType("sendgrid")
    helpers = types.ModuleType("sendgrid.helpers")
    helpers_mail = types.ModuleType("sendgrid.helpers.mail")

    class SendGridAPIClient:
        def __init__(self, api_key):
            self.api_key = api_key

        def send(self, message):
            if raise_on_send:
                raise RuntimeError("send failed")
            return SimpleNamespace(status_code=status_code)

    class Mail:
        def __init__(
            self,
            from_email,
            to_emails,
            subject,
            html_content,
            plain_text_content=None,
        ):
            self.from_email = from_email
            self.to_emails = to_emails
            self.subject = subject
            self.html_content = html_content
            self.plain_text_content = plain_text_content

    sendgrid.SendGridAPIClient = SendGridAPIClient
    helpers_mail.Mail = Mail

    monkeypatch.setitem(sys.modules, "sendgrid", sendgrid)
    monkeypatch.setitem(sys.modules, "sendgrid.helpers", helpers)
    monkeypatch.setitem(sys.modules, "sendgrid.helpers.mail", helpers_mail)


def test_email_service_enabled_respects_env_and_api_key(monkeypatch):
    from app.core.email_service import EmailService
    from config import settings

    monkeypatch.setattr(settings, "SENDGRID_API_KEY", "")
    monkeypatch.delenv("EMAIL_ENABLED", raising=False)
    assert EmailService.enabled() is False

    monkeypatch.setattr(settings, "SENDGRID_API_KEY", "key")
    assert EmailService.enabled() is True

    monkeypatch.setenv("EMAIL_ENABLED", "false")
    assert EmailService.enabled() is False


def test_email_service_send_email_disabled_returns_false(monkeypatch):
    from app.core.email_service import EmailService
    from config import settings

    monkeypatch.setattr(settings, "SENDGRID_API_KEY", "")
    monkeypatch.delenv("EMAIL_ENABLED", raising=False)

    ok = EmailService.send_email(
        to_email="a@example.com",
        subject="hi",
        html_content="<p>hi</p>",
    )
    assert ok is False


def test_email_service_send_email_accepts_2xx(monkeypatch):
    from app.core.email_service import EmailService
    from config import settings

    monkeypatch.setattr(settings, "SENDGRID_API_KEY", "key")
    monkeypatch.setattr(settings, "SENDGRID_FROM_EMAIL", "noreply@example.com")
    monkeypatch.setattr(settings, "SENDGRID_FROM_NAME", "LyfterCook")
    monkeypatch.delenv("EMAIL_ENABLED", raising=False)

    _install_fake_sendgrid(monkeypatch, status_code=202)
    ok = EmailService.send_email(
        to_email="a@example.com",
        subject="subject",
        html_content="<p>hi</p>",
        text_content="hi",
    )
    assert ok is True


def test_email_service_send_email_rejects_non_2xx(monkeypatch):
    from app.core.email_service import EmailService
    from config import settings

    monkeypatch.setattr(settings, "SENDGRID_API_KEY", "key")
    monkeypatch.setattr(settings, "SENDGRID_FROM_EMAIL", "noreply@example.com")
    monkeypatch.setattr(settings, "SENDGRID_FROM_NAME", "LyfterCook")
    monkeypatch.delenv("EMAIL_ENABLED", raising=False)

    _install_fake_sendgrid(monkeypatch, status_code=400)
    ok = EmailService.send_email(
        to_email="a@example.com",
        subject="subject",
        html_content="<p>hi</p>",
    )
    assert ok is False


def test_email_service_send_email_handles_send_exception(monkeypatch):
    from app.core.email_service import EmailService
    from config import settings

    monkeypatch.setattr(settings, "SENDGRID_API_KEY", "key")
    monkeypatch.setattr(settings, "SENDGRID_FROM_EMAIL", "noreply@example.com")
    monkeypatch.setattr(settings, "SENDGRID_FROM_NAME", "LyfterCook")
    monkeypatch.delenv("EMAIL_ENABLED", raising=False)

    _install_fake_sendgrid(monkeypatch, raise_on_send=True)
    ok = EmailService.send_email(
        to_email="a@example.com",
        subject="subject",
        html_content="<p>hi</p>",
    )
    assert ok is False


def test_email_service_send_welcome_email_calls_send_email(monkeypatch):
    from app.core.email_service import EmailService

    called = {}

    def fake_send_email(*, to_email, subject, html_content, text_content=None):
        called["to_email"] = to_email
        called["subject"] = subject
        called["html_content"] = html_content
        called["text_content"] = text_content
        return True

    monkeypatch.setattr(EmailService, "send_email", staticmethod(fake_send_email))
    ok = EmailService.send_welcome_email(to_email="a@example.com", username="andy")
    assert ok is True
    assert called["to_email"] == "a@example.com"
    assert called["subject"] == "Welcome to LyfterCook"
    assert "andy" in called["html_content"]


def test_limiter_config_branches(monkeypatch):
    # Reloading not required: we only cover helper functions.
    limiter_mod = importlib.import_module("app.core.limiter")

    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "redis://explicit")
    assert limiter_mod._storage_uri() == "redis://explicit"

    monkeypatch.delenv("RATELIMIT_STORAGE_URI", raising=False)
    monkeypatch.setattr(limiter_mod.settings, "FLASK_ENV", "production")
    monkeypatch.setattr(limiter_mod.settings, "get_redis_url", lambda: "redis://from-settings")
    assert limiter_mod._storage_uri() == "redis://from-settings"

    monkeypatch.setattr(limiter_mod.settings, "FLASK_ENV", "development")
    assert limiter_mod._storage_uri() == "memory://"

    monkeypatch.setenv("TESTING", "true")
    assert limiter_mod._enabled() is False

    monkeypatch.setenv("TESTING", "false")
    monkeypatch.setattr(limiter_mod.settings, "FLASK_ENV", "testing")
    assert limiter_mod._enabled() is False

    monkeypatch.setattr(limiter_mod.settings, "FLASK_ENV", "development")
    assert limiter_mod._enabled() is True
