from flask import Blueprint
from app.public.controllers import PublicController
from app.core.middleware.cache_decorators import cache_response

public_bp = Blueprint("public", __name__, url_prefix="/public")


# ==================== Chef Discovery Routes ====================

@public_bp.route("/chefs", methods=["GET"])
@cache_response(ttl=300, key_prefix='public:chefs:list')
def get_chefs():
    """
    Get paginated list of active chefs
    Query params: specialty, location, search, page, per_page
    ---
    Public endpoint (no authentication required)
    Cached for 5 minutes
    """
    return PublicController.get_chefs()


@public_bp.route("/chefs/<int:chef_id>", methods=["GET"])
@cache_response(ttl=600, key_prefix='public:chefs:profile')
def get_chef_profile(chef_id: int):
    """
    Get public chef profile with dishes and menus
    ---
    Public endpoint (no authentication required)
    Cached for 10 minutes
    """
    return PublicController.get_chef_profile(chef_id)


# ==================== Search Routes ====================

@public_bp.route("/search", methods=["GET"])
@cache_response(ttl=180, key_prefix='public:search')
def search_chefs():
    """
    Full-text search for chefs
    Query params: q (query), page, per_page
    ---
    Public endpoint (no authentication required)
    Cached for 3 minutes
    """
    return PublicController.search_chefs()


@public_bp.route("/filters", methods=["GET"])
@cache_response(ttl=1800, key_prefix='public:filters')
def get_filters():
    """
    Get available filter options (specialties, locations)
    ---
    Public endpoint (no authentication required)
    Cached for 30 minutes
    """
    return PublicController.get_filters()


# ==================== Menu & Dish Routes ====================

@public_bp.route("/menus/<int:menu_id>", methods=["GET"])
@cache_response(ttl=600, key_prefix='public:menus:detail')
def get_menu_details(menu_id: int):
    """
    Get public menu with dishes and chef info
    ---
    Public endpoint (no authentication required)
    Cached for 10 minutes
    """
    return PublicController.get_menu_details(menu_id)


@public_bp.route("/dishes/<int:dish_id>", methods=["GET"])
@cache_response(ttl=600, key_prefix='public:dishes:detail')
def get_dish_details(dish_id: int):
    """
    Get public dish with chef info
    ---
    Public endpoint (no authentication required)
    Cached for 10 minutes
    """
    return PublicController.get_dish_details(dish_id)
