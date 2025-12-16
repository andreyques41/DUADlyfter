"""
Dish Service - Business logic for dish management
Note: Cloudinary integration will be added later when configured
"""
from typing import Optional, List
from app.dishes.repositories.dish_repository import DishRepository
from app.dishes.models.dish_model import Dish
from app.chefs.repositories.chef_repository import ChefRepository
from app.core.cache_manager import invalidate_cache
from app.core.middleware.cache_helper import CacheHelper
from config.logging import get_logger

logger = get_logger(__name__)


class DishService:
    """Service for dish business logic"""
    
    def __init__(self, dish_repository: DishRepository, chef_repository: ChefRepository):
        self.dish_repository = dish_repository
        self.chef_repository = chef_repository
        self.cache_helper = CacheHelper(resource_name="dish", version="v1")
    
    def create_dish(self, user_id: int, dish_data: dict) -> Dish:
        """
        Create a new dish for a chef
        
        Args:
            user_id: User ID of the chef
            dish_data: Dictionary with dish information and ingredients
            
        Returns:
            Created Dish instance
            
        Raises:
            ValueError: If chef profile not found
        """
        # Get chef profile
        chef = self.chef_repository.get_by_user_id(user_id)
        if not chef:
            logger.warning(f"Attempted to create dish for user {user_id} without chef profile")
            raise ValueError("Chef profile not found. Please create your chef profile first.")
        
        # Extract ingredients from dish_data
        ingredients_data = dish_data.pop('ingredients', [])
        
        # Add chef_id to dish data
        dish_data['chef_id'] = chef.id
        
        dish = self.dish_repository.create(dish_data, ingredients_data)
        logger.info(f"Created dish {dish.id} for chef {chef.id}")
        
        # Invalidate related caches
        self.cache_helper.invalidate(f"chef:{chef.id}:*")
        invalidate_cache('route:public:dishes:*')
        
        return dish
    
    def get_dish_by_id(self, dish_id: int, user_id: int) -> Optional[Dish]:
        """
        Get dish by ID (only if owned by the chef) - Returns ORM object for internal use
        
        Args:
            dish_id: Dish ID
            user_id: User ID of the chef
            
        Returns:
            Dish instance or None if not found or not owned
            
        Raises:
            ValueError: If chef profile not found
        """
        # Get chef profile
        chef = self.chef_repository.get_by_user_id(user_id)
        if not chef:
            raise ValueError("Chef profile not found")
        
        # Get dish
        dish = self.dish_repository.get_by_id(dish_id, include_ingredients=True)
        
        # Verify ownership
        if not dish or dish.chef_id != chef.id:
            return None
            
        return dish
    
    def get_dish_by_id_cached(self, dish_id: int, user_id: int) -> Optional[dict]:
        """
        Get dish by ID (only if owned by the chef) - Returns serialized dict with caching
        
        Args:
            dish_id: Dish ID
            user_id: User ID of the chef
            
        Returns:
            Serialized dish dict or None if not found or not owned
            
        Raises:
            ValueError: If chef profile not found
        """
        # Get chef profile
        chef = self.chef_repository.get_by_user_id(user_id)
        if not chef:
            raise ValueError("Chef profile not found")
        
        return self.cache_helper.get_or_set(
            cache_key=f"{dish_id}:user={user_id}",
            fetch_func=lambda: self._get_dish_if_owned(dish_id, chef.id),
            schema_class=DishResponseSchema,
            ttl=600
        )
    
    def _get_dish_if_owned(self, dish_id: int, chef_id: int) -> Optional[Dish]:
        """Helper to get dish only if owned by chef"""
        dish = self.dish_repository.get_by_id(dish_id, include_ingredients=True)
        
        # Verify ownership
        if not dish or dish.chef_id != chef_id:
            return None
            
        return dish
    
    def get_all_dishes(self, user_id: int, active_only: bool = False) -> List[Dish]:
        """
        Get all dishes for the logged in chef - Returns ORM objects for internal use
        
        Args:
            user_id: User ID of the chef
            active_only: Whether to filter only active dishes
            
        Returns:
            List of Dish instances
            
        Raises:
            ValueError: If chef profile not found
        """
        # Get chef profile
        chef = self.chef_repository.get_by_user_id(user_id)
        if not chef:
            raise ValueError("Chef profile not found")
        
        # Get dishes
        dishes = self.dish_repository.get_by_chef_id(chef.id, active_only=active_only)
        return dishes
    
    def get_all_dishes_cached(self, user_id: int, active_only: bool = False) -> List[dict]:
        """
        Get all dishes for the logged in chef - Returns serialized dicts with caching
        
        Args:
            user_id: User ID of the chef
            active_only: Whether to filter only active dishes
            
        Returns:
            List of serialized dish dicts
            
        Raises:
            ValueError: If chef profile not found
        """
        # Get chef profile
        chef = self.chef_repository.get_by_user_id(user_id)
        if not chef:
            raise ValueError("Chef profile not found")
        
        return self.cache_helper.get_or_set(
            cache_key=f"chef:{chef.id}:active={active_only}",
            fetch_func=lambda: self.dish_repository.get_by_chef_id(chef.id, active_only=active_only),
            schema_class=DishResponseSchema,
            ttl=300,
            many=True
        )
    
    def update_dish(self, dish_id: int, user_id: int, update_data: dict) -> Dish:
        """
        Update dish (only if owned by the chef)
        
        Args:
            dish_id: Dish ID
            user_id: User ID of the chef
            update_data: Dictionary with fields to update
            
        Returns:
            Updated Dish instance
            
        Raises:
            ValueError: If dish not found or not owned by chef
        """
        # Get dish with ownership check
        dish = self.get_dish_by_id(dish_id, user_id)
        if not dish:
            raise ValueError("Dish not found or access denied")
        
        # Extract ingredients if provided
        ingredients_data = update_data.pop('ingredients', None)
        
        # Filter out None values and fields that shouldn't be updated
        allowed_fields = ['name', 'description', 'price', 'category', 'preparation_steps', 
                         'prep_time', 'servings', 'photo_url', 'is_active']
        filtered_data = {
            k: v for k, v in update_data.items() 
            if v is not None and k in allowed_fields
        }
        
        updated_dish = self.dish_repository.update(dish, filtered_data, ingredients_data)
        logger.info(f"Updated dish {dish_id}")
        
        # Invalidate related caches
        chef = self.chef_repository.get_by_user_id(user_id)
        self.cache_helper.invalidate(
            f"{dish_id}:user={user_id}",
            f"chef:{chef.id}:active=True",
            f"chef:{chef.id}:active=False"
        )
        invalidate_cache('route:public:dishes:*')
        
        return updated_dish
    
    def delete_dish(self, dish_id: int, user_id: int) -> None:
        """
        Delete dish (only if owned by the chef)
        
        Args:
            dish_id: Dish ID
            user_id: User ID of the chef
            
        Raises:
            ValueError: If dish not found or not owned by chef
        """
        # Get dish with ownership check
        dish = self.get_dish_by_id(dish_id, user_id)
        if not dish:
            raise ValueError("Dish not found or access denied")
        
        self.dish_repository.delete(dish)
        logger.info(f"Deleted dish {dish_id}")
        
        # Invalidate related caches
        chef = self.chef_repository.get_by_user_id(user_id)
        self.cache_helper.invalidate(
            f"{dish_id}:user={user_id}",
            f"chef:{chef.id}:active=True",
            f"chef:{chef.id}:active=False"
        )
        invalidate_cache('route:public:dishes:*')
    
    def upload_dish_photo(self, dish_id: int, user_id: int, photo_file) -> str:
        """
        Upload dish photo to Cloudinary (placeholder for now)
        
        Args:
            dish_id: Dish ID
            user_id: User ID of the chef
            photo_file: File object from request
            
        Returns:
            Cloudinary URL
            
        Raises:
            ValueError: If dish not found or not owned
            NotImplementedError: Cloudinary not configured yet
        """
        # Get dish with ownership check
        dish = self.get_dish_by_id(dish_id, user_id)
        if not dish:
            raise ValueError("Dish not found or access denied")
        
        # TODO: Implement Cloudinary integration
        # from app.core.lib.cloudinary_utils import upload_image
        # photo_url = upload_image(photo_file, folder='dishes')
        # self.dish_repository.update(dish, {'photo_url': photo_url})
        
        raise NotImplementedError("Cloudinary integration not yet configured. Add photo_url directly in dish update for now.")
