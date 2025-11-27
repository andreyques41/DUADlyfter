from typing import List, Dict, Optional
from config.logging import get_logger
from app.public.repositories import PublicRepository
from app.chefs.schemas import ChefPublicSchema
from app.dishes.schemas import DishResponseSchema
from app.menus.schemas import MenuResponseSchema

logger = get_logger(__name__)


class PublicService:
    """Service layer for public-facing operations"""

    def __init__(self):
        self.repository = PublicRepository()

    # ==================== Chef Discovery ====================

    def get_chefs(
        self,
        specialty: Optional[str] = None,
        location: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict:
        """
        Get paginated list of active chefs with filters.
        
        Returns:
            {
                "chefs": [...],
                "total": 100,
                "page": 1,
                "per_page": 20,
                "total_pages": 5
            }
        """
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get chefs and total count
        chefs = self.repository.get_active_chefs(
            specialty=specialty,
            location=location,
            search=search,
            limit=per_page,
            offset=offset
        )
        
        total = self.repository.count_active_chefs(
            specialty=specialty,
            location=location,
            search=search
        )
        
        # Calculate total pages
        total_pages = (total + per_page - 1) // per_page  # Ceiling division
        
        return {
            "chefs": chefs,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }

    def get_chef_profile(self, chef_id: int) -> Optional[Dict]:
        """
        Get public chef profile with dishes and menus.
        
        Returns:
            {
                "chef": {...},
                "dishes": [...],
                "menus": [...],
                "stats": {
                    "total_dishes": 10,
                    "total_menus": 3
                }
            }
        """
        chef = self.repository.get_chef_by_id(chef_id)
        if not chef:
            return None
        
        # Get chef's dishes and menus
        dishes = self.repository.get_chef_dishes(chef_id, active_only=True)
        menus = self.repository.get_chef_menus(chef_id, active_only=True)
        
        return {
            "chef": chef,
            "dishes": dishes,
            "menus": menus,
            "stats": {
                "total_dishes": len(dishes),
                "total_menus": len(menus)
            }
        }

    # ==================== Menu & Dish Discovery ====================

    def get_menu_details(self, menu_id: int) -> Optional[Dict]:
        """
        Get public menu with all dishes included.
        
        Returns:
            {
                "menu": {...},
                "chef": {...},
                "dishes": [...]
            }
        """
        menu = self.repository.get_menu_by_id(menu_id)
        if not menu:
            return None
        
        # Get menu's chef
        chef = self.repository.get_chef_by_id(menu.chef_id)
        
        # Get menu dishes with order
        menu_dishes = self.repository.get_menu_dishes(menu_id)
        
        return {
            "menu": menu,
            "chef": chef,
            "dishes": menu_dishes
        }

    def get_dish_details(self, dish_id: int) -> Optional[Dict]:
        """
        Get public dish details with chef info.
        
        Returns:
            {
                "dish": {...},
                "chef": {...}
            }
        """
        dish = self.repository.get_dish_by_id(dish_id)
        if not dish:
            return None
        
        chef = self.repository.get_chef_by_id(dish.chef_id)
        
        return {
            "dish": dish,
            "chef": chef
        }

    # ==================== Search Helpers ====================

    def get_filters(self) -> Dict:
        """
        Get available filter options for chef search.
        
        Returns:
            {
                "specialties": ["Italian", "French", ...],
                "locations": ["New York", "Los Angeles", ...]
            }
        """
        return {
            "specialties": self.repository.get_available_specialties(),
            "locations": self.repository.get_available_locations()
        }

    def search_chefs(self, query: str, page: int = 1, per_page: int = 20) -> Dict:
        """
        Full-text search for chefs.
        Searches across bio, specialty, and location.
        """
        return self.get_chefs(
            search=query,
            page=page,
            per_page=per_page
        )
