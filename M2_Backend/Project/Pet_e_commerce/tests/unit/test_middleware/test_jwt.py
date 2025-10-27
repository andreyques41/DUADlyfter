"""
Unit tests for JWT utilities (app.core.lib.jwt).

Tests JWT token generation, verification, expiration, and error handling.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import jwt as pyjwt
from app.core.lib.jwt import generate_jwt_token, verify_jwt_token


class TestGenerateJWTToken:
    """Test JWT token generation."""
    
    @patch('app.core.lib.jwt.get_jwt_secret')
    @patch('app.core.lib.jwt.get_jwt_algorithm')
    @patch('app.core.lib.jwt.get_jwt_expiration_hours')
    def test_generate_token_with_single_role(self, mock_exp, mock_algo, mock_secret):
        """Should generate token with user role."""
        # Arrange
        mock_secret.return_value = 'test_secret'
        mock_algo.return_value = 'HS256'
        mock_exp.return_value = 24
        
        mock_role = Mock()
        mock_role.name = 'user'
        mock_user_role = Mock()
        mock_user_role.role = mock_role
        
        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = 'testuser'
        mock_user.user_roles = [mock_user_role]
        
        # Act
        token = generate_jwt_token(mock_user)
        
        # Assert
        assert token is not None
        payload = pyjwt.decode(token, 'test_secret', algorithms=['HS256'])
        assert payload['user_id'] == 1
        assert payload['username'] == 'testuser'
        assert payload['role'] == 'user'
        assert 'user' in payload['roles']
    
    @patch('app.core.lib.jwt.get_jwt_secret')
    @patch('app.core.lib.jwt.get_jwt_algorithm')
    @patch('app.core.lib.jwt.get_jwt_expiration_hours')
    def test_generate_token_with_admin_role(self, mock_exp, mock_algo, mock_secret):
        """Should generate token with admin as primary role."""
        # Arrange
        mock_secret.return_value = 'test_secret'
        mock_algo.return_value = 'HS256'
        mock_exp.return_value = 24
        
        mock_admin_role = Mock()
        mock_admin_role.name = 'admin'
        mock_user_role = Mock()
        mock_user_role.role = mock_admin_role
        
        mock_user = Mock()
        mock_user.id = 2
        mock_user.username = 'admin'
        mock_user.user_roles = [mock_user_role]
        
        # Act
        token = generate_jwt_token(mock_user)
        
        # Assert
        payload = pyjwt.decode(token, 'test_secret', algorithms=['HS256'])
        assert payload['role'] == 'admin'
        assert 'admin' in payload['roles']
    
    @patch('app.core.lib.jwt.get_jwt_secret')
    @patch('app.core.lib.jwt.get_jwt_algorithm')
    @patch('app.core.lib.jwt.get_jwt_expiration_hours')
    def test_generate_token_with_multiple_roles(self, mock_exp, mock_algo, mock_secret):
        """Should handle multiple roles, prioritizing admin."""
        # Arrange
        mock_secret.return_value = 'test_secret'
        mock_algo.return_value = 'HS256'
        mock_exp.return_value = 24
        
        mock_admin_role = Mock()
        mock_admin_role.name = 'admin'
        mock_user_role = Mock()
        mock_user_role.name = 'user'
        
        mock_ur1 = Mock()
        mock_ur1.role = mock_user_role
        mock_ur2 = Mock()
        mock_ur2.role = mock_admin_role
        
        mock_user = Mock()
        mock_user.id = 3
        mock_user.username = 'multiuser'
        mock_user.user_roles = [mock_ur1, mock_ur2]
        
        # Act
        token = generate_jwt_token(mock_user)
        
        # Assert
        payload = pyjwt.decode(token, 'test_secret', algorithms=['HS256'])
        assert payload['role'] == 'admin'  # Admin prioritized
    
    @patch('app.core.lib.jwt.get_jwt_secret')
    @patch('app.core.lib.jwt.get_jwt_algorithm')
    @patch('app.core.lib.jwt.get_jwt_expiration_hours')
    def test_generate_token_without_roles(self, mock_exp, mock_algo, mock_secret):
        """Should default to 'user' role when no roles assigned."""
        # Arrange
        mock_secret.return_value = 'test_secret'
        mock_algo.return_value = 'HS256'
        mock_exp.return_value = 24
        
        mock_user = Mock()
        mock_user.id = 4
        mock_user.username = 'noroles'
        mock_user.user_roles = []
        
        # Act
        token = generate_jwt_token(mock_user)
        
        # Assert
        payload = pyjwt.decode(token, 'test_secret', algorithms=['HS256'])
        assert payload['role'] == 'user'
        assert payload['roles'] == ['user']
    
    @patch('app.core.lib.jwt.get_jwt_secret')
    @patch('app.core.lib.jwt.get_jwt_algorithm')
    @patch('app.core.lib.jwt.get_jwt_expiration_hours')
    def test_generate_token_includes_expiration(self, mock_exp, mock_algo, mock_secret):
        """Should include expiration timestamp."""
        # Arrange
        mock_secret.return_value = 'test_secret'
        mock_algo.return_value = 'HS256'
        mock_exp.return_value = 24
        
        mock_user = Mock()
        mock_user.id = 5
        mock_user.username = 'exptest'
        mock_user.user_roles = []
        
        # Act
        token = generate_jwt_token(mock_user)
        
        # Assert
        payload = pyjwt.decode(token, 'test_secret', algorithms=['HS256'])
        assert 'exp' in payload
        assert 'iat' in payload
    
    @patch('app.core.lib.jwt.get_jwt_secret')
    @patch('app.core.lib.jwt.get_jwt_algorithm')
    @patch('app.core.lib.jwt.get_jwt_expiration_hours')
    @patch('app.core.lib.jwt.logger')
    def test_generate_token_handles_exceptions(self, mock_logger, mock_exp, mock_algo, mock_secret):
        """Should return None on errors."""
        # Arrange
        mock_secret.side_effect = Exception("Config error")
        
        mock_user = Mock()
        mock_user.id = 6
        mock_user.username = 'erroruser'
        
        # Act
        token = generate_jwt_token(mock_user)
        
        # Assert
        assert token is None
        mock_logger.error.assert_called_once()


class TestVerifyJWTToken:
    """Test JWT token verification."""
    
    @patch('app.core.lib.jwt.get_jwt_secret')
    @patch('app.core.lib.jwt.get_jwt_algorithm')
    def test_verify_valid_token(self, mock_algo, mock_secret):
        """Should decode valid token successfully."""
        # Arrange
        secret = 'test_secret'
        algorithm = 'HS256'
        mock_secret.return_value = secret
        mock_algo.return_value = algorithm
        
        payload = {
            'user_id': 1,
            'username': 'test',
            'role': 'user',
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        token = pyjwt.encode(payload, secret, algorithm=algorithm)
        
        # Act
        result = verify_jwt_token(token)
        
        # Assert
        assert result is not None
        assert result['user_id'] == 1
        assert result['username'] == 'test'
    
    @patch('app.core.lib.jwt.get_jwt_secret')
    @patch('app.core.lib.jwt.get_jwt_algorithm')
    @patch('app.core.lib.jwt.logger')
    def test_verify_expired_token(self, mock_logger, mock_algo, mock_secret):
        """Should return None for expired token."""
        # Arrange
        secret = 'test_secret'
        algorithm = 'HS256'
        mock_secret.return_value = secret
        mock_algo.return_value = algorithm
        
        payload = {
            'user_id': 1,
            'username': 'test',
            'exp': datetime.utcnow() - timedelta(hours=1)  # Expired
        }
        token = pyjwt.encode(payload, secret, algorithm=algorithm)
        
        # Act
        result = verify_jwt_token(token)
        
        # Assert
        assert result is None
        mock_logger.warning.assert_called_once_with("JWT token has expired")
    
    @patch('app.core.lib.jwt.get_jwt_secret')
    @patch('app.core.lib.jwt.get_jwt_algorithm')
    @patch('app.core.lib.jwt.logger')
    def test_verify_invalid_token(self, mock_logger, mock_algo, mock_secret):
        """Should return None for invalid token."""
        # Arrange
        mock_secret.return_value = 'test_secret'
        mock_algo.return_value = 'HS256'
        
        invalid_token = 'invalid.token.here'
        
        # Act
        result = verify_jwt_token(invalid_token)
        
        # Assert
        assert result is None
        mock_logger.warning.assert_called_once_with("Invalid JWT token")
    
    @patch('app.core.lib.jwt.get_jwt_secret')
    @patch('app.core.lib.jwt.get_jwt_algorithm')
    @patch('app.core.lib.jwt.logger')
    def test_verify_token_wrong_secret(self, mock_logger, mock_algo, mock_secret):
        """Should return None when token signed with different secret."""
        # Arrange
        mock_algo.return_value = 'HS256'
        
        # Token created with one secret
        payload = {'user_id': 1, 'exp': datetime.utcnow() + timedelta(hours=1)}
        token = pyjwt.encode(payload, 'secret1', algorithm='HS256')
        
        # Try to verify with different secret
        mock_secret.return_value = 'secret2'
        
        # Act
        result = verify_jwt_token(token)
        
        # Assert
        assert result is None
    
    @patch('app.core.lib.jwt.get_jwt_secret')
    @patch('app.core.lib.jwt.get_jwt_algorithm')
    def test_verify_token_extracts_all_claims(self, mock_algo, mock_secret):
        """Should extract all payload claims."""
        # Arrange
        secret = 'test_secret'
        algorithm = 'HS256'
        mock_secret.return_value = secret
        mock_algo.return_value = algorithm
        
        payload = {
            'user_id': 99,
            'username': 'multidata',
            'role': 'admin',
            'roles': ['user', 'admin'],
            'custom_claim': 'value',
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        token = pyjwt.encode(payload, secret, algorithm=algorithm)
        
        # Act
        result = verify_jwt_token(token)
        
        # Assert
        assert result['user_id'] == 99
        assert result['username'] == 'multidata'
        assert result['role'] == 'admin'
        assert 'admin' in result['roles']
        assert result['custom_claim'] == 'value'
