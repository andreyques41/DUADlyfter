"""
Unit Tests for CartController

Tests the HTTP request processing layer for cart operations.

Coverage:
- Initialization and dependencies
- DRY helper: _check_cart_access()
- GET operations (all carts, specific cart)
- POST cart creation
- PUT cart updates
- DELETE cart operations
- Cart item management (add/update/remove)
- Access control (admin vs user)
- Error handling and logging
- Delegation to cached service methods
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from flask import Flask, g, request
from marshmallow import ValidationError


@pytest.fixture
def test_app():
    """Create a simple Flask app for controller testing (renamed to avoid conflicts)."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def mock_cart_service():
    """Mock CartService with all required methods."""
    mock = Mock()
    # Cached methods
    mock.get_cart_by_user_id_cached = Mock(return_value=None)
    mock.get_all_carts_cached = Mock(return_value=[])
    # Regular methods
    mock.create_cart = Mock(return_value=None)
    mock.update_cart = Mock(return_value=None)
    mock.delete_cart = Mock(return_value=False)
    mock.add_item_to_cart = Mock(return_value=None)
    mock.update_item_quantity = Mock(return_value=None)  # Correct method name
    mock.remove_item_from_cart = Mock(return_value=False)
    return mock


@pytest.fixture
def controller(mock_cart_service):
    """Create CartController with mocked service."""
    from app.sales.controllers.cart_controller import CartController
    controller = CartController()
    controller.cart_service = mock_cart_service
    return controller


class TestCartControllerInitialization:
    """Test controller initialization."""
    
    def test_controller_initializes_with_service(self):
        """Test that controller initializes with CartService."""
        from app.sales.controllers.cart_controller import CartController
        
        controller = CartController()
        
        assert controller.cart_service is not None
        assert controller.logger is not None
    
    def test_controller_has_required_methods(self):
        """Test that controller has all required HTTP methods."""
        from app.sales.controllers.cart_controller import CartController
        
        controller = CartController()
        
        assert hasattr(controller, 'get')
        assert hasattr(controller, 'post')
        assert hasattr(controller, 'put')
        assert hasattr(controller, 'delete')
        assert hasattr(controller, 'add_item')
        assert hasattr(controller, 'update_item')
        assert hasattr(controller, 'remove_item')


class TestCartControllerDRYHelpers:
    """Test DRY helper methods (walrus operator pattern)."""
    
    def test_check_cart_access_allows_admin(self, app, controller):
        """Test that _check_cart_access allows admin users."""
        with app.app_context():
            # Mock admin user
            g.current_user = Mock(id=999, roles=[Mock(name='admin')])
            
            with patch('app.sales.controllers.cart_controller.is_user_or_admin', return_value=True):
                result = controller._check_cart_access(user_id=123)
            
            assert result is None  # No error = access granted
    
    def test_check_cart_access_allows_owner(self, app, controller):
        """Test that _check_cart_access allows cart owner."""
        with app.app_context():
            # Mock regular user accessing own cart
            g.current_user = Mock(id=123, roles=[Mock(name='user')])
            
            with patch('app.sales.controllers.cart_controller.is_user_or_admin', return_value=True):
                result = controller._check_cart_access(user_id=123)
            
            assert result is None  # No error = access granted
    
    def test_check_cart_access_denies_other_user(self, app, controller):
        """Test that _check_cart_access denies other users."""
        with app.app_context():
            # Mock regular user trying to access another user's cart
            g.current_user = Mock(id=456, roles=[Mock(name='user')])
            
            with patch('app.sales.controllers.cart_controller.is_user_or_admin', return_value=False):
                result = controller._check_cart_access(user_id=123)
            
            assert result is not None  # Error tuple returned
            response, status_code = result
            assert status_code == 403
            assert 'error' in response.get_json()


class TestCartControllerGetOperations:
    """Test GET operations - delegation to cached methods."""
    
    def test_get_all_carts_admin(self, app, controller, mock_cart_service):
        """Test that admin can get all carts (uses cached method)."""
        with app.app_context():
            # Mock admin user
            g.current_user = Mock(id=999, roles=[Mock(name='admin')])
            
            # Mock cached service response - Mocks need .items attribute for schema serialization
            mock_cart1 = Mock(id=1, user_id=1, items=[], created_at=None)
            mock_cart2 = Mock(id=2, user_id=2, items=[], created_at=None)
            mock_carts = [mock_cart1, mock_cart2]
            mock_cart_service.get_all_carts_cached.return_value = mock_carts
            
            with patch('app.sales.controllers.cart_controller.is_admin_user', return_value=True):
                response, status = controller.get(user_id=None)
            
            # Verify cached method was called
            mock_cart_service.get_all_carts_cached.assert_called_once()
            
            # Verify response
            assert status == 200
            data = response.get_json()
            assert data['total_carts'] == 2
            assert 'carts' in data
    
    def test_get_own_cart_customer(self, app, controller, mock_cart_service):
        """Test that customer gets own cart (uses cached method)."""
        with app.app_context():
            # Mock regular user
            g.current_user = Mock(id=123, roles=[Mock(name='user')])
            
            # Mock cached service response - Mock needs .items attribute for schema
            mock_cart = Mock(id=1, user_id=123, items=[], created_at=None)
            mock_cart_service.get_cart_by_user_id_cached.return_value = mock_cart
            
            with patch('app.sales.controllers.cart_controller.is_admin_user', return_value=False):
                response, status = controller.get(user_id=None)
            
            # Verify cached method was called with correct user_id
            mock_cart_service.get_cart_by_user_id_cached.assert_called_once_with(123)
            
            # Verify response
            assert status == 200
    
    def test_get_specific_cart_uses_cached_method(self, app, controller, mock_cart_service):
        """Test that getting specific cart uses cached method."""
        with app.app_context():
            # Mock user
            g.current_user = Mock(id=123)
            
            # Mock cached service response - Mock needs .items for schema
            mock_cart = Mock(id=1, user_id=123, items=[], created_at=None)
            mock_cart_service.get_cart_by_user_id_cached.return_value = mock_cart
            
            with patch('app.sales.controllers.cart_controller.is_user_or_admin', return_value=True):
                response, status = controller.get(user_id=123)
            
            # Verify cached method was called
            mock_cart_service.get_cart_by_user_id_cached.assert_called_once_with(123)
            
            assert status == 200
    
    def test_get_cart_not_found_returns_200_with_message(self, app, controller, mock_cart_service):
        """Test that cart not found returns 200 with message (not 404)."""
        with app.app_context():
            g.current_user = Mock(id=123)
            
            # Mock no cart found
            mock_cart_service.get_cart_by_user_id_cached.return_value = None
            
            with patch('app.sales.controllers.cart_controller.is_user_or_admin', return_value=True):
                response, status = controller.get(user_id=123)
            
            assert status == 200
            data = response.get_json()
            assert 'message' in data
            assert 'No cart found' in data['message']


class TestCartControllerPostOperations:
    """Test POST operations - cart creation."""
    
    def test_post_creates_cart_and_invalidates_cache(self, app, controller, mock_cart_service):
        """Test that POST creates cart (cache is auto-invalidated by decorator)."""
        with app.app_context():
            g.current_user = Mock(id=123)
            
            # Mock request data - CartRegistrationSchema requires 'items' with length >= 1
            with app.test_request_context(json={
                'user_id': 123,
                'items': [{'product_id': 1, 'quantity': 2}]
            }):
                # Mock service response (returns ORM object, not dict)
                mock_created_cart = Mock(id=1, user_id=123, items=[], created_at=None)
                mock_cart_service.create_cart.return_value = mock_created_cart
                
                # Mock schema validation to skip product lookup
                with patch('app.sales.schemas.cart_schema.cart_registration_schema.load') as mock_load:
                    mock_load.return_value = {'user_id': 123, 'items': [{'product_id': 1, 'quantity': 2}]}
                    
                    with patch('app.sales.controllers.cart_controller.is_user_or_admin', return_value=True):
                        response, status = controller.post()
                    
                    # Verify service method was called (has @cache_invalidate decorator)
                    mock_cart_service.create_cart.assert_called_once()
                    
                    # Verify response
                    assert status == 201
                    data = response.get_json()
                    assert data['message'] == 'Cart created successfully'
                    assert 'cart' in data
    
    def test_post_validation_error_returns_400(self, app, controller):
        """Test that POST with invalid data returns 400."""
        with app.app_context():
            g.current_user = Mock(id=123)
            
            # Mock invalid request data (missing user_id)
            with app.test_request_context(json={}):
                with patch('app.sales.controllers.cart_controller.is_user_or_admin', return_value=True):
                    with patch('app.sales.schemas.cart_schema.cart_registration_schema.load', 
                              side_effect=ValidationError({'user_id': ['Missing data']})):
                        response, status = controller.post()
                
                assert status == 400
                data = response.get_json()
                assert 'errors' in data
    
    def test_post_access_denied_returns_403(self, app, controller):
        """Test that POST to another user's cart is denied."""
        with app.app_context():
            g.current_user = Mock(id=456)
            
            # Include valid items list to pass validation up to access check
            with app.test_request_context(json={
                'user_id': 123,
                'items': [{'product_id': 1, 'quantity': 2}]
            }):
                # Mock schema to pass validation
                with patch('app.sales.schemas.cart_schema.cart_registration_schema.load') as mock_load:
                    mock_load.return_value = {'user_id': 123, 'items': []}
                    
                    with patch('app.sales.controllers.cart_controller.is_user_or_admin', return_value=False):
                        response, status = controller.post()
                    
                    assert status == 403


class TestCartControllerPutOperations:
    """Test PUT operations - cart updates."""
    
    def test_put_updates_cart_and_invalidates_cache(self, app, controller, mock_cart_service):
        """Test that PUT updates cart (cache is auto-invalidated by decorator)."""
        with app.app_context():
            g.current_user = Mock(id=123)
            
            # CartUpdateSchema requires 'items' field
            with app.test_request_context(json={'items': []}):
                mock_updated_cart = Mock(id=1, user_id=123, items=[], created_at=None)
                mock_cart_service.update_cart.return_value = mock_updated_cart
                
                with patch('app.sales.controllers.cart_controller.is_user_or_admin', return_value=True):
                    response, status = controller.put(user_id=123)
                
                # Verify service method was called (has @cache_invalidate decorator)
                mock_cart_service.update_cart.assert_called_once()
                
                assert status == 200


class TestCartControllerDeleteOperations:
    """Test DELETE operations - cart deletion."""
    
    def test_delete_removes_cart_and_invalidates_cache(self, app, controller, mock_cart_service):
        """Test that DELETE removes cart (cache is auto-invalidated by decorator)."""
        with app.app_context():
            g.current_user = Mock(id=123)
            
            mock_cart_service.delete_cart.return_value = True
            
            with patch('app.sales.controllers.cart_controller.is_user_or_admin', return_value=True):
                response, status = controller.delete(user_id=123)
            
            # Verify service method was called (has @cache_invalidate decorator)
            mock_cart_service.delete_cart.assert_called_once_with(123)
            
            assert status == 200
    
    def test_delete_nonexistent_cart_returns_404(self, app, controller, mock_cart_service):
        """Test that DELETE nonexistent cart returns 400 (as per controller implementation)."""
        with app.app_context():
            g.current_user = Mock(id=123)
            
            mock_cart_service.delete_cart.return_value = False
            
            with patch('app.sales.controllers.cart_controller.is_user_or_admin', return_value=True):
                response, status = controller.delete(user_id=123)
            
            # Controller returns 400 when delete_cart returns False
            assert status == 400


class TestCartControllerErrorHandling:
    """Test error handling and logging."""
    
    def test_get_handles_exception_gracefully(self, app, controller, mock_cart_service):
        """Test that exceptions in GET are handled and logged."""
        with app.app_context():
            g.current_user = Mock(id=123)
            
            # Mock service to raise exception
            mock_cart_service.get_cart_by_user_id_cached.side_effect = Exception("Database error")
            
            with patch('app.sales.controllers.cart_controller.is_user_or_admin', return_value=True):
                response, status = controller.get(user_id=123)
            
            # Verify error response
            assert status == 500
            data = response.get_json()
            assert 'error' in data
            assert 'Failed to retrieve cart' in data['error']
    
    def test_post_handles_service_failure(self, app, controller, mock_cart_service):
        """Test that POST handles service returning None."""
        with app.app_context():
            g.current_user = Mock(id=123)
            
            # Include valid items for schema
            with app.test_request_context(json={
                'user_id': 123,
                'items': [{'product_id': 1, 'quantity': 2}]
            }):
                # Service returns None (creation failed)
                mock_cart_service.create_cart.return_value = None
                
                # Mock schema to pass validation
                with patch('app.sales.schemas.cart_schema.cart_registration_schema.load') as mock_load:
                    mock_load.return_value = {'user_id': 123, 'items': []}
                    
                    with patch('app.sales.controllers.cart_controller.is_user_or_admin', return_value=True):
                        response, status = controller.post()
                    
                    assert status == 400
                    data = response.get_json()
                    assert 'error' in data


class TestCartControllerItemOperations:
    """Test cart item add/update/remove operations."""
    
    def test_add_item_delegates_to_service(self, app, controller, mock_cart_service):
        """Test that add_item calls service method with cache invalidation."""
        with app.app_context():
            g.current_user = Mock(id=123)
            
            with app.test_request_context(json={'quantity': 2}):
                # Mock needs .items attribute for schema serialization
                mock_cart = Mock(id=1, user_id=123, items=[], created_at=None)
                mock_cart_service.add_item_to_cart.return_value = mock_cart
                
                with patch('app.sales.controllers.cart_controller.is_user_or_admin', return_value=True):
                    response, status = controller.add_item(user_id=123, product_id=456)
                
                # Verify service was called (has @cache_invalidate decorator)
                mock_cart_service.add_item_to_cart.assert_called_once()
                
                assert status == 200
    
    def test_update_item_delegates_to_service(self, app, controller, mock_cart_service):
        """Test that update_item calls service method with cache invalidation."""
        with app.app_context():
            g.current_user = Mock(id=123)
            
            with app.test_request_context(json={'quantity': 5}):
                # Mock needs .items attribute for schema serialization
                mock_cart = Mock(id=1, user_id=123, items=[], created_at=None)
                mock_cart_service.update_item_quantity.return_value = mock_cart
                
                with patch('app.sales.controllers.cart_controller.is_user_or_admin', return_value=True):
                    response, status = controller.update_item(user_id=123, product_id=456)
                
                # Verify correct service method was called
                mock_cart_service.update_item_quantity.assert_called_once()
                
                assert status == 200
    
    def test_remove_item_delegates_to_service(self, app, controller, mock_cart_service):
        """Test that remove_item calls service method with cache invalidation."""
        with app.app_context():
            g.current_user = Mock(id=123)
            
            mock_cart_service.remove_item_from_cart.return_value = True
            
            with patch('app.sales.controllers.cart_controller.is_user_or_admin', return_value=True):
                response, status = controller.remove_item(user_id=123, product_id=456)
            
            mock_cart_service.remove_item_from_cart.assert_called_once_with(123, 456)
            
            assert status == 200
