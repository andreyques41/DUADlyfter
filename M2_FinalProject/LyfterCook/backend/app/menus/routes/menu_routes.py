"""
Menu Routes
Blueprint registration for menu endpoints
"""
from flask import Blueprint
from app.menus.controllers import MenuController
from app.core.middleware.auth_middleware import jwt_required
from app.core.middleware.cache_decorators import invalidate_on_modify

# Create blueprint
menu_bp = Blueprint('menus', __name__, url_prefix='/menus')

# Initialize controller
menu_controller = MenuController()


@menu_bp.route('', methods=['POST'])
@jwt_required
@invalidate_on_modify('route:public:menus:*')
def create_menu():
    """
    POST /menus
    Create a new menu with optional dish assignment
    Requires: Authorization header with Bearer token
    Invalidates: All public menu caches
    """
    from flask import g
    return menu_controller.create_menu(g.current_user)


@menu_bp.route('', methods=['GET'])
@jwt_required
def get_all_menus():
    """
    GET /menus
    Get all menus for the current chef
    Query params: active_only=true (optional)
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return menu_controller.get_all_menus(g.current_user)


@menu_bp.route('/<int:menu_id>', methods=['GET'])
@jwt_required
def get_menu_by_id(menu_id):
    """
    GET /menus/:id
    Get menu by ID with dishes
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return menu_controller.get_menu_by_id(menu_id, g.current_user)


@menu_bp.route('/<int:menu_id>', methods=['PUT'])
@jwt_required
@invalidate_on_modify('route:public:menus:*')
def update_menu(menu_id):
    """
    PUT /menus/:id
    Update menu basic info
    Requires: Authorization header with Bearer token
    Invalidates: All public menu caches
    """
    from flask import g
    return menu_controller.update_menu(menu_id, g.current_user)


@menu_bp.route('/<int:menu_id>/dishes', methods=['PUT'])
@jwt_required
@invalidate_on_modify('route:public:menus:*')
def assign_dishes(menu_id):
    """
    PUT /menus/:id/dishes
    Assign dishes to menu (replaces existing)
    Requires: Authorization header with Bearer token
    Invalidates: All public menu caches
    """
    from flask import g
    return menu_controller.assign_dishes(menu_id, g.current_user)


@menu_bp.route('/<int:menu_id>', methods=['DELETE'])
@jwt_required
@invalidate_on_modify('route:public:menus:*')
def delete_menu(menu_id):
    """
    DELETE /menus/:id
    Delete menu (menu_dishes cascade delete)
    Requires: Authorization header with Bearer token
    Invalidates: All public menu caches
    """
    from flask import g
    return menu_controller.delete_menu(menu_id, g.current_user)
