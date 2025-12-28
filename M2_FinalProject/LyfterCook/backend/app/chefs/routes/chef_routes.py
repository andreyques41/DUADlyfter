"""
Chef Routes
Blueprint registration for chef profile management endpoints

Note: Public chef listing/viewing has been moved to /public/chefs for better
      architecture and to avoid duplication. This module now focuses solely on
      authenticated chef profile management.
      
      Use /public/chefs for browsing chefs (with caching and advanced filters).
"""
from flask import Blueprint
from app.chefs.controllers import ChefController
from app.core.middleware.auth_middleware import jwt_required
from app.core.middleware.cache_decorators import invalidate_on_modify

# Create blueprint
chef_bp = Blueprint('chefs', __name__, url_prefix='/chefs')

# Initialize controller
chef_controller = ChefController()


@chef_bp.route('/profile', methods=['POST'])
@jwt_required
@invalidate_on_modify('route:public:chefs:*')
def create_profile():
    """
    POST /chefs/profile
    Create chef profile for authenticated user
    Requires: Authorization header with Bearer token
    Invalidates: All public chef caches
    """
    from flask import g
    return chef_controller.create_profile(g.current_user)


@chef_bp.route('/profile', methods=['GET'])
@jwt_required
def get_my_profile():
    """
    GET /chefs/profile
    Get current user's chef profile
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return chef_controller.get_my_profile(g.current_user)


@chef_bp.route('/profile', methods=['PUT'])
@jwt_required
@invalidate_on_modify('route:public:chefs:*')
def update_my_profile():
    """
    PUT /chefs/profile
    Update current user's chef profile
    Requires: Authorization header with Bearer token
    Invalidates: All public chef caches
    """
    from flask import g
    return chef_controller.update_my_profile(g.current_user)
