"""
Unit tests for CartService.

Tests all cart management operations including CRUD operations, 
item management (add/update/remove), cart finalization, and validation.
"""
from datetime import datetime
from unittest.mock import Mock
import pytest
from app.sales.services.cart_service import CartService
from app.sales.models.cart import Cart, CartItem


@pytest.fixture
def service():
    """Create CartService instance for testing."""
    return CartService()


@pytest.fixture
def mock_cart():
    """Create a mock cart object."""
    cart = Mock(spec=Cart)
    cart.id = 1
    cart.user_id = 100
    cart.finalized = False
    cart.created_at = datetime(2024, 1, 1, 12, 0, 0)
    cart.items = []
    return cart


@pytest.fixture
def mock_cart_with_items():
    """Create a mock cart with items."""
    cart = Mock(spec=Cart)
    cart.id = 1
    cart.user_id = 100
    cart.finalized = False
    
    item1 = Mock(spec=CartItem)
    item1.id = 1
    item1.product_id = 10
    item1.quantity = 2
    item1.amount = 59.98
    
    item2 = Mock(spec=CartItem)
    item2.id = 2
    item2.product_id = 20
    item2.quantity = 1
    item2.amount = 15.99
    
    cart.items = [item1, item2]
    return cart


@pytest.fixture
def mock_product():
    """Create a mock product."""
    product = Mock()
    product.id = 10
    product.name = "Dog Food"
    product.price = 29.99
    product.is_active = True
    product.stock_quantity = 50
    return product


# ========== CART RETRIEVAL TESTS ==========
class TestCartServiceRetrieval:
    """Test cart retrieval operations."""
    
    def test_get_cart_by_id_success(self, mocker, service, mock_cart):
        """Test successful retrieval of cart by ID."""
        mocker.patch.object(service.repository, 'get_by_id', return_value=mock_cart)
        
        result = service.get_cart_by_id(1)
        
        assert result == mock_cart
        service.repository.get_by_id.assert_called_once_with(1)
    
    def test_get_cart_by_id_not_found(self, mocker, service):
        """Test retrieving non-existent cart by ID."""
        mocker.patch.object(service.repository, 'get_by_id', return_value=None)
        
        result = service.get_cart_by_id(999)
        
        assert result is None
        service.repository.get_by_id.assert_called_once_with(999)
    
    def test_get_cart_by_user_id_success(self, mocker, service, mock_cart):
        """Test successful retrieval of cart by user ID."""
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=mock_cart)
        
        result = service.get_cart_by_user_id(100)
        
        assert result == mock_cart
        service.repository.get_by_user_id.assert_called_once_with(100)
    
    def test_get_cart_by_user_id_not_found(self, mocker, service):
        """Test retrieving cart for user without cart."""
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=None)
        
        result = service.get_cart_by_user_id(999)
        
        assert result is None
    
    def test_get_all_carts(self, mocker, service, mock_cart):
        """Test retrieving all carts."""
        carts = [mock_cart, Mock(spec=Cart)]
        mocker.patch.object(service.repository, 'get_all', return_value=carts)
        
        result = service.get_all_carts()
        
        assert result == carts
        assert len(result) == 2
        service.repository.get_all.assert_called_once()
    
    def test_get_all_carts_empty(self, mocker, service):
        """Test retrieving all carts when none exist."""
        mocker.patch.object(service.repository, 'get_all', return_value=[])
        
        result = service.get_all_carts()
        
        assert result == []


# ========== CART CREATION TESTS ==========
class TestCartServiceCreation:
    """Test cart creation operations."""
    
    def test_create_cart_success(self, mocker, service):
        """Test successful cart creation."""
        # Mock Cart class to avoid SQLAlchemy issues
        mock_cart_instance = Mock(spec=Cart)
        mock_cart_instance.items = []
        mock_cart_class = mocker.patch('app.sales.services.cart_service.Cart')
        mock_cart_class.return_value = mock_cart_instance
        
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=None)
        mocker.patch.object(service.repository, 'create', return_value=mock_cart_instance)
        
        cart_data = {
            'user_id': 100,
            'items': [
                {'product_id': 10, 'quantity': 2, 'amount': 59.98}
            ]
        }
        
        result = service.create_cart(**cart_data)
        
        assert result == mock_cart_instance
        service.repository.create.assert_called_once()
    
    def test_create_cart_without_user_id(self, mocker, service):
        """Test cart creation without user_id returns None."""
        result = service.create_cart(finalized=False)
        
        assert result is None
    
    def test_create_cart_duplicate_prevented(self, mocker, service, mock_cart):
        """Test that duplicate cart creation is prevented."""
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=mock_cart)
        mock_create = mocker.patch.object(service.repository, 'create')
        
        result = service.create_cart(user_id=100)
        
        assert result is None
        mock_create.assert_not_called()
    
    def test_create_cart_with_force_create(self, mocker, service):
        """Test cart creation with force_create bypasses duplicate check."""
        mock_cart_instance = Mock(spec=Cart)
        mock_cart_instance.items = []
        mock_cart_class = mocker.patch('app.sales.services.cart_service.Cart')
        mock_cart_class.return_value = mock_cart_instance
        
        existing_cart = Mock(spec=Cart)
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=existing_cart)
        mocker.patch.object(service.repository, 'create', return_value=mock_cart_instance)
        
        result = service.create_cart(force_create=True, user_id=100)
        
        assert result == mock_cart_instance
        service.repository.create.assert_called_once()
    
    def test_create_cart_with_items(self, mocker, service):
        """Test cart creation with multiple items."""
        mock_cart_instance = Mock(spec=Cart)
        mock_cart_instance.items = []
        mock_cart_class = mocker.patch('app.sales.services.cart_service.Cart')
        mock_cart_class.return_value = mock_cart_instance
        
        mock_cart_item_class = mocker.patch('app.sales.services.cart_service.CartItem')
        
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=None)
        mocker.patch.object(service.repository, 'create', return_value=mock_cart_instance)
        
        cart_data = {
            'user_id': 100,
            'items': [
                {'product_id': 10, 'quantity': 2, 'amount': 59.98},
                {'product_id': 20, 'quantity': 1, 'amount': 15.99}
            ]
        }
        
        result = service.create_cart(**cart_data)
        
        assert result == mock_cart_instance
        assert mock_cart_item_class.call_count == 2
    
    def test_create_cart_sets_defaults(self, mocker, service):
        """Test that create_cart sets default values."""
        mock_cart_instance = Mock(spec=Cart)
        mock_cart_instance.items = []
        mock_cart_class = mocker.patch('app.sales.services.cart_service.Cart')
        mock_cart_class.return_value = mock_cart_instance
        
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=None)
        mocker.patch.object(service.repository, 'create', return_value=mock_cart_instance)
        
        result = service.create_cart(user_id=100)
        
        # Check that Cart was called with defaults
        call_args = mock_cart_class.call_args[1]
        assert call_args['user_id'] == 100
        assert call_args['finalized'] is False
        assert 'created_at' in call_args
    
    def test_create_cart_handles_exception(self, mocker, service):
        """Test cart creation handles exceptions."""
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=None)
        mocker.patch.object(
            service.repository,
            'create',
            side_effect=Exception("Database error")
        )
        
        # Mock Cart to avoid instantiation error
        mock_cart_instance = Mock(spec=Cart)
        mock_cart_instance.items = []
        mocker.patch('app.sales.services.cart_service.Cart', return_value=mock_cart_instance)
        
        result = service.create_cart(user_id=100)
        
        assert result is None


# ========== CART UPDATE TESTS ==========
class TestCartServiceUpdate:
    """Test cart update operations."""
    
    def test_update_cart_success(self, mocker, service, mock_cart):
        """Test successful cart update."""
        updated_cart = Mock(spec=Cart)
        updated_cart.finalized = True
        
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=mock_cart)
        mocker.patch.object(service.repository, 'update', return_value=updated_cart)
        
        result = service.update_cart(100, finalized=True)
        
        assert result == updated_cart
        assert mock_cart.finalized is True
        service.repository.update.assert_called_once_with(mock_cart)
    
    def test_update_cart_not_found(self, mocker, service):
        """Test updating non-existent cart."""
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=None)
        mock_update = mocker.patch.object(service.repository, 'update')
        
        result = service.update_cart(999, finalized=True)
        
        assert result is None
        mock_update.assert_not_called()
    
    def test_update_cart_with_items(self, mocker, service):
        """Test updating cart items."""
        # Create a fresh mock cart with mockable items list
        mock_cart = Mock(spec=Cart)
        mock_cart.finalized = False
        mock_items_list = Mock()
        mock_cart.items = mock_items_list
        
        # Mock get_db (imported inside update_cart function)
        mock_db = Mock()
        mocker.patch('app.core.database.get_db', return_value=mock_db)
        
        mock_cart_item_class = mocker.patch('app.sales.services.cart_service.CartItem')
        
        updated_cart = Mock(spec=Cart)
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=mock_cart)
        mocker.patch.object(service.repository, 'update', return_value=updated_cart)
        
        new_items = [
            {'product_id': 30, 'quantity': 3, 'amount': 89.97}
        ]
        
        result = service.update_cart(100, items=new_items)
        
        assert result == updated_cart
        mock_items_list.clear.assert_called_once()
        mock_db.flush.assert_called_once()
        mock_cart_item_class.assert_called_once()
    
    def test_update_cart_handles_exception(self, mocker, service, mock_cart):
        """Test cart update handles exceptions."""
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=mock_cart)
        mocker.patch.object(
            service.repository,
            'update',
            side_effect=Exception("Update failed")
        )
        
        result = service.update_cart(100, finalized=True)
        
        assert result is None


# ========== CART DELETION TESTS ==========
class TestCartServiceDeletion:
    """Test cart deletion operations."""
    
    def test_delete_cart_success(self, mocker, service):
        """Test successful cart deletion."""
        mocker.patch.object(service.repository, 'delete_by_user_id', return_value=True)
        
        result = service.delete_cart(100)
        
        assert result is True
        service.repository.delete_by_user_id.assert_called_once_with(100)
    
    def test_delete_cart_not_found(self, mocker, service):
        """Test deleting non-existent cart."""
        mocker.patch.object(service.repository, 'delete_by_user_id', return_value=False)
        
        result = service.delete_cart(999)
        
        assert result is False
    
    def test_delete_cart_handles_exception(self, mocker, service):
        """Test cart deletion handles exceptions."""
        mocker.patch.object(
            service.repository,
            'delete_by_user_id',
            side_effect=Exception("Delete failed")
        )
        
        result = service.delete_cart(100)
        
        assert result is False


# ========== ADD ITEM TO CART TESTS ==========
class TestCartServiceAddItem:
    """Test adding items to cart."""
    
    def test_add_item_to_existing_cart_success(self, mocker, service, mock_product):
        """Test adding item to existing cart."""
        # Create mockable cart with items list
        mock_cart = Mock(spec=Cart)
        mock_cart.finalized = False
        mock_cart.id = 1
        mock_items_list = []
        mock_cart.items = mock_items_list
        
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=mock_cart)
        
        # Mock ProductService (imported inside add_item_to_cart)
        product_service_mock = Mock()
        product_service_mock.get_product_by_id.return_value = mock_product
        mocker.patch('app.products.services.ProductService', return_value=product_service_mock)
        
        # Don't mock CartItem - let it be created normally or just verify updated cart
        
        updated_cart = Mock(spec=Cart)
        mocker.patch.object(service.repository, 'update', return_value=updated_cart)
        
        result = service.add_item_to_cart(100, 10, 2)
        
        assert result == updated_cart
        product_service_mock.get_product_by_id.assert_called_once_with(10)
        service.repository.update.assert_called_once()
    
    def test_add_item_creates_cart_if_not_exists(self, mocker, service, mock_product):
        """Test adding item creates cart if user has no cart."""
        # First call returns None (no cart), second call returns created cart
        new_cart = Mock(spec=Cart)
        new_cart.id = 1
        new_cart.finalized = False
        new_cart.items = []
        
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=None)
        
        # Mock Cart class
        mock_cart_instance = Mock(spec=Cart)
        mock_cart_instance.finalized = False
        mock_cart_instance.items = []
        mocker.patch('app.sales.services.cart_service.Cart', return_value=mock_cart_instance)
        
        mocker.patch.object(service.repository, 'create', return_value=new_cart)
        
        product_service_mock = Mock()
        product_service_mock.get_product_by_id.return_value = mock_product
        mocker.patch('app.products.services.ProductService', return_value=product_service_mock)
        
        mocker.patch('app.sales.services.cart_service.CartItem')
        mocker.patch.object(service.repository, 'update', return_value=new_cart)
        
        result = service.add_item_to_cart(100, 10, 2)
        
        assert result == new_cart
        service.repository.create.assert_called_once()
    
    def test_add_item_product_not_found(self, mocker, service, mock_cart):
        """Test adding non-existent product."""
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=mock_cart)
        
        product_service_mock = Mock()
        product_service_mock.get_product_by_id.return_value = None
        mocker.patch('app.products.services.ProductService', return_value=product_service_mock)
        
        result = service.add_item_to_cart(100, 999, 1)
        
        assert result is None
    
    def test_add_item_to_finalized_cart(self, mocker, service, mock_cart):
        """Test adding item to finalized cart returns None."""
        mock_cart.finalized = True
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=mock_cart)
        
        result = service.add_item_to_cart(100, 10, 1)
        
        assert result is None
    
    def test_add_item_inactive_product(self, mocker, service, mock_cart, mock_product):
        """Test adding inactive product."""
        mock_product.is_active = False
        
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=mock_cart)
        
        product_service_mock = Mock()
        product_service_mock.get_product_by_id.return_value = mock_product
        mocker.patch('app.products.services.ProductService', return_value=product_service_mock)
        
        result = service.add_item_to_cart(100, 10, 1)
        
        assert result is None
    
    def test_add_item_insufficient_stock(self, mocker, service, mock_cart, mock_product):
        """Test adding item with insufficient stock."""
        mock_product.stock_quantity = 1
        
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=mock_cart)
        
        product_service_mock = Mock()
        product_service_mock.get_product_by_id.return_value = mock_product
        mocker.patch('app.products.services.ProductService', return_value=product_service_mock)
        
        result = service.add_item_to_cart(100, 10, 10)  # Request 10, only 1 available
        
        assert result is None
    
    def test_add_item_updates_existing_item(self, mocker, service, mock_product):
        """Test adding item that already exists in cart updates quantity."""
        existing_item = Mock(spec=CartItem)
        existing_item.product_id = 10
        existing_item.quantity = 1
        existing_item.amount = 29.99
        
        cart = Mock(spec=Cart)
        cart.finalized = False
        cart.items = [existing_item]
        
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=cart)
        
        product_service_mock = Mock()
        product_service_mock.get_product_by_id.return_value = mock_product
        mocker.patch('app.products.services.ProductService', return_value=product_service_mock)
        
        updated_cart = Mock(spec=Cart)
        mocker.patch.object(service.repository, 'update', return_value=updated_cart)
        
        result = service.add_item_to_cart(100, 10, 2)
        
        assert result == updated_cart
        assert existing_item.quantity == 3  # 1 + 2
        assert existing_item.amount == 29.99 * 3
    
    def test_add_item_handles_exception(self, mocker, service, mock_cart):
        """Test add_item_to_cart handles exceptions."""
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=mock_cart)
        
        product_service_mock = Mock()
        product_service_mock.get_product_by_id.side_effect = Exception("Service error")
        mocker.patch('app.products.services.ProductService', return_value=product_service_mock)
        
        result = service.add_item_to_cart(100, 10, 1)
        
        assert result is None


# ========== UPDATE ITEM QUANTITY TESTS ==========
class TestCartServiceUpdateQuantity:
    """Test updating item quantity in cart."""
    
    def test_update_item_quantity_success(self, mocker, service, mock_product):
        """Test successful quantity update."""
        existing_item = Mock(spec=CartItem)
        existing_item.product_id = 10
        existing_item.quantity = 2
        existing_item.amount = 59.98
        
        cart = Mock(spec=Cart)
        cart.finalized = False
        cart.items = [existing_item]
        
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=cart)
        
        product_service_mock = Mock()
        product_service_mock.get_product_by_id.return_value = mock_product
        mocker.patch('app.products.services.product_service.ProductService', return_value=product_service_mock)
        
        updated_cart = Mock(spec=Cart)
        mocker.patch.object(service.repository, 'update', return_value=updated_cart)
        
        result = service.update_item_quantity(100, 10, 5)
        
        assert result == updated_cart
        assert existing_item.quantity == 5
        assert existing_item.amount == 29.99 * 5
    
    def test_update_item_quantity_cart_not_found(self, mocker, service):
        """Test updating quantity when cart doesn't exist."""
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=None)
        
        result = service.update_item_quantity(999, 10, 5)
        
        assert result is None
    
    def test_update_item_quantity_finalized_cart(self, mocker, service):
        """Test updating quantity in finalized cart."""
        cart = Mock(spec=Cart)
        cart.finalized = True
        
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=cart)
        
        result = service.update_item_quantity(100, 10, 5)
        
        assert result is None
    
    def test_update_item_quantity_item_not_in_cart(self, mocker, service):
        """Test updating quantity for item not in cart."""
        cart = Mock(spec=Cart)
        cart.finalized = False
        cart.items = []
        
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=cart)
        
        result = service.update_item_quantity(100, 999, 5)
        
        assert result is None
    
    def test_update_item_quantity_zero_removes_item(self, mocker, service):
        """Test that quantity 0 removes item from cart."""
        existing_item = Mock(spec=CartItem)
        existing_item.product_id = 10
        
        # Use mockable list
        mock_items_list = Mock()
        
        cart = Mock(spec=Cart)
        cart.finalized = False
        cart.items = mock_items_list
        # Need to make items iterable for the for loop
        mock_items_list.__iter__ = Mock(return_value=iter([existing_item]))
        
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=cart)
        
        updated_cart = Mock(spec=Cart)
        mocker.patch.object(service.repository, 'update', return_value=updated_cart)
        
        result = service.update_item_quantity(100, 10, 0)
        
        assert result == updated_cart
        mock_items_list.remove.assert_called_once_with(existing_item)
    
    def test_update_item_quantity_handles_exception(self, mocker, service):
        """Test update_item_quantity handles exceptions."""
        cart = Mock(spec=Cart)
        cart.finalized = False
        cart.items = []
        
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=cart)
        mocker.patch.object(
            service.repository,
            'update',
            side_effect=Exception("Update failed")
        )
        
        result = service.update_item_quantity(100, 10, 5)
        
        assert result is None


# ========== REMOVE ITEM FROM CART TESTS ==========
class TestCartServiceRemoveItem:
    """Test removing items from cart."""
    
    def test_remove_item_success(self, mocker, service, mock_cart_with_items):
        """Test successful item removal."""
        updated_cart = Mock(spec=Cart)
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=mock_cart_with_items)
        mocker.patch.object(service.repository, 'update', return_value=updated_cart)
        
        result = service.remove_item_from_cart(100, 10)
        
        assert result is True
        service.repository.update.assert_called_once()
    
    def test_remove_item_cart_not_found(self, mocker, service):
        """Test removing item when cart doesn't exist."""
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=None)
        
        result = service.remove_item_from_cart(999, 10)
        
        assert result is False
    
    def test_remove_item_not_in_cart(self, mocker, service, mock_cart):
        """Test removing item that's not in cart."""
        mock_cart.items = []
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=mock_cart)
        mock_update = mocker.patch.object(service.repository, 'update')
        
        result = service.remove_item_from_cart(100, 999)
        
        assert result is False
        mock_update.assert_not_called()
    
    def test_remove_item_handles_exception(self, mocker, service, mock_cart_with_items):
        """Test remove_item handles exceptions."""
        mocker.patch.object(service.repository, 'get_by_user_id', return_value=mock_cart_with_items)
        mocker.patch.object(
            service.repository,
            'update',
            side_effect=Exception("Remove failed")
        )
        
        result = service.remove_item_from_cart(100, 10)
        
        assert result is False


# ========== CART FINALIZATION TESTS ==========
class TestCartServiceFinalization:
    """Test cart finalization operations."""
    
    def test_finalize_cart_success(self, mocker, service, mock_cart):
        """Test successful cart finalization."""
        finalized_cart = Mock(spec=Cart)
        finalized_cart.finalized = True
        
        mocker.patch.object(service.repository, 'finalize_cart', return_value=finalized_cart)
        
        result = service.finalize_cart(1)
        
        assert result == finalized_cart
        service.repository.finalize_cart.assert_called_once_with(1)
    
    def test_finalize_cart_not_found(self, mocker, service):
        """Test finalizing non-existent cart."""
        mocker.patch.object(service.repository, 'finalize_cart', return_value=None)
        
        result = service.finalize_cart(999)
        
        assert result is None
    
    def test_finalize_cart_handles_exception(self, mocker, service):
        """Test finalize_cart handles exceptions."""
        mocker.patch.object(
            service.repository,
            'finalize_cart',
            side_effect=Exception("Finalize failed")
        )
        
        result = service.finalize_cart(1)
        
        assert result is None


# ========== VALIDATION HELPERS TESTS ==========
class TestCartServiceValidation:
    """Test cart validation helper methods."""
    
    def test_cart_exists_for_user_true(self, mocker, service):
        """Test cart_exists_for_user returns True when cart exists."""
        mocker.patch.object(service.repository, 'exists_by_user_id', return_value=True)
        
        result = service.cart_exists_for_user(100)
        
        assert result is True
        service.repository.exists_by_user_id.assert_called_once_with(100)
    
    def test_cart_exists_for_user_false(self, mocker, service):
        """Test cart_exists_for_user returns False when cart doesn't exist."""
        mocker.patch.object(service.repository, 'exists_by_user_id', return_value=False)
        
        result = service.cart_exists_for_user(999)
        
        assert result is False
    
    def test_check_user_access_admin_allowed(self, service):
        """Test admin user has access to any cart."""
        current_user = Mock(id=1)
        
        result = service.check_user_access(current_user, is_admin=True, user_id=999)
        
        assert result is True
    
    def test_check_user_access_owner_allowed(self, service):
        """Test cart owner has access to their cart."""
        current_user = Mock(id=100)
        
        result = service.check_user_access(current_user, is_admin=False, user_id=100)
        
        assert result is True
    
    def test_check_user_access_non_owner_denied(self, service):
        """Test non-owner without admin has no access."""
        current_user = Mock(id=1)
        
        result = service.check_user_access(current_user, is_admin=False, user_id=100)
        
        assert result is False
    
    def test_check_user_access_no_user_id_provided(self, service):
        """Test access check without user_id."""
        current_user = Mock(id=1)
        
        result = service.check_user_access(current_user, is_admin=False, user_id=None)
        
        assert result is False
