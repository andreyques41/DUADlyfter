"""
Tests for UserRepository to improve coverage.

Focuses on error handling paths that are currently uncovered.
"""

import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from app.auth.repositories.user_repository import UserRepository
from app.auth.models import User, UserRole


class TestUserRepositoryErrorHandling:
    """Tests for UserRepository error handling paths."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return MagicMock()
    
    @pytest.fixture
    def repository(self, mock_db_session):
        """Create UserRepository with mock session."""
        return UserRepository(mock_db_session)
    
    def test_get_by_id_handles_sqlalchemy_error(self, repository, mock_db_session):
        """Test that get_by_id handles SQLAlchemy errors gracefully."""
        # Configure mock to raise SQLAlchemyError
        mock_db_session.query.return_value.filter.return_value.first.side_effect = SQLAlchemyError("DB error")
        
        result = repository.get_by_id(1)
        
        assert result is None
        mock_db_session.query.assert_called_once_with(User)
    
    def test_get_by_username_handles_sqlalchemy_error(self, repository, mock_db_session):
        """Test that get_by_username handles SQLAlchemy errors gracefully."""
        mock_db_session.query.return_value.filter.return_value.first.side_effect = SQLAlchemyError("DB error")
        
        result = repository.get_by_username("testuser")
        
        assert result is None
    
    def test_get_by_email_handles_sqlalchemy_error(self, repository, mock_db_session):
        """Test that get_by_email handles SQLAlchemy errors gracefully."""
        mock_db_session.query.return_value.filter.return_value.first.side_effect = SQLAlchemyError("DB error")
        
        result = repository.get_by_email("test@example.com")
        
        assert result is None
    
    def test_create_user_handles_sqlalchemy_error(self, repository, mock_db_session):
        """Test that create handles SQLAlchemy errors and rolls back."""
        mock_db_session.commit.side_effect = SQLAlchemyError("DB error")
        
        result = repository.create(
            username="newuser",
            email="new@example.com",
            password_hash="hashed_password",
            role=UserRole.CHEF
        )
        
        assert result is None
        mock_db_session.rollback.assert_called_once()
    
    def test_update_user_handles_sqlalchemy_error(self, repository, mock_db_session):
        """Test that update handles SQLAlchemy errors and rolls back."""
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.username = "testuser"
        
        mock_db_session.commit.side_effect = SQLAlchemyError("DB error")
        
        result = repository.update(mock_user)
        
        assert result is False
        mock_db_session.rollback.assert_called_once()
    
    def test_delete_user_not_found(self, repository, mock_db_session):
        """Test delete returns False when user not found."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        result = repository.delete(999)
        
        assert result is False
        mock_db_session.commit.assert_not_called()
    
    def test_delete_user_handles_sqlalchemy_error(self, repository, mock_db_session):
        """Test that delete handles SQLAlchemy errors and rolls back."""
        mock_user = MagicMock(spec=User)
        mock_user.username = "testuser"
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        mock_db_session.commit.side_effect = SQLAlchemyError("DB error")
        
        result = repository.delete(1)
        
        assert result is False
        mock_db_session.rollback.assert_called_once()
    
    def test_get_all_active_handles_sqlalchemy_error(self, repository, mock_db_session):
        """Test that get_all_active handles SQLAlchemy errors gracefully."""
        mock_db_session.query.return_value.filter.return_value.all.side_effect = SQLAlchemyError("DB error")
        
        result = repository.get_all_active()
        
        assert result == []
    
    def test_count_all_handles_sqlalchemy_error(self, repository, mock_db_session):
        """Test that count_all handles SQLAlchemy errors gracefully."""
        mock_db_session.query.return_value.count.side_effect = SQLAlchemyError("DB error")
        
        result = repository.count_all()
        
        assert result == 0


class TestUserRepositorySuccessPaths:
    """Tests for UserRepository success paths to verify logging."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return MagicMock()
    
    @pytest.fixture
    def repository(self, mock_db_session):
        """Create UserRepository with mock session."""
        return UserRepository(mock_db_session)
    
    def test_create_user_success_logs_info(self, repository, mock_db_session):
        """Test that successful user creation logs info message."""
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.username = "newuser"
        
        # Configure mock to return user after refresh
        mock_db_session.refresh.return_value = None
        
        with patch('app.auth.repositories.user_repository.User', return_value=mock_user):
            with patch('app.auth.repositories.user_repository.logger') as mock_logger:
                result = repository.create(
                    username="newuser",
                    email="new@example.com",
                    password_hash="hashed",
                    role=UserRole.CHEF
                )
                
                assert result == mock_user
                mock_logger.info.assert_called()
    
    def test_update_user_success_logs_info(self, repository, mock_db_session):
        """Test that successful user update logs info message."""
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.username = "testuser"
        
        with patch('app.auth.repositories.user_repository.logger') as mock_logger:
            result = repository.update(mock_user)
            
            assert result is True
            mock_logger.info.assert_called()
    
    def test_delete_user_success_logs_info(self, repository, mock_db_session):
        """Test that successful user deletion (soft delete) logs info message."""
        mock_user = MagicMock(spec=User)
        mock_user.username = "testuser"
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        with patch('app.auth.repositories.user_repository.logger') as mock_logger:
            result = repository.delete(1)
            
            assert result is True
            assert mock_user.is_active == 0
            mock_logger.info.assert_called()
    
    def test_get_by_id_success(self, repository, mock_db_session):
        """Test successful user retrieval by ID."""
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = repository.get_by_id(1)
        
        assert result == mock_user
    
    def test_get_by_username_success(self, repository, mock_db_session):
        """Test successful user retrieval by username."""
        mock_user = MagicMock(spec=User)
        mock_user.username = "testuser"
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = repository.get_by_username("testuser")
        
        assert result == mock_user
    
    def test_get_by_email_success(self, repository, mock_db_session):
        """Test successful user retrieval by email."""
        mock_user = MagicMock(spec=User)
        mock_user.email = "test@example.com"
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = repository.get_by_email("test@example.com")
        
        assert result == mock_user
    
    def test_get_all_active_success(self, repository, mock_db_session):
        """Test successful retrieval of all active users."""
        mock_users = [MagicMock(spec=User) for _ in range(3)]
        mock_db_session.query.return_value.filter.return_value.all.return_value = mock_users
        
        result = repository.get_all_active()
        
        assert result == mock_users
        assert len(result) == 3
    
    def test_count_all_success(self, repository, mock_db_session):
        """Test successful user count."""
        mock_db_session.query.return_value.count.return_value = 42
        
        result = repository.count_all()
        
        assert result == 42
