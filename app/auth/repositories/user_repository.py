"""
User Repository Module

Handles all database operations for User model using SQLAlchemy ORM.
Provides CRUD operations and query methods for user management.

Responsibilities:
- Database queries and operations (SELECT, INSERT, UPDATE, DELETE)
- User lookups by different fields (id, username, email)
- Transaction management via get_db (session per request)

Usage:
    repo = UserRepository()
    user = repo.get_by_id(1)
    all_users = repo.get_all()
"""
from typing import Optional, List
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import get_db
from app.auth.models.user import User, Role, RoleUser
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for User database operations."""
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            User object or None if not found
        """
        try:
            db = get_db()
            return db.query(User).filter_by(id=user_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching user by id {user_id}: {e}")
            return None
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User object or None if not found
        """
        try:
            db = get_db()
            return db.query(User).filter_by(username=username).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching user by username {username}: {e}")
            return None
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: Email to search for
            
        Returns:
            User object or None if not found
        """
        try:
            db = get_db()
            return db.query(User).filter_by(email=email).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching user by email {email}: {e}")
            return None
    
    def get_all(self) -> List[User]:
        """
        Get all users.
        
        Returns:
            List of all User objects
        """
        try:
            db = get_db()
            return db.query(User).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching all users: {e}")
            return []
    
    def create(self, user: User) -> Optional[User]:
        """
        Create a new user in the database.
        
        Args:
            user: User object to create (without ID)
            
        Returns:
            Created User object with ID, or None on error
        """
        try:
            db = get_db()
            db.add(user)
            db.flush()  # Get the ID before commit
            db.refresh(user)  # Refresh to load relationships
            return user
        except SQLAlchemyError as e:
            logger.error(f"Error creating user {user.username}: {e}")
            return None
    
    def update(self, user: User) -> Optional[User]:
        """
        Update an existing user.
        
        Args:
            user: User object with updated data
            
        Returns:
            Updated User object or None on error
        """
        try:
            db = get_db()
            # Merge the detached user object into the session
            updated_user = db.merge(user)
            db.flush()
            db.refresh(updated_user)
            return updated_user
        except SQLAlchemyError as e:
            logger.error(f"Error updating user {user.id}: {e}")
            return None
    
    def delete(self, user_id: int) -> bool:
        """
        Delete a user by ID.
        
        Args:
            user_id: ID of user to delete
            
        Returns:
            True if deleted, False on error or not found
        """
        try:
            db = get_db()
            user = db.query(User).filter_by(id=user_id).first()
            if user:
                db.delete(user)
                db.flush()
                return True
            return False
        except SQLAlchemyError as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False
    
    def exists_by_username(self, username: str) -> bool:
        """Check if a username exists."""
        return self.get_by_username(username) is not None
    
    def exists_by_email(self, email: str) -> bool:
        """Check if an email exists."""
        return self.get_by_email(email) is not None
    
    def assign_role(self, user_id: int, role_id: int) -> bool:
        """
        Assign a role to a user.
        
        Args:
            user_id: User ID
            role_id: Role ID
            
        Returns:
            True if assigned, False on error
        """
        try:
            db = get_db()
            role_user = RoleUser(user_id=user_id, role_id=role_id)
            db.add(role_user)
            db.flush()
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error assigning role {role_id} to user {user_id}: {e}")
            return False
    
    def get_user_roles(self, user_id: int) -> List[Role]:
        """
        Get all roles for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of Role objects
        """
        try:
            db = get_db()
            user = db.query(User).filter_by(id=user_id).first()
            if user and user.user_roles:
                return [ur.role for ur in user.user_roles]
            return []
        except SQLAlchemyError as e:
            logger.error(f"Error fetching roles for user {user_id}: {e}")
            return []