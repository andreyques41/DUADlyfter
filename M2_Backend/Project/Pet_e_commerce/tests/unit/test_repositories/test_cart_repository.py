"""
Unit tests for CartRepository.

Tests all CRUD operations, cart item management, and error handling
for the Cart repository layer without requiring an actual database.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError
from app.sales.repositories.cart_repository import CartRepository
from app.sales.models.cart import Cart, CartItem


class TestCartRepositoryGetByID:
    """Test get_by_id method."""
    
    @patch('app.sales.repositories.cart_repository.get_db')
    def test_get_by_id_success(self, mock_get_db):
        """Should return cart when found."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_cart = Mock(spec=Cart)
        mock_cart.id = 1
        
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_cart
        
        repo = CartRepository()
        
        # Act
        result = repo.get_by_id(1)
        
        # Assert
        assert result == mock_cart
        mock_db.query.assert_called_once_with(Cart)
    
    @patch('app.sales.repositories.cart_repository.get_db')
    def test_get_by_id_not_found(self, mock_get_db):
        """Should return None when cart not found."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        repo = CartRepository()
        
        # Act
        result = repo.get_by_id(999)
        
        # Assert
        assert result is None
    
    @patch('app.sales.repositories.cart_repository.get_db')
    @patch('app.sales.repositories.cart_repository.logger')
    def test_get_by_id_database_error(self, mock_logger, mock_get_db):
        """Should log error and return None on database error."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.side_effect = SQLAlchemyError("Database error")
        
        repo = CartRepository()
        
        # Act
        result = repo.get_by_id(1)
        
        # Assert
        assert result is None
        mock_logger.error.assert_called_once()


class TestCartRepositoryGetByUserID:
    """Test get_by_user_id method."""
    
    @patch('app.sales.repositories.cart_repository.get_db')
    def test_get_by_user_id_success(self, mock_get_db):
        """Should return active cart for user."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_cart = Mock(spec=Cart)
        mock_cart.user_id = 1
        mock_cart.finalized = False
        
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_cart
        
        repo = CartRepository()
        
        # Act
        result = repo.get_by_user_id(1)
        
        # Assert
        assert result == mock_cart
        mock_db.query.return_value.filter_by.assert_called_once_with(user_id=1, finalized=False)
    
    @patch('app.sales.repositories.cart_repository.get_db')
    def test_get_by_user_id_not_found(self, mock_get_db):
        """Should return None when no active cart exists."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        repo = CartRepository()
        
        # Act
        result = repo.get_by_user_id(999)
        
        # Assert
        assert result is None
    
    @patch('app.sales.repositories.cart_repository.get_db')
    @patch('app.sales.repositories.cart_repository.logger')
    def test_get_by_user_id_database_error(self, mock_logger, mock_get_db):
        """Should handle database errors gracefully."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.side_effect = SQLAlchemyError("Connection lost")
        
        repo = CartRepository()
        
        # Act
        result = repo.get_by_user_id(1)
        
        # Assert
        assert result is None
        mock_logger.error.assert_called_once()


class TestCartRepositoryGetAll:
    """Test get_all method."""
    
    @patch('app.sales.repositories.cart_repository.get_db')
    def test_get_all_success(self, mock_get_db):
        """Should return all carts."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_carts = [Mock(spec=Cart) for _ in range(3)]
        mock_db.query.return_value.all.return_value = mock_carts
        
        repo = CartRepository()
        
        # Act
        result = repo.get_all()
        
        # Assert
        assert len(result) == 3
        assert result == mock_carts
    
    @patch('app.sales.repositories.cart_repository.get_db')
    def test_get_all_empty(self, mock_get_db):
        """Should return empty list when no carts exist."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.all.return_value = []
        
        repo = CartRepository()
        
        # Act
        result = repo.get_all()
        
        # Assert
        assert result == []
    
    @patch('app.sales.repositories.cart_repository.get_db')
    @patch('app.sales.repositories.cart_repository.logger')
    def test_get_all_database_error(self, mock_logger, mock_get_db):
        """Should return empty list on database error."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.side_effect = SQLAlchemyError("Query failed")
        
        repo = CartRepository()
        
        # Act
        result = repo.get_all()
        
        # Assert
        assert result == []
        mock_logger.error.assert_called_once()


class TestCartRepositoryCreate:
    """Test create method."""
    
    @patch('app.sales.repositories.cart_repository.get_db')
    def test_create_success(self, mock_get_db):
        """Should create cart and return it with ID."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_cart = Mock(spec=Cart)
        mock_cart.user_id = 1
        
        repo = CartRepository()
        
        # Act
        result = repo.create(mock_cart)
        
        # Assert
        assert result == mock_cart
        mock_db.add.assert_called_once_with(mock_cart)
        mock_db.flush.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_cart)
    
    @patch('app.sales.repositories.cart_repository.get_db')
    @patch('app.sales.repositories.cart_repository.logger')
    def test_create_database_error(self, mock_logger, mock_get_db):
        """Should return None on database error."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.add.side_effect = SQLAlchemyError("Constraint violation")
        
        mock_cart = Mock(spec=Cart)
        mock_cart.user_id = 1
        
        repo = CartRepository()
        
        # Act
        result = repo.create(mock_cart)
        
        # Assert
        assert result is None
        mock_logger.error.assert_called_once()


class TestCartRepositoryUpdate:
    """Test update method."""
    
    @patch('app.sales.repositories.cart_repository.get_db')
    def test_update_attached_cart(self, mock_get_db):
        """Should update cart that's already in session."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_cart = Mock(spec=Cart)
        mock_cart.id = 1
        
        # Simulate cart is in session
        mock_db.__contains__ = Mock(return_value=True)
        
        repo = CartRepository()
        
        # Act
        result = repo.update(mock_cart)
        
        # Assert
        assert result == mock_cart
        mock_db.flush.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_cart)
    
    @patch('app.sales.repositories.cart_repository.get_db')
    def test_update_detached_cart(self, mock_get_db):
        """Should merge detached cart before updating."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_cart = Mock(spec=Cart)
        mock_cart.id = 1
        
        # Simulate cart is not in session
        mock_db.__contains__ = Mock(return_value=False)
        merged_cart = Mock(spec=Cart)
        mock_db.merge.return_value = merged_cart
        
        repo = CartRepository()
        
        # Act
        result = repo.update(mock_cart)
        
        # Assert
        assert result == merged_cart
        mock_db.merge.assert_called_once_with(mock_cart)
        mock_db.flush.assert_called_once()
    
    @patch('app.sales.repositories.cart_repository.get_db')
    @patch('app.sales.repositories.cart_repository.logger')
    def test_update_database_error(self, mock_logger, mock_get_db):
        """Should return None on database error."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.flush.side_effect = SQLAlchemyError("Update failed")
        
        mock_cart = Mock(spec=Cart)
        mock_cart.id = 1
        mock_db.__contains__ = Mock(return_value=True)
        
        repo = CartRepository()
        
        # Act
        result = repo.update(mock_cart)
        
        # Assert
        assert result is None
        mock_logger.error.assert_called_once()


class TestCartRepositoryDelete:
    """Test delete method."""
    
    @patch('app.sales.repositories.cart_repository.get_db')
    def test_delete_success(self, mock_get_db):
        """Should delete cart and return True."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_cart = Mock(spec=Cart)
        mock_cart.id = 1
        
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_cart
        
        repo = CartRepository()
        
        # Act
        result = repo.delete(1)
        
        # Assert
        assert result is True
        mock_db.delete.assert_called_once_with(mock_cart)
    
    @patch('app.sales.repositories.cart_repository.get_db')
    def test_delete_not_found(self, mock_get_db):
        """Should return False when cart doesn't exist."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        repo = CartRepository()
        
        # Act
        result = repo.delete(999)
        
        # Assert
        assert result is False
        mock_db.delete.assert_not_called()
    
    @patch('app.sales.repositories.cart_repository.get_db')
    @patch('app.sales.repositories.cart_repository.logger')
    def test_delete_database_error(self, mock_logger, mock_get_db):
        """Should return False on database error."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.side_effect = SQLAlchemyError("Delete failed")
        
        repo = CartRepository()
        
        # Act
        result = repo.delete(1)
        
        # Assert
        assert result is False
        mock_logger.error.assert_called_once()


class TestCartRepositoryDeleteByUserID:
    """Test delete_by_user_id method."""
    
    @patch('app.sales.repositories.cart_repository.get_db')
    def test_delete_by_user_id_success(self, mock_get_db):
        """Should delete active cart for user."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_cart = Mock(spec=Cart)
        mock_cart.user_id = 1
        
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_cart
        
        repo = CartRepository()
        
        # Act
        result = repo.delete_by_user_id(1)
        
        # Assert
        assert result is True
        mock_db.delete.assert_called_once_with(mock_cart)
        mock_db.flush.assert_called_once()
    
    @patch('app.sales.repositories.cart_repository.get_db')
    def test_delete_by_user_id_not_found(self, mock_get_db):
        """Should return False when no active cart exists."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        repo = CartRepository()
        
        # Act
        result = repo.delete_by_user_id(999)
        
        # Assert
        assert result is False
        mock_db.delete.assert_not_called()
    
    @patch('app.sales.repositories.cart_repository.get_db')
    @patch('app.sales.repositories.cart_repository.logger')
    def test_delete_by_user_id_database_error(self, mock_logger, mock_get_db):
        """Should return False on database error."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.side_effect = SQLAlchemyError("Delete failed")
        
        repo = CartRepository()
        
        # Act
        result = repo.delete_by_user_id(1)
        
        # Assert
        assert result is False
        mock_logger.error.assert_called_once()


class TestCartRepositoryFinalizeCart:
    """Test finalize_cart method."""
    
    @patch('app.sales.repositories.cart_repository.get_db')
    def test_finalize_cart_success(self, mock_get_db):
        """Should mark cart as finalized."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_cart = Mock(spec=Cart)
        mock_cart.id = 1
        mock_cart.finalized = False
        
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_cart
        
        repo = CartRepository()
        
        # Act
        result = repo.finalize_cart(1)
        
        # Assert
        assert result == mock_cart
        assert mock_cart.finalized is True
        mock_db.flush.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_cart)
    
    @patch('app.sales.repositories.cart_repository.get_db')
    def test_finalize_cart_not_found(self, mock_get_db):
        """Should return None when cart doesn't exist."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        repo = CartRepository()
        
        # Act
        result = repo.finalize_cart(999)
        
        # Assert
        assert result is None
    
    @patch('app.sales.repositories.cart_repository.get_db')
    @patch('app.sales.repositories.cart_repository.logger')
    def test_finalize_cart_database_error(self, mock_logger, mock_get_db):
        """Should return None on database error."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_cart = Mock(spec=Cart)
        mock_cart.id = 1
        
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_cart
        mock_db.flush.side_effect = SQLAlchemyError("Finalize failed")
        
        repo = CartRepository()
        
        # Act
        result = repo.finalize_cart(1)
        
        # Assert
        assert result is None
        mock_logger.error.assert_called_once()


class TestCartRepositoryExistsByUserID:
    """Test exists_by_user_id method."""
    
    @patch('app.sales.repositories.cart_repository.get_db')
    def test_exists_by_user_id_true(self, mock_get_db):
        """Should return True when cart exists for user."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = Mock(spec=Cart)
        
        repo = CartRepository()
        
        # Act
        result = repo.exists_by_user_id(1)
        
        # Assert
        assert result is True
    
    @patch('app.sales.repositories.cart_repository.get_db')
    def test_exists_by_user_id_false(self, mock_get_db):
        """Should return False when no cart exists for user."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        repo = CartRepository()
        
        # Act
        result = repo.exists_by_user_id(999)
        
        # Assert
        assert result is False
    
    @patch('app.sales.repositories.cart_repository.get_db')
    @patch('app.sales.repositories.cart_repository.logger')
    def test_exists_by_user_id_database_error(self, mock_logger, mock_get_db):
        """Should return False on database error."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.side_effect = SQLAlchemyError("Check failed")
        
        repo = CartRepository()
        
        # Act
        result = repo.exists_by_user_id(1)
        
        # Assert
        assert result is False
        mock_logger.error.assert_called_once()
