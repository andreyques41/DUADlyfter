"""
Authentication Service Module

Business logic layer for user management and authentication.
Handles validation, password management, and user operations.

Responsibilities:
- User registration with validation
- User profile management
- Password operations (hashing, updates)
- Business logic and validation rules
- Orchestrates repository operations

Dependencies:
- UserRepository: Database operations
- SecurityService: Password hashing/verification

Usage:
    service = AuthService()
    user = service.create_user(username, email, password)
"""
import logging
from typing import Optional, Tuple, List
from app.auth.repositories import UserRepository
from app.auth.models.user import User

logger = logging.getLogger(__name__)

class AuthService:
    """Service class for user management business logic."""
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.logger = logger

    # ============ USER RETRIEVAL METHODS ============
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: User ID to fetch
        
        Returns:
            User object or None if not found
        """
        self.logger.debug(f"Fetching user with id {user_id}")
        return self.user_repo.get_by_id(user_id)
    
    def get_all_users(self) -> List[User]:
        """
        Get all users.
        
        Returns:
            List of all users
        """
        self.logger.debug("Fetching all users")
        return self.user_repo.get_all()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User object or None if not found
        """
        self.logger.debug(f"Fetching user with username {username}")
        return self.user_repo.get_by_username(username)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            email: Email to search for
            
        Returns:
            User object or None if not found
        """
        self.logger.debug(f"Fetching user with email {email}")
        return self.user_repo.get_by_email(email)

    # ============ USER VALIDATION METHODS ============
    
    def check_username_exists(self, username: str) -> bool:
        """Check if username already exists."""
        return self.user_repo.exists_by_username(username)

    def check_email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        return self.user_repo.exists_by_email(email)

    # ============ USER CRUD OPERATIONS ============
    
    def create_user(self, username: str, email: str, password_hash: str, 
                   first_name: Optional[str] = None, last_name: Optional[str] = None,
                   phone: Optional[str] = None) -> Tuple[Optional[User], Optional[str]]:
        """
        Create a new user with validation.
        
        Args:
            username: Username for the new user
            email: Email for the new user
            password_hash: Pre-hashed password
            first_name: Optional first name
            last_name: Optional last name
            phone: Optional phone number
            
        Returns:
            Tuple of (User, None) on success, (None, error_message) on failure
        """
        try:
            # Business validation
            if self.check_username_exists(username):
                return None, "Username already exists"
            
            if self.check_email_exists(email):
                return None, "Email already exists"
            
            # Create user instance
            user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                first_name=first_name,
                last_name=last_name,
                phone=phone
            )
            
            # Save to database
            self.logger.debug(f"Creating new user: {username}")
            created_user = self.user_repo.create(user)
            
            if not created_user:
                return None, "Failed to create user"
            
            self.logger.info(f"User created successfully: {username}")
            return created_user, None
            
        except Exception as e:
            error_msg = f"Error creating user: {e}"
            self.logger.error(error_msg)
            return None, error_msg

    def update_user_password(self, user_id: int, new_password_hash: str) -> Tuple[Optional[User], Optional[str]]:
        """
        Update user password.
        
        Args:
            user_id: ID of user to update
            new_password_hash: New hashed password
            
        Returns:
            Tuple of (User, None) on success, (None, error_message) on failure
        """
        try:
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return None, "User not found"
            
            # Update password
            user.password_hash = new_password_hash
            
            # Save to database
            self.logger.debug(f"Updating password for user {user_id}")
            updated_user = self.user_repo.update(user)
            
            if not updated_user:
                return None, "Failed to update password"
            
            self.logger.info(f"Password updated for user: {user.username}")
            return updated_user, None
            
        except Exception as e:
            error_msg = f"Error updating password: {e}"
            self.logger.error(error_msg)
            return None, error_msg

    def update_user_profile(self, user_id: int, **fields) -> Tuple[Optional[User], Optional[str]]:
        """
        Update user profile fields.
        
        Args:
            user_id: ID of user to update
            **fields: Fields to update (username, email, first_name, last_name, phone)
            
        Returns:
            Tuple of (User, None) on success, (None, error_message) on failure
        """
        try:
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return None, "User not found"
            
            # Update allowed fields
            allowed_fields = {'username', 'email', 'first_name', 'last_name', 'phone'}
            for key, value in fields.items():
                if key in allowed_fields and hasattr(user, key):
                    setattr(user, key, value)
            
            # Save to database
            self.logger.debug(f"Updating profile for user {user_id}")
            updated_user = self.user_repo.update(user)
            
            if not updated_user:
                return None, "Failed to update profile"
            
            self.logger.info(f"Profile updated for user: {user.username}")
            return updated_user, None
            
        except Exception as e:
            error_msg = f"Error updating profile: {e}"
            self.logger.error(error_msg)
            return None, error_msg

    def delete_user(self, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Delete a user account.
        
        Args:
            user_id: ID of user to delete
            
        Returns:
            Tuple of (True, None) on success, (False, error_message) on failure
        """
        try:
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return False, "User not found"
            
            username = user.username
            
            # Delete from database
            self.logger.debug(f"Deleting user {user_id}")
            success = self.user_repo.delete(user_id)
            
            if not success:
                return False, "Failed to delete user"
            
            self.logger.info(f"User deleted: {username}")
            return True, None
            
        except Exception as e:
            error_msg = f"Error deleting user: {e}"
            self.logger.error(error_msg)
            return False, error_msg