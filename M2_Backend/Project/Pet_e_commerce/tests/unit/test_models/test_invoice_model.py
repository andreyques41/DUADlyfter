"""
Unit tests for Invoice model.
Tests invoice creation, validation, relationships, and business logic.
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from app.sales.models.invoice import Invoice, InvoiceStatus


@pytest.mark.unit
@pytest.mark.sales
class TestInvoiceStatusModel:
    """Test suite for the InvoiceStatus model."""

    def test_invoice_status_repr(self, db_session):
        """Test that invoice status __repr__ returns a formatted string with creation."""
        status = InvoiceStatus(name='Pending')
        db_session.add(status)
        db_session.commit()

        repr_str = repr(status)
        assert f"InvoiceStatus(id={status.id}" in repr_str
        assert "Pending" in repr_str


@pytest.mark.unit
@pytest.mark.sales
class TestInvoiceModel:
    """Test suite for the Invoice model."""

    def test_invoice_creation_with_valid_data(self, db_session, test_order, test_user, test_invoice_status_pending):
        """Test creating an invoice with valid data."""
        invoice = Invoice(
            order_id=test_order.id,
            user_id=test_user.id,
            invoice_status_id=test_invoice_status_pending.id,
            total_amount=99.99
        )
        db_session.add(invoice)
        db_session.commit()

        assert invoice.id is not None
        assert invoice.order_id == test_order.id
        assert invoice.user_id == test_user.id
        assert invoice.invoice_status_id == test_invoice_status_pending.id
        assert invoice.total_amount == 99.99

    def test_invoice_has_order_relationship(self, db_session, test_order, test_user, test_invoice_status_pending):
        """Test that invoice has a relationship to order."""
        invoice = Invoice(
            order_id=test_order.id,
            user_id=test_user.id,
            invoice_status_id=test_invoice_status_pending.id,
            total_amount=99.99
        )
        db_session.add(invoice)
        db_session.commit()

        # Test relationship
        assert invoice.order is not None
        assert invoice.order.id == test_order.id
        assert invoice.order.cart_id == test_order.cart_id

    def test_invoice_has_user_relationship(self, db_session, test_order, test_user, test_invoice_status_pending):
        """Test that invoice has a relationship to user."""
        invoice = Invoice(
            order_id=test_order.id,
            user_id=test_user.id,
            invoice_status_id=test_invoice_status_pending.id,
            total_amount=99.99
        )
        db_session.add(invoice)
        db_session.commit()

        # Test relationship
        assert invoice.user is not None
        assert invoice.user.id == test_user.id
        assert invoice.user.email == test_user.email

    def test_invoice_has_status_relationship(self, db_session, test_order, test_user, test_invoice_status_pending):
        """Test that invoice has a relationship to status."""
        invoice = Invoice(
            order_id=test_order.id,
            user_id=test_user.id,
            invoice_status_id=test_invoice_status_pending.id,
            total_amount=99.99
        )
        db_session.add(invoice)
        db_session.commit()

        # Test relationship
        assert invoice.status is not None
        assert invoice.status.id == test_invoice_status_pending.id
        assert invoice.status.name == 'Pending'

    def test_invoice_order_unique_constraint(self, db_session, test_order, test_user, test_invoice_status_pending):
        """Test that order_id must be unique (one invoice per order)."""
        # Create first invoice
        invoice1 = Invoice(
            order_id=test_order.id,
            user_id=test_user.id,
            invoice_status_id=test_invoice_status_pending.id,
            total_amount=99.99
        )
        db_session.add(invoice1)
        db_session.commit()

        # Try to create second invoice with same order_id
        invoice2 = Invoice(
            order_id=test_order.id,
            user_id=test_user.id,
            invoice_status_id=test_invoice_status_pending.id,
            total_amount=150.00
        )
        db_session.add(invoice2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_invoice_requires_order_id(self, db_session, test_user, test_invoice_status_pending):
        """Test that order_id is required."""
        invoice = Invoice(
            user_id=test_user.id,
            invoice_status_id=test_invoice_status_pending.id,
            total_amount=99.99
        )
        db_session.add(invoice)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_invoice_with_created_at_timestamp(self, db_session, test_order, test_user, test_invoice_status_pending):
        """Test invoice can have optional created_at timestamp."""
        created_time = datetime.utcnow()
        invoice = Invoice(
            order_id=test_order.id,
            user_id=test_user.id,
            invoice_status_id=test_invoice_status_pending.id,
            total_amount=99.99,
            created_at=created_time
        )
        db_session.add(invoice)
        db_session.commit()

        assert invoice.created_at is not None
        assert isinstance(invoice.created_at, datetime)
        assert invoice.created_at == created_time

    def test_invoice_with_due_date(self, db_session, test_order, test_user, test_invoice_status_pending):
        """Test invoice can have optional due date."""
        due_date = datetime.utcnow() + timedelta(days=30)
        invoice = Invoice(
            order_id=test_order.id,
            user_id=test_user.id,
            invoice_status_id=test_invoice_status_pending.id,
            total_amount=99.99,
            due_date=due_date
        )
        db_session.add(invoice)
        db_session.commit()

        assert invoice.due_date is not None
        assert isinstance(invoice.due_date, datetime)
        assert invoice.due_date == due_date

    def test_invoice_repr_returns_formatted_string(self, db_session, test_order, test_user, test_invoice_status_pending):
        """Test that invoice __repr__ returns a formatted string."""
        invoice = Invoice(
            order_id=test_order.id,
            user_id=test_user.id,
            invoice_status_id=test_invoice_status_pending.id,
            total_amount=99.99
        )
        db_session.add(invoice)
        db_session.commit()

        repr_str = repr(invoice)
        assert f"Invoice(id={invoice.id}" in repr_str
        assert f"order_id={test_order.id}" in repr_str
        assert "99.99" in repr_str
        assert f"status_id={test_invoice_status_pending.id}" in repr_str
