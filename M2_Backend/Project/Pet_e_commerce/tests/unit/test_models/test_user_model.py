"""
User Model Tests
~~~~~~~~~~~~~~~

Test User and Role models validation, relationships, and methods.

Target coverage: 95%+
"""
import pytest
from faker import Faker
from app.auth.models import User, Role, RoleUser
from app.auth.services.security_service import hash_password, verify_password

fake = Faker()


@pytest.mark.unit
@pytest.mark.auth
class TestUserModel:
    """Test User model."""
    
    def test_user_creation_with_valid_data(self, db_session, test_role_user):
        """Test creating user with valid data."""
        # Arrange
        user = User(
            username='newuser',
            email='newuser@example.com',
            password_hash=hash_password('password123')
        )
        
        # Act
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Assert
        assert user.id is not None
        assert user.username == 'newuser'
        assert user.email == 'newuser@example.com'
        assert user.password_hash != 'password123'  # Should be hashed
    
    def test_user_password_is_hashed(self):
        """Test that password is properly hashed."""
        # Arrange
        plain_password = 'SecurePass123!'
        
        # Act
        hashed = hash_password(plain_password)
        
        # Assert
        assert hashed != plain_password
        assert len(hashed) > 50  # Bcrypt produces long hashes
        assert hashed.startswith('$2b$')  # Bcrypt prefix
        assert verify_password(plain_password, hashed)
    
    def test_user_password_verification_success(self):
        """Test password verification with correct password."""
        # Arrange
        password = 'TestPass123'
        hashed = hash_password(password)
        
        # Act & Assert
        assert verify_password(password, hashed) is True
    
    def test_user_password_verification_failure(self):
        """Test password verification with wrong password."""
        # Arrange
        password = 'TestPass123'
        wrong_password = 'WrongPass456'
        hashed = hash_password(password)
        
        # Act & Assert
        assert verify_password(wrong_password, hashed) is False
    
    def test_user_email_is_unique(self, db_session, test_user):
        """Test that email must be unique."""
        # Arrange - test_user already has email
        duplicate_user = User(
            username='different',
            email=test_user.email,  # Duplicate email
            password_hash=hash_password('password')
        )
        
        # Act & Assert
        db_session.add(duplicate_user)
        with pytest.raises(Exception):  # Should raise IntegrityError
            db_session.commit()
    
    def test_user_username_is_unique(self, db_session, test_user):
        """Test that username must be unique."""
        # Arrange
        duplicate_user = User(
            username=test_user.username,  # Duplicate username
            email='different@example.com',
            password_hash=hash_password('password')
        )
        
        # Act & Assert
        db_session.add(duplicate_user)
        with pytest.raises(Exception):  # Should raise IntegrityError
            db_session.commit()
    
    def test_user_repr_returns_formatted_string(self, test_user):
        """Test __repr__ method."""
        # Act
        result = repr(test_user)
        
        # Assert
        assert 'User' in result
        assert str(test_user.id) in result
    
    def test_user_optional_fields_can_be_null(self, db_session, test_role_user):
        """Test that optional fields (first_name, last_name, phone) can be None."""
        # Arrange
        user = User(
            username='minimaluser',
            email='minimal@example.com',
            password_hash=hash_password('password')
            # No first_name, last_name, phone
        )
        
        # Act
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Assert
        assert user.id is not None
        assert user.first_name is None
        assert user.last_name is None
        assert user.phone is None
    
    def test_user_has_role_relationship(self, test_user, test_role_user):
        """Test that user has many-to-many relationship to roles via RoleUser."""
        # Act & Assert
        assert test_user.user_roles is not None
        assert len(test_user.user_roles) > 0
        assert test_user.user_roles[0].role.id == 1
        assert test_user.user_roles[0].role.name == 'user'


@pytest.mark.unit
@pytest.mark.auth
class TestRoleModel:
    """Test Role model."""
    
    def test_role_creation(self, test_role_user):
        """Test role creation via fixture."""
        # Assert - validates fixture role was created properly
        assert test_role_user.id is not None
        assert test_role_user.name == 'user'
        assert test_role_user.description is not None
    
    def test_role_repr_returns_formatted_string(self, test_role_user):
        """Test __repr__ method."""
        # Act
        result = repr(test_role_user)
        
        # Assert
        assert 'Role' in result
        assert str(test_role_user.id) in result
        assert 'user' in result
    
    def test_predefined_roles_exist(self, test_role_user, test_role_admin):
        """Test that predefined roles are available."""
        # Assert
        assert test_role_user.id == 1
        assert test_role_user.name == 'user'
        
        assert test_role_admin.id == 2
        assert test_role_admin.name == 'admin'
