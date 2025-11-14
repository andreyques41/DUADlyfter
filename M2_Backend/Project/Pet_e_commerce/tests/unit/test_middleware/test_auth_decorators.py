"""
Unit tests for authentication decorators (app.core.middleware.auth_decorators).

Tests @token_required_with_repo and @admin_required_with_repo decorators.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, g
from app.core.middleware.auth_decorators import token_required_with_repo, admin_required_with_repo


class TestTokenRequiredDecorator:
    """Test @token_required_with_repo decorator."""
    
    def setup_method(self):
        """Setup test Flask app and context."""
        self.app = Flask(__name__)
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def teardown_method(self):
        """Cleanup Flask context."""
        self.app_context.pop()
    
    @patch('app.core.middleware.auth_decorators.request')
    def test_missing_authorization_header(self, mock_request):
        """Should return 401 when Authorization header is missing."""
        # Arrange
        mock_request.headers = {}
        
        @token_required_with_repo
        def protected_route():
            return "Success"
        
        # Act
        response, status_code = protected_route()
        
        # Assert
        assert status_code == 401
        data = response.get_json()
        assert "Authorization header missing" in data['error']
    
    @patch('app.core.middleware.auth_decorators.request')
    def test_invalid_authorization_header_format(self, mock_request):
        """Should return 401 for invalid header format."""
        # Arrange
        mock_request.headers = {'Authorization': 'InvalidFormat'}
        
        @token_required_with_repo
        def protected_route():
            return "Success"
        
        # Act
        response, status_code = protected_route()
        
        # Assert
        assert status_code == 401
        data = response.get_json()
        assert "Invalid token format" in data['error']
    
    @patch('app.core.middleware.auth_decorators.verify_jwt_token')
    @patch('app.core.middleware.auth_decorators.request')
    def test_invalid_token(self, mock_request, mock_verify):
        """Should return 401 when token verification fails."""
        # Arrange
        mock_request.headers = {'Authorization': 'Bearer invalid_token'}
        mock_verify.return_value = None  # Token verification failed
        
        @token_required_with_repo
        def protected_route():
            return "Success"
        
        # Act
        response, status_code = protected_route()
        
        # Assert
        assert status_code == 401
        data = response.get_json()
        assert "Invalid or expired token" in data['error']
        mock_verify.assert_called_once_with('invalid_token')
    
    @patch('app.core.middleware.auth_decorators.get_user_by_id')
    @patch('app.core.middleware.auth_decorators.verify_jwt_token')
    @patch('app.core.middleware.auth_decorators.request')
    def test_user_not_found_after_token_decode(self, mock_request, mock_verify, mock_get_user):
        """Should return 401 when user not found in database."""
        # Arrange
        mock_request.headers = {'Authorization': 'Bearer valid_token'}
        mock_verify.return_value = {'user_id': 999}
        mock_get_user.return_value = None  # User not found
        
        @token_required_with_repo
        def protected_route():
            return "Success"
        
        # Act
        response, status_code = protected_route()
        
        # Assert
        assert status_code == 401
        data = response.get_json()
        assert "User not found" in data['error']
        mock_get_user.assert_called_once_with(999)
    
    @patch('app.core.middleware.auth_decorators.get_user_by_id')
    @patch('app.core.middleware.auth_decorators.verify_jwt_token')
    @patch('app.core.middleware.auth_decorators.request')
    def test_successful_authentication(self, mock_request, mock_verify, mock_get_user):
        """Should set g.current_user and call wrapped function."""
        # Arrange
        mock_request.headers = {'Authorization': 'Bearer valid_token'}
        mock_verify.return_value = {'user_id': 1, 'username': 'testuser'}
        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = 'testuser'
        mock_user.user_roles = []  # Empty roles to avoid iteration error
        mock_get_user.return_value = mock_user
        
        @token_required_with_repo
        def protected_route():
            return {"user": g.current_user.username}
        
        # Act
        result = protected_route()
        
        # Assert
        assert result == {"user": "testuser"}
        assert g.current_user == mock_user
    
    @patch('app.core.middleware.auth_decorators.get_user_by_id')
    @patch('app.core.middleware.auth_decorators.verify_jwt_token')
    @patch('app.core.middleware.auth_decorators.request')
    def test_decorator_preserves_function_metadata(self, mock_request, mock_verify, mock_get_user):
        """Should preserve wrapped function metadata."""
        # Arrange
        mock_request.headers = {'Authorization': 'Bearer valid_token'}
        mock_verify.return_value = {'user_id': 1}
        mock_get_user.return_value = Mock()
        
        @token_required_with_repo
        def my_protected_route():
            """Protected route docstring."""
            return "Success"
        
        # Assert
        assert my_protected_route.__name__ == 'my_protected_route'
        assert 'Protected route docstring' in my_protected_route.__doc__


class TestAdminRequiredDecorator:
    """Test @admin_required_with_repo decorator."""
    
    def setup_method(self):
        """Setup test Flask app and context."""
        self.app = Flask(__name__)
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def teardown_method(self):
        """Cleanup Flask context."""
        self.app_context.pop()
    
    @patch('app.core.middleware.auth_decorators.request')
    def test_admin_missing_authorization_header(self, mock_request):
        """Should return 401 when Authorization header is missing."""
        # Arrange
        mock_request.headers = {}
        
        @admin_required_with_repo
        def admin_route():
            return "Success"
        
        # Act
        response, status_code = admin_route()
        
        # Assert
        assert status_code == 401
        data = response.get_json()
        assert "Authorization header missing" in data['error']
    
    @patch('app.core.middleware.auth_decorators.user_has_role')
    @patch('app.core.middleware.auth_decorators.get_user_by_id')
    @patch('app.core.middleware.auth_decorators.verify_jwt_token')
    @patch('app.core.middleware.auth_decorators.request')
    def test_admin_user_not_authorized(self, mock_request, mock_verify, mock_get_user, mock_has_role):
        """Should return 403 when user is not admin."""
        # Arrange
        mock_request.headers = {'Authorization': 'Bearer valid_token'}
        mock_verify.return_value = {'user_id': 1}
        mock_user = Mock()
        mock_user.id = 1
        mock_user.user_roles = []  # Empty roles
        mock_get_user.return_value = mock_user
        mock_has_role.return_value = False  # Not admin
        
        @admin_required_with_repo
        def admin_route():
            return "Success"
        
        # Act
        response, status_code = admin_route()
        
        # Assert
        assert status_code == 403
        data = response.get_json()
        assert "Access forbidden" in data['error'] or "Admin" in data['error']
        mock_has_role.assert_called_once_with(mock_user, 'admin')
    
    @patch('app.core.middleware.auth_decorators.user_has_role')
    @patch('app.core.middleware.auth_decorators.get_user_by_id')
    @patch('app.core.middleware.auth_decorators.verify_jwt_token')
    @patch('app.core.middleware.auth_decorators.request')
    def test_admin_successful_authentication(self, mock_request, mock_verify, mock_get_user, mock_has_role):
        """Should allow access when user is admin."""
        # Arrange
        mock_request.headers = {'Authorization': 'Bearer valid_token'}
        mock_verify.return_value = {'user_id': 1}
        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = 'admin'
        mock_user.user_roles = []  # Empty roles
        mock_get_user.return_value = mock_user
        mock_has_role.return_value = True  # Is admin
        
        @admin_required_with_repo
        def admin_route():
            return {"admin": g.current_user.username}
        
        # Act
        result = admin_route()
        
        # Assert
        assert result == {"admin": "admin"}
        assert g.current_user == mock_user
    
    @patch('app.core.middleware.auth_decorators.verify_jwt_token')
    @patch('app.core.middleware.auth_decorators.request')
    def test_admin_invalid_token(self, mock_request, mock_verify):
        """Should return 401 for invalid token."""
        # Arrange
        mock_request.headers = {'Authorization': 'Bearer invalid_token'}
        mock_verify.return_value = None
        
        @admin_required_with_repo
        def admin_route():
            return "Success"
        
        # Act
        response, status_code = admin_route()
        
        # Assert
        assert status_code == 401
        data = response.get_json()
        assert "Invalid or expired token" in data['error']


class TestDecoratorIntegration:
    """Test decorator edge cases and integration scenarios."""
    
    def setup_method(self):
        """Setup test Flask app."""
        self.app = Flask(__name__)
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def teardown_method(self):
        """Cleanup Flask context."""
        self.app_context.pop()
    
    @patch('app.core.middleware.auth_decorators.get_user_by_id')
    @patch('app.core.middleware.auth_decorators.verify_jwt_token')
    @patch('app.core.middleware.auth_decorators.request')
    def test_token_extraction_with_bearer_prefix(self, mock_request, mock_verify, mock_get_user):
        """Should correctly extract token from 'Bearer <token>' format."""
        # Arrange
        token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test'
        mock_request.headers = {'Authorization': f'Bearer {token}'}
        mock_verify.return_value = {'user_id': 1}
        mock_get_user.return_value = Mock()
        
        @token_required_with_repo
        def protected_route():
            return "Success"
        
        # Act
        protected_route()
        
        # Assert
        mock_verify.assert_called_once_with(token)
    
    @patch('app.core.middleware.auth_decorators.request')
    def test_authorization_header_with_extra_spaces(self, mock_request):
        """Should handle malformed Authorization header gracefully."""
        # Arrange
        mock_request.headers = {'Authorization': 'Bearer  '}
        
        @token_required_with_repo
        def protected_route():
            return "Success"
        
        # Act
        response = protected_route()
        
        # Assert
        assert response[1] == 401
