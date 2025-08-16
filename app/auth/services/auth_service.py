"""
Authentication Service Module

This module provides comprehensive user management functionality including:
- User CRUD operations (Create, Read, Update, Delete)
- User authentication and validation
- Data persistence with secure password handling

Used by: Authentication routes for API operations
Dependencies: User models, shared CRUD utilities, security configuration
"""
import logging
from config.logging_config import EXC_INFO_LOG_ERRORS
from app.auth.models import User
from app.shared.utils import (
    save_models_to_json, 
    load_models_from_json, 
    load_single_model_by_field, 
    generate_next_id
)
from app.shared.json_db import USERS_DB_PATH

logger = logging.getLogger(__name__)

class AuthService:
    """Service class for authentication and user management operations."""
    
    def __init__(self, db_path=USERS_DB_PATH):
        self.db_path = db_path
        self.logger = logger

    # ============ USER RETRIEVAL METHODS ============
    
    def get_users(self, user_id=None):
        """
        Unified method to get all users or a specific user by ID.
        
        Args:
            user_id (int, optional): If provided, returns single user. 
            If None, returns all users.
        
        Returns:
            list[User] or User or None: List of users, single user, or None if not found
        """
        if user_id:
            self.logger.debug(f"Reading user with id {user_id} from {self.db_path}")
            return load_single_model_by_field(self.db_path, User, 'id', user_id, deserialize_method='from_dict_with_password')
        self.logger.debug(f"Reading all users from {self.db_path}")
        return load_models_from_json(self.db_path, User, deserialize_method='from_dict_with_password')

    def get_user_by_username(self, username):
        """Get a user by username."""
        users = self.get_users()
        for user in users:
            if user.username == username:
                return user
        return None

    # ============ USER VALIDATION METHODS ============
    
    def check_username_exists(self, username):
        """Check if username already exists."""
        return self.get_user_by_username(username) is not None

    def check_email_exists(self, email):
        """Check if email already exists."""
        users = self.get_users()
        for user in users:
            if user.email == email:
                return True
        return False

    # ============ USER CRUD OPERATIONS ============
    
    def create_user(self, user_instance, password_hash):
        """Create a new user with User instance from schema.
        
        Args:
            user_instance (User): User instance from schema with @post_load
            password_hash (str): Hashed password
            
        Returns:
            tuple: (User, None) on success, (None, error_message) on failure
        """
        try:
            # Load existing users to generate next ID
            existing_users = self.get_users()
            self.logger.debug(f"Preparing to write new user to {self.db_path}")
            
            # Set the proper ID and password hash on the user instance
            user_instance.id = generate_next_id(existing_users)
            user_instance.password_hash = password_hash
            
            # Save user to database
            existing_users.append(user_instance)
            save_models_to_json(existing_users, self.db_path, serialize_method='to_dict_with_password')
            self.logger.debug(f"Wrote new user list to {self.db_path}")
            
            self.logger.info(f"User created successfully: {user_instance.username}")
            return user_instance, None
            
        except Exception as e:
            error_msg = f"Error creating user: {e}"
            self.logger.error(error_msg, exc_info=EXC_INFO_LOG_ERRORS)
            return None, error_msg

    def update_user_password(self, user_id, new_password_hash):
        """Update user password."""
        try:
            user = self.get_users(user_id)
            if not user:
                return None, "User not found"
            
            user.password_hash = new_password_hash
            
            # Use helper method to update single user
            self.logger.debug(f"Preparing to update password for user {user_id} in {self.db_path}")
            success = self._update_single_user_in_collection(user)
            if not success:
                return None, "Failed to save password update"
            
            self.logger.info(f"Password updated for user: {user.username}")
            return user, None
            
        except Exception as e:
            error_msg = f"Error updating password: {e}"
            self.logger.error(error_msg, exc_info=EXC_INFO_LOG_ERRORS)
            return None, error_msg

    def update_user_profile(self, user_id, validated_data):
        """Update user profile (non-password fields)."""
        try:
            user = self.get_users(user_id)
            if not user:
                return None, "User not found"
            
            # Update user fields directly from validated data
            for key, value in validated_data.items():
                if hasattr(user, key) and key != 'password_hash':
                    setattr(user, key, value)
            
            # Use helper method to update single user
            self.logger.debug(f"Preparing to update profile for user {user_id} in {self.db_path}")
            success = self._update_single_user_in_collection(user)
            if not success:
                return None, "Failed to save profile update"
            
            self.logger.info(f"Profile updated for user: {user.username}")
            return user, None
            
        except Exception as e:
            error_msg = f"Error updating profile: {e}"
            self.logger.error(error_msg, exc_info=EXC_INFO_LOG_ERRORS)
            return None, error_msg

    def delete_user(self, user_id):
        """Delete a user account."""
        try:
            user = self.get_users(user_id)
            if not user:
                return False, "User not found"
            
            # Remove user from database
            all_users = self.get_users()
            self.logger.debug(f"Preparing to delete user {user_id} from {self.db_path}")
            all_users = [u for u in all_users if u.id != user_id]
            save_models_to_json(all_users, self.db_path, serialize_method='to_dict_with_password')
            self.logger.debug(f"Wrote updated user list to {self.db_path}")
            
            self.logger.info(f"User deleted: {user.username}")
            return True, None
            
        except Exception as e:
            error_msg = f"Error deleting user: {e}"
            self.logger.error(error_msg, exc_info=EXC_INFO_LOG_ERRORS)
            return False, error_msg

    # ============ PRIVATE INSTANCE METHODS ============
    
    def _update_single_user_in_collection(self, updated_user):
        """Helper method to update a single user in the collection and save to file
        
        Args:
            updated_user (User): The user object with updated data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load all users, update the specific one, and save
            all_users = self.get_users()
            self.logger.debug(f"Preparing to update user {updated_user.id} in {self.db_path}")
            for i, u in enumerate(all_users):
                if u.id == updated_user.id:
                    all_users[i] = updated_user
                    break
            else:
                # User not found in collection
                self.logger.error(f"User {updated_user.id} not found in collection during update")
                return False
            
            save_models_to_json(all_users, self.db_path, serialize_method='to_dict_with_password')
            self.logger.debug(f"Wrote updated user list to {self.db_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating user in collection: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return False


# ============ MODULE-LEVEL UTILITY FUNCTIONS ============
# (Now using shared utilities from app.shared.crud_utils)

def get_user_by_id(user_id):
    """Fetch a user by ID from the shared users DB."""
    return load_single_model_by_field(
        USERS_DB_PATH, User, 'id', user_id, deserialize_method='from_dict_with_password'
    )