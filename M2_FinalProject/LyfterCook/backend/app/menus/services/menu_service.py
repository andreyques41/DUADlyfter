"""
Menu Service - Business logic for menu management
"""
from typing import Optional, List
from app.menus.repositories.menu_repository import MenuRepository
from app.menus.models.menu_model import Menu
from app.chefs.repositories.chef_repository import ChefRepository
from app.dishes.repositories.dish_repository import DishRepository
from config.logging import get_logger

logger = get_logger(__name__)


class MenuService:
    """Service for menu business logic"""
    
    def __init__(self, menu_repository: MenuRepository, chef_repository: ChefRepository, dish_repository: DishRepository):
        self.menu_repository = menu_repository
        self.chef_repository = chef_repository
        self.dish_repository = dish_repository
    
    def create_menu(self, user_id: int, menu_data: dict) -> Menu:
        """
        Create a new menu for a chef
        
        Args:
            user_id: User ID of the chef
            menu_data: Dictionary with menu information and dish_ids
            
        Returns:
            Created Menu instance
            
        Raises:
            ValueError: If chef profile not found or dishes don't belong to chef
        """
        # Get chef profile
        chef = self.chef_repository.get_by_user_id(user_id)
        if not chef:
            logger.warning(f"Attempted to create menu for user {user_id} without chef profile")
            raise ValueError("Chef profile not found. Please create your chef profile first.")
        
        # Extract dish_ids
        dish_ids = menu_data.pop('dish_ids', [])
        
        # Validate dishes belong to chef
        if dish_ids:
            for dish_id in dish_ids:
                dish = self.dish_repository.get_by_id(dish_id, include_ingredients=False)
                if not dish or dish.chef_id != chef.id:
                    raise ValueError(f"Dish {dish_id} not found or does not belong to you")
        
        # Add chef_id to menu data
        menu_data['chef_id'] = chef.id
        
        menu = self.menu_repository.create(menu_data, dish_ids)
        logger.info(f"Created menu {menu.id} for chef {chef.id}")
        return menu
    
    def get_menu_by_id(self, menu_id: int, user_id: int) -> Optional[Menu]:
        """
        Get menu by ID (only if owned by the chef)
        
        Args:
            menu_id: Menu ID
            user_id: User ID of the chef
            
        Returns:
            Menu instance or None if not found or not owned
            
        Raises:
            ValueError: If chef profile not found
        """
        # Get chef profile
        chef = self.chef_repository.get_by_user_id(user_id)
        if not chef:
            raise ValueError("Chef profile not found")
        
        # Get menu
        menu = self.menu_repository.get_by_id(menu_id, include_dishes=True)
        
        # Verify ownership
        if menu and menu.chef_id != chef.id:
            logger.warning(f"User {user_id} attempted to access menu {menu_id} owned by chef {menu.chef_id}")
            return None
        
        return menu
    
    def get_all_menus(self, user_id: int, active_only: bool = False) -> List[Menu]:
        """
        Get all menus for a chef
        
        Args:
            user_id: User ID of the chef
            active_only: If True, only return active menus
            
        Returns:
            List of Menu instances with dishes
            
        Raises:
            ValueError: If chef profile not found
        """
        # Get chef profile
        chef = self.chef_repository.get_by_user_id(user_id)
        if not chef:
            raise ValueError("Chef profile not found")
        
        return self.menu_repository.get_by_chef_id(chef.id, active_only=active_only)
    
    def update_menu(self, menu_id: int, user_id: int, update_data: dict) -> Menu:
        """
        Update menu basic info (only if owned by the chef)
        
        Args:
            menu_id: Menu ID
            user_id: User ID of the chef
            update_data: Dictionary with fields to update
            
        Returns:
            Updated Menu instance
            
        Raises:
            ValueError: If menu not found or not owned by chef
        """
        # Get menu with ownership check
        menu = self.get_menu_by_id(menu_id, user_id)
        if not menu:
            raise ValueError("Menu not found or access denied")
        
        # Filter allowed fields
        allowed_fields = ['name', 'description', 'status']
        filtered_data = {
            k: v for k, v in update_data.items() 
            if v is not None and k in allowed_fields
        }
        
        updated_menu = self.menu_repository.update(menu, filtered_data)
        logger.info(f"Updated menu {menu_id}")
        return updated_menu
    
    def assign_dishes_to_menu(self, menu_id: int, user_id: int, dishes_data: List[dict]) -> Menu:
        """
        Assign dishes to menu (replaces existing)
        
        Args:
            menu_id: Menu ID
            user_id: User ID of the chef
            dishes_data: List of {dish_id, order_position}
            
        Returns:
            Updated Menu instance
            
        Raises:
            ValueError: If menu not found, not owned, or dishes don't belong to chef
        """
        # Get menu with ownership check
        menu = self.get_menu_by_id(menu_id, user_id)
        if not menu:
            raise ValueError("Menu not found or access denied")
        
        # Get chef
        chef = self.chef_repository.get_by_user_id(user_id)
        
        # Validate all dishes belong to chef
        for dish_data in dishes_data:
            dish_id = dish_data['dish_id']
            dish = self.dish_repository.get_by_id(dish_id, include_ingredients=False)
            if not dish or dish.chef_id != chef.id:
                raise ValueError(f"Dish {dish_id} not found or does not belong to you")
        
        updated_menu = self.menu_repository.assign_dishes(menu, dishes_data)
        logger.info(f"Assigned dishes to menu {menu_id}")
        return updated_menu
    
    def delete_menu(self, menu_id: int, user_id: int) -> None:
        """
        Delete menu (only if owned by the chef)
        
        Args:
            menu_id: Menu ID
            user_id: User ID of the chef
            
        Raises:
            ValueError: If menu not found or not owned by chef
        """
        # Get menu with ownership check
        menu = self.get_menu_by_id(menu_id, user_id)
        if not menu:
            raise ValueError("Menu not found or access denied")
        
        self.menu_repository.delete(menu)
        logger.info(f"Deleted menu {menu_id}")
