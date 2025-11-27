from flask import request
from config.logging import get_logger
from app.core.lib.error_utils import success_response, error_response
from app.public.services import PublicService
from app.chefs.schemas import ChefPublicSchema
from app.dishes.schemas import DishResponseSchema
from app.menus.schemas import MenuResponseSchema

logger = get_logger(__name__)


class PublicController:
    """Controller for public (non-authenticated) endpoints"""

    @staticmethod
    def _get_service() -> PublicService:
        """Helper to create service instance"""
        return PublicService()

    # ==================== Chef Endpoints ====================

    @staticmethod
    def get_chefs():
        """
        Get paginated list of active chefs with optional filters.
        Query params: specialty, location, search, page, per_page
        """
        try:
            # Get query params
            specialty = request.args.get("specialty")
            location = request.args.get("location")
            search = request.args.get("search")
            page = request.args.get("page", default=1, type=int)
            per_page = request.args.get("per_page", default=20, type=int)
            
            # Validate pagination params
            if page < 1:
                return error_response("Page must be >= 1", 400)
            if per_page < 1 or per_page > 100:
                return error_response("Per page must be between 1 and 100", 400)
            
            service = PublicController._get_service()
            result = service.get_chefs(
                specialty=specialty,
                location=location,
                search=search,
                page=page,
                per_page=per_page
            )
            
            # Serialize chefs
            chef_schema = ChefPublicSchema(many=True)
            serialized_chefs = chef_schema.dump(result["chefs"])
            
            return success_response({
                "chefs": serialized_chefs,
                "pagination": {
                    "total": result["total"],
                    "page": result["page"],
                    "per_page": result["per_page"],
                    "total_pages": result["total_pages"]
                }
            })
            
        except Exception as e:
            logger.error(f"Error fetching public chefs: {str(e)}")
            return error_response("Failed to fetch chefs", 500)

    @staticmethod
    def get_chef_profile(chef_id: int):
        """Get public chef profile with dishes and menus"""
        try:
            service = PublicController._get_service()
            result = service.get_chef_profile(chef_id)
            
            if not result:
                return error_response(f"Chef with ID {chef_id} not found or inactive", 404)
            
            # Serialize response
            chef_schema = ChefPublicSchema()
            dish_schema = DishResponseSchema(many=True)
            menu_schema = MenuResponseSchema(many=True)
            
            return success_response({
                "chef": chef_schema.dump(result["chef"]),
                "dishes": dish_schema.dump(result["dishes"]),
                "menus": menu_schema.dump(result["menus"]),
                "stats": result["stats"]
            })
            
        except Exception as e:
            logger.error(f"Error fetching chef profile {chef_id}: {str(e)}")
            return error_response("Failed to fetch chef profile", 500)

    # ==================== Menu & Dish Endpoints ====================

    @staticmethod
    def get_menu_details(menu_id: int):
        """Get public menu with dishes and chef info"""
        try:
            service = PublicController._get_service()
            result = service.get_menu_details(menu_id)
            
            if not result:
                return error_response(f"Menu with ID {menu_id} not found or inactive", 404)
            
            # Serialize response
            menu_schema = MenuResponseSchema()
            chef_schema = ChefPublicSchema()
            dish_schema = DishResponseSchema()
            
            # Serialize dishes with order position
            dishes_data = [
                {
                    **dish_schema.dump(item["dish"]),
                    "order_position": item["order_position"]
                }
                for item in result["dishes"]
            ]
            
            return success_response({
                "menu": menu_schema.dump(result["menu"]),
                "chef": chef_schema.dump(result["chef"]) if result["chef"] else None,
                "dishes": dishes_data
            })
            
        except Exception as e:
            logger.error(f"Error fetching menu {menu_id}: {str(e)}")
            return error_response("Failed to fetch menu", 500)

    @staticmethod
    def get_dish_details(dish_id: int):
        """Get public dish with chef info"""
        try:
            service = PublicController._get_service()
            result = service.get_dish_details(dish_id)
            
            if not result:
                return error_response(f"Dish with ID {dish_id} not found or inactive", 404)
            
            # Serialize response
            dish_schema = DishResponseSchema()
            chef_schema = ChefPublicSchema()
            
            return success_response({
                "dish": dish_schema.dump(result["dish"]),
                "chef": chef_schema.dump(result["chef"]) if result["chef"] else None
            })
            
        except Exception as e:
            logger.error(f"Error fetching dish {dish_id}: {str(e)}")
            return error_response("Failed to fetch dish", 500)

    # ==================== Search & Discovery ====================

    @staticmethod
    def search_chefs():
        """Full-text search for chefs"""
        try:
            query = request.args.get("q", "")
            page = request.args.get("page", default=1, type=int)
            per_page = request.args.get("per_page", default=20, type=int)
            
            if not query or len(query) < 2:
                return error_response("Search query must be at least 2 characters", 400)
            
            service = PublicController._get_service()
            result = service.search_chefs(query, page, per_page)
            
            # Serialize chefs
            chef_schema = ChefPublicSchema(many=True)
            serialized_chefs = chef_schema.dump(result["chefs"])
            
            return success_response({
                "query": query,
                "chefs": serialized_chefs,
                "pagination": {
                    "total": result["total"],
                    "page": result["page"],
                    "per_page": result["per_page"],
                    "total_pages": result["total_pages"]
                }
            })
            
        except Exception as e:
            logger.error(f"Error searching chefs: {str(e)}")
            return error_response("Failed to search chefs", 500)

    @staticmethod
    def get_filters():
        """Get available filter options"""
        try:
            service = PublicController._get_service()
            filters = service.get_filters()
            
            return success_response(filters)
            
        except Exception as e:
            logger.error(f"Error fetching filters: {str(e)}")
            return error_response("Failed to fetch filters", 500)
