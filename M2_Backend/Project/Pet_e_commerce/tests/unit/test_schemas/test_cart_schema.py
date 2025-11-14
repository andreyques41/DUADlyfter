"""
Unit tests for Cart schemas.

Tests cover:
- CartItemSchema: Product validation, quantity validation
- CartRegistrationSchema: User validation, items validation, duplicate detection
- CartResponseSchema: Serialization with calculated fields
- CartUpdateSchema: Update validation
"""

import pytest
from marshmallow import ValidationError
from app.sales.schemas.cart_schema import (
    CartItemSchema,
    CartRegistrationSchema,
    CartResponseSchema,
    CartUpdateSchema
)


@pytest.mark.unit
@pytest.mark.sales
class TestCartItemSchema:
    """Test CartItemSchema validation and serialization."""
    
    def test_cart_item_with_valid_data(self, mocker):
        """Test cart item creation with valid data."""
        # Mock ProductService
        mock_product = mocker.Mock()
        mock_product.id = 1
        mock_product.description = "Dog Food"
        mock_product.price = 25.99
        mock_product.stock = 100
        mock_product.is_active = True
        mock_product.is_available = mocker.Mock(return_value=True)
        
        mock_get_product = mocker.patch(
            'app.products.services.product_service.ProductService.get_product_by_id',
            return_value=mock_product
        )
        
        schema = CartItemSchema()
        data = {
            'product_id': 1,
            'quantity': 5
        }
        
        result = schema.load(data)
        
        # Verify ProductService was called
        mock_get_product.assert_called_once_with(1)
        
        # Verify result structure
        assert result['product_id'] == 1
        assert result['quantity'] == 5
        assert result['amount'] == 25.99 * 5  # 129.95
    
    def test_cart_item_with_invalid_product_id(self, mocker):
        """Test cart item with non-existent product."""
        mock_get_product = mocker.patch(
            'app.products.services.product_service.ProductService.get_product_by_id',
            return_value=None
        )
        
        schema = CartItemSchema()
        data = {
            'product_id': 999,
            'quantity': 2
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        # ValidationError from @post_load raises _schema level error
        assert '_schema' in exc_info.value.messages
        assert 'Product 999 not found or unavailable' in str(exc_info.value.messages['_schema'])
    
    def test_cart_item_with_unavailable_product(self, mocker):
        """Test cart item with unavailable product."""
        mock_product = mocker.Mock()
        mock_product.id = 1
        mock_product.is_active = False
        mock_product.is_available = mocker.Mock(return_value=False)
        
        mocker.patch(
            'app.products.services.product_service.ProductService.get_product_by_id',
            return_value=mock_product
        )
        
        schema = CartItemSchema()
        data = {
            'product_id': 1,
            'quantity': 2
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        # ValidationError from @post_load raises _schema level error
        assert '_schema' in exc_info.value.messages
        assert 'unavailable' in str(exc_info.value.messages['_schema']).lower()
    
    def test_cart_item_with_insufficient_stock(self, mocker):
        """Test cart item with quantity exceeding stock.
        Note: Stock validation happens in service layer, not schema.
        Schema only validates product exists and is available.
        """
        mock_product = mocker.Mock()
        mock_product.id = 1
        mock_product.stock = 5
        mock_product.is_active = True
        mock_product.is_available = mocker.Mock(return_value=True)
        mock_product.description = "Dog Food"
        mock_product.price = 25.99
        
        mocker.patch(
            'app.products.services.product_service.ProductService.get_product_by_id',
            return_value=mock_product
        )
        
        schema = CartItemSchema()
        data = {
            'product_id': 1,
            'quantity': 10  # More than stock, but schema doesn't check this
        }
        
        # Schema will pass - stock validation is in service layer
        result = schema.load(data)
        assert result['product_id'] == 1
        assert result['quantity'] == 10
    
    def test_cart_item_with_invalid_quantity(self):
        """Test cart item with out-of-range quantity."""
        schema = CartItemSchema()
        
        # Quantity below minimum
        with pytest.raises(ValidationError) as exc_info:
            schema.load({'product_id': 1, 'quantity': 0})
        assert 'quantity' in exc_info.value.messages
        
        # Quantity above maximum
        with pytest.raises(ValidationError) as exc_info:
            schema.load({'product_id': 1, 'quantity': 51})
        assert 'quantity' in exc_info.value.messages
    
    def test_cart_item_missing_required_fields(self):
        """Test cart item with missing required fields."""
        schema = CartItemSchema()
        
        # Missing product_id
        with pytest.raises(ValidationError) as exc_info:
            schema.load({'quantity': 2})
        assert 'product_id' in exc_info.value.messages
        
        # Missing quantity
        with pytest.raises(ValidationError) as exc_info:
            schema.load({'product_id': 1})
        assert 'quantity' in exc_info.value.messages


@pytest.mark.unit
@pytest.mark.sales
class TestCartRegistrationSchema:
    """Test CartRegistrationSchema validation."""
    
    def test_cart_registration_with_valid_data(self, mocker):
        """Test cart creation with valid data."""
        # Mock ProductService for both items
        mock_product1 = mocker.Mock(
            id=1, price=25.99, stock=100, is_active=True
        )
        mock_product1.is_available = mocker.Mock(return_value=True)
        mock_product1.description = "Dog Food"
        
        mock_product2 = mocker.Mock(
            id=2, price=15.49, stock=50, is_active=True
        )
        mock_product2.is_available = mocker.Mock(return_value=True)
        mock_product2.description = "Cat Toy"
        
        mocker.patch(
            'app.products.services.product_service.ProductService.get_product_by_id',
            side_effect=[mock_product1, mock_product2]
        )
        
        schema = CartRegistrationSchema()
        data = {
            'user_id': 1,
            'items': [
                {'product_id': 1, 'quantity': 2},
                {'product_id': 2, 'quantity': 3}
            ]
        }
        
        result = schema.load(data)
        
        assert result['user_id'] == 1
        assert len(result['items']) == 2
        assert result['items'][0]['product_id'] == 1
        assert result['items'][1]['product_id'] == 2
    
    def test_cart_registration_with_duplicate_products(self, mocker):
        """Test cart creation with duplicate products."""
        # Mock ProductService
        mock_product = mocker.Mock(
            id=1, price=25.99, stock=100, is_active=True
        )
        mock_product.is_available = mocker.Mock(return_value=True)
        mock_product.description = "Dog Food"
        
        mocker.patch(
            'app.products.services.product_service.ProductService.get_product_by_id',
            return_value=mock_product
        )
        
        schema = CartRegistrationSchema()
        data = {
            'user_id': 1,
            'items': [
                {'product_id': 1, 'quantity': 2},
                {'product_id': 1, 'quantity': 3}  # Duplicate
            ]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        # ValidationError from @validates_schema raises _schema level error
        assert '_schema' in exc_info.value.messages
        assert 'duplicate' in str(exc_info.value.messages['_schema']).lower()
    
    def test_cart_registration_with_empty_items(self):
        """Test cart creation with empty items list."""
        schema = CartRegistrationSchema()
        data = {
            'user_id': 1,
            'items': []
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'items' in exc_info.value.messages
    
    def test_cart_registration_with_too_many_items(self, mocker):
        """Test cart creation with too many items."""
        # Mock ProductService
        mock_product = mocker.Mock(
            id=1, price=25.99, stock=100, is_active=True
        )
        mock_product.is_available = mocker.Mock(return_value=True)
        mock_product.description = "Dog Food"
        
        mocker.patch(
            'app.products.services.product_service.ProductService.get_product_by_id',
            return_value=mock_product
        )
        
        schema = CartRegistrationSchema()
        # Create 101 items (exceeds max of 100)
        items = [{'product_id': i, 'quantity': 1} for i in range(1, 102)]
        data = {
            'user_id': 1,
            'items': items
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'items' in exc_info.value.messages
    
    def test_cart_registration_missing_user_id(self, mocker):
        """Test cart creation without user_id."""
        # Mock ProductService even though user_id will fail first
        mock_product = mocker.Mock(
            id=1, price=25.99, stock=100, is_active=True
        )
        mock_product.is_available = mocker.Mock(return_value=True)
        mock_product.description = "Dog Food"
        
        mocker.patch(
            'app.products.services.product_service.ProductService.get_product_by_id',
            return_value=mock_product
        )
        
        schema = CartRegistrationSchema()
        data = {
            'items': [
                {'product_id': 1, 'quantity': 2}
            ]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'user_id' in exc_info.value.messages


@pytest.mark.unit
@pytest.mark.sales
class TestCartResponseSchema:
    """Test CartResponseSchema serialization."""
    
    def test_cart_response_serialization(self, test_cart_with_items):
        """Test cart response with calculated fields."""
        schema = CartResponseSchema()
        result = schema.dump(test_cart_with_items)
        
        # Verify basic fields (Cart model uses 'id' not 'cart_id')
        assert result['id'] == test_cart_with_items.id
        assert result['user_id'] == test_cart_with_items.user_id
        
        # Verify calculated fields
        assert 'total' in result
        assert 'item_count' in result
        
        # Calculate expected total
        expected_total = sum(item.amount for item in test_cart_with_items.items)
        assert result['total'] == expected_total
        
        # Calculate expected item count
        expected_count = sum(item.quantity for item in test_cart_with_items.items)
        assert result['item_count'] == expected_count
    
    def test_cart_response_with_empty_cart(self, test_cart):
        """Test cart response with no items."""
        schema = CartResponseSchema()
        result = schema.dump(test_cart)
        
        assert result['id'] == test_cart.id
        assert result['total'] == 0
        assert result['item_count'] == 0
    
    def test_cart_response_includes_items(self, test_cart_with_items):
        """Test cart response includes item details."""
        schema = CartResponseSchema()
        result = schema.dump(test_cart_with_items)
        
        assert 'items' in result
        assert len(result['items']) == len(test_cart_with_items.items)
        
        # Verify first item structure
        first_item = result['items'][0]
        assert 'product_id' in first_item
        assert 'quantity' in first_item
        assert 'amount' in first_item


@pytest.mark.unit
@pytest.mark.sales
class TestCartUpdateSchema:
    """Test CartUpdateSchema validation."""
    
    def test_cart_update_with_valid_data(self, mocker):
        """Test cart update with valid items."""
        mock_product = mocker.Mock(
            id=1, price=25.99, stock=100, is_active=True
        )
        mock_product.is_available = mocker.Mock(return_value=True)
        mock_product.description = "Dog Food"
        
        mocker.patch(
            'app.products.services.product_service.ProductService.get_product_by_id',
            return_value=mock_product
        )
        
        schema = CartUpdateSchema()
        data = {
            'items': [
                {'product_id': 1, 'quantity': 5}
            ]
        }
        
        result = schema.load(data)
        
        assert 'items' in result
        assert len(result['items']) == 1
        assert result['items'][0]['product_id'] == 1
        assert result['items'][0]['quantity'] == 5
    
    def test_cart_update_missing_items(self):
        """Test cart update without items field."""
        schema = CartUpdateSchema()
        data = {}
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'items' in exc_info.value.messages
