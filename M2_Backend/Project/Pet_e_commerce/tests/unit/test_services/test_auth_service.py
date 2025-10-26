"""
Unit tests for AuthService module.

Tests cover:
- User retrieval by ID, username, email, and all users
- Role management (get, assign, remove)
- User validation (username/email existence)
- User CRUD operations (create, update profile, update password, delete)
- Role assignment with rollback on failure
- Validation helpers and error handling
"""
import pytest
from unittest.mock import Mock, MagicMock
from app.auth.services.auth_service import AuthService
from app.auth.models.user import User


@pytest.fixture
def service():
    """Fixture for AuthService instance."""
    return AuthService()


@pytest.fixture
def mock_user():
    """Fixture for mock User instance."""
    user = Mock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.password_hash = "hashed_password"
    user.first_name = "Test"
    user.last_name = "User"
    user.phone = "1234567890"
    
    # Mock user_roles relationship
    mock_role = Mock()
    mock_role.name = "user"
    
    mock_user_role = Mock()
    mock_user_role.role = mock_role
    
    user.user_roles = [mock_user_role]
    
    return user


@pytest.fixture
def mock_admin_user():
    """Fixture for mock admin User instance."""
    user = Mock(spec=User)
    user.id = 2
    user.username = "admin"
    user.email = "admin@example.com"
    user.password_hash = "hashed_admin_password"
    
    # Mock admin role
    mock_role = Mock()
    mock_role.name = "admin"
    
    mock_user_role = Mock()
    mock_user_role.role = mock_role
    
    user.user_roles = [mock_user_role]
    
    return user


class TestAuthServiceRetrieval:
    """Test user retrieval methods."""
    
    def test_get_user_by_id_success(self, service, mock_user, mocker):
        """Test successful user retrieval by ID."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=mock_user)
        
        result = service.get_user_by_id(1)
        
        assert result == mock_user
        service.user_repo.get_by_id.assert_called_once_with(1)
    
    def test_get_user_by_id_not_found(self, service, mocker):
        """Test user retrieval when user not found."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=None)
        
        result = service.get_user_by_id(999)
        
        assert result is None
    
    def test_get_user_by_username_success(self, service, mock_user, mocker):
        """Test successful user retrieval by username."""
        mocker.patch.object(service.user_repo, 'get_by_username', return_value=mock_user)
        
        result = service.get_user_by_username("testuser")
        
        assert result == mock_user
        service.user_repo.get_by_username.assert_called_once_with("testuser")
    
    def test_get_user_by_email_success(self, service, mock_user, mocker):
        """Test successful user retrieval by email."""
        mocker.patch.object(service.user_repo, 'get_by_email', return_value=mock_user)
        
        result = service.get_user_by_email("test@example.com")
        
        assert result == mock_user
        service.user_repo.get_by_email.assert_called_once_with("test@example.com")
    
    def test_get_all_users(self, service, mock_user, mock_admin_user, mocker):
        """Test retrieval of all users."""
        mocker.patch.object(service.user_repo, 'get_all', return_value=[mock_user, mock_admin_user])
        
        result = service.get_all_users()
        
        assert len(result) == 2
        assert mock_user in result
        assert mock_admin_user in result


class TestAuthServiceRoleManagement:
    """Test role management methods."""
    
    def test_get_user_roles_success(self, service, mock_user, mocker):
        """Test successful retrieval of user roles."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=mock_user)
        
        roles, error = service.get_user_roles(1)
        
        assert error is None
        assert roles == ["user"]
    
    def test_get_user_roles_user_not_found(self, service, mocker):
        """Test getting roles when user not found."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=None)
        
        roles, error = service.get_user_roles(999)
        
        assert roles is None
        assert error == "User not found"
    
    def test_get_user_roles_no_roles_returns_default(self, service, mocker):
        """Test getting roles returns default 'user' when no roles assigned."""
        user = Mock(spec=User)
        user.user_roles = []
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=user)
        
        roles, error = service.get_user_roles(1)
        
        assert error is None
        assert roles == ["user"]
    
    def test_get_user_roles_handles_exception(self, service, mocker):
        """Test exception handling in get_user_roles."""
        mocker.patch.object(service.user_repo, 'get_by_id', side_effect=Exception("Database error"))
        
        roles, error = service.get_user_roles(1)
        
        assert roles is None
        assert "Error getting user roles" in error
    
    def test_assign_role_to_user_success(self, service, mock_user, mocker):
        """Test successful role assignment."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=mock_user)
        mocker.patch('app.core.reference_data.ReferenceData.get_role_id', return_value=2)
        mocker.patch.object(service, 'get_user_roles', return_value=(["user"], None))
        mocker.patch.object(service.user_repo, 'assign_role', return_value=True)
        
        success, error = service.assign_role_to_user(1, "admin")
        
        assert success is True
        assert error is None
        service.user_repo.assign_role.assert_called_once_with(1, 2)
    
    def test_assign_role_user_not_found(self, service, mocker):
        """Test role assignment when user not found."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=None)
        
        success, error = service.assign_role_to_user(999, "admin")
        
        assert success is False
        assert error == "User not found"
    
    def test_assign_role_invalid_role(self, service, mock_user, mocker):
        """Test role assignment with invalid role name."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=mock_user)
        mocker.patch('app.core.reference_data.ReferenceData.get_role_id', return_value=None)
        
        success, error = service.assign_role_to_user(1, "invalid_role")
        
        assert success is False
        assert "Invalid role" in error
    
    def test_assign_role_already_assigned(self, service, mock_user, mocker):
        """Test assigning role that user already has."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=mock_user)
        mocker.patch('app.core.reference_data.ReferenceData.get_role_id', return_value=2)
        mocker.patch.object(service, 'get_user_roles', return_value=(["admin"], None))
        
        success, error = service.assign_role_to_user(1, "admin")
        
        assert success is False
        assert "already has role" in error
    
    def test_assign_role_repository_failure(self, service, mock_user, mocker):
        """Test role assignment when repository fails."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=mock_user)
        mocker.patch('app.core.reference_data.ReferenceData.get_role_id', return_value=2)
        mocker.patch.object(service, 'get_user_roles', return_value=(["user"], None))
        mocker.patch.object(service.user_repo, 'assign_role', return_value=False)
        
        success, error = service.assign_role_to_user(1, "admin")
        
        assert success is False
        assert "Failed to assign role" in error
    
    def test_assign_role_handles_exception(self, service, mock_user, mocker):
        """Test exception handling in assign_role."""
        mocker.patch.object(service.user_repo, 'get_by_id', side_effect=Exception("Database error"))
        
        success, error = service.assign_role_to_user(1, "admin")
        
        assert success is False
        assert "Error assigning role" in error
    
    def test_remove_role_from_user_success(self, service, mock_user, mocker):
        """Test successful role removal."""
        # User has both "user" and "admin" roles
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=mock_user)
        mocker.patch('app.core.reference_data.ReferenceData.get_role_id', return_value=2)
        mocker.patch.object(service, 'get_user_roles', return_value=(["user", "admin"], None))
        mocker.patch.object(service.user_repo, 'remove_role', return_value=True)
        
        success, error = service.remove_role_from_user(1, "admin")
        
        assert success is True
        assert error is None
        service.user_repo.remove_role.assert_called_once_with(1, 2)
    
    def test_remove_role_user_not_found(self, service, mocker):
        """Test role removal when user not found."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=None)
        
        success, error = service.remove_role_from_user(999, "admin")
        
        assert success is False
        assert error == "User not found"
    
    def test_remove_role_invalid_role(self, service, mock_user, mocker):
        """Test role removal with invalid role name."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=mock_user)
        mocker.patch('app.core.reference_data.ReferenceData.get_role_id', return_value=None)
        
        success, error = service.remove_role_from_user(1, "invalid_role")
        
        assert success is False
        assert "Invalid role" in error
    
    def test_remove_role_user_does_not_have_role(self, service, mock_user, mocker):
        """Test removing role that user doesn't have."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=mock_user)
        mocker.patch('app.core.reference_data.ReferenceData.get_role_id', return_value=2)
        mocker.patch.object(service, 'get_user_roles', return_value=(["user"], None))
        
        success, error = service.remove_role_from_user(1, "admin")
        
        assert success is False
        assert "does not have role" in error
    
    def test_remove_last_role_prevented(self, service, mock_user, mocker):
        """Test that removing last role is prevented."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=mock_user)
        mocker.patch('app.core.reference_data.ReferenceData.get_role_id', return_value=1)
        mocker.patch.object(service, 'get_user_roles', return_value=(["user"], None))
        
        success, error = service.remove_role_from_user(1, "user")
        
        assert success is False
        assert "Cannot remove the last role" in error
    
    def test_remove_role_repository_failure(self, service, mock_user, mocker):
        """Test role removal when repository fails."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=mock_user)
        mocker.patch('app.core.reference_data.ReferenceData.get_role_id', return_value=2)
        mocker.patch.object(service, 'get_user_roles', return_value=(["user", "admin"], None))
        mocker.patch.object(service.user_repo, 'remove_role', return_value=False)
        
        success, error = service.remove_role_from_user(1, "admin")
        
        assert success is False
        assert "Failed to remove role" in error
    
    def test_remove_role_handles_exception(self, service, mock_user, mocker):
        """Test exception handling in remove_role."""
        mocker.patch.object(service.user_repo, 'get_by_id', side_effect=Exception("Database error"))
        
        success, error = service.remove_role_from_user(1, "admin")
        
        assert success is False
        assert "Error removing role" in error


class TestAuthServiceValidation:
    """Test user validation methods."""
    
    def test_check_username_exists_true(self, service, mocker):
        """Test checking if username exists - returns True."""
        mocker.patch.object(service.user_repo, 'exists_by_username', return_value=True)
        
        result = service.check_username_exists("testuser")
        
        assert result is True
    
    def test_check_username_exists_false(self, service, mocker):
        """Test checking if username exists - returns False."""
        mocker.patch.object(service.user_repo, 'exists_by_username', return_value=False)
        
        result = service.check_username_exists("newuser")
        
        assert result is False
    
    def test_check_email_exists_true(self, service, mocker):
        """Test checking if email exists - returns True."""
        mocker.patch.object(service.user_repo, 'exists_by_email', return_value=True)
        
        result = service.check_email_exists("test@example.com")
        
        assert result is True
    
    def test_check_email_exists_false(self, service, mocker):
        """Test checking if email exists - returns False."""
        mocker.patch.object(service.user_repo, 'exists_by_email', return_value=False)
        
        result = service.check_email_exists("new@example.com")
        
        assert result is False


class TestAuthServiceUserCreation:
    """Test user creation methods."""
    
    def test_create_user_success(self, service, mock_user, mocker):
        """Test successful user creation with default role."""
        mocker.patch.object(service, '_validate_user_uniqueness', return_value=None)
        mocker.patch.object(service, '_validate_and_get_role_id', return_value=(1, None))
        mocker.patch.object(service, '_build_user_instance', return_value=mock_user)
        mocker.patch.object(service.user_repo, 'create', return_value=mock_user)
        mocker.patch.object(service, '_assign_role_with_rollback', return_value=None)
        
        user, error = service.create_user("testuser", "test@example.com", "hashed_password")
        
        assert error is None
        assert user == mock_user
    
    def test_create_user_with_admin_role(self, service, mock_admin_user, mocker):
        """Test user creation with admin role."""
        mocker.patch.object(service, '_validate_user_uniqueness', return_value=None)
        mocker.patch.object(service, '_validate_and_get_role_id', return_value=(2, None))
        mocker.patch.object(service, '_build_user_instance', return_value=mock_admin_user)
        mocker.patch.object(service.user_repo, 'create', return_value=mock_admin_user)
        mocker.patch.object(service, '_assign_role_with_rollback', return_value=None)
        
        user, error = service.create_user("admin", "admin@example.com", "hashed_password", role_name="admin")
        
        assert error is None
        assert user == mock_admin_user
    
    def test_create_user_username_exists(self, service, mocker):
        """Test user creation when username already exists."""
        mocker.patch.object(service, '_validate_user_uniqueness', return_value="Username already exists")
        
        user, error = service.create_user("testuser", "test@example.com", "hashed_password")
        
        assert user is None
        assert error == "Username already exists"
    
    def test_create_user_email_exists(self, service, mocker):
        """Test user creation when email already exists."""
        mocker.patch.object(service, '_validate_user_uniqueness', return_value="Email already exists")
        
        user, error = service.create_user("testuser", "test@example.com", "hashed_password")
        
        assert user is None
        assert error == "Email already exists"
    
    def test_create_user_invalid_role(self, service, mocker):
        """Test user creation with invalid role."""
        mocker.patch.object(service, '_validate_user_uniqueness', return_value=None)
        mocker.patch.object(service, '_validate_and_get_role_id', return_value=(None, "Invalid role: invalid_role"))
        
        user, error = service.create_user("testuser", "test@example.com", "hashed_password", role_name="invalid_role")
        
        assert user is None
        assert "Invalid role" in error
    
    def test_create_user_repository_failure(self, service, mock_user, mocker):
        """Test user creation when repository create fails."""
        mocker.patch.object(service, '_validate_user_uniqueness', return_value=None)
        mocker.patch.object(service, '_validate_and_get_role_id', return_value=(1, None))
        mocker.patch.object(service, '_build_user_instance', return_value=mock_user)
        mocker.patch.object(service.user_repo, 'create', return_value=None)
        
        user, error = service.create_user("testuser", "test@example.com", "hashed_password")
        
        assert user is None
        assert error == "Failed to create user"
    
    def test_create_user_role_assignment_fails(self, service, mock_user, mocker):
        """Test user creation when role assignment fails (rollback triggered)."""
        mocker.patch.object(service, '_validate_user_uniqueness', return_value=None)
        mocker.patch.object(service, '_validate_and_get_role_id', return_value=(1, None))
        mocker.patch.object(service, '_build_user_instance', return_value=mock_user)
        mocker.patch.object(service.user_repo, 'create', return_value=mock_user)
        mocker.patch.object(service, '_assign_role_with_rollback', return_value="Failed to assign role to user")
        
        user, error = service.create_user("testuser", "test@example.com", "hashed_password")
        
        assert user is None
        assert error == "Failed to assign role to user"
    
    def test_create_user_handles_exception(self, service, mocker):
        """Test exception handling in create_user."""
        mocker.patch.object(service, '_validate_user_uniqueness', side_effect=Exception("Database error"))
        
        user, error = service.create_user("testuser", "test@example.com", "hashed_password")
        
        assert user is None
        assert "Error creating user" in error


class TestAuthServiceUserUpdate:
    """Test user update methods."""
    
    def test_update_user_profile_success(self, service, mock_user, mocker):
        """Test successful user profile update."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=mock_user)
        mocker.patch.object(service.user_repo, 'update', return_value=mock_user)
        
        user, error = service.update_user_profile(1, first_name="Updated", last_name="Name")
        
        assert error is None
        assert user == mock_user
        service.user_repo.update.assert_called_once_with(mock_user)
    
    def test_update_user_profile_not_found(self, service, mocker):
        """Test profile update when user not found."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=None)
        
        user, error = service.update_user_profile(999, first_name="Test")
        
        assert user is None
        assert error == "User not found"
    
    def test_update_user_profile_repository_failure(self, service, mock_user, mocker):
        """Test profile update when repository update fails."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=mock_user)
        mocker.patch.object(service.user_repo, 'update', return_value=None)
        
        user, error = service.update_user_profile(1, first_name="Updated")
        
        assert user is None
        assert error == "Failed to update profile"
    
    def test_update_user_profile_handles_exception(self, service, mocker):
        """Test exception handling in update_user_profile."""
        mocker.patch.object(service.user_repo, 'get_by_id', side_effect=Exception("Database error"))
        
        user, error = service.update_user_profile(1, first_name="Test")
        
        assert user is None
        assert "Error updating profile" in error
    
    def test_update_user_password_success(self, service, mock_user, mocker):
        """Test successful password update."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=mock_user)
        mocker.patch.object(service.user_repo, 'update', return_value=mock_user)
        
        user, error = service.update_user_password(1, "new_hashed_password")
        
        assert error is None
        assert user == mock_user
        assert mock_user.password_hash == "new_hashed_password"
        service.user_repo.update.assert_called_once_with(mock_user)
    
    def test_update_user_password_not_found(self, service, mocker):
        """Test password update when user not found."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=None)
        
        user, error = service.update_user_password(999, "new_hashed_password")
        
        assert user is None
        assert error == "User not found"
    
    def test_update_user_password_repository_failure(self, service, mock_user, mocker):
        """Test password update when repository update fails."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=mock_user)
        mocker.patch.object(service.user_repo, 'update', return_value=None)
        
        user, error = service.update_user_password(1, "new_hashed_password")
        
        assert user is None
        assert error == "Failed to update password"
    
    def test_update_user_password_handles_exception(self, service, mocker):
        """Test exception handling in update_user_password."""
        mocker.patch.object(service.user_repo, 'get_by_id', side_effect=Exception("Database error"))
        
        user, error = service.update_user_password(1, "new_hashed_password")
        
        assert user is None
        assert "Error updating password" in error


class TestAuthServiceUserDeletion:
    """Test user deletion methods."""
    
    def test_delete_user_success(self, service, mock_user, mocker):
        """Test successful user deletion."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=mock_user)
        mocker.patch.object(service.user_repo, 'delete', return_value=True)
        
        success, error = service.delete_user(1)
        
        assert success is True
        assert error is None
        service.user_repo.delete.assert_called_once_with(1)
    
    def test_delete_user_not_found(self, service, mocker):
        """Test user deletion when user not found."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=None)
        
        success, error = service.delete_user(999)
        
        assert success is False
        assert error == "User not found"
    
    def test_delete_user_repository_failure(self, service, mock_user, mocker):
        """Test user deletion when repository delete fails."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=mock_user)
        mocker.patch.object(service.user_repo, 'delete', return_value=False)
        
        success, error = service.delete_user(1)
        
        assert success is False
        assert error == "Failed to delete user"
    
    def test_delete_user_handles_exception(self, service, mocker):
        """Test exception handling in delete_user."""
        mocker.patch.object(service.user_repo, 'get_by_id', side_effect=Exception("Database error"))
        
        success, error = service.delete_user(1)
        
        assert success is False
        assert "Error deleting user" in error


class TestAuthServiceHelperMethods:
    """Test private helper methods."""
    
    def test_validate_user_uniqueness_username_exists(self, service, mocker):
        """Test uniqueness validation when username exists."""
        mocker.patch.object(service, 'check_username_exists', return_value=True)
        mocker.patch.object(service, 'check_email_exists', return_value=False)
        
        error = service._validate_user_uniqueness("testuser", "test@example.com")
        
        assert error == "Username already exists"
    
    def test_validate_user_uniqueness_email_exists(self, service, mocker):
        """Test uniqueness validation when email exists."""
        mocker.patch.object(service, 'check_username_exists', return_value=False)
        mocker.patch.object(service, 'check_email_exists', return_value=True)
        
        error = service._validate_user_uniqueness("testuser", "test@example.com")
        
        assert error == "Email already exists"
    
    def test_validate_user_uniqueness_success(self, service, mocker):
        """Test uniqueness validation when both are unique."""
        mocker.patch.object(service, 'check_username_exists', return_value=False)
        mocker.patch.object(service, 'check_email_exists', return_value=False)
        
        error = service._validate_user_uniqueness("testuser", "test@example.com")
        
        assert error is None
    
    def test_validate_and_get_role_id_success(self, service, mocker):
        """Test role ID retrieval for valid role."""
        mocker.patch('app.core.reference_data.ReferenceData.get_role_id', return_value=1)
        
        role_id, error = service._validate_and_get_role_id("user")
        
        assert role_id == 1
        assert error is None
    
    def test_validate_and_get_role_id_invalid_role(self, service, mocker):
        """Test role ID retrieval for invalid role."""
        mocker.patch('app.core.reference_data.ReferenceData.get_role_id', return_value=None)
        
        role_id, error = service._validate_and_get_role_id("invalid_role")
        
        assert role_id is None
        assert "Invalid role" in error
    
    def test_build_user_instance(self, service, mocker):
        """Test building user instance with provided data."""
        mock_user_class = mocker.patch('app.auth.services.auth_service.User')
        
        service._build_user_instance("testuser", "test@example.com", "hashed_password", 
                                     "Test", "User", "1234567890")
        
        mock_user_class.assert_called_once_with(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
            phone="1234567890"
        )
    
    def test_assign_role_with_rollback_success(self, service, mock_user, mocker):
        """Test role assignment without rollback."""
        mocker.patch.object(service.user_repo, 'assign_role', return_value=True)
        
        error = service._assign_role_with_rollback(mock_user, 1, "user")
        
        assert error is None
        service.user_repo.assign_role.assert_called_once_with(1, 1)
    
    def test_assign_role_with_rollback_triggers_rollback(self, service, mock_user, mocker):
        """Test role assignment failure triggers user deletion rollback."""
        mocker.patch.object(service.user_repo, 'assign_role', return_value=False)
        mocker.patch.object(service.user_repo, 'delete', return_value=True)
        
        error = service._assign_role_with_rollback(mock_user, 1, "user")
        
        assert error == "Failed to assign role to user"
        service.user_repo.assign_role.assert_called_once_with(1, 1)
        service.user_repo.delete.assert_called_once_with(1)
