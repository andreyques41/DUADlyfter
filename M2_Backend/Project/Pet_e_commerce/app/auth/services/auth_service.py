"""
Authentication Service Module

Business logic layer for authentication operations only.
Handles user registration and login validation.

Responsibilities:
- User registration with validation
- User lookup for authentication
- Username/email uniqueness checks
- Initial role assignment during registration
- Orchestrates repository operations for auth

Dependencies:
- UserRepository: Database operations
- ReferenceData: Role ID lookups

Usage:
    service = AuthService()
    user, error = service.create_user(username, email, password)
    user = service.get_user_by_username(username)
"""
import logging
from typing import Optional, Tuple
from app.auth.repositories import UserRepository
from app.auth.models.user import User

logger = logging.getLogger(__name__)


class AuthService:
    """Service class for authentication business logic."""
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.logger = logger

    # ============================================
    # PUBLIC METHODS - USER RETRIEVAL FOR AUTH
    # ============================================
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username for authentication.
        Used during login - not cached for security.
        
        Args:
            username: Username to search for
            
        Returns:
            User object or None if not found
        """
        self.logger.debug(f"Fetching user with username {username}")
        return self.user_repo.get_by_username(username)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email for registration validation.
        Used during registration - not cached.
        
        Args:
            email: Email to search for
            
        Returns:
            User object or None if not found
        """
        self.logger.debug(f"Fetching user with email {email}")
        return self.user_repo.get_by_email(email)

    # ============================================
    # PUBLIC METHODS - USER REGISTRATION
    # ============================================
    
    def create_user(self, username: str, email: str, password: str, 
                   first_name: Optional[str] = None, last_name: Optional[str] = None,
                   phone: Optional[str] = None, role_name: str = "user") -> Tuple[Optional[User], Optional[str]]:
        """
        Create a new user with validation and role assignment.
        
        Args:
            username: Username for the new user
            email: Email for the new user
            password: Plain text password (will be hashed)
            first_name: Optional first name
            last_name: Optional last name
            phone: Optional phone number
            role_name: Role name to assign (default: "user")
            
        Returns:
            Tuple of (User, None) on success, (None, error_message) on failure
        """
        from app.auth.services.security_service import hash_password
        
        try:
            # Step 1: Validate uniqueness
            if error := self._validate_user_uniqueness(username, email):
                return None, error
            
            # Step 2: Validate role
            role_id, error = self._validate_and_get_role_id(role_name)
            if error:
                return None, error
            
            # Step 3: Hash password
            password_hash = hash_password(password)
            
            # Step 4: Create user instance
            user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                first_name=first_name,
                last_name=last_name,
                phone=phone
            )
            
            # Step 5: Save to database
            self.logger.debug(f"Creating new user: {username}")
            created_user = self.user_repo.create(user)
            
            if not created_user:
                return None, "Failed to create user"
            
            # Step 6: Assign role with rollback protection
            if error := self._assign_role_with_rollback(created_user, role_id, role_name):
                return None, error
            
            self.logger.info(f"User created successfully: {username} with role: {role_name}")
            return created_user, None
            
        except Exception as e:
            self.logger.error(f"Error creating user: {e}")
            return None, f"Error creating user: {e}"
    
    # ============================================
    # PRIVATE HELPER METHODS
    # ============================================
    
    def _validate_user_uniqueness(self, username: str, email: str) -> Optional[str]:
        """
        Validate that username and email are unique.
        
        Returns:
            Error message if validation fails, None if successful
        """
        if self.user_repo.exists_by_username(username):
            return "Username already exists"
        
        if self.user_repo.exists_by_email(email):
            return "Email already exists"
        
        return None
    
    def _validate_and_get_role_id(self, role_name: str) -> Tuple[Optional[int], Optional[str]]:
        """
        Validate role exists and get its ID.
        
        Returns:
            Tuple of (role_id, None) on success, (None, error_message) on failure
        """
        from app.core.reference_data import ReferenceData
        
        role_id = ReferenceData.get_role_id(role_name)
        if not role_id:
            return None, f"Invalid role: {role_name}"
        
        return role_id, None
    
    def _assign_role_with_rollback(self, user: User, role_id: int, role_name: str) -> Optional[str]:
        """
        Assign role to user. Rollback user creation if assignment fails.
        
        Returns:
            Error message if failed, None if successful
        """
        self.logger.debug(f"Assigning role '{role_name}' (ID: {role_id}) to user {user.username}")
        
        if not self.user_repo.assign_role(user.id, role_id):
            self.logger.error(f"Failed to assign role, rolling back user {user.username}")
            self.user_repo.delete(user.id)
            return "Failed to assign role to user"
        
        return None
