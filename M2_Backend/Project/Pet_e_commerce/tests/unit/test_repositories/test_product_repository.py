"""
Unit tests for ProductRepository.

Tests all CRUD operations, filtering, search functionality, and error handling
for the Product repository layer without requiring an actual database.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError
from app.products.repositories.product_repository import ProductRepository
from app.products.models.product import Product, ProductCategory, PetType


class TestProductRepositoryGetByID:
    """Test get_by_id method."""
    
    @patch('app.products.repositories.product_repository.get_db')
    def test_get_by_id_success(self, mock_get_db):
        """Should return product when found."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_product = Mock(spec=Product)
        mock_product.id = 1
        mock_product.name = 'Test Product'
        
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_product
        
        repo = ProductRepository()
        
        # Act
        result = repo.get_by_id(1)
        
        # Assert
        assert result == mock_product
        mock_db.query.assert_called_once_with(Product)
    
    @patch('app.products.repositories.product_repository.get_db')
    def test_get_by_id_not_found(self, mock_get_db):
        """Should return None when product not found."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        repo = ProductRepository()
        
        # Act
        result = repo.get_by_id(999)
        
        # Assert
        assert result is None
    
    @patch('app.products.repositories.product_repository.get_db')
    @patch('app.products.repositories.product_repository.logger')
    def test_get_by_id_database_error(self, mock_logger, mock_get_db):
        """Should log error and return None on database error."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.side_effect = SQLAlchemyError("Database error")
        
        repo = ProductRepository()
        
        # Act
        result = repo.get_by_id(1)
        
        # Assert
        assert result is None
        mock_logger.error.assert_called_once()


class TestProductRepositoryGetBySKU:
    """Test get_by_sku method."""
    
    @patch('app.products.repositories.product_repository.get_db')
    def test_get_by_sku_success(self, mock_get_db):
        """Should return product when SKU exists."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_product = Mock(spec=Product)
        mock_product.sku = 'PROD-001'
        
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_product
        
        repo = ProductRepository()
        
        # Act
        result = repo.get_by_sku('PROD-001')
        
        # Assert
        assert result == mock_product
        mock_db.query.return_value.filter_by.assert_called_once_with(sku='PROD-001')
    
    @patch('app.products.repositories.product_repository.get_db')
    def test_get_by_sku_not_found(self, mock_get_db):
        """Should return None when SKU doesn't exist."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        repo = ProductRepository()
        
        # Act
        result = repo.get_by_sku('INVALID')
        
        # Assert
        assert result is None


class TestProductRepositoryGetAll:
    """Test get_all method."""
    
    @patch('app.products.repositories.product_repository.get_db')
    def test_get_all_success(self, mock_get_db):
        """Should return all products."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_products = [Mock(spec=Product) for _ in range(5)]
        mock_db.query.return_value.all.return_value = mock_products
        
        repo = ProductRepository()
        
        # Act
        result = repo.get_all()
        
        # Assert
        assert len(result) == 5
        assert result == mock_products
    
    @patch('app.products.repositories.product_repository.get_db')
    def test_get_all_empty(self, mock_get_db):
        """Should return empty list when no products exist."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.all.return_value = []
        
        repo = ProductRepository()
        
        # Act
        result = repo.get_all()
        
        # Assert
        assert result == []


class TestProductRepositoryGetByFilters:
    """Test get_by_filters method."""
    
    @patch('app.products.repositories.product_repository.get_db')
    def test_filter_by_category(self, mock_get_db):
        """Should filter products by category_id."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_query = mock_db.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [Mock(spec=Product)]
        
        repo = ProductRepository()
        
        # Act
        result = repo.get_by_filters({'category_id': 1})
        
        # Assert
        assert len(result) == 1
        mock_query.filter.assert_called()
    
    @patch('app.products.repositories.product_repository.get_db')
    def test_filter_by_pet_type(self, mock_get_db):
        """Should filter products by pet_type_id."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_query = mock_db.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [Mock(spec=Product)]
        
        repo = ProductRepository()
        
        # Act
        result = repo.get_by_filters({'pet_type_id': 2})
        
        # Assert
        assert len(result) == 1
    
    @patch('app.products.repositories.product_repository.get_db')
    def test_filter_by_brand(self, mock_get_db):
        """Should filter products by brand using ILIKE."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_query = mock_db.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [Mock(spec=Product)]
        
        repo = ProductRepository()
        
        # Act
        result = repo.get_by_filters({'brand': 'Purina'})
        
        # Assert
        assert len(result) == 1
    
    @patch('app.products.repositories.product_repository.get_db')
    def test_filter_by_min_stock(self, mock_get_db):
        """Should filter products by minimum stock quantity."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_query = mock_db.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [Mock(spec=Product)]
        
        repo = ProductRepository()
        
        # Act
        result = repo.get_by_filters({'min_stock': 10})
        
        # Assert
        assert len(result) == 1
    
    @patch('app.products.repositories.product_repository.get_db')
    def test_filter_by_is_active(self, mock_get_db):
        """Should filter products by active status."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_query = mock_db.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [Mock(spec=Product)]
        
        repo = ProductRepository()
        
        # Act
        result = repo.get_by_filters({'is_active': True})
        
        # Assert
        assert len(result) == 1
    
    @patch('app.products.repositories.product_repository.get_db')
    def test_filter_by_search_term(self, mock_get_db):
        """Should search in description and brand fields."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_query = mock_db.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [Mock(spec=Product)]
        
        repo = ProductRepository()
        
        # Act
        result = repo.get_by_filters({'search': 'dog food'})
        
        # Assert
        assert len(result) == 1
    
    @patch('app.products.repositories.product_repository.get_db')
    def test_filter_multiple_criteria(self, mock_get_db):
        """Should apply multiple filters together."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_query = mock_db.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [Mock(spec=Product)]
        
        repo = ProductRepository()
        
        # Act
        filters = {
            'category_id': 1,
            'pet_type_id': 2,
            'brand': 'Purina',
            'min_stock': 5,
            'is_active': True
        }
        result = repo.get_by_filters(filters)
        
        # Assert
        assert len(result) == 1


class TestProductRepositoryCreate:
    """Test create method."""
    
    @patch('app.products.repositories.product_repository.get_db')
    def test_create_success(self, mock_get_db):
        """Should create product and return it with ID."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_product = Mock(spec=Product)
        mock_product.name = 'New Product'
        
        repo = ProductRepository()
        
        # Act
        result = repo.create(mock_product)
        
        # Assert
        assert result == mock_product
        mock_db.add.assert_called_once_with(mock_product)
        mock_db.flush.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_product)


class TestProductRepositoryUpdate:
    """Test update method."""
    
    @patch('app.products.repositories.product_repository.get_db')
    def test_update_success(self, mock_get_db):
        """Should update product and return updated object."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_product = Mock(spec=Product)
        mock_product.id = 1
        
        mock_db.merge.return_value = mock_product
        
        repo = ProductRepository()
        
        # Act
        result = repo.update(mock_product)
        
        # Assert
        assert result == mock_product
        mock_db.merge.assert_called_once_with(mock_product)
        mock_db.flush.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_product)


class TestProductRepositoryDelete:
    """Test delete method."""
    
    @patch('app.products.repositories.product_repository.get_db')
    def test_delete_success(self, mock_get_db):
        """Should delete product and return True."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_product = Mock(spec=Product)
        mock_product.id = 1
        
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_product
        
        repo = ProductRepository()
        
        # Act
        result = repo.delete(1)
        
        # Assert
        assert result is True
        mock_db.delete.assert_called_once_with(mock_product)
        mock_db.flush.assert_called_once()
    
    @patch('app.products.repositories.product_repository.get_db')
    def test_delete_not_found(self, mock_get_db):
        """Should return False when product doesn't exist."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        repo = ProductRepository()
        
        # Act
        result = repo.delete(999)
        
        # Assert
        assert result is False
        mock_db.delete.assert_not_called()


class TestProductRepositoryExistsBySKU:
    """Test exists_by_sku method."""
    
    @patch('app.products.repositories.product_repository.get_db')
    def test_exists_by_sku_true(self, mock_get_db):
        """Should return True when SKU exists."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = Mock(spec=Product)
        
        repo = ProductRepository()
        
        # Act
        result = repo.exists_by_sku('PROD-001')
        
        # Assert
        assert result is True
    
    @patch('app.products.repositories.product_repository.get_db')
    def test_exists_by_sku_false(self, mock_get_db):
        """Should return False when SKU doesn't exist."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        repo = ProductRepository()
        
        # Act
        result = repo.exists_by_sku('INVALID')
        
        # Assert
        assert result is False


class TestProductRepositoryLookupMethods:
    """Test category and pet type lookup methods."""
    
    @patch('app.products.repositories.product_repository.get_db')
    def test_get_category_by_name_success(self, mock_get_db):
        """Should return category when found."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_category = Mock(spec=ProductCategory)
        mock_category.category = 'food'
        
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_category
        
        repo = ProductRepository()
        
        # Act
        result = repo.get_category_by_name('food')
        
        # Assert
        assert result == mock_category
        mock_db.query.return_value.filter_by.assert_called_once_with(category='food')
    
    @patch('app.products.repositories.product_repository.get_db')
    def test_get_category_by_name_not_found(self, mock_get_db):
        """Should return None when category doesn't exist."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        repo = ProductRepository()
        
        # Act
        result = repo.get_category_by_name('invalid')
        
        # Assert
        assert result is None
    
    @patch('app.products.repositories.product_repository.get_db')
    def test_get_pet_type_by_name_success(self, mock_get_db):
        """Should return pet type when found."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_pet_type = Mock(spec=PetType)
        mock_pet_type.type = 'dog'
        
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_pet_type
        
        repo = ProductRepository()
        
        # Act
        result = repo.get_pet_type_by_name('dog')
        
        # Assert
        assert result == mock_pet_type
        mock_db.query.return_value.filter_by.assert_called_once_with(type='dog')
    
    @patch('app.products.repositories.product_repository.get_db')
    def test_get_pet_type_by_name_not_found(self, mock_get_db):
        """Should return None when pet type doesn't exist."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        repo = ProductRepository()
        
        # Act
        result = repo.get_pet_type_by_name('invalid')
        
        # Assert
        assert result is None
