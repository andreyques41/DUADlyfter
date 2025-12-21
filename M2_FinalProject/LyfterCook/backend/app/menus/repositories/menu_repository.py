"""
Menu Repository - Data access layer for Menu and MenuDish models
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from app.menus.models.menu_model import Menu
from app.menus.models.menu_dish_model import MenuDish
from config.logging import get_logger

logger = get_logger(__name__)


class MenuRepository:
    """Repository for Menu and MenuDish database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, menu_data: dict, dish_ids: List[int] = None) -> Menu:
        """
        Create a new menu with dishes
        
        Args:
            menu_data: Dictionary with menu information
            dish_ids: List of dish IDs to add to menu
            
        Returns:
            Created Menu instance with dishes
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            menu = Menu(**menu_data)
            self.db.add(menu)
            self.db.flush()  # Get menu ID
            
            # Add dishes if provided
            if dish_ids:
                for idx, dish_id in enumerate(dish_ids):
                    menu_dish = MenuDish(
                        menu_id=menu.id,
                        dish_id=dish_id,
                        order_position=idx
                    )
                    self.db.add(menu_dish)
            
            self.db.flush()
            logger.info(f"Menu created with ID: {menu.id}, {len(dish_ids or [])} dishes")
            return menu
        except SQLAlchemyError as e:
            logger.error(f"Error creating menu: {e}", exc_info=True)
            raise
    
    def get_by_id(self, menu_id: int, include_dishes: bool = True) -> Optional[Menu]:
        """
        Get menu by ID
        
        Args:
            menu_id: Menu ID
            include_dishes: If True, eager load dishes
            
        Returns:
            Menu instance or None if not found
        """
        try:
            query = self.db.query(Menu)
            if include_dishes:
                query = query.options(joinedload(Menu.menu_dishes).joinedload(MenuDish.dish))
            
            menu = query.filter(Menu.id == menu_id).first()
            if menu:
                logger.debug(f"Retrieved menu ID: {menu_id}")
            return menu
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving menu by ID {menu_id}: {e}", exc_info=True)
            raise
    
    def get_by_chef_and_name(self, chef_id: int, name: str) -> Optional[Menu]:
        """
        Get menu by chef and name (case-insensitive)
        
        Args:
            chef_id: Chef ID
            name: Menu name
            
        Returns:
            Menu instance or None if not found
        """
        try:
            menu = self.db.query(Menu).filter(
                Menu.chef_id == chef_id,
                Menu.name.ilike(name)
            ).first()
            if menu:
                logger.debug(f"Found existing menu '{name}' for chef {chef_id}")
            return menu
        except SQLAlchemyError as e:
            logger.error(f"Error checking menu by name: {e}", exc_info=True)
            raise
    
    def get_by_chef_id(self, chef_id: int, active_only: bool = False) -> List[Menu]:
        """
        Get all menus for a specific chef
        
        Args:
            chef_id: Chef ID
            active_only: If True, only return active menus
            
        Returns:
            List of Menu instances with dishes
        """
        try:
            query = self.db.query(Menu).options(
                joinedload(Menu.menu_dishes).joinedload(MenuDish.dish)
            )
            query = query.filter(Menu.chef_id == chef_id)
            
            if active_only:
                query = query.filter(Menu.status == 'active')
            
            menus = query.all()
            logger.debug(f"Retrieved {len(menus)} menus for chef {chef_id}")
            return menus
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving menus for chef {chef_id}: {e}", exc_info=True)
            raise
    
    def update(self, menu: Menu, update_data: dict) -> Menu:
        """
        Update menu basic info (not dishes)
        
        Args:
            menu: Menu instance to update
            update_data: Dictionary with fields to update
            
        Returns:
            Updated Menu instance
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            for key, value in update_data.items():
                if hasattr(menu, key):
                    setattr(menu, key, value)
            
            self.db.flush()
            logger.info(f"Updated menu ID: {menu.id}")
            return menu
        except SQLAlchemyError as e:
            logger.error(f"Error updating menu ID {menu.id}: {e}", exc_info=True)
            raise
    
    def assign_dishes(self, menu: Menu, dishes_data: List[dict]) -> Menu:
        """
        Replace all dishes in menu
        
        Args:
            menu: Menu instance
            dishes_data: List of {dish_id, order_position}
            
        Returns:
            Updated Menu instance
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            # Delete existing menu_dishes
            self.db.query(MenuDish).filter(MenuDish.menu_id == menu.id).delete()
            
            # Add new dishes
            for dish_data in dishes_data:
                menu_dish = MenuDish(
                    menu_id=menu.id,
                    dish_id=dish_data['dish_id'],
                    order_position=dish_data.get('order_position', 0)
                )
                self.db.add(menu_dish)
            
            self.db.flush()
            logger.info(f"Assigned {len(dishes_data)} dishes to menu {menu.id}")
            return menu
        except SQLAlchemyError as e:
            logger.error(f"Error assigning dishes to menu {menu.id}: {e}", exc_info=True)
            raise
    
    def delete(self, menu: Menu) -> None:
        """
        Delete menu (menu_dishes cascade delete automatically)
        
        Args:
            menu: Menu instance to delete
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            self.db.delete(menu)
            self.db.flush()
            logger.info(f"Deleted menu ID: {menu.id}")
        except SQLAlchemyError as e:
            logger.error(f"Error deleting menu ID {menu.id}: {e}", exc_info=True)
            raise
