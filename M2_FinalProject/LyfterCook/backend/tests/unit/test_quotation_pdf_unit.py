"""Unit tests for quotation PDF generation (ADR-003 P0).

Covers:
- app.quotations.services.quotation_pdf_service.QuotationPdfService
- app.quotations.controllers.quotation_controller.QuotationController.download_quotation_pdf

All tests are isolated (no DB).
"""

from __future__ import annotations

import builtins
import sys
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from app.quotations.controllers.quotation_controller import QuotationController
from app.quotations.services.quotation_pdf_service import PdfResult, QuotationPdfService


class TestQuotationPdfService:
    def test_render_html_escapes_fields_and_renders_items(self):
        item = SimpleNamespace(
            item_name='<b>Item</b>',
            description='Desc & more',
            quantity=2,
            unit_price="10.00",
            subtotal="20.00",
        )
        quotation = SimpleNamespace(
            id=1,
            quotation_number='<script>alert(1)</script>',
            status='draft & pending',
            created_at=datetime(2026, 1, 10, 12, 0, 0),
            client=SimpleNamespace(name='Alice <Admin>'),
            items=[item],
            total_amount="20.00",
            notes="Line1\nLine2",
            terms_and_conditions="Use <terms>",
        )

        html_str = QuotationPdfService.render_html(quotation)

        assert "<script>" not in html_str
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html_str
        assert "draft &amp; pending" in html_str
        assert "Alice &lt;Admin&gt;" in html_str
        assert "&lt;b&gt;Item&lt;/b&gt;" in html_str
        assert "Desc &amp; more" in html_str
        assert "2026-01-10 12:00" in html_str
        assert "Line1" in html_str
        assert "Use &lt;terms&gt;" in html_str

    def test_render_html_no_items_renders_placeholder_row(self):
        quotation = SimpleNamespace(
            quotation_number="QT-1",
            status="draft",
            created_at=None,
            client=None,
            items=[],
            total_amount="0.00",
            notes="",
            terms_and_conditions="",
        )

        html_str = QuotationPdfService.render_html(quotation)

        assert "No items" in html_str
        assert "QT-1" in html_str

    def test_render_pdf_weasyprint_unavailable(self, monkeypatch):
        quotation = SimpleNamespace(id=1, quotation_number="QT-1")

        real_import = builtins.__import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "weasyprint":
                raise ImportError("no weasyprint")
            return real_import(name, globals, locals, fromlist, level)

        monkeypatch.setattr(builtins, "__import__", fake_import)

        result = QuotationPdfService.render_pdf(quotation)

        assert result.ok is False
        assert result.pdf_bytes is None
        assert result.error is not None
        assert "WeasyPrint unavailable" in result.error

    def test_render_pdf_success(self, monkeypatch):
        quotation = SimpleNamespace(id=1, quotation_number="QT-1")

        class FakeHTML:
            def __init__(self, string: str):
                self._string = string

            def write_pdf(self):
                return b"%PDF-FAKE"

        fake_weasyprint = SimpleNamespace(HTML=FakeHTML)

        with patch.dict(sys.modules, {"weasyprint": fake_weasyprint}):
            result = QuotationPdfService.render_pdf(quotation)

        assert result.ok is True
        assert result.pdf_bytes == b"%PDF-FAKE"
        assert result.error is None

    def test_render_pdf_write_pdf_fails(self):
        quotation = SimpleNamespace(id=123, quotation_number="QT-123")

        class FakeHTML:
            def __init__(self, string: str):
                self._string = string

            def write_pdf(self):
                raise RuntimeError("boom")

        fake_weasyprint = SimpleNamespace(HTML=FakeHTML)

        with patch.dict(sys.modules, {"weasyprint": fake_weasyprint}):
            result = QuotationPdfService.render_pdf(quotation)

        assert result.ok is False
        assert result.pdf_bytes is None
        assert result.error == "Failed to generate PDF"


class TestQuotationControllerDownloadPdf:
    @pytest.fixture
    def flask_app(self):
        app = Flask(__name__)
        app.config["TESTING"] = True
        return app

    def test_download_pdf_not_found_returns_404(self, flask_app):
        controller = QuotationController()
        service = MagicMock()
        service.get_quotation_by_id.return_value = None

        with flask_app.app_context():
            with patch.object(controller, "_get_service", return_value=service):
                with patch(
                    "app.quotations.controllers.quotation_controller.error_response",
                    return_value=("err", 404),
                ) as mock_err:
                    resp = controller.download_quotation_pdf(quotation_id=1, current_user={"id": 99})

        assert resp == ("err", 404)
        mock_err.assert_called_once()

    def test_download_pdf_generation_unavailable_returns_501(self, flask_app):
        controller = QuotationController()
        service = MagicMock()
        quotation = SimpleNamespace(id=1, quotation_number="QT-1")
        service.get_quotation_by_id.return_value = quotation

        with flask_app.app_context():
            with patch.object(controller, "_get_service", return_value=service):
                with patch(
                    "app.quotations.controllers.quotation_controller.QuotationPdfService.render_pdf",
                    return_value=PdfResult(ok=False, pdf_bytes=None, error="WeasyPrint unavailable"),
                ):
                    with patch(
                        "app.quotations.controllers.quotation_controller.error_response",
                        return_value=("err", 501),
                    ) as mock_err:
                        resp = controller.download_quotation_pdf(quotation_id=1, current_user={"id": 1})

        assert resp == ("err", 501)
        mock_err.assert_called_once()

    def test_download_pdf_success_sets_headers(self, flask_app):
        controller = QuotationController()
        service = MagicMock()
        quotation = SimpleNamespace(id=7, quotation_number="QT-007")
        service.get_quotation_by_id.return_value = quotation

        with flask_app.app_context():
            with patch.object(controller, "_get_service", return_value=service):
                with patch(
                    "app.quotations.controllers.quotation_controller.QuotationPdfService.render_pdf",
                    return_value=PdfResult(ok=True, pdf_bytes=b"%PDF", error=None),
                ):
                    resp = controller.download_quotation_pdf(quotation_id=7, current_user={"id": 1})

        assert resp.status_code == 200
        assert resp.mimetype == "application/pdf"
        assert resp.data == b"%PDF"
        assert "attachment;" in resp.headers.get("Content-Disposition", "")
        assert "quotation-QT-007.pdf" in resp.headers.get("Content-Disposition", "")

    def test_download_pdf_unexpected_exception_returns_500(self, flask_app):
        controller = QuotationController()

        with flask_app.app_context():
            with patch.object(controller, "_get_service", side_effect=RuntimeError("boom")):
                with patch(
                    "app.quotations.controllers.quotation_controller.error_response",
                    return_value=("err", 500),
                ) as mock_err:
                    resp = controller.download_quotation_pdf(quotation_id=1, current_user={"id": 1})

        assert resp == ("err", 500)
        mock_err.assert_called_once()
