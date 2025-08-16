"""
User Utilities Module

Provides lightweight user data access functions for use in decorators and
other modules that need user data without creating circular dependencies.

Functions are designed to be used by authentication decorators and other
utilities that need to fetch user data without depending on service classes.
"""
from app.shared.utils.crud_utils import load_single_model_by_field
from app.shared.json_db import USERS_DB_PATH
from app.auth.models import User

def get_user_by_id(user_id):
    """
    Fetch a user by ID from the users database.
    
    This function is designed for use in decorators and utilities that need
    to fetch user data without creating circular dependencies with service classes.
    
    Args:
        user_id (int): The ID of the user to fetch
        
    Returns:
        User or None: User object if found, None otherwise
    """
    return load_single_model_by_field(
        USERS_DB_PATH, 
        User, 
        'id', 
        user_id, 
        deserialize_method='from_dict_with_password'
    )

def get_user_by_username(username):
    """
    Fetch a user by username from the users database.
    
    Args:
        username (str): The username to search for
        
    Returns:
        User or None: User object if found, None otherwise
    """
    return load_single_model_by_field(
        USERS_DB_PATH, 
        User, 
        'username', 
        username, 
        deserialize_method='from_dict_with_password'
    )
