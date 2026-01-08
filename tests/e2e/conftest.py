"""
E2E Test Configuration and Fixtures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides fixtures specific to End-to-End testing:
- Flask test client for HTTP requests
- Authentication tokens (user and admin)
- Authorization headers
- Helper functions for common E2E operations

These tests verify complete request-response cycles through the entire stack.
"""
import pytest
import json


@pytest.fixture
def client(app):
    """
    Flask test client for making HTTP requests.
    
    Scope: function (new client per test for isolation)
    
    Usage:
        response = client.get('/products')
        response = client.post('/auth/login', json={...})
    """
    return app.test_client()


@pytest.fixture
def user_token(client):
    """
    JWT token for regular user authentication.
    
    Creates a user via API and returns the JWT token.
    
    Scope: function
    
    Returns:
        str: JWT bearer token
    """
    # Register user via API
    user_data = {
        'username': 'e2etestuser',
        'email': 'e2etest@example.com',
        'password': 'password123',
        'first_name': 'E2E',
        'last_name': 'Test'
    }
    
    # Try to register (might already exist from previous test)
    client.post('/auth/register', json=user_data)
    
    # Login to get token
    response = client.post('/auth/login', json={
        'username': 'e2etestuser',
        'password': 'password123'
    })
    
    assert response.status_code == 200, f"Login failed: {response.get_json()}"
    data = response.get_json()
    assert 'token' in data, "No token in login response"
    
    return data['token']


@pytest.fixture
def admin_token(client):
    """
    JWT token for admin user authentication.
    
    Creates an admin user via API and returns the JWT token.
    
    Scope: function
    
    Returns:
        str: JWT bearer token
    """
    # Register admin via API
    admin_data = {
        'username': 'e2eadminuser',
        'email': 'e2eadmin@example.com',
        'password': 'admin123',
        'first_name': 'E2E Admin',
        'last_name': 'Test',
        'role': 'admin'  # Request admin role
    }
    
    # Try to register (might already exist)
    client.post('/auth/register', json=admin_data)
    
    # Login to get token
    response = client.post('/auth/login', json={
        'username': 'e2eadminuser',
        'password': 'admin123'
    })
    
    assert response.status_code == 200, f"Admin login failed: {response.get_json()}"
    data = response.get_json()
    assert 'token' in data, "No token in admin login response"
    
    return data['token']


@pytest.fixture
def auth_headers(user_token):
    """
    Authorization headers with user token.
    
    Scope: function
    
    Returns:
        dict: Headers with Bearer token
    
    Usage:
        response = client.get('/auth/users/1', headers=auth_headers)
    """
    return {
        'Authorization': f'Bearer {user_token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def admin_headers(admin_token):
    """
    Authorization headers with admin token.
    
    Scope: function
    
    Returns:
        dict: Headers with Bearer token
    
    Usage:
        response = client.get('/auth/users', headers=admin_headers)
    """
    return {
        'Authorization': f'Bearer {admin_token}',
        'Content-Type': 'application/json'
    }


# ============================================
# HELPER FUNCTIONS (not fixtures)
# ============================================

def get_json_or_fail(response):
    """
    Get JSON from response or fail with descriptive error.
    
    Args:
        response: Flask response object
    
    Returns:
        dict: Parsed JSON data
    
    Raises:
        AssertionError: If response is not valid JSON
    """
    try:
        return response.get_json()
    except Exception as e:
        raise AssertionError(
            f"Failed to parse JSON response. "
            f"Status: {response.status_code}, "
            f"Data: {response.data.decode()}, "
            f"Error: {e}"
        )


def assert_success_response(response, expected_status=200):
    """
    Assert response is successful with expected status.
    
    Args:
        response: Flask response object
        expected_status: Expected HTTP status code
    """
    actual = response.status_code
    if actual != expected_status:
        data = get_json_or_fail(response)
        raise AssertionError(
            f"Expected status {expected_status}, got {actual}. "
            f"Response: {data}"
        )


def assert_error_response(response, expected_status, expected_error_key='error'):
    """
    Assert response is an error with expected status and error message.
    
    Args:
        response: Flask response object
        expected_status: Expected HTTP status code
        expected_error_key: Key in JSON response containing error (default: 'error')
    """
    actual = response.status_code
    if actual != expected_status:
        data = get_json_or_fail(response)
        raise AssertionError(
            f"Expected error status {expected_status}, got {actual}. "
            f"Response: {data}"
        )
    
    data = get_json_or_fail(response)
    assert expected_error_key in data, f"Expected '{expected_error_key}' in error response: {data}"


# =======================
# E2E Helper Fixtures
# =======================

@pytest.fixture
def create_test_products(client, admin_headers):
    """
    Fixture to create test products using the service layer (bypassing API schema bugs).
    
    Returns a function that creates n products and returns the list.
    """
    from app.products.services.product_service import ProductService
    from app.products.schemas.product_schema import ProductResponseSchema
    
    def _create_products(count=1, prefix="TestProduct"):
        """Create count number of test products."""
        products = []
        service = ProductService()
        schema = ProductResponseSchema()
        
        for i in range(count):
            product_data = {
                'description': f'{prefix} {i} for E2E testing',
                'product_category_id': 1,  # food category (from reference data)
                'pet_type_id': 1,  # dog (from reference data)
                'stock_quantity': 100,
                'price': 10.0 + i,
                'is_active': True
            }
            created = service.create_product(**product_data)
            if created:
                products.append(schema.dump(created))
        
        return products
    
    return _create_products


@pytest.fixture
def create_test_order(client):
    """
    Fixture to create test orders using the service layer.
    
    Returns a function that creates an order for a given user with products.
    Handles all the complexity of cart creation and order setup.
    """
    from app.sales.services.order_service import OrderService
    from app.sales.services.cart_service import CartService
    from app.core.reference_data import ReferenceData
    
    def _create_order(user_id, products, shipping_address="123 Test St, Test City, TC 12345"):
        """
        Create an order for a user with given products.
        
        Args:
            user_id: User ID to create order for
            products: List of product dicts/objects with 'id' and optionally 'quantity'
            shipping_address: Shipping address string
            
        Returns:
            Created Order object or None
        """
        cart_service = CartService()
        order_service = OrderService()
        
        # Get existing cart or create new one
        cart = cart_service.get_cart_by_user_id(user_id=user_id)
        
        if not cart:
            # Create new cart
            cart = cart_service.create_cart(user_id=user_id)
        
        if not cart:
            print(f"Failed to create cart for user {user_id}")
            return None
        
        # Calculate total amount
        total_amount = 0.0
        order_items = []
        
        for product in products:
            # Handle tuple format: (product_id, quantity, price)
            if isinstance(product, tuple):
                product_id, quantity, price = product
            # Handle dict format
            elif isinstance(product, dict):
                product_id = product['id']
                price = product.get('price', 10.0)
                quantity = product.get('quantity', 1)
            # Handle object format
            else:
                product_id = product.id
                price = getattr(product, 'price', 10.0)
                quantity = getattr(product, 'quantity', 1)
            
            item_total = price * quantity
            total_amount += item_total
            
            order_items.append({
                'product_id': product_id,
                'quantity': quantity,
                'amount': item_total
            })
        
        # Get pending status ID
        pending_status_id = ReferenceData.get_order_status_id('pending')
        
        # Create order
        order = order_service.create_order(
            user_id=user_id,
            cart_id=cart.id,
            items=order_items,
            total_amount=total_amount,
            shipping_address=shipping_address,
            order_status_id=pending_status_id
        )
        
        return order
    
    return _create_order
