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

    # ============================================
    # PUBLIC METHODS - USER RETRIEVAL
    # ============================================
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        self.logger.debug(f"Fetching user with id {user_id}")
        return self.user_repo.get_by_id(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        self.logger.debug(f"Fetching user with username {username}")
        return self.user_repo.get_by_username(username)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        self.logger.debug(f"Fetching user with email {email}")
        return self.user_repo.get_by_email(email)
    
    def get_all_users(self) -> List[User]:
        """Get all users."""
        self.logger.debug("Fetching all users")
        return self.user_repo.get_all()

    # ============================================
    # PUBLIC METHODS - ROLE MANAGEMENT
    # ============================================
    
    def get_user_roles(self, user_id: int) -> Tuple[Optional[List[str]], Optional[str]]:
        """
        Get all roles assigned to a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Tuple of (role_names_list, None) on success, (None, error_message) on failure
        """
        try:
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return None, "User not found"
            
            # Get all role names from user_roles relationship
            if hasattr(user, 'user_roles') and user.user_roles:
                role_names = [user_role.role.name for user_role in user.user_roles if user_role.role]
                return role_names if role_names else ["user"], None
            
            return ["user"], None
            
        except Exception as e:
            self.logger.error(f"Error getting user roles: {e}")
            return None, f"Error getting user roles: {e}"
    
    def assign_role_to_user(self, user_id: int, role_name: str) -> Tuple[bool, Optional[str]]:
        """
        Assign a role to a user (if not already assigned).
        
        Args:
            user_id: ID of the user
            role_name: Name of the role to assign
            
        Returns:
            Tuple of (True, None) on success, (False, error_message) on failure
        """
        try:
            # Validate user exists
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return False, "User not found"
            
            # Validate role exists
            role_id, error = self._validate_and_get_role_id(role_name)
            if error:
                return False, error
            
            # Check if user already has this role
            current_roles, error = self.get_user_roles(user_id)
            if error:
                return False, error
            
            if role_name in current_roles:
                return False, f"User already has role '{role_name}'"
            
            # Assign the role
            self.logger.debug(f"Assigning role '{role_name}' to user {user_id}")
            if not self.user_repo.assign_role(user_id, role_id):
                return False, "Failed to assign role"
            
            self.logger.info(f"Role '{role_name}' assigned to user {user_id}")
            return True, None
            
        except Exception as e:
            self.logger.error(f"Error assigning role: {e}")
            return False, f"Error assigning role: {e}"
    
    def remove_role_from_user(self, user_id: int, role_name: str) -> Tuple[bool, Optional[str]]:
        """
        Remove a role from a user.
        
        Args:
            user_id: ID of the user
            role_name: Name of the role to remove
            
        Returns:
            Tuple of (True, None) on success, (False, error_message) on failure
        """
        try:
            # Validate user exists
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return False, "User not found"
            
            # Validate role exists
            role_id, error = self._validate_and_get_role_id(role_name)
            if error:
                return False, error
            
            # Check if user has this role
            current_roles, error = self.get_user_roles(user_id)
            if error:
                return False, error
            
            if role_name not in current_roles:
                return False, f"User does not have role '{role_name}'"
            
            # Prevent removing last role
            if len(current_roles) == 1:
                return False, "Cannot remove the last role from user. Users must have at least one role."
            
            # Remove the role
            self.logger.debug(f"Removing role '{role_name}' from user {user_id}")
            if not self.user_repo.remove_role(user_id, role_id):
                return False, "Failed to remove role"
            
            self.logger.info(f"Role '{role_name}' removed from user {user_id}")
            return True, None
            
        except Exception as e:
            self.logger.error(f"Error removing role: {e}")
            return False, f"Error removing role: {e}"

    # ============================================
    # PUBLIC METHODS - USER VALIDATION
    # ============================================
    
    def check_username_exists(self, username: str) -> bool:
        """Check if username already exists."""
        return self.user_repo.exists_by_username(username)

    def check_email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        return self.user_repo.exists_by_email(email)

    # ============================================
    # PUBLIC METHODS - USER CRUD OPERATIONS
    # ============================================
    
    def create_user(self, username: str, email: str, password_hash: str, 
                   first_name: Optional[str] = None, last_name: Optional[str] = None,
                   phone: Optional[str] = None, role_name: str = "user") -> Tuple[Optional[User], Optional[str]]:
        """
        Create a new user with validation and role assignment.
        
        Args:
            username: Username for the new user
            email: Email for the new user
            password_hash: Pre-hashed password
            first_name: Optional first name
            last_name: Optional last name
            phone: Optional phone number
            role_name: Role name to assign (default: "user")
            
        Returns:
            Tuple of (User, None) on success, (None, error_message) on failure
        """
        try:
            # Step 1: Validate uniqueness
            if error := self._validate_user_uniqueness(username, email):
                return None, error
            
            # Step 2: Validate role
            role_id, error = self._validate_and_get_role_id(role_name)
            if error:
                return None, error
            
            # Step 3: Create user instance
            user = self._build_user_instance(username, email, password_hash, 
                                             first_name, last_name, phone)
            
            # Step 4: Save to database
            self.logger.debug(f"Creating new user: {username}")
            created_user = self.user_repo.create(user)
            
            if not created_user:
                return None, "Failed to create user"
            
            # Step 5: Assign role with rollback protection
            if error := self._assign_role_with_rollback(created_user, role_id, role_name):
                return None, error
            
            self.logger.info(f"User created successfully: {username} with role: {role_name}")
            return created_user, None
            
        except Exception as e:
            self.logger.error(f"Error creating user: {e}")
            return None, f"Error creating user: {e}"

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
            
            self.logger.debug(f"Updating profile for user {user_id}")
            updated_user = self.user_repo.update(user)
            
            if not updated_user:
                return None, "Failed to update profile"
            
            self.logger.info(f"Profile updated for user: {user.username}")
            return updated_user, None
            
        except Exception as e:
            self.logger.error(f"Error updating profile: {e}")
            return None, f"Error updating profile: {e}"

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
            
            user.password_hash = new_password_hash
            
            self.logger.debug(f"Updating password for user {user_id}")
            updated_user = self.user_repo.update(user)
            
            if not updated_user:
                return None, "Failed to update password"
            
            self.logger.info(f"Password updated for user: {user.username}")
            return updated_user, None
            
        except Exception as e:
            self.logger.error(f"Error updating password: {e}")
            return None, f"Error updating password: {e}"

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
            
            self.logger.debug(f"Deleting user {user_id}")
            if not self.user_repo.delete(user_id):
                return False, "Failed to delete user"
            
            self.logger.info(f"User deleted: {username}")
            return True, None
            
        except Exception as e:
            self.logger.error(f"Error deleting user: {e}")
            return False, f"Error deleting user: {e}"
    
    # ============================================
    # PRIVATE HELPER METHODS
    # ============================================
    
    def _validate_user_uniqueness(self, username: str, email: str) -> Optional[str]:
        """
        Validate that username and email are unique.
        
        Returns:
            Error message if validation fails, None if successful
        """
        if self.check_username_exists(username):
            return "Username already exists"
        
        if self.check_email_exists(email):
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
    
    def _build_user_instance(self, username: str, email: str, password_hash: str,
                            first_name: Optional[str], last_name: Optional[str],
                            phone: Optional[str]) -> User:
        """Build a User instance with provided data."""
        return User(
            username=username,
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )
    
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
