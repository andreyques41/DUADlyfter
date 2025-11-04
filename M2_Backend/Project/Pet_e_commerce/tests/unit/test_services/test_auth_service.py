"""
Unit tests for AuthService and UserService modules.

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
from app.auth.services.user_service import UserService
from app.auth.models.user import User


@pytest.fixture
def service():
    """Fixture for UserService instance (used by most tests)."""
    return UserService()


@pytest.fixture
def auth_service():
    """Fixture for AuthService instance (used by auth-specific tests)."""
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


class TestAuthServiceUserCreation:
    """Test user creation methods in AuthService."""
    
    def test_create_user_success(self, auth_service, mock_user, mocker):
        """Test successful user creation with default role."""
        mocker.patch.object(auth_service, '_validate_user_uniqueness', return_value=None)
        mocker.patch.object(auth_service, '_validate_and_get_role_id', return_value=(1, None))
        mocker.patch('app.auth.services.security_service.hash_password', return_value="hashed")
        mocker.patch.object(auth_service.user_repo, 'create', return_value=mock_user)
        mocker.patch.object(auth_service, '_assign_role_with_rollback', return_value=None)
        
        user, error = auth_service.create_user("testuser", "test@example.com", "plain_password")
        
        assert error is None
        assert user == mock_user
    
    def test_create_user_with_admin_role(self, auth_service, mock_admin_user, mocker):
        """Test user creation with admin role."""
        mocker.patch.object(auth_service, '_validate_user_uniqueness', return_value=None)
        mocker.patch.object(auth_service, '_validate_and_get_role_id', return_value=(2, None))
        mocker.patch('app.auth.services.security_service.hash_password', return_value="hashed")
        mocker.patch.object(auth_service.user_repo, 'create', return_value=mock_admin_user)
        mocker.patch.object(auth_service, '_assign_role_with_rollback', return_value=None)
        
        user, error = auth_service.create_user("admin", "admin@example.com", "plain_password", role_name="admin")
        
        assert error is None
        assert user == mock_admin_user
    
    def test_create_user_username_exists(self, auth_service, mocker):
        """Test user creation when username already exists."""
        mocker.patch.object(auth_service, '_validate_user_uniqueness', return_value="Username already exists")
        
        user, error = auth_service.create_user("testuser", "test@example.com", "plain_password")
        
        assert user is None
        assert error == "Username already exists"
    
    def test_create_user_email_exists(self, auth_service, mocker):
        """Test user creation when email already exists."""
        mocker.patch.object(auth_service, '_validate_user_uniqueness', return_value="Email already exists")
        
        user, error = auth_service.create_user("testuser", "test@example.com", "plain_password")
        
        assert user is None
        assert error == "Email already exists"
    
    def test_create_user_invalid_role(self, auth_service, mocker):
        """Test user creation with invalid role."""
        mocker.patch.object(auth_service, '_validate_user_uniqueness', return_value=None)
        mocker.patch.object(auth_service, '_validate_and_get_role_id', return_value=(None, "Invalid role: invalid_role"))
        
        user, error = auth_service.create_user("testuser", "test@example.com", "plain_password", role_name="invalid_role")
        
        assert user is None
        assert "Invalid role" in error
    
    def test_create_user_repository_failure(self, auth_service, mock_user, mocker):
        """Test user creation when repository create fails."""
        mocker.patch.object(auth_service, '_validate_user_uniqueness', return_value=None)
        mocker.patch.object(auth_service, '_validate_and_get_role_id', return_value=(1, None))
        mocker.patch('app.auth.services.security_service.hash_password', return_value="hashed")
        mocker.patch.object(auth_service.user_repo, 'create', return_value=None)
        
        user, error = auth_service.create_user("testuser", "test@example.com", "plain_password")
        
        assert user is None
        assert error == "Failed to create user"
    
    def test_create_user_role_assignment_fails(self, auth_service, mock_user, mocker):
        """Test user creation when role assignment fails (rollback triggered)."""
        mocker.patch.object(auth_service, '_validate_user_uniqueness', return_value=None)
        mocker.patch.object(auth_service, '_validate_and_get_role_id', return_value=(1, None))
        mocker.patch('app.auth.services.security_service.hash_password', return_value="hashed")
        mocker.patch.object(auth_service.user_repo, 'create', return_value=mock_user)
        mocker.patch.object(auth_service, '_assign_role_with_rollback', return_value="Failed to assign role to user")
        
        user, error = auth_service.create_user("testuser", "test@example.com", "plain_password")
        
        assert user is None
        assert error == "Failed to assign role to user"
    
    def test_create_user_handles_exception(self, auth_service, mocker):
        """Test exception handling in create_user."""
        mocker.patch.object(auth_service, '_validate_user_uniqueness', side_effect=Exception("Database error"))
        
        user, error = auth_service.create_user("testuser", "test@example.com", "plain_password")
        
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
    """Test private helper methods of AuthService."""
    
    def test_validate_user_uniqueness_username_exists(self, auth_service, mocker):
        """Test uniqueness validation when username exists."""
        mocker.patch.object(auth_service.user_repo, 'exists_by_username', return_value=True)
        mocker.patch.object(auth_service.user_repo, 'exists_by_email', return_value=False)
        
        error = auth_service._validate_user_uniqueness("testuser", "test@example.com")
        
        assert error == "Username already exists"
    
    def test_validate_user_uniqueness_email_exists(self, auth_service, mocker):
        """Test uniqueness validation when email exists."""
        mocker.patch.object(auth_service.user_repo, 'exists_by_username', return_value=False)
        mocker.patch.object(auth_service.user_repo, 'exists_by_email', return_value=True)
        
        error = auth_service._validate_user_uniqueness("testuser", "test@example.com")
        
        assert error == "Email already exists"
    
    def test_validate_user_uniqueness_success(self, auth_service, mocker):
        """Test uniqueness validation when both are unique."""
        mocker.patch.object(auth_service.user_repo, 'exists_by_username', return_value=False)
        mocker.patch.object(auth_service.user_repo, 'exists_by_email', return_value=False)
        
        error = auth_service._validate_user_uniqueness("testuser", "test@example.com")
        
        assert error is None
    
    def test_validate_and_get_role_id_success(self, auth_service, mocker):
        """Test role ID retrieval for valid role."""
        mocker.patch('app.core.reference_data.ReferenceData.get_role_id', return_value=1)
        
        role_id, error = auth_service._validate_and_get_role_id("user")
        
        assert role_id == 1
        assert error is None
    
    def test_validate_and_get_role_id_invalid_role(self, auth_service, mocker):
        """Test role ID retrieval for invalid role."""
        mocker.patch('app.core.reference_data.ReferenceData.get_role_id', return_value=None)
        
        role_id, error = auth_service._validate_and_get_role_id("invalid_role")
        
        assert role_id is None
        assert "Invalid role" in error
    
    def test_assign_role_with_rollback_success(self, auth_service, mock_user, mocker):
        """Test role assignment without rollback."""
        mocker.patch.object(auth_service.user_repo, 'assign_role', return_value=True)
        
        error = auth_service._assign_role_with_rollback(mock_user, 1, "user")
        
        assert error is None
        auth_service.user_repo.assign_role.assert_called_once_with(1, 1)
    
    def test_assign_role_with_rollback_triggers_rollback(self, auth_service, mock_user, mocker):
        """Test role assignment failure triggers user deletion rollback."""
        mocker.patch.object(auth_service.user_repo, 'assign_role', return_value=False)
        mocker.patch.object(auth_service.user_repo, 'delete', return_value=True)
        
        error = auth_service._assign_role_with_rollback(mock_user, 1, "user")
        
        assert error == "Failed to assign role to user"
        auth_service.user_repo.assign_role.assert_called_once_with(1, 1)
        auth_service.user_repo.delete.assert_called_once_with(1)


# ========== CACHE-AWARE METHODS TESTS ==========
class TestAuthServiceCachedMethods:
    """Test cached retrieval methods that return Dict[str, Any] instead of ORM objects."""
    
    def test_get_user_by_id_cached_returns_dict(self, mocker, service, mock_user):
        """Test get_user_by_id_cached returns dictionary, not ORM object."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=mock_user)
        
        # Mock get_or_set to return a dict (simulating schema serialization)
        def mock_get_or_set(cache_key, fetch_func, schema_class, schema_kwargs=None, ttl=300, many=False):
            # Simulate what the real method does: fetch and serialize
            orm_object = fetch_func()
            # Return a dict representation (simulating schema.dump())
            return {'id': orm_object.id, 'username': orm_object.username, 'email': orm_object.email}
        
        mocker.patch.object(service.cache_helper, 'get_or_set', side_effect=mock_get_or_set)
        
        result = service.get_user_by_id_cached(1, include_sensitive=True)
        
        assert isinstance(result, dict)
        assert result['id'] == 1
        assert result['username'] == "testuser"
    
    def test_get_user_by_id_cached_uses_cache_helper(self, mocker, service):
        """Test that cached method uses CacheHelper."""
        mock_get_or_set = mocker.patch.object(service.cache_helper, 'get_or_set', return_value={'id': 1})
        
        result = service.get_user_by_id_cached(1, include_sensitive=True)
        
        mock_get_or_set.assert_called_once()
        call_kwargs = mock_get_or_set.call_args[1]
        
        assert 'cache_key' in call_kwargs
        assert 'ttl' in call_kwargs
        assert call_kwargs['ttl'] == 600  # 10 minutes for users
    
    def test_get_all_users_cached_returns_list_of_dicts(self, mocker, service, mock_user):
        """Test get_all_users_cached returns list of dicts."""
        mock_user2 = Mock(id=2, username="user2", email="user2@test.com")
        
        mocker.patch.object(service.user_repo, 'get_all', return_value=[mock_user, mock_user2])
        
        # Mock get_or_set to return list of dicts (simulating schema serialization with many=True)
        def mock_get_or_set(cache_key, fetch_func, schema_class, schema_kwargs=None, ttl=300, many=False):
            orm_objects = fetch_func()
            # Return list of dict representations (simulating schema.dump(many=True))
            return [{'id': obj.id, 'username': obj.username, 'email': obj.email} for obj in orm_objects]
        
        mocker.patch.object(service.cache_helper, 'get_or_set', side_effect=mock_get_or_set)
        
        result = service.get_all_users_cached(include_sensitive=True)
        
        assert isinstance(result, list)
        assert all(isinstance(user, dict) for user in result)
        assert len(result) == 2
    
    def test_get_user_by_id_cached_include_sensitive_vs_public(self, mocker, service, mock_user):
        """Test include_sensitive=True includes sensitive data vs public schema."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=mock_user)
        
        # Mock get_or_set to return dict
        def mock_get_or_set(cache_key, fetch_func, schema_class, schema_kwargs=None, ttl=300, many=False):
            orm_object = fetch_func()
            return {'id': orm_object.id, 'username': orm_object.username}
        
        mocker.patch.object(service.cache_helper, 'get_or_set', side_effect=mock_get_or_set)
        
        result_sensitive = service.get_user_by_id_cached(1, include_sensitive=True)
        result_public = service.get_user_by_id_cached(1, include_sensitive=False)
        
        assert isinstance(result_sensitive, dict)
        assert isinstance(result_public, dict)
    
    def test_get_user_by_id_cached_cache_miss_fetches_from_db(self, mocker, service, mock_user):
        """Test cache miss triggers database fetch."""
        mocker.patch.object(service.user_repo, 'get_by_id', return_value=mock_user)
        
        # Mock get_or_set to return dict and verify it calls fetch_func
        def mock_get_or_set(cache_key, fetch_func, schema_class, schema_kwargs=None, ttl=300, many=False):
            orm_object = fetch_func()
            return {'id': orm_object.id, 'username': orm_object.username}
        
        mocker.patch.object(service.cache_helper, 'get_or_set', side_effect=mock_get_or_set)
        
        result = service.get_user_by_id_cached(1, include_sensitive=True)
        
        service.user_repo.get_by_id.assert_called_once_with(1)
        assert isinstance(result, dict)


class TestAuthServiceCacheInvalidation:
    """Test @cache_invalidate decorator on mutation methods."""
    
    def test_create_user_has_cache_invalidate_decorator(self, auth_service):
        """Test that create_user has @cache_invalidate decorator."""
        assert hasattr(auth_service.create_user, '__name__')
    
    def test_update_user_profile_has_cache_invalidate_decorator(self, service):
        """Test that update_user_profile has @cache_invalidate decorator."""
        assert hasattr(service.update_user_profile, '__name__')
    
    def test_update_user_password_has_cache_invalidate_decorator(self, service):
        """Test that update_user_password has @cache_invalidate decorator."""
        assert hasattr(service.update_user_password, '__name__')
    
    def test_delete_user_has_cache_invalidate_decorator(self, service):
        """Test that delete_user has @cache_invalidate decorator."""
        assert hasattr(service.delete_user, '__name__')
    
    def test_assign_role_to_user_has_cache_invalidate_decorator(self, service):
        """Test that assign_role_to_user has @cache_invalidate decorator."""
        assert hasattr(service.assign_role_to_user, '__name__')
    
    def test_remove_role_from_user_has_cache_invalidate_decorator(self, service):
        """Test that remove_role_from_user has @cache_invalidate decorator."""
        assert hasattr(service.remove_role_from_user, '__name__')
