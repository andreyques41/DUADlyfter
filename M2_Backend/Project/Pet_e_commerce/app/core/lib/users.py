"""
User Utilities Module

Provides lightweight user data access functions for use in decorators and
other modules that need user data without creating circular dependencies.

Functions are designed to be used by authentication decorators and other
utilities that need to fetch user data without depending on service classes.

Note: Uses UserRepository directly to avoid circular imports with AuthService
"""
from typing import Optional
from app.auth.repositories import UserRepository
from app.auth.models.user import User

# Module-level repository instance
_user_repo = UserRepository()

def get_user_by_id(user_id: int) -> Optional[User]:
    """
    Fetch a user by ID from the database.
    
    This function is designed for use in decorators and utilities that need
    to fetch user data without creating circular dependencies with service classes.
    
    Args:
        user_id: The ID of the user to fetch
        
    Returns:
        User object if found, None otherwise
    """
    return _user_repo.get_by_id(user_id)

def get_user_by_username(username: str) -> Optional[User]:
    """
    Fetch a user by username from the database.
    
    Args:
        username: The username to search for
        
    Returns:
        User object if found, None otherwise
    """
    return _user_repo.get_by_username(username)
