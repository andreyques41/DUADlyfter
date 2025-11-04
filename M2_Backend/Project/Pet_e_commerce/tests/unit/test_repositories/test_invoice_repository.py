"""
Unit tests for InvoiceRepository.

Tests all CRUD operations, filtering, status management, and error handling.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError
from app.sales.repositories.invoice_repository import InvoiceRepository
from app.sales.models.invoice import Invoice, InvoiceStatus


class TestInvoiceRepositoryBasicOperations:
    """Test basic CRUD operations."""
    
    @patch('app.sales.repositories.invoice_repository.get_db')
    def test_get_by_id_success(self, mock_get_db):
        """Should return invoice when found."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_invoice = Mock(spec=Invoice)
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_invoice
        
        repo = InvoiceRepository()
        result = repo.get_by_id(1)
        
        assert result == mock_invoice
    
    @patch('app.sales.repositories.invoice_repository.get_db')
    def test_get_by_id_not_found(self, mock_get_db):
        """Should return None when not found."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        repo = InvoiceRepository()
        result = repo.get_by_id(999)
        
        assert result is None
    
    @patch('app.sales.repositories.invoice_repository.get_db')
    @patch('app.sales.repositories.invoice_repository.logger')
    def test_get_by_id_database_error(self, mock_logger, mock_get_db):
        """Should handle database errors."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.side_effect = SQLAlchemyError("DB error")
        
        repo = InvoiceRepository()
        result = repo.get_by_id(1)
        
        assert result is None
        mock_logger.error.assert_called_once()
    
    @patch('app.sales.repositories.invoice_repository.get_db')
    def test_get_by_order_id_success(self, mock_get_db):
        """Should return invoice for order."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_invoice = Mock(spec=Invoice)
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_invoice
        
        repo = InvoiceRepository()
        result = repo.get_by_order_id(1)
        
        assert result == mock_invoice
    
    @patch('app.sales.repositories.invoice_repository.get_db')
    def test_get_by_user_id_success(self, mock_get_db):
        """Should return invoices for user."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_invoices = [Mock(spec=Invoice), Mock(spec=Invoice)]
        mock_db.query.return_value.filter_by.return_value.all.return_value = mock_invoices
        
        repo = InvoiceRepository()
        result = repo.get_by_user_id(1)
        
        assert len(result) == 2
    
    @patch('app.sales.repositories.invoice_repository.get_db')
    def test_get_all_success(self, mock_get_db):
        """Should return all invoices."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_invoices = [Mock(spec=Invoice) for _ in range(5)]
        mock_db.query.return_value.all.return_value = mock_invoices
        
        repo = InvoiceRepository()
        result = repo.get_all()
        
        assert len(result) == 5


class TestInvoiceRepositoryFiltering:
    """Test filtering operations."""
    
    @patch('app.sales.repositories.invoice_repository.get_db')
    def test_get_by_filters_with_user_id(self, mock_get_db):
        """Should filter by user_id."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_query = mock_db.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [Mock(spec=Invoice)]
        
        repo = InvoiceRepository()
        result = repo.get_by_filters({'user_id': 1})
        
        assert len(result) == 1
    
    @patch('app.sales.repositories.invoice_repository.get_db')
    def test_get_by_filters_with_status(self, mock_get_db):
        """Should filter by status_id."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_query = mock_db.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [Mock(spec=Invoice)]
        
        repo = InvoiceRepository()
        result = repo.get_by_filters({'status_id': 2})
        
        assert len(result) == 1
    
    @patch('app.sales.repositories.invoice_repository.get_db')
    def test_get_by_filters_with_overdue(self, mock_get_db):
        """Should filter by overdue status."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_query = mock_db.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [Mock(spec=Invoice)]
        
        repo = InvoiceRepository()
        result = repo.get_by_filters({'overdue': True})
        
        assert len(result) == 1


class TestInvoiceRepositoryCreateUpdateDelete:
    """Test create, update, and delete operations."""
    
    @patch('app.sales.repositories.invoice_repository.get_db')
    def test_create_success(self, mock_get_db):
        """Should create invoice successfully."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_invoice = Mock(spec=Invoice)
        
        repo = InvoiceRepository()
        result = repo.create(mock_invoice)
        
        assert result == mock_invoice
        mock_db.add.assert_called_once_with(mock_invoice)
        mock_db.flush.assert_called_once()
    
    @patch('app.sales.repositories.invoice_repository.get_db')
    def test_update_success(self, mock_get_db):
        """Should update invoice successfully."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_invoice = Mock(spec=Invoice)
        mock_db.merge.return_value = mock_invoice
        
        repo = InvoiceRepository()
        result = repo.update(mock_invoice)
        
        assert result == mock_invoice
        mock_db.merge.assert_called_once()
    
    @patch('app.sales.repositories.invoice_repository.get_db')
    def test_delete_success(self, mock_get_db):
        """Should delete invoice successfully."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_invoice = Mock(spec=Invoice)
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_invoice
        
        repo = InvoiceRepository()
        result = repo.delete(1)
        
        assert result is True
        mock_db.delete.assert_called_once()
    
    @patch('app.sales.repositories.invoice_repository.get_db')
    def test_delete_not_found(self, mock_get_db):
        """Should return False when not found."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        repo = InvoiceRepository()
        result = repo.delete(999)
        
        assert result is False


class TestInvoiceRepositoryStatusOperations:
    """Test status-related operations."""
    
    @patch('app.sales.repositories.invoice_repository.get_db')
    def test_get_status_by_name_success(self, mock_get_db):
        """Should return status when found."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_status = Mock(spec=InvoiceStatus)
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_status
        
        repo = InvoiceRepository()
        result = repo.get_status_by_name('pending')
        
        assert result == mock_status
    
    @patch('app.sales.repositories.invoice_repository.get_db')
    def test_get_status_by_name_not_found(self, mock_get_db):
        """Should return None when not found."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        repo = InvoiceRepository()
        result = repo.get_status_by_name('invalid')
        
        assert result is None
    
    @patch('app.sales.repositories.invoice_repository.get_db')
    def test_exists_by_order_id_true(self, mock_get_db):
        """Should return True when invoice exists for order."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = Mock(spec=Invoice)
        
        repo = InvoiceRepository()
        result = repo.exists_by_order_id(1)
        
        assert result is True
    
    @patch('app.sales.repositories.invoice_repository.get_db')
    def test_exists_by_order_id_false(self, mock_get_db):
        """Should return False when no invoice exists."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        repo = InvoiceRepository()
        result = repo.exists_by_order_id(999)
        
        assert result is False
