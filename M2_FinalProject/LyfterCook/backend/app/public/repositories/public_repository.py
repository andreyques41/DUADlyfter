from typing import List, Optional, Dict
from flask import g
from sqlalchemy import and_, or_
from config.logging import get_logger
from app.chefs.models import Chef
from app.dishes.models import Dish
from app.menus.models.menu_model import Menu, MenuStatus
from app.menus.models.menu_dish_model import MenuDish

logger = get_logger(__name__)


class PublicRepository:
    """Repository for public-facing data access (no authentication required)"""

    # ==================== Public Chef Listings ====================

    @staticmethod
    def get_active_chefs(
        specialty: Optional[str] = None,
        location: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Chef]:
        """
        Get active chef profiles with optional filters.
        
        Args:
            specialty: Filter by specialty (partial match)
            location: Filter by location (partial match)
            search: Search in bio, specialty, or location
            limit: Max results to return
            offset: Pagination offset
        """
        query = g.db.query(Chef).filter(Chef.is_active == True)
        
        # Apply specialty filter
        if specialty:
            query = query.filter(Chef.specialty.ilike(f"%{specialty}%"))
        
        # Apply location filter
        if location:
            query = query.filter(Chef.location.ilike(f"%{location}%"))
        
        # Apply search across multiple fields
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Chef.bio.ilike(search_term),
                    Chef.specialty.ilike(search_term),
                    Chef.location.ilike(search_term)
                )
            )
        
        # Order by created_at desc (newest first) and apply pagination
        return query.order_by(Chef.created_at.desc()).limit(limit).offset(offset).all()

    @staticmethod
    def get_chef_by_id(chef_id: int) -> Optional[Chef]:
        """Get active chef profile by ID"""
        return g.db.query(Chef).filter(
            and_(Chef.id == chef_id, Chef.is_active == True)
        ).first()

    @staticmethod
    def count_active_chefs(
        specialty: Optional[str] = None,
        location: Optional[str] = None,
        search: Optional[str] = None
    ) -> int:
        """Count total active chefs matching filters (for pagination)"""
        query = g.db.query(Chef).filter(Chef.is_active == True)
        
        if specialty:
            query = query.filter(Chef.specialty.ilike(f"%{specialty}%"))
        
        if location:
            query = query.filter(Chef.location.ilike(f"%{location}%"))
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Chef.bio.ilike(search_term),
                    Chef.specialty.ilike(search_term),
                    Chef.location.ilike(search_term)
                )
            )
        
        return query.count()

    # ==================== Public Dishes ====================

    @staticmethod
    def get_chef_dishes(chef_id: int, active_only: bool = True) -> List[Dish]:
        """Get all dishes for a specific chef"""
        query = g.db.query(Dish).filter(Dish.chef_id == chef_id)
        
        if active_only:
            query = query.filter(Dish.is_active == True)
        
        return query.order_by(Dish.category, Dish.name).all()

    @staticmethod
    def get_dish_by_id(dish_id: int) -> Optional[Dish]:
        """Get a specific active dish"""
        return g.db.query(Dish).filter(
            and_(Dish.id == dish_id, Dish.is_active == True)
        ).first()

    # ==================== Public Menus ====================

    @staticmethod
    def get_chef_menus(chef_id: int, active_only: bool = True) -> List[Menu]:
        """Get all menus for a specific chef"""
        query = g.db.query(Menu).filter(Menu.chef_id == chef_id)
        
        if active_only:
            query = query.filter(Menu.status == MenuStatus.PUBLISHED)
        
        return query.order_by(Menu.created_at.desc()).all()

    @staticmethod
    def get_menu_by_id(menu_id: int) -> Optional[Menu]:
        """Get a specific active menu"""
        return g.db.query(Menu).filter(
            and_(Menu.id == menu_id, Menu.status == MenuStatus.PUBLISHED)
        ).first()

    @staticmethod
    def get_menu_dishes(menu_id: int) -> List[Dict]:
        """
        Get all dishes in a menu with order position.
        Returns list of dicts with dish info and order_position.
        """
        results = (
            g.db.query(Dish, MenuDish.order_position)
            .join(MenuDish, MenuDish.dish_id == Dish.id)
            .filter(MenuDish.menu_id == menu_id)
            .filter(Dish.is_active == True)
            .order_by(MenuDish.order_position)
            .all()
        )
        
        return [
            {
                "dish": dish,
                "order_position": order_position
            }
            for dish, order_position in results
        ]

    # ==================== Search & Discovery ====================

    @staticmethod
    def get_available_specialties() -> List[str]:
        """Get list of unique specialties from active chefs"""
        results = (
            g.db.query(Chef.specialty)
            .filter(
                and_(
                    Chef.is_active == True,
                    Chef.specialty.isnot(None),
                    Chef.specialty != ""
                )
            )
            .distinct()
            .all()
        )
        return [r[0] for r in results]

    @staticmethod
    def get_available_locations() -> List[str]:
        """Get list of unique locations from active chefs"""
        results = (
            g.db.query(Chef.location)
            .filter(
                and_(
                    Chef.is_active == True,
                    Chef.location.isnot(None),
                    Chef.location != ""
                )
            )
            .distinct()
            .all()
        )
        return [r[0] for r in results]
