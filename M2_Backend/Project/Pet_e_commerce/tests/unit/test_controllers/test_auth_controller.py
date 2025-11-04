"""
Unit Tests for AuthController

Tests HTTP request processing for authentication operations.

Coverage:
- Initialization
- Login with JWT generation
- Registration
- Input validation
- Error handling
"""
import pytest
from unittest.mock import Mock, patch
from flask import Flask
from marshmallow import ValidationError


@pytest.fixture
def test_app():
    """Create a simple Flask app for controller testing (renamed to avoid conflicts)."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def mock_auth_service():
    mock = Mock()
    mock.get_user_by_username = Mock(return_value=None)
    mock.register_user = Mock(return_value=None)
    return mock


@pytest.fixture
def controller(mock_auth_service):
    from app.auth.controllers.auth_controller import AuthController
    controller = AuthController()
    controller.auth_service = mock_auth_service
    return controller


class TestAuthControllerInit:
    def test_initializes_with_service(self):
        from app.auth.controllers.auth_controller import AuthController
        controller = AuthController()
        assert controller.auth_service is not None
        assert controller.logger is not None


class TestAuthControllerLogin:
    """Test login operations with JWT generation."""
    
    def test_login_successful_returns_token(self, app, controller, mock_auth_service):
        """Test successful login returns JWT token."""
        with app.app_context():
            mock_user = Mock(id=123, username='testuser', password_hash='hashed')
            mock_auth_service.get_user_by_username.return_value = mock_user
            
            with app.test_request_context(json={'username': 'testuser', 'password': 'password123'}):
                with patch('app.auth.controllers.auth_controller.verify_password', return_value=True):
                    with patch('app.auth.controllers.auth_controller.generate_jwt_token', return_value='token_123'):
                        response, status = controller.login()
                
                assert status == 200
                data = response.get_json()
                assert data['message'] == 'Login successful'
                assert data['token'] == 'token_123'
                assert data['token_type'] == 'Bearer'
                assert 'user' in data
    
    def test_login_invalid_username_returns_401(self, app, controller, mock_auth_service):
        """Test login with invalid username returns 401."""
        with app.app_context():
            mock_auth_service.get_user_by_username.return_value = None
            
            with app.test_request_context(json={'username': 'nonexistent', 'password': 'password'}):
                response, status = controller.login()
                
                assert status == 401
                data = response.get_json()
                assert 'error' in data
                assert 'Invalid credentials' in data['error']
    
    def test_login_invalid_password_returns_401(self, app, controller, mock_auth_service):
        """Test login with invalid password returns 401."""
        with app.app_context():
            mock_user = Mock(id=123, username='testuser', password_hash='hashed')
            mock_auth_service.get_user_by_username.return_value = mock_user
            
            with app.test_request_context(json={'username': 'testuser', 'password': 'wrongpassword'}):
                with patch('app.auth.controllers.auth_controller.verify_password', return_value=False):
                    response, status = controller.login()
                
                assert status == 401
    
    def test_login_validation_error_returns_400(self, app, controller):
        """Test login with invalid data returns 400."""
        with app.app_context():
            with app.test_request_context(json={}):
                with patch('app.auth.schemas.user_login_schema.load', 
                          side_effect=ValidationError({'username': ['Missing data']})):
                    response, status = controller.login()
                
                assert status == 400
                data = response.get_json()
                assert 'errors' in data


class TestAuthControllerRegistration:
    """Test registration operations."""
    
    def test_register_validation_error_returns_400(self, app, controller):
        """Test registration with invalid data returns 400."""
        with app.app_context():
            with app.test_request_context(json={}):
                with patch('app.auth.schemas.user_registration_schema.load',
                          side_effect=ValidationError({'email': ['Invalid email']})):
                    response, status = controller.register()
                
                assert status == 400


class TestAuthControllerErrorHandling:
    """Test error handling."""
    
    def test_login_handles_service_exception(self, app, controller, mock_auth_service):
        """Test login handles service exceptions gracefully."""
        with app.app_context():
            mock_auth_service.get_user_by_username.side_effect = Exception("Database error")
            
            with app.test_request_context(json={'username': 'test', 'password': 'pass'}):
                response, status = controller.login()
                
                assert status == 500
                data = response.get_json()
                assert 'error' in data
