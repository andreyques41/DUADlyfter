"""
User Repository
Data access layer for User model.
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.auth.models import User, UserRole
from config.logging import get_logger

logger = get_logger(__name__)


class UserRepository:
    """Repository for User database operations."""
    
    def __init__(self, db_session: Session):
        """
        Initialize repository with database session.
        
        Args:
            db_session: SQLAlchemy session
        """
        self.db = db_session
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None
        """
        try:
            return self.db.query(User).filter(User.id == user_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching user by ID {user_id}: {e}", exc_info=True)
            return None
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User object or None
        """
        try:
            return self.db.query(User).filter(User.username == username).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching user by username '{username}': {e}", exc_info=True)
            return None
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: Email address
            
        Returns:
            User object or None
        """
        try:
            return self.db.query(User).filter(User.email == email).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching user by email '{email}': {e}", exc_info=True)
            return None
    
    def create(self, username: str, email: str, password_hash: str, role: UserRole = UserRole.CHEF) -> Optional[User]:
        """
        Create new user.
        
        Args:
            username: Username
            email: Email address
            password_hash: Hashed password
            role: User role (default: CHEF)
            
        Returns:
            Created User object or None if failed
        """
        try:
            user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                role=role
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"User created successfully: {username} (ID: {user.id})")
            return user
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating user '{username}': {e}", exc_info=True)
            return None
    
    def update(self, user: User) -> bool:
        """
        Update existing user.
        
        Args:
            user: User object with updated data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.db.commit()
            self.db.refresh(user)
            logger.info(f"User updated successfully: {user.username} (ID: {user.id})")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating user {user.id}: {e}", exc_info=True)
            return False
    
    def delete(self, user_id: int) -> bool:
        """
        Delete user (soft delete by setting is_active = 0).
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user = self.get_by_id(user_id)
            if not user:
                logger.warning(f"User {user_id} not found for deletion")
                return False
            
            user.is_active = 0
            self.db.commit()
            logger.info(f"User deactivated: {user.username} (ID: {user_id})")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting user {user_id}: {e}", exc_info=True)
            return False
    
    def get_all_active(self) -> list[User]:
        """
        Get all active users.
        
        Returns:
            List of active User objects
        """
        try:
            return self.db.query(User).filter(User.is_active == 1).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching active users: {e}", exc_info=True)
            return []
