"""
Unit tests for ProductService.

Tests cover:
- Product retrieval (by ID, SKU, all products, filtering)
- Product creation with reference data conversion
- Product updates with reference data conversion
- Product deletion
- SKU validation
- Error handling and edge cases
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from app.products.services.product_service import ProductService
from app.products.models.product import Product


@pytest.mark.unit
@pytest.mark.products
class TestProductServiceRetrieval:
    """Test product retrieval methods."""
    
    def test_get_product_by_id_success(self, mocker):
        """Test successfully retrieving a product by ID."""
        service = ProductService()
        
        # Mock product
        mock_product = Mock(spec=Product)
        mock_product.id = 1
        mock_product.name = "Dog Food Premium"
        
        # Mock repository
        mocker.patch.object(
            service.product_repo,
            'get_by_id',
            return_value=mock_product
        )
        
        result = service.get_product_by_id(1)
        
        assert result == mock_product
        assert result.id == 1
        service.product_repo.get_by_id.assert_called_once_with(1)
    
    def test_get_product_by_id_not_found(self, mocker):
        """Test retrieving non-existent product by ID."""
        service = ProductService()
        
        mocker.patch.object(
            service.product_repo,
            'get_by_id',
            return_value=None
        )
        
        result = service.get_product_by_id(999)
        
        assert result is None
        service.product_repo.get_by_id.assert_called_once_with(999)
    
    def test_get_product_by_sku_success(self, mocker):
        """Test successfully retrieving a product by SKU."""
        service = ProductService()
        
        mock_product = Mock(spec=Product)
        mock_product.sku = "DOG001"
        mock_product.name = "Dog Toy"
        
        mocker.patch.object(
            service.product_repo,
            'get_by_sku',
            return_value=mock_product
        )
        
        result = service.get_product_by_sku("DOG001")
        
        assert result == mock_product
        assert result.sku == "DOG001"
        service.product_repo.get_by_sku.assert_called_once_with("DOG001")
    
    def test_get_product_by_sku_not_found(self, mocker):
        """Test retrieving product by non-existent SKU."""
        service = ProductService()
        
        mocker.patch.object(
            service.product_repo,
            'get_by_sku',
            return_value=None
        )
        
        result = service.get_product_by_sku("INVALID")
        
        assert result is None
    
    def test_get_all_products(self, mocker):
        """Test retrieving all products."""
        service = ProductService()
        
        mock_products = [
            Mock(spec=Product, id=1, name="Product 1"),
            Mock(spec=Product, id=2, name="Product 2"),
            Mock(spec=Product, id=3, name="Product 3"),
        ]
        
        mocker.patch.object(
            service.product_repo,
            'get_all',
            return_value=mock_products
        )
        
        result = service.get_all_products()
        
        assert len(result) == 3
        assert result == mock_products
        service.product_repo.get_all.assert_called_once()
    
    def test_get_all_products_empty(self, mocker):
        """Test retrieving all products when none exist."""
        service = ProductService()
        
        mocker.patch.object(
            service.product_repo,
            'get_all',
            return_value=[]
        )
        
        result = service.get_all_products()
        
        assert result == []
        assert len(result) == 0


@pytest.mark.unit
@pytest.mark.products
class TestProductServiceFiltering:
    """Test product filtering with reference data conversion."""
    
    def test_get_products_by_filters_with_category_name(self, mocker):
        """Test filtering products by category name (converts to ID)."""
        service = ProductService()
        
        mock_products = [Mock(spec=Product, id=1, name="Dog Food")]
        
        # Mock ReferenceData.get_product_category_id
        mocker.patch(
            'app.products.services.product_service.ReferenceData.get_product_category_id',
            return_value=1
        )
        
        # Mock repository
        mocker.patch.object(
            service.product_repo,
            'get_by_filters',
            return_value=mock_products
        )
        
        result = service.get_products_by_filters({'category': 'food'})
        
        assert result == mock_products
        # Verify category was converted to category_id
        service.product_repo.get_by_filters.assert_called_once_with({'category_id': 1})
    
    def test_get_products_by_filters_with_invalid_category(self, mocker):
        """Test filtering with invalid category name returns empty list."""
        service = ProductService()
        
        # Mock ReferenceData to return None for invalid category
        mocker.patch(
            'app.products.services.product_service.ReferenceData.get_product_category_id',
            return_value=None
        )
        
        result = service.get_products_by_filters({'category': 'invalid_category'})
        
        # Should return empty list for invalid category
        assert result == []
    
    def test_get_products_by_filters_with_pet_type_name(self, mocker):
        """Test filtering products by pet_type name (converts to ID)."""
        service = ProductService()
        
        mock_products = [Mock(spec=Product, id=1, name="Cat Toy")]
        
        # Mock ReferenceData.get_pet_type_id
        mocker.patch(
            'app.products.services.product_service.ReferenceData.get_pet_type_id',
            return_value=2
        )
        
        mocker.patch.object(
            service.product_repo,
            'get_by_filters',
            return_value=mock_products
        )
        
        result = service.get_products_by_filters({'pet_type': 'cat'})
        
        assert result == mock_products
        service.product_repo.get_by_filters.assert_called_once_with({'pet_type_id': 2})
    
    def test_get_products_by_filters_with_invalid_pet_type(self, mocker):
        """Test filtering with invalid pet_type returns empty list."""
        service = ProductService()
        
        mocker.patch(
            'app.products.services.product_service.ReferenceData.get_pet_type_id',
            return_value=None
        )
        
        result = service.get_products_by_filters({'pet_type': 'invalid_pet'})
        
        assert result == []
    
    def test_get_products_by_filters_with_multiple_filters(self, mocker):
        """Test filtering with multiple criteria including conversions."""
        service = ProductService()
        
        mock_products = [Mock(spec=Product, id=1)]
        
        mocker.patch(
            'app.products.services.product_service.ReferenceData.get_product_category_id',
            return_value=1
        )
        mocker.patch(
            'app.products.services.product_service.ReferenceData.get_pet_type_id',
            return_value=2
        )
        
        mocker.patch.object(
            service.product_repo,
            'get_by_filters',
            return_value=mock_products
        )
        
        filters = {
            'category': 'food',
            'pet_type': 'dog',
            'brand': 'Premium Brand',
            'is_active': True
        }
        
        result = service.get_products_by_filters(filters)
        
        # Verify category and pet_type were converted to IDs
        expected_filters = {
            'category_id': 1,
            'pet_type_id': 2,
            'brand': 'Premium Brand',
            'is_active': True
        }
        service.product_repo.get_by_filters.assert_called_once_with(expected_filters)
        assert result == mock_products
    
    def test_get_products_by_filters_no_conversions_needed(self, mocker):
        """Test filtering without reference data conversions."""
        service = ProductService()
        
        mock_products = [Mock(spec=Product, id=1)]
        
        mocker.patch.object(
            service.product_repo,
            'get_by_filters',
            return_value=mock_products
        )
        
        filters = {'brand': 'Test Brand', 'is_active': True}
        
        result = service.get_products_by_filters(filters)
        
        # Filters should pass through unchanged
        service.product_repo.get_by_filters.assert_called_once_with(filters)
        assert result == mock_products


@pytest.mark.unit
@pytest.mark.products
class TestProductServiceCreation:
    """Test product creation with reference data conversion."""
    
    def test_create_product_success(self, mocker):
        """Test successful product creation with reference data conversion."""
        service = ProductService()
        
        # Mock ReferenceData conversions
        mocker.patch(
            'app.products.services.product_service.ReferenceData.get_product_category_id',
            return_value=1
        )
        mocker.patch(
            'app.products.services.product_service.ReferenceData.get_pet_type_id',
            return_value=2
        )
        
        # Mock SKU check
        mocker.patch.object(
            service,
            'check_sku_exists',
            return_value=False
        )
        
        # Mock Product class to avoid SQLAlchemy instantiation
        mock_product_instance = Mock(spec=Product)
        mock_product_instance.id = 1
        mock_product_instance.sku = "DOG123"
        
        mock_product_class = mocker.patch('app.products.services.product_service.Product')
        mock_product_class.return_value = mock_product_instance
        
        # Mock repository create
        mock_created_product = Mock(spec=Product)
        mock_created_product.id = 1
        mock_created_product.sku = "DOG123"
        
        mocker.patch.object(
            service.product_repo,
            'create',
            return_value=mock_created_product
        )
        
        product_data = {
            'name': 'Premium Dog Food',
            'description': 'High quality dog food',
            'category': 'food',
            'pet_type': 'dog',
            'price': 29.99,
            'stock_quantity': 100,
            'sku': 'DOG123'
        }
        
        result = service.create_product(**product_data)
        
        assert result == mock_created_product
        assert result.sku == 'DOG123'
        service.product_repo.create.assert_called_once()
    
    def test_create_product_with_invalid_category(self, mocker):
        """Test product creation with invalid category returns None."""
        service = ProductService()
        
        # Mock ReferenceData to return None for invalid category
        mocker.patch(
            'app.products.services.product_service.ReferenceData.get_product_category_id',
            return_value=None
        )
        
        product_data = {
            'name': 'Test Product',
            'category': 'invalid_category',
            'pet_type': 'dog',
            'price': 19.99,
            'stock_quantity': 50
        }
        
        result = service.create_product(**product_data)
        
        assert result is None
    
    def test_create_product_with_invalid_pet_type(self, mocker):
        """Test product creation with invalid pet_type returns None."""
        service = ProductService()
        
        mocker.patch(
            'app.products.services.product_service.ReferenceData.get_product_category_id',
            return_value=1
        )
        mocker.patch(
            'app.products.services.product_service.ReferenceData.get_pet_type_id',
            return_value=None
        )
        
        product_data = {
            'name': 'Test Product',
            'category': 'food',
            'pet_type': 'invalid_pet',
            'price': 19.99,
            'stock_quantity': 50
        }
        
        result = service.create_product(**product_data)
        
        assert result is None
    
    def test_create_product_with_duplicate_sku(self, mocker):
        """Test product creation with duplicate SKU returns None."""
        service = ProductService()
        
        mocker.patch(
            'app.products.services.product_service.ReferenceData.get_product_category_id',
            return_value=1
        )
        mocker.patch(
            'app.products.services.product_service.ReferenceData.get_pet_type_id',
            return_value=2
        )
        
        # Mock SKU already exists
        mocker.patch.object(
            service,
            'check_sku_exists',
            return_value=True
        )
        
        product_data = {
            'name': 'Test Product',
            'category': 'food',
            'pet_type': 'dog',
            'price': 19.99,
            'stock_quantity': 50,
            'sku': 'EXISTING_SKU'
        }
        
        result = service.create_product(**product_data)
        
        assert result is None
    
    def test_create_product_generates_sku_if_not_provided(self, mocker):
        """Test that SKU is auto-generated if not provided."""
        service = ProductService()
        
        mocker.patch(
            'app.products.services.product_service.ReferenceData.get_product_category_id',
            return_value=1
        )
        mocker.patch(
            'app.products.services.product_service.ReferenceData.get_pet_type_id',
            return_value=2
        )
        mocker.patch.object(service, 'check_sku_exists', return_value=False)
        
        # Mock Product class
        mock_product_instance = Mock(spec=Product)
        mocker.patch('app.products.services.product_service.Product', return_value=mock_product_instance)
        
        mock_created = Mock(spec=Product)
        mocker.patch.object(service.product_repo, 'create', return_value=mock_created)
        
        product_data = {
            'name': 'Test Product',
            'category': 'food',
            'pet_type': 'dog',
            'price': 19.99,
            'stock_quantity': 50
            # No SKU provided
        }
        
        result = service.create_product(**product_data)
        
        # Verify create was called (SKU was generated internally)
        assert service.product_repo.create.called
        assert result == mock_created
    
    def test_create_product_sets_default_is_active(self, mocker):
        """Test that is_active defaults to True."""
        service = ProductService()
        
        mocker.patch(
            'app.products.services.product_service.ReferenceData.get_product_category_id',
            return_value=1
        )
        mocker.patch(
            'app.products.services.product_service.ReferenceData.get_pet_type_id',
            return_value=2
        )
        mocker.patch.object(service, 'check_sku_exists', return_value=False)
        
        # Mock Product class and capture the arguments
        mock_product_instance = Mock(spec=Product)
        mock_product_instance.is_active = True
        mock_product_class = mocker.patch('app.products.services.product_service.Product')
        mock_product_class.return_value = mock_product_instance
        
        mock_created = Mock(spec=Product)
        mocker.patch.object(service.product_repo, 'create', return_value=mock_created)
        
        product_data = {
            'name': 'Test Product',
            'category': 'food',
            'pet_type': 'dog',
            'price': 19.99,
            'stock_quantity': 50,
            'sku': 'TEST123'
        }
        
        result = service.create_product(**product_data)
        
        # Verify Product was instantiated with is_active=True
        assert mock_product_class.called
        call_kwargs = mock_product_class.call_args[1]
        assert 'is_active' in call_kwargs
        assert call_kwargs['is_active'] is True
        assert result == mock_created
    
    def test_create_product_with_exception(self, mocker):
        """Test product creation handles exceptions gracefully."""
        service = ProductService()
        
        mocker.patch(
            'app.products.services.product_service.ReferenceData.get_product_category_id',
            side_effect=Exception("Database error")
        )
        
        product_data = {
            'name': 'Test Product',
            'category': 'food',
            'pet_type': 'dog',
            'price': 19.99,
            'stock_quantity': 50
        }
        
        result = service.create_product(**product_data)
        
        assert result is None


@pytest.mark.unit
@pytest.mark.products
class TestProductServiceUpdate:
    """Test product update operations."""
    
    def test_update_product_success(self, mocker):
        """Test successful product update."""
        service = ProductService()
        
        # Mock existing product
        mock_product = Mock(spec=Product)
        mock_product.id = 1
        mock_product.name = "Old Name"
        mock_product.price = 19.99
        
        mocker.patch.object(
            service.product_repo,
            'get_by_id',
            return_value=mock_product
        )
        
        mock_updated = Mock(spec=Product)
        mock_updated.id = 1
        mock_updated.name = "New Name"
        
        mocker.patch.object(
            service.product_repo,
            'update',
            return_value=mock_updated
        )
        
        result = service.update_product(1, name="New Name", price=29.99)
        
        assert result == mock_updated
        service.product_repo.update.assert_called_once()
    
    def test_update_product_not_found(self, mocker):
        """Test updating non-existent product returns None."""
        service = ProductService()
        
        mocker.patch.object(
            service.product_repo,
            'get_by_id',
            return_value=None
        )
        
        result = service.update_product(999, name="New Name")
        
        assert result is None
    
    def test_update_product_with_category_conversion(self, mocker):
        """Test updating product with category name conversion."""
        service = ProductService()
        
        mock_product = Mock(spec=Product)
        mock_product.id = 1
        
        mocker.patch.object(service.product_repo, 'get_by_id', return_value=mock_product)
        
        mocker.patch(
            'app.products.services.product_service.ReferenceData.get_product_category_id',
            return_value=2
        )
        
        mock_updated = Mock(spec=Product)
        mocker.patch.object(service.product_repo, 'update', return_value=mock_updated)
        
        result = service.update_product(1, category='toys')
        
        # Verify product_category_id was set
        assert result == mock_updated
    
    def test_update_product_with_invalid_category(self, mocker):
        """Test updating with invalid category returns None."""
        service = ProductService()
        
        mock_product = Mock(spec=Product)
        mocker.patch.object(service.product_repo, 'get_by_id', return_value=mock_product)
        
        mocker.patch(
            'app.products.services.product_service.ReferenceData.get_product_category_id',
            return_value=None
        )
        
        result = service.update_product(1, category='invalid_category')
        
        assert result is None
    
    def test_update_product_with_pet_type_conversion(self, mocker):
        """Test updating product with pet_type name conversion."""
        service = ProductService()
        
        mock_product = Mock(spec=Product)
        mock_product.id = 1
        
        mocker.patch.object(service.product_repo, 'get_by_id', return_value=mock_product)
        
        mocker.patch(
            'app.products.services.product_service.ReferenceData.get_pet_type_id',
            return_value=3
        )
        
        mock_updated = Mock(spec=Product)
        mocker.patch.object(service.product_repo, 'update', return_value=mock_updated)
        
        result = service.update_product(1, pet_type='bird')
        
        assert result == mock_updated
    
    def test_update_product_with_invalid_pet_type(self, mocker):
        """Test updating with invalid pet_type returns None."""
        service = ProductService()
        
        mock_product = Mock(spec=Product)
        mocker.patch.object(service.product_repo, 'get_by_id', return_value=mock_product)
        
        mocker.patch(
            'app.products.services.product_service.ReferenceData.get_pet_type_id',
            return_value=None
        )
        
        result = service.update_product(1, pet_type='invalid_pet')
        
        assert result is None
    
    def test_update_product_with_exception(self, mocker):
        """Test update handles exceptions gracefully."""
        service = ProductService()
        
        mocker.patch.object(
            service.product_repo,
            'get_by_id',
            side_effect=Exception("Database error")
        )
        
        result = service.update_product(1, name="New Name")
        
        assert result is None


@pytest.mark.unit
@pytest.mark.products
class TestProductServiceDeletion:
    """Test product deletion operations."""
    
    def test_delete_product_success(self, mocker):
        """Test successful product deletion."""
        service = ProductService()
        
        mock_product = Mock(spec=Product)
        mock_product.id = 1
        
        mocker.patch.object(service.product_repo, 'get_by_id', return_value=mock_product)
        mocker.patch.object(service.product_repo, 'delete', return_value=True)
        
        result = service.delete_product(1)
        
        assert result is True
        service.product_repo.delete.assert_called_once_with(1)
    
    def test_delete_product_not_found(self, mocker):
        """Test deleting non-existent product returns False."""
        service = ProductService()
        
        mocker.patch.object(service.product_repo, 'get_by_id', return_value=None)
        
        result = service.delete_product(999)
        
        assert result is False
    
    def test_delete_product_repository_failure(self, mocker):
        """Test deletion returns False when repository fails."""
        service = ProductService()
        
        mock_product = Mock(spec=Product)
        mocker.patch.object(service.product_repo, 'get_by_id', return_value=mock_product)
        mocker.patch.object(service.product_repo, 'delete', return_value=False)
        
        result = service.delete_product(1)
        
        assert result is False
    
    def test_delete_product_with_exception(self, mocker):
        """Test deletion handles exceptions gracefully."""
        service = ProductService()
        
        mocker.patch.object(
            service.product_repo,
            'get_by_id',
            side_effect=Exception("Database error")
        )
        
        result = service.delete_product(1)
        
        assert result is False


@pytest.mark.unit
@pytest.mark.products
class TestProductServiceValidation:
    """Test product validation methods."""
    
    def test_check_sku_exists_true(self, mocker):
        """Test SKU existence check returns True when SKU exists."""
        service = ProductService()
        
        mocker.patch.object(
            service.product_repo,
            'exists_by_sku',
            return_value=True
        )
        
        result = service.check_sku_exists("EXISTING_SKU")
        
        assert result is True
        service.product_repo.exists_by_sku.assert_called_once_with("EXISTING_SKU")
    
    def test_check_sku_exists_false(self, mocker):
        """Test SKU existence check returns False when SKU doesn't exist."""
        service = ProductService()
        
        mocker.patch.object(
            service.product_repo,
            'exists_by_sku',
            return_value=False
        )
        
        result = service.check_sku_exists("NEW_SKU")
        
        assert result is False
