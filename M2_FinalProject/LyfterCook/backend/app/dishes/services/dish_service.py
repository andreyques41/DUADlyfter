"""
Dish Service - Business logic for dish management
Note: Cloudinary integration will be added later when configured
"""
from typing import Optional, List
from app.dishes.repositories.dish_repository import DishRepository
from app.dishes.models.dish_model import Dish
from app.chefs.repositories.chef_repository import ChefRepository
from config.logging import get_logger

logger = get_logger(__name__)


class DishService:
    """Service for dish business logic"""
    
    def __init__(self, dish_repository: DishRepository, chef_repository: ChefRepository):
        self.dish_repository = dish_repository
        self.chef_repository = chef_repository
    
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
        return dish
    
    def get_dish_by_id(self, dish_id: int, user_id: int) -> Optional[Dish]:
        """
        Get dish by ID (only if owned by the chef)
        
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
        if dish and dish.chef_id != chef.id:
            logger.warning(f"User {user_id} attempted to access dish {dish_id} owned by chef {dish.chef_id}")
            return None
        
        return dish
    
    def get_all_dishes(self, user_id: int, active_only: bool = False) -> List[Dish]:
        """
        Get all dishes for a chef
        
        Args:
            user_id: User ID of the chef
            active_only: If True, only return active dishes
            
        Returns:
            List of Dish instances with ingredients
            
        Raises:
            ValueError: If chef profile not found
        """
        # Get chef profile
        chef = self.chef_repository.get_by_user_id(user_id)
        if not chef:
            raise ValueError("Chef profile not found")
        
        return self.dish_repository.get_by_chef_id(chef.id, active_only=active_only)
    
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
