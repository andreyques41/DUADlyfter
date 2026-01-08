"""
Unit tests for User Schemas.
Tests Marshmallow schema validation, serialization, and deserialization.
"""
import pytest
from marshmallow import ValidationError
from app.auth.schemas.user_schema import (
    UserRegistrationSchema,
    UserLoginSchema,
    UserUpdateSchema,
    UserResponseSchema,
    UserPasswordChangeSchema,
    RoleAssignmentSchema
)
from app.auth.models.user import User


@pytest.mark.unit
@pytest.mark.auth
class TestUserRegistrationSchema:
    """Test suite for UserRegistrationSchema."""

    def test_valid_registration_data(self):
        """Test schema accepts valid registration data."""
        schema = UserRegistrationSchema()
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        result = schema.load(data)
        
        assert isinstance(result, User)
        assert result.username == 'testuser'
        assert result.email == 'test@example.com'
        assert result.first_name == 'Test'
        assert result.last_name == 'User'
        # password_hash should be empty (set later by service)
        assert result.password_hash == ""

    def test_username_too_short(self):
        """Test schema rejects username shorter than 3 characters."""
        schema = UserRegistrationSchema()
        data = {
            'username': 'ab',  # Too short
            'email': 'test@example.com',
            'password': 'SecurePass123'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'username' in exc_info.value.messages

    def test_invalid_email_format(self):
        """Test schema rejects invalid email format."""
        schema = UserRegistrationSchema()
        data = {
            'username': 'testuser',
            'email': 'notanemail',  # Invalid format
            'password': 'SecurePass123'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'email' in exc_info.value.messages

    def test_password_too_short(self):
        """Test schema rejects password shorter than 8 characters."""
        schema = UserRegistrationSchema()
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Short1'  # Too short
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'password' in exc_info.value.messages

    def test_required_fields_missing(self):
        """Test schema rejects data with missing required fields."""
        schema = UserRegistrationSchema()
        data = {
            'username': 'testuser'
            # Missing email and password
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        errors = exc_info.value.messages
        assert 'email' in errors
        assert 'password' in errors

    def test_optional_fields_can_be_omitted(self):
        """Test schema accepts data without optional fields."""
        schema = UserRegistrationSchema()
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePass123'
            # Omitting first_name, last_name, phone
        }
        
        result = schema.load(data)
        
        assert isinstance(result, User)
        assert result.username == 'testuser'
        assert result.first_name is None
        assert result.last_name is None

    def test_role_defaults_to_user_when_not_provided(self):
        """Test that role defaults to 'user' when not provided."""
        schema = UserRegistrationSchema()
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePass123'
        }
        
        result = schema.load(data)
        
        # Role should be attached as _role_name
        assert hasattr(result, '_role_name')
        assert result._role_name == 'user'


@pytest.mark.unit
@pytest.mark.auth
class TestUserLoginSchema:
    """Test suite for UserLoginSchema."""

    def test_valid_login_data(self):
        """Test schema accepts valid login credentials."""
        schema = UserLoginSchema()
        data = {
            'username': 'testuser',
            'password': 'SecurePass123'
        }
        
        result = schema.load(data)
        
        assert result['username'] == 'testuser'
        assert result['password'] == 'SecurePass123'

    def test_missing_username(self):
        """Test schema rejects login without username."""
        schema = UserLoginSchema()
        data = {
            'password': 'SecurePass123'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'username' in exc_info.value.messages

    def test_missing_password(self):
        """Test schema rejects login without password."""
        schema = UserLoginSchema()
        data = {
            'username': 'testuser'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'password' in exc_info.value.messages


@pytest.mark.unit
@pytest.mark.auth
class TestUserUpdateSchema:
    """Test suite for UserUpdateSchema."""

    def test_valid_update_data(self):
        """Test schema accepts valid update data."""
        schema = UserUpdateSchema()
        data = {
            'username': 'newusername',
            'email': 'newemail@example.com',
            'first_name': 'NewFirst',
            'last_name': 'NewLast'
        }
        
        result = schema.load(data)
        
        assert result['username'] == 'newusername'
        assert result['email'] == 'newemail@example.com'
        assert result['first_name'] == 'NewFirst'
        assert result['last_name'] == 'NewLast'

    def test_partial_update(self):
        """Test schema accepts partial update (not all fields required)."""
        schema = UserUpdateSchema()
        data = {
            'first_name': 'UpdatedFirst'
        }
        
        result = schema.load(data)
        
        assert result['first_name'] == 'UpdatedFirst'
        assert 'username' not in result
        assert 'email' not in result

    def test_invalid_email_in_update(self):
        """Test schema rejects invalid email in update."""
        schema = UserUpdateSchema()
        data = {
            'email': 'notanemail'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'email' in exc_info.value.messages


@pytest.mark.unit
@pytest.mark.auth
class TestUserResponseSchema:
    """Test suite for UserResponseSchema."""

    def test_serialization_excludes_password(self, test_user):
        """Test that password is not included in serialized response."""
        schema = UserResponseSchema()
        
        result = schema.dump(test_user)
        
        assert 'password' not in result
        assert 'password_hash' not in result
        assert result['username'] == test_user.username
        assert result['email'] == test_user.email

    def test_serialization_includes_all_fields(self, test_user):
        """Test that all expected fields are in serialized response."""
        schema = UserResponseSchema()
        
        result = schema.dump(test_user)
        
        assert 'id' in result
        assert 'username' in result
        assert 'email' in result
        assert 'roles' in result
        assert 'first_name' in result
        assert 'last_name' in result

    def test_roles_field_returns_list(self, test_user):
        """Test that roles field returns a list."""
        schema = UserResponseSchema()
        
        result = schema.dump(test_user)
        
        assert isinstance(result['roles'], list)


@pytest.mark.unit
@pytest.mark.auth
class TestUserPasswordChangeSchema:
    """Test suite for UserPasswordChangeSchema."""

    def test_valid_password_change(self):
        """Test schema accepts valid password change data."""
        schema = UserPasswordChangeSchema()
        data = {
            'current_password': 'OldPass123',
            'new_password': 'NewPass456',
            'confirm_password': 'NewPass456'
        }
        
        result = schema.load(data)
        
        assert result['current_password'] == 'OldPass123'
        assert result['new_password'] == 'NewPass456'
        assert result['confirm_password'] == 'NewPass456'

    def test_password_mismatch(self):
        """Test schema rejects when new password and confirm don't match."""
        schema = UserPasswordChangeSchema()
        data = {
            'current_password': 'OldPass123',
            'new_password': 'NewPass456',
            'confirm_password': 'DifferentPass789'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'confirm_password' in exc_info.value.messages

    def test_new_password_same_as_current(self):
        """Test schema rejects when new password is same as current."""
        schema = UserPasswordChangeSchema()
        data = {
            'current_password': 'SamePass123',
            'new_password': 'SamePass123',
            'confirm_password': 'SamePass123'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'new_password' in exc_info.value.messages

    def test_new_password_too_short(self):
        """Test schema rejects new password shorter than 8 characters."""
        schema = UserPasswordChangeSchema()
        data = {
            'current_password': 'OldPass123',
            'new_password': 'Short1',
            'confirm_password': 'Short1'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'new_password' in exc_info.value.messages


@pytest.mark.unit
@pytest.mark.auth
class TestRoleAssignmentSchema:
    """Test suite for RoleAssignmentSchema."""

    def test_valid_role_assignment(self, mocker):
        """Test schema accepts valid role."""
        # Mock ReferenceData.is_valid_role to return True
        mocker.patch('app.auth.schemas.user_schema.ReferenceData.is_valid_role', return_value=True)
        
        schema = RoleAssignmentSchema()
        data = {
            'role': 'admin'
        }
        
        result = schema.load(data)
        
        assert result['role'] == 'admin'

    def test_invalid_role(self, mocker):
        """Test schema rejects invalid role."""
        # Mock ReferenceData.is_valid_role to return False
        mocker.patch('app.auth.schemas.user_schema.ReferenceData.is_valid_role', return_value=False)
        
        schema = RoleAssignmentSchema()
        data = {
            'role': 'invalidrole'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'role' in exc_info.value.messages

    def test_missing_role(self):
        """Test schema rejects when role is missing."""
        schema = RoleAssignmentSchema()
        data = {}
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'role' in exc_info.value.messages
