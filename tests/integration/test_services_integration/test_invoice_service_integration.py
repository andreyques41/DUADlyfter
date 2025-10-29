"""
Integration tests for Invoice Service.
Tests the InvoiceService with real database interactions.
"""
import pytest
from datetime import datetime, timedelta
from flask import g
from app.sales.services.invoice_service import InvoiceService
from app.sales.models.invoice import Invoice, InvoiceStatus


@pytest.mark.integration
@pytest.mark.sales
class TestInvoiceCreationIntegration:
    """Integration tests for invoice creation."""
    
    def test_create_invoice_with_order(self, app, integration_db_session, test_user, test_order):
        """Test creating an invoice from an order."""
        # Arrange
        service = InvoiceService()
        invoice_data = {
            'order_id': test_order.id,
            'user_id': test_user.id,
            'total_amount': test_order.total_amount,
            'status': 'pending'
        }
        
        # Act
        with app.app_context():
            g.db = integration_db_session
            invoice = service.create_invoice(**invoice_data)
            # Assert BEFORE commit to avoid detached instance error
            assert invoice is not None
            assert invoice.order_id == test_order.id
            assert invoice.user_id == test_user.id
            assert invoice.total_amount == test_order.total_amount
            assert invoice.status.name == 'pending'  # Correct relationship name
            assert invoice.due_date is not None
            integration_db_session.commit()
    
    def test_create_invoice_sets_due_date(self, app, integration_db_session, test_user, test_order):
        """Test that invoice creation sets a due date."""
        # Arrange
        service = InvoiceService()
        invoice_data = {
            'order_id': test_order.id,
            'user_id': test_user.id,
            'total_amount': 150.00,
            'status': 'pending'
        }
        
        # Act & Assert
        with app.app_context():
            g.db = integration_db_session
            invoice = service.create_invoice(**invoice_data)
            assert invoice.due_date is not None
            # Due date should be in the future
            assert invoice.due_date > datetime.utcnow()
            integration_db_session.commit()
    
    def test_create_invoice_prevents_duplicate(self, app, integration_db_session, test_user, test_order):
        """Test that creating duplicate invoice for same order fails."""
        # Arrange
        service = InvoiceService()
        invoice_data = {
            'order_id': test_order.id,
            'user_id': test_user.id,
            'total_amount': 100.00,
            'status': 'pending'
        }
        
        # Act & Assert
        with app.app_context():
            g.db = integration_db_session
            # First invoice should succeed
            invoice1 = service.create_invoice(**invoice_data)
            integration_db_session.commit()
            assert invoice1 is not None
            
            # Second invoice for same order should fail
            invoice2 = service.create_invoice(**invoice_data)
            assert invoice2 is None


@pytest.mark.integration
@pytest.mark.sales
class TestInvoiceRetrievalIntegration:
    """Integration tests for invoice retrieval."""
    
    def test_get_invoice_by_id(self, app, integration_db_session, test_user, test_order):
        """Test retrieving an invoice by ID."""
        # Arrange - Get IDs before any app context to avoid detached instance errors
        service = InvoiceService()
        user_id = test_user.id
        order_id = test_order.id
        
        invoice_data = {
            'order_id': order_id,
            'user_id': user_id,
            'total_amount': 200.00,
            'status': 'pending'
        }
        
        with app.app_context():
            g.db = integration_db_session
            created_invoice = service.create_invoice(**invoice_data)
            invoice_id = created_invoice.id  # Get ID before commit
            integration_db_session.commit()
        
        # Act
        with app.app_context():
            g.db = integration_db_session
            invoice = service.get_invoice_by_id(invoice_id)
            # Assert inside context to avoid detached instance error
            assert invoice is not None
            assert invoice.id == invoice_id
            assert invoice.order_id == order_id
    
    def test_get_invoice_by_order_id(self, app, integration_db_session, test_user, test_order):
        """Test retrieving an invoice by order ID."""
        # Arrange
        service = InvoiceService()
        invoice_data = {
            'order_id': test_order.id,
            'user_id': test_user.id,
            'total_amount': 300.00,
            'status': 'pending'
        }
        
        with app.app_context():
            g.db = integration_db_session
            service.create_invoice(**invoice_data)
            integration_db_session.commit()
            
            # Act - retrieve in same context
            invoice = service.get_invoice_by_order_id(test_order.id)
            
            # Assert inside context
            assert invoice is not None
            assert invoice.order_id == test_order.id
    
    def test_get_invoices_by_user_id(self, app, integration_db_session, test_user, test_order, test_order2):
        """Test retrieving all invoices for a user."""
        # Arrange - Get IDs before any app context
        service = InvoiceService()
        user_id = test_user.id
        order1_id = test_order.id
        order2_id = test_order2.id
        
        with app.app_context():
            g.db = integration_db_session
            # Create two invoices for the same user
            service.create_invoice(
                order_id=order1_id,
                user_id=user_id,
                total_amount=100.00,
                status='pending'
            )
            service.create_invoice(
                order_id=order2_id,
                user_id=user_id,
                total_amount=200.00,
                status='pending'
            )
            integration_db_session.commit()
            
            # Act & Assert in same context
            invoices = service.get_invoices_by_user_id(user_id)
            assert len(invoices) >= 2
            assert all(inv.user_id == user_id for inv in invoices)


@pytest.mark.integration
@pytest.mark.sales
class TestInvoiceUpdateIntegration:
    """Integration tests for invoice updates."""
    
    def test_update_invoice_status(self, app, integration_db_session, test_user, test_order):
        """Test updating invoice status."""
        # Arrange
        service = InvoiceService()
        invoice_data = {
            'order_id': test_order.id,
            'user_id': test_user.id,
            'total_amount': 150.00,
            'status': 'pending'
        }
        
        with app.app_context():
            g.db = integration_db_session
            invoice = service.create_invoice(**invoice_data)
            invoice_id = invoice.id  # Get ID before commit
            integration_db_session.commit()
        
        # Act
        with app.app_context():
            g.db = integration_db_session
            updated_invoice = service.update_invoice(invoice_id, status='paid')  # Use kwargs
            # Assert inside context
            assert updated_invoice is not None
            assert updated_invoice.status.name == 'paid'  # Correct relationship name
            integration_db_session.commit()
    
    def test_update_invoice_due_date(self, app, integration_db_session, test_user, test_order):
        """Test updating invoice due date."""
        # Arrange
        service = InvoiceService()
        new_due_date = datetime.utcnow() + timedelta(days=60)
        
        with app.app_context():
            g.db = integration_db_session
            invoice = service.create_invoice(
                order_id=test_order.id,
                user_id=test_user.id,
                total_amount=250.00,
                status='pending'
            )
            invoice_id = invoice.id  # Get ID before commit
            integration_db_session.commit()
        
        # Act
        with app.app_context():
            g.db = integration_db_session
            updated_invoice = service.update_invoice(invoice_id, due_date=new_due_date)  # Use kwargs
            # Assert inside context
            assert updated_invoice is not None
            assert updated_invoice.due_date.date() == new_due_date.date()
            integration_db_session.commit()


@pytest.mark.integration
@pytest.mark.sales
class TestInvoiceDeletionIntegration:
    """Integration tests for invoice deletion."""
    
    def test_delete_invoice(self, app, integration_db_session, test_user, test_order):
        """Test deleting an invoice."""
        # Arrange
        service = InvoiceService()
        
        with app.app_context():
            g.db = integration_db_session
            invoice = service.create_invoice(
                order_id=test_order.id,
                user_id=test_user.id,
                total_amount=175.00,
                status='pending'
            )
            integration_db_session.commit()
            invoice_id = invoice.id
        
        # Act
        with app.app_context():
            g.db = integration_db_session
            result = service.delete_invoice(invoice_id)
            integration_db_session.commit()
        
        # Assert
        assert result is True
        
        # Verify deletion
        with app.app_context():
            g.db = integration_db_session
            deleted_invoice = service.get_invoice_by_id(invoice_id)
            assert deleted_invoice is None
    
    def test_delete_nonexistent_invoice(self, app, integration_db_session):
        """Test deleting a non-existent invoice."""
        # Arrange
        service = InvoiceService()
        
        # Act
        with app.app_context():
            g.db = integration_db_session
            result = service.delete_invoice(99999)
        
        # Assert
        assert result is False
