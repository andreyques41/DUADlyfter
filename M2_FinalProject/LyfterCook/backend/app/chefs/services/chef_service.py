"""
Chef Service - Business logic for chef profile management
"""
from typing import Optional, List, Dict
from app.chefs.repositories.chef_repository import ChefRepository
from app.chefs.models.chef_model import Chef
from app.core.cache_manager import invalidate_cache
from app.core.middleware.cache_helper import CacheHelper
from config.logging import get_logger

logger = get_logger(__name__)


class ChefService:
    """Service for chef profile business logic"""
    
    def __init__(self, chef_repository: ChefRepository):
        self.chef_repository = chef_repository
        self.cache_helper = CacheHelper(resource_name="chef", version="v1")
    
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
        
        # Invalidate related caches
        self.cache_helper.invalidate_pattern("*")  # Clear all chef caches
        invalidate_cache('route:public:chefs:*')  # Clear public route cache
        
        return chef
    
    def get_profile_by_user_id(self, user_id: int) -> Optional[Chef]:
        """
        Get chef profile by user ID (returns ORM object for internal use).
        
        Args:
            user_id: User ID
            
        Returns:
            Chef instance or None if not found
        """
        return self.chef_repository.get_by_user_id(user_id)
    
    def get_profile_by_user_id_cached(self, user_id: int) -> Optional[dict]:
        """
        Get chef profile by user ID with caching (returns serialized dict).
        
        Args:
            user_id: User ID
            
        Returns:
            Serialized chef dict or None if not found
        """
        from app.chefs.schemas.chef_schema import ChefResponseSchema
        
        return self.cache_helper.get_or_set(
            cache_key=f"profile:user:{user_id}",
            fetch_func=lambda: self.chef_repository.get_by_user_id(user_id),
            schema_class=ChefResponseSchema,
            ttl=600  # 10 minutes
        )
    
    def get_profile_by_id(self, chef_id: int) -> Optional[Chef]:
        """
        Get chef profile by ID (returns ORM object for internal use).
        
        Args:
            chef_id: Chef ID
            
        Returns:
            Chef instance or None if not found
        """
        return self.chef_repository.get_by_id(chef_id)
    
    def get_profile_by_id_cached(self, chef_id: int) -> Optional[dict]:
        """
        Get chef profile by ID with caching (returns serialized dict).
        
        Args:
            chef_id: Chef ID
            
        Returns:
            Serialized chef dict or None if not found
        """
        from app.chefs.schemas.chef_schema import ChefResponseSchema
        
        return self.cache_helper.get_or_set(
            cache_key=f"profile:{chef_id}",
            fetch_func=lambda: self.chef_repository.get_by_id(chef_id),
            schema_class=ChefResponseSchema,
            ttl=600  # 10 minutes
        )
    
    def get_all_profiles(self, active_only: bool = True) -> List[Chef]:
        """
        Get all chef profiles (returns ORM objects for internal use).
        
        Args:
            active_only: If True, return only active profiles
            
        Returns:
            List of Chef instances
        """
        return self.chef_repository.get_all(active_only=active_only)
    
    def get_all_profiles_cached(self, active_only: bool = True) -> List[dict]:
        """
        Get all chef profiles with caching (returns serialized list).
        
        Args:
            active_only: If True, return only active profiles
            
        Returns:
            List of serialized chef dicts
        """
        from app.chefs.schemas.chef_schema import ChefResponseSchema
        
        return self.cache_helper.get_or_set(
            cache_key=f"list:active:{active_only}",
            fetch_func=lambda: self.chef_repository.get_all(active_only=active_only),
            schema_class=ChefResponseSchema,
            ttl=300,  # 5 minutes
            many=True
        )
    
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
        
        # Invalidate related caches
        self.cache_helper.invalidate(
            f"profile:{chef.id}",
            f"profile:user:{user_id}",
            "list:active:True",
            "list:active:False"
        )
        invalidate_cache('route:public:chefs:*')
        invalidate_cache('route:chefs:*')
        
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
        
        # Invalidate related caches
        self.cache_helper.invalidate(
            f"profile:{chef.id}",
            f"profile:user:{user_id}",
            "list:active:True",
            "list:active:False"
        )
        invalidate_cache('route:public:chefs:*')
        
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
        
        # Invalidate related caches
        self.cache_helper.invalidate(
            f"profile:{chef.id}",
            f"profile:user:{user_id}",
            "list:active:True",
            "list:active:False"
        )
        invalidate_cache('route:public:chefs:*')
        
        return updated_chef
