"""Unit tests for Calendar (.ics) export (ADR-003 P0).

Covers:
- app.appointments.services.calendar_ics_service.CalendarIcsService
- app.appointments.controllers.appointment_controller.AppointmentController.download_appointment_ics

All tests are isolated (no DB).
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from app.appointments.controllers.appointment_controller import AppointmentController
from app.appointments.services.calendar_ics_service import CalendarIcsService, _ics_escape


class TestCalendarIcsService:
    def test_ics_escape_rfc5545_basics(self):
        raw = "a\\b;c,d\nnext"
        escaped = _ics_escape(raw)
        assert escaped == "a\\\\b\\;c\\,d\\nnext"

    def test_appointment_to_event_requires_scheduled_at(self):
        appointment = SimpleNamespace(id=1, scheduled_at=None)
        with pytest.raises(ValueError, match="scheduled_at"):
            CalendarIcsService.appointment_to_event(appointment)

    def test_appointment_to_event_builds_expected_fields_and_to_ics(self):
        appointment = SimpleNamespace(
            id=123,
            scheduled_at=datetime(2026, 1, 10, 12, 0, 0),  # naive -> treated as UTC
            duration_minutes=90,
            title="Tasting; Session, 1",
            description="Bring samples",
            meeting_url="https://meet.example.com/abc",
            location="Kitchen, Main",
        )

        event = CalendarIcsService.appointment_to_event(appointment, backend_url="http://localhost:5000")

        assert event.uid == "appointment-123@lyftercook"
        assert event.dtstart_utc.tzinfo == timezone.utc
        assert event.dtstart_utc.strftime("%Y%m%dT%H%M%SZ") == "20260110T120000Z"
        assert event.dtend_utc.strftime("%Y%m%dT%H%M%SZ") == "20260110T133000Z"
        assert event.url == "http://localhost:5000/appointments/123"

        ics = event.to_ics()
        assert "BEGIN:VCALENDAR" in ics
        assert "BEGIN:VEVENT" in ics
        assert "UID:appointment-123@lyftercook" in ics
        assert "DTSTART:20260110T120000Z" in ics
        assert "DTEND:20260110T133000Z" in ics
        # Escaping in SUMMARY/LOCATION
        assert "SUMMARY:Tasting\\; Session\\, 1" in ics
        assert "LOCATION:Kitchen\\, Main" in ics
        # Description includes meeting url and newlines are escaped
        assert "DESCRIPTION:Bring samples\\\\n\\\\nMeeting: https://meet.example.com/abc" in ics
        assert "URL:http://localhost:5000/appointments/123" in ics


class TestAppointmentControllerDownloadIcs:
    @pytest.fixture
    def flask_app(self):
        app = Flask(__name__)
        app.config["TESTING"] = True
        return app

    def test_download_ics_not_found_returns_404(self, flask_app):
        controller = AppointmentController()
        service = MagicMock()
        service.get_appointment_by_id.return_value = None

        with flask_app.app_context():
            with patch.object(controller, "_get_service", return_value=service):
                with patch(
                    "app.appointments.controllers.appointment_controller.error_response",
                    return_value=("err", 404),
                ) as mock_err:
                    resp = controller.download_appointment_ics(appointment_id=1, current_user={"id": 1})

        assert resp == ("err", 404)
        mock_err.assert_called_once()

    def test_download_ics_success_sets_headers_and_mimetype(self, flask_app, monkeypatch):
        controller = AppointmentController()
        service = MagicMock()
        appointment = SimpleNamespace(id=5)
        service.get_appointment_by_id.return_value = appointment

        fake_event = SimpleNamespace(to_ics=lambda: "BEGIN:VCALENDAR\r\nEND:VCALENDAR\r\n")

        from config import settings
        monkeypatch.setattr(settings, "BACKEND_URL", "http://localhost:5000")

        with flask_app.app_context():
            with patch.object(controller, "_get_service", return_value=service):
                with patch(
                    "app.appointments.controllers.appointment_controller.CalendarIcsService.appointment_to_event",
                    return_value=fake_event,
                ):
                    resp = controller.download_appointment_ics(appointment_id=5, current_user={"id": 1})

        assert resp.status_code == 200
        assert resp.mimetype.startswith("text/calendar")
        assert "appointment-5.ics" in resp.headers.get("Content-Disposition", "")
        assert "BEGIN:VCALENDAR" in resp.get_data(as_text=True)

    def test_download_ics_value_error_returns_400(self, flask_app):
        controller = AppointmentController()
        service = MagicMock()
        appointment = SimpleNamespace(id=5)
        service.get_appointment_by_id.return_value = appointment

        with flask_app.app_context():
            with patch.object(controller, "_get_service", return_value=service):
                with patch(
                    "app.appointments.controllers.appointment_controller.CalendarIcsService.appointment_to_event",
                    side_effect=ValueError("bad appointment"),
                ):
                    with patch(
                        "app.appointments.controllers.appointment_controller.error_response",
                        return_value=("err", 400),
                    ) as mock_err:
                        resp = controller.download_appointment_ics(appointment_id=5, current_user={"id": 1})

        assert resp == ("err", 400)
        mock_err.assert_called_once()

    def test_download_ics_unexpected_exception_returns_500(self, flask_app):
        controller = AppointmentController()

        with flask_app.app_context():
            with patch.object(controller, "_get_service", side_effect=RuntimeError("boom")):
                with patch(
                    "app.appointments.controllers.appointment_controller.error_response",
                    return_value=("err", 500),
                ) as mock_err:
                    resp = controller.download_appointment_ics(appointment_id=1, current_user={"id": 1})

        assert resp == ("err", 500)
        mock_err.assert_called_once()
