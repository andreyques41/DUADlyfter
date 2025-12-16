"""
Dish Routes
Blueprint registration for dish endpoints
"""
from flask import Blueprint
from app.dishes.controllers import DishController
from app.core.middleware.auth_middleware import jwt_required
from app.core.middleware.cache_decorators import invalidate_on_modify

# Create blueprint
dish_bp = Blueprint('dishes', __name__, url_prefix='/dishes')

# Initialize controller
dish_controller = DishController()


@dish_bp.route('', methods=['POST'])
@jwt_required
@invalidate_on_modify('route:public:dishes:*')
def create_dish():
    """
    POST /dishes
    Create a new dish with ingredients
    Requires: Authorization header with Bearer token
    Invalidates: All public dish caches
    """
    from flask import g
    return dish_controller.create_dish(g.current_user)


@dish_bp.route('', methods=['GET'])
@jwt_required
def get_all_dishes():
    """
    GET /dishes
    Get all dishes for the current chef
    Query params: active_only=true (optional)
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return dish_controller.get_all_dishes(g.current_user)


@dish_bp.route('/<int:dish_id>', methods=['GET'])
@jwt_required
def get_dish_by_id(dish_id):
    """
    GET /dishes/:id
    Get dish by ID with ingredients
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return dish_controller.get_dish_by_id(dish_id, g.current_user)


@dish_bp.route('/<int:dish_id>', methods=['PUT'])
@jwt_required
@invalidate_on_modify('route:public:dishes:*')
def update_dish(dish_id):
    """
    PUT /dishes/:id
    Update dish and optionally ingredients
    Requires: Authorization header with Bearer token
    Invalidates: All public dish caches
    """
    from flask import g
    return dish_controller.update_dish(dish_id, g.current_user)


@dish_bp.route('/<int:dish_id>', methods=['DELETE'])
@jwt_required
@invalidate_on_modify('route:public:dishes:*')
def delete_dish(dish_id):
    """
    DELETE /dishes/:id
    Delete dish (ingredients cascade delete)
    Requires: Authorization header with Bearer token
    Invalidates: All public dish caches
    """
    from flask import g
    return dish_controller.delete_dish(dish_id, g.current_user)
