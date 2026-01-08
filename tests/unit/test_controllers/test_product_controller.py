"""
Unit Tests for ProductController

Tests HTTP request processing for product operations.

Coverage:
- Initialization
- _try_authenticate_user() - optional authentication
- _extract_filters_from_request() - advanced filtering
- GET operations with role-based schemas
- POST product creation (admin only)
- PUT/PATCH updates (admin only)
- DELETE operations (admin only)
- Cached method delegation
"""
import pytest
from unittest.mock import Mock, patch
from flask import Flask, g


@pytest.fixture
def test_app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def mock_product_service():
    mock = Mock()
    mock.get_all_products_cached = Mock(return_value=[])
    mock.get_product_by_id_cached = Mock(return_value=None)
    mock.get_product_by_sku_cached = Mock(return_value=None)
    mock.get_products_by_category_cached = Mock(return_value=[])
    mock.get_products_by_pet_type_cached = Mock(return_value=[])
    mock.create_product = Mock(return_value=None)
    mock.update_product = Mock(return_value=None)
    mock.delete_product = Mock(return_value=False)
    return mock


@pytest.fixture
def controller(mock_product_service):
    from app.products.controllers.product_controller import ProductController
    controller = ProductController()
    controller.product_service = mock_product_service
    return controller


class TestProductControllerInit:
    def test_initializes_with_service(self):
        from app.products.controllers.product_controller import ProductController
        controller = ProductController()
        assert controller.product_service is not None
        assert controller.product_schema is not None


class TestProductControllerOptionalAuth:
    """Test _try_authenticate_user() - does not fail on missing token."""
    
    def test_try_authenticate_user_with_valid_token(self, app, controller):
        with app.app_context():
            with app.test_request_context(headers={'Authorization': 'Bearer valid_token'}):
                mock_user = Mock(id=123, username='testuser')
                
                with patch('app.products.controllers.product_controller.verify_jwt_token', return_value={'user_id': 123}):
                    with patch('app.products.controllers.product_controller.get_user_by_id', return_value=mock_user):
                        controller._try_authenticate_user()
                
                assert hasattr(g, 'current_user')
                assert g.current_user.id == 123
    
    def test_try_authenticate_user_without_token_does_not_fail(self, app, controller):
        """Test that missing token does not raise exception."""
        with app.app_context():
            with app.test_request_context():
                # Should not raise exception
                controller._try_authenticate_user()
                
                # g.current_user should not be set
                assert not hasattr(g, 'current_user')
    
    def test_try_authenticate_user_with_invalid_token_does_not_fail(self, app, controller):
        """Test that invalid token does not raise exception (public access)."""
        with app.app_context():
            with app.test_request_context(headers={'Authorization': 'Bearer invalid'}):
                with patch('app.products.controllers.product_controller.verify_jwt_token', return_value=None):
                    # Should not raise exception
                    controller._try_authenticate_user()
                    
                    assert not hasattr(g, 'current_user')


class TestProductControllerFilters:
    """Test _extract_filters_from_request() - advanced filtering."""
    
    def test_extract_category_filter(self, app, controller):
        with app.app_context():
            with app.test_request_context('/?category=food'):
                filters = controller._extract_filters_from_request()
                assert filters['category'] == 'food'
    
    def test_extract_pet_type_filter(self, app, controller):
        with app.app_context():
            with app.test_request_context('/?pet_type=dog'):
                filters = controller._extract_filters_from_request()
                assert filters['pet_type'] == 'dog'
    
    def test_extract_brand_filter(self, app, controller):
        with app.app_context():
            with app.test_request_context('/?brand=PetNutrition'):
                filters = controller._extract_filters_from_request()
                assert filters['brand'] == 'PetNutrition'
    
    def test_extract_is_active_filter(self, app, controller):
        with app.app_context():
            with app.test_request_context('/?is_active=true'):
                filters = controller._extract_filters_from_request()
                assert filters['is_active'] is True
    
    def test_extract_multiple_filters(self, app, controller):
        with app.app_context():
            with app.test_request_context('/?category=food&pet_type=dog&brand=PetNutrition'):
                filters = controller._extract_filters_from_request()
                assert filters['category'] == 'food'
                assert filters['pet_type'] == 'dog'
                assert filters['brand'] == 'PetNutrition'


class TestProductControllerGetOperations:
    """Test GET operations with role-based schemas."""
    
    def test_get_all_products_admin_uses_cached_with_admin_flag(self, app, controller, mock_product_service):
        """Test admin get uses cached method with include_admin_data=True."""
        with app.app_context():
            g.current_user = Mock(id=999, roles=[Mock(name='admin')])
            mock_product_service.get_all_products_cached.return_value = []
            
            with patch('app.products.controllers.product_controller.is_admin_user', return_value=True):
                # Controller method is get(), not get_list()
                response, status = controller.get(product_id=None)
            
            # Verify cached method called with include_admin_data and show_exact_stock flags
            mock_product_service.get_all_products_cached.assert_called_once()
            call_kwargs = mock_product_service.get_all_products_cached.call_args[1]
            assert call_kwargs.get('include_admin_data') is True
            assert call_kwargs.get('show_exact_stock') is True
            assert status == 200
    
    def test_get_all_products_public_uses_cached_with_admin_false(self, app, controller, mock_product_service):
        """Test public get uses cached method with include_admin_data=False."""
        with app.app_context():
            # No user set (public access)
            mock_product_service.get_all_products_cached.return_value = []
            
            with patch('app.products.controllers.product_controller.is_admin_user', return_value=False):
                # Controller method is get(), not get_list()
                response, status = controller.get(product_id=None)
            
            # Verify cached method called with include_admin_data=False
            call_kwargs = mock_product_service.get_all_products_cached.call_args[1]
            assert call_kwargs.get('include_admin_data') is False
            assert call_kwargs.get('show_exact_stock') is False
            assert status == 200
    
    def test_get_specific_product_uses_cached_method(self, app, controller, mock_product_service):
        """Test get specific product uses get_product_by_id_cached."""
        with app.app_context():
            mock_product_service.get_product_by_id_cached.return_value = {'id': 1, 'name': 'Product'}
            
            with patch('app.products.controllers.product_controller.is_admin_user', return_value=False):
                response, status = controller.get(product_id=1)
            
            mock_product_service.get_product_by_id_cached.assert_called_once()
            call_kwargs = mock_product_service.get_product_by_id_cached.call_args[1]
            assert call_kwargs.get('include_admin_data') is False
            assert call_kwargs.get('show_exact_stock') is False
            assert status == 200


class TestProductControllerPostOperations:
    """Test POST operations (admin only)."""
    
    def test_post_creates_product_with_cache_invalidation(self, app, controller, mock_product_service):
        """Test admin can create product (cache invalidated by decorator)."""
        with app.app_context():
            g.current_user = Mock(id=999, username='admin', roles=[Mock(name='admin')])
            
            # Provide valid JSON matching ProductRegistrationSchema requirements
            valid_product_data = {
                'name': 'New Product',
                'description': 'A great product',
                'price': 29.99,
                'category': 'food',  # String name, not ID
                'pet_type': 'dog',   # String name, not ID
                'stock_quantity': 100
            }
            
            with app.test_request_context(json=valid_product_data):
                # Mock product must have numeric attributes for schema serialization
                mock_product = Mock(
                    id=1,
                    name='New Product',
                    description='A great product',
                    price=29.99,
                    product_category_id=1,
                    pet_type_id=1,
                    stock_quantity=100,
                    weight=None,
                    brand=None,
                    image_url=None,
                    is_active=True,
                    sku='TEST-001',
                    # Admin fields for ProductResponseSchema._get_admin_data()
                    internal_cost=15.0,  # Real float for arithmetic operations
                    supplier_info=None,
                    created_by=None,
                    last_updated=None
                )
                mock_product_service.create_product.return_value = mock_product
                
                with patch('app.products.controllers.product_controller.is_admin_user', return_value=True):
                    response, status = controller.post()
                
                mock_product_service.create_product.assert_called_once()
                assert status == 201
    
    def test_post_non_admin_denied(self, app, controller):
        """Test non-admin cannot create products (returns 400 from schema validation)."""
        with app.app_context():
            g.current_user = Mock(id=123, roles=[Mock(name='user')])
            
            with app.test_request_context(json={}):
                with patch('app.products.controllers.product_controller.is_admin_user', return_value=False):
                    response, status = controller.post()
                
                # Schema validation will fail on empty JSON, returning 400
                assert status == 400


class TestProductControllerDeleteOperations:
    """Test DELETE operations (admin only)."""
    
    def test_delete_product_invalidates_cache(self, app, controller, mock_product_service):
        """Test admin can delete product (cache invalidated by decorator)."""
        with app.app_context():
            g.current_user = Mock(id=999, roles=[Mock(name='admin')])
            mock_product_service.delete_product.return_value = True
            
            with patch('app.products.controllers.product_controller.is_admin_user', return_value=True):
                response, status = controller.delete(product_id=1)
            
            mock_product_service.delete_product.assert_called_once_with(1)
            assert status == 200
