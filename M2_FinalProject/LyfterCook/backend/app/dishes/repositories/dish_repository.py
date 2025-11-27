"""
Dish Repository - Data access layer for Dish and Ingredient models
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from app.dishes.models.dish_model import Dish
from app.dishes.models.ingredient_model import Ingredient
from config.logging import get_logger

logger = get_logger(__name__)


class DishRepository:
    """Repository for Dish and Ingredient database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, dish_data: dict, ingredients_data: List[dict] = None) -> Dish:
        """
        Create a new dish with ingredients
        
        Args:
            dish_data: Dictionary with dish information
            ingredients_data: List of ingredient dictionaries
            
        Returns:
            Created Dish instance with ingredients
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            dish = Dish(**dish_data)
            self.db.add(dish)
            self.db.flush()  # Get dish ID
            
            # Add ingredients if provided
            if ingredients_data:
                for ing_data in ingredients_data:
                    ing_data['dish_id'] = dish.id
                    ingredient = Ingredient(**ing_data)
                    self.db.add(ingredient)
            
            self.db.flush()
            logger.info(f"Dish created with ID: {dish.id}, {len(ingredients_data or [])} ingredients")
            return dish
        except SQLAlchemyError as e:
            logger.error(f"Error creating dish: {e}", exc_info=True)
            raise
    
    def get_by_id(self, dish_id: int, include_ingredients: bool = True) -> Optional[Dish]:
        """
        Get dish by ID
        
        Args:
            dish_id: Dish ID
            include_ingredients: If True, eager load ingredients
            
        Returns:
            Dish instance or None if not found
        """
        try:
            query = self.db.query(Dish)
            if include_ingredients:
                query = query.options(joinedload(Dish.ingredients))
            
            dish = query.filter(Dish.id == dish_id).first()
            if dish:
                logger.debug(f"Retrieved dish ID: {dish_id}")
            return dish
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving dish by ID {dish_id}: {e}", exc_info=True)
            raise
    
    def get_by_chef_id(self, chef_id: int, active_only: bool = False) -> List[Dish]:
        """
        Get all dishes for a specific chef
        
        Args:
            chef_id: Chef ID
            active_only: If True, only return active dishes
            
        Returns:
            List of Dish instances with ingredients
        """
        try:
            query = self.db.query(Dish).options(joinedload(Dish.ingredients))
            query = query.filter(Dish.chef_id == chef_id)
            
            if active_only:
                query = query.filter(Dish.is_active == True)
            
            dishes = query.all()
            logger.debug(f"Retrieved {len(dishes)} dishes for chef {chef_id}")
            return dishes
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving dishes for chef {chef_id}: {e}", exc_info=True)
            raise
    
    def update(self, dish: Dish, update_data: dict, ingredients_data: List[dict] = None) -> Dish:
        """
        Update dish and optionally replace ingredients
        
        Args:
            dish: Dish instance to update
            update_data: Dictionary with fields to update
            ingredients_data: If provided, replaces all ingredients
            
        Returns:
            Updated Dish instance
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            # Update dish fields
            for key, value in update_data.items():
                if hasattr(dish, key):
                    setattr(dish, key, value)
            
            # Replace ingredients if provided
            if ingredients_data is not None:
                # Delete existing ingredients
                self.db.query(Ingredient).filter(Ingredient.dish_id == dish.id).delete()
                
                # Add new ingredients
                for ing_data in ingredients_data:
                    ing_data['dish_id'] = dish.id
                    ingredient = Ingredient(**ing_data)
                    self.db.add(ingredient)
            
            self.db.flush()
            logger.info(f"Updated dish ID: {dish.id}")
            return dish
        except SQLAlchemyError as e:
            logger.error(f"Error updating dish ID {dish.id}: {e}", exc_info=True)
            raise
    
    def delete(self, dish: Dish) -> None:
        """
        Delete dish (ingredients cascade delete automatically)
        
        Args:
            dish: Dish instance to delete
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            self.db.delete(dish)
            self.db.flush()
            logger.info(f"Deleted dish ID: {dish.id}")
        except SQLAlchemyError as e:
            logger.error(f"Error deleting dish ID {dish.id}: {e}", exc_info=True)
            raise
