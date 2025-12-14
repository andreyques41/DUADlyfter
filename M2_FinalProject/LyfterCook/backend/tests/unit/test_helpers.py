"""
Test Utilities and Helper Functions
Common utilities for testing.
"""

import json
from typing import Dict, Any, Optional


def assert_success_response(response, expected_status=200):
    """
    Assert that response is successful with expected status code.
    """
    assert response.status_code == expected_status, \
        f"Expected {expected_status}, got {response.status_code}: {response.get_json()}"
    
    data = response.get_json()
    assert data is not None, "Response data is None"
    assert 'data' in data or 'message' in data, "Response missing 'data' or 'message'"
    
    return data


def assert_error_response(response, expected_status=400):
    """
    Assert that response is an error with expected status code.
    """
    assert response.status_code == expected_status, \
        f"Expected {expected_status}, got {response.status_code}"
    
    data = response.get_json()
    assert data is not None, "Response data is None"
    assert 'error' in data or 'message' in data, "Error response missing 'error' or 'message'"
    
    return data


def assert_validation_error(response):
    """
    Assert that response is a validation error (400).
    """
    return assert_error_response(response, 400)


def assert_unauthorized_error(response):
    """
    Assert that response is unauthorized (401).
    """
    return assert_error_response(response, 401)


def assert_forbidden_error(response):
    """
    Assert that response is forbidden (403).
    """
    return assert_error_response(response, 403)


def assert_not_found_error(response):
    """
    Assert that response is not found (404).
    """
    return assert_error_response(response, 404)


def make_request(client, method: str, url: str, 
                 headers: Optional[Dict] = None, 
                 json_data: Optional[Dict] = None,
                 query_params: Optional[Dict] = None):
    """
    Make HTTP request with proper formatting.
    """
    if query_params:
        query_string = '&'.join([f"{k}={v}" for k, v in query_params.items()])
        url = f"{url}?{query_string}"
    
    method_func = getattr(client, method.lower())
    
    kwargs = {}
    if headers:
        kwargs['headers'] = headers
    if json_data:
        kwargs['json'] = json_data
    
    return method_func(url, **kwargs)


def create_test_user(db_session, email: str, password: str, role: str = 'chef'):
    """
    Create a test user in the database.
    """
    from app.auth.models import User
    import bcrypt
    from datetime import datetime
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = User(
        email=email,
        password=hashed_password.decode('utf-8'),
        role=role,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def create_test_chef(db_session, user_id: int, name: str = 'Test Chef'):
    """
    Create a test chef profile.
    """
    from app.chefs.models import Chef
    from datetime import datetime
    
    chef = Chef(
        user_id=user_id,
        name=name,
        phone='+1-555-0100',
        location='Test City',
        specialty='Test Specialty',
        bio='Test bio',
        is_active=True,
        created_at=datetime.utcnow()
    )
    db_session.add(chef)
    db_session.commit()
    db_session.refresh(chef)
    return chef


def create_test_client(db_session, chef_id: int, name: str = 'Test Client'):
    """
    Create a test client profile.
    """
    from app.clients.models import Client
    from datetime import datetime
    
    client = Client(
        chef_id=chef_id,
        name=name,
        email='testclient@example.com',
        phone='+1-555-0200',
        company='Test Company',
        notes='Test client',
        created_at=datetime.utcnow()
    )
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)
    return client


def create_test_dish(db_session, chef_id: int, name: str = 'Test Dish'):
    """
    Create a test dish.
    """
    from app.dishes.models import Dish
    from datetime import datetime
    
    dish = Dish(
        chef_id=chef_id,
        name=name,
        description='Test description',
        category='Main Course',
        price=19.99,
        prep_time=30,
        servings=2,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db_session.add(dish)
    db_session.commit()
    db_session.refresh(dish)
    return dish


def create_test_menu(db_session, chef_id: int, name: str = 'Test Menu'):
    """
    Create a test menu.
    """
    from app.menus.models import Menu
    from datetime import datetime
    
    menu = Menu(
        chef_id=chef_id,
        name=name,
        description='Test menu description',
        status='active',
        created_at=datetime.utcnow()
    )
    db_session.add(menu)
    db_session.commit()
    db_session.refresh(menu)
    return menu


class ResponseValidator:
    """
    Helper class for validating API responses.
    """
    
    @staticmethod
    def validate_pagination(data: Dict[str, Any]):
        """
        Validate pagination fields in response.
        Supports both flat and nested pagination structures.
        """
        # Check for nested pagination object
        if 'pagination' in data:
            pagination = data['pagination']
            assert 'total' in pagination, "Missing 'total' in pagination"
            assert 'page' in pagination, "Missing 'page' in pagination"
            assert 'per_page' in pagination, "Missing 'per_page' in pagination"
            assert isinstance(pagination['total'], int), "'total' must be integer"
            assert isinstance(pagination['page'], int), "'page' must be integer"
            assert isinstance(pagination['per_page'], int), "'per_page' must be integer"
        else:
            # Flat structure
            assert 'total' in data, "Missing 'total' in pagination"
            assert 'page' in data, "Missing 'page' in pagination"
            assert 'per_page' in data, "Missing 'per_page' in pagination"
            assert isinstance(data['total'], int), "'total' must be integer"
            assert isinstance(data['page'], int), "'page' must be integer"
            assert isinstance(data['per_page'], int), "'per_page' must be integer"
    
    @staticmethod
    def validate_chef_response(chef: Dict[str, Any]):
        """
        Validate chef object structure.
        """
        required_fields = ['id', 'bio', 'location', 'specialty']
        for field in required_fields:
            assert field in chef, f"Missing '{field}' in chef response"
    
    @staticmethod
    def validate_dish_response(dish: Dict[str, Any]):
        """
        Validate dish object structure.
        """
        required_fields = ['id', 'name', 'description', 'category', 'price', 
                          'prep_time', 'servings', 'is_active']
        for field in required_fields:
            assert field in dish, f"Missing '{field}' in dish response"
    
    @staticmethod
    def validate_menu_response(menu: Dict[str, Any]):
        """
        Validate menu object structure.
        """
        required_fields = ['id', 'name', 'description', 'status']
        for field in required_fields:
            assert field in menu, f"Missing '{field}' in menu response"
    
    @staticmethod
    def validate_quotation_response(quotation: Dict[str, Any]):
        """
        Validate quotation object structure.
        """
        required_fields = ['id', 'chef_id', 'quotation_number', 'status', 'created_at']
        for field in required_fields:
            assert field in quotation, f"Missing '{field}' in quotation response"
