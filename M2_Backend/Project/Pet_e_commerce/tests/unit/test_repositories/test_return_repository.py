"""
Unit tests for ReturnRepository.

Tests all CRUD operations, filtering, status management, and error handling.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError
from app.sales.repositories.return_repository import ReturnRepository
from app.sales.models.returns import Return, ReturnStatus


class TestReturnRepositoryBasicOperations:
    """Test basic CRUD operations."""
    
    @patch('app.sales.repositories.return_repository.get_db')
    def test_get_by_id_success(self, mock_get_db):
        """Should return return object when found."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_return = Mock(spec=Return)
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_return
        
        repo = ReturnRepository()
        result = repo.get_by_id(1)
        
        assert result == mock_return
    
    @patch('app.sales.repositories.return_repository.get_db')
    def test_get_by_id_not_found(self, mock_get_db):
        """Should return None when not found."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        repo = ReturnRepository()
        result = repo.get_by_id(999)
        
        assert result is None
    
    @patch('app.sales.repositories.return_repository.get_db')
    @patch('app.sales.repositories.return_repository.logger')
    def test_get_by_id_database_error(self, mock_logger, mock_get_db):
        """Should handle database errors."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.side_effect = SQLAlchemyError("DB error")
        
        repo = ReturnRepository()
        result = repo.get_by_id(1)
        
        assert result is None
        mock_logger.error.assert_called_once()
    
    @patch('app.sales.repositories.return_repository.get_db')
    def test_get_by_order_id_success(self, mock_get_db):
        """Should return returns for order."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_returns = [Mock(spec=Return), Mock(spec=Return)]
        mock_db.query.return_value.filter_by.return_value.all.return_value = mock_returns
        
        repo = ReturnRepository()
        result = repo.get_by_order_id(1)
        
        assert len(result) == 2
    
    @patch('app.sales.repositories.return_repository.get_db')
    def test_get_by_user_id_success(self, mock_get_db):
        """Should return returns for user."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_returns = [Mock(spec=Return), Mock(spec=Return)]
        mock_db.query.return_value.filter_by.return_value.all.return_value = mock_returns
        
        repo = ReturnRepository()
        result = repo.get_by_user_id(1)
        
        assert len(result) == 2
    
    @patch('app.sales.repositories.return_repository.get_db')
    def test_get_all_success(self, mock_get_db):
        """Should return all returns."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_returns = [Mock(spec=Return) for _ in range(5)]
        mock_db.query.return_value.all.return_value = mock_returns
        
        repo = ReturnRepository()
        result = repo.get_all()
        
        assert len(result) == 5
    
    @patch('app.sales.repositories.return_repository.get_db')
    @patch('app.sales.repositories.return_repository.logger')
    def test_get_all_database_error(self, mock_logger, mock_get_db):
        """Should return empty list on error."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.side_effect = SQLAlchemyError("Error")
        
        repo = ReturnRepository()
        result = repo.get_all()
        
        assert result == []


class TestReturnRepositoryFiltering:
    """Test filtering operations."""
    
    @patch('app.sales.repositories.return_repository.get_db')
    def test_get_by_filters_with_user_id(self, mock_get_db):
        """Should filter by user_id."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_query = mock_db.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [Mock(spec=Return)]
        
        repo = ReturnRepository()
        result = repo.get_by_filters({'user_id': 1})
        
        assert len(result) == 1
    
    @patch('app.sales.repositories.return_repository.get_db')
    def test_get_by_filters_with_status(self, mock_get_db):
        """Should filter by status_id."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_query = mock_db.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [Mock(spec=Return)]
        
        repo = ReturnRepository()
        result = repo.get_by_filters({'status_id': 2})
        
        assert len(result) == 1
    
    @patch('app.sales.repositories.return_repository.get_db')
    def test_get_by_filters_with_order_id(self, mock_get_db):
        """Should filter by order_id."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_query = mock_db.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [Mock(spec=Return)]
        
        repo = ReturnRepository()
        result = repo.get_by_filters({'order_id': 5})
        
        assert len(result) == 1
    
    @patch('app.sales.repositories.return_repository.get_db')
    @patch('app.sales.repositories.return_repository.logger')
    def test_get_by_filters_database_error(self, mock_logger, mock_get_db):
        """Should return empty list on error."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.side_effect = SQLAlchemyError("Filter error")
        
        repo = ReturnRepository()
        result = repo.get_by_filters({'user_id': 1})
        
        assert result == []


class TestReturnRepositoryCreateUpdateDelete:
    """Test create, update, and delete operations."""
    
    @patch('app.sales.repositories.return_repository.get_db')
    def test_create_success(self, mock_get_db):
        """Should create return successfully."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_return = Mock(spec=Return)
        
        repo = ReturnRepository()
        result = repo.create(mock_return)
        
        assert result == mock_return
        mock_db.add.assert_called_once_with(mock_return)
        mock_db.flush.assert_called_once()
    
    @patch('app.sales.repositories.return_repository.get_db')
    @patch('app.sales.repositories.return_repository.logger')
    def test_create_database_error(self, mock_logger, mock_get_db):
        """Should return None on error."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.add.side_effect = SQLAlchemyError("Create failed")
        mock_return = Mock(spec=Return)
        
        repo = ReturnRepository()
        result = repo.create(mock_return)
        
        assert result is None
    
    @patch('app.sales.repositories.return_repository.get_db')
    def test_update_success(self, mock_get_db):
        """Should update return successfully."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_return = Mock(spec=Return)
        mock_db.merge.return_value = mock_return
        
        repo = ReturnRepository()
        result = repo.update(mock_return)
        
        assert result == mock_return
        mock_db.merge.assert_called_once()
    
    @patch('app.sales.repositories.return_repository.get_db')
    @patch('app.sales.repositories.return_repository.logger')
    def test_update_database_error(self, mock_logger, mock_get_db):
        """Should return None on error."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.merge.side_effect = SQLAlchemyError("Update failed")
        mock_return = Mock(spec=Return)
        
        repo = ReturnRepository()
        result = repo.update(mock_return)
        
        assert result is None
    
    @patch('app.sales.repositories.return_repository.get_db')
    def test_delete_success(self, mock_get_db):
        """Should delete return successfully."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_return = Mock(spec=Return)
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_return
        
        repo = ReturnRepository()
        result = repo.delete(1)
        
        assert result is True
        mock_db.delete.assert_called_once()
    
    @patch('app.sales.repositories.return_repository.get_db')
    def test_delete_not_found(self, mock_get_db):
        """Should return False when not found."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        repo = ReturnRepository()
        result = repo.delete(999)
        
        assert result is False
    
    @patch('app.sales.repositories.return_repository.get_db')
    @patch('app.sales.repositories.return_repository.logger')
    def test_delete_database_error(self, mock_logger, mock_get_db):
        """Should return False on error."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.side_effect = SQLAlchemyError("Delete failed")
        
        repo = ReturnRepository()
        result = repo.delete(1)
        
        assert result is False


class TestReturnRepositoryStatusOperations:
    """Test status-related operations."""
    
    @patch('app.sales.repositories.return_repository.get_db')
    def test_get_status_by_name_success(self, mock_get_db):
        """Should return status when found."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_status = Mock(spec=ReturnStatus)
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_status
        
        repo = ReturnRepository()
        result = repo.get_status_by_name('pending')
        
        assert result == mock_status
    
    @patch('app.sales.repositories.return_repository.get_db')
    def test_get_status_by_name_not_found(self, mock_get_db):
        """Should return None when not found."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        repo = ReturnRepository()
        result = repo.get_status_by_name('invalid')
        
        assert result is None
    
    @patch('app.sales.repositories.return_repository.get_db')
    @patch('app.sales.repositories.return_repository.logger')
    def test_get_status_by_name_database_error(self, mock_logger, mock_get_db):
        """Should return None on error."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.side_effect = SQLAlchemyError("Status error")
        
        repo = ReturnRepository()
        result = repo.get_status_by_name('pending')
        
        assert result is None
