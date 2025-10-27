"""
Unit tests for authentication library (app.core.lib.auth).

Tests user role checking and authorization functions.
"""
import pytest
from unittest.mock import Mock, MagicMock
from app.core.lib.auth import user_has_role


class TestUserHasRole:
    """Test user_has_role function."""
    
    def test_user_has_single_role(self):
        """Should return True when user has the requested role."""
        # Arrange
        mock_role = Mock()
        mock_role.name = 'admin'
        
        mock_user_role = Mock()
        mock_user_role.role = mock_role
        
        mock_user = Mock()
        mock_user.user_roles = [mock_user_role]
        
        # Act
        result = user_has_role(mock_user, 'admin')
        
        # Assert
        assert result is True
    
    def test_user_has_multiple_roles(self):
        """Should find role among multiple user roles."""
        # Arrange
        mock_admin_role = Mock()
        mock_admin_role.name = 'admin'
        mock_user_role = Mock()
        mock_user_role.name = 'user'
        
        mock_ur1 = Mock()
        mock_ur1.role = mock_user_role
        mock_ur2 = Mock()
        mock_ur2.role = mock_admin_role
        
        mock_user = Mock()
        mock_user.user_roles = [mock_ur1, mock_ur2]
        
        # Act
        result = user_has_role(mock_user, 'admin')
        
        # Assert
        assert result is True
    
    def test_user_does_not_have_role(self):
        """Should return False when user doesn't have role."""
        # Arrange
        mock_role = Mock()
        mock_role.name = 'user'
        
        mock_user_role = Mock()
        mock_user_role.role = mock_role
        
        mock_user = Mock()
        mock_user.user_roles = [mock_user_role]
        
        # Act
        result = user_has_role(mock_user, 'admin')
        
        # Assert
        assert result is False
    
    def test_user_with_no_roles(self):
        """Should return False when user has no roles assigned."""
        # Arrange
        mock_user = Mock()
        mock_user.user_roles = []
        
        # Act
        result = user_has_role(mock_user, 'admin')
        
        # Assert
        assert result is False
    
    def test_case_sensitive_role_check(self):
        """Should perform case-sensitive role matching."""
        # Arrange
        mock_role = Mock()
        mock_role.name = 'Admin'  # Capital A
        
        mock_user_role = Mock()
        mock_user_role.role = mock_role
        
        mock_user = Mock()
        mock_user.user_roles = [mock_user_role]
        
        # Act
        result_lower = user_has_role(mock_user, 'admin')
        result_capital = user_has_role(mock_user, 'Admin')
        
        # Assert
        assert result_lower is False  # Case sensitive
        assert result_capital is True
    
    def test_user_role_with_special_characters(self):
        """Should handle role names with special characters."""
        # Arrange
        mock_role = Mock()
        mock_role.name = 'super-admin_2024'
        
        mock_user_role = Mock()
        mock_user_role.role = mock_role
        
        mock_user = Mock()
        mock_user.user_roles = [mock_user_role]
        
        # Act
        result = user_has_role(mock_user, 'super-admin_2024')
        
        # Assert
        assert result is True
    
    def test_multiple_same_role(self):
        """Should handle edge case of duplicate role assignments."""
        # Arrange
        mock_role1 = Mock()
        mock_role1.name = 'admin'
        mock_role2 = Mock()
        mock_role2.name = 'admin'
        
        mock_ur1 = Mock()
        mock_ur1.role = mock_role1
        mock_ur2 = Mock()
        mock_ur2.role = mock_role2
        
        mock_user = Mock()
        mock_user.user_roles = [mock_ur1, mock_ur2]
        
        # Act
        result = user_has_role(mock_user, 'admin')
        
        # Assert
        assert result is True
    
    def test_none_user(self):
        """Should handle None user gracefully."""
        # Arrange
        mock_user = None
        
        # Act
        result = user_has_role(mock_user, 'admin')
        
        # Assert - Returns False for None user (defensive check in implementation)
        assert result is False
    
    def test_common_roles(self):
        """Should work with common role names."""
        # Arrange roles
        roles = ['admin', 'user', 'moderator', 'guest', 'premium']
        
        for role_name in roles:
            mock_role = Mock()
            mock_role.name = role_name
            mock_user_role = Mock()
            mock_user_role.role = mock_role
            mock_user = Mock()
            mock_user.user_roles = [mock_user_role]
            
            # Act
            result = user_has_role(mock_user, role_name)
            
            # Assert
            assert result is True, f"Failed for role: {role_name}"
