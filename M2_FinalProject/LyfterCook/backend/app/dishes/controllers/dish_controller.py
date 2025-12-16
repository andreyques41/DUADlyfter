"""
Dish Controller - HTTP request/response handling for dish endpoints
"""
from flask import request, jsonify, g
from app.dishes.schemas import (
    DishCreateSchema,
    DishUpdateSchema,
    DishResponseSchema
)
from app.dishes.services import DishService
from app.dishes.repositories import DishRepository
from app.chefs.repositories import ChefRepository
from app.core.lib.error_utils import error_response, success_response
from app.core.database import get_db
from app.core.middleware.request_decorators import validate_json
from config.logging import get_logger

logger = get_logger(__name__)


class DishController:
    """Controller for dish operations"""
    
    def __init__(self):
        """Initialize controller with logger"""
        self.logger = logger
    
    def _get_service(self):
        """
        Get dish service with database session.
        Creates new instances per request using Flask's g.db.
        """
        db = get_db()
        dish_repo = DishRepository(db)
        chef_repo = ChefRepository(db)
        return DishService(dish_repo, chef_repo)
    
    @validate_json(DishCreateSchema)
    def create_dish(self, current_user):
        """
        Create a new dish with ingredients
        
        Request body:
            {
                "name": "Pasta Carbonara",
                "description": "Classic Italian pasta dish",
                "price": 15.99,
                "category": "Main Course",
                "preparation_steps": "1. Boil pasta...",
                "prep_time": 30,
                "servings": 4,
                "photo_url": "https://cloudinary.com/...",
                "ingredients": [
                    {
                        "name": "Spaghetti",
                        "quantity": 400,
                        "unit": "g",
                        "is_optional": false
                    },
                    {
                        "name": "Eggs",
                        "quantity": 4,
                        "unit": "pieces",
                        "is_optional": false
                    }
                ]
            }
        
        Returns:
            201: Dish created successfully
            400: Validation error or chef profile not found
            500: Server error
        """
        try:
            service = self._get_service()
            dish_data = request.validated_data
            
            dish = service.create_dish(current_user['id'], dish_data)
            
            # Serialize response
            schema = DishResponseSchema()
            result = schema.dump(dish)
            
            self.logger.info(f"Dish created for chef {current_user['id']}")
            return success_response(
                data=result,
                message="Dish created successfully",
                status_code=201
            )
            
        except ValueError as e:
            self.logger.warning(f"Dish creation failed: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            self.logger.error(f"Error creating dish: {e}", exc_info=True)
            return error_response("Failed to create dish", 500)
    
    def get_all_dishes(self, current_user):
        """
        Get all dishes for the current chef
        
        Query params:
            active_only: bool (optional, default=false)
        
        Returns:
            200: List of dishes with ingredients
            400: Chef profile not found
            500: Server error
        """
        try:
            service = self._get_service()
            
            # Check if we should filter by active only
            active_only = request.args.get('active_only', 'false').lower() == 'true'
            
            result = service.get_all_dishes_cached(current_user['id'], active_only=active_only)
            
            return success_response(
                data=result,
                message=f"Retrieved {len(result)} dishes"
            )
            
        except ValueError as e:
            self.logger.warning(f"Get dishes failed: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            self.logger.error(f"Error retrieving dishes: {e}", exc_info=True)
            return error_response("Failed to retrieve dishes", 500)
    
    def get_dish_by_id(self, dish_id: int, current_user):
        """
        Get dish by ID with ingredients
        
        Args:
            dish_id: Dish ID from URL parameter
        
        Returns:
            200: Dish data with ingredients
            404: Dish not found or access denied
            500: Server error
        """
        try:
            service = self._get_service()
            result = service.get_dish_by_id_cached(dish_id, current_user['id'])
            
            if not result:
                return error_response("Dish not found or access denied", 404)
            
            return success_response(data=result)
            
        except ValueError as e:
            self.logger.warning(f"Get dish failed: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            self.logger.error(f"Error retrieving dish {dish_id}: {e}", exc_info=True)
            return error_response("Failed to retrieve dish", 500)
    
    @validate_json(DishUpdateSchema)
    def update_dish(self, dish_id: int, current_user):
        """
        Update dish and optionally ingredients
        
        Args:
            dish_id: Dish ID from URL parameter
        
        Request body (all fields optional):
            {
                "name": "Updated Pasta Carbonara",
                "price": 17.99,
                "is_active": true,
                "ingredients": [...]  // If provided, replaces all ingredients
            }
        
        Returns:
            200: Dish updated successfully
            404: Dish not found or access denied
            400: Validation error
            500: Server error
        """
        try:
            service = self._get_service()
            update_data = request.validated_data
            
            dish = service.update_dish(dish_id, current_user['id'], update_data)
            
            # Serialize response
            schema = DishResponseSchema()
            result = schema.dump(dish)
            
            self.logger.info(f"Dish {dish_id} updated")
            return success_response(
                data=result,
                message="Dish updated successfully"
            )
            
        except ValueError as e:
            self.logger.warning(f"Dish update failed: {str(e)}")
            return error_response(str(e), 404)
        except Exception as e:
            self.logger.error(f"Error updating dish {dish_id}: {e}", exc_info=True)
            return error_response("Failed to update dish", 500)
    
    def delete_dish(self, dish_id: int, current_user):
        """
        Delete dish (ingredients cascade delete)
        
        Args:
            dish_id: Dish ID from URL parameter
        
        Returns:
            200: Dish deleted successfully
            404: Dish not found or access denied
            500: Server error
        """
        try:
            service = self._get_service()
            service.delete_dish(dish_id, current_user['id'])
            
            self.logger.info(f"Dish {dish_id} deleted")
            return success_response(
                data={},
                message="Dish deleted successfully"
            )
            
        except ValueError as e:
            self.logger.warning(f"Dish deletion failed: {str(e)}")
            return error_response(str(e), 404)
        except Exception as e:
            self.logger.error(f"Error deleting dish {dish_id}: {e}", exc_info=True)
            return error_response("Failed to delete dish", 500)
