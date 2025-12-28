"""
Auth Module Tests
Tests for authentication endpoints: login, register, token refresh.
"""

import pytest
import json
from datetime import datetime, timedelta, timezone
from tests.unit.test_helpers import (
    assert_success_response, 
    assert_error_response,
    assert_validation_error,
    assert_unauthorized_error
)


class TestAuthRegister:
    """Tests for user registration endpoint."""
    
    def test_register_chef_success(self, client, db_session):
        """Test successful chef registration."""
        data = {
            'username': 'newchef',
            'email': 'newchef@test.com',
            'password': 'SecurePass123!',
            'role': 'chef'
        }
        
        response = client.post('/auth/register', 
                              json=data,
                              headers={'Content-Type': 'application/json'})
        
        result = assert_success_response(response, 201)
        assert result['data']['email'] == 'newchef@test.com'
        assert result['data']['role'] == 'chef'
    
    def test_register_admin_ignored(self, client, db_session):
        """Test that admin role in registration is ignored (becomes chef)."""
        data = {
            'username': 'newadmin',
            'email': 'newadmin@test.com',
            'password': 'SecurePass123!',
            'role': 'admin'
        }
        
        response = client.post('/auth/register', 
                              json=data,
                              headers={'Content-Type': 'application/json'})
        
        result = assert_success_response(response, 201)
        # Should create as chef, not admin (security requirement)
        assert result['data']['role'] == 'chef'
    
    def test_register_duplicate_email(self, client, db_session, test_user):
        """Test registration with existing email."""
        data = {
            'username': 'duplicateuser',
            'email': test_user.email,
            'password': 'AnotherPass123!',
            'role': 'chef'
        }
        
        response = client.post('/auth/register', 
                              json=data,
                              headers={'Content-Type': 'application/json'})
        
        assert_error_response(response, 400)
    
    def test_register_invalid_email(self, client, db_session):
        """Test registration with invalid email format."""
        data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'SecurePass123!',
            'role': 'chef'
        }
        
        response = client.post('/auth/register', 
                              json=data,
                              headers={'Content-Type': 'application/json'})
        
        assert_validation_error(response)
    
    def test_register_weak_password(self, client, db_session):
        """Test registration with weak password."""
        data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'password': '123',
            'role': 'chef'
        }
        
        response = client.post('/auth/register', 
                              json=data,
                              headers={'Content-Type': 'application/json'})
        
        assert_validation_error(response)
    
    def test_register_invalid_role(self, client, db_session):
        """Test registration with invalid role."""
        data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'SecurePass123!',
            'role': 'superadmin'
        }
        
        response = client.post('/auth/register', 
                              json=data,
                              headers={'Content-Type': 'application/json'})
        
        assert_validation_error(response)
    
    def test_register_missing_fields(self, client, db_session):
        """Test registration with missing required fields."""
        data = {
            'email': 'test@test.com'
            # Missing username, password and role
        }
        
        response = client.post('/auth/register', 
                              json=data,
                              headers={'Content-Type': 'application/json'})
        
        assert_validation_error(response)


class TestAuthLogin:
    """Tests for user login endpoint."""
    
    def test_login_success(self, client, db_session, test_user):
        """Test successful login."""
        data = {
            'username': test_user.username,
            'password': 'password123'
        }
        
        response = client.post('/auth/login', 
                              json=data,
                              headers={'Content-Type': 'application/json'})
        
        result = assert_success_response(response, 200)
        assert 'user' in result['data']
        assert 'token' in result['data']
        assert result['data']['user']['email'] == test_user.email
    
    def test_login_wrong_password(self, client, db_session, test_user):
        """Test login with incorrect password."""
        data = {
            'username': test_user.username,
            'password': 'wrongpassword'
        }
        
        response = client.post('/auth/login', 
                              json=data,
                              headers={'Content-Type': 'application/json'})
        
        assert_unauthorized_error(response)
    
    def test_login_nonexistent_user(self, client, db_session):
        """Test login with non-existent username."""
        data = {
            'username': 'nonexistent',
            'password': 'password123'
        }
        
        response = client.post('/auth/login', 
                              json=data,
                              headers={'Content-Type': 'application/json'})
        
        assert_unauthorized_error(response)
    
    def test_login_inactive_user(self, client, db_session, test_user):
        """Test login with inactive user account."""
        # Deactivate user
        test_user.is_active = False
        db_session.commit()
        
        data = {
            'username': test_user.username,
            'password': 'password123'
        }
        
        response = client.post('/auth/login', 
                              json=data,
                              headers={'Content-Type': 'application/json'})
        
        # API returns 401 for inactive users
        assert_unauthorized_error(response)
    
    def test_login_missing_fields(self, client, db_session):
        """Test login with missing fields."""
        data = {
            'username': 'testuser'
            # Missing password
        }
        
        response = client.post('/auth/login', 
                              json=data,
                              headers={'Content-Type': 'application/json'})
        
        assert_validation_error(response)



class TestAuthProtectedEndpoints:
    """Tests for JWT authentication middleware."""
    
    def test_access_with_valid_token(self, client, db_session, auth_headers, test_chef):
        """Test accessing protected endpoint with valid token."""
        response = client.get('/chefs/profile', headers=auth_headers)
        
        # Should succeed (200 or 404 depending on data)
        assert response.status_code in [200, 404]
    
    def test_access_without_token(self, client, db_session):
        """Test accessing protected endpoint without token."""
        response = client.get('/dishes')
        
        assert_unauthorized_error(response)
    
    def test_access_with_invalid_token(self, client, db_session):
        """Test accessing protected endpoint with invalid token."""
        headers = {
            'Authorization': 'Bearer invalid-token',
            'Content-Type': 'application/json'
        }
        
        response = client.get('/dishes', headers=headers)
        
        assert_unauthorized_error(response)
    
    def test_access_with_expired_token(self, client, db_session, test_user):
        """Test accessing protected endpoint with expired token."""
        import jwt
        from config.settings import JWT_SECRET_KEY, JWT_ALGORITHM
        
        # Create expired token
        payload = {
            'user_id': test_user.id,
            'email': test_user.email,
            'role': test_user.role.value if hasattr(test_user.role, 'value') else test_user.role,
                'exp': (datetime.now(timezone.utc) - timedelta(hours=1)).replace(tzinfo=None)  # Expired 1 hour ago
        }
        expired_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        
        headers = {
            'Authorization': f'Bearer {expired_token}',
            'Content-Type': 'application/json'
        }
        
        response = client.get('/dishes', headers=headers)
        
        assert_unauthorized_error(response)
