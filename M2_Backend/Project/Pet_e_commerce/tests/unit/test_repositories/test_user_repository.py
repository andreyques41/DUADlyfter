"""
Unit tests for UserRepository.

Tests all CRUD operations, query methods, role management, and error handling
for the User repository layer without requiring an actual database.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError
from app.auth.repositories.user_repository import UserRepository
from app.auth.models.user import User, Role, RoleUser


class TestUserRepositoryGetByID:
    """Test get_by_id method."""
    
    @patch('app.auth.repositories.user_repository.get_db')
    def test_get_by_id_success(self, mock_get_db):
        """Should return user with roles loaded when found."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.username = 'testuser'
        
        mock_query = mock_db.query.return_value
        mock_query.options.return_value.filter_by.return_value.first.return_value = mock_user
        
        repo = UserRepository()
        
        # Act
        result = repo.get_by_id(1)
        
        # Assert
        assert result == mock_user
        mock_db.query.assert_called_once_with(User)
        mock_query.options.return_value.filter_by.assert_called_once_with(id=1)
    
    @patch('app.auth.repositories.user_repository.get_db')
    def test_get_by_id_not_found(self, mock_get_db):
        """Should return None when user not found."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_query = mock_db.query.return_value
        mock_query.options.return_value.filter_by.return_value.first.return_value = None
        
        repo = UserRepository()
        
        # Act
        result = repo.get_by_id(999)
        
        # Assert
        assert result is None
    
    @patch('app.auth.repositories.user_repository.get_db')
    @patch('app.auth.repositories.user_repository.logger')
    def test_get_by_id_database_error(self, mock_logger, mock_get_db):
        """Should log error and return None on database error."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.side_effect = SQLAlchemyError("Database error")
        
        repo = UserRepository()
        
        # Act
        result = repo.get_by_id(1)
        
        # Assert
        assert result is None
        mock_logger.error.assert_called_once()
        assert "Error fetching user by id 1" in str(mock_logger.error.call_args)


class TestUserRepositoryGetByUsername:
    """Test get_by_username method."""
    
    @patch('app.auth.repositories.user_repository.get_db')
    def test_get_by_username_success(self, mock_get_db):
        """Should return user when username exists."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_user = Mock(spec=User)
        mock_user.username = 'testuser'
        
        mock_query = mock_db.query.return_value
        mock_query.options.return_value.filter_by.return_value.first.return_value = mock_user
        
        repo = UserRepository()
        
        # Act
        result = repo.get_by_username('testuser')
        
        # Assert
        assert result == mock_user
        mock_query.options.return_value.filter_by.assert_called_once_with(username='testuser')
    
    @patch('app.auth.repositories.user_repository.get_db')
    def test_get_by_username_not_found(self, mock_get_db):
        """Should return None when username doesn't exist."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_query = mock_db.query.return_value
        mock_query.options.return_value.filter_by.return_value.first.return_value = None
        
        repo = UserRepository()
        
        # Act
        result = repo.get_by_username('nonexistent')
        
        # Assert
        assert result is None
    
    @patch('app.auth.repositories.user_repository.get_db')
    @patch('app.auth.repositories.user_repository.logger')
    def test_get_by_username_database_error(self, mock_logger, mock_get_db):
        """Should handle database errors gracefully."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.side_effect = SQLAlchemyError("Connection lost")
        
        repo = UserRepository()
        
        # Act
        result = repo.get_by_username('testuser')
        
        # Assert
        assert result is None
        mock_logger.error.assert_called_once()


class TestUserRepositoryGetByEmail:
    """Test get_by_email method."""
    
    @patch('app.auth.repositories.user_repository.get_db')
    def test_get_by_email_success(self, mock_get_db):
        """Should return user when email exists."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_user = Mock(spec=User)
        mock_user.email = 'test@example.com'
        
        mock_query = mock_db.query.return_value
        mock_query.filter_by.return_value.first.return_value = mock_user
        
        repo = UserRepository()
        
        # Act
        result = repo.get_by_email('test@example.com')
        
        # Assert
        assert result == mock_user
        mock_query.filter_by.assert_called_once_with(email='test@example.com')
    
    @patch('app.auth.repositories.user_repository.get_db')
    def test_get_by_email_not_found(self, mock_get_db):
        """Should return None when email doesn't exist."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_query = mock_db.query.return_value
        mock_query.filter_by.return_value.first.return_value = None
        
        repo = UserRepository()
        
        # Act
        result = repo.get_by_email('nonexistent@example.com')
        
        # Assert
        assert result is None
    
    @patch('app.auth.repositories.user_repository.get_db')
    @patch('app.auth.repositories.user_repository.logger')
    def test_get_by_email_database_error(self, mock_logger, mock_get_db):
        """Should handle database errors gracefully."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.side_effect = SQLAlchemyError("Timeout")
        
        repo = UserRepository()
        
        # Act
        result = repo.get_by_email('test@example.com')
        
        # Assert
        assert result is None
        mock_logger.error.assert_called_once()


class TestUserRepositoryGetAll:
    """Test get_all method."""
    
    @patch('app.auth.repositories.user_repository.get_db')
    def test_get_all_success(self, mock_get_db):
        """Should return all users."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_users = [Mock(spec=User), Mock(spec=User), Mock(spec=User)]
        mock_db.query.return_value.all.return_value = mock_users
        
        repo = UserRepository()
        
        # Act
        result = repo.get_all()
        
        # Assert
        assert result == mock_users
        assert len(result) == 3
    
    @patch('app.auth.repositories.user_repository.get_db')
    def test_get_all_empty(self, mock_get_db):
        """Should return empty list when no users exist."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.all.return_value = []
        
        repo = UserRepository()
        
        # Act
        result = repo.get_all()
        
        # Assert
        assert result == []
    
    @patch('app.auth.repositories.user_repository.get_db')
    @patch('app.auth.repositories.user_repository.logger')
    def test_get_all_database_error(self, mock_logger, mock_get_db):
        """Should return empty list on database error."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.side_effect = SQLAlchemyError("Server error")
        
        repo = UserRepository()
        
        # Act
        result = repo.get_all()
        
        # Assert
        assert result == []
        mock_logger.error.assert_called_once()


class TestUserRepositoryCreate:
    """Test create method."""
    
    @patch('app.auth.repositories.user_repository.get_db')
    def test_create_success(self, mock_get_db):
        """Should create user and return it with ID."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_user = Mock(spec=User)
        mock_user.username = 'newuser'
        
        repo = UserRepository()
        
        # Act
        result = repo.create(mock_user)
        
        # Assert
        assert result == mock_user
        mock_db.add.assert_called_once_with(mock_user)
        mock_db.flush.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_user)
    
    @patch('app.auth.repositories.user_repository.get_db')
    @patch('app.auth.repositories.user_repository.logger')
    def test_create_database_error(self, mock_logger, mock_get_db):
        """Should return None on database error."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.add.side_effect = SQLAlchemyError("Constraint violation")
        
        mock_user = Mock(spec=User)
        mock_user.username = 'duplicate'
        
        repo = UserRepository()
        
        # Act
        result = repo.create(mock_user)
        
        # Assert
        assert result is None
        mock_logger.error.assert_called_once()


class TestUserRepositoryUpdate:
    """Test update method."""
    
    @patch('app.auth.repositories.user_repository.get_db')
    def test_update_success(self, mock_get_db):
        """Should update user and return updated object."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.username = 'updated_user'
        
        mock_db.merge.return_value = mock_user
        
        repo = UserRepository()
        
        # Act
        result = repo.update(mock_user)
        
        # Assert
        assert result == mock_user
        mock_db.merge.assert_called_once_with(mock_user)
        mock_db.flush.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_user)
    
    @patch('app.auth.repositories.user_repository.get_db')
    @patch('app.auth.repositories.user_repository.logger')
    def test_update_database_error(self, mock_logger, mock_get_db):
        """Should return None on database error."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.merge.side_effect = SQLAlchemyError("Update failed")
        
        mock_user = Mock(spec=User)
        mock_user.id = 1
        
        repo = UserRepository()
        
        # Act
        result = repo.update(mock_user)
        
        # Assert
        assert result is None
        mock_logger.error.assert_called_once()


class TestUserRepositoryDelete:
    """Test delete method."""
    
    @patch('app.auth.repositories.user_repository.get_db')
    def test_delete_success(self, mock_get_db):
        """Should delete user and return True."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_user = Mock(spec=User)
        mock_user.id = 1
        
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_user
        
        repo = UserRepository()
        
        # Act
        result = repo.delete(1)
        
        # Assert
        assert result is True
        mock_db.delete.assert_called_once_with(mock_user)
        mock_db.flush.assert_called_once()
    
    @patch('app.auth.repositories.user_repository.get_db')
    def test_delete_not_found(self, mock_get_db):
        """Should return False when user doesn't exist."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        repo = UserRepository()
        
        # Act
        result = repo.delete(999)
        
        # Assert
        assert result is False
        mock_db.delete.assert_not_called()
    
    @patch('app.auth.repositories.user_repository.get_db')
    @patch('app.auth.repositories.user_repository.logger')
    def test_delete_database_error(self, mock_logger, mock_get_db):
        """Should return False on database error."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.side_effect = SQLAlchemyError("Delete failed")
        
        repo = UserRepository()
        
        # Act
        result = repo.delete(1)
        
        # Assert
        assert result is False
        mock_logger.error.assert_called_once()


class TestUserRepositoryExistsMethods:
    """Test exists_by_username and exists_by_email methods."""
    
    @patch('app.auth.repositories.user_repository.UserRepository.get_by_username')
    def test_exists_by_username_true(self, mock_get_by_username):
        """Should return True when username exists."""
        # Arrange
        mock_get_by_username.return_value = Mock(spec=User)
        repo = UserRepository()
        
        # Act
        result = repo.exists_by_username('existing')
        
        # Assert
        assert result is True
    
    @patch('app.auth.repositories.user_repository.UserRepository.get_by_username')
    def test_exists_by_username_false(self, mock_get_by_username):
        """Should return False when username doesn't exist."""
        # Arrange
        mock_get_by_username.return_value = None
        repo = UserRepository()
        
        # Act
        result = repo.exists_by_username('nonexistent')
        
        # Assert
        assert result is False
    
    @patch('app.auth.repositories.user_repository.UserRepository.get_by_email')
    def test_exists_by_email_true(self, mock_get_by_email):
        """Should return True when email exists."""
        # Arrange
        mock_get_by_email.return_value = Mock(spec=User)
        repo = UserRepository()
        
        # Act
        result = repo.exists_by_email('existing@example.com')
        
        # Assert
        assert result is True
    
    @patch('app.auth.repositories.user_repository.UserRepository.get_by_email')
    def test_exists_by_email_false(self, mock_get_by_email):
        """Should return False when email doesn't exist."""
        # Arrange
        mock_get_by_email.return_value = None
        repo = UserRepository()
        
        # Act
        result = repo.exists_by_email('nonexistent@example.com')
        
        # Assert
        assert result is False


class TestUserRepositoryRoleManagement:
    """Test role assignment and removal methods."""
    
    @patch('app.auth.repositories.user_repository.get_db')
    def test_assign_role_success(self, mock_get_db):
        """Should assign role to user successfully."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        repo = UserRepository()
        
        # Act
        result = repo.assign_role(user_id=1, role_id=2)
        
        # Assert
        assert result is True
        mock_db.add.assert_called_once()
        mock_db.flush.assert_called_once()
        
        # Verify RoleUser was created with correct IDs
        role_user_arg = mock_db.add.call_args[0][0]
        assert isinstance(role_user_arg, RoleUser)
    
    @patch('app.auth.repositories.user_repository.get_db')
    @patch('app.auth.repositories.user_repository.logger')
    def test_assign_role_database_error(self, mock_logger, mock_get_db):
        """Should return False on database error."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.add.side_effect = SQLAlchemyError("Role constraint error")
        
        repo = UserRepository()
        
        # Act
        result = repo.assign_role(user_id=1, role_id=2)
        
        # Assert
        assert result is False
        mock_logger.error.assert_called_once()
    
    @patch('app.auth.repositories.user_repository.get_db')
    def test_remove_role_success(self, mock_get_db):
        """Should remove role from user successfully."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_role_user = Mock(spec=RoleUser)
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_role_user
        
        repo = UserRepository()
        
        # Act
        result = repo.remove_role(user_id=1, role_id=2)
        
        # Assert
        assert result is True
        mock_db.delete.assert_called_once_with(mock_role_user)
        mock_db.flush.assert_called_once()
    
    @patch('app.auth.repositories.user_repository.get_db')
    @patch('app.auth.repositories.user_repository.logger')
    def test_remove_role_not_found(self, mock_logger, mock_get_db):
        """Should return False when role assignment doesn't exist."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        repo = UserRepository()
        
        # Act
        result = repo.remove_role(user_id=1, role_id=2)
        
        # Assert
        assert result is False
        mock_logger.warning.assert_called_once()
        mock_db.delete.assert_not_called()
    
    @patch('app.auth.repositories.user_repository.get_db')
    @patch('app.auth.repositories.user_repository.logger')
    def test_remove_role_database_error(self, mock_logger, mock_get_db):
        """Should return False on database error."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.side_effect = SQLAlchemyError("Delete error")
        
        repo = UserRepository()
        
        # Act
        result = repo.remove_role(user_id=1, role_id=2)
        
        # Assert
        assert result is False
        mock_logger.error.assert_called_once()
    
    @patch('app.auth.repositories.user_repository.get_db')
    def test_get_user_roles_success(self, mock_get_db):
        """Should return list of roles for user."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_role1 = Mock(spec=Role)
        mock_role1.name = 'user'
        mock_role2 = Mock(spec=Role)
        mock_role2.name = 'admin'
        
        mock_role_user1 = Mock(spec=RoleUser)
        mock_role_user1.role = mock_role1
        mock_role_user2 = Mock(spec=RoleUser)
        mock_role_user2.role = mock_role2
        
        mock_user = Mock(spec=User)
        mock_user.user_roles = [mock_role_user1, mock_role_user2]
        
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_user
        
        repo = UserRepository()
        
        # Act
        result = repo.get_user_roles(1)
        
        # Assert
        assert len(result) == 2
        assert result[0] == mock_role1
        assert result[1] == mock_role2
    
    @patch('app.auth.repositories.user_repository.get_db')
    def test_get_user_roles_no_roles(self, mock_get_db):
        """Should return empty list when user has no roles."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_user = Mock(spec=User)
        mock_user.user_roles = []
        
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_user
        
        repo = UserRepository()
        
        # Act
        result = repo.get_user_roles(1)
        
        # Assert
        assert result == []
    
    @patch('app.auth.repositories.user_repository.get_db')
    def test_get_user_roles_user_not_found(self, mock_get_db):
        """Should return empty list when user doesn't exist."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        repo = UserRepository()
        
        # Act
        result = repo.get_user_roles(999)
        
        # Assert
        assert result == []
    
    @patch('app.auth.repositories.user_repository.get_db')
    @patch('app.auth.repositories.user_repository.logger')
    def test_get_user_roles_database_error(self, mock_logger, mock_get_db):
        """Should return empty list on database error."""
        # Arrange
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.side_effect = SQLAlchemyError("Query failed")
        
        repo = UserRepository()
        
        # Act
        result = repo.get_user_roles(1)
        
        # Assert
        assert result == []
        mock_logger.error.assert_called_once()
