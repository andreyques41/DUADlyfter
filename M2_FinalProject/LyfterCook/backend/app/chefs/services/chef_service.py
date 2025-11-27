"""
Chef Service - Business logic for chef profile management
"""
from typing import Optional, List, Dict
from app.chefs.repositories.chef_repository import ChefRepository
from app.chefs.models.chef_model import Chef
from config.logging import get_logger

logger = get_logger(__name__)


class ChefService:
    """Service for chef profile business logic"""
    
    def __init__(self, chef_repository: ChefRepository):
        self.chef_repository = chef_repository
    
    def create_profile(self, user_id: int, profile_data: dict) -> Chef:
        """
        Create a new chef profile
        
        Args:
            user_id: User ID to associate with chef profile
            profile_data: Dictionary with bio, specialty, phone, location
            
        Returns:
            Created Chef instance
            
        Raises:
            ValueError: If chef profile already exists for user
        """
        # Check if chef profile already exists
        if self.chef_repository.exists_by_user_id(user_id):
            logger.warning(f"Attempted to create duplicate chef profile for user {user_id}")
            raise ValueError(f"Chef profile already exists for user {user_id}")
        
        # Prepare chef data
        chef_data = {
            'user_id': user_id,
            'bio': profile_data.get('bio'),
            'specialty': profile_data.get('specialty'),
            'phone': profile_data.get('phone'),
            'location': profile_data.get('location'),
            'is_active': True
        }
        
        chef = self.chef_repository.create(chef_data)
        logger.info(f"Created chef profile for user {user_id}")
        return chef
    
    def get_profile_by_user_id(self, user_id: int) -> Optional[Chef]:
        """
        Get chef profile by user ID
        
        Args:
            user_id: User ID
            
        Returns:
            Chef instance or None if not found
        """
        return self.chef_repository.get_by_user_id(user_id)
    
    def get_profile_by_id(self, chef_id: int) -> Optional[Chef]:
        """
        Get chef profile by ID
        
        Args:
            chef_id: Chef ID
            
        Returns:
            Chef instance or None if not found
        """
        return self.chef_repository.get_by_id(chef_id)
    
    def get_all_profiles(self, active_only: bool = True) -> List[Chef]:
        """
        Get all chef profiles
        
        Args:
            active_only: If True, return only active profiles
            
        Returns:
            List of Chef instances
        """
        return self.chef_repository.get_all(active_only=active_only)
    
    def update_profile(self, user_id: int, update_data: dict) -> Chef:
        """
        Update chef profile
        
        Args:
            user_id: User ID of the chef to update
            update_data: Dictionary with fields to update
            
        Returns:
            Updated Chef instance
            
        Raises:
            ValueError: If chef profile not found
        """
        chef = self.chef_repository.get_by_user_id(user_id)
        if not chef:
            logger.warning(f"Attempted to update non-existent chef profile for user {user_id}")
            raise ValueError(f"Chef profile not found for user {user_id}")
        
        # Filter out None values and fields that shouldn't be updated
        filtered_data = {
            k: v for k, v in update_data.items() 
            if v is not None and k in ['bio', 'specialty', 'phone', 'location', 'is_active']
        }
        
        updated_chef = self.chef_repository.update(chef, filtered_data)
        logger.info(f"Updated chef profile for user {user_id}")
        return updated_chef
    
    def deactivate_profile(self, user_id: int) -> Chef:
        """
        Deactivate chef profile
        
        Args:
            user_id: User ID of the chef to deactivate
            
        Returns:
            Updated Chef instance
            
        Raises:
            ValueError: If chef profile not found
        """
        chef = self.chef_repository.get_by_user_id(user_id)
        if not chef:
            logger.warning(f"Attempted to deactivate non-existent chef profile for user {user_id}")
            raise ValueError(f"Chef profile not found for user {user_id}")
        
        updated_chef = self.chef_repository.update(chef, {'is_active': False})
        logger.info(f"Deactivated chef profile for user {user_id}")
        return updated_chef
    
    def activate_profile(self, user_id: int) -> Chef:
        """
        Activate chef profile
        
        Args:
            user_id: User ID of the chef to activate
            
        Returns:
            Updated Chef instance
            
        Raises:
            ValueError: If chef profile not found
        """
        chef = self.chef_repository.get_by_user_id(user_id)
        if not chef:
            logger.warning(f"Attempted to activate non-existent chef profile for user {user_id}")
            raise ValueError(f"Chef profile not found for user {user_id}")
        
        updated_chef = self.chef_repository.update(chef, {'is_active': True})
        logger.info(f"Activated chef profile for user {user_id}")
        return updated_chef
