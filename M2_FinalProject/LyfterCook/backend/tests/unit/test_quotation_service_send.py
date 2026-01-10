"""Unit tests for QuotationService.send_quotation_email (GAP-1).

Tests email sending logic for quotations with mocked dependencies.
"""

from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.quotations.services.quotation_service import QuotationService


class TestQuotationServiceSendEmail:
    """Test send_quotation_email method."""

    @pytest.fixture
    def mock_quotation_repo(self):
        """Create a mock quotation repository."""
        return MagicMock()

    @pytest.fixture
    def mock_chef_repo(self):
        """Create a mock chef repository."""
        return MagicMock()

    @pytest.fixture
    def mock_client_repo(self):
        """Create a mock client repository."""
        return MagicMock()

    @pytest.fixture
    def mock_menu_repo(self):
        """Create a mock menu repository."""
        return MagicMock()

    @pytest.fixture
    def mock_dish_repo(self):
        """Create a mock dish repository."""
        return MagicMock()

    @pytest.fixture
    def quotation_service(self, mock_quotation_repo, mock_chef_repo, mock_client_repo, mock_menu_repo, mock_dish_repo):
        """Create QuotationService with mocked repositories."""
        return QuotationService(
            quotation_repository=mock_quotation_repo,
            chef_repository=mock_chef_repo,
            client_repository=mock_client_repo,
            menu_repository=mock_menu_repo,
            dish_repository=mock_dish_repo
        )

    @pytest.fixture
    def test_quotation_with_client(self):
        """Quotation with client that has email."""
        client = SimpleNamespace(
            id=1,
            name="John Doe",
            email="client@example.com",
        )
        chef_user = SimpleNamespace(
            id=1,
            username="chef_mario",
            email="chef@example.com",
        )
        chef = SimpleNamespace(
            id=1,
            user_id=1,
            user=chef_user,
        )
        quotation = SimpleNamespace(
            id=1,
            quotation_number="QT-2026-001",
            client_id=1,
            client=client,
            chef_id=1,
            chef=chef,
            status="draft",
            sent_at=None,
            created_at=datetime(2026, 1, 10, 10, 0, 0),
        )
        return quotation

    @pytest.fixture
    def test_quotation_no_client(self):
        """Quotation without client."""
        chef_user = SimpleNamespace(
            id=1,
            username="chef_mario",
        )
        chef = SimpleNamespace(
            id=1,
            user_id=1,
            user=chef_user,
        )
        quotation = SimpleNamespace(
            id=2,
            quotation_number="QT-2026-002",
            client_id=None,
            client=None,
            chef_id=1,
            chef=chef,
            status="draft",
            sent_at=None,
        )
        return quotation

    def test_send_to_client_email_success(
        self, quotation_service, mock_quotation_repo, test_quotation_with_client
    ):
        """Send using client's email (send_to_client=True)."""
        # Need to mock chef_repository to pass ownership validation
        mock_chef = SimpleNamespace(id=1, user_id=1)
        quotation_service.chef_repository.get_by_user_id.return_value = mock_chef
        quotation_service.quotation_repository.get_by_id.return_value = test_quotation_with_client
        
        sent_time = datetime(2026, 1, 10, 10, 30, 0)
        updated_quotation = SimpleNamespace(
            id=1,
            quotation_number="QT-2026-001",
            client_id=1,
            client=test_quotation_with_client.client,
            chef_id=1,
            chef=test_quotation_with_client.chef,
            status="draft",
            sent_at=sent_time,
            created_at=test_quotation_with_client.created_at,
        )
        mock_quotation_repo.mark_sent.return_value = updated_quotation

        with patch("app.quotations.services.quotation_service.QuotationPdfService.render_pdf") as mock_pdf:
            with patch("app.quotations.services.quotation_service.EmailService.send_quotation_email") as mock_email:
                mock_pdf.return_value = SimpleNamespace(ok=True, pdf_bytes=b"%PDF-1.4 fake", error=None)
                mock_email.return_value = True

                result = quotation_service.send_quotation_email(
                    quotation_id=1,
                    user_id=1,
                    send_to_client=True,
                )

        assert result["sent_to"] == "client@example.com"
        assert result["sent_at"] is not None
        mock_email.assert_called_once()
        call_kwargs = mock_email.call_args.kwargs
        assert call_kwargs["to_email"] == "client@example.com"
        assert call_kwargs["chef_name"] == "chef_mario"
        assert call_kwargs["quotation_number"] == "QT-2026-001"
        assert call_kwargs["pdf_bytes"] == b"%PDF-1.4 fake"

    def test_send_to_custom_email(
        self, quotation_service, mock_quotation_repo, test_quotation_with_client
    ):
        """Send to custom email instead of client email."""
        # Need to mock chef_repository to pass ownership validation
        mock_chef = SimpleNamespace(id=1, user_id=1)
        quotation_service.chef_repository.get_by_user_id.return_value = mock_chef
        quotation_service.quotation_repository.get_by_id.return_value = test_quotation_with_client
        
        sent_time = datetime(2026, 1, 10, 10, 30, 0)
        updated_quotation = SimpleNamespace(
            id=1,
            quotation_number="QT-2026-001",
            client_id=1,
            client=test_quotation_with_client.client,
            chef_id=1,
            chef=test_quotation_with_client.chef,
            status="draft",
            sent_at=sent_time,
            created_at=test_quotation_with_client.created_at,
        )
        mock_quotation_repo.mark_sent.return_value = updated_quotation

        with patch("app.quotations.services.quotation_service.QuotationPdfService.render_pdf") as mock_pdf:
            with patch("app.quotations.services.quotation_service.EmailService.send_quotation_email") as mock_email:
                mock_pdf.return_value = SimpleNamespace(ok=True, pdf_bytes=b"%PDF", error=None)
                mock_email.return_value = True

                result = quotation_service.send_quotation_email(
                    quotation_id=1,
                    user_id=1,
                    custom_email="custom@example.com",
                )

        assert result["sent_to"] == "custom@example.com"
        mock_email.assert_called_once()
        assert mock_email.call_args.kwargs["to_email"] == "custom@example.com"

    def test_send_no_email_available_raises_error(
        self, quotation_service, mock_quotation_repo, test_quotation_no_client
    ):
        """Error if no email available (no client and no custom_email)."""
        # Need to mock chef_repository to pass ownership validation
        mock_chef = SimpleNamespace(id=1, user_id=1)
        quotation_service.chef_repository.get_by_user_id.return_value = mock_chef
        quotation_service.quotation_repository.get_by_id.return_value = test_quotation_no_client

        with pytest.raises(ValueError, match="No email address available"):
            quotation_service.send_quotation_email(
                quotation_id=2,
                user_id=1,
                send_to_client=True,
            )

    def test_send_quotation_not_found_raises_error(
        self, quotation_service, mock_quotation_repo
    ):
        """Error if quotation not found or access denied."""
        mock_quotation_repo.get_quotation_by_id.return_value = None

        with pytest.raises(ValueError, match="Quotation not found"):
            quotation_service.send_quotation_email(
                quotation_id=999,
                user_id=1,
            )

    def test_send_pdf_generation_fails_raises_error(
        self, quotation_service, mock_quotation_repo, test_quotation_with_client
    ):
        """Error if PDF generation fails."""
        # Need to mock chef_repository to pass ownership validation
        mock_chef = SimpleNamespace(id=1, user_id=1)
        quotation_service.chef_repository.get_by_user_id.return_value = mock_chef
        quotation_service.quotation_repository.get_by_id.return_value = test_quotation_with_client

        with patch("app.quotations.services.quotation_service.QuotationPdfService.render_pdf") as mock_pdf:
            mock_pdf.return_value = SimpleNamespace(ok=False, pdf_bytes=None, error="WeasyPrint not available")

            with pytest.raises(ValueError, match="WeasyPrint not available"):
                quotation_service.send_quotation_email(
                    quotation_id=1,
                    user_id=1,
                    send_to_client=True,
                )

    def test_send_email_sending_fails_raises_error(
        self, quotation_service, mock_quotation_repo, test_quotation_with_client
    ):
        """Error if EmailService fails to send."""
        # Need to mock chef_repository to pass ownership validation
        mock_chef = SimpleNamespace(id=1, user_id=1)
        quotation_service.chef_repository.get_by_user_id.return_value = mock_chef
        quotation_service.quotation_repository.get_by_id.return_value = test_quotation_with_client

        with patch("app.quotations.services.quotation_service.QuotationPdfService.render_pdf") as mock_pdf:
            with patch("app.quotations.services.quotation_service.EmailService.send_quotation_email") as mock_email:
                mock_pdf.return_value = SimpleNamespace(ok=True, pdf_bytes=b"%PDF", error=None)
                mock_email.return_value = False

                with pytest.raises(ValueError, match="Failed to send quotation email"):
                    quotation_service.send_quotation_email(
                        quotation_id=1,
                        user_id=1,
                        send_to_client=True,
                    )

    def test_send_marks_sent_at_timestamp(
        self, quotation_service, mock_quotation_repo, test_quotation_with_client
    ):
        """After successful send, sent_at is updated."""
        # Need to mock chef_repository to pass ownership validation
        mock_chef = SimpleNamespace(id=1, user_id=1)
        quotation_service.chef_repository.get_by_user_id.return_value = mock_chef
        quotation_service.quotation_repository.get_by_id.return_value = test_quotation_with_client

        sent_time = datetime(2026, 1, 10, 10, 45, 0)
        updated_quotation = SimpleNamespace(
            id=1,
            quotation_number="QT-2026-001",
            client_id=1,
            client=test_quotation_with_client.client,
            chef_id=1,
            chef=test_quotation_with_client.chef,
            status="draft",
            sent_at=sent_time,
            created_at=test_quotation_with_client.created_at,
        )
        mock_quotation_repo.mark_sent.return_value = updated_quotation

        with patch("app.quotations.services.quotation_service.QuotationPdfService.render_pdf") as mock_pdf:
            with patch("app.quotations.services.quotation_service.EmailService.send_quotation_email") as mock_email:
                mock_pdf.return_value = SimpleNamespace(ok=True, pdf_bytes=b"%PDF", error=None)
                mock_email.return_value = True

                result = quotation_service.send_quotation_email(
                    quotation_id=1,
                    user_id=1,
                    send_to_client=True,
                )

        assert result["sent_at"] == sent_time
        mock_quotation_repo.mark_sent.assert_called_once()

    def test_send_with_custom_message(
        self, quotation_service, mock_quotation_repo, test_quotation_with_client
    ):
        """Send with custom message passed to EmailService."""
        # Need to mock chef_repository to pass ownership validation
        mock_chef = SimpleNamespace(id=1, user_id=1)
        quotation_service.chef_repository.get_by_user_id.return_value = mock_chef
        quotation_service.quotation_repository.get_by_id.return_value = test_quotation_with_client
        
        sent_time = datetime(2026, 1, 10, 10, 30, 0)
        updated_quotation = SimpleNamespace(
            id=1,
            quotation_number="QT-2026-001",
            client_id=1,
            client=test_quotation_with_client.client,
            chef_id=1,
            chef=test_quotation_with_client.chef,
            status="draft",
            sent_at=sent_time,
            created_at=test_quotation_with_client.created_at,
        )
        mock_quotation_repo.mark_sent.return_value = updated_quotation

        with patch("app.quotations.services.quotation_service.QuotationPdfService.render_pdf") as mock_pdf:
            with patch("app.quotations.services.quotation_service.EmailService.send_quotation_email") as mock_email:
                mock_pdf.return_value = SimpleNamespace(ok=True, pdf_bytes=b"%PDF", error=None)
                mock_email.return_value = True

                quotation_service.send_quotation_email(
                    quotation_id=1,
                    user_id=1,
                    send_to_client=True,
                    custom_message="Looking forward to serving you!",
                )

        mock_email.assert_called_once()
        assert mock_email.call_args.kwargs["custom_message"] == "Looking forward to serving you!"
