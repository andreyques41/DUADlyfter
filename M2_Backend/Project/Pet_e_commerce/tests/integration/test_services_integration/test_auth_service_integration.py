"""
Integration Tests: Auth Service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests authentication service with real database operations.
Validates complete flows: registration, login, role assignment, password changes.

These tests use a real database (PostgreSQL test) to ensure:
- Services and repositories work together correctly
- Database constraints are respected
- Transactions commit properly
- Foreign keys and relationships work
"""
import pytest
from flask import g
from app.auth.services.auth_service import AuthService
from app.auth.services.security_service import hash_password, verify_password
from app.auth.repositories.user_repository import UserRepository
from app.core.lib.jwt import generate_jwt_token


@pytest.mark.integration
class TestUserRegistrationIntegration:
    """Integration tests for user registration flow."""
    
    def test_register_user_complete_flow(self, app, integration_db_session):
        """Test complete user registration: hash password + create user + assign default role."""
        with app.app_context():
            g.db = integration_db_session
            # Arrange
            auth_service = AuthService()
            password_plain = 'SecurePass123!'
            password_hash = hash_password(password_plain)
            
            # Act - Simulate registration flow (like RegisterAPI does)
            new_user, error = auth_service.create_user(
                username='newuser',
                email='newuser@example.com',
                password=password_plain,
                first_name='New',
                last_name='User',
                role_name='user'
            )
            
            # Assert
            assert error is None
            assert new_user is not None
            assert new_user.username == 'newuser'
            assert new_user.email == 'newuser@example.com'
            
            # Verify password was hashed (not stored as plain text)
            assert new_user.password_hash != password_plain
            assert len(new_user.password_hash) > 50  # Bcrypt hash length
            assert verify_password(password_plain, new_user.password_hash)
            
            # Verify user has default role
            assert len(new_user.user_roles) == 1
            assert new_user.user_roles[0].role.name == 'user'
            
            # Verify user persisted in database
            persisted_user = auth_service.get_user_by_username('newuser')
            assert persisted_user is not None
            assert persisted_user.id == new_user.id
    
    def test_register_duplicate_username_fails(self, app, integration_db_session):
        """Test that registering duplicate username fails."""
        with app.app_context():
            g.db = integration_db_session
            
            # Arrange
            auth_service = AuthService()
            password_plain = ''
            
            # Act - first registration
            first_user, error1 = auth_service.create_user(
                username='duplicate',
                email='first@example.com',
                password=password_plain,
                first_name='First',
                last_name='User'
            )
            assert error1 is None
            assert first_user is not None
            
            # Act - second registration with same username
            second_user, error2 = auth_service.create_user(
                username='duplicate',
                email='second@example.com',
                password=password_plain,
                first_name='Second',
                last_name='User'
            )
            
            # Assert
            assert second_user is None
            assert error2 is not None
            assert 'already exists' in error2.lower()
    
    def test_register_duplicate_email_fails(self, app, integration_db_session):
        """Test that registering duplicate email fails."""
        with app.app_context():
            g.db = integration_db_session
            
            # Arrange
            auth_service = AuthService()
            password_plain = ''
            
            # Act - first user
            first_user, error1 = auth_service.create_user(
                username='user1',
                email='same@example.com',
                password=password_plain,
                first_name='User',
                last_name='One'
            )
            assert error1 is None
            
            # Act - second user with same email
            second_user, error2 = auth_service.create_user(
                username='user2',
                email='same@example.com',
                password=password_plain,
                first_name='User',
                last_name='Two'
            )
            
            # Assert
            assert second_user is None
            assert error2 is not None
            assert 'already exists' in error2.lower()


@pytest.mark.integration
class TestUserLoginIntegration:
    """Integration tests for user login flow."""
    
    def test_login_with_valid_credentials(self, app, integration_db_session):
        """Test complete login flow: find user + verify password + generate JWT."""
        with app.app_context():
            g.db = integration_db_session
            
            # Arrange - Register user first
            auth_service = AuthService()
            password_plain = 'MyPassword123!'
            password_hash = hash_password(password_plain)
            
            new_user, error = auth_service.create_user(
                username='loginuser',
                email='login@example.com',
                password=password_plain,
                first_name='Login',
                last_name='User'
            )
            assert error is None
            
            # Act - Simulate login flow (like AuthAPI does)
            user = auth_service.get_user_by_username('loginuser')
            assert user is not None
            
            # Verify password
            password_valid = verify_password(password_plain, user.password_hash)
            assert password_valid is True
            
            # Generate JWT token
            token = generate_jwt_token(user)
            
            # Assert
            assert token is not None
            assert isinstance(token, str)
            assert len(token) > 20  # JWT tokens are long
    
    def test_login_with_invalid_password(self, app, integration_db_session):
        """Test login fails with wrong password."""
        with app.app_context():
            g.db = integration_db_session
            
            # Arrange - Register user
            auth_service = AuthService()
            password_plain = ''
            
            new_user, error = auth_service.create_user(
                username='testuser',
                email='test@example.com',
                password=password_plain,
                first_name='Test',
                last_name='User'
            )
            assert error is None
            
            # Act - Try to login with wrong password
            user = auth_service.get_user_by_username('testuser')
            password_valid = verify_password('WrongPassword!', user.password_hash)
            
            # Assert
            assert password_valid is False
    
    def test_login_with_nonexistent_user(self, app, integration_db_session):
        """Test login fails for non-existent user."""
        with app.app_context():
            g.db = integration_db_session
            
            # Arrange
            auth_service = AuthService()
            
            # Act
            user = auth_service.get_user_by_username('nonexistent')
            
            # Assert
            assert user is None


@pytest.mark.integration
class TestRoleAssignmentIntegration:
    """Integration tests for role assignment."""
    
    def test_assign_admin_role_to_user(self, app, integration_db_session):
        """Test assigning admin role to existing user."""
        with app.app_context():
            g.db = integration_db_session
            
            # Arrange
            auth_service = AuthService()
            user_repo = UserRepository()
            password_plain = ''
            
            # Create user with default role
            new_user, error = auth_service.create_user(
                username='regularuser',
                email='regular@example.com',
                password=password_plain,
                first_name='Regular',
                last_name='User',
                role_name='user'
            )
            assert error is None
            user_id = new_user.id
            
            # Act - assign admin role
            admin_role_id = 2  # From load_reference_data
            result = user_repo.assign_role(user_id, admin_role_id)
            
            # Assert
            assert result is True
            
            # Verify user now has admin role
            user = user_repo.get_by_id(user_id)
            role_names = [ur.role.name for ur in user.user_roles]
            assert 'admin' in role_names
            assert 'user' in role_names  # Should still have user role
    
    def test_remove_role_from_user(self, app, integration_db_session):
        """Test removing role from user."""
        with app.app_context():
            g.db = integration_db_session
            
            # Arrange
            auth_service = AuthService()
            user_repo = UserRepository()
            password_plain = ''
            
            # Create user
            new_user, error = auth_service.create_user(
                username='testuser',
                email='test@example.com',
                password=password_plain,
                first_name='Test',
                last_name='User'
            )
            assert error is None
            user_id = new_user.id
            
            # Get the role_id for the default role ('user')
            from app.core.reference_data import ReferenceData
            role_id = ReferenceData.get_role_id('user')
            assert role_id is not None
            
            # Act - remove role
            result = user_repo.remove_role(user_id, role_id)
            
            # Assert
            assert result is True
            
            # Verify role was removed
            user = user_repo.get_by_id(user_id)
            assert len(user.user_roles) == 0


@pytest.mark.integration
class TestPasswordManagementIntegration:
    """Integration tests for password management."""
    
    def test_change_password(self, app, integration_db_session):
        """Test changing user password."""
        with app.app_context():
            g.db = integration_db_session
            from app.auth.services.user_service import UserService
            
            # Arrange
            auth_service = AuthService()
            user_service = UserService()
            old_password_plain = 'OldPassword123!'
            old_password_hash = hash_password(old_password_plain)
            
            # Create user
            new_user, error = auth_service.create_user(
                username='changepass',
                email='change@example.com',
                password=old_password_plain,
                first_name='Change',
                last_name='Password'
            )
            assert error is None
            user_id = new_user.id
            
            # Verify old password works
            assert verify_password(old_password_plain, new_user.password_hash)
            
            # Act - change password (simulate route flow)
            new_password_plain = 'NewPassword123!'
            new_password_hash = hash_password(new_password_plain)
            updated_user, error = user_service.update_user_password(user_id, new_password_hash)
            
            # Assert
            assert error is None
            assert updated_user is not None
            
            # Verify can verify with new password
            assert verify_password(new_password_plain, updated_user.password_hash)
            
            # Verify cannot verify with old password
            assert not verify_password(old_password_plain, updated_user.password_hash)

    def test_change_password_verification(self, app, integration_db_session):
        """Test password verification before change."""
        with app.app_context():
            g.db = integration_db_session
            from app.auth.services.user_service import UserService
            
            # Arrange
            auth_service = AuthService()
            user_service = UserService()
            correct_password = 'MyPassword123!'
            password_hash = hash_password(correct_password)
            
            # Create user
            new_user, error = auth_service.create_user(
                username='secureuser',
                email='secure@example.com',
                password=correct_password,  # Fixed: was password_plain
                first_name='Secure',
                last_name='User'
            )
            assert error is None
            
            # Act - verify current password (like route does before allowing change)
            user = user_service.get_user_by_id(new_user.id)  # Fixed: use user_service, not auth_service
            wrong_password_valid = verify_password('WrongOldPass!', user.password_hash)
            correct_password_valid = verify_password(correct_password, user.password_hash)
            
            # Assert
            assert wrong_password_valid is False
            assert correct_password_valid is True


@pytest.mark.integration
class TestUserProfileIntegration:
    """Integration tests for user profile management."""
    
    def test_update_user_profile(self, app, integration_db_session):
        """Test updating user profile information."""
        with app.app_context():
            g.db = integration_db_session
            from app.auth.services.user_service import UserService
            
            # Arrange
            auth_service = AuthService()
            user_service = UserService()
            password_plain = 'OriginalPassword123!'
            
            # Create user
            new_user, error = auth_service.create_user(
                username='updateuser',
                email='update@example.com',
                password=password_plain,
                first_name='Original',
                last_name='Name'
            )
            assert error is None
            user_id = new_user.id
            
            # Act - update profile
            updated_user, error = user_service.update_user_profile(
                user_id,
                first_name='Updated',
                last_name='NewName',
                email='newemail@example.com'
            )
            
            # Assert
            assert error is None
            assert updated_user is not None
            assert updated_user.first_name == 'Updated'
            assert updated_user.last_name == 'NewName'
            assert updated_user.email == 'newemail@example.com'
            
            # Verify changes persisted (Fixed: get_user_by_id returns User object, not tuple)
            persisted_user = user_service.get_user_by_id(user_id)
            assert persisted_user.first_name == 'Updated'
            assert persisted_user.last_name == 'NewName'
            assert persisted_user.email == 'newemail@example.com'
    
    def test_get_all_users(self, app, integration_db_session):
        """Test retrieving all users."""
        with app.app_context():
            g.db = integration_db_session
            from app.auth.services.user_service import UserService
            
            # Arrange
            auth_service = AuthService()
            user_service = UserService()
            password_plain = 'TestPassword123!'
            
            # Create multiple users with unique usernames
            for i in range(3):
                new_user, error = auth_service.create_user(
                    username=f'bulkuser{i}',  # Changed from 'user{i}' to avoid conflicts
                    email=f'bulkuser{i}@example.com',
                    password=password_plain,
                    first_name='User',
                    last_name=f'{i}'
                )
                assert error is None
            
            # Act (Fixed: use user_service, not auth_service)
            all_users = user_service.get_all_users()
            
            # Assert
            assert len(all_users) >= 3
            usernames = [u.username for u in all_users]
            assert 'bulkuser0' in usernames
            assert 'bulkuser1' in usernames
            assert 'bulkuser2' in usernames
