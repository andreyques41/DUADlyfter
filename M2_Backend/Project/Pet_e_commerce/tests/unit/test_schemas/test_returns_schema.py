"""
Unit tests for Return schemas.

Tests cover:
- ReturnItemSchema: Product validation, quantity validation, refund amount
- ReturnRegistrationSchema: Order validation, items validation, status validation
- ReturnUpdateSchema: Partial update validation
- ReturnStatusUpdateSchema: Status-only updates
- ReturnResponseSchema: Serialization with status name conversion
"""

import pytest
from marshmallow import ValidationError
from app.sales.schemas.returns_schema import (
    ReturnItemSchema,
    ReturnRegistrationSchema,
    ReturnUpdateSchema,
    ReturnStatusUpdateSchema,
    ReturnResponseSchema
)


@pytest.mark.unit
@pytest.mark.sales
class TestReturnItemSchema:
    """Test ReturnItemSchema validation and serialization."""
    
    def test_return_item_with_valid_data(self, mocker):
        """Test return item creation with valid data."""
        # Mock ProductService
        mock_product = mocker.Mock()
        mock_product.id = 1
        mock_product.price = 49.99
        
        mocker.patch(
            'app.products.services.product_service.ProductService.get_product_by_id',
            return_value=mock_product
        )
        
        schema = ReturnItemSchema()
        data = {
            'product_id': 1,
            'quantity': 2,
            'reason': 'Product was damaged during shipping'
        }
        
        result = schema.load(data)
        
        # Result should be a ReturnItem object
        assert result.product_id == 1
        assert result.quantity == 2
        assert result.reason == 'Product was damaged during shipping'
        assert result.amount == 49.99 * 2  # Auto-calculated from price
    
    def test_return_item_with_custom_refund_amount(self, mocker):
        """Test return item with custom refund amount."""
        mock_product = mocker.Mock()
        mock_product.id = 1
        mock_product.price = 49.99
        
        mocker.patch(
            'app.products.services.product_service.ProductService.get_product_by_id',
            return_value=mock_product
        )
        
        schema = ReturnItemSchema()
        data = {
            'product_id': 1,
            'quantity': 2,
            'reason': 'Partial refund requested',
            'refund_amount': 50.00  # Custom amount
        }
        
        result = schema.load(data)
        
        assert result.amount == 50.00  # Uses custom amount
    
    def test_return_item_with_invalid_product_id(self, mocker):
        """Test return item with non-existent product."""
        mocker.patch(
            'app.products.services.product_service.ProductService.get_product_by_id',
            return_value=None
        )
        
        schema = ReturnItemSchema()
        data = {
            'product_id': 999,
            'quantity': 1,
            'reason': 'Defective item'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert '_schema' in exc_info.value.messages
        assert 'Product 999 not found' in str(exc_info.value.messages['_schema'])
    
    def test_return_item_with_invalid_quantity(self):
        """Test return item with out-of-range quantity."""
        schema = ReturnItemSchema()
        
        # Quantity below minimum
        with pytest.raises(ValidationError) as exc_info:
            schema.load({
                'product_id': 1,
                'quantity': 0,
                'reason': 'Test'
            })
        assert 'quantity' in exc_info.value.messages
        
        # Quantity above maximum
        with pytest.raises(ValidationError) as exc_info:
            schema.load({
                'product_id': 1,
                'quantity': 101,
                'reason': 'Test'
            })
        assert 'quantity' in exc_info.value.messages
    
    def test_return_item_missing_reason(self, mocker):
        """Test return item without reason field."""
        mock_product = mocker.Mock()
        mock_product.id = 1
        mock_product.price = 49.99
        
        mocker.patch(
            'app.products.services.product_service.ProductService.get_product_by_id',
            return_value=mock_product
        )
        
        schema = ReturnItemSchema()
        data = {
            'product_id': 1,
            'quantity': 1
            # Missing 'reason'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'reason' in exc_info.value.messages
    
    def test_return_item_with_negative_refund_amount(self):
        """Test return item with negative refund amount."""
        schema = ReturnItemSchema()
        data = {
            'product_id': 1,
            'quantity': 1,
            'reason': 'Test',
            'refund_amount': -10.00  # Negative not allowed
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'refund_amount' in exc_info.value.messages


@pytest.mark.unit
@pytest.mark.sales
class TestReturnRegistrationSchema:
    """Test ReturnRegistrationSchema validation."""
    
    def test_return_registration_with_valid_data(self, mocker):
        """Test return creation with valid data."""
        # Mock ProductService
        mock_product = mocker.Mock()
        mock_product.id = 1
        mock_product.price = 49.99
        
        mocker.patch(
            'app.products.services.product_service.ProductService.get_product_by_id',
            return_value=mock_product
        )
        
        # Mock OrderService
        mock_order = mocker.Mock()
        mock_order.id = 1
        mock_order.user_id = 1
        
        mocker.patch(
            'app.sales.services.order_service.OrderService.get_order_by_id',
            return_value=mock_order
        )
        
        # Mock Flask g.current_user using MagicMock
        mock_current_user = mocker.MagicMock()
        mock_current_user.id = 1
        
        mock_g = mocker.MagicMock()
        mock_g.current_user = mock_current_user
        
        mocker.patch('flask.g', new=mock_g)
        
        # Mock ReferenceData
        mocker.patch(
            'app.sales.schemas.returns_schema.ReferenceData.is_valid_return_status',
            return_value=True
        )
        
        schema = ReturnRegistrationSchema()
        data = {
            'order_id': 1,
            'items': [
                {
                    'product_id': 1,
                    'quantity': 2,
                    'reason': 'Product defective'
                }
            ],
            'status': 'pending'
        }
        
        result = schema.load(data)
        
        assert result['user_id'] == 1
        assert result['order_id'] == 1
        assert len(result['items']) == 1
        assert result['total_amount'] == 49.99 * 2
        assert result['status'] == 'pending'
    
    def test_return_registration_without_status(self, mocker):
        """Test return creation without status (should be set by service)."""
        mock_product = mocker.Mock()
        mock_product.id = 1
        mock_product.price = 29.99
        
        mocker.patch(
            'app.products.services.product_service.ProductService.get_product_by_id',
            return_value=mock_product
        )
        
        mock_order = mocker.Mock()
        mock_order.id = 1
        mock_order.user_id = 1
        
        mocker.patch(
            'app.sales.services.order_service.OrderService.get_order_by_id',
            return_value=mock_order
        )
        
        mock_current_user = mocker.MagicMock()
        mock_current_user.id = 1
        
        mock_g = mocker.MagicMock()
        mock_g.current_user = mock_current_user
        
        mocker.patch('flask.g', new=mock_g)
        
        schema = ReturnRegistrationSchema()
        data = {
            'order_id': 1,
            'items': [
                {
                    'product_id': 1,
                    'quantity': 1,
                    'reason': 'Wrong item received'
                }
            ]
        }
        
        result = schema.load(data)
        
        assert result['order_id'] == 1
        assert 'status' not in result  # Service will set default
    
    def test_return_registration_with_invalid_status(self, mocker):
        """Test return creation with invalid status."""
        mock_product = mocker.Mock()
        mock_product.id = 1
        mock_product.price = 29.99
        
        mocker.patch(
            'app.products.services.product_service.ProductService.get_product_by_id',
            return_value=mock_product
        )
        
        mocker.patch(
            'app.sales.schemas.returns_schema.ReferenceData.is_valid_return_status',
            return_value=False
        )
        
        schema = ReturnRegistrationSchema()
        data = {
            'order_id': 1,
            'items': [
                {
                    'product_id': 1,
                    'quantity': 1,
                    'reason': 'Test'
                }
            ],
            'status': 'invalid_status'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'status' in exc_info.value.messages
    
    def test_return_registration_with_nonexistent_order(self, mocker):
        """Test return creation with order that doesn't exist."""
        mock_product = mocker.Mock()
        mock_product.id = 1
        mock_product.price = 29.99
        
        mocker.patch(
            'app.products.services.product_service.ProductService.get_product_by_id',
            return_value=mock_product
        )
        
        mocker.patch(
            'app.sales.services.order_service.OrderService.get_order_by_id',
            return_value=None
        )
        
        mock_current_user = mocker.MagicMock()
        mock_current_user.id = 1
        
        mock_g = mocker.MagicMock()
        mock_g.current_user = mock_current_user
        
        mocker.patch('flask.g', new=mock_g)
        
        schema = ReturnRegistrationSchema()
        data = {
            'order_id': 999,
            'items': [
                {
                    'product_id': 1,
                    'quantity': 1,
                    'reason': 'Test'
                }
            ]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert '_schema' in exc_info.value.messages
        assert 'Order 999 not found' in str(exc_info.value.messages['_schema'])
    
    def test_return_registration_with_wrong_user_order(self, mocker):
        """Test return creation for order belonging to different user."""
        mock_product = mocker.Mock()
        mock_product.id = 1
        mock_product.price = 29.99
        
        mocker.patch(
            'app.products.services.product_service.ProductService.get_product_by_id',
            return_value=mock_product
        )
        
        mock_order = mocker.Mock()
        mock_order.id = 1
        mock_order.user_id = 2  # Different user
        
        mocker.patch(
            'app.sales.services.order_service.OrderService.get_order_by_id',
            return_value=mock_order
        )
        
        mock_current_user = mocker.MagicMock()
        mock_current_user.id = 1  # Current user
        
        mock_g = mocker.MagicMock()
        mock_g.current_user = mock_current_user
        
        mocker.patch('flask.g', new=mock_g)
        
        schema = ReturnRegistrationSchema()
        data = {
            'order_id': 1,
            'items': [
                {
                    'product_id': 1,
                    'quantity': 1,
                    'reason': 'Test'
                }
            ]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert '_schema' in exc_info.value.messages
        assert 'does not belong to current user' in str(exc_info.value.messages['_schema'])
    
    def test_return_registration_missing_order_id(self, mocker):
        """Test return creation without order_id."""
        # Mock ProductService to prevent errors when items are processed
        mock_product = mocker.Mock()
        mock_product.id = 1
        mock_product.price = 29.99
        
        mocker.patch(
            'app.products.services.product_service.ProductService.get_product_by_id',
            return_value=mock_product
        )
        
        schema = ReturnRegistrationSchema()
        data = {
            'items': [
                {
                    'product_id': 1,
                    'quantity': 1,
                    'reason': 'Test'
                }
            ]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'order_id' in exc_info.value.messages


@pytest.mark.unit
@pytest.mark.sales
class TestReturnUpdateSchema:
    """Test ReturnUpdateSchema validation."""
    
    def test_return_update_with_items(self, mocker):
        """Test return update with new items."""
        mock_product = mocker.Mock()
        mock_product.id = 1
        mock_product.price = 39.99
        
        mocker.patch(
            'app.products.services.product_service.ProductService.get_product_by_id',
            return_value=mock_product
        )
        
        schema = ReturnUpdateSchema()
        data = {
            'items': [
                {
                    'product_id': 1,
                    'quantity': 3,
                    'reason': 'Updated reason'
                }
            ]
        }
        
        result = schema.load(data)
        
        assert hasattr(result, 'items')
        assert len(result.items) == 1
        assert hasattr(result, 'total_refund')
        assert result.total_refund == 39.99 * 3
    
    def test_return_update_with_status(self, mocker):
        """Test return update with status change."""
        mocker.patch(
            'app.sales.schemas.returns_schema.ReferenceData.is_valid_return_status',
            return_value=True
        )
        
        schema = ReturnUpdateSchema()
        data = {
            'status': 'approved'
        }
        
        result = schema.load(data)
        
        assert hasattr(result, 'status')
        assert result.status == 'approved'
    
    def test_return_update_with_invalid_status(self, mocker):
        """Test return update with invalid status."""
        mocker.patch(
            'app.sales.schemas.returns_schema.ReferenceData.is_valid_return_status',
            return_value=False
        )
        
        schema = ReturnUpdateSchema()
        data = {
            'status': 'bogus_status'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'status' in exc_info.value.messages


@pytest.mark.unit
@pytest.mark.sales
class TestReturnStatusUpdateSchema:
    """Test ReturnStatusUpdateSchema validation."""
    
    def test_status_update_with_valid_status(self, mocker):
        """Test status-only update with valid status."""
        mocker.patch(
            'app.sales.schemas.returns_schema.ReferenceData.is_valid_return_status',
            return_value=True
        )
        
        schema = ReturnStatusUpdateSchema()
        data = {'status': 'approved'}
        
        result = schema.load(data)
        
        assert result['status'] == 'approved'
    
    def test_status_update_with_invalid_status(self, mocker):
        """Test status-only update with invalid status."""
        mocker.patch(
            'app.sales.schemas.returns_schema.ReferenceData.is_valid_return_status',
            return_value=False
        )
        
        schema = ReturnStatusUpdateSchema()
        data = {'status': 'invalid'}
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'status' in exc_info.value.messages
    
    def test_status_update_missing_status(self):
        """Test status-only update without status field."""
        schema = ReturnStatusUpdateSchema()
        data = {}
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'status' in exc_info.value.messages


@pytest.mark.unit
@pytest.mark.sales
class TestReturnResponseSchema:
    """Test ReturnResponseSchema serialization."""
    
    def test_return_response_serialization(self, mocker):
        """Test return response with status name conversion."""
        from datetime import datetime
        
        # Create a mock return object
        mock_return = mocker.Mock()
        mock_return.id = 1
        mock_return.user_id = 1
        mock_return.order_id = 1
        mock_return.total_refund = 99.98
        mock_return.created_at = datetime(2024, 1, 15, 10, 30, 0)
        mock_return.return_status_id = 1
        mock_return.items = []
        
        mocker.patch(
            'app.sales.schemas.returns_schema.ReferenceData.get_return_status_name',
            return_value='Pending'
        )
        
        schema = ReturnResponseSchema()
        result = schema.dump(mock_return)
        
        # Verify basic fields
        assert result['id'] == 1
        assert result['user_id'] == 1
        assert result['order_id'] == 1
        assert result['total_refund'] == 99.98
        
        # Verify status converted to name
        assert result['status'] == 'Pending'
    
    def test_return_response_with_none_status(self, mocker):
        """Test return response with missing status."""
        from datetime import datetime
        
        mock_return = mocker.Mock()
        mock_return.id = 1
        mock_return.user_id = 1
        mock_return.order_id = 1
        mock_return.total_refund = 50.00
        mock_return.created_at = datetime(2024, 1, 15, 10, 30, 0)
        mock_return.return_status_id = None
        mock_return.items = []
        
        schema = ReturnResponseSchema()
        result = schema.dump(mock_return)
        
        # Should handle None gracefully
        assert result['status'] is None
