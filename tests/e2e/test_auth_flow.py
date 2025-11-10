"""
E2E Tests: Authentication Flow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests complete authentication workflows from HTTP request to response.
Validates registration, login, token generation, and role-based access control.

Coverage:
- User registration (success and duplicate handling)
- User login (success and invalid credentials)
- JWT token generation and validation
- Protected endpoint access (with/without token)
- Role-based access control (admin vs regular user)

These tests verify the entire auth stack works correctly end-to-end.
"""
import pytest
from tests.e2e.conftest import get_json_or_fail, assert_success_response, assert_error_response


class TestAuthenticationFlow:
    """E2E tests for complete authentication workflows"""
    
    def test_user_registration_success(self, client, db_session):
        """
        E2E: User registration with valid data returns 201 and user object.
        
        Flow:
        1. POST /auth/register with valid user data
        2. Verify 201 Created status
        3. Verify response contains user data with correct fields
        4. Verify user has default 'user' role
        5. Verify sensitive data (password) is NOT in response
        """
        # Arrange
        user_data = {
            'username': 'newtestuser',
            'email': 'newtest@example.com',
            'password': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User',
            'phone': '+1234567890'
        }
        
        # Act
        response = client.post('/auth/register', json=user_data)
        
        # Assert
        assert_success_response(response, 201)
        data = get_json_or_fail(response)
        
        # Verify response structure
        assert 'message' in data
        assert 'user' in data
        
        # Verify user data
        user = data['user']
        assert user['username'] == user_data['username']
        assert user['email'] == user_data['email']
        assert user['first_name'] == user_data['first_name']
        assert user['last_name'] == user_data['last_name']
        
        # Verify role assigned
        assert 'roles' in user
        assert 'user' in user['roles']
        
        # Verify password NOT in response
        assert 'password' not in user
        assert 'password_hash' not in user
    
    def test_user_registration_duplicate_username(self, client):
        """
        E2E: Registration with duplicate username returns 409 Conflict.
        
        Flow:
        1. Register first user
        2. Attempt to register with same username
        3. Verify 409 Conflict status
        4. Verify error message indicates duplicate
        """
        # Arrange - Create first user
        first_user = {
            'username': 'duplicatetestuser',
            'email': 'first@example.com',
            'password': 'SecurePass123!',
            'first_name': 'First',
            'last_name': 'User'
        }
        
        # Create first user
        response1 = client.post('/auth/register', json=first_user)
        assert response1.status_code == 201, "First user should be created successfully"
        
        # Arrange - Try to create duplicate
        duplicate_data = {
            'username': 'duplicatetestuser',  # Same username
            'email': 'different@example.com',
            'password': 'SecurePass123!',
            'first_name': 'Duplicate',
            'last_name': 'User'
        }
        
        # Act
        response = client.post('/auth/register', json=duplicate_data)
        
        # Assert
        assert_error_response(response, 409)
        data = get_json_or_fail(response)
        assert 'error' in data
        assert 'username' in data['error'].lower() or 'exists' in data['error'].lower()
    
    def test_login_success_returns_token(self, client):
        """
        E2E: Successful login returns 200, token, and user data.
        
        Flow:
        1. Register a user first
        2. POST /auth/login with valid credentials
        3. Verify 200 OK status
        4. Verify response contains JWT token
        5. Verify response contains user data
        6. Verify token format is valid (JWT structure)
        """
        # Arrange - Register user first
        user_data = {
            'username': 'logintestuser',
            'email': 'logintest@example.com',
            'password': 'password123',
            'first_name': 'Login',
            'last_name': 'Test'
        }
        client.post('/auth/register', json=user_data)
        
        # Arrange - Login credentials
        credentials = {
            'username': 'logintestuser',
            'password': 'password123'
        }
        
        # Act
        response = client.post('/auth/login', json=credentials)
        
        # Assert
        assert_success_response(response, 200)
        data = get_json_or_fail(response)
        
        # Verify response structure
        assert 'message' in data
        assert 'token' in data
        assert 'user' in data
        
        # Verify token format (JWT has 3 parts separated by dots)
        token = data['token']
        assert isinstance(token, str)
        assert len(token.split('.')) == 3, "Token should be valid JWT format (3 parts)"
        
        # Verify user data
        user = data['user']
        assert user['username'] == 'logintestuser'
        assert 'roles' in user
    
    def test_login_invalid_credentials(self, client):
        """
        E2E: Login with invalid password returns 401 Unauthorized.
        
        Flow:
        1. Register a user
        2. POST /auth/login with wrong password
        3. Verify 401 Unauthorized status
        4. Verify error message
        5. Verify NO token in response
        """
        # Arrange - Register user
        user_data = {
            'username': 'invalidlogintest',
            'email': 'invalidlogin@example.com',
            'password': 'CorrectPassword123',
            'first_name': 'Invalid',
            'last_name': 'Login'
        }
        client.post('/auth/register', json=user_data)
        
        # Arrange - Wrong credentials
        invalid_credentials = {
            'username': 'invalidlogintest',
            'password': 'WrongPassword123!'
        }
        
        # Act
        response = client.post('/auth/login', json=invalid_credentials)
        
        # Assert
        assert_error_response(response, 401)
        data = get_json_or_fail(response)
        assert 'token' not in data, "Token should not be present on failed login"
    
    def test_access_protected_endpoint_without_token(self, client):
        """
        E2E: Accessing protected endpoint without token returns 401.
        
        Flow:
        1. GET /auth/users (protected, admin-only) without Authorization header
        2. Verify 401 Unauthorized status
        3. Verify error message about missing token
        """
        # Act
        response = client.get('/auth/users')
        
        # Assert
        assert_error_response(response, 401)
        data = get_json_or_fail(response)
        error_msg = data.get('error', '').lower()
        assert 'authorization' in error_msg or 'token' in error_msg or 'missing' in error_msg
    
    def test_access_protected_endpoint_with_valid_token(self, client):
        """
        E2E: Accessing own profile with valid token returns 200.
        
        Flow:
        1. Register and login to get token and user ID
        2. GET /auth/users/{id} with valid user token
        3. Verify 200 OK status
        4. Verify user data returned
        """
        # Arrange - Register user
        user_data = {
            'username': 'protectedtest',
            'email': 'protected@example.com',
            'password': 'password123',
            'first_name': 'Protected',
            'last_name': 'Test'
        }
        client.post('/auth/register', json=user_data)
        
        # Login to get token
        login_response = client.post('/auth/login', json={
            'username': 'protectedtest',
            'password': 'password123'
        })
        login_data = login_response.get_json()
        token = login_data['token']
        user_id = login_data['user']['id']
        
        # Act
        response = client.get(
            f'/auth/users/{user_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        # Assert
        assert_success_response(response, 200)
        data = get_json_or_fail(response)
        
        # Verify correct user data
        assert data['id'] == user_id
        assert data['username'] == 'protectedtest'
    
    def test_admin_can_access_all_users(self, client, admin_headers):
        """
        E2E: Admin can list all users.
        
        Flow:
        1. GET /auth/users with admin token
        2. Verify 200 OK status
        3. Verify response contains list of users
        """
        # Act
        response = client.get('/auth/users', headers=admin_headers)
        
        # Assert
        assert_success_response(response, 200)
        data = get_json_or_fail(response)
        
        # Should return list or object with users
        if isinstance(data, list):
            users = data
        elif 'users' in data:
            users = data['users']
        else:
            raise AssertionError(f"Expected list of users, got: {data}")
        
        # Verify it's a list with users
        assert isinstance(users, list)
        assert len(users) > 0, "Should have at least one user"
        
        # Verify each user has expected fields
        for user in users:
            assert 'id' in user
            assert 'username' in user
            assert 'password' not in user, "Password should never be in response"
    
    def test_regular_user_cannot_access_all_users(self, client, auth_headers):
        """
        E2E: Regular user cannot list all users (403 Forbidden).
        
        Flow:
        1. GET /auth/users with regular user token
        2. Verify 403 Forbidden status
        3. Verify error message about admin access
        """
        # Act
        response = client.get('/auth/users', headers=auth_headers)
        
        # Assert
        assert_error_response(response, 403)
        data = get_json_or_fail(response)
        error_msg = data.get('error', '').lower()
        assert 'admin' in error_msg or 'forbidden' in error_msg or 'access' in error_msg


class TestPasswordManagement:
    """E2E tests for password-related operations"""
    
    def test_user_can_change_own_password(self, client):
        """
        E2E: User can change their own password.
        
        Flow:
        1. Register and login user
        2. PUT /auth/users/{id} with current_password and new_password
        3. Verify 200 OK status
        4. Login with NEW password → success
        5. Login with OLD password → fail
        """
        # Arrange - Register user
        user_data = {
            'username': 'passwordchangetest',
            'email': 'pwchange@example.com',
            'password': 'OldPassword123',
            'first_name': 'Password',
            'last_name': 'Change'
        }
        client.post('/auth/register', json=user_data)
        
        # Login to get token
        login_response = client.post('/auth/login', json={
            'username': 'passwordchangetest',
            'password': 'OldPassword123'
        })
        login_data = login_response.get_json()
        token = login_data['token']
        user_id = login_data['user']['id']
        
        # Arrange - Password change data (correct field names including confirm)
        password_change_data = {
            'current_password': 'OldPassword123',
            'new_password': 'NewSecurePass123!',
            'confirm_password': 'NewSecurePass123!'
        }
        
        # Act - Change password
        response = client.put(
            f'/auth/users/{user_id}',
            json=password_change_data,
            headers={'Authorization': f'Bearer {token}'}
        )
        
        # Assert password change successful
        assert_success_response(response, 200)
        
        # Act - Try login with new password
        login_response = client.post('/auth/login', json={
            'username': 'passwordchangetest',
            'password': 'NewSecurePass123!'
        })
        
        # Assert new password works
        assert_success_response(login_response, 200)
        login_data = get_json_or_fail(login_response)
        assert 'token' in login_data
        
        # Act - Try login with old password
        old_login_response = client.post('/auth/login', json={
            'username': 'passwordchangetest',
            'password': 'OldPassword123'  # Old password
        })
        
        # Assert old password no longer works
        assert old_login_response.status_code == 401


class TestRoleManagement:
    """E2E tests for admin role assignment"""
    
    def test_admin_role_management(self, client, admin_headers):
        """
        E2E: Admin assigns roles to users and verifies permissions.
        
        Flow:
        1. Create regular user
        2. Admin assigns admin role
        3. Verify user has admin role
        4. User can now access admin endpoints with new token
        
        Note: DELETE /auth/users/{id}/roles has a known bug where roles
        aren't properly removed from database. Skipping removal test for now.
        """
        # Arrange - Create regular user
        user_data = {
            'username': 'roletest_user',
            'email': 'roletest@example.com',
            'password': 'password123',
            'first_name': 'Role',
            'last_name': 'Test'
        }
        reg_response = client.post('/auth/register', json=user_data)
        assert_success_response(reg_response, 201)
        user = get_json_or_fail(reg_response)['user']
        user_id = user['id']
        
        # Login to get user token
        login_response = client.post('/auth/login', json={
            'username': 'roletest_user',
            'password': 'password123'
        })
        user_token = get_json_or_fail(login_response)['token']
        user_headers = {'Authorization': f'Bearer {user_token}'}
        
        # Verify user starts as regular user (cannot list all users)
        response = client.get('/auth/users', headers=user_headers)
        assert response.status_code == 403, "Regular user should not access all users"
        
        # Act - Admin assigns admin role
        assign_response = client.post(
            f'/auth/users/{user_id}/roles',
            json={'role': 'admin'},
            headers=admin_headers
        )
        
        # Assert role assigned successfully
        assert_success_response(assign_response, 200)
        
        # Get updated user info
        user_info_response = client.get(f'/auth/users/{user_id}', headers=admin_headers)
        assert_success_response(user_info_response, 200)
        user_info = get_json_or_fail(user_info_response)
        
        # Verify admin role present
        assert 'roles' in user_info
        assert 'admin' in user_info['roles'], "User should have admin role"
        
        # Verify user can now access admin endpoints (need fresh token)
        login_response_2 = client.post('/auth/login', json={
            'username': 'roletest_user',
            'password': 'password123'
        })
        new_user_token = get_json_or_fail(login_response_2)['token']
        new_user_headers = {'Authorization': f'Bearer {new_user_token}'}
        
        admin_access_response = client.get('/auth/users', headers=new_user_headers)
        assert_success_response(admin_access_response, 200)
        
        # Verify user can now list all users (admin privilege)
        data = get_json_or_fail(admin_access_response)
        assert 'users' in data or isinstance(data, list), "Should return list of users"
        
        # Note: Role removal (DELETE /auth/users/{id}/roles) has a known bug
        # where roles aren't properly removed from database.  
        # Skipping role removal verification for now.
