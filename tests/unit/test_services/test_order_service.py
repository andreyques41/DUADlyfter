"""
Unit tests for OrderService.

Tests all order management operations including CRUD operations,
status management, cart integration, and order validation.
"""
from datetime import datetime
from unittest.mock import Mock
import pytest
from app.sales.services.order_service import OrderService
from app.sales.models.order import Order, OrderItem


@pytest.fixture
def service():
    """Create OrderService instance for testing."""
    return OrderService()


@pytest.fixture
def mock_order():
    """Create a mock order object."""
    order = Mock(spec=Order)
    order.id = 1
    order.user_id = 100
    order.cart_id = 10
    order.order_status_id = 1
    order.total_amount = 99.99
    order.shipping_address = "123 Main St"
    order.created_at = datetime(2024, 1, 1, 12, 0, 0)
    order.items = []
    return order


@pytest.fixture
def mock_order_with_items():
    """Create a mock order with items."""
    order = Mock(spec=Order)
    order.id = 1
    order.user_id = 100
    order.cart_id = 10
    order.order_status_id = 1
    order.total_amount = 75.97
    
    item1 = Mock(spec=OrderItem)
    item1.product_id = 10
    item1.quantity = 2
    item1.amount = 59.98
    
    item2 = Mock(spec=OrderItem)
    item2.product_id = 20
    item2.quantity = 1
    item2.amount = 15.99
    
    order.items = [item1, item2]
    return order


@pytest.fixture
def mock_cart():
    """Create a mock cart."""
    cart = Mock()
    cart.id = 10
    cart.user_id = 100
    cart.finalized = False
    return cart


# ========== ORDER RETRIEVAL TESTS ==========
class TestOrderServiceRetrieval:
    """Test order retrieval operations."""
    
    def test_get_order_by_id_success(self, mocker, service, mock_order):
        """Test successful retrieval of order by ID."""
        mocker.patch.object(service.repository, 'get_by_id', return_value=mock_order)
        
        result = service.get_order_by_id(1)
        
        assert result == mock_order
        service.repository.get_by_id.assert_called_once_with(1)
    
    def test_get_order_by_id_not_found(self, mocker, service):
        """Test retrieving non-existent order by ID."""
        mocker.patch.object(service.repository, 'get_by_id', return_value=None)
        
        result = service.get_order_by_id(999)
        
        assert result is None
    
    def test_get_orders_by_user_id(self, mocker, service, mock_order):
        """Test retrieving orders by user ID."""
        orders = [mock_order, Mock(spec=Order)]
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=orders)
        
        result = service.get_orders_by_user_id(100)
        
        assert result == orders
        assert len(result) == 2
        service.repository.get_by_user_id.assert_called_once_with(100)
    
    def test_get_order_by_cart_id(self, mocker, service, mock_order):
        """Test retrieving order by cart ID."""
        mocker.patch.object(service.repository, 'get_by_cart_id', return_value=mock_order)
        
        result = service.get_order_by_cart_id(10)
        
        assert result == mock_order
        service.repository.get_by_cart_id.assert_called_once_with(10)
    
    def test_get_all_orders(self, mocker, service, mock_order):
        """Test retrieving all orders."""
        orders = [mock_order, Mock(spec=Order), Mock(spec=Order)]
        mocker.patch.object(service.repository, 'get_all', return_value=orders)
        
        result = service.get_all_orders()
        
        assert result == orders
        assert len(result) == 3
    
    def test_get_orders_by_filters(self, mocker, service, mock_order):
        """Test retrieving orders by filters."""
        orders = [mock_order]
        filters = {'user_id': 100, 'order_status_id': 1}
        mocker.patch.object(service.repository, 'get_by_filters', return_value=orders)
        
        result = service.get_orders_by_filters(filters)
        
        assert result == orders
        service.repository.get_by_filters.assert_called_once_with(filters)


# ========== ORDER CREATION TESTS ==========
class TestOrderServiceCreation:
    """Test order creation operations."""
    
    def test_create_order_success_with_cart_id(self, mocker, service, mock_cart):
        """Test successful order creation with provided cart_id."""
        # Mock Order and OrderItem classes
        mock_order_instance = Mock(spec=Order)
        mock_order_instance.items = []
        mock_order_instance.total_amount = 75.97
        mock_order_instance.cart_id = 10
        mocker.patch('app.sales.services.order_service.Order', return_value=mock_order_instance)
        mocker.patch('app.sales.services.order_service.OrderItem')
        
        # Mock ReferenceData for status conversion
        mocker.patch('app.sales.services.order_service.ReferenceData.get_order_status_id', return_value=1)
        
        # Mock validation
        mocker.patch.object(service, '_validate_total_integrity', return_value=[])
        
        # Mock repository
        created_order = Mock(spec=Order)
        created_order.id = 1
        created_order.cart_id = 10
        mocker.patch.object(service.repository, 'create', return_value=created_order)
        
        # Mock CartService (imported inside create_order)
        cart_service_mock = Mock()
        cart_service_mock.finalize_cart.return_value = mock_cart
        mocker.patch('app.sales.services.cart_service.CartService', return_value=cart_service_mock)
        
        order_data = {
            'user_id': 100,
            'cart_id': 10,
            'status': 'pending',
            'shipping_address': '123 Main St',
            'items': [
                {'product_id': 10, 'quantity': 2, 'amount': 59.98},
                {'product_id': 20, 'quantity': 1, 'amount': 15.99}
            ]
        }
        
        result = service.create_order(**order_data)
        
        assert result == created_order
        service.repository.create.assert_called_once()
        cart_service_mock.finalize_cart.assert_called_once_with(10)
    
    def test_create_order_converts_status_name(self, mocker, service):
        """Test that create_order converts status name to ID."""
        mock_order_instance = Mock(spec=Order)
        mock_order_instance.items = []
        mocker.patch('app.sales.services.order_service.Order', return_value=mock_order_instance)
        mocker.patch('app.sales.services.order_service.OrderItem')
        
        mock_ref_data = mocker.patch('app.sales.services.order_service.ReferenceData.get_order_status_id', return_value=2)
        mocker.patch.object(service, '_validate_total_integrity', return_value=[])
        
        created_order = Mock(spec=Order)
        created_order.cart_id = 10
        mocker.patch.object(service.repository, 'create', return_value=created_order)
        
        cart_service_mock = Mock()
        cart_service_mock.finalize_cart.return_value = Mock()
        mocker.patch('app.sales.services.cart_service.CartService', return_value=cart_service_mock)
        
        service.create_order(
            user_id=100,
            cart_id=10,
            status='shipped',
            items=[{'product_id': 10, 'quantity': 1, 'amount': 29.99}]
        )
        
        mock_ref_data.assert_called_once_with('shipped')
    
    def test_create_order_invalid_status(self, mocker, service):
        """Test order creation with invalid status."""
        mocker.patch('app.sales.services.order_service.ReferenceData.get_order_status_id', return_value=None)
        
        result = service.create_order(
            user_id=100,
            status='invalid_status',
            items=[{'product_id': 10, 'quantity': 1, 'amount': 29.99}]
        )
        
        assert result is None
    
    def test_create_order_without_user_id(self, mocker, service):
        """Test order creation without user_id."""
        mocker.patch('app.sales.services.order_service.ReferenceData.get_order_status_id', return_value=1)
        
        result = service.create_order(
            status='pending',
            items=[{'product_id': 10, 'quantity': 1, 'amount': 29.99}]
        )
        
        assert result is None
    
    def test_create_order_without_items(self, mocker, service):
        """Test order creation without items."""
        mocker.patch('app.sales.services.order_service.ReferenceData.get_order_status_id', return_value=1)
        
        result = service.create_order(
            user_id=100,
            status='pending',
            items=[]
        )
        
        assert result is None
    
    def test_create_order_creates_cart_if_needed(self, mocker, service):
        """Test that order creation creates cart if cart_id not provided."""
        # Mock Order
        mock_order_instance = Mock(spec=Order)
        mock_order_instance.items = []
        mocker.patch('app.sales.services.order_service.Order', return_value=mock_order_instance)
        mocker.patch('app.sales.services.order_service.OrderItem')
        
        mocker.patch('app.sales.services.order_service.ReferenceData.get_order_status_id', return_value=1)
        mocker.patch.object(service, '_validate_total_integrity', return_value=[])
        
        # Mock CartService (imported inside the function)
        cart_service_mock = Mock()
        new_cart = Mock()
        new_cart.id = 20
        cart_service_mock.get_cart_by_user_id.return_value = None  # No existing cart
        cart_service_mock.create_cart.return_value = new_cart
        cart_service_mock.finalize_cart.return_value = new_cart
        mocker.patch('app.sales.services.cart_service.CartService', return_value=cart_service_mock)
        
        created_order = Mock(spec=Order)
        created_order.cart_id = 20
        mocker.patch.object(service.repository, 'create', return_value=created_order)
        
        result = service.create_order(
            user_id=100,
            status='pending',
            items=[{'product_id': 10, 'quantity': 1, 'amount': 29.99}]
        )
        
        assert result == created_order
        cart_service_mock.create_cart.assert_called_once()
    
    def test_create_order_validation_failure(self, mocker, service):
        """Test order creation with validation failure."""
        mock_order_instance = Mock(spec=Order)
        mock_order_instance.items = []
        mocker.patch('app.sales.services.order_service.Order', return_value=mock_order_instance)
        mocker.patch('app.sales.services.order_service.OrderItem')
        
        mocker.patch('app.sales.services.order_service.ReferenceData.get_order_status_id', return_value=1)
        mocker.patch.object(service, '_validate_total_integrity', return_value=['Total mismatch'])
        
        result = service.create_order(
            user_id=100,
            cart_id=10,
            status='pending',
            items=[{'product_id': 10, 'quantity': 1, 'amount': 29.99}]
        )
        
        assert result is None
    
    def test_create_order_handles_exception(self, mocker, service):
        """Test order creation handles exceptions."""
        mocker.patch(
            'app.sales.services.order_service.ReferenceData.get_order_status_id',
            side_effect=Exception("Database error")
        )
        
        result = service.create_order(
            user_id=100,
            status='pending',
            items=[{'product_id': 10, 'quantity': 1, 'amount': 29.99}]
        )
        
        assert result is None


# ========== ORDER UPDATE TESTS ==========
class TestOrderServiceUpdate:
    """Test order update operations."""
    
    def test_update_order_success(self, mocker, service, mock_order):
        """Test successful order update."""
        mocker.patch.object(service.repository, 'get_by_id', return_value=mock_order)
        mocker.patch.object(service, 'validate_order_data', return_value=[])
        mocker.patch.object(service, '_validate_total_integrity', return_value=[])
        
        updated_order = Mock(spec=Order)
        mocker.patch.object(service.repository, 'update', return_value=updated_order)
        
        result = service.update_order(1, shipping_address='456 Oak Ave')
        
        assert result == updated_order
        assert mock_order.shipping_address == '456 Oak Ave'
    
    def test_update_order_not_found(self, mocker, service):
        """Test updating non-existent order."""
        mocker.patch.object(service.repository, 'get_by_id', return_value=None)
        
        result = service.update_order(999, shipping_address='456 Oak Ave')
        
        assert result is None
    
    def test_update_order_with_status_conversion(self, mocker, service, mock_order):
        """Test updating order with status name conversion."""
        mocker.patch.object(service.repository, 'get_by_id', return_value=mock_order)
        mocker.patch('app.sales.services.order_service.ReferenceData.get_order_status_id', return_value=2)
        mocker.patch.object(service, 'validate_order_data', return_value=[])
        mocker.patch.object(service, '_validate_total_integrity', return_value=[])
        
        updated_order = Mock(spec=Order)
        mocker.patch.object(service.repository, 'update', return_value=updated_order)
        
        result = service.update_order(1, status='shipped')
        
        assert result == updated_order
        assert mock_order.order_status_id == 2
    
    def test_update_order_with_invalid_status(self, mocker, service, mock_order):
        """Test updating order with invalid status."""
        mocker.patch.object(service.repository, 'get_by_id', return_value=mock_order)
        mocker.patch('app.sales.services.order_service.ReferenceData.get_order_status_id', return_value=None)
        
        result = service.update_order(1, status='invalid_status')
        
        assert result is None
    
    def test_update_order_with_items(self, mocker, service, mock_order):
        """Test updating order items."""
        # Create mockable items list
        mock_items_list = Mock()
        mock_order.items = mock_items_list
        
        mocker.patch.object(service.repository, 'get_by_id', return_value=mock_order)
        mocker.patch('app.core.database.get_db', return_value=Mock())
        mocker.patch('app.sales.services.order_service.OrderItem')
        mocker.patch.object(service, 'validate_order_data', return_value=[])
        mocker.patch.object(service, '_validate_total_integrity', return_value=[])
        
        updated_order = Mock(spec=Order)
        mocker.patch.object(service.repository, 'update', return_value=updated_order)
        
        new_items = [
            {'product_id': 30, 'quantity': 3, 'amount': 89.97}
        ]
        
        result = service.update_order(1, items=new_items)
        
        assert result == updated_order
        assert mock_order.total_amount == 89.97
        mock_items_list.clear.assert_called_once()
    
    def test_update_order_validation_failure(self, mocker, service, mock_order):
        """Test order update with validation failure."""
        mocker.patch.object(service.repository, 'get_by_id', return_value=mock_order)
        mocker.patch.object(service, 'validate_order_data', return_value=['Validation error'])
        
        result = service.update_order(1, shipping_address='456 Oak Ave')
        
        assert result is None
    
    def test_update_order_handles_exception(self, mocker, service, mock_order):
        """Test order update handles exceptions."""
        mocker.patch.object(service.repository, 'get_by_id', return_value=mock_order)
        mocker.patch.object(
            service.repository,
            'update',
            side_effect=Exception("Database error")
        )
        mocker.patch.object(service, 'validate_order_data', return_value=[])
        mocker.patch.object(service, '_validate_total_integrity', return_value=[])
        
        result = service.update_order(1, shipping_address='456 Oak Ave')
        
        assert result is None


# ========== ORDER DELETION TESTS ==========
class TestOrderServiceDeletion:
    """Test order deletion operations."""
    
    def test_delete_order_success(self, mocker, service, mock_order):
        """Test successful order deletion."""
        # Mock order with deletable status
        mock_status = Mock()
        mock_status.status = 'pending'
        mock_order.status = mock_status
        
        mocker.patch.object(service.repository, 'get_by_id', return_value=mock_order)
        mocker.patch.object(service.repository, 'delete', return_value=True)
        
        result = service.delete_order(1)
        
        assert result is True
        service.repository.delete.assert_called_once_with(1)
    
    def test_delete_order_not_found(self, mocker, service):
        """Test deleting non-existent order."""
        mocker.patch.object(service.repository, 'get_by_id', return_value=None)
        
        result = service.delete_order(999)
        
        assert result is False
    
    def test_delete_order_wrong_status(self, mocker, service, mock_order):
        """Test deleting order with non-deletable status."""
        mock_status = Mock()
        mock_status.status = 'Shipped'
        mock_order.status = mock_status
        
        mocker.patch.object(service.repository, 'get_by_id', return_value=mock_order)
        
        result = service.delete_order(1)
        
        assert result is False
    
    def test_delete_order_handles_exception(self, mocker, service, mock_order):
        """Test order deletion handles exceptions."""
        mocker.patch.object(service.repository, 'get_by_id', return_value=mock_order)
        mocker.patch.object(
            service.repository,
            'delete',
            side_effect=Exception("Database error")
        )
        
        result = service.delete_order(1)
        
        assert result is False


# ========== ORDER STATUS MANAGEMENT TESTS ==========
class TestOrderServiceStatusManagement:
    """Test order status management operations."""
    
    def test_update_order_status_success(self, mocker, service, mock_order):
        """Test successful status update."""
        mocker.patch('app.sales.services.order_service.ReferenceData.get_order_status_id', return_value=2)
        mocker.patch.object(service, 'update_order', return_value=mock_order)
        
        result = service.update_order_status(1, 'shipped')
        
        assert result == mock_order
        service.update_order.assert_called_once_with(1, order_status_id=2)
    
    def test_update_order_status_invalid(self, mocker, service):
        """Test status update with invalid status."""
        mocker.patch('app.sales.services.order_service.ReferenceData.get_order_status_id', return_value=None)
        
        result = service.update_order_status(1, 'invalid_status')
        
        assert result is None
    
    def test_get_status_id_by_name(self, mocker, service):
        """Test getting status ID by name."""
        mocker.patch('app.sales.services.order_service.ReferenceData.get_order_status_id', return_value=3)
        
        result = service.get_status_id_by_name('delivered')
        
        assert result == 3


# ========== VALIDATION TESTS ==========
class TestOrderServiceValidation:
    """Test order validation methods."""
    
    def test_validate_order_data_valid(self, service, mock_order_with_items):
        """Test validation with valid order."""
        mock_order_with_items.cart_id = 10
        mock_order_with_items.user_id = 100
        mock_order_with_items.order_status_id = 1
        mock_order_with_items.total_amount = 75.97
        
        # Set up items properly
        for item in mock_order_with_items.items:
            item.product_id = item.product_id
            item.quantity = item.quantity
            item.amount = item.amount
        
        errors = service.validate_order_data(mock_order_with_items)
        
        assert errors == []
    
    def test_validate_order_data_missing_cart_id(self, service, mock_order):
        """Test validation with missing cart_id."""
        mock_order.cart_id = None
        
        errors = service.validate_order_data(mock_order, require_cart_id=True)
        
        assert 'cart_id is required' in errors
    
    def test_validate_order_data_cart_id_not_required(self, service, mock_order):
        """Test validation without requiring cart_id."""
        mock_order.cart_id = None
        mock_order.user_id = 100
        mock_order.order_status_id = 1
        mock_order.total_amount = 99.99
        mock_order.items = []
        
        errors = service.validate_order_data(mock_order, require_cart_id=False)
        
        assert 'cart_id is required' not in errors
    
    def test_validate_order_data_negative_total(self, service, mock_order):
        """Test validation with negative total."""
        mock_order.total_amount = -10.0
        
        errors = service.validate_order_data(mock_order)
        
        assert 'total_amount must be non-negative' in errors
    
    def test_validate_order_data_invalid_items(self, service, mock_order):
        """Test validation with invalid items."""
        bad_item = Mock(spec=OrderItem)
        bad_item.product_id = None
        bad_item.quantity = -1
        bad_item.amount = -5.0
        
        mock_order.items = [bad_item]
        
        errors = service.validate_order_data(mock_order)
        
        assert any('product_id is required' in err for err in errors)
        assert any('quantity must be positive' in err for err in errors)
        assert any('amount must be non-negative' in err for err in errors)
    
    def test_order_exists_by_cart(self, mocker, service):
        """Test checking if order exists for cart."""
        mocker.patch.object(service.repository, 'exists_by_cart_id', return_value=True)
        
        result = service.order_exists_by_cart(10)
        
        assert result is True
        service.repository.exists_by_cart_id.assert_called_once_with(10)
