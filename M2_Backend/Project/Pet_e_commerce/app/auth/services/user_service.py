"""
User Service Module

Business logic layer for user management with caching support.
Handles user CRUD operations, role management, and profile updates.

Responsibilities:
- User retrieval with caching
- User profile management
- Role assignment and removal
- Business logic and validation rules
- Orchestrates repository operations
- Cache management for frequently accessed users

Dependencies:
- UserRepository: Database operations
- CacheHelper: Redis caching for performance
- ReferenceData: Role ID lookups

Usage:
    service = UserService()
    user_data = service.get_user_by_id_cached(1, include_sensitive=True)
    users = service.get_all_users_cached(include_sensitive=True)
"""
import logging
from typing import Optional, Tuple, List
from app.auth.repositories import UserRepository
from app.auth.models.user import User
from app.core.cache_manager import get_cache
from app.core.middleware.cache_decorators import CacheHelper, cache_invalidate

logger = logging.getLogger(__name__)


class UserService:
    """Service class for user management business logic with caching support."""
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.logger = logger
        # Get global cache manager instance (singleton pattern)
        self.cache_manager = get_cache()
        # Initialize cache helper for reusable schema-based caching
        self.cache_helper = CacheHelper(resource_name="user", version="v1")

    # ============================================
    # PUBLIC METHODS - USER RETRIEVAL (WITH CACHING)
    # ============================================
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID (returns ORM object).
        Note: Use get_user_by_id_cached() for cached access in controllers.
        
        Args:
            user_id: User ID to fetch
        
        Returns:
            User object or None if not found
        """
        self.logger.debug(f"Fetching user with id {user_id}")
        return self.user_repo.get_by_id(user_id)
    
    def get_user_by_id_cached(self, user_id: int, include_sensitive: bool = False) -> Optional[dict]:
        """
        Get user by ID with schema-based caching (RECOMMENDED).
        Returns serialized dict ready for JSON response.
        
        Args:
            user_id: User ID to fetch
            include_sensitive: Include sensitive fields (email, phone)
        
        Returns:
            Serialized user dict or None if not found
        """
        from app.auth.schemas import user_response_schema
        
        return self.cache_helper.get_or_set(
            cache_key=f"{user_id}:sensitive={include_sensitive}",
            fetch_func=lambda: self.user_repo.get_by_id(user_id),
            schema_class=type(user_response_schema),  # Use schema class
            schema_kwargs={},  # UserResponseSchema handles sensitive data internally
            ttl=600  # 10 minutes (users change less frequently than products)
        )
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username (returns ORM object).
        Used primarily for authentication - not cached.
        
        Args:
            username: Username to search for
            
        Returns:
            User object or None if not found
        """
        self.logger.debug(f"Fetching user with username {username}")
        return self.user_repo.get_by_username(username)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email (returns ORM object).
        Used primarily for registration validation - not cached.
        
        Args:
            email: Email to search for
            
        Returns:
            User object or None if not found
        """
        self.logger.debug(f"Fetching user with email {email}")
        return self.user_repo.get_by_email(email)
    
    def get_all_users(self) -> List[User]:
        """
        Get all users (returns ORM objects).
        Note: Use get_all_users_cached() for cached access in controllers.
        
        Returns:
            List of all users
        """
        self.logger.debug("Fetching all users")
        return self.user_repo.get_all()
    
    def get_all_users_cached(self, include_sensitive: bool = False) -> List[dict]:
        """
        Get all users with schema-based caching (RECOMMENDED).
        Returns list of serialized dicts ready for JSON response.
        
        Args:
            include_sensitive: Include sensitive fields (email, phone)
        
        Returns:
            List of serialized user dicts
        """
        from app.auth.schemas import users_response_schema
        
        return self.cache_helper.get_or_set(
            cache_key=f"all:sensitive={include_sensitive}",
            fetch_func=lambda: self.user_repo.get_all(),
            schema_class=type(users_response_schema),
            schema_kwargs={},
            ttl=300,  # 5 minutes (shorter for lists)
            many=True
        )

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
    
    @cache_invalidate([
        lambda self, user_id, role_name: f"user:v1:{user_id}:sensitive=True",
        lambda self, user_id, role_name: f"user:v1:{user_id}:sensitive=False",
        lambda self, user_id, role_name: "user:v1:all:sensitive=True",
        lambda self, user_id, role_name: "user:v1:all:sensitive=False",
    ])
    def assign_role_to_user(self, user_id: int, role_name: str) -> Tuple[bool, Optional[str]]:
        """
        Assign a role to a user (if not already assigned).
        Invalidates user caches after successful assignment.
        
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
    
    @cache_invalidate([
        lambda self, user_id, role_name: f"user:v1:{user_id}:sensitive=True",
        lambda self, user_id, role_name: f"user:v1:{user_id}:sensitive=False",
        lambda self, user_id, role_name: "user:v1:all:sensitive=True",
        lambda self, user_id, role_name: "user:v1:all:sensitive=False",
    ])
    def remove_role_from_user(self, user_id: int, role_name: str) -> Tuple[bool, Optional[str]]:
        """
        Remove a role from a user.
        Invalidates user caches after successful removal.
        
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
    # PUBLIC METHODS - USER CRUD OPERATIONS
    # ============================================
    
    @cache_invalidate([
        lambda self, user_id, **kwargs: f"user:v1:{user_id}:sensitive=True",
        lambda self, user_id, **kwargs: f"user:v1:{user_id}:sensitive=False",
        lambda self, **kwargs: "user:v1:all:sensitive=True",
        lambda self, **kwargs: "user:v1:all:sensitive=False",
    ])
    def update_user_profile(self, user_id: int, **fields) -> Tuple[Optional[User], Optional[str]]:
        """
        Update user profile fields.
        Invalidates user caches after successful update.
        
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

    @cache_invalidate([
        lambda self, user_id, new_password_hash: f"user:v1:{user_id}:sensitive=True",
        lambda self, user_id, new_password_hash: f"user:v1:{user_id}:sensitive=False",
    ])
    def update_user_password(self, user_id: int, new_password_hash: str) -> Tuple[Optional[User], Optional[str]]:
        """
        Update user password.
        Invalidates user caches after successful update.
        
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

    @cache_invalidate([
        lambda self, user_id: f"user:v1:{user_id}:sensitive=True",
        lambda self, user_id: f"user:v1:{user_id}:sensitive=False",
        lambda self, user_id: "user:v1:all:sensitive=True",
        lambda self, user_id: "user:v1:all:sensitive=False",
    ])
    def delete_user(self, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Delete a user account.
        Invalidates user caches after successful deletion.
        
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
