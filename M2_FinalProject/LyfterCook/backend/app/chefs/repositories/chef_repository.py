"""
Chef Repository - Data access layer for Chef model
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.chefs.models.chef_model import Chef
from config.logging import get_logger

logger = get_logger(__name__)


class ChefRepository:
    """Repository for Chef database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, chef_data: dict) -> Chef:
        """
        Create a new chef profile
        
        Args:
            chef_data: Dictionary with chef information
            
        Returns:
            Created Chef instance
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            chef = Chef(**chef_data)
            self.db.add(chef)
            self.db.flush()  # Get the ID without committing
            logger.info(f"Chef profile created with ID: {chef.id}")
            return chef
        except SQLAlchemyError as e:
            logger.error(f"Error creating chef profile: {e}", exc_info=True)
            raise
    
    def get_by_id(self, chef_id: int) -> Optional[Chef]:
        """
        Get chef by ID
        
        Args:
            chef_id: Chef ID
            
        Returns:
            Chef instance or None if not found
        """
        try:
            chef = self.db.query(Chef).filter(Chef.id == chef_id).first()
            if chef:
                logger.debug(f"Retrieved chef ID: {chef_id}")
            return chef
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving chef by ID {chef_id}: {e}", exc_info=True)
            raise
    
    def get_by_user_id(self, user_id: int) -> Optional[Chef]:
        """
        Get chef by user ID
        
        Args:
            user_id: User ID
            
        Returns:
            Chef instance or None if not found
        """
        try:
            chef = self.db.query(Chef).filter(Chef.user_id == user_id).first()
            if chef:
                logger.debug(f"Retrieved chef for user ID: {user_id}")
            return chef
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving chef by user ID {user_id}: {e}", exc_info=True)
            raise
    
    def get_all(self, active_only: bool = True) -> List[Chef]:
        """
        Get all chefs
        
        Args:
            active_only: If True, return only active chefs
            
        Returns:
            List of Chef instances
        """
        try:
            query = self.db.query(Chef)
            if active_only:
                query = query.filter(Chef.is_active == True)
            else:
                logger.debug(f"No filter applied - returning all chefs")
            chefs = query.all()
            logger.info(f"Retrieved {len(chefs)} chef profiles (active_only={active_only})")
            return chefs
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving all chefs: {e}", exc_info=True)
            raise
    
    def update(self, chef: Chef, update_data: dict) -> Chef:
        """
        Update chef profile
        
        Args:
            chef: Chef instance to update
            update_data: Dictionary with fields to update
            
        Returns:
            Updated Chef instance
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            for key, value in update_data.items():
                if hasattr(chef, key):
                    setattr(chef, key, value)
            
            self.db.flush()
            logger.info(f"Updated chef profile ID: {chef.id}")
            return chef
        except SQLAlchemyError as e:
            logger.error(f"Error updating chef ID {chef.id}: {e}", exc_info=True)
            raise
    
    def delete(self, chef: Chef) -> None:
        """
        Delete chef profile
        
        Args:
            chef: Chef instance to delete
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            self.db.delete(chef)
            self.db.flush()
            logger.info(f"Deleted chef profile ID: {chef.id}")
        except SQLAlchemyError as e:
            logger.error(f"Error deleting chef ID {chef.id}: {e}", exc_info=True)
            raise
    
    def exists_by_user_id(self, user_id: int) -> bool:
        """
        Check if chef profile exists for user
        
        Args:
            user_id: User ID
            
        Returns:
            True if chef exists, False otherwise
        """
        try:
            count = self.db.query(Chef).filter(Chef.user_id == user_id).count()
            return count > 0
        except SQLAlchemyError as e:
            logger.error(f"Error checking chef existence for user {user_id}: {e}", exc_info=True)
            raise
