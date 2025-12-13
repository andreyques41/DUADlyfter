"""
Menu Controller - HTTP request/response handling for menu endpoints
"""
from flask import request, jsonify, g
from app.menus.schemas import (
    MenuCreateSchema,
    MenuUpdateSchema,
    MenuResponseSchema,
    MenuAssignDishesSchema
)
from app.menus.services import MenuService
from app.menus.repositories import MenuRepository
from app.chefs.repositories import ChefRepository
from app.dishes.repositories import DishRepository
from app.core.lib.error_utils import error_response, success_response
from app.core.database import get_db
from app.core.middleware.request_decorators import validate_json
from config.logging import get_logger

logger = get_logger(__name__)


class MenuController:
    """Controller for menu operations"""
    
    def __init__(self):
        """Initialize controller with logger"""
        self.logger = logger
    
    def _get_service(self):
        """
        Get menu service with database session.
        Creates new instances per request using Flask's g.db.
        """
        db = get_db()
        menu_repo = MenuRepository(db)
        chef_repo = ChefRepository(db)
        dish_repo = DishRepository(db)
        return MenuService(menu_repo, chef_repo, dish_repo)
    
    @validate_json(MenuCreateSchema)
    def create_menu(self, current_user):
        """
        Create a new menu with dishes
        
        Request body:
            {
                "name": "Summer Menu 2025",
                "description": "Fresh seasonal dishes",
                "status": "active",
                "dish_ids": [1, 2, 3]  // Optional
            }
        
        Returns:
            201: Menu created successfully
            400: Validation error or chef profile not found
            500: Server error
        """
        try:
            service = self._get_service()
            menu_data = request.validated_data
            
            menu = service.create_menu(current_user['id'], menu_data)
            
            # Serialize response
            schema = MenuResponseSchema()
            result = schema.dump(menu)
            
            self.logger.info(f"Menu created for chef {current_user['id']}")
            return success_response(
                data=result,
                message="Menu created successfully",
                status_code=201
            )
            
        except ValueError as e:
            self.logger.warning(f"Menu creation failed: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            self.logger.error(f"Error creating menu: {e}", exc_info=True)
            return error_response("Failed to create menu", 500)
    
    def get_all_menus(self, current_user):
        """
        Get all menus for the current chef
        
        Query params:
            active_only: bool (optional, default=false)
        
        Returns:
            200: List of menus with dishes
            400: Chef profile not found
            500: Server error
        """
        try:
            service = self._get_service()
            
            # Check if we should filter by active only
            active_only = request.args.get('active_only', 'false').lower() == 'true'
            
            menus = service.get_all_menus(current_user['id'], active_only=active_only)
            
            # Serialize response
            schema = MenuResponseSchema(many=True)
            result = schema.dump(menus)
            
            return success_response(
                data=result,
                message=f"Retrieved {len(result)} menus"
            )
            
        except ValueError as e:
            self.logger.warning(f"Get menus failed: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            self.logger.error(f"Error retrieving menus: {e}", exc_info=True)
            return error_response("Failed to retrieve menus", 500)
    
    def get_menu_by_id(self, menu_id: int, current_user):
        """
        Get menu by ID with dishes
        
        Args:
            menu_id: Menu ID from URL parameter
        
        Returns:
            200: Menu data with dishes
            404: Menu not found or access denied
            500: Server error
        """
        try:
            service = self._get_service()
            menu = service.get_menu_by_id(menu_id, current_user['id'])
            
            if not menu:
                return error_response("Menu not found or access denied", 404)
            
            # Serialize response
            schema = MenuResponseSchema()
            result = schema.dump(menu)
            
            return success_response(data=result)
            
        except ValueError as e:
            self.logger.warning(f"Get menu failed: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            self.logger.error(f"Error retrieving menu {menu_id}: {e}", exc_info=True)
            return error_response("Failed to retrieve menu", 500)
    
    @validate_json(MenuUpdateSchema)
    def update_menu(self, menu_id: int, current_user):
        """
        Update menu basic info
        
        Args:
            menu_id: Menu ID from URL parameter
        
        Request body (all fields optional):
            {
                "name": "Updated Menu Name",
                "description": "New description",
                "status": "inactive"
            }
        
        Returns:
            200: Menu updated successfully
            404: Menu not found or access denied
            400: Validation error
            500: Server error
        """
        try:
            service = self._get_service()
            update_data = request.validated_data
            
            menu = service.update_menu(menu_id, current_user['id'], update_data)
            
            # Serialize response
            schema = MenuResponseSchema()
            result = schema.dump(menu)
            
            self.logger.info(f"Menu {menu_id} updated")
            return success_response(
                data=result,
                message="Menu updated successfully"
            )
            
        except ValueError as e:
            self.logger.warning(f"Menu update failed: {str(e)}")
            return error_response(str(e), 404)
        except Exception as e:
            self.logger.error(f"Error updating menu {menu_id}: {e}", exc_info=True)
            return error_response("Failed to update menu", 500)
    
    @validate_json(MenuAssignDishesSchema)
    def assign_dishes(self, menu_id: int, current_user):
        """
        Assign dishes to menu (replaces existing)
        
        Args:
            menu_id: Menu ID from URL parameter
        
        Request body:
            {
                "dishes": [
                    {"dish_id": 1, "order_position": 0},
                    {"dish_id": 3, "order_position": 1},
                    {"dish_id": 2, "order_position": 2}
                ]
            }
        
        Returns:
            200: Dishes assigned successfully
            404: Menu not found or access denied
            400: Validation error or dish doesn't belong to chef
            500: Server error
        """
        try:
            service = self._get_service()
            data = request.validated_data
            dishes_data = data['dishes']
            
            menu = service.assign_dishes_to_menu(menu_id, current_user['id'], dishes_data)
            
            # Serialize response
            schema = MenuResponseSchema()
            result = schema.dump(menu)
            
            self.logger.info(f"Dishes assigned to menu {menu_id}")
            return success_response(
                data=result,
                message="Dishes assigned successfully"
            )
            
        except ValueError as e:
            self.logger.warning(f"Assign dishes failed: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            self.logger.error(f"Error assigning dishes to menu {menu_id}: {e}", exc_info=True)
            return error_response("Failed to assign dishes", 500)
    
    def delete_menu(self, menu_id: int, current_user):
        """
        Delete menu (menu_dishes cascade delete)
        
        Args:
            menu_id: Menu ID from URL parameter
        
        Returns:
            200: Menu deleted successfully
            404: Menu not found or access denied
            500: Server error
        """
        try:
            service = self._get_service()
            service.delete_menu(menu_id, current_user['id'])
            
            self.logger.info(f"Menu {menu_id} deleted")
            return success_response(
                data={},
                message="Menu deleted successfully"
            )
            
        except ValueError as e:
            self.logger.warning(f"Menu deletion failed: {str(e)}")
            return error_response(str(e), 404)
        except Exception as e:
            self.logger.error(f"Error deleting menu {menu_id}: {e}", exc_info=True)
            return error_response("Failed to delete menu", 500)
