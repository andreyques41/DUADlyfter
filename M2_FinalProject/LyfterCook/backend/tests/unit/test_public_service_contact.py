"""Unit tests for PublicService.submit_contact_form (GAP-2).

Tests contact form submission logic with mocked dependencies.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.public.services.public_service import PublicService


class TestPublicServiceContactForm:
    """Test submit_contact_form method."""

    @pytest.fixture
    def public_service(self):
        """Create PublicService with mocked repository."""
        service = PublicService()
        service.repository = MagicMock()  # Replace with mock
        return service

    @pytest.fixture
    def test_chef_with_email(self):
        """Chef with user that has email."""
        user = SimpleNamespace(
            id=1,
            username="chef_mario",
            email="chef@example.com",
        )
        chef = SimpleNamespace(
            id=1,
            user_id=1,
            user=user,
            specialty="Italian",
            location="NYC",
        )
        return chef

    @pytest.fixture
    def test_chef_no_email(self):
        """Chef with user but no email."""
        user = SimpleNamespace(
            id=2,
            username="chef_no_email",
            email=None,
        )
        chef = SimpleNamespace(
            id=2,
            user_id=2,
            user=user,
        )
        return chef

    @pytest.fixture
    def test_chef_no_user(self):
        """Chef without user."""
        chef = SimpleNamespace(
            id=3,
            user_id=None,
            user=None,
        )
        return chef

    @pytest.fixture
    def valid_contact_data(self):
        """Valid contact form data."""
        return {
            "chef_id": 1,
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "+1-555-1234",
            "message": "I would like to book you for my wedding reception.",
        }

    def test_submit_contact_chef_not_found(
        self, public_service, valid_contact_data
    ):
        """Chef not found returns 404 error."""
        public_service.repository.get_chef_by_id.return_value = None

        result = public_service.submit_contact_form(valid_contact_data)

        assert result["ok"] is False
        assert result["status"] == 404
        assert "not found" in result["error"].lower()

    def test_submit_contact_chef_no_email(
        self, public_service, test_chef_no_email, valid_contact_data
    ):
        """Chef without email returns 400 error."""
        public_service.repository.get_chef_by_id.return_value = test_chef_no_email

        result = public_service.submit_contact_form(valid_contact_data)

        assert result["ok"] is False
        assert result["status"] == 400
        assert "email not available" in result["error"].lower()

    def test_submit_contact_chef_no_user(
        self, public_service, test_chef_no_user, valid_contact_data
    ):
        """Chef without user object returns 400 error."""
        public_service.repository.get_chef_by_id.return_value = test_chef_no_user

        result = public_service.submit_contact_form(valid_contact_data)

        assert result["ok"] is False
        assert result["status"] == 400
        assert "email not available" in result["error"].lower()

    def test_submit_contact_success(
        self, public_service, test_chef_with_email, valid_contact_data
    ):
        """Successful contact form submission."""
        public_service.repository.get_chef_by_id.return_value = test_chef_with_email

        with patch("app.public.services.public_service.EmailService.send_contact_notification") as mock_email:
            mock_email.return_value = True

            result = public_service.submit_contact_form(valid_contact_data)

        assert result["ok"] is True
        mock_email.assert_called_once()
        call_kwargs = mock_email.call_args.kwargs
        assert call_kwargs["chef_email"] == "chef@example.com"
        assert call_kwargs["chef_name"] == "chef_mario"
        assert call_kwargs["visitor_name"] == "Jane Doe"
        assert call_kwargs["visitor_email"] == "jane@example.com"
        assert call_kwargs["visitor_phone"] == "+1-555-1234"
        assert call_kwargs["message"] == "I would like to book you for my wedding reception."

    def test_submit_contact_email_sending_fails(
        self, public_service, test_chef_with_email, valid_contact_data
    ):
        """Email sending failure returns 500 error."""
        public_service.repository.get_chef_by_id.return_value = test_chef_with_email

        with patch("app.public.services.public_service.EmailService.send_contact_notification") as mock_email:
            mock_email.return_value = False

            result = public_service.submit_contact_form(valid_contact_data)

        assert result["ok"] is False
        assert result["status"] == 500
        assert "failed to send" in result["error"].lower()

    def test_submit_contact_without_phone(
        self, public_service, test_chef_with_email
    ):
        """Contact form without phone field still succeeds."""
        data = {
            "chef_id": 1,
            "name": "John Smith",
            "email": "john@example.com",
            "message": "Quick question about your services.",
        }
        public_service.repository.get_chef_by_id.return_value = test_chef_with_email

        with patch("app.public.services.public_service.EmailService.send_contact_notification") as mock_email:
            mock_email.return_value = True

            result = public_service.submit_contact_form(data)

        assert result["ok"] is True
        mock_email.assert_called_once()
        call_kwargs = mock_email.call_args.kwargs
        assert call_kwargs["visitor_phone"] is None

    def test_submit_contact_passes_all_visitor_data(
        self, public_service, test_chef_with_email
    ):
        """All visitor data is passed to EmailService."""
        data = {
            "chef_id": 1,
            "name": "Alice Wonder",
            "email": "alice@example.com",
            "phone": "+44-20-1234-5678",
            "message": "Interested in catering for 50 people.",
        }
        public_service.repository.get_chef_by_id.return_value = test_chef_with_email

        with patch("app.public.services.public_service.EmailService.send_contact_notification") as mock_email:
            mock_email.return_value = True

            result = public_service.submit_contact_form(data)

        assert result["ok"] is True
        call_kwargs = mock_email.call_args.kwargs
        assert call_kwargs["visitor_name"] == "Alice Wonder"
        assert call_kwargs["visitor_email"] == "alice@example.com"
        assert call_kwargs["visitor_phone"] == "+44-20-1234-5678"
        assert "50 people" in call_kwargs["message"]
